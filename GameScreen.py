import pygame
import pygame_textinput
import Sprite, GameStats
import json

from random import randint
from os import path

clock = pygame.time.Clock()

class ScreenManager():
    playerStats = GameStats.GameStats()

    def __init__(self, w, h):
        self.running = True
        self.check_for_player_stats()

        self.titleScreen = TitleScreen(w, h)
        self.typingGame = TypingScreen(w, h, self.playerStats)
        self.statsScreen = PlayerStatsScreen(w, h, self.playerStats)

        self.screens = {
            "title": self.titleScreen,
            "typingGame": self.typingGame,
            "stats": self.statsScreen
        }

        self.currentScreenKey = None
        self.change_screens("title")

    def update(self, events, elapsed):
        self.check_for_screen_change()

        self.screens[self.currentScreenKey].update(events, elapsed)

    def draw(self, buffer):
        self.screens[self.currentScreenKey].draw(buffer)

    def check_for_player_stats(self):
        if path.exists('playerStats.json'):
            
            with open('playerStats.json') as json_file:
                data = json.load(json_file)
                d = data['stats']
                self.playerStats.totalPlaytime = d['totalPlaytime']
                self.playerStats.deaths = d['deaths']
                self.playerStats.failedWords = d['failedWords']
                self.playerStats.gamesPlayed = d['gamesPlayed']
                self.playerStats.kills = d['kills']
                self.playerStats.longestGame = d['longestGame']
                self.playerStats.successfulWords = d['successfulWords']
        else:
            data = {}
            data['stats'] = {
                'totalPlaytime': 0,
                'deaths': 0,
                'failedWords': 0,
                'gamesPlayed': 0,
                'kills': 0,
                'longestGame': 0,
                'successfulWords': 0
            }

            with open('playerStats.json', 'w') as outfile:
                json.dump(data, outfile)

    def check_for_screen_change(self):
        if self.screens[self.currentScreenKey].moveToScreen is not None:
            if self.screens[self.currentScreenKey].moveToScreen == "Exit":
                self.running = False
                return

            self.change_screens(self.screens[self.currentScreenKey].moveToScreen)

    def change_screens(self, key):
        if self.currentScreenKey is not None:
            self.screens[self.currentScreenKey].on_close()
            self.screens[self.currentScreenKey].moveToScreen = None

        self.currentScreenKey = key
        self.screens[self.currentScreenKey].on_open()

class GameScreen():

    active = True

    def __init__(self, w, h):
        self.buffer = pygame.surface.Surface((w, h))
        self.isActive = False
        self.moveToScreen = None

    # update
    def update(self, events, elapsed):
        pass

    # draw
    def draw(self, buffer):
        pass

    def on_open(self):
        pass

    def on_close(self):
        pass

class TitleScreen(GameScreen):

    def __init__(self, w, h):
        super().__init__(w, h)

        self.title = Sprite.Text(320, 80, pygame.font.Font('assets/fonts/Bungee-Regular.ttf', 48), "Typing Adventure", (255,255,255))
        self.title.set_draw_to_center()

        self.startbutton = Sprite.TextButton(320, 180, pygame.font.Font('assets/fonts/Bungee-Regular.ttf', 24), "Start Game", (255,255,255))
        self.startbutton.set_draw_to_center()
        self.statsbutton = Sprite.TextButton(320, 230, pygame.font.Font('assets/fonts/Bungee-Regular.ttf', 24), "Player Stats", (255,255,255))
        self.statsbutton.set_draw_to_center()
        self.exitbutton = Sprite.TextButton(320, 280, pygame.font.Font('assets/fonts/Bungee-Regular.ttf', 24), "Exit", (255,255,255))
        self.exitbutton.set_draw_to_center()

    # update
    def update(self, events, elapsed):
        if self.startbutton.collides_with_point(pygame.mouse.get_pos()) is True:
            if self.startbutton.on_click() is True:              
                self.moveToScreen = "typingGame"
                  
        if self.statsbutton.collides_with_point(pygame.mouse.get_pos()) is True:
            if self.statsbutton.on_click() is True:              
                self.moveToScreen = "stats"
        
        if self.exitbutton.collides_with_point(pygame.mouse.get_pos()) is True:
            if self.exitbutton.on_click() is True:              
                self.moveToScreen = "Exit"

    # draw
    def draw(self, buffer):
        self.title.draw(buffer)
        self.startbutton.draw(buffer)
        self.statsbutton.draw(buffer)
        self.exitbutton.draw(buffer)

    def on_open(self):
        pygame.mixer.music.load('assets/sound/music/Tribal Ritual.wav')
        pygame.mixer.music.play(-1)
        pygame.mixer.music.set_volume(.2)

    def on_close(self):
        pass

class TypingScreen(GameScreen):
    zombies = []
    words = []
    availableWords = []
    difficulty = 1

    def __init__(self, w, h, playerStats):
        super().__init__(w, h)
        self.tmpStats = GameStats.GameStats()

        self.gameover = False   
        self.backbuffer = pygame.Surface((640,360))
        self.backbuffer.fill((0,0,0))
        self.backbuffer.set_alpha(200)
        self.gameoverlabel = Sprite.Text(320, 80, pygame.font.Font('assets/fonts/Bungee-Regular.ttf', 48), "Game Over", (255, 0, 0))   
        self.gameoverlabel.set_draw_to_center()  
        self.replaybutton = Sprite.TextButton(320, 180, pygame.font.Font('assets/fonts/joystix.ttf', 24), "Restart Game", (255,255,255))
        self.replaybutton.set_draw_to_center()
        self.backbutton = Sprite.TextButton(320, 240, pygame.font.Font('assets/fonts/joystix.ttf', 24), "Back To Title", (255,255,255))
        self.backbutton.set_draw_to_center()

        self.background = pygame.image.load('assets/desertbg.png')
        self.ground = pygame.image.load('assets/ground.png')
        self.barrier = Sprite.Barrier(60, 172, 64, 128)

        self.shooter = Sprite.Shooter(20, 180, 64, 64)

        self.textinput = pygame_textinput.TextInput('', 'assets/fonts/joystix.ttf', 20, True, (255,255,255), (0, 0, 1), 400, 35, 9)

        self.totaltime = 0
        self.timelabel = Sprite.Text(420, 310, pygame.font.Font('assets/fonts/Bungee-Regular.ttf', 16), 'Time Elapsed: ', (255,255,255))
        self.timeamount = Sprite.Text(580, 310, pygame.font.Font('assets/fonts/Bungee-Regular.ttf', 16), '0', (255,255,255))
        self.zombieskilled = 0
        self.zombieskilledlabel = Sprite.Text(420, 330, pygame.font.Font('assets/fonts/Bungee-Regular.ttf', 16), 'Zombies Killed: ', (255,255,255))
        self.zombieskilledamount = Sprite.Text(580, 330, pygame.font.Font('assets/fonts/Bungee-Regular.ttf', 16), '0', (255,255,255))
        self.difficultylabel = Sprite.Text(620, 20, pygame.font.Font('assets/fonts/Bungee-Regular.ttf', 16), '1', (255,255,255))

        self.ticksToNextZombie = randint(20,60)


        self.set_up_game()

    def update(self, events, elapsed):
        if self.gameover is True:

            if self.replaybutton.collides_with_point(pygame.mouse.get_pos()) is True:
                if self.replaybutton.on_click() is True:              
                    self.reset_game()
                    
            if self.backbutton.collides_with_point(pygame.mouse.get_pos()) is True:
                if self.backbutton.on_click() is True:              
                    self.moveToScreen = "title"

            return

        for zomb in self.zombies:
            if zomb.dead is True:
                self.zombies.remove(zomb)
                del zomb
                continue

            zomb.update()
            
            if self.barrier.health > 0:
                if zomb.attacking is False and zomb.x <= (self.barrier.collisionRect.x + self.barrier.collisionRect.w):
                    zomb.x = (self.barrier.collisionRect.x + self.barrier.collisionRect.w)
                    zomb.walking = False
                    zomb.attacking = True

                if zomb.attacking is True:
                    if zomb.damageBarrier is True:
                        self.barrier.been_hit(1, (zomb.x, zomb.y + zomb.height/2))
                        zomb.damageBarrier = False
                        if self.barrier.health <= 0:
                            self.barrier_destoryed()                   
            else:
                if zomb.x < 25:
                    self.set_gameover()

        self.check_for_new_zombie()

        self.shooter.update()
        self.barrier.update()

        if self.textinput.update(events):
            print(self.textinput.get_text())
            self.check_input(self.textinput.get_text())

        self.totaltime += elapsed
        self.timeamount.set_text("{:.1f}".format(self.totaltime/1000))

        if self.difficulty <= (self.totaltime/1000)//25:
            print('hit')
            self.difficulty += 1
            self.difficultylabel.set_text(str(self.difficulty))
            self.set_available_words()
    
    def draw(self, buffer):
        pygame.draw.rect(buffer, (50, 20, 255), (0, 0, 640, 180))
        buffer.blit(self.background, (0,0))
        buffer.blit(self.ground, (0, 180))

        if self.barrier.health > 0:
            self.barrier.draw(buffer)

        self.shooter.draw(buffer)
        
        for zomb in self.zombies:
            zomb.draw(buffer)

        self.timelabel.draw(buffer)
        self.timeamount.draw(buffer)
        self.zombieskilledlabel.draw(buffer)
        self.zombieskilledamount.draw(buffer)
        self.difficultylabel.draw(buffer)

        buffer.blit(self.textinput.get_surface(), (250, 315))

        if self.gameover is True:
            # Darken 
            buffer.blit(self.backbuffer, (0,0))
            self.gameoverlabel.draw(buffer)
            self.replaybutton.draw(buffer)
            self.backbutton.draw(buffer)

    def set_up_game(self):

        with open('assets/data/words.json') as file:
            words = json.load(file)
            
        self.words = words['words']

        self.set_difficulty(1)

    def set_difficulty(self, difficulty):
        self.difficulty = difficulty
        self.set_available_words()

    def set_available_words(self):
        global startAt 
        global endAt

        if self.difficulty == 1:
            startAt = 3
            endAt = 4
        elif self.difficulty == 2:
            startAt = 3
            endAt = 5
        elif self.difficulty == 3:
            startAt = 3
            endAt = 6
        elif self.difficulty == 4:
            startAt = 4
            endAt = 7
        else:
            startAt = 4
            endAt = 8
        
        for word in self.words:
            if len(word) >= startAt and len(word) <= endAt:
                self.availableWords.append(word)

    def set_gameover(self):
        self.gameover = True
        ScreenManager.playerStats.deaths += 1
        ScreenManager.playerStats.totalPlaytime += self.totaltime
        ScreenManager.playerStats.gamesPlayed += 1

        ScreenManager.playerStats = ScreenManager.playerStats.combine_stats(self.tmpStats)

        data = {}
        data['stats'] = {
            'totalPlaytime': ScreenManager.playerStats.totalPlaytime,
            'deaths': ScreenManager.playerStats.deaths,
            'failedWords': ScreenManager.playerStats.failedWords,
            'gamesPlayed': ScreenManager.playerStats.gamesPlayed,
            'kills': ScreenManager.playerStats.kills,
            'longestGame': ScreenManager.playerStats.longestGame,
            'successfulWords': ScreenManager.playerStats.successfulWords
        }

        with open('playerStats.json', 'w') as outfile:
            json.dump(data, outfile)

    def reset_game(self):
        self.totaltime = 0
        self.zombieskilled = 0
        self.zombieskilledamount.set_text(str(self.zombieskilled))
        self.zombies.clear()
        self.set_difficulty(1)
        self.gameover = False
        self.barrier.reset()
        

    def get_new_word(self):
        wordindex = randint(0, len(self.availableWords))
        return self.availableWords[wordindex]

    def check_input(self, word):
        if word == '' or self.shooter.jammed is True:
            return

        word = word.lower()

        for zomb in self.zombies:
            if(zomb.word.text == word):
                zomb.dying = True
                pygame.mixer.Sound.play(zomb.zombieDeathSound)

                zomb.walking = False
                zomb.add_damage_blocks((zomb.x + zomb.width/2, zomb.y + zomb.height/2))
                self.zombieskilled += 1
                self.zombieskilledamount.set_text(str(self.zombieskilled))
                self.shooter.set_shooting()          
                self.textinput.clear_text()
                ScreenManager.playerStats.successfulWords += 1
                ScreenManager.playerStats.kills += 1
                return

        # Misspelling
        self.shooter.set_jammed()
        ScreenManager.playerStats.failedWords += 1
    
    def barrier_destoryed(self):
        for zomb in self.zombies:
            zomb.attacking = False
            zomb.walking = True

    def check_for_new_zombie(self):
        if self.ticksToNextZombie == 0:
            self.add_zombie()
            self.ticksToNextZombie = randint(100, 150) // (self.difficulty/2)
            print(self.ticksToNextZombie)
        else:
            self.ticksToNextZombie -= 1

    def add_zombie(self):
        y = randint(140, 240)
        zombie = Sprite.Zombie(650, y, 64, 64)
        zombie.set_speed(randint(1, 1 + (self.difficulty//3)))
        zombie.active = True
        zombie.walking = True
        zombie.set_word(self.get_new_word())
        self.zombies.append(zombie)
        self.zombies.sort(key=lambda z: z.y)

    def on_open(self):
        # Stop any music that is playing and unload it
        pygame.mixer.music.stop()

        pygame.mixer.music.load('assets/sound/music/Star Commander.wav')
        pygame.mixer.music.play(-1)

    def on_close(self):
        # Stop any music that is playing and unload it
        pygame.mixer.music.stop()

class PlayerStatsScreen(GameScreen):

    def __init__(self, w, h, playerstats):
        super().__init__(w, h)
        self.backbutton = Sprite.TextButton(75, 330, pygame.font.Font('assets/fonts/Bungee-Regular.ttf', 24), "< Back", (255,255,255))
        self.backbutton.set_draw_to_center()

    def set_up_stats(self):
        self.killslabel = Sprite.Text(50, 50, pygame.font.Font('assets/fonts/joystix.ttf', 24), "Kills", (255,255,255))
        self.killsamount = Sprite.Text(300, 50, pygame.font.Font('assets/fonts/joystix.ttf', 24), str(ScreenManager.playerStats.kills), (255,223,0))
        self.gameplayedlabel = Sprite.Text(50, 80, pygame.font.Font('assets/fonts/joystix.ttf', 24), "Games Played", (255,255,255))
        self.gameplayedamount = Sprite.Text(300, 80, pygame.font.Font('assets/fonts/joystix.ttf', 24), str(ScreenManager.playerStats.gamesPlayed), (255,223,0))
        self.totaltimelabel = Sprite.Text(50, 110, pygame.font.Font('assets/fonts/joystix.ttf', 24), "Time Played", (255,255,255))
        self.totaltimeamount = Sprite.Text(300, 110, pygame.font.Font('assets/fonts/joystix.ttf', 24), str(ScreenManager.playerStats.totalPlaytime//1000) + " seconds", (255,223,0))
        self.longestgamelabel = Sprite.Text(50, 140, pygame.font.Font('assets/fonts/joystix.ttf', 24), "Longest Game", (255,255,255))
        self.longestgameamount = Sprite.Text(300, 140, pygame.font.Font('assets/fonts/joystix.ttf', 24), str(ScreenManager.playerStats.longestGame//1000) + " seconds", (255,223,0))
        self.failedwordslabel = Sprite.Text(50, 170, pygame.font.Font('assets/fonts/joystix.ttf', 24), "Words Failed", (255,255,255))
        self.failedwordsamount = Sprite.Text(300, 170, pygame.font.Font('assets/fonts/joystix.ttf', 24), str(ScreenManager.playerStats.failedWords), (255,223,0))

    def update(self, events, elapsed):
        if self.backbutton.collides_with_point(pygame.mouse.get_pos()) is True:
            if self.backbutton.on_click() is True:              
                self.moveToScreen = "title"
    
    def draw(self, buffer):

        self.backbutton.draw(buffer)

        self.killslabel.draw(buffer)
        self.killsamount.draw(buffer)
        self.gameplayedlabel.draw(buffer)
        self.gameplayedamount.draw(buffer)
        self.totaltimelabel.draw(buffer)
        self.totaltimeamount.draw(buffer)
        self.longestgamelabel.draw(buffer)
        self.longestgameamount.draw(buffer) 
        self.failedwordslabel.draw(buffer) 
        self.failedwordsamount.draw(buffer)

    def on_open(self):
        self.set_up_stats()

    def on_close(self):
        pass

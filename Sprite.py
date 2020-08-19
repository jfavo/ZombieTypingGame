import pygame
import itertools
from random import randint

clock = pygame.time.Clock()

class SpriteSheet():

    def __init__(self, path):
        self.sheet = pygame.image.load(path)

    def SetImage(self, rect):
        r = pygame.Rect(rect)
        image = pygame.Surface(r.size).convert()
        image.blit(self.sheet, (0, 0), rect)
        colorkey = image.get_at((0,0))
        image.set_colorkey(colorkey, pygame.RLEACCEL)
        return image

    def SetImages(self, rects):
        return [self.SetImage(rect) for rect in rects]

class Text():
    drawtocenter = False

    def __init__(self, x, y, font, text, color):
        self.font = font
        self.text = text
        self.color = color
        self.textSurface = self.font.render(text, True, self.color)
        self.rect = self.textSurface.get_rect()
        self.collisionRect = pygame.Rect(x, y, self.rect.w, self.rect.h)
        self.x = x
        self.y = y

    def set_color(self, color):
        self.color = color
        self.textSurface = self.font.render(self.text, True, color)

    def set_text(self, text):
        self.text = text
        self.textSurface = self.font.render(self.text, True, self.color)

    def set_position(self, x, y):
        self.x = x
        self.y = y

    def set_draw_to_center(self):
        self.drawtocenter = True
        self.collisionRect = pygame.Rect(self.x + self.collisionRect.w/2, self.y + self.collisionRect.h/2, self.collisionRect.w, self.collisionRect.h)

    def update(self):
        pass

    def draw(self, buffer):
        if self.drawtocenter is True:
            buffer.blit(self.textSurface, (self.x - self.rect.w/2, self.y - self.rect.h/2))
        else:
            buffer.blit(self.textSurface, (self.x, self.y))

class TextButton(Text):

    def __init__(self, x, y, font, text, color):
        super().__init__(x, y, font, text, color)
        self.collisionRect = pygame.Rect(x - 10, y - 10, self.rect.w + 20, self.rect.h + 20)
        self.backgroundColor = (0,0,0)

        self.hovered = False

    def collides_with_point(self, point):
        if self.collisionRect.x <= point[0]/2 and self.collisionRect.x + self.collisionRect.w >= point[0]/2:
            if self.collisionRect.y <= point[1]/2 and self.collisionRect.y + self.collisionRect.h >= point[1]/2:
                if self.hovered is False:
                    pygame.mouse.set_cursor(*pygame.cursors.tri_left)
                    self.set_color((0,0,0))
                    self.backgroundColor = (255,255,255)             
                    self.hovered = True
                return True
        
        self.hovered = False
        self.set_color((255,255,255))
        self.backgroundColor = (0,0,0)
        pygame.mouse.set_cursor(*pygame.cursors.arrow)
        return False

    def on_click(self):
        if pygame.mouse.get_pressed()[0]:
            #pygame.mixer.Sound.play(self.selectSound)
            return True
        
        return False

    
    def draw(self, buffer):
        pygame.draw.rect(buffer, self.backgroundColor, self.collisionRect)
        super().draw(buffer)

    def set_draw_to_center(self):
        self.drawtocenter = True
        self.collisionRect = pygame.Rect(self.x - 10 - (self.rect.w/2), self.y - 10 - self.rect.h/2, self.collisionRect.w, self.collisionRect.h)


class Sprite(object):
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.width = w
        self.height = h
        self.image = None
        self.currentImage = None
        self.color = (0,0,0)
        self.active = False
        self.hasCollision = False
        self.collisionRect = None
        self.stepCount = 0

    def get_position(self):
        return [self.x, self.y]

    def get_position_rect(self):
        return (self.x, self.y, self.width, self.height)

    # Initializing methods

    def SetImage(self, image):
        self.image = image
        self.currentImage = image

    def SetCollisionParams(self, rect):
        self.collisionRect = rect
        self.hasCollision = True

    # update methods

    def update(self):
        return

    def MoveSprite(self, x, y):
        self.x = x
        self.y = y

    # drawing methods
    
    def draw(self, screen):
        if self.currentImage is None:
            pygame.draw.rect(screen, self.color, self.get_position_rect())
        else:
            screen.blit(self.currentImage, self.get_position())

class Shooter(Sprite):

    def __init__(self, x, y, w, h):
        super().__init__(x, y, w, h)
        self.idle = True
        self.idleSteps = 0
        self.shooting = False
        self.shootingSteps = 0
        self.jammed = False
        self.jammedSteps = 0
        self.jammed_ticks_max = 100
        self.dead = False
        self.victory = False

        self.shootingsound = pygame.mixer.Sound('assets/sound/soundfx/gunshot.wav')
        self.shootingsound.set_volume(.5)

        self.jammed_bar = StatusBar(x + 5, y + h + 15, w - 25, 5, self.jammed_ticks_max)

        idleRects = [(0, 0, 76, 76), (76, 0, 76, 76), (0, 76, 76, 76)]
        shootingRects = [(76,76,76,76), (0, 152, 76, 76)]
        jammedRects = [(76,152,76,76), (0,228,76,76),(76, 228, 76, 76), (0, 304, 76, 76), (76, 304, 76,76)]
        spriteSheet = SpriteSheet('assets/CowboyAnimations.png')
        self.idleAnimations = spriteSheet.SetImages(idleRects)
        self.shootingAnimations = spriteSheet.SetImages(shootingRects)
        self.jammedAnimations = spriteSheet.SetImages(jammedRects)
        self.jammedImage = pygame.image.load('assets/Jammed.png')
        self.currentImage = self.idleAnimations[0]

    def draw(self, screen):
        super().draw(screen)
        if self.jammed is True:
            screen.blit(self.jammedImage, (self.x + self.width/2 - 32, self.y - 16))
            self.jammed_bar.draw(screen)

    def update(self):
        if self.shooting is True:
            if self.shootingSteps == 4:
                self.shootingSteps = 0
                self.shooting = False
                self.idle = True
            else:
                self.currentImage = self.shootingAnimations[self.shootingSteps//2]
                self.shootingSteps += 1

        if self.jammed is True:
            if self.jammedSteps == 25:
                self.jammedSteps = 0

            self.currentImage = self.jammedAnimations[self.jammedSteps//5]
            self.jammedSteps += 1
            self.jammedTicks += 1
            self.jammed_bar.update_bar(self.jammedTicks)

            if self.jammedTicks == self.jammed_ticks_max:

                self.jammed = False
                self.idle = True              

        if self.idle is True:
            if self.idleSteps == 18:
                self.idleSteps = 0

            self.currentImage = self.idleAnimations[self.idleSteps//6]

            self.idleSteps += 1   

    
    def set_shooting(self):
        self.idle = False
        self.shooting = True
        self.shootingSteps = 0
        pygame.mixer.Sound.play(self.shootingsound)

    def set_jammed(self):
        self.idle = False
        self.shooting = False
        self.jammed = True
        self.jammedSteps = 0
        self.jammedTicks = 0

class Zombie(Sprite):

    def __init__(self, x, y, w, h):
        super().__init__(x, y, w, h)      
        idleRects = [(0, 0, 64, 64), (64, 0, 64, 64), (0, 64, 64, 64), (64, 64, 64, 64), (0, 128, 64, 64)]
        dyingRects = [(64, 128, 64, 64), (0, 192, 64, 64), (64, 192, 64, 64), (0, 256, 64, 64)]
        attackRects = [(64, 256, 64, 64), (0, 320, 64, 64), (64, 320, 64, 64), (0, 384, 64, 64), (64, 384, 64, 64)]
        spriteSheet = SpriteSheet('assets/Zombie.png')
        self.image = spriteSheet.SetImages(idleRects)
        self.dyingAnimations = spriteSheet.SetImages(dyingRects)
        self.attackAnimations = spriteSheet.SetImages(attackRects)
        self.currentImage = self.image[0]
        self.collisionRect = pygame.Rect(12, 12, 40, 40)
        self.damage_blocks = []

        self.dying = False
        self.dyingSteps = 0
        self.dead = False
        self.walking = False
        self.attacking = False
        self.attackCount = 0
        self.attackPaused = False
        self.attackPauseSteps = 0
        self.damageBarrier = False

        self.zombieDeathSound = pygame.mixer.Sound('assets/sound/soundfx/zombiedeath.wav')
        self.zombieDeathSound.set_volume(.5)

    def set_speed(self, speed):
        self.speed = speed

    def set_word(self, word):
        self.word = Text(self.x, self.y, pygame.font.Font('assets/fonts/joystix.ttf', 16), word, (255, 255, 255))
        self.wordbuffer = self.word.collisionRect.w/2, self.word.collisionRect.h/2


    # draw
    def draw(self, screen):
        super().draw(screen)
        
        for block in self.damage_blocks:
            block.draw(screen)

        if self.dying is False:
            pygame.draw.rect(screen, (0,0,0), (self.word.x, self.word.y, self.word.collisionRect.w, self.word.collisionRect.h))
            self.word.draw(screen)

    # update

    def update(self):
        for block in self.damage_blocks:
            if block.animation_done is True:
                self.damage_blocks.remove(block)
                del block
            else:
                block.update()


        if self.attacking is True:
            if self.attackPaused is True:
                if self.attackPauseSteps == 10:
                    self.attackPaused = False
                else:
                    self.attackPauseSteps += 1
            else:

                if self.attackCount == 20:  
                    self.attackCount = 0
                    self.attackPaused = True
                    self.attackPauseSteps = 0
                if self.attackCount == 12:
                    # Damage barrier
                    self.damageBarrier = True

                self.currentImage = self.attackAnimations[self.attackCount//4]
                self.attackCount += 1


        if self.dying is True:
            if self.dyingSteps == 12:
                self.dead = True

                for block in self.damage_blocks:
                    self.damage_blocks.remove(block)
                    del block
                return
            else:

                self.currentImage = self.dyingAnimations[self.dyingSteps//3]
                self.dyingSteps += 1

        if self.walking is True:
            if self.stepCount + 1 >= 30:
                self.stepCount = 0
                
            self.currentImage = self.image[self.stepCount//6]
            self.stepCount += 1

            if self.stepCount > 6:
                self.MoveSprite(self.x - self.speed, self.y)
                self.word.set_position(self.x + self.width/2 - self.wordbuffer[0], self.y - self.wordbuffer[1])


    def add_damage_blocks(self, point):
        for _ in itertools.repeat(None, randint(4,7)):
            size = randint(2, 6)
            velocity = (randint(-20, -15), randint(-50, -30))
            sprite = SprayBlock(point[0], point[1], size, size, velocity, (255, 0, 0))
            self.damage_blocks.append(sprite)

class Barrier(Sprite):
    damage_blocks = []
    destroyed = False

    def __init__(self, x, y, w, h):
        super().__init__(x, y, w, h)
        self.image = [pygame.image.load("assets/barrier.png"), pygame.image.load("assets/barrierDamaged1.png"), pygame.image.load("assets/barrierDamaged2.png")]
        self.currentImage = self.image[0]
        self.health = 100
        self.collisionRect = pygame.Rect(x + 5, y, w - 30, h)
        self.health_bar = StatusBar(x, y + h + 5, w, 10, self.health)

        self.barrierHitSound = pygame.mixer.Sound('assets/sound/soundfx/barrierhit.wav')
        self.barrierHitSound.set_volume(.5)
    
    def update(self):
        for block in self.damage_blocks:
            if block.animation_done is True:
                self.damage_blocks.remove(block)
                del block
            else:
                block.update()

    def draw(self, screen):
        if self.destroyed is False:
            super().draw(screen)
        
        for block in self.damage_blocks:
            block.draw(screen)

        self.health_bar.draw(screen)

    def been_hit(self, damage, point):
        if self.health > 0:
            pygame.mixer.Sound.play(self.barrierHitSound)

            if self.health <= 33:
                self.currentImage = self.image[2]
            elif self.health <= 66:
                self.currentImage = self.image[1]

            self.health -= damage
            self.health_bar.update_bar(self.health)
            self.add_damage_blocks(point)


    def add_damage_blocks(self, point):
        for _ in itertools.repeat(None, randint(4,7)):
            size = randint(2, 6)
            velocity = (randint(-45, 45), randint(-60, -30))
            sprite = SprayBlock(point[0], point[1], size, size, velocity, (89, 60, 31))
            self.damage_blocks.append(sprite)

    def reset(self):
        self.currentImage = self.image[0]
        self.health = 100
        self.health_bar.update_bar(self.health)

class SprayBlock(Sprite):
    gravity = 5
    velocity_x = 0
    velocity_y = 0
    animation_steps = 0
    animation_steps_max = randint(12, 18)
    animation_done = False

    def __init__(self, x, y, w, h, velocity, color):
        super().__init__(x,y,w,h)
        self.velocity_x = velocity[0]
        self.velocity_y = velocity[1]
        self.color = color

    def update(self):
        if self.animation_steps < self.animation_steps_max:
            self.animation_steps += 1
        else:
            self.animation_done = True 

        self.velocity_y += self.gravity
        self.y += self.velocity_y * .15
        self.x += self.velocity_x * .15

    def draw(self,screen):
        if self.animation_done is False:
            super().draw(screen)

class StatusBar(Sprite):

    def __init__(self, x, y, w, h, max):
        super().__init__(x, y, w, h)
        self.background = Sprite(x - 5, y - 5, w + 10, h + 10)
        self.background.color = (0,0,0)
        self.bar = Sprite(x, y, w, h)
        self.bar.color = (255, 0, 0)
        self.max = max
        self.original_width = w

    def draw(self, screen):
        self.background.draw(screen)
        self.bar.draw(screen)

    def update_bar(self, newPoint):
        newWidth = (newPoint / self.max) * self.original_width
        self.bar.width = newWidth

    def reset_bar(self):
        self.bar.width = self.original_width

    
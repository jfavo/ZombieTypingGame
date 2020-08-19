
class GameStats():

    def __init__(self):
        self.kills = 0
        self.deaths = 0
        self.gamesPlayed = 0
        self.totalPlaytime = 0
        self.longestGame = 0
        self.successfulWords = 0
        self.failedWords = 0
    
    def combine_stats(self, stats):
        self.kills += stats.kills
        self.deaths += stats.deaths
        self.gamesPlayed += stats.gamesPlayed
        self.totalPlaytime += stats.totalPlaytime
        
        if self.longestGame < stats.totalPlaytime:
            self.longestGame = stats.totalPlaytime

        self.successfulWords += stats.successfulWords
        self.failedWords += stats.failedWords

        return self
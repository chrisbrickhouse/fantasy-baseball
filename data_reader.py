import csv
import numpy as np
from math import log

class Player():
    def __init__(self,*argv):
        self.n = 162  # Number of games in 2017
        self.name = argv[1]
        bpid = argv[2]
        self.team = argv[4]  # Not always correct best to ignore
        games = argv[6]
        plate_appearances = argv[7]
        at_bats = argv[8]
        runs = argv[9]
        hits = argv[10]
        doubles = argv[11]
        triples = argv[12]
        home_runs = argv[13]
        rbi = argv[14]
        steals = argv[15]
        caught = argv[16]
        walks = argv[17]
        strikeouts = argv[18]
        self.batting_avg = argv[19]
        self.on_base_perc = argv[20]
        self.slugging_perc = argv[21]
        total_bases = argv[24]
        self._pos(argv[30])
        self.data = {
            'bpid': bpid,
            'G': games,
            'PA': plate_appearances,
            'AB': at_bats,
            'TB': total_bases,
            'BB': walks,
            'K': strikeouts,
            'H': hits,
            '2B': doubles,
            '3B': triples,
            'HR': home_runs,
            'R': runs,
            'SB': steals,
            'CS': caught,
            'RBI': rbi,
        }
        self.sim_data = []
        self.sim_wins = 0.0
        self.sim_plays = 0.0

    def points_per_game(self,scoring_rules=None):
        data = self.data
        tbpg = self.divide('TB')
        rpg = self.divide('R')
        sbpg = self.divide('SB')
        cspg = self.divide('CS')
        bbpg = self.divide('BB')
        rbipg = self.divide('RBI')
        kpg = self.divide('K')
        points = self.score(tbpg,rpg,bbpg,rbipg,cspg,sbpg,kpg)
        self.ppg = points

    def score(self,tb,r,bb,rbi,cs,sb,k):
        points = tb + r + bb + rbi - cs
        points += (sb * 2.0)
        points += (k / 2.0)
        return(points)

    def divide(self,x,y='G'):
        result = float(self.data[x])/float(self.data[y])
        return(result)

    def random_poisson(self,x,y='G',size=None):
        div = self.divide(x,y)
        rand = np.random.poisson(div,size)
        return(rand)

    def ppg_stats(self):
        data = self.sim_data
        m = np.mean(data)
        sd = np.std(data)
        z = 1.96
        n = len(data)
        ci = (z * sd) / (n**0.5)
        self.ucb = m + ci
        self.lcb = m - ci

    def _pos(self, s):
        eligable = s.split('/')[0]
        positions = []
        self.pitcher = False
        for p in eligable:
            if p == 'D':
                positions.append('DH')
            elif int(p) >= 7:
                positions.append('OF')
            elif int(p) == 1:
                positions.append('P')
                self.pitcher = True
            elif int(p) == 2:
                positions.append('C')
            elif int(p) == 6:
                positions.append('SS')
            else:
                pos = str(int(p) - 2)+'B'
                positions.append(pos)
        self.positions= positions


class Pitcher():
    def __init__(self,*argv):
        self.n = 162  # Number of games in 2017
        self.name = argv[1]
        bpid = argv[2]
        self.team = argv[4]  # Not always correct best to ignore
        wins = argv[6]
        losses = argv[7]
        self.earned_run_avg = argv[9]
        games = argv[10]
        self.starts = argv[11]
        saves = argv[15]
        self.innings_pitched = str(argv[16]).split('.')
        try:
            outs_pitched = int(self.innings_pitched[0])*3 \
                           +int(self.innings_pitched[1])
        except IndexError:
            outs_pitched = int(self.innings_pitched[0])*3
        hits_allowed = argv[17]
        self.runs_allowed = argv[18]
        earned_runs = argv[19]
        self.hr_allowed = argv[20]
        walks_issued = int(argv[21])+int(argv[22])
        strikeouts = argv[23]
        hit_batsman = argv[24]
        self.fielding_indep_pitch = argv[29]
        self.walks_hits_per_inning_pitches = argv[30]
        self.data = {
            'bpid': bpid,
            'G': games,
            'W': wins,
            'L': losses,
            'OP': outs_pitched,
            'IP': outs_pitched / 3.0,
            'SV': saves,
            'HA': hits_allowed,
            'HB': hit_batsman,
            'ER': earned_runs,
            'K': strikeouts,
            'BB': walks_issued,
        }
        self.positions = ['P']
        self.sim_data = []
        self.sim_plays = 0.0
        self.sim_wins = 0.0

    def points_per_game(self,scoring_rules=None):
        data = self.data
        opg = self.divide('OP')
        wpg = self.divide('W')
        lpg = self.divide('L')
        spg = self.divide('SV')
        kpg = self.divide('K')
        hpg = self.divide('HA')
        hbpg = self.divide('HB')
        erpg = self.divide('ER')
        bbpg = self.divide('BB')
        points = self.score(opg,hpg,hbpg,bbpg,wpg,erpg,lpg,spg,kpg)
        self.ppg = points

    def score(self,opg,hpg,hbpg,bbpg,wpg,erpg,lpg,spg,kpg):
        points = opg - hpg - hbpg - bbpg
        points += 2.0 * (wpg - erpg - lpg)
        points += 5.0 * spg
        points += (kpg / 2.0)
        return(points)

    def divide(self,x,y='G'):
        result = float(self.data[x])/float(self.data[y])
        return(result)

    def random_poisson(self,x,y='G',size=None):
        div = self.divide(x,y)
        rand = np.random.poisson(div,size)
        return(rand)

    def ppg_stats(self):
        data = self.sim_data
        m = np.mean(data)
        sd = np.std(data)
        z = 1.96
        n = len(data)
        ci = (z * sd) / (n**0.5)
        self.ucb = m + ci
        self.lcb = m - ci


def read_file(fname,pitcher=False):
    players = []
    with open(fname,'r') as f:
        reader = csv.reader(f)
        next(reader)  # Skip header
        for row in reader:
            if 'LgAvg' in row[1]:
                continue
            if pitcher:
                p = Pitcher(*row)
            else:
                p = Player(*row)
            players.append(p)
    return(players)

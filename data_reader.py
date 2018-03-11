import csv
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

    def points_per_game(self,scoring_rules=None):
        data = self.data
        tb_pg = self.divide('TB')
        r_pg = self.divide('R')
        sb_pg = self.divide('SB')
        cs_pg = self.divide('CS')
        bb_pg = self.divide('BB')
        rbi_pg = self.divide('RBI')
        k_pg = self.divide('K')
        points = tb_pg + r_pg + bb_pg + rbi_pg - cs_pg
        points += (sb_pg * 2.0)
        points += (k_pg / 2.0)
        self.ppg = points

    def divide(self,x,y='G'):
        result = float(self.data[x])/float(self.data[y])
        return(result)


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
        outs_pitched = int(innings_pitched[0])*3 + int(innings_pitched[1])
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


def read_file(fname,pitcher=False):
    players = []
    with open(fname,'r') as f:
        reader = csv.reader(f)
        next(reader)  # Skip header
        for row in reader:
            if pitcher:
                p = Pitcher(*row)
            else:
                p = Player(*row)
            players.append(p)
    return(players)

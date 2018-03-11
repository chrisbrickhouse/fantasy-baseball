import random
import data_reader
import numpy as np

class Team():
    def __init__(self):
        self.players = []
        self.positions = {
            'P': [],
            'C': [],
            '1B': [],
            '2B': [],
            '3B': [],
            'SS': [],
            'OF': [],
            'DH': [],
        }
        self.positions_min = {
            'P': 9,
            'C': 1,
            '1B': 1,
            '2B': 1,
            '3B': 1,
            'SS': 1,
            'OF': 4,
            'DH': 0,
        }

    def draft_random(self, draftables):
        i = random.randint(0,len(draftables)-1)
        pick = draftables.pop(i)
        self.players.append(pick)
        return(draftables)

    def draft(self,draftables,i=0):
        if i >= len(draftables):
            # If reach bottom of list and no proper pick, choose randomly.
            i = random.randint(0,len(draftables)-1)
            pick = draftables.pop(i)
            self.players.append(pick)
            return(draftables)
        ps = self.positions
        pmin = self.positions_min
        positions = draftables[i].positions
        for pos in positions:
            if len(ps[pos]) < pmin[pos]:
                # If player plays position not yet filled, draft them.
                pick = draftables.pop(i)
                self.players.append(pick)
                self.positions[pos].append(pick)
                return(draftables)
        for pos in ps:
            if len(ps[pos]) < pmin[pos]:
                # If not all positions are full, see if the next best player
                #   fills the niche.
                i+=1
                draftables = self.draft(draftables,i)
                return(draftables)
        # If position minimums are all filled, draft the player
        pick = draftables.pop(i)
        self.players.append(pick)
        return(draftables)

    def sim_game(self,r=False):
        players = self.players
        total_points = 0
        for player in players:
            player.sim_plays += 1
            pscore = self._player_score(player)
            player.sim_data.append(pscore)
            total_points += pscore
        self.score = total_points
        if r:
            return(total_points)
        else:
            return()

    def reset(self):
        self.players = []
        self.positions = {
            'P': [],
            'C': [],
            '1B': [],
            '2B': [],
            '3B': [],
            'SS': [],
            'OF': [],
            'DH': [],
        }
        self.positions_min = {
            'P': 9,
            'C': 1,
            '1B': 1,
            '2B': 1,
            '3B': 1,
            'SS': 1,
            'OF': 4,
            'DH': 0,
        }

    def _player_score(self,player):
        if 'P' in player.positions:
            opg = player.random_poisson('OP')
            wpg = player.random_poisson('W')
            lpg = player.random_poisson('L')
            spg = player.random_poisson('SV')
            kpg = player.random_poisson('K')
            hpg = player.random_poisson('HA')
            hbpg = player.random_poisson('HB')
            erpg = player.random_poisson('ER')
            bbpg = player.random_poisson('BB')
            points = player.score(opg,hpg,hbpg,bbpg,wpg,erpg,lpg,spg,kpg)
        else:
            tb = player.random_poisson('TB')
            r = player.random_poisson('R')
            bb = player.random_poisson('BB')
            rbi = player.random_poisson('RBI')
            cs = player.random_poisson('CS')
            sb = player.random_poisson('SB')
            k = player.random_poisson('K')
            points = player.score(tb,r,bb,rbi,cs,sb,k)
        return(points)

players = data_reader.read_file('./2017Players.csv')
for p in players:
    p.points_per_game()
pitchers = data_reader.read_file('./2017Pitchers.csv',True)
for p in pitchers:
    p.points_per_game()

players = [x for x in players if not x.pitcher]
pitchers.sort(key=lambda x: x.ppg,reverse=True)
players.sort(key=lambda x: x.ppg,reverse=True)
my_team = Team()
other_team = Team()
teams = [my_team,other_team]
no_plays = [x for x in players+pitchers if x.sim_plays < 50]
while len(no_plays) > 0:
    topPosPlayers = players[:250]
    topPitchers = pitchers[:250]
    top500 = topPitchers+topPosPlayers
    top500.sort(key=lambda x: x.ppg,reverse=True)

    random.shuffle(teams)
    on_clock = 0

    for i in range(50):
        t = teams[on_clock]
        top500 = t.draft_random(top500)
        on_clock ^= 1

    for team in teams:
        team.sim_game()
    if teams[0].score > teams[1].score:
        for player in teams[0].players:
            player.sim_wins += 1
    else:
        for player in teams[1].players:
            player.sim_wins += 1
    for team in teams:
        team.reset()
    no_plays = [x for x in top500 if x.sim_plays < 50]

for _ in range(500):
    draftlist = top500[:]
    for p in draftlist:
        p.ppg_stats()
    draftlist.sort(key=lambda x: x.ucb, reverse=True)

    random.shuffle(teams)
    on_clock = 0

    for i in range(50):
        t = teams[on_clock]
        draftlist = t.draft(draftlist)
        on_clock ^= 1

    for team in teams:
        team.sim_game()
    if teams[0].score > teams[1].score:
        for player in teams[0].players:
            player.sim_wins += 1
    else:
        for player in teams[1].players:
            player.sim_wins += 1
    for team in teams:
        team.reset()

for p in draftlist:
    p.ppg_stats()
pitcher_output = [x for x in draftlist if 'P' in x.positions]
player_output = [x for x in draftlist if 'P' not in x.positions]
pitcher_output.sort(key=lambda x: x.lcb, reverse=True)
player_output.sort(key=lambda x: x.lcb, reverse=True)
print('=========Pitchers========')
for x in pitcher_output[:25]:
    print(x.name,x.positions,np.mean(x.sim_data))
print('=========Fielders========')
for x in player_output[:50]:
    print(x.name,x.positions,np.mean(x.sim_data))

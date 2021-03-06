import pygame
import pygame.freetype

class Leader(pygame.sprite.Sprite):
    maingame = None

    def __init__(self, leaderid, squadposition, armyposition, battalion, leaderstat):
        self._layer = 10
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.morale = 100
        stat = leaderstat.leaderlist[leaderid]
        self.gameid = leaderid  # Different than unit game id, leadergameid is only used as reference to the id data
        self.name = stat[0]
        self.health = stat[1]
        self.authority = stat[2]
        self.meleecommand = stat[3]
        self.rangecommand = stat[4]
        self.cavcommand = stat[5]
        self.combat = stat[6] * 10
        self.social = leaderstat.leaderclass[stat[7]]
        self.description = stat[-1]
        self.squadpos = squadposition  # Squad position is the index of squad in squad sprite loop
        # self.trait = stat
        # self.skill = stat
        self.state = 0  ## 0 = alive, 96 = retreated, 97 = captured, 98 = missing, 99 = wound, 100 = dead
        if self.name == "none":
            self.health = 0
            self.state = 100  ## no leader is same as dead so no need to update
        self.battalion = battalion
        # self.mana = stat
        self.gamestart = 0
        self.armyposition = armyposition
        self.baseimgposition = [(134, 185), (80, 235), (190, 235), (134, 283)]
        self.imgposition = self.baseimgposition[self.armyposition]
        ## put leader image into leader slot
        try:
            self.fullimage = leaderstat.imgs[leaderstat.imgorder.index(leaderid)].copy()
        except:  ## Use Unknown leader image if there is none in list
            self.fullimage = leaderstat.imgs[-1].copy()
        self.image = pygame.transform.scale(self.fullimage, (50, 50))
        self.rect = self.image.get_rect(center=self.imgposition)
        self.image_original = self.image.copy()
        self.badmorale = (20, 30)  ## other position morale lost
        self.commander = False
        self.originalcommander = False
        if self.armyposition == 0:
            squadpenal = int((self.squadpos / len(self.battalion.armysquad[0])) * 10) # Authority get reduced the further leader stay in the back line
            self.authority = self.authority - ((self.authority * squadpenal / 100) / 2)
            self.badmorale = (30, 50)  ## main general morale lost when die
            if self.battalion.commander:
                self.commander = True
                self.originalcommander = True

    def poschangestat(self, leader):
        """Change stat that related to army position such as in leader dead event"""
        leader.badmorale = (20, 30)  ## sub general morale lost for bad event
        if leader.armyposition == 0:
            squadpenal = int((leader.squadpos / len(leader.battalion.armysquad[0])) * 10)
            leader.authority = leader.authority - ((leader.authority * squadpenal / 100) / 2)
            leader.badmorale = (30, 50)  ## main general morale lost for bad event

    def gone(self):
        eventtext = {96:"retreat",97:"captured",98:"missing",99:"wounded",100:"dead"}
        if self.commander and self.battalion.leader[3].state not in (96, 97, 98, 99, 100) and self.battalion.leader[3].name != "None":
            ## If commander die will use strategist as next commander first
            print('test')
            self.battalion.leader[0], self.battalion.leader[3] = self.battalion.leader[3], self.battalion.leader[0]
        elif self.battalion.leader[1].state not in (96, 97, 98, 99, 100) and self.battalion.leader[1].name != "None":
            self.battalion.leader.append(self.battalion.leader.pop(self.armyposition))  ## move leader to last of list when dead
        thisbadmorale = self.badmorale[0]
        if self.state == 99: # wonnd inflict less morale penalty
            thisbadmorale = self.badmorale[1]
        for squad in self.battalion.squadsprite:
            squad.basemorale -= thisbadmorale  ## decrease all squad morale when leader die depending on position
        if self.commander:  ## reduce morale to whole army if commander die from the dmg (leader die cal is in gameleader.py)
            self.maingame.textdrama.queue.append(str(self.name) + " is " + eventtext[self.state])
            eventmapid = "ld0"
            whicharmy = self.maingame.playerarmy
            if self.battalion.gameid >= 2000:
                whicharmy = self.maingame.enemyarmy
                eventmapid = "ld1"
            if self.originalcommander:
                self.maingame.eventlog.addlog([0, "Commander " + str(self.name) + " is " + eventtext[self.state]], [0, 1, 2], eventmapid)
            else: self.maingame.eventlog.addlog([0, "Commander " + str(self.name) + " is " + eventtext[self.state]], [0, 1, 2])
            for army in whicharmy:
                for squad in army.squadsprite:
                    squad.basemorale -= 100
        else:
            self.maingame.eventlog.addlog([0, str(self.name) + " is " + eventtext[self.state]], [0, 2])
        for index, leader in enumerate(self.battalion.leader):  ## also change army position of all leader in that battalion
            leader.armyposition = index  ## change army position to new one
            if self.battalion.commander and leader.armyposition == 0:
                self.commander = True
            leader.imgposition = leader.baseimgposition[leader.armyposition]
            leader.rect = leader.image.get_rect(center=leader.imgposition)
            self.poschangestat(leader)
        self.battalion.commandbuff = [(self.battalion.leader[0].meleecommand - 5) * 0.1, (self.battalion.leader[0].rangecommand - 5) * 0.1,
                                      (self.battalion.leader[0].cavcommand - 5) * 0.1]
        self.authority = 0
        self.meleecommand = 0
        self.rangecommand = 0
        self.cavcommand = 0
        self.combat = 0
        self.social = 0
        pygame.draw.line(self.image, (150, 20, 20), (5, 5), (45, 35), 5)
        self.maingame.setuparmyicon()
        self.battalion.leaderchange = True

    def update(self):
        if self.gamestart == 0:
            self.squad = self.battalion.squadsprite[self.squadpos]
            self.gamestart = 1
        if self.state not in (96, 97, 98, 99, 100):
            if self.health <= 0:
                self.health = 0
                self.state = 100
                # if random.randint(0,1) == 1: self.state = 99 ## chance to become wound instead when hp reach 0
                self.gone()
        

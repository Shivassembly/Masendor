import csv
import datetime
import random
import ast
import re
import numpy as np
import pygame
import pygame.freetype
import os
import main

config = main.config
SoundVolume = main.Soundvolume
SCREENRECT = main.SCREENRECT
main_dir = main.main_dir

## Data Loading gamescript

def load_image(file, subfolder=""):
    """loads an image, prepares it for play"""
    thisfile = os.path.join(main_dir, 'data', subfolder, file)
    try:
        surface = pygame.image.load(thisfile).convert_alpha()
    except pygame.error:
        raise SystemExit('Could not load image "%s" %s' % (thisfile, pygame.get_error()))
    return surface.convert_alpha()

def load_images(subfolder=[], loadorder=True, returnorder=False):
    """loads all images(files) in folder using loadorder list file use only png file"""
    imgs = []
    dirpath = os.path.join(main_dir, 'data')
    if subfolder != []:
        for folder in subfolder:
            dirpath = os.path.join(dirpath, folder)
    if loadorder:
        loadorderfile = open(dirpath + "/load_order.txt", "r")
        loadorderfile = ast.literal_eval(loadorderfile.read())
        for file in loadorderfile:
            imgs.append(load_image(dirpath + "/" + file))
    else:
        loadorderfile = [f for f in os.listdir(dirpath) if f.endswith('.' + "png")]  ## read all file
        loadorderfile.sort(key=lambda var: [int(x) if x.isdigit() else x for x in re.findall(r'[^0-9]|[0-9]+', var)])
        for file in loadorderfile:
            imgs.append(load_image(dirpath + "/" + file))
    if returnorder == False:
        return imgs
    else:
        loadorderfile = [int(name.replace(".png", "")) for name in loadorderfile]
        return imgs, loadorderfile


def csv_read(file, subfolder=[], outputtype=0):
    """output type 0 = dict, 1 = list"""
    returnoutput = {}
    if outputtype == 1: returnoutput = []
    folderlist = ""
    for folder in subfolder:
        folderlist += "\\" + folder
    folderlist += "\\" + file
    with open(main_dir + folderlist, 'r') as unitfile:
        rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
        for row in rd:
            for n, i in enumerate(row):
                if i.isdigit() or ("-" in i and re.search('[a-zA-Z]', i) is None):
                    row[n] = int(i)
            if outputtype == 0:
                returnoutput[row[0]] = row[1:]
            elif outputtype == 1:
                returnoutput.append(row)
        unitfile.close()
    return returnoutput


def load_sound(file):
    file = os.path.join(main_dir, "data/sound/", file)
    sound = pygame.mixer.Sound(file)
    return sound


## Other battle gamescript

def convertweathertime(weatherevent):
    for index, item in enumerate(weatherevent):
        newtime = datetime.datetime.strptime(item[1], '%H:%M:%S').time()
        newtime = datetime.timedelta(hours=newtime.hour, minutes=newtime.minute, seconds=newtime.second)
        weatherevent[index] = [item[0], newtime, item[2]]


## Battle Start related gamescript

def addarmy(squadlist, position, gameid, colour, imagesize, leader, leaderstat, unitstat, control, coa, command=False, startangle=0):
    from gamescript import gamebattalion, gameleader
    squadlist = squadlist[~np.all(squadlist == 0, axis=1)]
    squadlist = squadlist[:, ~np.all(squadlist == 0, axis=0)]
    army = gamebattalion.Unitarmy(startposition=position, gameid=gameid,
                                  squadlist=squadlist, imgsize=imagesize,
                                  colour=colour, control=control, coa=coa, commander=command, startangle=abs(360 - startangle))
    army.hitbox = [gamebattalion.Hitbox(army, 0, army.rect.width - int(army.rect.width * 0.1), 5),
                   gamebattalion.Hitbox(army, 1, 5, army.rect.height - int(army.rect.height * 0.1)),
                   gamebattalion.Hitbox(army, 2, 5, army.rect.height - int(army.rect.height * 0.1)),
                   gamebattalion.Hitbox(army, 3, army.rect.width - int(army.rect.width * 0.1), 5)]
    army.leader = [gameleader.Leader(leader[0], leader[4], 0, army, leaderstat),
                   gameleader.Leader(leader[1], leader[5], 1, army, leaderstat),
                   gameleader.Leader(leader[2], leader[6], 2, army, leaderstat),
                   gameleader.Leader(leader[3], leader[7], 3, army, leaderstat)]
    return army


def unitsetup(maingame):
    from gamescript import gamesquad
    """squadindexlist is list of every squad index in the game for indexing the squad group"""
    # defaultarmy = np.array([[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0]])
    letterboard = ("a", "b", "c", "d", "e", "f", "g", "h")
    numberboard = ("8", "7", "6", "5", "4", "3", "2", "1")
    boardpos = []
    for dd in numberboard:
        for ll in letterboard:
            boardpos.append(ll + dd)
    squadindexlist = []
    unitlist = []
    playercolour = (144, 167, 255)
    enemycolour = (255, 114, 114)
    """army num is list index for battalion in either player or enemy group"""
    playerstart, enemystart = 0, 0
    """squadindex is list index for all squad group"""
    squadindex = 0
    """firstsquad check if it the first ever in group"""
    squadgameid = 10000
    with open(main_dir + "\data\\ruleset" + maingame.rulesetfolder + "\map\\" + maingame.mapselected + "\\unit_pos.csv", 'r') as unitfile:
        rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
        for row in rd:
            for n, i in enumerate(row):
                if i.isdigit():
                    row[n] = int(i)
                if n in range(1, 12):
                    row[n] = [int(item) if item.isdigit() else item for item in row[n].split(',')]
            if row[0] < 2000:
                if row[0] == 1:
                    """First player battalion as commander"""
                    army = addarmy(np.array([row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8]]), (row[9][0], row[9][1]), row[0],
                                   playercolour,
                                   (maingame.imagewidth, maingame.imageheight), row[10] + row[11], maingame.allleader, maingame.gameunitstat, True,
                                   maingame.coa[row[12]], True,
                                   startangle=row[13])
                else:
                    army = addarmy(np.array([row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8]]), (row[9][0], row[9][1]), row[0],
                                   playercolour, (maingame.imagewidth, maingame.imageheight), row[10] + row[11], maingame.allleader,
                                   maingame.gameunitstat, True, maingame.coa[row[12]],
                                   startangle=row[13])
                maingame.playerarmy.append(army)
                playerstart += 1
            elif row[0] >= 2000:
                if row[0] == 2000:
                    """First enemy battalion as commander"""
                    army = addarmy(np.array([row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8]]), (row[9][0], row[9][1]), row[0],
                                   enemycolour,
                                   (maingame.imagewidth, maingame.imageheight), row[10] + row[11], maingame.allleader, maingame.gameunitstat,
                                   maingame.enactment, maingame.coa[row[12]], True,
                                   startangle=row[13])
                elif row[0] > 2000:
                    army = addarmy(np.array([row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8]]), (row[9][0], row[9][1]), row[0],
                                   enemycolour,
                                   (maingame.imagewidth, maingame.imageheight), row[10] + row[11], maingame.allleader, maingame.gameunitstat,
                                   maingame.enactment, maingame.coa[row[12]], startangle=row[13])
                maingame.enemyarmy.append(army)
                enemystart += 1
            """armysquadindex is list index for squad list in a specific army"""
            armysquadindex = 0
            """Setup squad in army to squad group"""
            for squadnum in np.nditer(army.armysquad, op_flags=['readwrite'], order='C'):
                if squadnum != 0:
                    addsquad = gamesquad.Unitsquad(unitid=squadnum, gameid=squadgameid, weaponlist=maingame.allweapon, armourlist=maingame.allarmour,
                                                   statlist=maingame.gameunitstat,
                                                   battalion=army, position=army.squadpositionlist[armysquadindex],
                                                   inspectuipos=maingame.inspectuipos)
                    maingame.squad.append(addsquad)
                    addsquad.boardpos = boardpos[armysquadindex]
                    squadnum[...] = squadgameid
                    army.squadsprite.append(addsquad)
                    squadindexlist.append(squadgameid)
                    squadgameid += 1
                    squadindex += 1
                armysquadindex += 1
    unitfile.close()
    return squadindexlist

## Battle related gamescript

def squadcombatcal(who, squadlist, squadindexlist, target, whoside, targetside):
    """calculate squad engagement using information after battalionengage who is player battalion, target is enemy battalion"""
    squadtargetside = [2 if targetside == 3 else 3 if targetside == 2 else targetside][0]
    whofrontline = who.frontline[whoside]
    """only calculate if the attack is attack with the front side"""
    if whoside == 0:
        sortmidfront = [whofrontline[3], whofrontline[4], whofrontline[2], whofrontline[5],
                        whofrontline[1], whofrontline[6], whofrontline[0], whofrontline[7]]
        combatpositioncal(squadlist, squadindexlist, sortmidfront, who, target, whoside, targetside, squadtargetside)

def combatpositioncal(squadlist, squadindexlist, sortmidfront, attacker, receiver, attackerside, receiverside, squadside):
    for thiswho in sortmidfront:
        if thiswho > 1:
            position = np.where(attacker.frontline[attackerside] == thiswho)[0][0]
            fronttarget = receiver.frontline[receiverside][position]
            """check if squad not already fighting if true skip picking new enemy """
            attackersquad = squadlist[np.where(squadindexlist == thiswho)[0][0]]
            if any(battle > 1 for battle in attackersquad.battlesideid) == False:
                """get front of another battalion frontline to assign front combat if it 0 squad will find another unit on the left or right"""
                if fronttarget > 1:
                    receiversquad = squadlist[np.where(squadindexlist == fronttarget)[0][0]]
                    """only attack if the side is already free else just wait until it free"""
                    if receiversquad.battlesideid[squadside] == 0:
                        attackersquad.battleside[attackerside] = receiversquad
                        attackersquad.battlesideid[attackerside] = fronttarget
                        receiversquad.battleside[squadside] = attackersquad
                        receiversquad.battlesideid[squadside] = thiswho
                else:
                    """pick flank attack if no enemy already fighting and not already fighting"""
                    chance = random.randint(0, 1)
                    secondpick = 0
                    if chance == 0: secondpick = 1
                    """attack left array side of the squad if get random 0, right if 1"""
                    truetargetside = changecombatside(chance, receiverside)
                    fronttarget = squadselectside(receiver.frontline[receiverside], chance, position)
                    if fronttarget > 1: # attack if the found defender at that side is free if not check other side
                        receiversquad = squadlist[np.where(squadindexlist == fronttarget)[0][0]]
                        if receiversquad.battlesideid[truetargetside] == 0:
                            attackersquad.battleside[attackerside] = receiversquad
                            attackersquad.battlesideid[attackerside] = fronttarget
                            receiversquad.battleside[truetargetside] = attackersquad
                            receiversquad.battlesideid[truetargetside] = thiswho
                    else: # Switch to another side if above not found
                        truetargetside = changecombatside(secondpick, receiverside)
                        fronttarget = squadselectside(receiver.frontline[receiverside], secondpick, position)
                        if fronttarget > 1:
                            receiversquad = squadlist[np.where(squadindexlist == fronttarget)[0][0]]
                            if receiversquad.battlesideid[truetargetside] == 0:
                                attackersquad.battleside[attackerside] = receiversquad
                                attackersquad.battlesideid[attackerside] = fronttarget
                                receiversquad.battleside[truetargetside] = attackersquad
                                receiversquad.battlesideid[truetargetside] = thiswho
                        else:
                            attackersquad.battleside[attackerside] = None
                            attackersquad.battlesideid[attackerside] = 0

def squadselectside(targetside, side, position):
    """side 0 is left 1 is right"""
    thisposition = position
    if side == 0:
        max = 0 # keep searching to the the left until reach the first squad
        while targetside[thisposition] <= 1 and thisposition != max:
            thisposition -= 1
    else:
        max = 7 # keep searching to the the right until reach the last squad
        while targetside[thisposition] <= 1 and thisposition != max:
            thisposition += 1
    if thisposition < 0:
        thisposition = 0
    elif thisposition > 7:
        thisposition = 7
    fronttarget = 0
    if targetside[thisposition] != 0:
        fronttarget = targetside[thisposition]
    return fronttarget

def changecombatside(side, position):
    """position is attacker position against defender 0 = front 1 = left 2 = rear 3 = right"""
    """side is side of attack for rotating to find the correct side the defender got attack accordingly (e.g. left attack on right side is front)"""
    subposition = position
    if subposition == 2:
        subposition = 3
    elif subposition == 3:
        subposition = 2
    changepos = 1
    if subposition == 2:
        changepos = -1
    finalposition = subposition + changepos  ## right
    if side == 0: finalposition = subposition - changepos  ## left
    if finalposition == -1:
        finalposition = 3
    elif finalposition == 4:
        finalposition = 0
    return finalposition

def losscal(attacker, defender, hit, defense, type, defside = None):
    """Calculate damage"""
    who = attacker
    target = defender
    heightadventage = who.battalion.height - target.battalion.height
    if type == 1: heightadventage = int(heightadventage / 2)
    hit += heightadventage
    if defense < 0 or who.ignoredef: defense = 0  ## Ignore def trait
    hitchance = hit - defense
    if hitchance < 0: hitchance = 0
    elif hitchance > 200: hitchance = 200
    combatscore = round(hitchance / 50, 1)
    if combatscore == 0 and random.randint(0, 10) > 9:  ## Final chence to not miss
        combatscore = 0.1
    leaderdmgbonus = 0
    if who.leader is not None: leaderdmgbonus = who.leader.combat
    if type == 0:  # Melee damage
        dmg = who.dmg
        if who.charging: ## Include charge in dmg if charging
            if who.ignorechargedef == False: ## Ignore charge defense if have ignore trait
                sidecal = who.battlesidecal[defside]
                if target.fulldef == True:
                    sidecal = 1
                dmg = dmg + (who.charge / 10) - (target.chargedef * sidecal / 10)
            elif who.ignorechargedef:
                dmg = dmg + (who.charge / 10)
        dmg = dmg * ((100 - (target.armour * who.penetrate)) / 100) * combatscore
        if target.state == 10: dmg = dmg / 5 ## More dmg against enemy not fighting
    elif type == 1:  # Range Damage
        dmg = who.rangedmg * ((100 - (target.armour * who.rangepenetrate)) / 100) * combatscore
    leaderdmg = dmg
    unitdmg = (dmg * who.troopnumber) + leaderdmgbonus
    if (who.antiinf and target.type in (1, 2)) or (who.anticav and target.type in (4, 5, 6, 7)):  # Anti trait dmg bonus
        unitdmg = unitdmg * 1.25
    if type == 0:
        unitdmg = unitdmg / 10
    moraledmg = dmg / 20
    if unitdmg < 0:
        unitdmg = 0
    if leaderdmg < 0:
        leaderdmg = 0
    if moraledmg < 0:
        moraledmg = 0
    return unitdmg, moraledmg, leaderdmg


def applystatustoenemy(statuslist, inflictstatus, receiver, attackerside):
    for status in inflictstatus.items():
        if status[1] == 1 and attackerside == 0:
            receiver.statuseffect[status[0]] = statuslist[status[0]].copy()
        elif status[1] in (2, 3):
            receiver.statuseffect[status[0]] = statuslist[status[0]].copy()
            if status[1] == 3:
                for squad in receiver.nearbysquadlist[0:2]:
                    if squad != 0:
                        squad.statuseffect[status[0]] = statuslist[status[0]].copy()
        elif status[1] == 4:
            for squad in receiver.battalion.spritearray.flat:
                if squad.state != 100:
                    squad.statuseffect[status[0]] = statuslist[status[0]].copy()

def complexdmg(attacker, receiver, dmg, moraledmg, leaderdmg, dmgeffect, timermod):
    targetdmg = round(dmg * dmgeffect * timermod)
    targetmoraledmg = round(moraledmg * dmgeffect * timermod)
    if targetdmg > receiver.unithealth:
        targetdmg = receiver.unithealth
    receiver.unithealth -= targetdmg
    receiver.basemorale -= targetmoraledmg
    if attacker.elemmelee not in (0, 5):  # apply element effect if atk has element
        receiver.elemcount[attacker.elemmelee - 1] += round(targetdmg * (100 - receiver.elemresist[attacker.elemmelee - 1] / 100))
    attacker.basemorale += round((targetmoraledmg / 5)) # recover some morale when deal morale dmg to enemy
    if receiver.leader is not None and receiver.leader.health > 0 and random.randint(0, 10) > 8:  # dmg on squad leader
        targetleaderdmg = round(leaderdmg - (leaderdmg * receiver.leader.combat/101) * timermod)
        if targetleaderdmg > receiver.leader.health:
            targetleaderdmg = receiver.leader.health
        receiver.leader.health -= targetleaderdmg


def dmgcal(who, target, whoside, targetside, statuslist, combattimer):
    """target position 0 = Front, 1 = Side, 3 = Rear, whoside and targetside is the side attacking and defending respectively"""
    wholuck = random.randint(-50, 50) # attacker luck
    targetluck = random.randint(-50, 50) # defender luck
    whopercent = who.battlesidecal[whoside] # attacker attack side modifier
    """34 battlemaster no flanked penalty"""
    if who.fulldef or 91 in who.statuseffect: whopercent = 1
    targetpercent = who.battlesidecal[targetside] # defender defend side modifier
    if target.fulldef or 91 in target.statuseffect: targetpercent = 1
    dmgeffect = who.frontdmgeffect
    targetdmgeffect = target.frontdmgeffect
    if whoside != 0 and whopercent != 1:  # if attack or defend from side will use discipline to help reduce penalty a bit
        whopercent = who.battlesidecal[whoside] + (who.discipline / 300)
        dmgeffect = who.sidedmgeffect
        if whopercent > 1: whopercent = 1
    if targetside != 0 and targetpercent != 1: # same for the target
        targetpercent = who.battlesidecal[targetside] + (target.discipline / 300)
        targetdmgeffect = target.sidedmgeffect
        if targetpercent > 1: targetpercent = 1
    whohit, whodefense = float(who.attack * whopercent) + wholuck, float(who.meleedef * whopercent) + wholuck
    targethit, targetdefense = float(who.attack * targetpercent) + targetluck, float(target.meleedef * targetpercent) + targetluck
    """33 backstabber ignore def when atk rear, 55 Oblivious To Unexpected can't def from rear"""
    if (who.backstab and targetside == 2) or (target.oblivious and targetside == 2) or (
            target.flanker and whoside in (1, 3)): # Apply only for attacker
        targetdefense = 0
    whodmg, whomoraledmg, wholeaderdmg = losscal(who, target, whohit, targetdefense, 0, targetside) # get dmg by attacker
    targetdmg, targetmoraledmg, targetleaderdmg = losscal(target, who, targethit, whodefense, 0, whoside) # get dmg by defender
    timermod = combattimer / 0.5 # since the update happen anytime more than 0.5 second, high speed that pass by longer than x1 speed will become inconsistent
    complexdmg(who, target, whodmg, whomoraledmg, wholeaderdmg, targetdmgeffect, timermod) # inflict dmg to defender
    complexdmg(target, who, targetdmg, targetmoraledmg, targetleaderdmg, dmgeffect, timermod) # inflict dmg to attacker
    if who.corneratk:  # Attack corner (side) of self with aoe attack
        listloop = target.nearbysquadlist[2:4]
        if targetside in (0, 2): listloop = target.nearbysquadlist[0:2]
        for squad in listloop:
            if squad != 0 and squad.state != 100:
                targethit, targetdefense = float(who.attack * targetpercent) + targetluck, float(squad.meleedef * targetpercent) + targetluck
                whodmg, whomoraledmg = losscal(who, squad, whohit, targetdefense, 0)
                squad.unithealth -= round(whodmg * dmgeffect)
                squad.basemorale -= whomoraledmg
    ## inflict status based on aoe 1 = front only 2 = all 4 side, 3 corner enemy unit, 4 entire battalion
    if who.inflictstatus != {}:
        applystatustoenemy(statuslist, who.inflictstatus, target, whoside)
    if target.inflictstatus != {}:
        applystatustoenemy(statuslist, target.inflictstatus, who, targetside)
    ## End inflict status


def die(who, battle, group, enemygroup):
    """remove battalion,hitbox when it dies"""
    battle.deadindex += 1
    if who.gameid < 2000:
        battle.playerposlist.pop(who.gameid)
    else:
        battle.enemyposlist.pop(who.gameid)
    if who.commander:  ## more morale penalty if the battalion is a command battalion
        for army in group:
            for squad in army.squadsprite:
                squad.basemorale -= 30
    for hitbox in who.hitbox:
        battle.allcamera.remove(hitbox)
        battle.hitboxes.remove(hitbox)
        hitbox.kill()
    battle.allunitlist.remove(who)
    battle.allunitindex.remove(who.gameid)
    group.remove(who)
    battle.deadunit.add(who)
    battle.allcamera.change_layer(sprite=who, new_layer=1)
    who.gotkilled = 1
    for thisarmy in enemygroup:  ## get bonus authority to the another army
        thisarmy.authority += 5
    for thisarmy in group:  ## morale dmg to every squad in army when allied battalion destroyed
        for squad in thisarmy.squadsprite:
            squad.basemorale -= 20


def splitunit(battle, who, how):
    """split battalion either by row or column into two seperate battalion"""
    from gamescript import gamebattalion, gameleader
    if how == 0:  ## split by row
        newarmysquad = np.array_split(who.armysquad, 2)[1]
        who.armysquad = np.array_split(who.armysquad, 2)[0]
        who.squadalive = np.array_split(who.squadalive, 2)[0]
        newpos = who.allsidepos[3] - ((who.allsidepos[3] - who.basepos) / 2)
        who.basepos = who.allsidepos[0] - ((who.allsidepos[0] - who.basepos) / 2)
    else:  ## split by column
        newarmysquad = np.array_split(who.armysquad, 2, axis=1)[1]
        who.armysquad = np.array_split(who.armysquad, 2, axis=1)[0]
        who.squadalive = np.array_split(who.squadalive, 2, axis=1)[0]
        newpos = who.allsidepos[2] - ((who.allsidepos[2] - who.basepos) / 2)
        who.basepos = who.allsidepos[1] - ((who.allsidepos[1] - who.basepos) / 2)
    if who.leader[1].squad.gameid not in newarmysquad:  ## move leader if squad not in new one
        if who.leader[1].squad.unittype in (1, 3, 5, 6, 7, 10, 11):  ## if squad type melee move to front
            leaderreplace = [np.where(who.armysquad == who.leader[1].squad.gameid)[0][0],
                             np.where(who.armysquad == who.leader[1].squad.gameid)[1][0]]
            leaderreplaceflat = np.where(who.armysquad.flat == who.leader[1].squad.gameid)[0]
            who.armysquad[leaderreplace[0]][leaderreplace[1]] = newarmysquad[0][int(len(newarmysquad[0]) / 2)]
            newarmysquad[0][int(len(newarmysquad[0]) / 2)] = who.leader[1].squad.gameid
        else:  ## if not move to center of battalion
            leaderreplace = [np.where(who.armysquad == who.leader[1].squad.gameid)[0][0],
                             np.where(who.armysquad == who.leader[1].squad.gameid)[1][0]]
            leaderreplaceflat = np.where(who.armysquad.flat == who.leader[1].squad.gameid)[0]
            who.armysquad[leaderreplace[0]][leaderreplace[1]] = newarmysquad[int(len(newarmysquad) / 2)][int(len(newarmysquad[0]) / 2)]
            newarmysquad[int(len(newarmysquad) / 2)][int(len(newarmysquad[0]) / 2)] = who.leader[1].squad.gameid
        who.squadalive[leaderreplace[0]][leaderreplace[1]] = \
            [0 if who.armysquad[leaderreplace[0]][leaderreplace[1]] == 0 else 1 if who.squadsprite[leaderreplaceflat[0]].state == 100 else 2][0]
    squadsprite = [squad for squad in who.squadsprite if squad.gameid in newarmysquad]  ## list of sprite not sorted yet
    newsquadsprite = []
    for squadindex in newarmysquad.flat:  ## sort so the new leader squad position match what set before
        for squad in squadsprite:
            if squad.gameid == squadindex:
                newsquadsprite.append(squad)
                break
    who.squadsprite = [squad for squad in who.squadsprite if squad.gameid in who.armysquad]
    for thissprite in (who.squadsprite, newsquadsprite):  ## reset position in inspectui for both battalion
        width, height = 0, 0
        squadnum = 0
        for squad in thissprite:
            width += battle.imagewidth
            if squadnum >= len(who.armysquad[0]):
                width = 0
                width += battle.imagewidth
                height += battle.imageheight
                squadnum = 0
            squad.inspposition = (width + battle.inspectuipos[0], height + battle.inspectuipos[1])
            squad.rect = squad.image.get_rect(topleft=squad.inspposition)
            squad.pos = pygame.Vector2(squad.rect.centerx, squad.rect.centery)
            squadnum += 1
    newleader = [who.leader[1], gameleader.Leader(1, 0, 1, who, battle.allleader), gameleader.Leader(1, 0, 2, who, battle.allleader),
                 gameleader.Leader(1, 0, 3, who, battle.allleader)]
    who.leader = [who.leader[0], who.leader[2], who.leader[3], gameleader.Leader(1, 0, 3, who, battle.allleader)]
    for index, leader in enumerate(who.leader):  ## also change army position of all leader in that battalion
        leader.armyposition = index  ## change army position to new one
        leader.imgposition = leader.baseimgposition[leader.armyposition]
        leader.rect = leader.image.get_rect(center=leader.imgposition)
    coa = who.coa
    who.recreatesprite()
    who.makeallsidepos()
    who.setupfrontline()
    who.viewmode = battle.camerascale
    who.viewmodechange()
    who.height = who.gamemapheight.getheight(who.basepos)
    for thishitbox in who.hitbox: thishitbox.kill()
    who.hitbox = [gamebattalion.Hitbox(who, 0, who.rect.width - (who.rect.width * 0.1), 1),
                  gamebattalion.Hitbox(who, 1, 1, who.rect.height - (who.rect.height * 0.1)),
                  gamebattalion.Hitbox(who, 2, 1, who.rect.height - (who.rect.height * 0.1)),
                  gamebattalion.Hitbox(who, 3, who.rect.width - (who.rect.width * 0.1), 1)]
    who.rotate()
    who.newangle = who.angle
    ## need to recal max stat again for the original battalion
    maxhealth = []
    maxstamina = []
    maxmorale = []
    for squad in who.squadsprite:
        maxhealth.append(squad.maxtroop)
        maxstamina.append(squad.maxstamina)
        maxmorale.append(squad.maxmorale)
    maxhealth = sum(maxhealth)
    maxstamina = sum(maxstamina) / len(maxstamina)
    maxmorale = sum(maxmorale) / len(maxmorale)
    who.maxhealth, who.health75, who.health50, who.health25, = maxhealth, round(maxhealth * 0.75), round(
        maxhealth * 0.50), round(maxhealth * 0.25)
    who.maxstamina, who.stamina75, who.stamina50, who.stamina25, = maxstamina, round(maxstamina * 0.75), round(
        maxstamina * 0.50), round(maxstamina * 0.25)
    who.maxmorale = maxmorale
    ## start making new battalion
    if who.gameid < 2000:
        playercommand = True
        newgameid = battle.playerarmy[-1].gameid + 1
        colour = (144, 167, 255)
        army = gamebattalion.Unitarmy(startposition=newpos, gameid=newgameid,
                                      squadlist=newarmysquad, imgsize=(battle.imagewidth, battle.imageheight),
                                      colour=colour, control=playercommand, coa=coa, commander=False, startangle=who.angle)
        battle.playerarmy.append(army)
    else:
        playercommand = battle.enactment
        newgameid = battle.enemyarmy[-1].gameid + 1
        colour = (255, 114, 114)
        army = gamebattalion.Unitarmy(startposition=newpos, gameid=newgameid,
                                      squadlist=newarmysquad, imgsize=(battle.imagewidth, battle.imageheight),
                                      colour=colour, control=playercommand, coa=coa, commander=False, startangle=who.angle)
        battle.enemyarmy.append(army)
    army.leader = newleader
    army.squadsprite = newsquadsprite
    for squad in army.squadsprite:
        squad.battalion = army
    for index, leader in enumerate(army.leader):  ## change army position of all leader in new battalion
        if how == 0:
            leader.squadpos -= newarmysquad.size  ## just minus the row gone to find new position
        else:
            if leader.name != "None":
                for index, squad in enumerate(army.squadsprite):  ## loop to find new squad pos based on new squadsprite list
                    if squad.gameid == leader.squad.gameid:
                        leader.squadpos = index
                    break
            else: leader.squadpos = 0
        leader.battalion = army  ## set leader battalion to new one
        leader.armyposition = index  ## change army position to new one
        leader.imgposition = leader.baseimgposition[leader.armyposition]  ## change image pos
        leader.rect = leader.image.get_rect(center=leader.imgposition)
        leader.poschangestat(leader)  ## change stat based on new army position
    army.commandbuff = [(army.leader[0].meleecommand - 5) * 0.1, (army.leader[0].rangecommand - 5) * 0.1, (army.leader[0].cavcommand - 5) * 0.1]
    army.leadersocial = army.leader[0].social
    army.authrecal()
    battle.allunitlist.append(army)
    battle.allunitindex.append(army.gameid)
    army.viewmode = battle.camerascale
    army.recreatesprite()
    army.makeallsidepos()
    army.viewmodechange()
    army.angle = army.angle
    army.rotate()
    army.terrain, army.feature = army.getfeature(army.basepos, army.gamemap)
    army.sidefeature = [army.getfeature(army.allsidepos[0], army.gamemap), army.getfeature(army.allsidepos[1], army.gamemap),
                        army.getfeature(army.allsidepos[2], army.gamemap), army.getfeature(army.allsidepos[3], army.gamemap)]
    army.hitbox = [gamebattalion.Hitbox(army, 0, army.rect.width - (army.rect.width * 0.1), 1),
                   gamebattalion.Hitbox(army, 1, 1, army.rect.height - (army.rect.height * 0.1)),
                   gamebattalion.Hitbox(army, 2, 1, army.rect.height - (army.rect.height * 0.1)),
                   gamebattalion.Hitbox(army, 3, army.rect.width - (army.rect.width * 0.1), 1)]
    army.autosquadplace = False

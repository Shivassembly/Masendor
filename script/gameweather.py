import pygame
import pygame.freetype
import random
from RTS import mainmenu

SCREENRECT = mainmenu.SCREENRECT
main_dir = mainmenu.main_dir

class Weather:
    def __init__(self, type, level, weatherlist):
        self.type = type
        stat = weatherlist[type]
        self.level = level ## Weather level 0 = Light, 1 = Normal, 2 = Strong
        self.meleeatk_buff = stat[1] * (self.level+1)
        self.meleedef_buff = stat[2] * (self.level+1)
        self.rangedef_buff = stat[3] * (self.level+1)
        self.armour_buff = stat[4] * (self.level+1)
        self.speed_buff = stat[5] * (self.level+1)
        self.accuracy_buff = stat[6] * (self.level+1)
        self.reload_buff = stat[7] * (self.level+1)
        self.charge_buff = stat[8] * (self.level+1)
        self.chargedef_buff = stat[9] * (self.level+1)
        self.hpregen_buff = stat[10] * (self.level+1)
        self.staminaregen_buff = stat[11] * (self.level+1)
        self.morale_buff = stat[12] * (self.level+1)
        self.discipline_buff = stat[13] * (self.level+1)
        # self.sight_buff = stat[14] * (self.level+1)
        # self.hidden_buff = stat[15] * (self.level+1)
        self.temperature = stat[16] * (self.level+1)
        self.elem = (stat[17], (self.level+1))
        self.spawnrate = stat[18] * (self.level + 1)
        self.statuseffect = stat[19]
        self.specialeffect = stat[20]
        self.spawnangle = stat[21]
        self.speed = stat[22] * (self.level + 1)

    # def weatherchange(self, level):
    #     self.level = level

class Mattersprite(pygame.sprite.Sprite):
    def __init__(self, pos, target, speed, image):
        self._layer = 7
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.speed = speed
        # if type in (0,1,2):
        #     self.speed =
        self.pos = pygame.Vector2(pos)
        self.target = pygame.Vector2(target)
        self.image = image
        self.rect = self.image.get_rect(center=self.pos)

    def update(self, dt):
        move = self.target - self.pos
        move_length = move.length()
        if move_length > 0.1:
            move.normalize_ip()
            move = move * self.speed  * dt
            if move.length() <= move_length:
                self.pos += move
                self.rect.center = list(int(v) for v in self.pos)
            else:
                self.pos = self.target
                self.rect.center = self.target
        else :
            self.kill()

class Specialeffect(pygame.sprite.Sprite):
    """Special effect from weather beyond sprite such as thunder, fog etc."""
    def __init__(self, pos, image):
        self._layer = 9
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = pygame.Surface(SCREENRECT, pygame.SRCALPHA)
        imagerect = image.get_rect(topleft=(0,0))
        self.image.blit(image,imagerect)

class Supereffect(pygame.sprite.Sprite):
    """Super effect that affect whole screen"""
    def __init__(self, pos, image):
        self._layer = 9
        pygame.sprite.Sprite.__init__(self, self.containers)
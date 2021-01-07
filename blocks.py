"""Import used by index.py to store all block objects."""
import pygame as pg
import utils
import random
pg.init()

SPRITES = { # misc sprites
    "Void": pg.image.load("sprites/Void.png")
}
# full tile sprites
grassdict = utils.make_dict("./sprites/Grass/")
grass_extras_dict = utils.make_dict("./sprites/misc/grassdeco/")
walldict = utils.make_dict("./sprites/Wall/")

class Block():
    """Any tile that inherits from this class will have a choose_sprite method"""
    def choose_sprite(self, position, layout, size):
        """
        0  |  1  |  2  - An 8 binary digit string is stored to denote whether or not a particular 
        3  | pos |  4  - index is occupied by a tile of the same type as the centre tile
        5  |  6  |  7  - 1 is a different tile and 0 is a tile of the same type/style.
        """
        info = [1,1,1,1,1,1,1,1]
        for y in [-1, 0, 1]:
            for x in [-1, 0, 1]:
                blocky = position[1] + y
                blockx = position[0] + x
                if len(layout[0]) >blockx > -1 and len(layout) > blocky > -1:
                    if layout[blocky][blockx].group == self.group:
                        if y == -1 and x == -1:
                            info[0] = 0
                        elif y == -1 and x == 0:
                            info[1] = 0
                        elif y == -1 and x == 1:
                            info[2] = 0
                        elif y == 0 and x == -1:
                            info[3] = 0
                        elif y == 0 and x == 1:
                            info[4] = 0
                        elif y == 1 and x == -1:
                            info[5] = 0
                        elif y == 1 and x == 0:
                            info[6] = 0
                        elif y == 1 and x == 1:
                            info[7] = 0
        id = info.copy()
        if info[1] == 1:
            id[0] = 1
            id[2] = 1
        if info[4] == 1:
            id[2] = 1
            id[7] = 1
        if info[3] == 1:
            id[0] = 1
            id[5] = 1
        if info[6] == 1:
            id[5] = 1
            id[7] = 1
        self.sprite = pg.transform.scale(self.spritedict[str(id).strip("[]").replace(", ", "")], (size, size))
        self.do_additional_generation(position, layout, size)

    def do_additional_generation(self, position, layout, size):
        return

class Void():
    """Solid texture used for filling empty space on the screen,
    and can also be used by editors as a regular, full tile."""
    def __init__(self, size, weight=0):
        self.group = "Void"
        self.weight = weight
        self.transparent = True
        self.light = 0
        self.sprite = pg.transform.scale(SPRITES["Void"], (size, size))
        self.luminous = False

class Grass(Block):
    """Default values: solid=False, transparent=True.
    Changeable attributes: None.
    """
    def __init__(self, size):
        self.weight = 1
        self.transparent = True
        self.group = "Grass"
        self.spritedict = grassdict
        self.sprite = pg.transform.scale(grassdict["00000000"], (size, size))
        self.light = 255
        self.luminous = True

    def do_additional_generation(self, position, layout, size):
        if random.randint(1, 4) == 1:
            offset1 = random.randint(-5, 5)
            offset2 = random.randint(-5, 5)
            location = (self.sprite.get_width() + offset1, self.sprite.get_height() + offset2)
            blittable = random.choice(list(grass_extras_dict.values()))
            self.sprite.blit(blittable, location)

class Wall(Block):
    """Default values: solid=True, transparent=False.
    Changeable attributes: None.
    """
    def __init__(self, size,  weight=0, transparent=False):
        self.weight = weight
        self.transparent = transparent
        self.group = "Wall"
        self.spritedict = walldict
        self.light = 0
        self.luminous = False
        self.sprite = pg.transform.scale(walldict["00000000"], (size, size))

class DarkGrass(Block):
    """Identical as normal grass, but emits no light."""
    def __init__(self, size):
        self.weight = 1
        self.transparent = True
        self.light = 0
        self.luminous = False
        self.spritedict = grassdict
        self.sprite = pg.transform.scale(grassdict["00000000"], (size, size))
        self.group = "Grass"
    def do_additional_generation(self, position, layout, size):
        if random.randint(1, 4) == 1:
            # todo make this variable with ppb
            offset1 = random.randint(-20, 20)
            offset2 = random.randint(-20, 20)
            blittable = random.choice(list(grass_extras_dict.values()))
            location = ((self.sprite.get_width() - blittable.get_width()) / 2 + offset1, (self.sprite.get_height() - blittable.get_height()) / 2 + offset2)
            self.sprite.blit(blittable, location)
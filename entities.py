"""Import used by index.py to store all entity objects."""
import random
import pygame as pg
import math
import utils
pg.init()

# General Behaviour of entities:
# Update methods should always return a list of entities that should continue to be processed for the next frame
# Pathfinding methods will simply set the next_move attribute according to data given - movement methods still have to be called as needed.
# Directions are represented using Numpad Notation to avoid string processing: North East South West = 8 6 2 4

class Sprites():
    """Simple class for storing and resizing sprites."""
    def __init__(self):
        self.sprites = {
            "blank": pg.image.load("sprites/blank.png"),
            "teleporter": pg.image.load("sprites/Teleporter.png"),
            "caveman": pg.image.load("sprites/Caveman.png"),
        }
        # 8 different sprites, named 0.png - 7.png
        self.fireballsprites = utils.make_dict("./sprites/fireball/")
        self.fireballsprites["d4"] = pg.transform.rotate(self.fireballsprites["d6"], 180)
        self.fireballsprites["d8"] = pg.transform.rotate(self.fireballsprites["d6"], 90)
        self.fireballsprites["d2"] = pg.transform.rotate(self.fireballsprites["d6"], 270)
        self.redtint = pg.Surface((1, 1)).convert_alpha()
        self.redtint.fill((255, 0, 0, 200))
    def resize(self, ppb):
        for key in self.sprites.keys():
            self.sprites[key] = pg.transform.scale(self.sprites[key], (ppb, ppb))
        for key in self.fireballsprites.keys():
            self.fireballsprites[key] = pg.transform.scale(self.fireballsprites[key], (ppb, ppb))
        self.redtint = pg.transform.scale(self.redtint, (ppb, ppb))


sprites = Sprites()

class Entity():
    """Base class for most entities, and should
    only be used for the purposes of inheritance.
    """
    def __init__(self, position):
        self.x = position[0]
        self.y = position[1]
        self.luminescent = False
        self.interactable = False
        self.walkable = False
        self.friendly = False
        self.projectile = False
        self.enemy = False
        self.pickup = False
        self.direction = 6
        self.sprite = None
        self.next_move = (self.x, self.y)
    
    def frame_update(self):
        return [self]

    def update(self, layout, player, assets, entlist):
        return [self]
    
    def process_projectile_collisions(self, layout, entlist):
        for entity in entlist:
            if (entity.x, entity.y) == (self.x, self.y) and entity.friendly and entity.projectile:
                self.health -= entity.damage
                entity.destroyed = True


    def call_pathfind(self, layout, target, entities):
        ...
    
    def move(self):
        """Moves an entity to their next tile, or turns them towards it.
        Does NOT check for collision - this should be done in e.update(),
        after which this method should be called.
        If the next movement is more than one tile away, the entity is teleported
        without any regard for the direction in which it's facing.
        """
        if self.next_move == (self.x, self.y):
            return
        dx = self.next_move[0] - self.x
        dy = self.next_move[1] - self.y
        if dx != 0 and dy != 0:
            self.x = self.next_move[0]
            self.y = self.next_move[1]
        if dx == 1:
            if self.direction == 6:
                self.x += 1
                return
            self.direction = 6
            return
        if dy == 1:
            if self.direction == 2:
                self.y += 1
                return
            self.direction = 2
            return
        if dx == -1:
            if self.direction == 4:
                self.x -= 1
                return
            self.direction = 4
            return
        if dy == -1:
            if self.direction == 8:
                self.y -= 1
                return
            self.direction = 8
            return
        raise ValueError

    def ent_contact(self, ent):
        """Returns true if an object is within one block away from the entity.
        Does not return true if the player is positioned diagonally one tile away.
        """
        # todo optimize if possible
        if ent.x == self.x and ent.y == self.y:
            return True
        if ent.x == self.x and (ent.y == self.y + 1 or ent.y == self.y - 1):
            return True
        if ent.y == self.y and (ent.x == self.x + 1 or ent.x == self.x - 1):
            return True
        return False

    def has_los(self, layout, target):
        dx = self.x - target.x
        dy = self.y - target.y
        if dx == 0:
            for i in range(abs(dy)):
                if not layout[target.y + i][target.x].transparent:
                    return False
            return True
        accuracy = 400
        dy = self.y - target.y
        m = dy/dx
        c = self.y - m * self.x
        for i in range(0, abs(dx * accuracy)):
            if dx > 0:
                currentx = target.x + i/accuracy
            else:
                currentx = target.x - i/accuracy
            currenty = currentx * m + c
            if not layout[round(currenty)][round(currentx)].transparent:
                return False
        return True

    def simple_pathfind(self, layout, target, entities):
        """Sets next_move to one tile closer to a given target if there is no obstruction."""
        distancex = self.x - target[0] # positive = left
        distancey = self.y - target[1] # positive = up
        if distancex == 0 and distancey == 0:
            return

        # Safe to say that there are probably better ways of doing this (todo)    

        if abs(distancex) >= abs(distancey):
            if distancex > 0 and layout[self.y][self.x - 1].weight > 0:
                self.next_move = (self.x - 1, self.y)
                return
            elif distancex < 0 and layout[self.y][self.x + 1].weight > 0:
                self.next_move = (self.x + 1, self.y)
                return
            else:
                if distancey > 0 and layout[self.y - 1][self.x].weight > 0:
                    self.next_move = (self.x, self.y - 1)
                    return
                elif distancey < 0 and layout[self.y + 1][self.x].weight > 0:
                    self.next_move = (self.x, self.y + 1)
                    return
        else:
            if distancey > 0 and layout[self.y - 1][self.x].weight > 0:
                self.next_move = (self.x, self.y - 1)
                return
            elif distancey < 0 and layout[self.y + 1][self.x].weight > 0:
                self.next_move = (self.x, self.y + 1) 
                return
            else:
                if distancex > 0 and layout[self.y][self.x - 1].weight > 0:
                    self.next_move = (self.x - 1, self.y)
                    return
                elif distancex < 0 and layout[self.y][self.x + 1].weight > 0:
                    self.next_move = (self.x + 1, self.y)
                    return
    
    def get_direction_facing(self, playerpos: "x, y tuple"):
        if self.x > playerpos[0]:
            return 6
        if self.x < playerpos[0]:
            return 4
        if self.y > playerpos[1]:
            return 2
        if self.y < playerpos[1]:
            return 8
        raise ValueError
    
    def directional_pathfind(self, layout):
        """Sets next_move depending on what direction the entity is facing."""
        if self.direction == 6:
            self.next_move = (self.x + 1, self.y)
            return
        elif self.direction == 4:
            self.next_move = (self.x - 1, self.y)
            return
        elif self.direction == 8:
            self.next_move = (self.x, self.y - 1)
            return
        else:
            self.next_move = (self.x, self.y + 1)
            return

    def get_sprite(self):
        return sprites.sprites[self.sprite]

# True entities
# Enemies

class Caveman(Entity):
    """Simplest AI and lowest stats.
    Moves one tile closer to the player every other turn provided that
    there is a clear line of sight.
    Should remember where the player was when it loses line of sight.
    Otherwise, wanders aimlessly around its last active location."""
    def __init__(self, position, health=50, damage=20):
        super().__init__(position)
        self.luminescent = True
        self.light = 50
        self.health = health
        self.damage = damage
        self.sprite = sprites.sprites["caveman"].copy()
        self.damagedsprite = self.sprite.copy()
        self.damagedsprite.blit(sprites.redtint, (0,0), special_flags = pg.BLEND_RGBA_MULT)
        self.enemy = True
        self.actiontick = 0
        self.damagetick = 0
    def call_pathfind(self, layout, target, entities):
        self.simple_pathfind(layout, target, entities)

    def frame_update(self):
        if self.damagetick > 0:
            self.damagetick -= 1
        return [self]
    def update(self, layout, player, assets, entlist):

        if self.actiontick == 1:
            self.actiontick = 0
            if self.ent_contact(player):
                player.damage(self.damage)
            elif self.has_los(layout, player):
                self.move()
        else:
            self.actiontick = 1

        if player.attacked and player.facing_tile == [self.x, self.y]:
            self.health -= player.dmg
            self.damagetick = 10
        self.process_projectile_collisions(layout, entlist)
        if self.health <= 0:
            return []

        return [self]
    
    def get_sprite(self):
        if self.damagetick == 0:
            return self.sprite
        else:
            return self.damagedsprite

# Projectiles

class Fireball(Entity):
    def __init__(self, position, playerpos, friendly=True):
        super().__init__(position)
        self.damage = 50
        self.luminescent = True
        self.light = 255
        self.friendly = friendly
        self.projectile = True
        self.walkable = True
        self.direction = self.get_direction_facing(playerpos)
        self.destroyed = False
        self.frame = 0
        self.just_spawned = True

    def frame_update(self):
        if self.destroyed:
            self.frame += 1
            self.light -= 10
            if self.frame > 28:
                return []
        return [self]
            
                

    def update(self, layout, player, assets, entlist):
        if self.just_spawned:
            self.just_spawned = False
            self.next_move = (self.x, self.y)
        if self.destroyed == True:
            return [self]
        try:
            if self.next_move[0] < 0 or self.next_move[1] < 0:
                raise IndexError
            if layout[self.next_move[1]][self.next_move[0]].weight == 0:
                self.destroyed = True
                self.light = 300
                return [self]
        except IndexError:
            self.destroyed == True
            self.light = 255
        self.move()
        return [self]
    
    def call_pathfind(self, layout, target, entities):
        self.directional_pathfind(layout)
    
    def get_sprite(self):
        if self.destroyed:
            return sprites.fireballsprites[str(self.frame // 4)]
        return sprites.fireballsprites["d" + str(self.direction)]

# Gameplay entities

class Teleporter(Entity):
    """This is an entity that when interacted with by the player, will cause them
     to transport to another level, while keeping their character intact.

    Pass a tuple for position, as well as a destination variable with the name of
    the next level. By default, the teleporter places the game in a "win" state.
    """
    def __init__(self, position, destination="LEVELCLEAR"):
        super().__init__(position)
        self.interactable = True
        self.luminescent = True
        self.light = 50
        self.brighter = True
        self.destination = destination
        self.interacted = False
        self.sprite = "teleporter"
    
    def frame_update(self):
        if random.randint(1, 20) == 1:
            self.brighter = not self.brighter
        if self.brighter:
            self.light += 1
            if self.light < 20:
                self.light = 20
                self.brighter = True
        else:
            self.light -= 1
            if self.light > 60:
                self.light = 60
                self.brighter = False
        return [self]


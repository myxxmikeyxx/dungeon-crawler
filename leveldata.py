import pygame as pg
import blocks
import entities
import copy
from player import Player
from userinterface import UserInterface

class LevelData():
    def __init__(self, selection, assets):
        # todo add check_validity() to see if the data is useable
        size = assets.ppb
        compressiondict = {
            "g": blocks.Grass(size), # grass
            "v": blocks.Void(size), # void
            "a": blocks.Void(size, weight=1), # air
            "w": blocks.Wall(size), # wall
            "h": blocks.Wall(size, weight=1, transparent = True), # hidden
            "i": blocks.DarkGrass(size) # indoor
        }
        self.name = selection
        with open("levels/" + self.name, "r") as f:
            filedata = f.read().split("\n")
            level_data = filedata[0].split("|")
            try:
                item_data = filedata[1].split(" ")
            except:
                item_data = []
        self.name = selection
        self.entities = []
        self.width = int(level_data[0])
        self.height = int(level_data[1])
        self.player = eval(level_data[2])
        self.player.resize_sprites(size)
        tilelist = self.convert_data(list(level_data[3]))
        entitylist = level_data[4].split("/")
        if entitylist[0] != "":
            for entitystring in entitylist:
                self.entities.append(eval("entities." + entitystring))
        self.rows = []
        iteration = 0
        for i in range(self.height):
            self.rows.append([])
            for j in range(self.width):
                self.rows[i].append(copy.copy(compressiondict[tilelist[iteration]]))
                iteration += 1
        self.spritepass(assets.ppb)
        self.player.inventory.generate_sprite(assets)
        self.player.add_inventory_items(item_data)
        ui = UserInterface(self.player, assets)
        self.player.ui = ui
        assets.screen = pg.display.set_mode((assets.resolutionx, assets.resolutiony + self.player.ui.height))

        self.transparency_map = []
        for i in range(len(self.rows)):
            self.transparency_map.append([])
            for j in range(len(self.rows[0])):
                if self.rows[i][j].transparent == True:
                    self.transparency_map[i].append(True)
                else:
                    self.transparency_map[i].append(False)

    def spritepass(self, ppb):
        """Iterates through every tile and calls their choose_sprite()
        method, if they have one.
        """
        for i in range(0, len(self.rows)):
            for j in range(0, len(self.rows[0])):
                try:
                    self.rows[i][j].choose_sprite((j, i), self.rows, ppb)
                except:
                    pass

    def generate_base_lighting(self):
        baselighting = []
        lights_to_preprocess = []
        for i in range(self.height):
            baselighting.append([])
            for j in range(self.width):
                if self.rows[i][j].luminous:
                    lights_to_preprocess.append([self.rows[i][j].light, j, i])
                baselighting[i].append(self.rows[i][j].light)
        return baselighting, lights_to_preprocess

    def convert_data(self, data):
        instructions = ""
        current = ""
        for character in data:
            try:
                int(character)
                current += character
            except ValueError:
                instructions += int(current) * character
                current = ""
        return instructions
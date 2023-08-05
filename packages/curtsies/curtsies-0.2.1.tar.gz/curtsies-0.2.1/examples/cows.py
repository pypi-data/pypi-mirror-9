import sys
import random

from collections import namedtuple

from curtsies import input, Cbreak, FullscreenWindow, fmtstr, FSArray
from curtsies.fmtfuncs import *


Point = namedtuple('Point', ['x', 'y'])

class Player(object):
    def __init__(self, x, y, take, put, move):
        self.age = 0
        self.x = x
        self.y = y
        self.taker = take
        self.putter = put
        self.mover = move
        self.holding = None
    def take(self):
        self.holding = self.taker(self)
    def put(self):
        if self.holding:
            self.putter(self, self.holding)
            self.holding = None
    def process(self, key):
        movements = {
         '<LEFT>' : Point(-1,  0),
         '<RIGHT>': Point( 1,  0),
         '<UP>'   : Point( 0,  1),
         '<DOWN>' : Point( 0, -1),
         'h'      : Point(-1,  0),
         'l'      : Point( 1,  0),
         'k'      : Point( 0,  1),
         'j'      : Point( 0, -1),
         }
        if key in movements:
            m = movements[key]
            self.mover(self, self.x + m.x, self.y + m.y)
        elif key in ('f',):
            self.take()
        elif key in ('d',):
            self.put()
    z_index = 3
    sigil = bold(red('O'))

class Cow(object):
    def __init__(self, x, y, take, put, move):
        self.x = x
        self.y = y
        self.taker = take
        self.putter = put
        self.mover = move
    def process(self, key):
        self.taker(self)
        m = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0)])
        self.mover(self, self.x + m[0], self.y + m[1])
    def passable(self, who): return True
    def takeable(self, who): return not isinstance(who, Cow)
    sigil = bold(gray('C'))
    z_index = 2

class Terrain(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def passable(self, who): return True
    def takeable(self, who): return False
    z_index = 0

class Movable(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def passable(self, who): return True
    def takeable(self, who): return True
    z_index = 1

class Obstacle(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def passable(self, who): return False
    def takeable(self, who): return False
    z_index = 1

class Bush(Movable):
    sigil = bold(green('x'))
class Grass(Terrain):
    sigil = on_green(' ')
class Stone(Obstacle):
    sigil = on_gray(bold(gray('@')))

class World(object):
    def __init__(self, width, height):
        self.array = [[random.choice(['x', ' ', ' ', ' ']) for _ in range(width)] for _ in range(height)]
        self.player = Player(10, 10, self.taker, self.putter, self.mover)
        self.width = width
        self.height = height
        self.npcs = []
        self.randomly_disperse(Bush, .1)
        self.clump(Grass, .2)
        self.randomly_disperse_except_on_player(Stone, .05)
        self.randomly_disperse(lambda x, y: Cow(x, y, self.taker, self.putter, self.mover), .03)

    def randomly_disperse(self, thing, ratio):
        self.npcs.extend([thing(random.randint(0, self.width - 1), random.randint(0, self.height - 1))
                          for _ in range(int(self.width*self.height*ratio))])

    def clump(self, thing, ratio):
        def touching(x, y):
            return len([thing for x, y in [(x+dx, y+dy)
                                       for dx in [0, 1, -1]
                                       for dy in [0, 1, -1]]
                        if (x, y) in placed])
        placed = set()
        while len(placed) < ratio * self.width * self.height:
            print '.'
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            if not (x, y) in placed and random.random() < (touching(x, y)+1)**2*.1:
                placed.add((x, y))
                self.npcs.append(thing(x, y))
                print len(placed), '/', ratio * self.width * self.height

    def randomly_disperse_except_on_player(self, thing, ratio):
        self.npcs.extend([thing(x, y)
                          for x, y in [(random.randint(0, self.width - 1), random.randint(0, self.height - 1))
                                       for _ in range(int(self.width*self.height*ratio))]
                          if self.player.x != x and self.player.y != y])

    def taker(self, entity):
        here = sorted([e for e in self.npcs
                       if e.x == entity.x and e.y == entity.y and
                       e.takeable(entity)],
                      key=lambda x: x.z_index)
        if here:
            e = here.pop()
            self.npcs.remove(e)
            return e

    def putter(self, putter, thing):
        thing.x, thing.y = putter.x, putter.y
        self.npcs.append(thing)

    def mover(self, entity, x, y):
        there = [e for e in self.npcs if e.x == x and e.y == y]
        if all(t.passable(entity) for t in there):
            entity.x = x
            entity.y = y

    def move(self, key):
        for entity in self.npcs + [self.player]:
            if hasattr(entity, 'process'):
                entity.process(key)

        for entity in [self.player] + self.npcs:
            entity.x = max(0, min(self.width - 1, entity.x))
            entity.y = max(0, min(self.height - 1, entity.y))

    def render(self):
        a = FSArray(self.height, self.width)
        entities = sorted(self.npcs + [self.player], key=lambda x: x.z_index)

        for entity in sorted(self.npcs + [self.player], key=lambda x: x.z_index):
            (old,) = a[a.height - entity.y - 1, entity.x]
            d = old.shared_atts
            d.update(entity.sigil.shared_atts)
            new = fmtstr(entity.sigil.s, **d)
            a[a.height - entity.y - 1, entity.x] = new
        return a

def fullscreen_with_input():
    w = FullscreenWindow(sys.stdout)
    world = World(w.width, w.height)
    #world = World(30, 30)
    with w:
        with Cbreak(sys.stdin):
            a = FSArray(w.height, w.width)
            world_view = world.render()
            a[0:world_view.height, 0:world_view.width] = world_view
            w.render_to_terminal(a)
            for e in input.Input():
                world.move(e)
                a = FSArray(w.height, w.width)
                world_view = world.render()
                a[0:world_view.height, 0:world_view.width] = world_view
                w.render_to_terminal(a)

def test():
    w = FullscreenWindow(sys.stdout)
    world = World(w.width, w.height)
    with w:
        for e in ['j', 'j']:
            world.move(e)
            a = FSArray(w.height, w.width)
            world_view = world.render()
            a[0:world_view.height, 0:world_view.width] = world_view
            w.render_to_terminal(a)

if __name__ == '__main__':
    #fullscreen_with_input()
    test()


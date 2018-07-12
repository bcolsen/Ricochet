import itertools
import random

from boards import *

# Directions
NORTH = 'N'
EAST = 'E'
SOUTH = 'S'
WEST = 'W'

DIRECTIONS = [NORTH, EAST, SOUTH, WEST]

REVERSE = {
    NORTH: SOUTH,
    EAST: WEST,
    SOUTH: NORTH,
    WEST: EAST,
}

L_TURN = {
    NORTH: WEST,
    EAST: SOUTH,
    SOUTH: EAST,
    WEST: NORTH,
}

R_TURN = {
    NORTH: EAST,
    EAST: NORTH,
    SOUTH: WEST,
    WEST: SOUTH,
}

OFFSET = {
    NORTH: -16,
    EAST: 1,
    SOUTH: 16,
    WEST: -1,
}

MOD = {
    NORTH: 256,
    EAST: 16,
    SOUTH: 256,
    WEST: 16,
}


# Masks
M_NORTH = 0x01
M_EAST  = 0x02
M_SOUTH = 0x04
M_WEST  = 0x08
M_ROBOT = 0x10

M_LOOKUP = {
    NORTH: M_NORTH,
    EAST: M_EAST,
    SOUTH: M_SOUTH,
    WEST: M_WEST,
}

# Bumpers
LEFT = 'D'
RIGHT = 'F'

# Colors
RED = 'R'
GREEN = 'G'
BLUE = 'B'
YELLOW = 'Y'
SILVER = 'L'

COLORS = [RED, GREEN, BLUE, YELLOW, SILVER]

# Shapes
CIRCLE = 'C'
TRIANGLE = 'T'
SQUARE = 'Q'
HEXAGON = 'H'

RAINBOW = 'J'

SHAPES = [CIRCLE, TRIANGLE, SQUARE, HEXAGON]

# Tokens
TOKENS = [''.join(token) for token in itertools.product(COLORS[0:4], SHAPES)]

QUADS = [
    (Q_R1, Q_R2, Q_R3, Q_R4),
    (Q_G1, Q_G2, Q_G3, Q_G4),
    (Q_B1, Q_B2, Q_B3, Q_B4),
    (Q_Y1, Q_Y2, Q_Y3, Q_Y4),
]

P_QUADS = [
    (P_R1, P_R2, P_R3, P_R4),
    (P_G1, P_G2, P_G3, P_G4),
    (P_B1, P_B2, P_B3, P_B4),
    (P_Y1, P_Y2, P_Y3, P_Y4),
]
# Rotation
ROTATE_QUAD = [
    56, 48, 40, 32, 24, 16,  8,  0, 
    57, 49, 41, 33, 25, 17,  9,  1, 
    58, 50, 42, 34, 26, 18, 10,  2, 
    59, 51, 43, 35, 27, 19, 11,  3, 
    60, 52, 44, 36, 28, 20, 12,  4, 
    61, 53, 45, 37, 29, 21, 13,  5, 
    62, 54, 46, 38, 30, 22, 14,  6, 
    63, 55, 47, 39, 31, 23, 15,  7,
]

ROTATE_WALL = {
    NORTH: EAST,
    EAST: SOUTH,
    SOUTH: WEST,
    WEST: NORTH,
    LEFT: RIGHT,
    RIGHT: LEFT,
}

# Helper Functions
def idx(x, y, size=16):
    return y * size + x

def xy(index, size=16):
    x = index % size
    y = index // size
    return (x, y)

def rotate_quad(data, times=1):
    for i in range(times):
        result = [data[index] for index in ROTATE_QUAD]
        result = [''.join(ROTATE_WALL.get(c, c) for c in x) for x in result]
        data = result
    return data

def create_grid(quads=None):
    if quads is None:
        quads = [random.choice(pair) for pair in QUADS]
        random.shuffle(quads)
    quads = [quad.split(',') for quad in quads]
    quads = [rotate_quad(quads[i], i) for i in [0, 1, 3, 2]]
    result = [None for i in range(16 * 16)]
    for i, quad in enumerate(quads):
        dx, dy = xy(i, 2)
        for j, data in enumerate(quad):
            x, y = xy(j, 8)
            x += dx * 8
            y += dy * 8
            index = idx(x, y)
            result[index] = data
    for i, data in enumerate(result):
        if 'J' in data:
            for direction in 'NSEW':
                if direction in data:
                    index = i + OFFSET[direction]
                    print(result[index])
                    if not REVERSE[direction] in result[index]:
                        result[index] += REVERSE[direction]
    return result

def to_mask(cell):
    result = 0
    for letter, mask in M_LOOKUP.items():
        if letter in cell:
            result |= mask
    return result

def get_row_column(index, direction):
    if direction in 'NS':
        return index % 16
    elif direction in 'EW':
        return index // 16

#Set
class Match(object):
    def __init__(self, seed=None, quads=None, robots=None, token=None, num_robots=4):
        if seed:
            random.seed(seed)
        self.seed = seed
        self.quads = quads
        self.tokens = list(TOKENS)
        random.shuffle(self.tokens)
        self.num_robots = num_robots
        
        token = self.tokens.pop()
        self.game = Game(self.seed, self.quads, robots, token, self.num_robots)
        
    def next_game(self, robots=None):
        try:
            token = self.tokens.pop()
        except IndexError:
            print("The Match is over..Computer Wins")
        if robots is None:
            if self.num_robots == 5:
                robots = [self.game.robots[x] for x in 'RGBYL']
            else:
                robots = [self.game.robots[x] for x in 'RGBY']
        print('game solve', robots)
        self.game = Game(self.seed, self.quads, robots, token, self.num_robots)
        return self.game
    
# Game
class Game(object):
    @staticmethod
    def hardest():
        quads = [QUAD_2B, QUAD_4B, QUAD_3B, QUAD_1B]
        robots = [226, 48, 43, 18]
        token = 'BT'
        return Game(quads=quads, robots=robots, token=token)
    def __init__(self, seed=None, quads=None, robots=None, token=None, num_robots=4):
        if seed:
            random.seed(seed)
        self.grid = create_grid(quads)
        self.colors = COLORS[:num_robots]
        if robots is None:
            self.robots = self.place_robots()
        else:
            self.robots = dict(zip(self.colors, robots))
        self.token = token or random.choice(TOKENS)
        self.moves = 0
        self.last = None
        self.new_robot = False
        self.start_robots = dict(self.robots)
    def place_robots(self):
        result = {}
        used = set()
        for color in self.colors:
            while True:
                index = random.randint(0, 255)
                if index in (119, 120, 135, 136):
                    continue
                if self.grid[index][-2:] in TOKENS:
                    continue
                if index in used:
                    continue
                result[color] = index
                used.add(index)
                break
        return result
    def get_robot(self, index):
        for color, position in self.robots.items():
            if position == index:
                return color
        return None
    def can_move(self, color, direction, index):
        #print color, direction, index, self.new_robot, self.last_new
        if self.last_new == (color, REVERSE[direction], index):
            #print 'not new direction rev', color, direction
            return False
        if self.last_new == (color, direction, index):
            #print 'not new direction same', color, direction
            return False
        index = self.robots[color]
        if direction in self.grid[index]:
            return False
        new_index = index + OFFSET[direction]
        if new_index in self.robots.values():
            return False
        return True
    def compute_move(self, color, direction):
        index = self.robots[color]
        robots = self.robots.values()
        #print color, direction
        #print index, index % MOD[direction]
        #row = index - index % MOD[direction]
        #print row
        i = 0
        self.new_robot = False
        while True:
            #print index, direction, index % MOD[direction]
            # Bumpers
            if color not in self.grid[index]: #Same colors go through
                if LEFT in self.grid[index]:
                    direction = L_TURN[direction]
                if RIGHT in self.grid[index]:
                    direction = R_TURN[direction]
            if direction in self.grid[index]: # Hit a wall and stop
                break
            row = index - index % MOD[direction]
            new_index = (index + OFFSET[direction]) % MOD[direction] + row
            if new_index == self.robots[color]: #Infinite loop
                index = new_index
                break
            elif new_index in robots: # Hit a wall and stop before
                rcolor = list(self.robots.keys())[list(self.robots.values()).index(new_index)]
                # if new robot
                if color == self.token[0] and not (new_index == self.start_robots[rcolor]):
                    self.new_robot = True
                    #print "new robot", new_index, rcolor, self.start_robots
                break
            index = new_index
        return index
    def do_move(self, color, direction, index):
        #print self.robots
        start = self.robots[color]
        last = self.last
#        if last == (color, REVERSE[direction]):
#            raise Exception
        end = self.compute_move(color, direction)
#        if start == end:
#            raise Exception
        self.moves += 1
        self.robots[color] = end
        self.last = (color, direction, index) #should be end
        return (color, start, last)
    def undo_move(self, data):
        color, start, last = data
        self.moves -= 1
        self.robots[color] = start
        self.last = last
    def get_moves(self, colors=None):
        result = []
        colors = colors or self.colors
        for color in colors:
            for direction in DIRECTIONS:
                if self.can_move(color, direction, self.robots[color]):
                    result.append((color, direction, self.robots[color]))
        return result
    def over(self):
        color = self.token[0]
        return self.token in self.grid[self.robots[color]]
    def key(self):
        return tuple(self.robots.values())
    def unique(self,path):
        #print 'unique', path
        for sol in self.result_list + self.mono_list:
            iter_sol = iter(sol)
            m_c, m_d, m_i = next(iter_sol)
            m_rc = get_row_column(m_i,m_d)
            for c, d, i in path:
                rc = get_row_column(i,d)
                #print (c, d, i), rc, (m_c, m_d, m_i),m_rc
                if (c, d) == (m_c, m_d) and rc == m_rc:
                    try:
                        m_c, m_d, m_i = next(iter_sol)
                        m_rc = get_row_column(m_i,m_d)
                    except StopIteration:
                        #print 'false'
                        return False
        #print 'true'
        return True
#    def mono(self, path):
#        other_colors = list(COLORS)
#        other_colors.remove(self.token[0])
#        #print other_colors
#        if len(set([move[0] for move in path])) <= 1:#all the same color
#            return True
#        else:
#            return False
    def search(self):
        #print self.start_robots 
        self.new_robot = False
        max_depth = 1
        self.result_list = []
        self.mono_list = []
        while True:
            print('Searching to depth:', max_depth)
            self.new_robot = False
            result = self._search([], [], set(), 0, max_depth)
            if len(self.result_list) >= 5 or max_depth > 9:
                return self.result_list
            max_depth += 1
    def _search(self, path, new_robot, memo, depth, max_depth):
        if self.over():# and self.new_robot:
#            if any([i[0] for i in new_robot]):
#                print path, new_robot
            if self.unique(path):
                #print path, new_robot
                if any([i[0] for i in new_robot]):
                    print('**', len(path), ', '.join(''.join(move[0:-1]) for move in path))
                    self.result_list += [list(path)]
                else:
                    print('mono', len(path), ', '.join(''.join(move[0:-1]) for move in path))
                    self.mono_list += [list(path)]
#            else:
#                print "not unique"
        if depth == max_depth:
            return None
        if max_depth >= 8 and len(self.result_list) >= 5:
            return None
        elif max_depth >= 10 and len(self.result_list) >= 1:
            return None
        key = (depth, self.key())
        if key in memo:
            return None
        if key in memo:
            return None
        memo.add(key)
        if depth == max_depth - 1:
            colors = [self.token[0]]
        else:
            colors = None
        try:
            self.last_new = [(i[0],i[1],v[1]) for (i, v) in zip(path, new_robot) if v[0]][-1]
            #print path, new_robot, self.last_new
        except IndexError:
            self.last_new = None
        moves = self.get_moves(colors)
        for move in moves:
            data = self.do_move(*move)
            path.append(move)
            new_robot.append((self.new_robot,self.robots[move[0]]))
            result = self._search(path, new_robot, memo, depth + 1, max_depth)
            #print path
            path.pop(-1)
            new_robot.pop(-1)
            self.undo_move(data)
            if result:
                return result
        return None
    def export(self):
        grid = []
        token = None
        robots = [self.robots[color] for color in self.colors]
        for index, cell in enumerate(self.grid):
            mask = to_mask(cell)
            if index in robots:
                mask |= M_ROBOT
            grid.append(mask)
            if self.token in cell:
                token = index
        robot = self.colors.index(self.token[0])
        return {
            'grid': grid,
            'robot': robot,
            'token': token,
            'robots': robots,
        }

import random

def _rotate(tetrimino): # We're just gonna use this once
    return [[tetrimino[-1-x][y] for x in range(len(tetrimino))] for y in range(len(tetrimino))]

class TopOut(Exception):
    pass

class Board:
    NAMES = "IJLOSZT."
    COLORS = [
        (0, 255, 255),
        (0, 0, 255),
        (255, 0xA5, 0),
        (255, 255, 0),
        (0, 255, 0),
        (255, 0, 0),
        (255, 0, 255),
        (127, 127, 127)
    ]
    _SHAPES = [
        [
            [0,0,0,0],
            [1,1,1,1],
            [0,0,0,0],
            [0,0,0,0]
        ],
        [
            [1,0,0],
            [1,1,1],
            [0,0,0]
        ],
        [
            [0,0,1],
            [1,1,1],
            [0,0,0]
        ],
        [
            [1,1],
            [1,1]
        ],
        [
            [0,1,1],
            [1,1,0],
            [0,0,0]
        ],
        [
            [1,1,0],
            [0,1,1],
            [0,0,0]
        ],
        [
            [0,1,0],
            [1,1,1],
            [0,0,0]
        ],
        []
    ]

    SHAPES = [[r[::-1] for r in [s, _rotate(s), _rotate(_rotate(s)), _rotate(_rotate(_rotate(s)))]] for s in _SHAPES]

    ROTATION = [
        [  # Clockwise
            [( 0, 0), (-1, 0), (-1,+1), ( 0,-2), (-1,-2)],  # 0 -> 1
            [( 0, 0), (+1, 0), (+1,-1), ( 0,+2), (+1,+2)],  # 1 -> 2, etc.
            [( 0, 0), (+1, 0), (+1,+1), ( 0,-2), (+1,-2)],
            [( 0, 0), (-1, 0), (-1,-1), ( 0,+2), (-1,+2)]
        ],
        [  # Counterclockwise
            [( 0, 0), (+1, 0), (+1,+1), ( 0,-2), (+1,-2)],  # 0 -> 4
            [( 0, 0), (+1, 0), (+1,-1), ( 0,+2), (+1,+2)],  # 1 -> 0, etc.
            [( 0, 0), (-1, 0), (-1,+1), ( 0,-2), (-1,-2)],
            [( 0, 0), (-1, 0), (-1,-1), ( 0,+2), (-1,+2)],
        ]
    ]

    ROTATION_I = [
        [
            [( 0, 0), (-2, 0), (+1, 0), (-2,-1), (+1,+2)],
            [( 0, 0), (-1, 0), (+2, 0), (-1,+2), (+2,-1)],
            [( 0, 0), (+2, 0), (-1, 0), (+2,+1), (-1,-2)],
            [( 0, 0), (+1, 0), (-2, 0), (+1,-2), (-2,+1)]
        ],
        [
            [( 0, 0), (-1, 0), (+2, 0), (-1,+2), (+2,-1)],
            [( 0, 0), (+2, 0), (-1, 0), (+2,+1), (-1,-2)],
            [( 0, 0), (+1, 0), (-2, 0), (+1,-2), (-2,+1)],
            [( 0, 0), (-2, 0), (+1, 0), (-2,-1), (+1,+2)]
        ]
    ]

    def __init__(self):
        # States:
        # 0 : no block
        #  -1  : black
        #  0~6 : ghost block
        # 1 : block
        #  -1  : grey
        #  0~6 : block
        # 2 : active
        #  0~6 : block
        # Coords: left to right rows, packed bottom to top.
        self.board = [[[0, -1] for _ in range(10)] for _ in range(40)]
        self.current = -1
        self.currentrot = 0
        self.currentpos = [0, 0]
        self.totallno = 0

    def reset(self):
        self.board = [[[0, -1] for _ in range(10)] for _ in range(40)]
        self.current = -1
        self.currentrot = 0
        self.currentpos = [0, 0]
        self.totallno = 0

    def __getitem__(self, idx):
        return self.board[idx[1]][idx[0]]

    def __str__(self):
        return "\n".join("".join(".." if (ent, col) == (0, -1) else ";;" if ent == 0 else "[]" if ent == 1 else "##" for ent, col in row) for row in self.ext_board())

    def ext_board(self):  # should be used only if not collide
        # if self.collides():
        #     raise RuntimeWarning("WARNING: Collision detected.")
        if self.current == -1:
            return self.board[19::-1]
        else:
            x0, y0 = self.currentpos
            l = [[j for j in i] for i in self.board[:]]
            for y, row in enumerate(self.SHAPES[self.current][self.currentrot]):
                for x, cell in enumerate(row):
                    if cell == 1:
                        l[y0 + y][x0 + x] = (2, self.current)
            return l[19::-1]

    def supply_tetrimino(self, tetr_id):
        self.current = tetr_id
        if self.current == 0: # I is different
            self.currentpos = [3, 18]
        elif self.current == 3: # O is different
            self.currentpos = [4, 20]
        else:
            self.currentpos = [3, 19]
        self.currentrot = 0
        if self.collides():
            print("Block Out")
            raise TopOut("Blocked out!")

    def collides(self):
        if self.current == -1:
            return False
        x0, y0 = self.currentpos
        for y, row in enumerate(self.SHAPES[self.current][self.currentrot]):
            for x, cell in enumerate(row):
                if cell == 1:
                    if 0 <= y0+y < 40 and 0 <= x0+x < 10:  #? We can compact this
                        if self.board[y0 + y][x0 + x][0] != 0:
                            return True
                    else:
                        return True
        return False

    def update_shadow(self):
        if self.collides():
            return
        # clear
        for i in range(10):
            for j in range(40):
                if self.board[j][i][0] == 0:
                    self.board[j][i][1] = -1
        # update
        if self.current == -1:
            return
        xc, yc = self.currentpos
        while not self.collides():
            self.currentpos[1] -= 1
        x0, y0 = self.currentpos
        for y, row in enumerate(self.SHAPES[self.current][self.currentrot]):
            for x, cell in enumerate(row):
                if cell == 1:
                    self.board[y0 + y + 1][x0 + x] = [0, self.current]
        self.currentpos = [xc, yc]

    def move(self, x, y):
        self.currentpos[0] += x
        self.currentpos[1] += y
        if self.collides():
            self.currentpos[0] -= x
            self.currentpos[1] -= y
            return False
        return True

    def rotate(self, clockwise=True):
        c = self.currentrot
        self.currentrot += 1 if clockwise else -1
        self.currentrot %= 4
        for kickx, kicky in (self.ROTATION_I if self.current == 0 else self.ROTATION)[0 if clockwise else 1][c]:
            self.currentpos[0] += kickx
            self.currentpos[1] += kicky
            if not self.collides():
                return True
            self.currentpos[0] -= kickx
            self.currentpos[1] -= kicky
        self.currentrot = c
        return False

    def lock(self):
        # should have checked collision
        if self.current == -1:
            raise RuntimeError("Nothing to lock.")
        else:
            x0, y0 = self.currentpos
            lockout = True
            for y, row in enumerate(self.SHAPES[self.current][self.currentrot]):
                for x, cell in enumerate(row):
                    if cell == 1:
                        self.board[y0 + y][x0 + x] = [1, self.current]
                        if y0 + y < 20:
                            lockout = False
            if lockout:
                print("Lock Out")
                raise TopOut("Locked out.")
            self.currentpos = (0, 0)
            self.current = -1
            self.currentrot = 0

    def clear(self):
        self.board = [r for r in self.board if not all(i == 1 for i, _ in r)]
        lno = 40 - len(self.board)
        self.board.extend([[[0, -1] for _ in range(10)] for _ in range(lno)])
        self.totallno += lno
        return lno

    def garbage(self, number):
        lno = random.randint(0, 9)
        self.board = [[[1, -1] if i != lno else [0, -1] for i in range(10)] for _ in range(number)] + self.board
        if any(any(i == 1 for i, _ in row) for row in self.board[40:]):
            print("Garbage Out")
            raise TopOut("Garbage out.")
        self.board = self.board[:40]
        if self.collides():
            print("Block Out by garbage")
            raise TopOut("Block Out!")

    def cleared(self):
        for r in self.board:
            for c, _ in r:
                if c == 1:
                    return False
        return True


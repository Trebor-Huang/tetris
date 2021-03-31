from board import *
import random

class Game:  # this class does not implement any time related stuff
    @staticmethod
    def bag7(s):
        l = [0,1,2,3,4,5,6]
        random.seed(s)
        while True:
            random.shuffle(l)
            for i in l:
                yield i
            random.seed(tuple(l))

    def __init__(self):
        self.board = Board()
        self.tetrimino_stream = None
        self.hold = -1
        self.holdable = True
        self.next = [-1, -1, -1, -1, -1]
        self.playing = False
        self.is_tspin = False
        self.ren = 0
        self.pending_garbage = 0
        self.b2b = False
        self.dead = False

    def start(self, seed):
        self.board.reset()
        self.tetrimino_stream = self.bag7(seed)
        self.hold = -1
        self.holdable = True
        self.board.supply_tetrimino(next(self.tetrimino_stream))
        self.next = [next(self.tetrimino_stream) for _ in range(5)]
        self.playing = True
        self.is_tspin = False
        self.ren = 0
        self.pending_garbage = 0
        self.b2b = False
        self.dead = False

    def hold_tetrimino(self):
        if self.dead or not self.holdable:
            return False
        self.holdable = False
        h = self.hold
        self.hold = self.board.current
        if h == -1:
            self.board.supply_tetrimino(self.next.pop(0))
            self.next.append(next(self.tetrimino_stream))
        else:
            try:
                self.board.supply_tetrimino(h)
            except Exception:
                self.dead = True
        return True

    def gravity(self):
        if self.dead:
            return False
        r = self.board.move(0, -1)
        if r:
            self.is_tspin = False
        return r

    def grounded(self):
        res = self.board.move(0, -1)
        if res: self.board.move(0, 1)
        return not res

    def hard_drop(self):  # implies lock()
        self.soft_drop()
        return self.lock()

    def soft_drop(self):
        if self.dead:
            return False
        moved = False
        while self.board.move(0, -1):
            moved = True
        self.is_tspin = self.is_tspin and not moved
        return moved

    def rotate(self, clockwise):
        if self.dead:
            return False
        r = self.board.rotate(clockwise)
        self.is_tspin = r
        return r

    def move(self, right):
        if self.dead:
            return False
        if r := self.board.move(1 if right else -1, 0):
            self.is_tspin = False
        return r

    def lock(self):
        # locks, checks for t-spin, clear lines and supply new block
        is_tspin = False
        if self.is_tspin and self.board.current == 6:
            c = 0
            for _dx, _dy in ((0,0), (2,0), (0,2), (2,2)):
                _x, _y = _dx + self.board.currentpos[0], _dy + self.board.currentpos[1]
                if _y < 0 or _x < 0 or _x >= 10:
                    c += 1
                elif(self.board[_x, _y][0] == 1):
                    c += 1
            if c >= 3:
                is_tspin = True
        self.is_tspin = False
        try:
            self.board.lock()
            self.holdable = True
            lno = self.board.clear()
            self.board.supply_tetrimino(self.next.pop(0))
        except Exception:
            self.dead = True
        if self.dead:
            return (False, 0, 0, False, False)
        self.next.append(next(self.tetrimino_stream))
        if lno == 0:
            self.ren = 0
            try:
                self.garbage(self.pending_garbage)
            except Exception:
                self.dead = True
                return (False, 0, 0, False, False)
            self.pending_garbage = 0
        else:
            self.ren += 1
        is_tspin = is_tspin and lno > 0
        this_b2b = is_tspin or (lno == 4)
        result = (is_tspin, lno, self.ren, self.board.cleared(), this_b2b and self.b2b)
        self.b2b = this_b2b
        return result

    def garbage(self, lno):
        self.board.garbage(lno)

    def display(self):
        self.board.update_shadow()
        print("\n" * 10)
        print(str(self.board))

if __name__ == "__main__":
    g = Game()
    g.start(0)
    g.display()
    while True:
        c = input("Your move: ")
        if c == "s":
            g.gravity()
        elif c == "a":
            g.move(False)
        elif c == "d":
            g.move(True)
        elif c == "z":
            g.rotate(False)
        elif c == "x":
            g.rotate(True)
        elif c == "c":
            g.hold_tetrimino()
        elif c == " ":
            g.hard_drop()
        elif c == "ss":
            g.soft_drop()
        elif c == "l":
            g.lock()
        elif c[:1] == "a":
            g.garbage(int(c.split()[1].strip()))
        g.display()
        print(g.hold, g.next, g.ren, g.is_tspin)

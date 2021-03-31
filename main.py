import tkinter as tk
import game, time

KEYS = {
    "space" : (0, "Hard Drop"),
    "v" : (0, "Left"),
    "n" : (0, "Right"),
    "b" : (0, "Gravity"),
    "g" : (0, "Rotate Right"),
    "z" : (0, "Rotate Left"),
    "x" : (0, "Rotate Right"),
    "c" : (0, "Hold"),

    #"0" : (1, "Hard Drop"),
    #"1" : (1, "Left"),
    #"2" : (1, "Right"),
    #"Down" : (1, "Gravity"),
    #"Left" : (1, "Rotate Right"),
    #"Right" : (1, "Rotate Left"),
    #"-" : (1, "Rotate Right"),
    #"Up" : (1, "Hold"),
    
    "Left" : (1, "Hard Drop"),
    "1" : (1, "Left"),
    "3" : (1, "Right"),
    "bracketright" : (1, "Gravity"),
    "bracketleft" : (1, "Rotate Left"),
    "backslash" : (1, "Rotate Right"),
    "l" : (1, "Hold"),
}

DAS_DELAY = [130, 120] # ms, [Left player, Right player]
DAS_INTERVAL = [1, 2]
GRAVITY = 0 # ms
LOCK_DELAY = 1000
AUTOLOCK_PROTECTION = 100
LINE_COUNT = 0
SIDE = 2  # 0 is left, 1 is right, 2 is two, -1 is no attack
TSD = False
CHEESE = 0
CHEESE_SIZE = 0

TILE_SIZE = 20
NEXT_TILE_SIZE = 13
HOLD_TILE_SIZE = 16
GARBAGE_GAUGE = 10
GARBAGE_COLOR = "#EA3210"
COLORS = [
    "#00FFFF",
    "#3333FF",
    "#FFA500",
    "#FFFF00",
    "#00FF00",
    "#FF0000",
    "#FF00FF",
    "#777777"
]
COLORS_GHOST = [
    "#008888",
    "#2222AA",
    "#664400",
    "#888800",
    "#009900",
    "#990000",
    "#880088",
    ""
]
SHAPES = [
    [
        [0,0,0,0],
        [1,1,1,1],
        [0,0,0,0],
        [0,0,0,0]
    ],
    [
        [0,0,0,0],
        [1,0,0,0],
        [1,1,1,0],
        [0,0,0,0]
    ],
    [
        [0,0,0,0],
        [0,0,1,0],
        [1,1,1,0],
        [0,0,0,0]
    ],
    [
        [0,0,0,0],
        [0,1,1,0],
        [0,1,1,0],
        [0,0,0,0]
    ],
    [
        [0,0,0,0],
        [0,1,1,0],
        [1,1,0,0],
        [0,0,0,0]
    ],
    [
        [0,0,0,0],
        [1,1,0,0],
        [0,1,1,0],
        [0,0,0,0]
    ],
    [
        [0,0,0,0],
        [0,1,0,0],
        [1,1,1,0],
        [0,0,0,0]
    ],
    [
        [0,0,0,0],
        [0,0,0,0],
        [0,0,0,0],
        [0,0,0,0]
    ]
]

def get_color(t):
    if t[0] == 0:
        return COLORS_GHOST[t[1]]
    else:
        return COLORS[t[1]]
    
class BoardDisplay(tk.Frame):
    def __init__(self, master=None, inverted=False, side=0):
        super().__init__(master)
        self.autolock = -1
        self.side = side
        self.das_lr = -1
        self.das_g = -1
        self.autolocking = False
        self.master = master
        self.pack()
        self.game = game.Game()
        self.side_frame = tk.Frame(self)
        self.main_frame = tk.Frame(self)
        self.canvas = tk.Canvas(self.main_frame,
                                height = TILE_SIZE * 20,
                                width = TILE_SIZE * 10,
                                bg = "#000")
        self.tiles = [[self.canvas.create_rectangle(
            x * TILE_SIZE + 2,
            y * TILE_SIZE + 2,
            (x + 1) * TILE_SIZE,
            (y + 1) * TILE_SIZE
        ) for x in range(10)] for y in range(20)]
        self.gauge = tk.Canvas(self.side_frame,
                               height = TILE_SIZE * 20,
                               width = GARBAGE_GAUGE,
                               bg = "#000")
        self.gauge_rect = self.gauge.create_rectangle(
            0, 0, 0, 0,
            fill = GARBAGE_COLOR
        )
        self.next = [
            tk.Canvas(self.side_frame,
                      height = NEXT_TILE_SIZE * 4,
                      width = NEXT_TILE_SIZE * 4,
                      bg = "#000")
            for _ in range(5)
        ]
        self.next_rect = [
            [
                [
                    n.create_rectangle(
                        x * NEXT_TILE_SIZE + 1, y * NEXT_TILE_SIZE + 1,
                        (x+1) * NEXT_TILE_SIZE + 2, (y+1) * NEXT_TILE_SIZE + 2,
                        fill = "#000",
                        outline = ""
                    )
                for y in range(4)]
            for x in range(4)]
        for n in self.next]
        self.hold = tk.Canvas(self.side_frame,
                      height = HOLD_TILE_SIZE * 4,
                      width = HOLD_TILE_SIZE * 4,
                      bg = "#000")
        self.hold_rect = [
            [
                self.hold.create_rectangle(
                    x * HOLD_TILE_SIZE + 1, y * HOLD_TILE_SIZE + 1,
                    (x+1) * HOLD_TILE_SIZE + 2, (y+1) * HOLD_TILE_SIZE + 2,
                    fill = "#000",
                    outline = ""
                )
            for y in range(4)]
        for x in range(4)]
        left, right = ["right", "left"] if inverted else ["left", "right"]
        self.side_frame.pack(side=left)
        self.main_frame.pack(side=right)
        self.canvas.pack(side=left)
        self.gauge.pack(side=right)
        self.hold.pack(side="bottom")
        for c in self.next:
            c.pack(side="top")

    def command(self, cmd):
        if self.game.dead:
            return (False,)
        t = False
        if cmd == "Hard Drop":
            self.autolock_cancel()
            if self.autolocking:
                return (False,)
            r = self.game.hard_drop()
            res = ""
            if r[0]:
                res += "T-Spin "
            if r[1] > 0:
                res += ["", "Single\t", "Double\t", "Triple\t", "Tetris\t"][r[1]]
            if r[2] > 1:
                res += str(r[2]) + " Ren "
            if r[3]:
                res += "PC!! "
            if r[4]:
                res += "B2B!"
            if res != "":
                print("LR"[self.side], LINE_COUNT - self.game.board.totallno, res)
            self.master.exchange_garbage(self.side, *r)
            t = False
        elif cmd == "Left":
            t = self.game.move(False)
        elif cmd == "Right":
            t = self.game.move(True)
        elif cmd == "Soft Drop":
            t = self.game.soft_drop()
        elif cmd == "Gravity":
            t = self.game.gravity()
            # no auto lock here
        elif cmd == "Rotate Right":
            t = self.game.rotate(True)
        elif cmd == "Rotate Left":
            t = self.game.rotate(False)
        elif cmd == "Hold":
            t = self.game.hold_tetrimino()
        if LINE_COUNT != 0 and self.game.board.totallno >= LINE_COUNT:
            self.game.dead = True
            print(time.time() - self.start_time)
        self.display()
        if t:
            self.autolock_cancel()
        return (t,)

    def _das_lr(self, cmd):
        self.command(cmd)
        self.das_lr = self.after(DAS_INTERVAL[self.side], self._das_lr, cmd)

    def _das_g(self):
        self.command("Gravity")
        self.das_g = self.after(DAS_INTERVAL[self.side], self._das_g)

    def start(self, seed):
        self.game.start(seed)
        self.start_time = time.time()

    def display(self):
        self.game.board.update_shadow()
        self.display_board()
        for i, c in enumerate(self.game.next):
            self.display_next(c, i)
        self.display_hold(self.game.hold)
        self.gauge.coords(
            self.gauge_rect,
            (
                0,
                (TILE_SIZE - self.game.pending_garbage) * 20,
                GARBAGE_GAUGE + 2,
                TILE_SIZE * 20 + 2
            )
        )

    def display_board(self):
        b = self.game.board.ext_board()
        for x in range(10):
            for y in range(20):
                self.canvas.itemconfig(
                    self.tiles[y][x],
                    fill = get_color(b[y][x]),
                    outline = "#FFF" if b[y][x][0] == 2 or self.game.dead else ""
                )

    def display_next(self, c, n):
        for x in range(4):
            for y in range(4):
                self.next[n].itemconfig(
                    self.next_rect[n][x][y],
                    fill = get_color([1, c]) if SHAPES[c][y][x] == 1 else ""
                )

    def display_hold(self, c):
        self.hold["bg"] = "#000" if self.game.holdable else "#555"
        for x in range(4):
            for y in range(4):
                self.hold.itemconfig(
                    self.hold_rect[x][y],
                    fill = get_color([1, c]) if SHAPES[c][y][x] == 1 else ""
                )

    def autolock_gravity(self):
        if not self.game.gravity() and self.autolock == -1:
            self.autolock = self.after(LOCK_DELAY, self._autolock)
        self.display()

    def autolock_cancel(self):
        if self.autolock != -1:
            self.after_cancel(self.autolock)
            self.autolock = -1

    def autolock_unprotect(self):
        self.autolocking = False

    def _autolock(self):
        self.game.lock()
        if LINE_COUNT != 0 and self.game.board.totallno >= LINE_COUNT:
            self.game.dead = True
            print(time.time() - self.start_time)
        self.autolock = -1
        self.autolocking = True
        self.after(AUTOLOCK_PROTECTION, self.autolock_unprotect)

class App(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        self.boards = [BoardDisplay(self, side=0), BoardDisplay(self, side=1)]
        self.boards[0].pack(side="left")
        self.boards[1].pack(side="right")
        self.focus_set()
        self.master.resizable(0,0)
        self.bind(sequence="<KeyPress>", func=self.press)
        self.bind(sequence="<KeyRelease>", func=self.release)
        self.debounce = set()

    def _press(self, keysym):
        l, c = KEYS[keysym]
        r = self.boards[l].command(c)
        
    def press(self, event):
        if event.keysym in KEYS and event.keysym not in self.debounce:
            self.debounce.add(event.keysym)
            self._press(event.keysym)
            side = KEYS[event.keysym][0]
            if KEYS[event.keysym][1] in ("Left", "Right"):
                if self.boards[side].das_lr != -1:
                    self.boards[side].after_cancel(self.boards[side].das_lr)
                self.boards[side].das_lr = \
                  self.boards[side].after(DAS_DELAY[side],
                                    self.boards[side]._das_lr, KEYS[event.keysym][1])
            elif KEYS[event.keysym][1] == "Gravity":
                if self.boards[side].das_lr != -1:
                    self.boards[side].after_cancel(self.boards[side].das_g)
                self.boards[side].das_g = \
                  self.boards[side].after(DAS_DELAY[side],
                                    self.boards[side]._das_g)
        elif event.keysym == "q":
            self.destroy()
            self.__init__(master = self.master)
            self.start()
        elif event.keysym == "Escape":
            self.master.destroy()


    def release(self, event):
        if event.keysym in KEYS:
            self.debounce.remove(event.keysym)
            side, c = KEYS[event.keysym]
            if self.boards[side].das_g != -1 and c == "Gravity":
                self.boards[side].after_cancel(self.boards[side].das_g)
                self.boards[side].das_g = -1
            if self.boards[side].das_lr != -1 and c in ("Left", "Right"):
                self.boards[side].after_cancel(self.boards[side].das_lr)
                self.boards[side].das_lr = -1

    def display(self):
        self.boards[0].display()
        self.boards[1].display()

    def start(self):
        s = time.time()
        self.boards[0].start(s)
        self.boards[1].start(s)
        self.display()
        if SIDE != -1 and SIDE != 2:
            self.boards[1-SIDE].game.dead = True
        if GRAVITY > 0:
            self.after(GRAVITY, self._gravity)
        if CHEESE > 0:
            self.after(CHEESE, self._garbage)

    def _gravity(self):
        if not self.boards[0].game.dead:
            self.boards[0].autolock_gravity()
        if not self.boards[1].game.dead:
            self.boards[1].autolock_gravity()
        self.after(GRAVITY, self._gravity)

    def _garbage(self):
        if not self.boards[0].game.dead:
            self.boards[0].game.garbage(CHEESE_SIZE)
            self.boards[0].game.board.move(0, CHEESE_SIZE)
        if not self.boards[1].game.dead:
            self.boards[1].game.garbage(CHEESE_SIZE)
            self.boards[1].game.board.move(0, CHEESE_SIZE)
        self.display()
        self.after(CHEESE, self._garbage)

    def exchange_garbage(self, side, is_tspin, lno, ren, pc, b2b):
        if SIDE == -1: return
        if lno > 0 and TSD and (not is_tspin or lno != 2):
            self.boards[side].game.dead = True
        if TSD:
            return
        glno = ([0,2,4,6] if is_tspin else [0,0,1,2,4])[lno] + int(ren / 2) + (8 if pc else 0) + (1 if b2b else 0)
        if glno > self.boards[side].game.pending_garbage:
            self.boards[1 - side].game.pending_garbage += glno - self.boards[side].game.pending_garbage
            self.boards[side].game.pending_garbage = 0
        else:
            self.boards[side].game.pending_garbage -= glno
        self.boards[0].display()
        self.boards[1].display()

root = tk.Tk()
app = App(master=root)
root.title("Tetris")
app.start()
app.display()
app.mainloop()

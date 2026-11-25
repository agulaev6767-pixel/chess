import random
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.graphics import Color, Ellipse, Line

VALS = {'P':1,'N':3,'B':3,'R':5,'Q':9,'K':0,'.':0}
SHP = {
    'P':"2812,7212,6438,5858,6472,5084,3672,4258,3638",
    'R':"2212,7812,7228,7268,7868,7886,6686,6676,5676,5686,4486,4476,3476,3486,2286,2268,2868,2828",
    'N':"2212,7812,7235,6255,7862,6882,5288,4480,2664,2845,3838,2826",
    'B':"2412,7612,6628,7052,6074,5088,4074,3052,3428",
    'Q':"2212,7812,7230,8472,6656,6282,5060,3882,3456,1672,2830",
    'K':"2212,7812,7232,7862,6068,5576,6476,6484,5584,5592,4592,4584,3684,3676,4576,4068,2262,2832"
}

class Cell(Button):
    def __init__(self, r, c, app, **kw):
        super().__init__(**kw)
        self.r, self.c, self.app = r, c, app
        self.background_normal = ''
        self.bind(pos=self.upd, size=self.upd)

    def on_release(self):
        self.app.tap(self.r, self.c)

    def upd(self, *a):
        self.canvas.after.clear()
        p = self.app.b[self.r][self.c]
        with self.canvas.after:
            if p != '.':
                iw = p.isupper()
                pts = list()
                for pt in SHP[p.upper()].split(','):
                    pts.extend((self.x + int(pt[:2])*0.01*self.width, self.y + int(pt[2:])*0.01*self.height))
                Color(*(1,1,1,1) if iw else (0.12,0.12,0.12,1))
                Line(points=pts, close=True, width=2.2)
            if (self.r, self.c) in self.app.h:
                Color(0.1, 0.1, 0.1, 0.55)
                d = self.width * (0.45 if p != '.' else 0.3)
                Ellipse(pos=(self.center_x - d/2, self.center_y - d/2), size=(d, d))
class ChessApp(App):
    def build(self):
        self.bot_mode = True
        root = BoxLayout(orientation='vertical', padding=8, spacing=8)
        top = BoxLayout(size_hint_y=0.1, spacing=8)
        self.b1 = Button(text="BOT", background_normal='', background_color=(0.3,0.69,0.31,1), bold=True)
        self.b2 = Button(text="2 PLAYERS", background_normal='', background_color=(0.25,0.25,0.25,1), bold=True)
        self.b1.bind(on_release=lambda x: self.init_game(True))
        self.b2.bind(on_release=lambda x: self.init_game(False))
        top.add_widget(self.b1); top.add_widget(self.b2)
        root.add_widget(top)

        self.st_lbl = Label(text="HOD: BELYE", size_hint_y=0.07, bold=True)
        root.add_widget(self.st_lbl)

        grid = GridLayout(cols=8, rows=8, size_hint_y=0.63)
        self.cells = dict()
        for r in range(8):
            for c in range(8):
                btn = Cell(r, c, self)
                self.cells[(r, c)] = btn
                grid.add_widget(btn)
        root.add_widget(grid)

        self.chat = Label(text="", size_hint_y=0.2, halign="left", valign="top")
        self.chat.bind(size=self.chat.setter('text_size'))
        root.add_widget(self.chat)
        self.init_game(True)
        return root

    def init_game(self, bot):
        self.bot_mode, self.w, self.sel, self.h, self.last, self.over = bot, True, None, list(), tuple(), False
        self.b1.background_color = (0.3,0.69,0.31,1) if bot else (0.25,0.25,0.25,1)
        self.b2.background_color = (0.3,0.69,0.31,1) if not bot else (0.25,0.25,0.25,1)
        self.cas = {"K":True,"Q":True,"k":True,"q":True}
        self.b = list(list(r) for r in ("rnbqkbnr","pppppppp","........","........","........","........","PPPPPPPP","RNBQKBNR"))
        self.log = list(); self.chat.text = ""; self.st_lbl.text = "HOD: BELYE"; self.draw()

    def raw_ok(self, b, r1, c1, r2, c2, wt):
        p, tg = b[r1][c1], b[r2][c2]
        if p=='.' or p.isupper()!=wt or (tg!='.' and tg.isupper()==wt) or (r1,c1)==(r2,c2): return False
        dr, dc = r2-r1, c2-c1; adr, adc, tp = abs(dr), abs(dc), p.upper()
        def clr():
            sr, sc = (r2>r1)-(r2<r1), (c2>c1)-(c2<c1); r, c = r1+sr, c1+sc
            while (r,c)!=(r2,c2):
                if b[r][c]!='.': return False
                r+=sr; c+=sc
            return True
        if tp=='P':
            d, sr = (-1,6) if wt else (1,1)
            return (dc==0 and tg=='.' and (dr==d or (r1==sr and dr==2*d and b[r1+d][c1]=='.'))) or (adc==1 and dr==d and tg!='.')
        return ((dr==0 or dc==0) and clr()) if tp=='R' else (((adr,adc) in ((2,1),(1,2))) if tp=='N' else ((adr==adc and clr()) if tp=='B' else (((dr==0 or dc==0 or adr==adc) and clr()) if tp=='Q' else (adr<=1 and adc<=1))))

    def chk(self, b, wt):
        k = 'K' if wt else 'k'
        kr, kc = next(((r,c) for r in range(8) for c in range(8) if b[r][c]==k), (-1,-1))
        return any(self.raw_ok(b,r,c,kr,kc,not wt) for r in range(8) for c in range(8) if b[r][c]!='.' and b[r][c].isupper()!=wt)

    def sim(self, b, r1, c1, r2, c2):
        nb = list(list(r) for r in b); p = nb[r1][c1]; nb[r2][c2], nb[r1][c1] = p, '.'
        if p.upper()=='K' and abs(c2-c1)==2:
            row = nb[r1]; rc = 'R' if p.isupper() else 'r'
            if c2==6: row.pop(7); row.insert(7,'.'); row.pop(5); row.insert(5,rc)
            elif c2==2: row.pop(0); row.insert(0,'.'); row.pop(3); row.insert(3,rc)
        if p=='P' and r2==0: nb[r2][c2]='Q'
        elif p=='p' and r2==7: nb[r2][c2]='q'
        return nb

    def moves(self, b, r1, c1, wt):
        res = list((r2,c2) for r2 in range(8) for c2 in range(8) if self.raw_ok(b,r1,c1,r2,c2,wt) and not self.chk(self.sim(b,r1,c1,r2,c2),wt))
        if b[r1][c1].upper()=='K' and not self.chk(b,wt):
            row = 7 if wt else 0; ks, qs = ('K','Q') if wt else ('k','q')
            if r1==row and c1==4:
                c0,c1_,c2_,c3_,c4_,c5_,c6_,c7_ = b[row]
                if self.cas[ks] and c5_==c6_=='.' and c7_.upper()=='R' and not self.chk(self.sim(b,row,4,row,5),wt) and not self.chk(self.sim(b,row,4,row,6),wt): res.append((row,6))
                if self.cas[qs] and c1_==c2_==c3_=='.' and c0.upper()=='R' and not self.chk(self.sim(b,row,4,row,3),wt) and not self.chk(self.sim(b,row,4,row,2),wt): res.append((row,2))
        return res

    def draw(self):
        ic, kc = self.chk(self.b, self.w), ('K' if self.w else 'k')
        for r in range(8):
            for c in range(8):
                il, cell = (r+c)%2==0, self.cells[(r,c)]
                col = (0.73,0.79,0.27,1) if self.sel==(r,c) else ((0.88,0.32,0.32,1) if ic and self.b[r][c]==kc else (((0.8,0.82,0.42,1) if il else (0.67,0.64,0.23,1)) if (r,c) in self.last else ((0.94,0.85,0.71,1) if il else (0.71,0.53,0.39,1))))
                cell.background_color = col; cell.upd()

    def do_move(self, r1, c1, r2, c2):
        p, ww = self.b[r1][c1], self.w
        msg = ("WHITE" if ww else ("BOT" if self.bot_mode else "BLACK")) + ": " + chr(65+c1)+str(8-r1) + "-" + chr(65+c2)+str(8-r2)
        if p=='K': self.cas["K"]=self.cas["Q"]=False
        elif p=='k': self.cas["k"]=self.cas["q"]=False
        if (7,0) in ((r1,c1),(r2,c2)): self.cas["Q"]=False
        if (7,7) in ((r1,c1),(r2,c2)): self.cas["K"]=False
        if (0,0) in ((r1,c1),(r2,c2)): self.cas["q"]=False
        if (0,7) in ((r1,c1),(r2,c2)): self.cas["k"]=False
        self.b, self.last, self.w = self.sim(self.b,r1,c1,r2,c2), ((r1,c1),(r2,c2)), not ww
        if not any(self.moves(self.b,r,c,self.w) for r in range(8) for c in range(8) if self.b[r][c]!='.' and self.b[r][c].isupper()==self.w):
            self.over = True
            if self.chk(self.b, self.w):
                msg += "!"; self.st_lbl.text = ("POBEDA!" if ww else "PROIGRYSH!") if self.bot_mode else ("WHITE WIN!" if ww else "BLACK WIN!")
            else: self.st_lbl.text = "NICHYA!"
        else:
            if self.chk(self.b, self.w): msg += "!"
            self.st_lbl.text = "HOD: BELYE" if self.w else ("BOT DUMAET..." if self.bot_mode else "HOD: CHERNYE")
        self.log.append(msg)
        self.chat.text = "\n".join(self.log[max(0, len(self.log)-5):])

    def bot_turn(self, dt):
        if self.over: return
        ms = list((r1,c1,r2,c2) for r1 in range(8) for c1 in range(8) if self.b[r1][c1]!='.' and not self.b[r1][c1].isupper() for r2,c2 in self.moves(self.b,r1,c1,False))
        if ms:
            best = max(VALS[self.b[r2][c2].upper()] for r1,c1,r2,c2 in ms)
            self.do_move(*random.choice(list((r1,c1,r2,c2) for r1,c1,r2,c2 in ms if VALS[self.b[r2][c2].upper()]==best))); self.draw()

    def tap(self, r, c):
        if self.over or (self.bot_mode and not self.w): return
        if self.sel and (r,c) in self.h:
            self.do_move(*self.sel, r, c); self.sel=None; self.h=list(); self.draw()
            if not self.over and self.bot_mode and not self.w: Clock.schedule_once(self.bot_turn, 0.25)
            return
        p = self.b[r][c]
        self.sel, self.h = ((r,c), self.moves(self.b,r,c,self.w)) if (p!='.' and p.isupper()==self.w) else (None, list())
        self.draw()

if __name__ == '__main__':
    ChessApp().run()

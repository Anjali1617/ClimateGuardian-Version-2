"""
=============================================================
  PLANET EARTH SUSTAINABILITY SIMULATION  —  Python / Pygame
=============================================================
  Install:  pip install pygame
  Run:      python planet_game.py

  RULES:
  - Collect 50 GOOD points  → YOU WIN!
  - Collect 15 BAD  points  → YOU LOSE!
  - Press E at any time     → Exit with result screen
  - On result screen: press ENTER to play again, ESC to quit
=============================================================
"""

import pygame
import math
import random
import sys
import json
import os

def save_score(score_data):
    """Save the final score to a JSON file to integrate with Streamlit."""
    score_file = os.path.join(os.path.dirname(__file__), 'planet_game_score.json')
    try:
        with open(score_file, 'w') as f:
            json.dump(score_data, f)
    except Exception:
        pass

pygame.init()

W, H = 950, 650
FPS  = 60

screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Planet Earth — Sustainability Simulation")
clock  = pygame.time.Clock()

font_huge = pygame.font.SysFont("arial", 52, bold=True)
font_big  = pygame.font.SysFont("arial", 34, bold=True)
font_mid  = pygame.font.SysFont("arial", 15, bold=True)
font_sml  = pygame.font.SysFont("arial", 12, bold=True)
font_xs   = pygame.font.SysFont("arial", 10, bold=True)

WHITE  = (255, 255, 255)
BLACK  = (  0,   0,   0)
GREEN  = ( 68, 238, 128)
RED    = (238,  50,  34)
YELLOW = (255, 220,  50)

GY = int(H * 0.57)   # ground top y
OY = int(H * 0.72)   # ocean  top y

WIN_GOOD  = 50   # good points needed to WIN
LOSE_BAD  = 15   # bad  points to trigger LOSE


# ══════════════════════════════════════════════════════════
#  HELPERS — Particle, Puff
# ══════════════════════════════════════════════════════════
class Particle:
    def __init__(self, x, y, col):
        a = random.uniform(0, math.pi * 2)
        s = random.uniform(2, 7)
        self.x  = float(x); self.y  = float(y)
        self.vx = math.cos(a)*s; self.vy = math.sin(a)*s
        self.life = 60; self.col = col

    def update(self):
        self.x += self.vx; self.y += self.vy
        self.vy += 0.15;   self.life -= 1

    def draw(self, surf):
        if self.life <= 0: return
        a = max(0, int(255 * self.life / 60))
        s = pygame.Surface((10, 10), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.col, a), (5, 5), 4)
        surf.blit(s, (int(self.x)-5, int(self.y)-5))


class Puff:
    def __init__(self, x, y, col):
        self.x = x + random.uniform(-4, 4); self.y = float(y)
        self.r = random.uniform(6, 10);      self.alpha = 180
        self.vx = random.uniform(-0.4, 0.4); self.col = col

    def update(self):
        self.y -= 0.9; self.r = min(self.r+0.4, 38)
        self.alpha -= 3; self.x += self.vx

    def alive(self): return self.alpha > 0

    def draw(self, surf):
        r = int(self.r)
        s = pygame.Surface((r*2+4, r*2+4), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.col, int(self.alpha)), (r+2, r+2), r)
        surf.blit(s, (int(self.x)-r-2, int(self.y)-r-2))


# ══════════════════════════════════════════════════════════
#  WORLD OBJECTS
# ══════════════════════════════════════════════════════════
class Tree:
    def __init__(self):
        self.x = random.uniform(20, W-20)
        self.y = GY - random.uniform(5, 25)
        self.h = random.uniform(38, 75)
        self.sway = random.uniform(0, 6.28)

    def draw(self, surf, forest_pct):
        self.sway += 0.018
        sw  = math.sin(self.sway)*2.2
        idx = int((self.x/W)*100)
        dead = forest_pct < 25 or idx > int(forest_pct)
        tx = int(self.x+sw*0.3); ty = int(self.y); th = int(self.h)
        pygame.draw.rect(surf, (122,58,16) if dead else (90,42,8), (tx-4, ty, 8, int(th*0.45)))
        if not dead:
            lc = (42,138,16) if forest_pct>55 else ((90,122,16) if forest_pct>35 else (120,106,16))
            pygame.draw.circle(surf, lc, (int(self.x+sw), int(ty-th*0.2)), int(th*0.4))
        else:
            pygame.draw.line(surf,(122,58,16),(int(self.x),ty),(int(self.x+sw-10),ty-int(th*0.48)),3)
            pygame.draw.line(surf,(122,58,16),(int(self.x),ty-int(th*0.22)),(int(self.x+sw+9),ty-int(th*0.52)),3)


class Factory:
    def __init__(self, coal=False):
        self.x = random.uniform(60, W-60)
        self.y = GY-18; self.coal=coal; self.puffs=[]

    def update(self):
        if random.random()<0.18:
            sc = (70,52,52) if self.coal else (160,160,160)
            self.puffs.append(Puff(self.x+3,  self.y-62, sc))
            self.puffs.append(Puff(self.x+24, self.y-57, sc))
        for p in self.puffs: p.update()
        self.puffs = [p for p in self.puffs if p.alive()]

    def draw(self, surf):
        col  = (68,50,50)  if self.coal else (80,80,96)
        col2 = (50,34,34)  if self.coal else (96,96,112)
        fx=int(self.x); fy=int(self.y)
        pygame.draw.rect(surf,col, (fx-24,fy-48,48,48))
        pygame.draw.rect(surf,col2,(fx-30,fy-36,10,36))
        pygame.draw.rect(surf,col2,(fx+20,fy-54,10,54))
        pygame.draw.rect(surf,col2,(fx-9, fy-60,15,60))
        for p in self.puffs: p.draw(surf)


class Solar:
    def __init__(self):
        self.x=random.uniform(30,W-30); self.y=GY

    def draw(self,surf):
        sx=int(self.x); sy=int(self.y)
        pygame.draw.rect(surf,(26,106,74), (sx-18,sy,36,8))
        pygame.draw.rect(surf,(16,144,220),(sx-14,sy-11,12,9))
        pygame.draw.rect(surf,(16,144,220),(sx+2, sy-11,12,9))
        pygame.draw.rect(surf,(0,200,255), (sx-14,sy-11,12,9),1)
        pygame.draw.rect(surf,(0,200,255), (sx+2, sy-11,12,9),1)


class Turbine:
    def __init__(self):
        self.x=random.uniform(50,W-50); self.y=GY-80; self.angle=random.uniform(0,6.28)

    def update(self): self.angle+=0.055

    def draw(self,surf):
        tx=int(self.x); ty=int(self.y)
        pygame.draw.line(surf,(200,200,200),(tx,GY),(tx,ty),4)
        for b in range(3):
            ang=self.angle+b*(math.pi*2/3); bl=36
            ex=tx+int(math.sin(ang)*bl); ey=ty-int(math.cos(ang)*bl)
            pts=[(tx+int(math.sin(ang-0.15)*8),ty-int(math.cos(ang-0.15)*8)),
                 (ex,ey),(tx+int(math.sin(ang+0.15)*8),ty-int(math.cos(ang+0.15)*8))]
            pygame.draw.polygon(surf,(220,220,220),pts)
        pygame.draw.circle(surf,(140,140,140),(tx,ty),6)


class Fish:
    def __init__(self):
        self.x=random.uniform(0,W); self.y=OY+random.uniform(10,H-OY-20)
        self.vx=random.choice([-1,1])*random.uniform(0.5,1.0)
        self.size=random.uniform(8,16)
        self.col=random.choice([(80,170,255),(255,170,80),(80,220,160)])

    def update(self):
        self.x+=self.vx
        if self.x>W+20: self.x=-20
        if self.x<-20:  self.x=W+20

    def draw(self,surf):
        fw=int(self.size); fh=max(1,int(self.size*0.48))
        s=pygame.Surface((fw*4+4,fh*4+4),pygame.SRCALPHA)
        pygame.draw.ellipse(s,(*self.col,200),(fw,fh,fw*2,fh*2))
        tail=[(0,fh+fh//2),(fw,fh),(fw,fh*2+fh//2)] if self.vx>0 else [(fw*4,fh+fh//2),(fw*3,fh),(fw*3,fh*2+fh//2)]
        pygame.draw.polygon(s,(*self.col,200),tail)
        surf.blit(s,(int(self.x)-fw*2,int(self.y)-fh*2))


class OilRig:
    def __init__(self):
        self.x=random.uniform(40,W-40); self.y=OY+10

    def draw(self,surf):
        rx=int(self.x); ry=int(self.y)
        pygame.draw.line(surf,(130,130,130),(rx-20,ry),(rx+20,ry),3)
        pygame.draw.line(surf,(130,130,130),(rx-14,ry),(rx,ry-32),3)
        pygame.draw.line(surf,(130,130,130),(rx,ry-32),(rx+14,ry),3)
        pygame.draw.rect(surf,(68,68,68),(rx-6,ry-36,12,8))
        s=pygame.Surface((44,14),pygame.SRCALPHA)
        pygame.draw.ellipse(s,(150,90,20,130),(0,0,44,14))
        surf.blit(s,(rx-22,ry+4))


class Trash:
    def __init__(self):
        self.x=random.uniform(0,W); self.y=OY+random.uniform(10,H-OY-10)

    def draw(self,surf):
        pygame.draw.rect(surf,(180,120,40),(int(self.x),int(self.y),14,5))
        pygame.draw.rect(surf,(100,130,50),(int(self.x)+5,int(self.y)-4,9,4))


class Cloud:
    def __init__(self):
        self.x=random.uniform(0,W); self.y=random.uniform(H*0.05,H*0.2)
        self.w=random.uniform(80,150); self.spd=random.uniform(0.2,0.45)

    def update(self):
        self.x+=self.spd
        if self.x>W+self.w: self.x=-self.w

    def draw(self,surf,temp):
        alpha=220 if temp<2 else (100 if temp<3 else 45)
        col=(255,255,255) if temp<2 else ((200,140,80) if temp<3 else (160,80,50))
        cw=int(self.w)
        s=pygame.Surface((cw*2,60),pygame.SRCALPHA)
        pygame.draw.ellipse(s,(*col,alpha),(0,      22,cw,       28))
        pygame.draw.ellipse(s,(*col,alpha),(cw//4,  10,cw//2+20, 26))
        pygame.draw.ellipse(s,(*col,alpha),(cw//2,  18,cw//2,    22))
        surf.blit(s,(int(self.x-cw//2),int(self.y)-20))


# ══════════════════════════════════════════════════════════
#  MENU BUTTON (radial)
# ══════════════════════════════════════════════════════════
class MenuButton:
    R = 42

    def __init__(self, label, icon, good, fn):
        self.label=label; self.icon=icon; self.good=good; self.fn=fn
        self.cx=0; self.cy=0

    def set_pos(self,cx,cy): self.cx=cx; self.cy=cy

    def hit(self,mx,my): return math.hypot(mx-self.cx,my-self.cy)<self.R

    def draw(self,surf):
        col      = (30,160,70)  if self.good else (200,40,30)
        ring_col = (68,255,136) if self.good else (255,68,68)
        pygame.draw.circle(surf,col,     (self.cx,self.cy),self.R)
        pygame.draw.circle(surf,ring_col,(self.cx,self.cy),self.R+3,3)
        pygame.draw.circle(surf,BLACK,   (self.cx,self.cy),self.R,1)
        it=font_mid.render(self.icon,True,WHITE)
        surf.blit(it,(self.cx-it.get_width()//2, self.cy-18))
        lt=font_xs.render(self.label.split()[0],True,WHITE)
        surf.blit(lt,(self.cx-lt.get_width()//2, self.cy+4))
        tag="GOOD" if self.good else "BAD"
        tg=font_xs.render(tag,True,(150,255,180) if self.good else (255,140,140))
        surf.blit(tg,(self.cx-tg.get_width()//2, self.cy+16))


# ══════════════════════════════════════════════════════════
#  MAIN GAME
# ══════════════════════════════════════════════════════════
class Game:
    def __init__(self): self.reset()

    def reset(self):
        self.temp   = 1.0; self.forest=65.0; self.energy=20.0; self.ocean=75.0
        self.good_pts = 0   # cumulative GOOD points collected
        self.bad_pts  = 0   # cumulative BAD  points collected
        self.phase    = "play"   # play | result
        self.result   = ""       # "win" | "lose" | "exit_win" | "exit_lose"
        self.msg=""; self.msg_timer=0; self.msg_good=True
        self.particles=[]
        self.trees    =[Tree()    for _ in range(14)]
        self.factories=[Factory() for _ in range(3)]
        self.solars=[]; self.turbines=[]
        self.fish_list=[Fish() for _ in range(10)]
        self.oil_rigs=[]; self.trashes=[]
        self.clouds=[Cloud() for _ in range(5)]
        self.menu_open=False; self.menu_cx=W//2; self.menu_cy=H//2
        self.menu_btns=[]
        self._refresh_menu()

    # ── action factory ───────────────────────────────────
    def _make_actions(self):
        return [
            # GOOD
            MenuButton("Plant Trees",   "T", True,  self._act_plant_trees),
            MenuButton("Solar Farm",    "S", True,  self._act_solar),
            MenuButton("Wind Power",    "W", True,  self._act_wind),
            MenuButton("Clean Ocean",   "O", True,  self._act_clean_ocean),
            MenuButton("Recycle",       "Re",True,  self._act_recycle),
            # BAD
            MenuButton("Build Factory", "F", False, self._act_factory),
            MenuButton("Dump Trash",    "D", False, self._act_dump_trash),
            MenuButton("Cut Forest",    "C", False, self._act_cut_forest),
            MenuButton("Oil Drilling",  "R", False, self._act_oil_drill),
            MenuButton("Coal Plant",    "K", False, self._act_coal_plant),
        ]

    def _refresh_menu(self):
        all_a=self._make_actions()
        good=[a for a in all_a if a.good]; bad=[a for a in all_a if not a.good]
        random.shuffle(good); random.shuffle(bad)
        chosen=good[:4]+bad[:4]; random.shuffle(chosen)
        self.menu_btns=chosen

    def _place_menu(self):
        n=len(self.menu_btns); R=int(min(W,H)*0.26)
        for i,btn in enumerate(self.menu_btns):
            ang=-math.pi/2+(i/n)*math.pi*2
            btn.set_pos(int(self.menu_cx+math.cos(ang)*R),
                        int(self.menu_cy+math.sin(ang)*R))

    def _burst(self,x,y,col):
        for _ in range(22): self.particles.append(Particle(x,y,col))

    def _show_msg(self,text,good):
        self.msg=text; self.msg_timer=220; self.msg_good=good

    # ── add points ───────────────────────────────────────
    def _add_good(self, pts):
        self.good_pts+=pts
        if self.good_pts>=WIN_GOOD:
            self.good_pts=WIN_GOOD
            self.phase="result"; self.result="win"

    def _add_bad(self, pts):
        self.bad_pts+=pts
        if self.bad_pts>=LOSE_BAD:
            self.bad_pts=LOSE_BAD
            self.phase="result"; self.result="lose"

    # ── GOOD actions ─────────────────────────────────────
    def _act_plant_trees(self):
        self.forest=min(100,self.forest+9); self.temp=round(self.temp-0.12,2)
        for _ in range(5): self.trees.append(Tree())
        self._burst(self.menu_cx,self.menu_cy,(60,180,80))
        self._show_msg("+10 GOOD pts   Trees planted! Forest grows.", True)
        self._add_good(10)

    def _act_solar(self):
        self.energy=min(100,self.energy+10)
        for _ in range(4): self.solars.append(Solar())
        self._burst(self.menu_cx,self.menu_cy,(255,190,0))
        self._show_msg("+8 GOOD pts   Solar farm built!", True)
        self._add_good(8)

    def _act_wind(self):
        self.energy=min(100,self.energy+8); self.temp=round(self.temp-0.08,2)
        self.turbines.append(Turbine())
        self._burst(self.menu_cx,self.menu_cy,(80,160,255))
        self._show_msg("+7 GOOD pts   Wind turbine spinning!", True)
        self._add_good(7)

    def _act_clean_ocean(self):
        self.ocean=min(100,self.ocean+14)
        self.trashes=self.trashes[max(0,len(self.trashes)-6):]
        self._burst(self.menu_cx,self.menu_cy,(20,150,255))
        self._show_msg("+10 GOOD pts   Ocean cleaned! Fish thrive.", True)
        self._add_good(10)

    def _act_recycle(self):
        self.forest=min(100,self.forest+3); self.ocean=min(100,self.ocean+3)
        self._burst(self.menu_cx,self.menu_cy,(0,220,160))
        self._show_msg("+8 GOOD pts   Recycling program started!", True)
        self._add_good(8)

    # ── BAD actions ──────────────────────────────────────
    def _act_factory(self):
        self.factories.append(Factory(coal=False))
        self.temp=round(self.temp+0.25,2)
        self._burst(self.menu_cx,self.menu_cy,(220,80,40))
        self._show_msg("+3 BAD pts   Factory built! Pollution rises.", False)
        self._add_bad(3)

    def _act_dump_trash(self):
        self.ocean=max(0,self.ocean-12)
        for _ in range(6): self.trashes.append(Trash())
        self._burst(self.menu_cx,self.menu_cy,(160,100,30))
        self._show_msg("+4 BAD pts   Trash dumped in ocean!", False)
        self._add_bad(4)

    def _act_cut_forest(self):
        self.forest=max(0,self.forest-14); self.temp=round(self.temp+0.22,2)
        cut=min(6,len(self.trees)); self.trees=self.trees[cut:]
        self._burst(self.menu_cx,self.menu_cy,(180,100,20))
        self._show_msg("+4 BAD pts   Forest cut! Temperature spikes.", False)
        self._add_bad(4)

    def _act_oil_drill(self):
        self.ocean=max(0,self.ocean-10); self.energy=max(0,self.energy-5)
        self.oil_rigs.append(OilRig())
        self._burst(self.menu_cx,self.menu_cy,(160,60,60))
        self._show_msg("+3 BAD pts   Oil rig placed! Ocean polluted.", False)
        self._add_bad(3)

    def _act_coal_plant(self):
        self.temp=round(self.temp+0.30,2); self.energy=max(0,self.energy-8)
        self.factories.append(Factory(coal=True))
        self._burst(self.menu_cx,self.menu_cy,(100,50,50))
        self._show_msg("+5 BAD pts   Coal plant! Sky turns toxic!", False)
        self._add_bad(5)

    # ── input ────────────────────────────────────────────
    def handle_click(self,mx,my):
        if self.phase=="result":
            self.reset(); return
        if self.menu_open:
            for btn in self.menu_btns:
                if btn.hit(mx,my):
                    btn.fn(); self.menu_open=False; self._refresh_menu(); return
            self.menu_open=False; return
        R=int(min(W,H)*0.26)
        self.menu_cx=max(R+50,min(W-R-50,mx))
        self.menu_cy=max(R+50,min(H-R-50,my))
        self.menu_open=True; self._place_menu()
        self._burst(mx,my,(255,255,255))

    def handle_key(self,key):
        if key==pygame.K_e:
            # E pressed — exit to result
            if self.phase=="play":
                if self.good_pts>=WIN_GOOD:
                    self.result="exit_win"
                elif self.bad_pts>=LOSE_BAD:
                    self.result="exit_lose"
                elif self.good_pts>self.bad_pts*2:
                    self.result="exit_win"
                else:
                    self.result="exit_lose"
                self.phase="result"
        if self.phase=="result":
            if key==pygame.K_RETURN: self.reset()
            if key==pygame.K_ESCAPE: 
                save_score({'result': self.result, 'good_pts': self.good_pts, 'bad_pts': self.bad_pts})
                pygame.quit(); sys.exit()

    # ── update ───────────────────────────────────────────
    def update(self):
        for p in self.particles: p.update()
        self.particles=[p for p in self.particles if p.life>0]
        for f in self.factories: f.update()
        for t in self.turbines:  t.update()
        for f in self.fish_list: f.update()
        for cl in self.clouds:   cl.update()
        if self.msg_timer>0: self.msg_timer-=1

    # ── master draw ──────────────────────────────────────
    def draw(self,surf,t_ms):
        self._draw_sky(surf)
        self._draw_sun(surf)
        for cl in self.clouds:    cl.draw(surf,self.temp)
        self._draw_mountains(surf)
        self._draw_ground(surf)
        for tr in self.trees:     tr.draw(surf,self.forest)
        for sl in self.solars:    sl.draw(surf)
        for tb in self.turbines:  tb.draw(surf)
        for fc in self.factories: fc.draw(surf)
        self._draw_ocean(surf,t_ms)
        for og in self.oil_rigs:  og.draw(surf)
        for tr in self.trashes:   tr.draw(surf)
        n=int((self.ocean/100)*len(self.fish_list))
        for f in self.fish_list[:n]: f.draw(surf)
        for p in self.particles:  p.draw(surf)
        self._draw_hud(surf)
        self._draw_scoreboards(surf)
        self._draw_e_hint(surf)
        self._draw_legend(surf)
        if self.menu_open: self._draw_menu(surf)
        self._draw_msg(surf)
        if self.phase=="result": self._draw_result(surf)

    # ── draw helpers ─────────────────────────────────────
    @staticmethod
    def _lerp(c1,c2,t):
        t=max(0,min(1,t))
        return tuple(int(c1[i]+(c2[i]-c1[i])*t) for i in range(3))

    def _draw_sky(self,surf):
        t=self.temp
        if   t<1.5: top,bot=(74,168,232),(184,232,248)
        elif t<2.5: top,bot=(192,136,64),(224,176,96)
        elif t<3.5: top,bot=(160,80,32),(192,96,48)
        else:       top,bot=(112,32,16),(144,32,32)
        for y in range(int(H*0.58)+1):
            pygame.draw.line(surf,self._lerp(top,bot,y/(H*0.58)),(0,y),(W,y))

    def _draw_sun(self,surf):
        t=self.temp
        if   t<1.5: col,sz=(255,224,80),28
        elif t<2.5: col,sz=(255,144,16),36
        elif t<3.5: col,sz=(255,80,0),44
        else:       col,sz=(255,32,0),54
        cx,cy=int(W*0.84),int(H*0.1)
        for r in range(sz+18,sz,-5):
            a=max(0,55-(r-sz)*9)
            gs=pygame.Surface((r*2,r*2),pygame.SRCALPHA)
            pygame.draw.circle(gs,(*col,a),(r,r),r); surf.blit(gs,(cx-r,cy-r))
        pygame.draw.circle(surf,col,(cx,cy),sz)

    def _draw_mountains(self,surf):
        col=(42,96,16) if self.forest>50 else ((106,80,16) if self.forest>30 else (122,40,10))
        s=pygame.Surface((W,H),pygame.SRCALPHA)
        for px,mh in [(0.08,110),(0.28,155),(0.52,138),(0.74,108),(0.92,88)]:
            cx2=int(W*px)
            pygame.draw.polygon(s,(*col,100),[(cx2-mh,GY),(cx2,GY-int(mh*0.68)),(cx2+mh,GY)])
        surf.blit(s,(0,0))

    def _draw_ground(self,surf):
        f=self.forest
        gc=(58,122,26) if f>55 else ((122,106,16) if f>35 else ((139,64,16) if f>15 else (106,40,10)))
        pygame.draw.rect(surf,gc,(0,GY,W,OY-GY))
        pygame.draw.rect(surf,(90,48,16),(0,OY-14,W,20))

    def _draw_ocean(self,surf,t_ms):
        o=self.ocean
        oc=(26,111,168) if o>65 else ((26,96,80) if o>40 else ((74,74,32) if o>20 else (58,40,10)))
        pygame.draw.rect(surf,oc,(0,OY,W,H-OY))
        for wv in range(6):
            wx=int(((t_ms/1300+wv*0.18)%1)*W)
            s2=pygame.Surface((52,16),pygame.SRCALPHA)
            pygame.draw.arc(s2,(255,255,255,55),(0,0,52,16),0,math.pi,2)
            surf.blit(s2,(wx,OY+8+wv*8))
        if o<40:
            ov=pygame.Surface((W,H-OY),pygame.SRCALPHA); ov.fill((100,60,20,110)); surf.blit(ov,(0,OY))

    def _draw_hud(self,surf):
        pad=8; bw=(W-pad*5)//4; bh=26
        bars=[
            (f"Temp +{self.temp:.1f}C",min(1.0,self.temp/4.2),(80,210,80) if self.temp<2 else (230,60,60)),
            (f"Forest {int(self.forest)}%",self.forest/100,(60,180,60)),
            (f"Energy {int(self.energy)}%",self.energy/100,(255,180,0)),
            (f"Ocean  {int(self.ocean)}%", self.ocean/100, (30,150,255)),
        ]
        for i,(lbl,val,col) in enumerate(bars):
            bx=pad+(bw+pad)*i; by=8
            bg=pygame.Surface((bw,bh),pygame.SRCALPHA); bg.fill((0,0,0,160)); surf.blit(bg,(bx,by))
            pygame.draw.rect(surf,col,(bx,by,max(8,int(bw*val)),bh))
            pygame.draw.rect(surf,BLACK,(bx,by,bw,bh),1)
            t=font_sml.render(lbl,True,WHITE); surf.blit(t,(bx+bw//2-t.get_width()//2,by+5))

    def _draw_scoreboards(self,surf):
        # ── GOOD points bar (left) ──────────────────────
        bx=10; by=42; bw=180; bh=22
        bg=pygame.Surface((bw,bh),pygame.SRCALPHA); bg.fill((0,0,0,160)); surf.blit(bg,(bx,by))
        fill=int(bw*(self.good_pts/WIN_GOOD))
        pygame.draw.rect(surf,(40,200,80),(bx,by,fill,bh))
        pygame.draw.rect(surf,(68,255,136),(bx,by,bw,bh),2)
        t=font_sml.render(f"GOOD  {self.good_pts}/{WIN_GOOD}",True,WHITE)
        surf.blit(t,(bx+bw//2-t.get_width()//2,by+3))

        # ── BAD points bar (right of good) ─────────────
        bx2=200; bw2=180
        bg2=pygame.Surface((bw2,bh),pygame.SRCALPHA); bg2.fill((0,0,0,160)); surf.blit(bg2,(bx2,by))
        fill2=int(bw2*(self.bad_pts/LOSE_BAD))
        pygame.draw.rect(surf,(200,40,30),(bx2,by,fill2,bh))
        pygame.draw.rect(surf,(255,68,68),(bx2,by,bw2,bh),2)
        t2=font_sml.render(f"BAD   {self.bad_pts}/{LOSE_BAD}",True,WHITE)
        surf.blit(t2,(bx2+bw2//2-t2.get_width()//2,by+3))

    def _draw_e_hint(self,surf):
        # E key hint — top right corner
        bx=W-115; by=42; bw=105; bh=22
        bg=pygame.Surface((bw,bh),pygame.SRCALPHA); bg.fill((0,0,0,160)); surf.blit(bg,(bx,by))
        pygame.draw.rect(surf,(180,140,0),(bx,by,bw,bh),2)
        t=font_sml.render("Press E to Exit",True,YELLOW); surf.blit(t,(bx+bw//2-t.get_width()//2,by+3))

    def _draw_legend(self,surf):
        if self.menu_open: return
        ls=pygame.Surface((175,46),pygame.SRCALPHA); ls.fill((0,0,0,140)); surf.blit(ls,(8,H-54))
        pygame.draw.circle(surf,(68,255,136),(22,H-38),7)
        t1=font_xs.render("= Good action  +pts",True,WHITE); surf.blit(t1,(34,H-44))
        pygame.draw.circle(surf,(255,68,68),(22,H-20),7)
        t2=font_xs.render("= Bad action   +bad pts",True,WHITE); surf.blit(t2,(34,H-26))

    def _draw_menu(self,surf):
        R=int(min(W,H)*0.26)
        dim=pygame.Surface((W,H),pygame.SRCALPHA)
        pygame.draw.circle(dim,(0,0,0,50),(self.menu_cx,self.menu_cy),R+55)
        surf.blit(dim,(0,0))
        for btn in self.menu_btns: btn.draw(surf)
        pygame.draw.circle(surf,(255,255,255),(self.menu_cx,self.menu_cy),18)
        ct=font_xs.render("X",True,BLACK); surf.blit(ct,(self.menu_cx-ct.get_width()//2,self.menu_cy-ct.get_height()//2))

    def _draw_msg(self,surf):
        if self.msg_timer<=0: return
        alpha=min(255,self.msg_timer*4)
        col=(20,150,70,210) if self.msg_good else (200,40,30,210)
        mw=min(W-32,540); mx=(W-mw)//2; my=int(H*0.37)
        ms=pygame.Surface((mw,44),pygame.SRCALPHA)
        pygame.draw.rect(ms,col,(0,0,mw,44),border_radius=10)
        ms.set_alpha(alpha); surf.blit(ms,(mx,my))
        t=font_mid.render(self.msg,True,WHITE); surf.blit(t,(mx+mw//2-t.get_width()//2,my+13))

    # ── RESULT SCREEN ────────────────────────────────────
    def _draw_result(self,surf):
        # full overlay
        ov=pygame.Surface((W,H),pygame.SRCALPHA)
        ov.fill((0,0,0,210)); surf.blit(ov,(0,0))

        won = self.result in ("win","exit_win")

        # ── big animated border ──────────────────────────
        border_col = GREEN if won else RED
        t_ms = pygame.time.get_ticks()
        thick = 6+int(math.sin(t_ms/200)*3)
        pygame.draw.rect(surf,border_col,(thick,thick,W-thick*2,H-thick*2),thick,border_radius=18)

        # ── trophy / skull icon ──────────────────────────
        icon_cx = W//2
        if won:
            # draw a simple trophy shape
            pygame.draw.rect(surf,YELLOW,(icon_cx-30,H//2-120,60,50),border_radius=8)
            pygame.draw.rect(surf,YELLOW,(icon_cx-12,H//2-70,24,20))
            pygame.draw.rect(surf,YELLOW,(icon_cx-24,H//2-50,48,10),border_radius=4)
            pygame.draw.ellipse(surf,YELLOW,(icon_cx-8,H//2-130,16,16))   # handle left
            pygame.draw.ellipse(surf,YELLOW,(icon_cx-8,H//2-130,16,16))
        else:
            # draw a simple X mark
            pygame.draw.line(surf,RED,(icon_cx-30,H//2-130),(icon_cx+30,H//2-80),10)
            pygame.draw.line(surf,RED,(icon_cx+30,H//2-130),(icon_cx-30,H//2-80),10)

        # ── main title ───────────────────────────────────
        if won:
            title_text = "YOU ARE WINNER!"
            title_col  = GREEN
        else:
            title_text = "YOU LOSE THE GAME!"
            title_col  = RED

        title=font_huge.render(title_text,True,title_col)
        surf.blit(title,(W//2-title.get_width()//2, H//2-68))

        # ── subtitle message ─────────────────────────────
        if won:
            sub="Congratulations! You protected the planet!"
            sub_col=(150,255,180)
        else:
            sub="The planet suffered from your choices!"
            sub_col=(255,140,140)
        s1=font_big.render(sub,True,sub_col)
        surf.blit(s1,(W//2-s1.get_width()//2,H//2-10))

        # ── stats box ────────────────────────────────────
        stats_y=H//2+50
        box_w=400; box_x=W//2-box_w//2
        sb=pygame.Surface((box_w,90),pygame.SRCALPHA); sb.fill((255,255,255,18))
        pygame.draw.rect(sb,(255,255,255,60),(0,0,box_w,90),2,border_radius=10)
        surf.blit(sb,(box_x,stats_y))

        g_t=font_mid.render(f"Good points collected :  {self.good_pts} / {WIN_GOOD}",True,(100,255,140))
        b_t=font_mid.render(f"Bad  points collected :  {self.bad_pts} / {LOSE_BAD}",True,(255,100,100))
        reason_text = "Reached 50 good points!" if won else "Reached 15 bad points!"
        r_t=font_sml.render(reason_text,True,GREEN if won else RED)
        surf.blit(g_t,(box_x+20,stats_y+10))
        surf.blit(b_t,(box_x+20,stats_y+34))
        surf.blit(r_t,(box_x+20,stats_y+62))

        # ── action buttons ───────────────────────────────
        btn_y=H//2+162

        # PLAY AGAIN
        pulse=int(200+math.sin(t_ms/300)*55)
        pa_w=200; pa_x=W//2-pa_w-20; pa_h=46
        pa_s=pygame.Surface((pa_w,pa_h),pygame.SRCALPHA)
        pa_s.fill((30,160,70,pulse)); surf.blit(pa_s,(pa_x,btn_y))
        pygame.draw.rect(surf,(68,255,136),(pa_x,btn_y,pa_w,pa_h),2,border_radius=10)
        pt=font_mid.render("ENTER  — Play Again",True,WHITE)
        surf.blit(pt,(pa_x+pa_w//2-pt.get_width()//2,btn_y+14))

        # QUIT
        qt_w=200; qt_x=W//2+20; qt_h=46
        qt_s=pygame.Surface((qt_w,qt_h),pygame.SRCALPHA)
        qt_s.fill((160,30,30,pulse)); surf.blit(qt_s,(qt_x,btn_y))
        pygame.draw.rect(surf,(255,68,68),(qt_x,btn_y,qt_w,qt_h),2,border_radius=10)
        qtt=font_mid.render("ESC  — Quit Game",True,WHITE)
        surf.blit(qtt,(qt_x+qt_w//2-qtt.get_width()//2,btn_y+14))


# ══════════════════════════════════════════════════════════
#  MAIN LOOP
# ══════════════════════════════════════════════════════════
def main():
    game=Game()
    while True:
        t_ms=pygame.time.get_ticks()
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                result_state = game.result if game.phase == "result" else "quit"
                save_score({'result': result_state, 'good_pts': game.good_pts, 'bad_pts': game.bad_pts})
                pygame.quit(); sys.exit()
            if event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
                game.handle_click(*event.pos)
            if event.type==pygame.KEYDOWN:
                game.handle_key(event.key)

        game.update()
        screen.fill(BLACK)
        game.draw(screen,t_ms)
        pygame.display.flip()
        clock.tick(FPS)

if __name__=="__main__":
    main()
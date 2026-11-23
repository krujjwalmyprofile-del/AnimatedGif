"""Retro game-style GIF: 'Answer vs Value' for the Sandbox GTME post."""
import math, random
from PIL import Image, ImageDraw, ImageFont

W = H = 400          # internal pixel canvas
UP = 2               # upscale -> 800x800
FPS = 12
FONT = ImageFont.truetype("/usr/share/fonts/opentype/unifont/unifont.otf", 16)

SKY = (20, 20, 40); SKY2 = (34, 30, 64); STAR = (120, 120, 170)
WHITE = (240, 240, 232); GREY = (130, 130, 150); DARK = (10, 10, 18)
ORANGE = (255, 110, 50); YELLOW = (255, 210, 60); GREEN = (90, 210, 110)
RED = (230, 60, 70); BLUE = (80, 150, 255); PINK = (240, 110, 190)
BRICK = (150, 70, 50); BRICK2 = (110, 50, 40); GRASS = (70, 170, 90)
GROUND_Y = 320
LOGO = Image.open(__file__.rsplit("/", 1)[0] + "/sandbox-logo.png").convert("RGBA") if "/" in __file__ else Image.open("sandbox-logo.png").convert("RGBA")
OVERLAYS = []  # ("img", image, cx, cy, width) / ("cursor", x, y, scale) in OUTPUT pixels

from PIL import ImageChops, ImageFilter
KX0, KY0, KX1, KY1 = 20, 17, 500, 196       # knob box inside the logo image
TRAVEL = LOGO.width - 23 - 498               # how far the knob slides when pushed

def _pill(size, box, r, ss=4):
    m = Image.new("L", (size[0] * ss, size[1] * ss), 0)
    ImageDraw.Draw(m).rounded_rectangle([v * ss for v in box], radius=r * ss, fill=255)
    return m.resize(size, Image.LANCZOS)

# knob: cut out with its own rounded mask
_kn = LOGO.crop((KX0, KY0, KX1, KY1))
_kn.putalpha(ImageChops.multiply(_kn.getchannel("A"),
             _pill(_kn.size, (3, 2, _kn.width - 3, _kn.height - 1), 82)))
KNOB = _kn
# empty track: paint the knob area with a stretched column of bare track
_tr = LOGO.copy()
_col = LOGO.crop((520, 0, 521, LOGO.height)).resize((KX1 + 6 - 10, LOGO.height))
_tr.paste(_col, (10, 0), _col)
_tr.paste(LOGO.crop((0, 0, 24, LOGO.height)), (0, 0))   # keep the rounded left rim
_tr.putalpha(LOGO.getchannel("A"))
TRACK = _tr
_or = ImageChops.multiply(TRACK.convert("RGB"), Image.new("RGB", TRACK.size, (255, 120, 60)))
TRACK_ON = _or.convert("RGBA"); TRACK_ON.putalpha(LOGO.getchannel("A"))
_sh = Image.new("RGBA", KNOB.size, (0, 0, 0, 0))
ImageDraw.Draw(_sh).rounded_rectangle((6, 14, KNOB.width - 6, KNOB.height + 2), radius=80, fill=(0, 0, 0, 70))
KNOB_SHADOW = _sh.filter(ImageFilter.GaussianBlur(8))

def toggle_image(k):
    """k = 0 (off, the original logo) .. 1 (pushed on)."""
    if k <= 0: return LOGO
    off = int(TRAVEL * k)
    im = TRACK.copy()
    # orange fill grows behind the knob, iOS-switch style
    fill = Image.new("L", im.size, 0)
    ImageDraw.Draw(fill).rectangle((0, 0, KX0 + off + KNOB.width - 30, im.height), fill=255)
    im.paste(TRACK_ON, (0, 0), ImageChops.multiply(fill, LOGO.getchannel("A")))
    im.alpha_composite(KNOB_SHADOW, (KX0 + off, KY0))
    im.alpha_composite(KNOB, (KX0 + off, KY0))
    return im

def logo(cx, cy, width, image=None):
    if width > 4: OVERLAYS.append(("img", image or LOGO, cx, cy, width))

CURSOR = ["X...........", "XX..........", "XWX.........", "XWWX........", "XWWWX.......",
          "XWWWWX......", "XWWWWWX.....", "XWWWWWWX....", "XWWWWWWWX...", "XWWWWWWWWX..",
          "XWWWWWXXXXX.", "XWWXWWX.....", "XWX.XWWX....", "XX..XWWX....", "X....XWWX...",
          ".....XWWX...", "......XX...."]

def draw_cursor(big, x, y, px):
    d = ImageDraw.Draw(big)
    for r, row in enumerate(CURSOR):
        for c, ch in enumerate(row):
            if ch in "XW":
                d.rectangle((x + c * px, y + r * px, x + c * px + px - 1, y + r * px + px - 1),
                            fill=DARK if ch == "X" else WHITE)

random.seed(4)
STARS = [(random.randrange(W), random.randrange(40, 300), random.random() * 6) for _ in range(60)]

# ------------------------------------------------------------- helpers
def clamp(t): return max(0.0, min(1.0, t))
def seg(t, a, b): return clamp((t - a) / (b - a))

def txt(img, x, y, s, col, scale=1, anchor="m"):
    """Bitmap text. anchor: m=center, l=left, r=right (x), y is center."""
    tmp = Image.new("L", (len(s) * 16 + 16, 20), 0)
    d = ImageDraw.Draw(tmp); d.fontmode = "1"
    d.text((0, 1), s, font=FONT, fill=255)
    bb = tmp.getbbox()
    if not bb: return 0
    tmp = tmp.crop((0, 0, bb[2], 18))
    tmp = tmp.resize((tmp.width * scale, tmp.height * scale), Image.NEAREST)
    w = tmp.width
    px = {"m": x - w // 2, "l": x, "r": x - w}[anchor]
    img.paste(Image.new("RGB", tmp.size, col), (int(px), int(y - tmp.height // 2)), tmp)
    return w

def shadow_txt(img, x, y, s, col, scale=1, anchor="m"):
    txt(img, x + scale, y + scale, s, DARK, scale, anchor)
    return txt(img, x, y, s, col, scale, anchor)

def box(d, x0, y0, x1, y1, fill, border=WHITE, bw=2):
    d.rectangle((x0, y0, x1, y1), fill=border)
    d.rectangle((x0 + bw, y0 + bw, x1 - bw, y1 - bw), fill=fill)

PLAYER = ["..HHHH..", ".HHHHHH.", ".HSESES.", ".SSSSSS.", "..SSSS..", ".BBBBBB.",
          "BBBBBBBB", "S.BBBB.S", "..BBBB.."]
LEGS = [["..L..L..", ".LL..LL."], [".L....L.", "LL....LL"], ["..L.L...", ".LL.LL.."]]
EXPERT = ["..GGGG..", ".GGGGGG.", ".GSESES.", ".SSSSSS.", "..SSSS..", ".KKWWKK.",
          "KKKWRKKK", "S.KWRK.S", "..KKKK..", "..K..K..", ".KK..KK."]

def sprite(d, grid, x, y, px, body=ORANGE, hair=(60, 40, 30), flip=False):
    cmap = {"H": hair, "S": (240, 190, 150), "E": DARK, "B": body, "L": (40, 40, 80),
            "G": (180, 180, 190), "K": (90, 90, 110), "W": WHITE, "R": RED}
    for r, row in enumerate(grid):
        if flip: row = row[::-1]
        for c, ch in enumerate(row):
            if ch in cmap:
                d.rectangle((x + c * px, y + r * px, x + c * px + px - 1, y + r * px + px - 1), fill=cmap[ch])

def player(d, x, y, t, running=True, body=ORANGE, hair=(60, 40, 30), px=3, legs=None):
    """(x, y) = feet-center."""
    if legs is None:
        legs = LEGS[int(t * 10) % 2] if running else LEGS[0]
    g = PLAYER + legs
    sprite(d, g, x - 4 * px, y - len(g) * px, px, body, hair)

def qblock(d, x, y, s=18, col=YELLOW, img=None, mark="?"):
    d.rectangle((x, y, x + s, y + s), fill=(160, 100, 20))
    d.rectangle((x + 1, y + 1, x + s - 2, y + s - 2), fill=col)
    if img: txt(img, x + s // 2 + 1, y + s // 2 + 1, mark, (120, 60, 10))

def background(img, d, t, scroll=0.0):
    d.rectangle((0, 0, W, GROUND_Y), fill=SKY)
    d.rectangle((0, 200, W, GROUND_Y), fill=SKY2)
    for (sx, sy, ph) in STARS:
        if math.sin(t * 3 + ph) > -0.3:
            d.point((sx, sy), fill=STAR)
    # skyline (static, parallax-ish)
    for i in range(10):
        bx = (i * 47 - int(scroll * 0.3)) % 470 - 40
        bh = 40 + (i * 37) % 60
        d.rectangle((bx, GROUND_Y - bh, bx + 34, GROUND_Y), fill=(44, 40, 80))
        for wy in range(GROUND_Y - bh + 6, GROUND_Y - 6, 10):
            for wx in (bx + 6, bx + 16, bx + 26):
                if (wx + wy + i) % 3: d.rectangle((wx, wy, wx + 3, wy + 4), fill=(70, 66, 120))
    # ground
    d.rectangle((0, GROUND_Y, W, GROUND_Y + 6), fill=GRASS)
    d.rectangle((0, GROUND_Y + 6, W, H), fill=BRICK)
    off = int(scroll) % 24
    for row in range(5):
        y = GROUND_Y + 6 + row * 12
        d.line((0, y, W, y), fill=BRICK2)
        sh = 12 if row % 2 else 0
        for x in range(-off - 24 + sh, W + 24, 24):
            d.line((x, y, x, y + 12), fill=BRICK2)

def hud(img, d, t, value, day=None, lvl=None, live=False):
    d.rectangle((0, 0, W, 34), fill=DARK)
    d.line((0, 34, W, 34), fill=GREY)
    txt(img, 10, 17, "VALUE", WHITE, anchor="l")
    for i in range(10):
        x = 58 + i * 9
        on = i < value
        col = GREEN if on else ((70, 30, 40) if (value == 0 and int(t * 4) % 2) else (50, 50, 70))
        d.rectangle((x, 11, x + 6, 23), fill=col)
    if day is not None:
        txt(img, 222, 17, f"DAY {day}", YELLOW)
    if live:
        if int(t * 3) % 2: d.rectangle((182, 13, 189, 20), fill=RED)
        txt(img, 194, 17, "LIVE", RED, anchor="l")
    if lvl is not None:
        txt(img, W - 10, 17, f"LVL {lvl}", WHITE, anchor="r")

def caption(img, d, lines, a=1.0):
    if a <= 0: return
    y0 = 350
    box(d, 12, y0 - 6, W - 12, H - 10, DARK, GREY, 2)
    for i, s in enumerate(lines):
        txt(img, W // 2, y0 + 10 + i * 18, s, WHITE)

def banner(img, d, t, title, sub, dur=1.4):
    if t > dur: return
    k = seg(t, 0, 0.2) * (1 - seg(t, dur - 0.2, dur))
    hgt = int(70 * k)
    if hgt < 4: return
    cy = 175
    box(d, 30, cy - hgt, W - 30, cy + hgt, DARK, YELLOW, 3)
    if k > 0.9:
        shadow_txt(img, W // 2, cy - 18, title, YELLOW, 2)
        txt(img, W // 2, cy + 22, sub, WHITE)

# ------------------------------------------------------------- scenes
def ease_io(t):
    t = clamp(t); return t * t * (3 - 2 * t)

T_PRESS, T_SLIDE0, T_SLIDE1 = 1.75, 1.9, 2.55

def s_title(img, d, t):
    background(img, d, t, t * 20)
    on = ease_io(seg(t, T_SLIDE0, T_SLIDE1))
    hud(img, d, t, 0, lvl=0)
    shadow_txt(img, W // 2, 92, "ANSWER", WHITE, 4)
    shadow_txt(img, W // 2, 137, "vs", ORANGE, 2)
    shadow_txt(img, W // 2, 182, "VALUE", YELLOW, 5)
    # the logo is the start switch
    k = seg(t, 0.3, 0.7)
    pop = 1 + 0.12 * math.sin(k * math.pi)
    LW, LCX, LCY = 330, W * UP // 2, 510
    logo(LCX, LCY, int(LW * k * pop), toggle_image(on))
    sc = LW / LOGO.width
    kx = LCX + (KX0 + (KX1 - KX0) * 0.55 + TRAVEL * on - LOGO.width / 2) * sc
    ky = LCY + (100 - LOGO.height / 2) * sc
    if t > 0.9:
        g = ease_io(seg(t, 0.9, 1.7))
        cx = 720 + (kx - 720) * g
        cy = 760 + (ky - 760) * g
        if t > T_SLIDE1 + 0.1:  # let go and drift off
            r = ease_io(seg(t, T_SLIDE1 + 0.1, T_SLIDE1 + 0.8))
            cx, cy = kx + 60 * r, ky + 90 * r
        pressed = T_PRESS < t < T_SLIDE1 + 0.1
        OVERLAYS.append(("cursor", int(cx), int(cy), 3 if not pressed else 2))
        if T_PRESS < t < T_PRESS + 0.35:  # click sparks
            ImageDraw.Draw(img)
            for j in range(6):
                a = j * math.pi / 3
                r1, r2 = 14, 14 + 20 * seg(t, T_PRESS, T_PRESS + 0.35)
                OVERLAYS.append(("spark", cx + math.cos(a) * r1, cy + math.sin(a) * r1,
                                 cx + math.cos(a) * r2, cy + math.sin(a) * r2))
    player(d, W // 2, GROUND_Y - abs(int(math.sin(t * (5 if on < 1 else 12)) * 6)), t,
           running=on >= 1)
    if on < 1:
        if int(t * 2.5) % 2 == 0:
            shadow_txt(img, W // 2, 362, "PUSH TO START", WHITE, 2)
    else:
        shadow_txt(img, W // 2, 362, "GAME START!", YELLOW, 2)
        if t < T_SLIDE1 + 0.17:  # flash
            d.rectangle((0, 0, W, H), fill=WHITE)

def s_level1(img, d, t):
    scroll = t * 60  # treadmill: world moves, player goes nowhere
    background(img, d, t, scroll)
    cyc = 1.5
    t0 = t - 1.4
    n = max(0, int(t0 // cyc)) if t0 > 0 else 0
    ct = (t0 % cyc) / cyc if t0 > 0 else 0
    day = 1 + n
    px_, ex = 150, 320
    # stack of unanswered questions on the left
    falls = n + (1 if ct > 0.75 else 0) if t0 > 0 else 0
    for i in range(falls):
        col, row = i % 3, i // 3
        bx, by = 14 + col * 20, GROUND_Y - 19 - row * 20
        if i == falls - 1 and t0 > 0 and ct > 0.75:
            by -= int((1 - seg(ct, 0.75, 0.9)) * 200)
        qblock(d, bx, by, img=img)
    player(d, px_, GROUND_Y, t, running=True)
    sprite(d, EXPERT, ex - 12, GROUND_Y - 33, 3)
    txt(img, ex, GROUND_Y - 44, "EXPERT", GREY)
    hud(img, d, t, 0, day=day, lvl=1)
    if t0 > 0:
        qs = ["HOW DO WE GET LEADS?", "WHAT SHOULD WE BUILD?", "WHICH CHANNEL FIRST?", "NOW WHAT??"]
        if ct < 0.55:
            q = qs[n % 4]
            w = len(q) * 8 + 14
            box(d, px_ - 20, 190, px_ - 20 + w, 214, WHITE, DARK, 2)
            d.polygon((px_ - 6, 214, px_ + 4, 214, px_ - 2, 224), fill=WHITE)
            txt(img, px_ - 20 + w // 2, 202, q, DARK)
        # opinion projectile flies from expert to player
        if 0.3 < ct < 0.62:
            k = seg(ct, 0.3, 0.62)
            x = ex - 20 - (ex - px_ - 30) * k
            y = 262 - math.sin(k * math.pi) * 40
            box(d, x - 34, y - 9, x + 34, y + 9, (200, 200, 210), DARK, 2)
            txt(img, x, y, "OPINION", DARK)
        if 0.62 < ct < 0.95:
            k = seg(ct, 0.62, 0.95)
            shadow_txt(img, px_, 230 - int(k * 25), "+0 VALUE", RED)
    caption(img, d, ["ASK. GET AN OPINION. REPEAT." if t < 4.5 else "NEXT DAY: ANOTHER QUESTION.",
                     "YOU'RE RUNNING. YOU'RE NOT MOVING."])
    banner(img, d, t, "LEVEL 1", "THE OPINION LOOP")

PLATS = [(115, 278, "UNDERSTAND"), (215, 236, "STRATEGY"), (315, 194, "BUILD")]
L2_JUMPS = [(1.6, 2.4), (2.9, 3.7), (4.2, 5.0)]

def l2_player_pos(t):
    x, y = 85, GROUND_Y
    for i, (a, b) in enumerate(L2_JUMPS):
        tx, ty = PLATS[i][0], PLATS[i][1]
        if t < a: return x, y, False
        if t < b:
            k = seg(t, a, b)
            return x + (tx - x) * k, y + (ty - y) * k - math.sin(k * math.pi) * 45, True
        x, y = tx, ty
    return x, y, False

def s_level2(img, d, t):
    background(img, d, t, 0)
    landed = sum(1 for (a, b) in L2_JUMPS if t >= b)
    value = [0, 3, 6, 10][landed]
    # worries stack shrinks: 6 blocks, 2 popped per landing
    left = max(0, 6 - landed * 2)
    for i in range(left):
        col, row = i % 3, i // 3
        qblock(d, 14 + col * 20, GROUND_Y - 19 - row * 20, img=img)
    for i, (px_, py, lab) in enumerate(PLATS):
        lit = landed > i
        d.rectangle((px_ - 40, py, px_ + 40, py + 10), fill=GREEN if lit else (90, 90, 120))
        d.rectangle((px_ - 40, py + 10, px_ + 40, py + 14), fill=(40, 100, 60) if lit else (60, 60, 90))
        txt(img, px_, py + 26, lab, YELLOW if lit else GREY)
        # coin burst on landing
        if lit:
            k = seg(t, L2_JUMPS[i][1], L2_JUMPS[i][1] + 0.6)
            if k < 1:
                for j in range(8):
                    a = j * math.pi / 4
                    cx = px_ + math.cos(a) * 40 * k; cy = py - 20 + math.sin(a) * 30 * k - 20 * k
                    d.rectangle((cx - 2, cy - 2, cx + 2, cy + 2), fill=YELLOW)
                shadow_txt(img, px_, py - 50 - int(k * 15), "+VALUE", GREEN)
    # flag on the final platform
    if landed == 3:
        fx, fy = 345, 194
        d.line((fx, fy, fx, fy - 40), fill=WHITE, width=2)
        k = seg(t, L2_JUMPS[2][1], L2_JUMPS[2][1] + 0.5)
        d.polygon((fx + 1, fy - 40, fx + 1 + 22 * k, fy - 33, fx + 1, fy - 26), fill=ORANGE)
    x, y, air = l2_player_pos(t)
    player(d, int(x), int(y), t, running=air or (t < 1.6 and t > 1.3), legs=LEGS[1] if air else None)
    hud(img, d, t, value, lvl=2)
    if landed == 3 and int(t * 4) % 2:
        shadow_txt(img, W // 2, 110, "VALUE CREATED!", GREEN, 2)
    lines = (["SOMEONE HELPS YOU UNDERSTAND", "HOW TO SOLVE IT."] if landed < 2 else
             ["NO MORE WORRYING WHAT'S NEXT", "OR WHAT TO BUILD STRATEGY ON."])
    caption(img, d, lines)
    banner(img, d, t, "LEVEL 2", "CREATE VALUE")

CREW = [(ORANGE, (60, 40, 30)), (BLUE, (230, 200, 90)), (PINK, (30, 30, 30)), (GREEN, (150, 80, 40))]
TOWER = ["ICP", "OUTBOUND", "MESSAGING", "PIPELINE", "CONTENT", "GTME"]

def s_level3(img, d, t):
    background(img, d, t, 0)
    rows = int(clamp((t - 1.5) / 3.2) * len(TOWER) + 0.0001)
    rows = min(rows, len(TOWER))
    cx = W // 2
    for i in range(len(TOWER)):
        if i >= rows and not (i == rows and t > 1.5):
            break
        w = 150 - i * 14
        y1 = GROUND_Y - i * 22
        drop = 0
        if i == rows:  # currently dropping
            k = ((t - 1.5) / 3.2 * len(TOWER)) % 1
            drop = int((1 - k) ** 2 * 120)
        col = YELLOW if i == len(TOWER) - 1 else [BLUE, ORANGE, PINK, GREEN, (160, 120, 255)][i % 5]
        d.rectangle((cx - w // 2, y1 - 20 - drop, cx + w // 2, y1 - drop), fill=DARK)
        d.rectangle((cx - w // 2 + 2, y1 - 18 - drop, cx + w // 2 - 2, y1 - 2 - drop), fill=col)
        txt(img, cx, y1 - 10 - drop, TOWER[i], DARK)
    # crew hammering around the tower
    spots = [55, 105, 295, 345]
    for i, (body, hair) in enumerate(CREW):
        enter = seg(t, 0.2 + i * 0.25, 1.2 + i * 0.25)
        sx = -20 + (spots[i] + 20) * enter if i < 2 else W + 20 - (W + 20 - spots[i]) * enter
        hop = abs(int(math.sin(t * 7 + i * 1.3) * 8)) if enter >= 1 else 0
        player(d, int(sx), GROUND_Y - hop, t + i * 0.2, running=enter < 1, body=body, hair=hair)
        txt(img, int(sx), GROUND_Y - 40 - hop, f"P{i + 1}", body)
    hud(img, d, t, 10, lvl=3, live=True)
    txt(img, 300, 17, "", WHITE)
    lines = (["NOT ONE EXPERT'S OPINION.", "NOT A STRATEGIST'S TAKE."] if t < 3.6 else
             ["SEE THE WORK BEING DONE.", "BUILD ALONGSIDE IT."])
    caption(img, d, lines)
    banner(img, d, t, "LEVEL 3", "GTME: BUILT IN PUBLIC")

def s_end(img, d, t):
    d.rectangle((0, 0, W, H), fill=DARK)
    for (sx, sy, ph) in STARS:
        if math.sin(t * 3 + ph) > 0: d.point((sx, sy), fill=STAR)
    a = t > 0.2
    if a: shadow_txt(img, W // 2, 70, "LEVEL COMPLETE!", YELLOW, 2 + (1 if int(t * 4) % 2 and t < 1.2 else 0))
    if t > 0.9:
        w = txt(img, W // 2, 150, "LESS TALKING ABOUT VALUE.", GREY)
        k = seg(t, 1.2, 1.7)
        d.rectangle((W // 2 - w // 2 - 4, 150, W // 2 - w // 2 - 4 + int((w + 8) * k), 151), fill=RED)
    if t > 1.9:
        shadow_txt(img, W // 2, 200, "MORE CREATING IT.", WHITE, 2)
    if t > 2.6:
        k = seg(t, 2.6, 3.0)
        pop = 1 + 0.12 * math.sin(k * math.pi)
        logo(W * UP // 2, 530, int(340 * k * pop))
        txt(img, W // 2, 322, "VALUE  10/10", GREEN)
    if t > 3.0 and int(t * 2.5) % 2 == 0:
        txt(img, W // 2, 362, "▶ PLAY AGAIN", WHITE)

SCENES = [(s_title, 3.6), (s_level1, 7.4), (s_level2, 6.8), (s_level3, 6.2), (s_end, 5.0)]

frames = []
for fn, dur in SCENES:
    for i in range(int(dur * FPS)):
        t = i / FPS
        img = Image.new("RGB", (W, H), SKY)
        OVERLAYS.clear()
        fn(img, ImageDraw.Draw(img), t)
        # quick wipe-in at scene start (pixel iris)
        if t < 0.25 and fn is not s_title:
            k = t / 0.25
            ImageDraw.Draw(img).rectangle((0, 0, W, int(H * (1 - k))), fill=DARK)
        big = img.resize((W * UP, H * UP), Image.NEAREST)
        for ov in OVERLAYS:
            if ov[0] == "img":
                _, src, cx, cy, w = ov
                h = round(src.height * w / src.width)
                lg = src.resize((w, h), Image.LANCZOS)
                big.paste(lg, (int(cx - w // 2), int(cy - h // 2)), lg)
            elif ov[0] == "spark":
                ImageDraw.Draw(big).line(ov[1:], fill=YELLOW, width=4)
            elif ov[0] == "cursor":
                draw_cursor(big, ov[1], ov[2], ov[3])
        frames.append(big)

pal = [f.convert("P", palette=Image.ADAPTIVE, colors=96, dither=Image.Dither.NONE) for f in frames]
durs = [round(1000 / FPS)] * len(pal)
pal[0].save("/home/user/AnimatedGif/sandbox_value_gif/answer-vs-value-game.gif", save_all=True,
            append_images=pal[1:], duration=durs, loop=0, optimize=True, disposal=1)
print(len(frames), "frames")

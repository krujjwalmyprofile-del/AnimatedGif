"""Premium monochrome game GIF: 'Answer vs Value' for the Sandbox GTME post.

Light, quiet, black-ink theme that matches the Sandbox GTME toggle logo.
The logo is the start switch: a cursor pushes it on, the track fills black, the game begins.
"""
import math, os
from PIL import Image, ImageDraw, ImageFont, ImageChops, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
S = 2                      # supersample
W = H = 800
FPS = 15

BG = (244, 244, 241)
INK = (14, 14, 14)
INK2 = (60, 60, 60)
MUTED = (138, 138, 133)
HAIR = (218, 218, 212)
CARD = (252, 252, 250)
SOFT = (232, 232, 227)

FD = "/usr/share/fonts/opentype/inter/"
_fc = {}
def font(name, px):
    k = (name, px)
    if k not in _fc: _fc[k] = ImageFont.truetype(FD + name + ".otf", px * S)
    return _fc[k]
DISPLAY = "InterDisplay-SemiBold"
DISPLAY_M = "InterDisplay-Medium"

# ------------------------------------------------------------------ helpers
def clamp(t): return max(0.0, min(1.0, t))
def seg(t, a, b): return clamp((t - a) / (b - a))
def ease(t): t = clamp(t); return 1 - (1 - t) ** 3
def eio(t): t = clamp(t); return t * t * t * (t * (6 * t - 15) + 10)
def lerp(a, b, t): return a + (b - a) * t
def mix(c1, c2, t): return tuple(int(lerp(a, b, t)) for a, b in zip(c1, c2))
def fade(c, a): return mix(BG, c, clamp(a))
def P(*v): return [x * S for x in v]

def text(d, xy, s, f, col, anchor="lm"):
    d.text((xy[0] * S, xy[1] * S), s, font=f, fill=col, anchor=anchor)

def spaced(d, xy, s, f, col, track=2.0, anchor="l"):
    """Letter-spaced small caps label."""
    widths = [f.getlength(ch) + track * S for ch in s]
    total = sum(widths) - track * S
    x = xy[0] * S - {"l": 0, "m": total / 2, "r": total}[anchor]
    for ch, w in zip(s, widths):
        d.text((x, xy[1] * S), ch, font=f, fill=col, anchor="lm"); x += w
    return total / S

def rrect(d, box, r, fill=None, outline=None, width=1):
    d.rounded_rectangle(P(*box), radius=r * S, fill=fill, outline=outline,
                        width=int(width * S) if outline else 0)

def dot(d, c, r, fill=None, outline=None, width=1):
    d.ellipse(P(c[0] - r, c[1] - r, c[0] + r, c[1] + r), fill=fill, outline=outline,
              width=int(width * S) if outline else 0)

def hud(d, t, level, name, value, a=1.0, extra=None):
    spaced(d, (48, 46), f"LEVEL {level:02d}", font("Inter-SemiBold", 11), fade(INK, a), 2.4)
    spaced(d, (128, 46), name.upper(), font("Inter-Medium", 11), fade(MUTED, a), 2.4)
    spaced(d, (W - 48 - 130 - 16, 46), "VALUE", font("Inter-SemiBold", 11), fade(MUTED, a), 2.4, "r")
    x0 = W - 48 - 130
    rrect(d, (x0, 44, x0 + 130, 48), 2, fill=fade(HAIR, a))
    if value > 0.005:
        rrect(d, (x0, 44, x0 + 130 * value, 48), 2, fill=fade(INK, a))
    d.line(P(48, 72, W - 48, 72), fill=fade(HAIR, a), width=S)
    # footer
    d.line(P(48, H - 64, W - 48, H - 64), fill=fade(HAIR, a), width=S)
    spaced(d, (48, H - 40), "SANDBOX GTME", font("Inter-SemiBold", 11), fade(INK, a), 2.4)
    spaced(d, (W - 48, H - 40), f"{level:02d} / 03", font("Inter-Medium", 11), fade(MUTED, a), 2.4, "r")
    if extra: extra(a)

def heading(d, t, title, sub, a):
    k = ease(seg(t, 0.15, 0.75))
    text(d, (48, 128 + 10 * (1 - k)), title, font(DISPLAY, 44), fade(INK, a * k))
    k2 = ease(seg(t, 0.35, 0.95))
    text(d, (48, 174 + 8 * (1 - k2)), sub, font("Inter-Regular", 18), fade(MUTED, a * k2))

# ------------------------------------------------------------------ logo / toggle
LOGO = Image.open(os.path.join(HERE, "sandbox-logo.png")).convert("RGBA")
KX0, KY0, KX1, KY1 = 20, 17, 500, 196
TRAVEL = LOGO.width - 23 - 498

def _pill(size, box, r, ss=4):
    m = Image.new("L", (size[0] * ss, size[1] * ss), 0)
    ImageDraw.Draw(m).rounded_rectangle([v * ss for v in box], radius=r * ss, fill=255)
    return m.resize(size, Image.LANCZOS)

KNOB = LOGO.crop((KX0, KY0, KX1, KY1))
KNOB.putalpha(ImageChops.multiply(KNOB.getchannel("A"),
              _pill(KNOB.size, (3, 2, KNOB.width - 3, KNOB.height - 1), 82)))
TRACK = LOGO.copy()
_col = LOGO.crop((520, 0, 521, LOGO.height)).resize((KX1 + 6 - 10, LOGO.height))
TRACK.paste(_col, (10, 0), _col)
TRACK.paste(LOGO.crop((0, 0, 24, LOGO.height)), (0, 0))
TRACK.putalpha(LOGO.getchannel("A"))
# black track keeps a hint of the original's shading so it still reads as a physical object
_blk = ImageChops.multiply(TRACK.convert("RGB"), Image.new("RGB", TRACK.size, (34, 34, 34)))
TRACK_ON = _blk.convert("RGBA"); TRACK_ON.putalpha(LOGO.getchannel("A"))
_sh = Image.new("RGBA", KNOB.size, (0, 0, 0, 0))
ImageDraw.Draw(_sh).rounded_rectangle((8, 16, KNOB.width - 8, KNOB.height + 2), radius=80, fill=(0, 0, 0, 90))
KNOB_SHADOW = _sh.filter(ImageFilter.GaussianBlur(9))

def toggle_image(k):
    if k <= 0: return LOGO
    off = int(TRAVEL * k)
    im = TRACK.copy()
    fill = Image.new("L", im.size, 0)
    # fill trails the knob and reaches the very end of the pill once fully on (no grey sliver)
    right = KX0 + off + KNOB.width - 24 + int(60 * k)
    ImageDraw.Draw(fill).rectangle((0, 0, right, im.height), fill=255)
    im.paste(TRACK_ON, (0, 0), ImageChops.multiply(fill, LOGO.getchannel("A")))
    im.alpha_composite(KNOB_SHADOW, (KX0 + off, KY0))
    im.alpha_composite(KNOB, (KX0 + off, KY0))
    return im

def cursor_sprite(scale):
    pts = [(0, 0), (0, 18), (4.6, 13.8), (7.6, 20.6), (10.6, 19.4), (7.7, 12.8), (13.6, 12.8)]
    ss = 4; pad = 4
    im = Image.new("RGBA", (int(18 * scale * ss), int(26 * scale * ss)), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    poly = [((x + pad / 2) * scale * ss, (y + pad / 2) * scale * ss) for x, y in pts]
    d.polygon(poly, fill=(255, 255, 255, 255), outline=(255, 255, 255, 255))
    d.line(poly + [poly[0]], fill=(255, 255, 255, 255), width=int(3.2 * scale * ss), joint="curve")
    inner = [((x * 0.86 + 0.9 + pad / 2) * scale * ss, (y * 0.86 + 1.6 + pad / 2) * scale * ss) for x, y in pts]
    d.polygon(inner, fill=INK + (255,))
    im = im.resize((im.width // ss, im.height // ss), Image.LANCZOS)
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    sh.paste((0, 0, 0, 60), (0, 0), im.getchannel("A"))
    out = Image.new("RGBA", (im.width + 6, im.height + 6), (0, 0, 0, 0))
    out.alpha_composite(sh.filter(ImageFilter.GaussianBlur(2)), (2, 3))
    out.alpha_composite(im, (0, 0))
    return out
CURSOR = {1.0: cursor_sprite(1.5), 0.9: cursor_sprite(1.35)}

OVER = []   # overlays composited at 1x after downsampling
def logo_at(cx, cy, w, k=0.0, a=1.0):
    OVER.append(("logo", cx, cy, w, k, a))

# ------------------------------------------------------------------ scenes
T_PRESS, T_S0, T_S1 = 2.15, 2.3, 3.0

def s_title(d, t):
    a = 1.0
    k = ease(seg(t, 0.1, 0.8))
    spaced(d, (W / 2, 196 + 8 * (1 - k)), "A GAME IN THREE LEVELS", font("Inter-SemiBold", 12), fade(MUTED, k), 3, "m")
    k = ease(seg(t, 0.25, 0.95))
    text(d, (W / 2, 262 + 12 * (1 - k)), "Answer vs. Value", font(DISPLAY, 66), fade(INK, k), "mm")
    on = eio(seg(t, T_S0, T_S1))
    la = ease(seg(t, 0.6, 1.1))
    LW, LCX, LCY = 360, W / 2, 432 + 8 * (1 - la)
    logo_at(LCX, LCY, LW * (0.97 + 0.03 * la), on, la)
    # caption
    ca = ease(seg(t, 1.0, 1.4)) * (1 - ease(seg(t, T_S0, T_S0 + 0.25)))
    spaced(d, (W / 2, 560), "PUSH TO START", font("Inter-SemiBold", 12), fade(INK, ca * (0.55 + 0.45 * math.sin(t * 4) ** 2)), 3, "m")
    cb = ease(seg(t, T_S1 - 0.05, T_S1 + 0.4))
    spaced(d, (W / 2, 560), "LEVEL 01 UNLOCKED", font("Inter-SemiBold", 12), fade(INK, cb), 3, "m")
    # cursor
    sc = LW / LOGO.width
    kx = LCX + (KX0 + (KX1 - KX0) * 0.62 + TRAVEL * on - LOGO.width / 2) * sc
    ky = LCY + (112 - LOGO.height / 2) * sc
    if t > 1.2:
        g = eio(seg(t, 1.2, 2.05))
        cx, cy = lerp(640, kx, g), lerp(700, ky, g)
        if t > T_S1 + 0.15:
            r = eio(seg(t, T_S1 + 0.15, T_S1 + 0.9))
            cx, cy = kx + 70 * r, ky + 120 * r
        pressed = T_PRESS < t < T_S1 + 0.15
        ca2 = 1 - seg(t, T_S1 + 0.6, T_S1 + 0.9)
        OVER.append(("cursor", cx, cy, 0.9 if pressed else 1.0, ca2))
    # subtle progress hairline under the switch while sliding
    hud_a = 0
    return hud_a

def l1_extra(d, t):
    pass

QUESTIONS = ["How do we get leads?", "What should we build?", "Which channel first?", "What do we do now?"]

def s_level1(d, t):
    heading(d, t, "The opinion loop", "Ask. Get an opinion. Repeat.", 1)
    lap = 1.45
    t0 = t - 0.9
    laps = int(t0 // lap) if t0 > 0 else 0
    ph = (t0 % lap) / lap if t0 > 0 else 0
    day = min(laps + 1, 4)
    hud(d, t, 1, "The opinion loop", 0.0)
    spaced(d, (W - 48, 104), f"DAY {day:02d}", font("Inter-SemiBold", 11), INK, 2.4, "r")
    # loop around the expert
    C, R = (232, 452), 128
    la = ease(seg(t, 0.3, 0.9))
    d.ellipse(P(C[0] - R, C[1] - R, C[0] + R, C[1] + R), outline=fade(HAIR, la), width=2 * S)
    dot(d, C, 30, fill=fade(SOFT, la))
    text(d, (C[0], C[1]), "Expert", font("Inter-Medium", 14), fade(INK2, la), "mm")
    if t0 > 0:
        ang = -math.pi / 2 + ph * 2 * math.pi
        # trail
        for j in range(14):
            aj = ang - j * 0.07
            dot(d, (C[0] + R * math.cos(aj), C[1] + R * math.sin(aj)), 9 - j * 0.45,
                fill=mix(BG, INK, 0.5 * (1 - j / 14)))
        p = (C[0] + R * math.cos(ang), C[1] + R * math.sin(ang))
        dot(d, p, 10, fill=INK)
        # ask at the top of each lap, opinion comes back
        ask = seg(ph, 0.0, 0.08) * (1 - seg(ph, 0.14, 0.2))
        if ask > 0:
            top = (C[0], C[1] - R)
            d.line(P(top[0], top[1] + 12, C[0], C[1] - 32), fill=fade(INK, ask * 0.5), width=S)
        op = ease(seg(ph, 0.18, 0.32)) * (1 - ease(seg(ph, 0.78, 0.92)))
        if op > 0:
            bx, by = C[0] - 92, C[1] - 66
            rrect(d, (bx, by - 17, bx + 184, by + 17), 17, fill=fade(INK, op))
            text(d, (bx + 92, by), "Here’s what I think.", font("Inter-Medium", 14), fade(BG, op) if op > 0.5 else fade(INK, op), "mm")
            text(d, (C[0], C[1] + R + 34), "+0 value", font("Inter-Medium", 14), fade(MUTED, op), "mm")
    # open questions stack
    qa = ease(seg(t, 0.6, 1.1))
    spaced(d, (452, 300), "OPEN QUESTIONS", font("Inter-SemiBold", 11), fade(MUTED, qa), 2.4)
    n = min(laps + (1 if ph > 0.05 and t0 > 0 else 0), 4)
    text(d, (W - 48, 300), f"{n}", font("Inter-SemiBold", 14), fade(INK, qa), "rm")
    for i in range(n):
        k = ease(seg(t0 - i * lap, 0.05 * lap, 0.3 * lap)) if i == n - 1 else 1
        y = 330 + i * 52 - 14 * (1 - k)
        rrect(d, (452, y, W - 48, y + 42), 10, fill=fade(CARD, k), outline=fade(HAIR, k), width=1)
        dot(d, (474, y + 21), 4, outline=fade(INK, k), width=1.5)
        text(d, (490, y + 21), QUESTIONS[i], font("Inter-Medium", 15), fade(INK, k))
    ca = ease(seg(t, 3.2, 3.8))
    text(d, (48, 664), "You keep moving. You never get anywhere.", font("Inter-Medium", 18), fade(INK, ca))

STEPS = [(150, 560, "Understand"), (360, 478, "Strategy"), (570, 396, "Build")]
JUMPS = [(1.4, 2.15), (2.55, 3.3), (3.7, 4.45)]

def s_level2(d, t):
    landed = sum(1 for (_, b) in JUMPS if t >= b)
    # value fills smoothly with each landing
    v = 0
    for i, (_, b) in enumerate(JUMPS):
        v += eio(seg(t, b, b + 0.5)) / 3
    hud(d, t, 2, "Create value", v)
    heading(d, t, "Creating value", "Someone helps you understand how to solve it.", 1)
    q = 4 - min(4, int(sum(eio(seg(t, b, b + 0.3)) for (_, b) in JUMPS) * 4 / 3 + 0.0001))
    spaced(d, (W - 48, 104), f"OPEN QUESTIONS  {q}", font("Inter-SemiBold", 11), INK if q else MUTED, 2.4, "r")
    base_y = 640
    sa = ease(seg(t, 0.4, 1.0))
    d.line(P(48, base_y, 150 - 60, base_y), fill=fade(HAIR, sa), width=2 * S)
    for i, (x, y, lab) in enumerate(STEPS):
        a = ease(seg(t, 0.5 + i * 0.15, 1.0 + i * 0.15))
        lit = eio(seg(t, JUMPS[i][1], JUMPS[i][1] + 0.35))
        rrect(d, (x - 80, y, x + 80, y + 12), 6, fill=fade(mix(SOFT, INK, lit), a))
        spaced(d, (x - 80, y + 36), f"0{i + 1}", font("Inter-SemiBold", 11), fade(MUTED, a), 2.4)
        text(d, (x - 80, y + 60), lab, font("Inter-SemiBold", 18), fade(mix(MUTED, INK, lit), a))
        # quiet ring pulse on landing
        rp = seg(t, JUMPS[i][1], JUMPS[i][1] + 0.6)
        if 0 < rp < 1:
            r = 12 + 30 * ease(rp)
            d.ellipse(P(x - r, y - 12 - r, x + r, y - 12 + r), outline=fade(INK, 1 - rp), width=int(1.5 * S))
    # the dot
    x, y = 70, base_y - 11
    for i, (a_, b_) in enumerate(JUMPS):
        tx, ty = STEPS[i][0], STEPS[i][1] - 11
        if t < a_: break
        if t < b_:
            k = eio(seg(t, a_, b_))
            x, y = lerp(x, tx, k), lerp(y, ty, k) - math.sin(k * math.pi) * 70
            break
        x, y = tx, ty
    sq = 1.0
    for (_, b_) in JUMPS:  # tiny squash on landing
        s_ = seg(t, b_, b_ + 0.18)
        if 0 < s_ < 1: sq = 1 - 0.25 * math.sin(s_ * math.pi)
    d.ellipse(P(x - 11 / sq ** 0.5, y + 11 - 22 * sq, x + 11 / sq ** 0.5, y + 11), fill=INK)
    fa = ease(seg(t, JUMPS[2][1] + 0.3, JUMPS[2][1] + 0.9))
    text(d, (48, 300), "Value created.", font(DISPLAY, 28), fade(INK, fa))
    text(d, (48, 334), "No more worrying about what comes next.", font("Inter-Regular", 17), fade(MUTED, fa))

CARDS = ["ICP research", "Outbound system", "Messaging tests", "Pipeline build", "Content engine", "Weekly teardown"]

def s_level3(d, t):
    hud(d, t, 3, "Built in public", 1.0)
    heading(d, t, "Built in public", "Not one expert’s opinion. You see the work being done.", 1)
    la = ease(seg(t, 0.4, 0.9))
    pulse = 0.5 + 0.5 * math.sin(t * 5)
    rrect(d, (W - 48 - 78, 92, W - 48, 116), 12, outline=fade(INK, la), width=1)
    dot(d, (W - 48 - 60, 104), 4, fill=fade(mix(MUTED, INK, pulse), la))
    spaced(d, (W - 48 - 48, 104), "LIVE", font("Inter-SemiBold", 11), fade(INK, la), 2.4)
    for i, name in enumerate(CARDS):
        c, r = i % 3, i // 3
        x0, y0 = 48 + c * 240, 250 + r * 190
        k = ease(seg(t, 0.5 + i * 0.18, 1.0 + i * 0.18))
        if k <= 0: continue
        oy = 12 * (1 - k)
        rrect(d, (x0, y0 + oy, x0 + 224, y0 + 170 + oy), 14, fill=fade(CARD, k), outline=fade(HAIR, k), width=1)
        spaced(d, (x0 + 18, y0 + 28 + oy), f"0{i + 1}", font("Inter-SemiBold", 11), fade(MUTED, k), 2.4)
        text(d, (x0 + 18, y0 + 62 + oy), name, font("Inter-SemiBold", 18), fade(INK, k))
        # avatars: people building alongside
        n = 2 + (i * 5) % 3
        for j in range(n):
            ja = ease(seg(t, 1.2 + i * 0.18 + j * 0.15, 1.5 + i * 0.18 + j * 0.15))
            if ja <= 0: continue
            cx = x0 + 28 + j * 18
            tone = [INK, (90, 90, 90), (150, 150, 146), (200, 200, 195)][j % 4]
            dot(d, (cx, y0 + 104 + oy), 11, fill=fade(CARD, k * ja))
            dot(d, (cx, y0 + 104 + oy), 9, fill=fade(tone, k * ja))
        prog = (0.45 + 0.5 * ((i * 37) % 10) / 10) * eio(seg(t, 1.0 + i * 0.18, 3.4 + i * 0.18))
        rrect(d, (x0 + 18, y0 + 140 + oy, x0 + 206, y0 + 144 + oy), 2, fill=fade(SOFT, k))
        if prog > 0.01:
            rrect(d, (x0 + 18, y0 + 140 + oy, x0 + 18 + 188 * prog, y0 + 144 + oy), 2, fill=fade(INK, k))
    ca = ease(seg(t, 3.0, 3.6))
    text(d, (48, 664), "See the work. Build alongside it.", font("Inter-Medium", 18), fade(INK, ca))

def s_end(d, t):
    k = ease(seg(t, 0.1, 0.7))
    spaced(d, (W / 2, 210), "LEVEL COMPLETE", font("Inter-SemiBold", 12), fade(MUTED, k), 3, "m")
    f1 = font(DISPLAY_M, 38)
    s1 = "Less talking about value."
    text(d, (W / 2, 280), s1, f1, fade(MUTED, k), "mm")
    tw = f1.getlength(s1) / S
    st = eio(seg(t, 0.8, 1.4))
    if st > 0:
        d.line(P(W / 2 - tw / 2 - 4, 283, W / 2 - tw / 2 - 4 + (tw + 8) * st, 283), fill=INK, width=int(2.5 * S))
    k2 = ease(seg(t, 1.5, 2.2))
    text(d, (W / 2, 348 + 10 * (1 - k2)), "More creating it.", font(DISPLAY, 62), fade(INK, k2), "mm")
    la = ease(seg(t, 2.3, 2.9))
    logo_at(W / 2, 480 + 8 * (1 - la), 300, 1.0, la)   # the switch stays on
    pa = ease(seg(t, 3.0, 3.5))
    spaced(d, (W / 2, 590), "PLAY AGAIN", font("Inter-SemiBold", 12), fade(MUTED, pa), 3, "m")

SCENES = [(s_title, 4.0), (s_level1, 7.0), (s_level2, 6.2), (s_level3, 5.6), (s_end, 5.2)]
XF = 0.35

def render():
    frames = []
    for fn, dur in SCENES:
        n = int(dur * FPS)
        for i in range(n):
            t = i / FPS
            OVER.clear()
            im = Image.new("RGB", (W * S, H * S), BG)
            fn(ImageDraw.Draw(im), t)
            im = im.resize((W, H), Image.LANCZOS).convert("RGBA")
            for ov in OVER:
                if ov[0] == "logo":
                    _, cx, cy, w, k, a = ov
                    src = toggle_image(k)
                    w = int(w); h = round(src.height * w / src.width)
                    lg = src.resize((w, h), Image.LANCZOS)
                    if a < 1:
                        lg.putalpha(lg.getchannel("A").point(lambda v: int(v * a)))
                    im.alpha_composite(lg, (int(cx - w / 2), int(cy - h / 2)))
                elif ov[0] == "cursor":
                    _, cx, cy, sc, a = ov
                    cs = CURSOR[sc]
                    if a < 1:
                        cs = cs.copy(); cs.putalpha(cs.getchannel("A").point(lambda v: int(v * a)))
                    im.alpha_composite(cs, (int(cx - 3), int(cy - 3)))
            im = im.convert("RGB")
            # crossfades between scenes
            fin, fout = clamp(t / XF), clamp((dur - t) / XF)
            a = min(fin if fn is not s_title else 1, fout if fn is not s_end else 1)
            if a < 1:
                im = Image.blend(Image.new("RGB", im.size, BG), im, a)
            frames.append(im)
    return frames

if __name__ == "__main__":
    frames = render()
    pal = [f.quantize(colors=48, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE) for f in frames]
    durs = [round(1000 / FPS)] * len(pal)
    durs[-1] = 1500
    out = os.path.join(HERE, "answer-vs-value-premium.gif")
    pal[0].save(out, save_all=True, append_images=pal[1:], duration=durs, loop=0, optimize=True, disposal=1)
    print(len(frames), "frames ->", out)

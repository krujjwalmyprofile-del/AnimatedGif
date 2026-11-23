"""Premium monochrome chess GIF: 'Answer vs Value' for the Sandbox GTME post.

01  The opinion loop  - the expert hands you one move at a time; knights shuffle; draw by repetition.
02  Creating value    - see the whole board, form a plan, play it through to checkmate.
03  Built in public   - a live board: every move visible, people building alongside.
Reuses the theme, HUD, toggle logo and cursor from make_premium_gif.py.
"""
import math, os
from PIL import Image, ImageDraw, ImageFont
import make_premium_gif as pm
from make_premium_gif import (S, W, H, BG, INK, INK2, MUTED, HAIR, CARD, SOFT, font, DISPLAY, DISPLAY_M,
                              clamp, seg, ease, eio, lerp, mix, fade, P, text, spaced, rrect, dot,
                              hud, heading, logo_at, toggle_image, CURSOR, LOGO, KX0, KX1, TRAVEL, OVER)

FPS = 12
LIGHT_SQ = (238, 238, 233)
DARK_SQ = (210, 210, 203)
GLYPH = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 38 * S)
SOLID = {"k": "♚", "q": "♛", "r": "♜", "b": "♝", "n": "♞", "p": "♟"}
OUTLINE = {"k": "♔", "q": "♕", "r": "♖", "b": "♗", "n": "♘", "p": "♙"}

BX, BY, SQ = 48, 222, 44          # board origin + square size (8 * 44 = 352)

def fen(f):
    pos = {}
    for r, row in enumerate(f.split("/")):
        c = 0
        for ch in row:
            if ch.isdigit(): c += int(ch)
            else:
                pos["abcdefgh"[c] + str(8 - r)] = ch; c += 1
    return pos

START = fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR")
SCHOLAR = fen("r1bqkb1r/pppp1ppp/2n2n2/4p2Q/2B1P3/8/PPPP1PPP/RNB1K1NR")

def sq_xy(sq):
    c = "abcdefgh".index(sq[0]); r = int(sq[1])
    return BX + c * SQ + SQ / 2, BY + (8 - r) * SQ + SQ / 2

def piece(d, ch, x, y, a=1.0):
    k = ch.lower()
    xy = (x * S, (y + 1) * S)
    if ch.isupper():
        d.text(xy, SOLID[k], font=GLYPH, fill=fade(CARD, a), anchor="mm")
        d.text(xy, OUTLINE[k], font=GLYPH, fill=fade(INK, a), anchor="mm")
    else:
        d.text(xy, SOLID[k], font=GLYPH, fill=fade(INK, a), anchor="mm")

def board(d, pos, a=1.0, moving=(), tint=None, hide=()):
    """moving: list of (piece, from_sq, to_sq, k). tint: {sq: strength 0..1}."""
    for r in range(8):
        for c in range(8):
            sq = "abcdefgh"[c] + str(8 - r)
            base = LIGHT_SQ if (r + c) % 2 == 0 else DARK_SQ
            if tint and sq in tint: base = mix(base, INK, 0.16 * tint[sq])
            d.rectangle(P(BX + c * SQ, BY + r * SQ, BX + (c + 1) * SQ, BY + (r + 1) * SQ), fill=fade(base, a))
    d.rectangle(P(BX, BY, BX + 8 * SQ, BY + 8 * SQ), outline=fade(HAIR, a), width=S)
    f = font("Inter-Medium", 10)
    for i in range(8):
        text(d, (BX + i * SQ + SQ / 2, BY + 8 * SQ + 12), "abcdefgh"[i], f, fade(MUTED, a), "mm")
        text(d, (BX - 10, BY + i * SQ + SQ / 2), str(8 - i), f, fade(MUTED, a), "mm")
    busy = {m[1] for m in moving} | set(hide)
    for sq, ch in pos.items():
        if sq in busy: continue
        piece(d, ch, *sq_xy(sq), a)
    for ch, fr, to, k in moving:
        (x0, y0), (x1, y1) = sq_xy(fr), sq_xy(to)
        piece(d, ch, lerp(x0, x1, k), lerp(y0, y1, k) - 6 * math.sin(k * math.pi), a)

def arrow(d, fr, to, k, a=1.0, col=INK2):
    if k <= 0 or a <= 0: return
    (x0, y0), (x1, y1) = sq_xy(fr), sq_xy(to)
    ang = math.atan2(y1 - y0, x1 - x0)
    L = math.hypot(x1 - x0, y1 - y0) - 10
    xe, ye = x0 + math.cos(ang) * L * k, y0 + math.sin(ang) * L * k
    c = fade(col, a * 0.85)
    d.line(P(x0, y0, xe - math.cos(ang) * 8, ye - math.sin(ang) * 8), fill=c, width=int(5 * S))
    hl, hw = 16, 11
    bx, by = xe - math.cos(ang) * hl, ye - math.sin(ang) * hl
    d.polygon(P(xe, ye, bx + math.sin(ang) * hw, by - math.cos(ang) * hw,
                bx - math.sin(ang) * hw, by + math.cos(ang) * hw), fill=c)

def chip(d, cx, cy, s, a, f=None, pad=18):
    f = f or font("Inter-SemiBold", 15)
    w = f.getlength(s) / S + pad * 2
    rrect(d, (cx - w / 2, cy - 18, cx + w / 2, cy + 18), 18, fill=fade(INK, a))
    text(d, (cx, cy), s, f, fade(BG, a) if a > 0.5 else fade(INK, a), "mm")

PX = 440                           # right panel x

# ---------------------------------------------------------------- title
T_PRESS, T_S0, T_S1 = 1.1, 1.25, 1.9

def s_title(d, t):
    """Frame 0 is the fully composed title: cursor already resting on the switch."""
    spaced(d, (W / 2, 196), "A GAME OF CHESS", font("Inter-SemiBold", 12), MUTED, 3, "m")
    text(d, (W / 2, 262), "Answer vs. Value", font(DISPLAY, 66), INK, "mm")
    piece(d, "K", W / 2 - 318, 266); piece(d, "k", W / 2 + 318, 266)
    on = eio(seg(t, T_S0, T_S1))
    LW, LCX, LCY = 360, W / 2, 432
    logo_at(LCX, LCY, LW, on, 1.0)
    # solid labels (a pulsing grey breaks up under GIF quantisation)
    ca = 1 - ease(seg(t, T_S0, T_S0 + 0.2))
    if ca > 0.02:
        spaced(d, (W / 2, 560), "PUSH TO START", font("Inter-SemiBold", 12), fade(INK, ca), 3, "m")
    cb = ease(seg(t, T_S1 - 0.1, T_S1 + 0.25))
    if cb > 0.02:
        spaced(d, (W / 2, 560), "WHITE TO MOVE", font("Inter-SemiBold", 12), fade(INK, cb), 3, "m")
    sc = LW / LOGO.width
    kx = LCX + (KX0 + (KX1 - KX0) * 0.62 + TRAVEL * on - LOGO.width / 2) * sc
    ky = LCY + (112 - LOGO.height / 2) * sc
    cx, cy = kx, ky
    if t > T_S1 + 0.15:
        r = eio(seg(t, T_S1 + 0.15, T_S1 + 0.9))
        cx, cy = kx + 70 * r, ky + 120 * r
    pressed = T_PRESS < t < T_S1 + 0.15
    OVER.append(("cursor", cx, cy, 0.9 if pressed else 1.0, 1 - seg(t, T_S1 + 0.6, T_S1 + 0.9)))

# ---------------------------------------------------------------- level 1: draw by repetition
Q1 = [("How do we get leads?", "Nf3"), ("What should we build?", "Ng1"),
      ("Which channel first?", "Nf3"), ("What do we do now?", "Ng1")]
L1_LAP = 1.35
L1_T0 = 0.9

def s_level1(d, t):
    hud(d, t, 1, "The opinion loop", 0.0)
    heading(d, t, "The opinion loop", "Ask the expert. Get one move. Repeat.", 1)
    t0 = t - L1_T0
    laps = max(0, int(t0 // L1_LAP)) if t0 > 0 else 0
    laps = min(laps, 4)
    ph = (t0 - laps * L1_LAP) / L1_LAP if t0 > 0 and laps < 4 else 1.0
    spaced(d, (W - 48, 104), f"DAY {min(laps + 1, 4):02d}", font("Inter-SemiBold", 11), INK, 2.4, "r")
    # knights: white Nf3/Ng1, black Nf6/Ng8 - forever
    pos = dict(START)
    wn_out = laps % 2 == 1          # after an odd number of full laps the knights are out
    if wn_out:
        pos.pop("g1"); pos.pop("g8"); pos["f3"] = "N"; pos["f6"] = "n"
    moving = []
    if t0 > 0 and laps < 4:
        kw = eio(seg(ph, 0.35, 0.55)); kb = eio(seg(ph, 0.62, 0.82))
        wf, wt = ("f3", "g1") if wn_out else ("g1", "f3")
        bf, bt = ("f6", "g8") if wn_out else ("g8", "f6")
        if kw > 0:
            moving.append(("N", wf, wt, kw))
        if kb > 0:
            moving.append(("n", bf, bt, kb))
    tint = {}
    if moving:
        for (_, fr, to, k) in moving: tint[fr] = tint[to] = 1.0
    board(d, pos, ease(seg(t, 0.2, 0.7)), moving, tint)
    # right panel: what you asked, what you got
    qa = ease(seg(t, 0.6, 1.1))
    spaced(d, (PX, 236), "ASKED THE EXPERT", font("Inter-SemiBold", 11), fade(MUTED, qa), 2.4)
    n = min(laps + (1 if t0 > 0 and laps < 4 else 0), 4)
    for i in range(n):
        k = ease(seg(t0 - i * L1_LAP, 0.0, 0.25 * L1_LAP))
        y = 258 + i * 66 - 12 * (1 - k)
        rrect(d, (PX, y, W - 48, y + 56), 10, fill=fade(CARD, k), outline=fade(HAIR, k), width=1)
        text(d, (PX + 16, y + 19), Q1[i][0], font("Inter-Medium", 15), fade(INK, k))
        ans = ease(seg(t0 - i * L1_LAP, 0.2 * L1_LAP, 0.35 * L1_LAP))
        text(d, (PX + 16, y + 39), f"Expert: “{Q1[i][1]}.”", font("Inter-Regular", 13), fade(MUTED, k * ans))
    # verdict
    va = ease(seg(t, L1_T0 + 4 * L1_LAP + 0.1, L1_T0 + 4 * L1_LAP + 0.6))
    if va > 0:
        chip(d, BX + 4 * SQ, BY + 4 * SQ, "½–½  Draw by repetition", va)
    ca = ease(seg(t, 3.4, 4.0))
    text(d, (48, 664), "You keep moving. You never get anywhere.", font("Inter-Medium", 18), fade(INK, ca))

# ---------------------------------------------------------------- level 2: see the board, play the plan
STEPS = [("Understand", "See the whole board.", 0.9, 2.3),
         ("Strategy", "Know why each move matters.", 2.3, 3.6),
         ("Build", "Play it through.", 3.6, 4.8)]

def s_level2(d, t):
    v = sum(eio(seg(t, b - 0.3, b + 0.2)) for (_, _, _, b) in STEPS) / 3
    hud(d, t, 2, "Create value", v)
    heading(d, t, "Creating value", "Someone helps you understand how to solve it.", 1)
    tint = {}
    # Understand: the weak point lights up
    u = eio(seg(t, 1.0, 1.6))
    if u > 0:
        pulse = 0.75 + 0.25 * math.sin(t * 6)
        tint["f7"] = 2.2 * u * pulse
        for s_ in ("e8", "g8", "e7", "g7"): tint[s_] = 0.6 * u
    pos = dict(SCHOLAR)
    moving = []
    mk = eio(seg(t, 3.8, 4.4))
    hide = []
    if mk > 0:
        moving.append(("Q", "h5", "f7", mk))
        if mk > 0.6: hide.append("f7")
    if t > 4.4:
        pos.pop("h5"); pos["f7"] = "Q"; moving = []; hide = []
        tint = {"e8": 3.0 * eio(seg(t, 4.4, 4.8)), "f7": 1.0, "h5": 1.0}
    board(d, pos, 1, moving, tint, hide)
    # Strategy: the plan, drawn on the board
    s1 = eio(seg(t, 2.4, 2.9)); s2 = eio(seg(t, 2.7, 3.2))
    fa = 1.0 if t < 4.3 else 0.0
    arrow(d, "c4", "f7", s1, fa); arrow(d, "h5", "f7", s2, fa)
    if t > 4.4:
        chip(d, BX + 4 * SQ, BY + 5.5 * SQ, "Qxf7#  Checkmate", ease(seg(t, 4.5, 4.9)))
    # right panel: the three steps
    for i, (name, sub, a_, b_) in enumerate(STEPS):
        y = 250 + i * 92
        ap = ease(seg(t, 0.4 + i * 0.12, 0.9 + i * 0.12))
        lit = eio(seg(t, a_, a_ + 0.4))
        done = eio(seg(t, b_ - 0.2, b_ + 0.2))
        dot(d, (PX + 12, y + 12), 12, fill=fade(mix(CARD, INK, done), ap), outline=fade(mix(HAIR, INK, lit), ap), width=1.5)
        if done > 0.6:
            d.line(P(PX + 6, y + 12, PX + 10.5, y + 16.5, PX + 18, y + 8), fill=CARD, width=int(2 * S), joint="curve")
        else:
            text(d, (PX + 12, y + 12), str(i + 1), font("Inter-SemiBold", 11), fade(mix(MUTED, INK, lit), ap), "mm")
        if i < 2:
            d.line(P(PX + 12, y + 30, PX + 12, y + 82), fill=fade(mix(HAIR, INK, done), ap), width=int(1.5 * S))
        text(d, (PX + 38, y + 12), name, font("Inter-SemiBold", 18), fade(mix(MUTED, INK, lit), ap))
        text(d, (PX + 38, y + 38), sub, font("Inter-Regular", 14), fade(MUTED, ap * (0.5 + 0.5 * lit)))
    ca = ease(seg(t, 4.9, 5.4))
    text(d, (48, 664), "No more worrying about the next move.", font("Inter-Medium", 18), fade(INK, ca))

# ---------------------------------------------------------------- level 3: a live board, in public
L3_MOVES = [("P", "e2", "e4"), ("p", "e7", "e5"), ("N", "g1", "f3"), ("n", "b8", "c6"),
            ("B", "f1", "c4"), ("b", "f8", "c5"), ("P", "c2", "c3"), ("n", "g8", "f6")]
L3_SAN = ["e4", "e5", "Nf3", "Nc6", "Bc4", "Bc5", "c3", "Nf6"]
L3_WHO = ["Program", "Cohort", "Program", "Cohort", "Program", "Cohort", "Program", "Cohort"]
L3_T0, L3_DT = 0.9, 0.5

def s_level3(d, t):
    hud(d, t, 3, "Built in public", 1.0)
    heading(d, t, "Built in public", "Not one expert’s opinion. Every move, in the open.", 1)
    la = ease(seg(t, 0.4, 0.9))
    pulse = 0.5 + 0.5 * math.sin(t * 5)
    rrect(d, (W - 48 - 78, 92, W - 48, 116), 12, outline=fade(INK, la), width=1)
    dot(d, (W - 48 - 60, 104), 4, fill=fade(mix(MUTED, INK, pulse), la))
    spaced(d, (W - 48 - 48, 104), "LIVE", font("Inter-SemiBold", 11), fade(INK, la), 2.4)
    pos = dict(START); moving = []; tint = {}
    for i, (ch, fr, to) in enumerate(L3_MOVES):
        k = eio(seg(t, L3_T0 + i * L3_DT, L3_T0 + i * L3_DT + 0.35))
        if k >= 1:
            pos.pop(fr); pos[to] = ch; tint = {fr: 1.0, to: 1.0}
        elif k > 0:
            moving.append((ch, fr, to, k)); tint = {fr: 1.0, to: 1.0}
            break
        else:
            break
    board(d, pos, 1, moving, tint)
    # move list
    ma = ease(seg(t, 0.5, 1.0))
    spaced(d, (PX, 236), "MOVES", font("Inter-SemiBold", 11), fade(MUTED, ma), 2.4)
    spaced(d, (W - 48, 236), "OPEN TO ALL", font("Inter-SemiBold", 11), fade(MUTED, ma), 2.4, "r")
    d.line(P(PX, 252, W - 48, 252), fill=fade(HAIR, ma), width=S)
    for i in range(len(L3_MOVES)):
        k = ease(seg(t, L3_T0 + i * L3_DT + 0.2, L3_T0 + i * L3_DT + 0.5))
        if k <= 0: break
        row, side = i // 2, i % 2
        y = 274 + row * 34
        if side == 0:
            text(d, (PX, y), f"{row + 1}.", font("Inter-Medium", 15), fade(MUTED, k))
        x = PX + 34 + side * 150
        text(d, (x, y), L3_SAN[i], font("Inter-SemiBold", 16), fade(INK, k))
        text(d, (x + 52, y), L3_WHO[i], font("Inter-Regular", 12), fade(MUTED, k))
    # people watching and building alongside
    ya = 430
    pa = ease(seg(t, 1.6, 2.1))
    spaced(d, (PX, ya), "BUILDING ALONGSIDE", font("Inter-SemiBold", 11), fade(MUTED, pa), 2.4)
    count = int(12 + 116 * eio(seg(t, 1.8, 4.6)))
    text(d, (W - 48, ya), str(count), font("Inter-SemiBold", 14), fade(INK, pa), "rm")
    tones = [INK, (80, 80, 80), (130, 130, 126), (175, 175, 170), (205, 205, 200)]
    for j in range(12):
        ja = ease(seg(t, 1.8 + j * 0.12, 2.1 + j * 0.12))
        if ja <= 0: continue
        cx = PX + 14 + j * 22
        dot(d, (cx, ya + 36), 13, fill=fade(BG, ja))
        dot(d, (cx, ya + 36), 11, fill=fade(tones[j % 5], ja))
    ca = ease(seg(t, 3.6, 4.2))
    text(d, (48, 664), "See every move being played. Build alongside it.", font("Inter-Medium", 18), fade(INK, ca))

# ---------------------------------------------------------------- end
def s_end(d, t):
    k = ease(seg(t, 0.1, 0.7))
    spaced(d, (W / 2, 210), "CHECKMATE", font("Inter-SemiBold", 12), fade(MUTED, k), 3, "m")
    f1 = font(DISPLAY_M, 38)
    s1 = "Less talking about value."
    text(d, (W / 2, 280), s1, f1, fade(MUTED, k), "mm")
    tw = f1.getlength(s1) / S
    st = eio(seg(t, 0.8, 1.4))
    if st > 0:
        d.line(P(W / 2 - tw / 2 - 4, 283, W / 2 - tw / 2 - 4 + (tw + 8) * st, 283), fill=INK, width=int(2.5 * S))
    k2 = ease(seg(t, 1.5, 2.2))
    text(d, (W / 2, 348 + 10 * (1 - k2)), "More creating it.", font(DISPLAY, 62), fade(INK, k2), "mm")
    # the switch arrives on, then a click slides it back off: the original logo, ready to play again
    E_PRESS, E_S0, E_S1 = 3.75, 3.9, 4.55
    la = ease(seg(t, 2.3, 2.9))
    on = 1 - eio(seg(t, E_S0, E_S1))
    LW, LCX, LCY = 300, W / 2, 480 + 8 * (1 - la)
    logo_at(LCX, LCY, LW, on, la)
    sc = LW / LOGO.width
    kx = LCX + (KX0 + (KX1 - KX0) * 0.62 + TRAVEL * on - LOGO.width / 2) * sc
    ky = LCY + (112 - LOGO.height / 2) * sc
    if t > 2.95:
        g = eio(seg(t, 2.95, 3.7))
        cx, cy = lerp(660, kx, g), lerp(720, ky, g)
        if t > E_S1 + 0.15:
            r = eio(seg(t, E_S1 + 0.15, E_S1 + 0.9))
            cx, cy = kx + 70 * r, ky + 120 * r
        pressed = E_PRESS < t < E_S1 + 0.15
        OVER.append(("cursor", cx, cy, 0.9 if pressed else 1.0, 1 - seg(t, E_S1 + 0.6, E_S1 + 0.9)))
    pa = ease(seg(t, E_S1, E_S1 + 0.5))
    spaced(d, (W / 2, 590), "PLAY AGAIN", font("Inter-SemiBold", 12), fade(MUTED, pa), 3, "m")

SCENES = [(s_title, 3.3), (s_level1, 7.2), (s_level2, 6.6), (s_level3, 6.2), (s_end, 6.4)]
XF = 0.35

def render():
    frames = []
    for fn, dur in SCENES:
        for i in range(int(dur * FPS)):
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
                    if a < 1: lg.putalpha(lg.getchannel("A").point(lambda v: int(v * a)))
                    im.alpha_composite(lg, (int(cx - w / 2), int(cy - h / 2)))
                elif ov[0] == "cursor":
                    _, cx, cy, sc, a = ov
                    cs = CURSOR[sc]
                    if a < 1:
                        cs = cs.copy(); cs.putalpha(cs.getchannel("A").point(lambda v: int(v * a)))
                    im.alpha_composite(cs, (int(cx - 3), int(cy - 3)))
                elif ov[0] == "img_raw":
                    _, src, cx, cy = ov
                    im.alpha_composite(src, (int(cx - src.width / 2), int(cy - src.height / 2)))
            im = im.convert("RGB")
            fin, fout = clamp(t / XF), clamp((dur - t) / XF)
            a = min(fin if fn is not s_title else 1, fout if fn is not s_end else 1)
            if a < 1:
                im = Image.blend(Image.new("RGB", im.size, BG), im, a)
            frames.append(im)
    return frames

if __name__ == "__main__":
    frames = render()
    pal = [f.quantize(colors=36, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE) for f in frames]
    durs = [round(1000 / FPS)] * len(pal)
    durs[-1] = 1500
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "answer-vs-value-chess.gif")
    pal[0].save(out, save_all=True, append_images=pal[1:], duration=durs, loop=0, optimize=True, disposal=1)
    print(len(frames), "frames ->", out)

"""Render 'Answer vs Value' GIF for the Sandbox GTME post."""
import math
from PIL import Image, ImageDraw, ImageFont

S = 2                      # supersample factor
W = H = 800                # output size
FPS = 15
BG = (246, 243, 236)
INK = (22, 24, 29)
MUTED = (140, 138, 130)
LINE = (214, 209, 198)
ACC = (255, 90, 40)
ACC_SOFT = (255, 222, 206)
CARD = (255, 255, 255)

F = "/usr/share/fonts/opentype/inter/"
def font(w, px): return ImageFont.truetype(F + f"Inter-{w}.otf", px * S)

def lerp(a, b, t): return a + (b - a) * t
def mix(c1, c2, t): return tuple(int(lerp(a, b, t)) for a, b in zip(c1, c2))
def clamp(t): return max(0.0, min(1.0, t))
def ease(t):
    t = clamp(t); return 1 - (1 - t) ** 3
def back(t):
    t = clamp(t); c = 1.7; return 1 + (c + 1) * (t - 1) ** 3 + c * (t - 1) ** 2
def seg(t, a, b): return clamp((t - a) / (b - a))
def fade(col, a): return mix(BG, col, clamp(a))

def P(*v): return [x * S for x in v]

def text(d, xy, s, f, col, anchor="mm"):
    d.text((xy[0] * S, xy[1] * S), s, font=f, fill=col, anchor=anchor)

def rrect(d, box, r, fill=None, outline=None, width=1):
    d.rounded_rectangle(P(*box), radius=r * S, fill=fill, outline=outline, width=width * S)

def circle(d, c, r, fill=None, outline=None, width=1):
    d.ellipse(P(c[0] - r, c[1] - r, c[0] + r, c[1] + r), fill=fill, outline=outline, width=width * S)

def person(d, c, r, col, a=1.0, label=None):
    circle(d, (c[0], c[1] - r * 0.55), r * 0.42, fill=fade(col, a))
    d.pieslice(P(c[0] - r * 0.8, c[1] + r * 0.05, c[0] + r * 0.8, c[1] + r * 1.5), 180, 360, fill=fade(col, a))
    if label:
        text(d, (c[0], c[1] + r * 1.2), label, font("Medium", 18), fade(MUTED, a))

def bubble(d, c, w, h, s, f, fill, col, scale, tail_left=True):
    if scale <= 0.01: return
    w2, h2 = w * scale / 2, h * scale / 2
    rrect(d, (c[0] - w2, c[1] - h2, c[0] + w2, c[1] + h2), 18 * scale, fill=fill)
    tx = c[0] - w2 * 0.5 if tail_left else c[0] + w2 * 0.5
    d.polygon(P(tx - 10 * scale, c[1] + h2 - 2, tx + 10 * scale, c[1] + h2 - 2, tx, c[1] + h2 + 16 * scale), fill=fill)
    if scale > 0.6:
        text(d, c, s, f, col)

def header(d, kicker, title, a):
    text(d, (W / 2, 92), kicker.upper(), font("SemiBold", 17), fade(ACC, a))
    text(d, (W / 2, 135), title, font("Bold", 40), fade(INK, a))

def footer(d, a=1):
    text(d, (W / 2, H - 38), "SANDBOX  ·  GTME", font("SemiBold", 14), fade(MUTED, a))

# ---------------------------------------------------------------- scenes
def scene_intro(d, t, dur):
    a1, a2, a3 = ease(seg(t, 0.1, 0.6)), ease(seg(t, 0.7, 1.2)), ease(seg(t, 1.5, 2.0))
    text(d, (W / 2, 300 + 12 * (1 - a1)), "Most service businesses", font("Medium", 34), fade(MUTED, a1))
    text(d, (W / 2, 350 + 12 * (1 - a1)), "are built around solving a problem.", font("Medium", 34), fade(MUTED, a1))
    text(d, (W / 2, 450 + 12 * (1 - a2)), "But the solution is only one part.", font("Bold", 38), fade(INK, a2))
    # underline sweeps
    lw = 300 * ease(seg(t, 1.5, 2.2))
    d.line(P(W / 2 - 150, 500, W / 2 - 150 + lw, 500), fill=fade(ACC, a3), width=5 * S)
    text(d, (W / 2, 545), "What every business needs is value creation.", font("SemiBold", 24), fade(ACC, a3))
    footer(d, a1)

def scene_loop(d, t, dur):
    a = ease(seg(t, 0, 0.4))
    header(d, "Giving an answer", "The opinion loop", a)
    you, exp = (230, 470), (570, 470)
    person(d, you, 52, INK, a, "You")
    person(d, exp, 52, MUTED, a, "The expert")
    cycle = 1.6
    n = int(t // cycle)
    ct = (t % cycle) / cycle
    day = min(n + 1, 4)
    # day counter
    rrect(d, (W / 2 - 60, 190, W / 2 + 60, 228), 19, fill=fade(INK, a))
    text(d, (W / 2, 209), f"Day {day}", font("SemiBold", 18), fade(BG, a))
    # question bubble then opinion bubble
    q_s = back(seg(ct, 0.0, 0.18)) * (1 - ease(seg(ct, 0.82, 0.95)))
    o_s = back(seg(ct, 0.32, 0.5)) * (1 - ease(seg(ct, 0.82, 0.95)))
    qs = ["How do we get leads?", "What should we build?", "Which channel first?", "Now what?"]
    bubble(d, (you[0] + 30, 330), 250, 56, qs[n % 4], font("SemiBold", 17), CARD, INK, q_s * a)
    bubble(d, (exp[0] - 30, 330), 250, 56, "Here's what I think.", font("Medium", 17), LINE, INK, o_s * a, tail_left=False)
    # loop arrow between them (rotating arc)
    ang = (t * 240) % 360
    cx, cy, r = W / 2, 470, 46
    d.arc(P(cx - r, cy - r, cx + r, cy + r), ang, ang + 270, fill=fade(ACC, a), width=4 * S)
    ex = cx + r * math.cos(math.radians(ang + 270)); ey = cy + r * math.sin(math.radians(ang + 270))
    circle(d, (ex, ey), 7, fill=fade(ACC, a))
    # pile of unanswered questions
    text(d, (W / 2, 610), "...and the next day, you're back with another question.",
         font("Medium", 19), fade(MUTED, ease(seg(t, 1.0, 1.5))))
    piles = min(n * 4 + int(ct * 4), 18)
    for i in range(piles):
        x = 160 + (i % 9) * 60; y = 670 + (i // 9) * 44
        circle(d, (x, y), 17, fill=fade(ACC_SOFT, a))
        text(d, (x, y - 1), "?", font("Bold", 18), fade(ACC, a))
    footer(d, a)

def scene_value(d, t, dur):
    a = ease(seg(t, 0, 0.4))
    header(d, "Creating value", "Understand how to solve it", a)
    you = (130, 430)
    person(d, you, 48, INK, a, "You")
    steps = ["Understand", "Strategy", "Build"]
    xs = [300, 470, 640]
    for i, (x, s) in enumerate(zip(xs, steps)):
        on = ease(seg(t, 0.6 + i * 0.7, 1.0 + i * 0.7))
        x0 = you[0] + 60 if i == 0 else xs[i - 1] + 44
        d.line(P(x0, 430, lerp(x0, x - 44, on), 430), fill=fade(ACC, a), width=5 * S)
        circle(d, (x, 430), 40, fill=fade(mix(CARD, ACC, on), a), outline=fade(mix(LINE, ACC, on), a), width=3)
        if on > 0.9:  # check mark
            d.line(P(x - 14, 431, x - 4, 442, x + 16, 418), fill=CARD, width=6 * S, joint="curve")
        else:
            text(d, (x, 430), str(i + 1), font("Bold", 22), fade(MUTED, a))
        text(d, (x, 495), s, font("SemiBold", 20), fade(mix(MUTED, INK, on), a))
    # old questions dissolve
    gone = ease(seg(t, 0.4, 2.6))
    for i in range(18):
        x = 160 + (i % 9) * 60; y = 670 + (i // 9) * 44 - 60 * gone
        al = a * (1 - gone)
        if al > 0.02:
            circle(d, (x, y), 17 * (1 - gone * 0.6), fill=fade(ACC_SOFT, al))
            text(d, (x, y - 1), "?", font("Bold", 18), fade(ACC, al))
    b = ease(seg(t, 2.8, 3.3))
    text(d, (W / 2, 595), "No more worrying about what to do next,", font("Medium", 22), fade(INK, b))
    text(d, (W / 2, 628), "or the hundred other things waiting in line.", font("Medium", 22), fade(INK, b))
    c = ease(seg(t, 3.6, 4.1))
    rrect(d, (W / 2 - 250, 680, W / 2 + 250, 728), 24, fill=fade(INK, c))
    text(d, (W / 2, 704), "That's the gap between an answer and value.", font("SemiBold", 18), fade(BG, c))
    footer(d, a)

def scene_public(d, t, dur):
    a = ease(seg(t, 0, 0.4))
    header(d, "How we run Sandbox", "GTME, built in public", a)
    cards = ["ICP research", "Outbound system", "Messaging tests",
             "Pipeline build", "Content engine", "Weekly teardown"]
    for i, name in enumerate(cards):
        col, row = i % 3, i // 3
        x0, y0 = 70 + col * 225, 200 + row * 165
        p = ease(seg(t, 0.3 + i * 0.25, 0.7 + i * 0.25))
        if p <= 0: continue
        oy = 20 * (1 - p)
        rrect(d, (x0, y0 + oy, x0 + 205, y0 + 145 + oy), 16, fill=fade(CARD, p), outline=fade(LINE, p), width=2)
        pulse = 0.5 + 0.5 * math.sin(t * 6 + i)
        circle(d, (x0 + 24, y0 + 28 + oy), 6, fill=fade(mix(ACC_SOFT, ACC, pulse), p))
        text(d, (x0 + 38, y0 + 28 + oy), "LIVE", font("Bold", 12), fade(ACC, p), anchor="lm")
        text(d, (x0 + 18, y0 + 68 + oy), name, font("SemiBold", 18), fade(INK, p), anchor="lm")
        prog = clamp((t - 0.6 - i * 0.25) / 2.2) * (0.55 + 0.45 * ((i * 37) % 10) / 10)
        rrect(d, (x0 + 18, y0 + 104 + oy, x0 + 187, y0 + 114 + oy), 5, fill=fade(LINE, p))
        if prog > 0.03:
            rrect(d, (x0 + 18, y0 + 104 + oy, x0 + 18 + 169 * prog, y0 + 114 + oy), 5, fill=fade(INK, p))
    b = ease(seg(t, 2.2, 2.7))
    text(d, (W / 2, 580), "Not one expert's opinion. Not a strategist's take.", font("Medium", 21), fade(MUTED, b))
    text(d, (W / 2, 625), "See the work being done. Build alongside it.", font("Bold", 26), fade(INK, b))
    footer(d, a)

def scene_end(d, t, dur):
    a1, a2 = ease(seg(t, 0.1, 0.6)), ease(seg(t, 1.0, 1.5))
    f1 = font("SemiBold", 44)
    y1 = 345
    text(d, (W / 2, y1), "Less talking about value.", f1, fade(MUTED, a1))
    tw = d.textlength("Less talking about value.", font=f1) / S
    st = ease(seg(t, 0.6, 1.0))
    d.line(P(W / 2 - tw / 2 - 6, y1 + 2, W / 2 - tw / 2 - 6 + (tw + 12) * st, y1 + 2), fill=fade(ACC, a1), width=4 * S)
    text(d, (W / 2, 430 + 14 * (1 - a2)), "More creating it.", font("Bold", 64), fade(INK, a2))
    a3 = ease(seg(t, 1.8, 2.3))
    rrect(d, (W / 2 - 110, 520, W / 2 + 110, 566), 23, fill=fade(ACC, a3))
    text(d, (W / 2, 543), "SANDBOX  ·  GTME", font("Bold", 16), fade(BG, a3) if a3 > 0.5 else fade(ACC, a3))
    footer(d, 0)

SCENES = [(scene_intro, 3.6), (scene_loop, 6.4), (scene_value, 5.6), (scene_public, 5.0), (scene_end, 4.0)]
XF = 0.35  # crossfade seconds

frames = []
for fn, dur in SCENES:
    n = int(dur * FPS)
    for i in range(n):
        t = i / FPS
        im = Image.new("RGB", (W * S, H * S), BG)
        fn(ImageDraw.Draw(im), t, dur)
        out_a = clamp((dur - t) / XF)
        if out_a < 1 and fn is not scene_end:
            im = Image.blend(Image.new("RGB", im.size, BG), im, out_a)
        frames.append(im.resize((W, H), Image.LANCZOS))

# hold the final frame a bit longer
pal = [f.convert("P", palette=Image.ADAPTIVE, colors=64, dither=Image.Dither.NONE) for f in frames]
durs = [int(1000 / FPS)] * len(pal)
durs[-1] = 1800
pal[0].save("/home/user/AnimatedGif/sandbox_value_gif/answer-vs-value.gif", save_all=True,
            append_images=pal[1:], duration=durs, loop=0, optimize=True, disposal=1)
print(len(frames), "frames")

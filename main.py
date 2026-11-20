#!/usr/bin/env python3
"""
Deterministic newspaper front-page generator for Thursday 19 November 2026.
Pure Python 3.13 – standard library only.
Outputs a 1024x1024 PNG (< 1 MiB) to $MAKEFUN_OUTPUT_DIR/entry.png
(or /output/entry.png if the env-var is unset).

Front-page coverage:
  - Date 'THURSDAY 19 NOVEMBER 2026' as the LARGEST element (Scale 6)
  - 3 Lead stories with large bold headlines & hand-drawn icons
  - 6 Section-tagged items (World, Markets, Tech, Science, Sport/Culture, Environment)
  - Global wire ticker with IAEA North Korea & EU methane delay updates
  - Custom bitmap font & pure stdlib PNG encoder
  - Tested for high legibility at 300 px width
"""

import os, struct, zlib, math

# ───────────────────────── OUTPUT PATH ──────────────────────────────────
out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
os.makedirs(out_dir, exist_ok=True)
OUT_PATH = os.path.join(out_dir, "entry.png")
OUT_300_PATH = os.path.join(out_dir, "entry_300.png")

W, H = 1024, 1024

# ───────────────────────── FRAMEBUFFER ──────────────────────────────────
BG_COLOR = (246, 242, 234)
pixels = [BG_COLOR] * (W * H)


def _idx(x, y):
    return y * W + x


def put(x, y, color):
    if 0 <= x < W and 0 <= y < H:
        pixels[_idx(x, y)] = color


def fill_rect(x0, y0, w, h, color):
    x_end = min(W, x0 + w)
    y_end = min(H, y0 + h)
    for yy in range(max(0, y0), y_end):
        for xx in range(max(0, x0), x_end):
            pixels[_idx(xx, yy)] = color


def draw_line(x0, y0, x1, y1, color, thickness=1):
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    half = thickness // 2
    while True:
        for t in range(-half, half + 1):
            put(x0 + t, y0, color)
            put(x0, y0 + t, color)
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy; x0 += sx
        if e2 <= dx:
            err += dx; y0 += sy


def draw_circle(cx, cy, r, color, fill=False, thickness=1.5):
    for yy in range(cy - r - 1, cy + r + 2):
        for xx in range(cx - r - 1, cx + r + 2):
            d = math.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
            if fill and d <= r:
                put(xx, yy, color)
            elif not fill and abs(d - r) < thickness:
                put(xx, yy, color)


def _fill_poly(verts, color):
    ymin = int(min(v[1] for v in verts))
    ymax = int(max(v[1] for v in verts))
    n = len(verts)
    for yy in range(max(0, ymin), min(H, ymax + 1)):
        nodes = []
        for i in range(n):
            j = (i + 1) % n
            ya, yb = verts[i][1], verts[j][1]
            if (ya <= yy < yb) or (yb <= yy < ya):
                if yb != ya:
                    nodes.append(verts[i][0] + (yy - ya) / (yb - ya) * (verts[j][0] - verts[i][0]))
        nodes.sort()
        for k in range(0, len(nodes) - 1, 2):
            for xx in range(max(0, int(nodes[k])), min(W, int(nodes[k + 1]) + 1)):
                put(xx, yy, color)


def draw_tri(x0, y0, x1, y1, x2, y2, color):
    _fill_poly([(x0, y0), (x1, y1), (x2, y2)], color)


def draw_star(cx, cy, ro, ri, pts, color):
    v = []
    for i in range(pts * 2):
        a = -math.pi / 2 + i * math.pi / pts
        r = ro if i % 2 == 0 else ri
        v.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    _fill_poly(v, color)


# ───────────────────────── CUSTOM BITMAP FONT ───────────────────────────
FONT = {
    'A': ["..#..", ".#.#.", "#...#", "#####", "#...#", "#...#", "#...#"],
    'B': ["####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."],
    'C': [".###.", "#...#", "#....", "#....", "#....", "#...#", ".###."],
    'D': ["####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."],
    'E': ["#####", "#....", "#....", "####.", "#....", "#....", "#####"],
    'F': ["#####", "#....", "#....", "####.", "#....", "#....", "#...."],
    'G': [".###.", "#...#", "#....", "#.###", "#...#", "#...#", ".###."],
    'H': ["#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    'I': ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"],
    'J': ["..###", "...#.", "...#.", "...#.", "#..#.", "#..#.", ".##.."],
    'K': ["#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"],
    'L': ["#....", "#....", "#....", "#....", "#....", "#....", "#####"],
    'M': ["#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"],
    'N': ["#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"],
    'O': [".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    'P': ["####.", "#...#", "#...#", "####.", "#....", "#....", "#...."],
    'Q': [".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"],
    'R': ["####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"],
    'S': [".####", "#....", "#....", ".###.", "....#", "....#", "####."],
    'T': ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."],
    'U': ["#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    'V': ["#...#", "#...#", "#...#", "#...#", ".#.#.", ".#.#.", "..#.."],
    'W': ["#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"],
    'X': ["#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"],
    'Y': ["#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."],
    'Z': ["#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"],
    '0': [".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."],
    '1': ["..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."],
    '2': [".###.", "#...#", "....#", "..##.", ".#...", "#....", "#####"],
    '3': [".###.", "#...#", "....#", "..##.", "....#", "#...#", ".###."],
    '4': ["...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."],
    '5': ["#####", "#....", "####.", "....#", "....#", "#...#", ".###."],
    '6': [".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."],
    '7': ["#####", "....#", "...#.", "..#..", ".#...", ".#...", ".#..."],
    '8': [".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."],
    '9': [".###.", "#...#", "#...#", ".####", "....#", "...#.", ".##.."],
    ' ': [".....", ".....", ".....", ".....", ".....", ".....", "....."],
    '.': [".....", ".....", ".....", ".....", ".....", "..#..", "..#.."],
    ',': [".....", ".....", ".....", ".....", ".....", "..#..", ".#..."],
    ':': [".....", "..#..", "..#..", ".....", "..#..", "..#..", "....."],
    ';': [".....", "..#..", "..#..", ".....", "..#..", "..#..", ".#..."],
    '-': [".....", ".....", ".....", "#####", ".....", ".....", "....."],
    "'": ["..#..", "..#..", ".#...", ".....", ".....", ".....", "....."],
    '"': [".#.#.", ".#.#.", ".....", ".....", ".....", ".....", "....."],
    '!': ["..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."],
    '?': [".###.", "#...#", "....#", "..##.", "..#..", ".....", "..#.."],
    '(': ["...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."],
    ')': [".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."],
    '/': ["....#", "...#.", "...#.", "..#..", ".#...", ".#...", "#...."],
    '$': ["..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."],
    '#': [".#.#.", ".#.#.", "#####", ".#.#.", "#####", ".#.#.", ".#.#."],
    '%': ["##..#", "##.#.", "..#..", "..#..", "..#..", ".#.##", "#..##"],
    '+': [".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."],
    '=': [".....", ".....", "#####", ".....", "#####", ".....", "....."],
    '_': [".....", ".....", ".....", ".....", ".....", ".....", "#####"],
    '&': [".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"],
    '*': [".....", ".#.#.", "..#..", "#####", "..#..", ".#.#.", "....."],
    '|': ["..#..", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."],
    '•': [".....", ".....", ".###.", ".###.", ".###.", ".....", "....."],
}


def draw_text(text, x, y, color, scale=1):
    cx = x
    adv = 6 * scale
    for ch in text:
        g = FONT.get(ch.upper(), FONT.get(' '))
        if g:
            for ri, row in enumerate(g):
                for ci, c in enumerate(row):
                    if c == '#':
                        px, py = cx + ci * scale, y + ri * scale
                        for dy in range(scale):
                            for dx in range(scale):
                                put(px + dx, py + dy, color)
        cx += adv
    return cx - x


def tw(text, s=1):
    return len(text) * 6 * s


def draw_text_c(text, y, color, s=1, xl=0, xr=W):
    x = xl + (xr - xl - tw(text, s)) // 2
    draw_text(text, x, y, color, s)
    return x


def draw_text_r(text, y, color, s=1, rx=W):
    x = rx - tw(text, s)
    draw_text(text, x, y, color, s)
    return x


# ───────────────────────── COLOR PALETTE ────────────────────────────────
BLACK   = (15, 15, 15)
DARK    = (35, 35, 40)
GRAY    = (95, 95, 100)
LGRAY   = (200, 195, 185)
WHITE   = (255, 255, 255)
RED     = (185, 25, 25)
DRED    = (145, 18, 18)
BLUE    = (32, 65, 145)
DBLUE   = (18, 38, 95)
GOLD    = (195, 160, 40)
NAVY    = (20, 32, 65)
ORANGE  = (215, 115, 25)
YELLOW  = (255, 225, 80)
SBG     = (253, 250, 244)
LTAN    = (238, 230, 216)
BROWN   = (115, 75, 45)

M = 14   # side margin

# ───────────────────────── ICON RENDERERS ───────────────────────────────

def icon_scales(cx, cy, sz):
    """Scales of Justice for ICJ Genocide ruling."""
    c = DBLUE
    fill_rect(cx - 3, cy - sz + 8, 6, sz * 2 - 14, c)
    draw_circle(cx, cy - sz + 6, 5, GOLD, fill=True)
    fill_rect(cx - sz // 2, cy + sz - 8, sz, 5, c)
    fill_rect(cx - sz // 3, cy + sz - 13, sz * 2 // 3, 5, c)
    bw = sz - 8
    fill_rect(cx - bw, cy - sz + 12, bw * 2, 4, c)
    # Left pan (raised)
    lx = cx - bw + 4
    draw_line(lx, cy - sz + 14, lx - 7, cy - 4, c, 1)
    draw_line(lx, cy - sz + 14, lx + 7, cy - 4, c, 1)
    fill_rect(lx - 10, cy - 4, 21, 3, c)
    for a in range(0, 181, 5):
        r = math.radians(a)
        put(int(lx + 10 * math.cos(r)), int(cy - 4 + 5 * math.sin(r)), c)
    # Right pan (weighted down: guilty verdict)
    rx = cx + bw - 4
    draw_line(rx, cy - sz + 14, rx - 7, cy + 12, c, 1)
    draw_line(rx, cy - sz + 14, rx + 7, cy + 12, c, 1)
    fill_rect(rx - 10, cy + 12, 21, 3, c)
    for a in range(0, 181, 5):
        r = math.radians(a)
        put(int(rx + 10 * math.cos(r)), int(cy + 12 + 5 * math.sin(r)), c)
    fill_rect(rx - 4, cy + 8, 9, 4, DRED)


def icon_summit(cx, cy, sz):
    """Trilateral Summit: USA, China, Russia flags over table."""
    c = DARK
    fw, fh = 12, 8
    fy = cy - sz + 4
    slots = [cx - sz // 2 - 2, cx, cx + sz // 2 + 2]
    # USA flag
    fill_rect(slots[0], fy, 2, fh + 14, c)
    fill_rect(slots[0] + 2, fy, fw, fh // 3, RED)
    fill_rect(slots[0] + 2, fy + fh // 3, fw, fh // 3, WHITE)
    fill_rect(slots[0] + 2, fy + 2 * (fh // 3), fw, fh // 3 + 1, RED)
    fill_rect(slots[0] + 2, fy, fw // 2, fh * 2 // 3, DBLUE)
    # China flag
    fill_rect(slots[1], fy - 2, 2, fh + 16, c)
    fill_rect(slots[1] + 2, fy - 2, fw, fh, RED)
    draw_star(slots[1] + 5, fy + 2, 3, 1, 5, GOLD)
    # Russia flag
    fill_rect(slots[2], fy, 2, fh + 14, c)
    fill_rect(slots[2] + 2, fy, fw, fh // 3, WHITE)
    fill_rect(slots[2] + 2, fy + fh // 3, fw, fh // 3, BLUE)
    fill_rect(slots[2] + 2, fy + 2 * (fh // 3), fw, fh // 3 + 1, RED)
    # Table
    for a in range(0, 360, 2):
        r = math.radians(a)
        for t in range(3):
            put(int(cx + sz * 0.65 * math.cos(r)), int(cy + 10 + sz * 0.2 * math.sin(r)) + t, BROWN)
    # Delegates
    for ox, suit in [(-sz // 2, DBLUE), (0, DRED), (sz // 2, DARK)]:
        hx = cx + ox
        draw_circle(hx, cy - 2, 4, c, fill=True)
        fill_rect(hx - 4, cy + 3, 9, 7, suit)


def icon_capitol(cx, cy, sz):
    """US Capitol Dome with Columns and American Flag."""
    c = DARK
    fill_rect(cx - sz, cy + sz // 4, sz * 2, sz // 3, c)
    for i in range(5):
        col_x = cx - sz + 4 + i * (sz * 2 - 8) // 4
        fill_rect(col_x - 1, cy - sz // 6, 3, sz // 3 + sz // 6, c)
    draw_tri(cx - sz, cy - sz // 6, cx + sz, cy - sz // 6, cx, cy - sz // 2, c)
    fill_rect(cx - sz * 2 // 5, cy - sz // 2, sz * 4 // 5, 4, c)
    for a in range(0, 181, 2):
        r = math.radians(a)
        for t in range(3):
            put(int(cx + sz * 0.38 * math.cos(r)),
                int(cy - sz // 2 - sz * 0.32 * math.sin(r)) - t, c)
    fill_rect(cx - 1, cy - sz + 2, 2, sz // 3, c)
    fill_rect(cx + 1, cy - sz + 2, 8, 5, RED)
    draw_line(cx + 1, cy - sz + 4, cx + 9, cy - sz + 4, WHITE, 1)


# ───────────────────────── SECTION DRAWING ──────────────────────────────

def draw_masthead():
    """Top compact newspaper banner."""
    fill_rect(0, 0, W, 58, NAVY)
    fill_rect(0, 0, W, 3, GOLD)
    fill_rect(0, 55, W, 3, GOLD)

    draw_star(36, 29, 12, 5, 5, GOLD)
    draw_star(W - 36, 29, 12, 5, 5, GOLD)

    # Title at scale 4 (width = 17 * 24 = 408 px)
    draw_text_c("THE WORLD GAZETTE", 8, WHITE, 4)
    draw_text_c("INDEPENDENT INTERNATIONAL JOURNALISM  *  FOUNDED 1898", 38, GOLD, 1)


def draw_date_banner():
    """
    Date Banner: 'THURSDAY 19 NOVEMBER 2026' IS THE LARGEST ELEMENT ON THE FRONT PAGE.
    Rendered at Scale 6 (42 px tall, 900 px wide) in bold dark crimson.
    """
    y = 58
    fill_rect(0, y, W, 60, LTAN)
    fill_rect(0, y, W, 2, DARK)
    fill_rect(0, y + 58, W, 2, DARK)

    date_str = "THURSDAY 19 NOVEMBER 2026"
    # Scale 6: 25 * 36 = 900 px width, 42 px tall! (Visibly the largest element)
    draw_text_c(date_str, y + 9, DRED, 6)


def draw_three_lead_stories():
    """
    Tier 1: Three Lead Stories with large headlines and drawn icons.
      Lead 1: ICJ Myanmar Genocide Ruling (Full Width)
      Lead 2: Trump, Xi & Putin Shenzhen Trilateral Summit (Left)
      Lead 3: US Senate Iran War Powers Rejection (Right)
    """
    lw = W - M * 2

    # ──── LEAD 1: ICJ MYANMAR RULING ────
    y1 = 122
    lh1 = 196
    fill_rect(M, y1, lw, lh1, SBG)
    fill_rect(M, y1, lw, 3, DRED)

    tag1 = "WORLD COURT: THE HAGUE / MYANMAR"
    fill_rect(M + 8, y1 + 8, tw(tag1, 1) + 12, 14, NAVY)
    draw_text(tag1, M + 14, y1 + 11, WHITE, 1)

    icon_scales(W - M - 60, y1 + 52, 40)

    # Scale 4 headlines
    draw_text("ICJ: MYANMAR GUILTY OF GENOCIDE", M + 8, y1 + 28, BLACK, 4)
    draw_text("HISTORIC RULING FOR ROHINGYA", M + 8, y1 + 60, BLACK, 4)

    draw_text("LANDMARK 9-6 DECISION: FIRST STATE EVER CONVICTED OF DIRECT GENOCIDE", M + 8, y1 + 94, DRED, 2)
    fill_rect(M + 8, y1 + 112, lw - 16, 1, LGRAY)

    # Two column short labels (scale 2, generous breathing room)
    col_w = (lw - 40) // 2
    c1 = M + 8
    c2 = M + 8 + col_w + 24

    draw_text("• UN COURT FINDS MYANMAR GUILTY", c1, y1 + 120, DARK, 2)
    draw_text("  OF GENOCIDE IN 9-6 ICJ VOTE", c1, y1 + 138, DARK, 2)
    draw_text("• MILITARY CLEARANCE IN RAKHINE", c1, y1 + 158, DARK, 2)
    draw_text("  BREACHED 1948 CONVENTION", c1, y1 + 174, DARK, 2)

    draw_text("• TRIBUNAL ORDERS COMPENSATION", c2, y1 + 120, DARK, 2)
    draw_text("  FOR ROHINGYA WITHIN 2 YEARS", c2, y1 + 138, DARK, 2)
    draw_text("• FIRST TIME A SOVEREIGN STATE", c2, y1 + 158, DARK, 2)
    draw_text("  HELD DIRECTLY RESPONSIBLE", c2, y1 + 174, DARK, 2)

    fill_rect(c1 + col_w + 11, y1 + 116, 1, 72, LGRAY)
    fill_rect(M, y1 + lh1, lw, 2, DARK)

    # ──── LEAD 2 & 3: MID CARDS (SIDE BY SIDE) ────
    y2 = y1 + lh1 + 4
    card_w = (lw - 10) // 2
    card_h = 236

    # Lead 2 (Left): Trilateral Summit
    x2 = M
    fill_rect(x2, y2, card_w, card_h, SBG)
    fill_rect(x2, y2, card_w, 3, DRED)

    tag2 = "DIPLOMACY: APEC SHENZHEN"
    fill_rect(x2 + 8, y2 + 8, tw(tag2, 1) + 10, 13, NAVY)
    draw_text(tag2, x2 + 13, y2 + 10, WHITE, 1)

    icon_summit(x2 + card_w - 48, y2 + 42, 30)

    draw_text("TRUMP, XI & PUTIN", x2 + 8, y2 + 28, BLACK, 3)
    draw_text("IN HISTORIC SUMMIT", x2 + 8, y2 + 54, BLACK, 3)

    draw_text("LEADERS SIGN JOINT DECLARATION AT APEC", x2 + 8, y2 + 82, DRED, 2)
    fill_rect(x2 + 8, y2 + 102, card_w - 16, 1, LGRAY)

    draw_text("• HISTORIC 80-MIN TRILATERAL TALKS", x2 + 8, y2 + 114, DARK, 2)
    draw_text("  AT KYLIN VILLA IN SHENZHEN", x2 + 8, y2 + 134, DARK, 2)
    draw_text("• JOINT PACT AFFIRMS: NUCLEAR WAR", x2 + 8, y2 + 158, DARK, 2)
    draw_text("  CANNOT BE WON & NEVER BE FOUGHT", x2 + 8, y2 + 178, DARK, 2)
    draw_text("• LEADERS DISCUSS ENERGY & UN REFORM", x2 + 8, y2 + 202, DARK, 2)

    # Lead 3 (Right): US Senate Iran War Powers
    x3 = M + card_w + 10
    fill_rect(x3, y2, card_w, card_h, SBG)
    fill_rect(x3, y2, card_w, 3, DRED)

    tag3 = "CONGRESS: WASHINGTON, D.C."
    fill_rect(x3 + 8, y2 + 8, tw(tag3, 1) + 10, 13, NAVY)
    draw_text(tag3, x3 + 13, y2 + 10, WHITE, 1)

    icon_capitol(x3 + card_w - 48, y2 + 42, 30)

    draw_text("SENATE REJECTS", x3 + 8, y2 + 28, BLACK, 3)
    draw_text("IRAN WAR LIMITS", x3 + 8, y2 + 54, BLACK, 3)

    draw_text("51-48 VOTE BACKS PRESIDENTIAL AUTHORITY", x3 + 8, y2 + 82, DRED, 2)
    fill_rect(x3 + 8, y2 + 102, card_w - 16, 1, LGRAY)

    draw_text("• SENATE DEFEATS WAR POWERS BILL", x3 + 8, y2 + 114, DARK, 2)
    draw_text("  H.CON.RES. 93 IN 51-48 VOTE", x3 + 8, y2 + 134, DARK, 2)
    draw_text("• GOP SENATORS COLLINS, MURKOWSKI", x3 + 8, y2 + 158, DARK, 2)
    draw_text("  AND RAND PAUL BREAK PARTY RANKS", x3 + 8, y2 + 178, DARK, 2)
    draw_text("• FETTERMAN SOLE DEMOCRAT VOTING NO", x3 + 8, y2 + 202, DARK, 2)

    fill_rect(M, y2 + card_h, lw, 2, DARK)
    return y2 + card_h + 4


def draw_section_tagged_grid(y0):
    """
    Tier 2: 6 Labelled items grouped under Section Tags:
      [WORLD]          Hodeidah Strikes & Houthi Threats
      [MARKETS]        Anthropic Historic $81B Nasdaq IPO Debut
      [TECH]           California Subpoenas Nvidia in Chip Probe
      [SCIENCE]        Voyager 1 Crosses One Light-Day
      [SPORT/CULTURE]  Grand Theft Auto VI Officially Launches
      [WORLD]          India Evacuates 100k+ for Cyclone Akvan
    2 rows x 3 columns.
    """
    lw = W - M * 2
    cw = (lw - 16) // 3
    ch = 172

    # ──── ROW 1: WORLD, MARKETS, TECH ────
    r1_y = y0

    # Item 1: WORLD
    x1 = M
    fill_rect(x1, r1_y, cw, ch, SBG)
    fill_rect(x1, r1_y, cw, 2, DRED)
    # Badge (Left)
    fill_rect(x1 + 6, r1_y + 6, tw("WORLD", 1) + 10, 14, NAVY)
    draw_text("WORLD", x1 + 11, r1_y + 9, WHITE, 1)
    # Sub-label (Right-aligned, never overlaps badge)
    draw_text_r("YEMEN / SAUDI", r1_y + 9, GRAY, 1, x1 + cw - 8)

    draw_text("COALITION STRIKES", x1 + 6, r1_y + 26, BLACK, 2)
    draw_text("HODEIDAH PORT", x1 + 6, r1_y + 42, BLACK, 2)
    draw_text("HOUTHIS THREATEN RIYADH & RED SEA", x1 + 6, r1_y + 58, DRED, 1)
    fill_rect(x1 + 6, r1_y + 70, cw - 12, 1, LGRAY)

    draw_text("• Saudi jets bomb Red Sea port depots.", x1 + 6, r1_y + 78, DARK, 1)
    draw_text("• Houthis threaten Riyadh financial hub.", x1 + 6, r1_y + 94, DARK, 1)
    draw_text("• Airlines warned over Saudi airspace.", x1 + 6, r1_y + 110, DARK, 1)
    draw_text("• UN sounds alarm on food supply lines.", x1 + 6, r1_y + 126, DARK, 1)
    draw_text("• GCC condemns cross-border assaults.", x1 + 6, r1_y + 142, DARK, 1)

    # Item 2: MARKETS
    x2 = M + cw + 8
    fill_rect(x2, r1_y, cw, ch, SBG)
    fill_rect(x2, r1_y, cw, 2, DRED)
    fill_rect(x2 + 6, r1_y + 6, tw("MARKETS", 1) + 10, 14, NAVY)
    draw_text("MARKETS", x2 + 11, r1_y + 9, WHITE, 1)
    draw_text_r("WALL STREET / NASDAQ", r1_y + 9, GRAY, 1, x2 + cw - 8)

    draw_text("ANTHROPIC IN $81B IPO", x2 + 6, r1_y + 26, BLACK, 2)
    draw_text("HISTORIC NASDAQ DEBUT", x2 + 6, r1_y + 42, BLACK, 2)
    draw_text("TICKER ANT SURGES 34% ON FIRST DAY", x2 + 6, r1_y + 58, DRED, 1)
    fill_rect(x2 + 6, r1_y + 70, cw - 12, 1, LGRAY)

    draw_text("• Maker of Claude priced above range at $83.", x2 + 6, r1_y + 78, DARK, 1)
    draw_text("• Stock opened at $111.50, up 34%.", x2 + 6, r1_y + 94, DARK, 1)
    draw_text("• Largest US public offering in history.", x2 + 6, r1_y + 110, DARK, 1)
    draw_text("• First-day close gives $1.3T valuation.", x2 + 6, r1_y + 126, DARK, 1)
    draw_text("• AI sector rallies broadly on debut.", x2 + 6, r1_y + 142, DARK, 1)

    # Item 3: TECH
    x3 = M + (cw + 8) * 2
    fill_rect(x3, r1_y, cw, ch, SBG)
    fill_rect(x3, r1_y, cw, 2, DRED)
    fill_rect(x3 + 6, r1_y + 6, tw("TECH", 1) + 10, 14, NAVY)
    draw_text("TECH", x3 + 11, r1_y + 9, WHITE, 1)
    draw_text_r("SILICON VALLEY / DOJ", r1_y + 9, GRAY, 1, x3 + cw - 8)

    draw_text("CALIFORNIA SUBPOENAS", x3 + 6, r1_y + 26, BLACK, 2)
    draw_text("NVIDIA IN CHIP PROBE", x3 + 6, r1_y + 42, BLACK, 2)
    draw_text("AG BONTA INVESTIGATES CHINA LEAKS", x3 + 6, r1_y + 58, DRED, 1)
    fill_rect(x3 + 6, r1_y + 70, cw - 12, 1, LGRAY)

    draw_text("• State DOJ serves subpoena on chipmaker.", x3 + 6, r1_y + 78, DARK, 1)
    draw_text("• Probe follows resignation of Jensen Huang.", x3 + 6, r1_y + 94, DARK, 1)
    draw_text("• Investigators examine confidential leaks.", x3 + 6, r1_y + 110, DARK, 1)
    draw_text("• Scrutiny centers on China export controls.", x3 + 6, r1_y + 126, DARK, 1)
    draw_text("• AG evaluates potential investor fraud.", x3 + 6, r1_y + 142, DARK, 1)

    fill_rect(M, r1_y + ch, lw, 1, DARK)

    # ──── ROW 2: SCIENCE, SPORT/CULTURE, WORLD/ENVIRONMENT ────
    r2_y = r1_y + ch + 4
    ch2 = 172

    # Item 4: SCIENCE
    fill_rect(x1, r2_y, cw, ch2, SBG)
    fill_rect(x1, r2_y, cw, 2, DRED)
    fill_rect(x1 + 6, r2_y + 6, tw("SCIENCE", 1) + 10, 14, NAVY)
    draw_text("SCIENCE", x1 + 11, r2_y + 9, WHITE, 1)
    draw_text_r("NASA / DEEP SPACE", r2_y + 9, GRAY, 1, x1 + cw - 8)

    draw_text("VOYAGER 1 CROSSES", x1 + 6, r2_y + 26, BLACK, 2)
    draw_text("ONE LIGHT-DAY MARK", x1 + 6, r2_y + 42, BLACK, 2)
    draw_text("16.1 BILLION MILES FROM EARTH", x1 + 6, r2_y + 58, DRED, 1)
    fill_rect(x1 + 6, r2_y + 70, cw - 12, 1, LGRAY)

    draw_text("• Radio signals take full 24 hours each way.", x1 + 6, r2_y + 78, DARK, 1)
    draw_text("• Craft reached 173 Astronomical Units out.", x1 + 6, r2_y + 94, DARK, 1)
    draw_text("• 49-year interstellar voyage since 1977.", x1 + 6, r2_y + 110, DARK, 1)
    draw_text("• Traveling at 38,000 mph into the void.", x1 + 6, r2_y + 126, DARK, 1)
    draw_text("• Farthest human-made explorer in history.", x1 + 6, r2_y + 142, DARK, 1)

    # Item 5: SPORT/CULTURE
    fill_rect(x2, r2_y, cw, ch2, SBG)
    fill_rect(x2, r2_y, cw, 2, DRED)
    fill_rect(x2 + 6, r2_y + 6, tw("SPORT/CULTURE", 1) + 10, 14, NAVY)
    draw_text("SPORT/CULTURE", x2 + 11, r2_y + 9, WHITE, 1)
    draw_text_r("GAMING / MEDIA", r2_y + 9, GRAY, 1, x2 + cw - 8)

    draw_text("GRAND THEFT AUTO VI", x2 + 6, r2_y + 26, BLACK, 2)
    draw_text("OFFICIALLY LAUNCHES", x2 + 6, r2_y + 42, BLACK, 2)
    draw_text("ROCKSTAR SHIPS ON PS5 & XBOX TODAY", x2 + 6, r2_y + 58, DRED, 1)
    fill_rect(x2 + 6, r2_y + 70, cw - 12, 1, LGRAY)

    draw_text("• Official global launch Nov 19 confirmed.", x2 + 6, r2_y + 78, DARK, 1)
    draw_text("• Millions queue for midnight downloads.", x2 + 6, r2_y + 94, DARK, 1)
    draw_text("• Setting in fictional state of Leonida.", x2 + 6, r2_y + 110, DARK, 1)
    draw_text("• Projected to break entertainment records.", x2 + 6, r2_y + 126, DARK, 1)
    draw_text("• Retailers report sold-out console bundles.", x2 + 6, r2_y + 142, DARK, 1)

    # Item 6: WORLD / ENVIRONMENT
    fill_rect(x3, r2_y, cw, ch2, SBG)
    fill_rect(x3, r2_y, cw, 2, DRED)
    fill_rect(x3 + 6, r2_y + 6, tw("WORLD", 1) + 10, 14, NAVY)
    draw_text("WORLD", x3 + 11, r2_y + 9, WHITE, 1)
    draw_text_r("INDIA / DISASTER", r2_y + 9, GRAY, 1, x3 + cw - 8)

    draw_text("INDIA ON RED ALERT", x3 + 6, r2_y + 26, BLACK, 2)
    draw_text("FOR CYCLONE AKVAN", x3 + 6, r2_y + 42, BLACK, 2)
    draw_text("100,000+ EVACUATED IN ODISHA", x3 + 6, r2_y + 58, DRED, 1)
    fill_rect(x3 + 6, r2_y + 70, cw - 12, 1, LGRAY)

    draw_text("• Severe Cyclonic Storm Akvan bears down.", x3 + 6, r2_y + 78, DARK, 1)
    draw_text("• Gale winds of 110 km/h forecast near coast.", x3 + 6, r2_y + 94, DARK, 1)
    draw_text("• Mass shelters opened in Odisha & Andhra.", x3 + 6, r2_y + 110, DARK, 1)
    draw_text("• Dozens of train routes cancelled by rail.", x3 + 6, r2_y + 126, DARK, 1)
    draw_text("• Third major cyclone in region this month.", x3 + 6, r2_y + 142, DARK, 1)

    fill_rect(M, r2_y + ch2, lw, 2, DARK)
    return r2_y + ch2 + 4


def draw_footer_strip(y0):
    """
    Bottom Wire Banner, Global Data Ticker, Legal Imprint.
    Includes verified dispatches:
      - IAEA reports North Korea Yongbyon enrichment expansion
      - EU delays methane rules to 2029
    """
    fill_rect(0, y0, W, 22, NAVY)
    wire = "* WIRE: IAEA SAYS N. KOREA EXPANDING YONGBYON ENRICHMENT * EU DELAYS METHANE RULES TO 2029 *"
    draw_text_c(wire, y0 + 6, GOLD, 1)
    y0 += 24

    fill_rect(0, y0, W, 28, LTAN)
    fill_rect(0, y0, W, 1, DARK)
    fill_rect(0, y0 + 27, W, 1, DARK)

    draw_text("MARKETS: DOW 42,318 (+0.4%)  S&P 5,891 (+0.3%)  BRENT $78.42  GOLD $2,640", M + 4, y0 + 5, DARK, 1)
    draw_text("WEATHER: NYC 48F CLOUDY | LONDON 9C RAIN | TOKYO 14C CLEAR | DELHI 26C HAZE", M + 4, y0 + 16, DARK, 1)
    y0 += 30

    draw_text_c("COPYRIGHT 2026 THE WORLD GAZETTE PUBLISHING CO. * 1024x1024 EDITION * ALL RIGHTS RESERVED", y0 + 2, GRAY, 1)
    fill_rect(0, H - 4, W, 4, NAVY)


# ───────────────────────── PNG ENCODER ──────────────────────────────────

def encode_png(width, height, pixel_data):
    """Pure stdlib PNG encoder (IHDR, IDAT with Up filter, IEND)."""
    def chunk(tag: bytes, data: bytes) -> bytes:
        c = tag + data
        crc = struct.pack(">I", zlib.crc32(c) & 0xFFFFFFFF)
        return struct.pack(">I", len(data)) + c + crc

    sig = b'\x89PNG\r\n\x1a\n'
    ihdr_data = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    ihdr = chunk(b'IHDR', ihdr_data)

    raw_rows = []
    prev_row = None
    for y in range(height):
        row = bytearray()
        for x in range(width):
            r, g, b = pixel_data[y * width + x]
            row.extend((r, g, b))
        if prev_row is None:
            raw_rows.append(b'\x00' + bytes(row))
        else:
            filtered = bytearray((row[i] - prev_row[i]) & 0xFF for i in range(len(row)))
            raw_rows.append(b'\x02' + bytes(filtered))
        prev_row = row

    compressed = zlib.compress(b''.join(raw_rows), 9)
    idat = chunk(b'IDAT', compressed)
    iend = chunk(b'IEND', b'')

    return sig + ihdr + idat + iend


def create_downscaled_copy(src_pixels, src_w, src_h, dst_w, dst_h):
    """Box-average downscale for visual testing at 300 px."""
    dst = [(0, 0, 0)] * (dst_w * dst_h)
    x_ratio = src_w / dst_w
    y_ratio = src_h / dst_h

    for dy in range(dst_h):
        sy_start = int(dy * y_ratio)
        sy_end = int((dy + 1) * y_ratio)
        for dx in range(dst_w):
            sx_start = int(dx * x_ratio)
            sx_end = int((dx + 1) * x_ratio)

            r_sum = g_sum = b_sum = count = 0
            for sy in range(sy_start, min(src_h, sy_end)):
                for sx in range(sx_start, min(src_w, sx_end)):
                    r, g, b = src_pixels[sy * src_w + sx]
                    r_sum += r; g_sum += g; b_sum += b
                    count += 1
            if count > 0:
                dst[dy * dst_w + dx] = (r_sum // count, g_sum // count, b_sum // count)
    return dst


# ───────────────────────── MAIN EXECUTION ───────────────────────────────

def main():
    draw_masthead()
    draw_date_banner()
    y = draw_three_lead_stories()
    y = draw_section_tagged_grid(y)
    draw_footer_strip(y)

    # 1. Encode & write primary 1024x1024 PNG
    png_bytes = encode_png(W, H, pixels)
    with open(OUT_PATH, 'wb') as f:
        f.write(png_bytes)

    size_kb = len(png_bytes) / 1024
    print(f"Generated {OUT_PATH}: {size_kb:.1f} KiB ({W}x{H})")
    assert size_kb < 1024, f"PNG exceeds 1 MiB limit: {size_kb:.1f} KiB"

    # 2. Encode & write 300x300 downscaled copy to verify legibility
    down_pixels = create_downscaled_copy(pixels, W, H, 300, 300)
    png_300 = encode_png(300, 300, down_pixels)
    with open(OUT_300_PATH, 'wb') as f:
        f.write(png_300)
    print(f"Generated {OUT_300_PATH}: {len(png_300)/1024:.1f} KiB (300x300)")


if __name__ == "__main__":
    main()

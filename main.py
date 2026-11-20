#!/usr/bin/env python3
"""
Deterministic newspaper front-page generator for Thursday 19 November 2026.
Pure Python 3.13 – standard library only.
Outputs a 1024x1024 PNG (< 1 MiB) to $MAKEFUN_OUTPUT_DIR/entry.png
(or /output/entry.png if the env-var is unset).

Custom bitmap font, from-scratch PNG encoder, and hand-drawn icons
covering verified global news stories from November 19, 2026.
Optimized for high legibility at 300 px width with large bold headlines
and concise, high-contrast labels.
"""

import os, struct, zlib, math

# ───────────────────────── OUTPUT PATH ──────────────────────────────────
out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
os.makedirs(out_dir, exist_ok=True)
OUT_PATH = os.path.join(out_dir, "entry.png")

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

M = 16   # side margin

# ───────────────────────── ICON RENDERERS ───────────────────────────────

def icon_scales(cx, cy, sz):
    """Scales of Justice for ICJ Genocide ruling."""
    c = DBLUE
    # Vertical pillar with gold finial
    fill_rect(cx - 3, cy - sz + 10, 7, sz * 2 - 18, c)
    draw_circle(cx, cy - sz + 8, 5, GOLD, fill=True)
    # Tiered base
    fill_rect(cx - sz // 2, cy + sz - 10, sz, 5, c)
    fill_rect(cx - sz // 3, cy + sz - 15, sz * 2 // 3, 5, c)
    # Tilted balance beam
    bw = sz - 10
    fill_rect(cx - bw, cy - sz + 14, bw * 2, 4, c)
    # Left pan (raised: innocence / law)
    lx = cx - bw + 4
    draw_line(lx, cy - sz + 16, lx - 8, cy - 6, c, 1)
    draw_line(lx, cy - sz + 16, lx + 8, cy - 6, c, 1)
    fill_rect(lx - 12, cy - 6, 25, 3, c)
    for a in range(0, 181, 4):
        r = math.radians(a)
        put(int(lx + 12 * math.cos(r)), int(cy - 6 + 6 * math.sin(r)), c)
        put(int(lx + 12 * math.cos(r)), int(cy - 6 + 6 * math.sin(r)) + 1, c)
    # Right pan (weighted down: guilty verdict)
    rx = cx + bw - 4
    draw_line(rx, cy - sz + 16, rx - 8, cy + 14, c, 1)
    draw_line(rx, cy - sz + 16, rx + 8, cy + 14, c, 1)
    fill_rect(rx - 12, cy + 14, 25, 3, c)
    for a in range(0, 181, 4):
        r = math.radians(a)
        put(int(rx + 12 * math.cos(r)), int(cy + 14 + 6 * math.sin(r)), c)
        put(int(rx + 12 * math.cos(r)), int(cy + 14 + 6 * math.sin(r)) + 1, c)
    fill_rect(rx - 5, cy + 10, 11, 4, DRED)


def icon_summit(cx, cy, sz):
    """Trilateral Summit: USA, China, Russia flags over round table."""
    c = DARK
    fw, fh = 14, 10
    fy = cy - sz + 4
    slots = [cx - sz // 2 - 2, cx, cx + sz // 2 + 2]
    # USA flag (left)
    fill_rect(slots[0], fy, 2, fh + 16, c)
    fill_rect(slots[0] + 2, fy, fw, fh // 3, RED)
    fill_rect(slots[0] + 2, fy + fh // 3, fw, fh // 3, WHITE)
    fill_rect(slots[0] + 2, fy + 2 * (fh // 3), fw, fh // 3 + 1, RED)
    fill_rect(slots[0] + 2, fy, fw // 2, fh * 2 // 3, DBLUE)
    # China flag (center)
    fill_rect(slots[1], fy - 2, 2, fh + 18, c)
    fill_rect(slots[1] + 2, fy - 2, fw, fh, RED)
    draw_star(slots[1] + 6, fy + 2, 3, 1, 5, GOLD)
    # Russia flag (right)
    fill_rect(slots[2], fy, 2, fh + 16, c)
    fill_rect(slots[2] + 2, fy, fw, fh // 3, WHITE)
    fill_rect(slots[2] + 2, fy + fh // 3, fw, fh // 3, BLUE)
    fill_rect(slots[2] + 2, fy + 2 * (fh // 3), fw, fh // 3 + 1, RED)
    # Conference Table
    for a in range(0, 360, 2):
        r = math.radians(a)
        for t in range(4):
            put(int(cx + sz * 0.7 * math.cos(r)), int(cy + 12 + sz * 0.22 * math.sin(r)) + t, BROWN)
    # Delegates
    for ox, suit in [(-sz // 2, DBLUE), (0, DRED), (sz // 2, DARK)]:
        hx = cx + ox
        draw_circle(hx, cy - 2, 5, c, fill=True)
        fill_rect(hx - 5, cy + 4, 11, 8, suit)


def icon_capitol(cx, cy, sz):
    """US Capitol Dome with Columns and American Flag."""
    c = DARK
    fill_rect(cx - sz, cy + sz // 4, sz * 2, sz // 3, c)
    num_cols = 5
    for i in range(num_cols):
        col_x = cx - sz + 4 + i * (sz * 2 - 8) // (num_cols - 1)
        fill_rect(col_x - 1, cy - sz // 6, 3, sz // 3 + sz // 6, c)
    draw_tri(cx - sz, cy - sz // 6, cx + sz, cy - sz // 6, cx, cy - sz // 2, c)
    fill_rect(cx - sz * 2 // 5, cy - sz // 2, sz * 4 // 5, 4, c)
    for a in range(0, 181, 2):
        r = math.radians(a)
        for t in range(3):
            put(int(cx + sz * 0.38 * math.cos(r)),
                int(cy - sz // 2 - sz * 0.32 * math.sin(r)) - t, c)
    fill_rect(cx - 1, cy - sz + 2, 2, sz // 3, c)
    fill_rect(cx + 1, cy - sz + 2, 9, 6, RED)
    draw_line(cx + 1, cy - sz + 4, cx + 10, cy - sz + 4, WHITE, 1)


def icon_missile(cx, cy, sz):
    """Ballistic Missile / Defense symbol."""
    c = DRED
    bw = sz // 3
    fill_rect(cx - bw, cy - sz + 12, bw * 2, sz + 2, c)
    draw_tri(cx - bw, cy - sz + 12, cx + bw, cy - sz + 12, cx, cy - sz - 4, c)
    fill_rect(cx - bw, cy - sz // 4, bw * 2, 3, WHITE)
    draw_tri(cx - bw, cy + 12, cx - sz // 2 - 2, cy + 18, cx - bw, cy, c)
    draw_tri(cx + bw, cy + 12, cx + sz // 2 + 2, cy + 18, cx + bw, cy, c)
    draw_tri(cx - bw + 2, cy + 14, cx + bw - 2, cy + 14, cx, cy + sz + 2, ORANGE)
    draw_tri(cx - 2, cy + 15, cx + 2, cy + 15, cx, cy + sz - 5, YELLOW)


def icon_atom(cx, cy, sz):
    """Nuclear / Uranium Centrifuge symbol."""
    c = DARK
    draw_circle(cx, cy, 5, RED, fill=True)
    draw_circle(cx, cy, 3, YELLOW, fill=True)
    for ang in [0, 60, 120]:
        rot = math.radians(ang)
        for a in range(0, 360, 2):
            r = math.radians(a)
            ex, ey = sz * 0.85 * math.cos(r), sz * 0.32 * math.sin(r)
            rx = ex * math.cos(rot) - ey * math.sin(rot)
            ry = ex * math.sin(rot) + ey * math.cos(rot)
            px, py = int(cx + rx), int(cy + ry)
            put(px, py, c); put(px + 1, py, c)
        pa = [40, 160, 280][ang // 60]
        r2 = math.radians(pa)
        ex2, ey2 = sz * 0.85 * math.cos(r2), sz * 0.32 * math.sin(r2)
        rx2 = ex2 * math.cos(rot) - ey2 * math.sin(rot)
        ry2 = ex2 * math.sin(rot) + ey2 * math.cos(rot)
        draw_circle(int(cx + rx2), int(cy + ry2), 3, DBLUE, fill=True)


def icon_voyager(cx, cy, sz):
    """NASA Voyager 1 Interstellar Spacecraft."""
    c = DBLUE
    for a in range(120, 241, 3):
        r = math.radians(a)
        px = int(cx - sz // 4 + sz * 0.45 * math.cos(r))
        py = int(cy + sz * 0.75 * math.sin(r))
        for t in range(3):
            put(px + t, py, c)
    draw_line(cx - sz // 3, cy, cx - sz + 4, cy, c, 2)
    draw_circle(cx - sz + 4, cy, 3, GOLD, fill=True)
    fill_rect(cx - sz // 6, cy - 8, sz // 3, 16, DARK)
    draw_line(cx, cy - 8, cx + sz // 2, cy - sz + 4, c, 2)
    fill_rect(cx + sz // 2 - 2, cy - sz + 2, 8, 5, GOLD)
    draw_line(cx, cy + 8, cx + sz * 3 // 4, cy + sz - 2, c, 2)
    for sx, sy in [(-sz + 2, -sz + 4), (sz - 2, -sz + 8), (-sz + 6, sz - 6), (sz - 4, sz - 8)]:
        draw_star(cx + sx, cy + sy, 4, 1, 4, GOLD)


# ───────────────────────── SECTION DRAWING ──────────────────────────────

def draw_masthead():
    """Top newspaper banner with rich classic typography and ornamentation."""
    fill_rect(0, 0, W, 92, NAVY)
    fill_rect(0, 0, W, 4, GOLD)
    fill_rect(0, 88, W, 4, GOLD)

    draw_star(42, 46, 16, 6, 5, GOLD)
    draw_star(W - 42, 46, 16, 6, 5, GOLD)

    # Main Gazette Title (scale 5 = 30px per char)
    draw_text_c("THE WORLD GAZETTE", 14, WHITE, 5)

    # Tagline
    draw_text_c("INDEPENDENT INTERNATIONAL JOURNALISM  *  FOUNDED 1898", 58, GOLD, 2)


def draw_date_bar():
    """Date bar with date in LARGE bold type."""
    y = 92
    fill_rect(0, y, W, 50, LTAN)
    fill_rect(0, y, W, 2, DARK)
    fill_rect(0, y + 48, W, 2, DARK)

    # Date in LARGE TYPE (scale 3 = 18px per char)
    date_str = "THURSDAY, NOVEMBER 19, 2026"
    draw_text_c(date_str, y + 10, DRED, 3)

    # Metadata
    draw_text("VOL. CXXVIII NO. 44", M + 4, y + 9, GRAY, 1)
    draw_text("THE HAGUE * D.C. * TOKYO", M + 4, y + 23, GRAY, 1)
    draw_text("INTERNATIONAL EDITION", M + 4, y + 35, GRAY, 1)

    draw_text_r("FINAL LATE EDITION", y + 9, GRAY, 1, W - M - 4)
    draw_text_r("PRICE: $3.00 USD", y + 23, GRAY, 1, W - M - 4)
    draw_text_r("PRINTED GLOBALLY", y + 35, GRAY, 1, W - M - 4)


def draw_lead_story():
    """
    Lead Story: ICJ Genocide Verdict against Myanmar.
    Full-width top story with large bold headlines legible at 300px.
    """
    y0 = 146
    lw = W - M * 2
    lh = 276

    fill_rect(M, y0, lw, lh, SBG)
    fill_rect(M, y0, lw, 4, DRED)

    # Region tag badge
    tag = "WORLD COURT: THE HAGUE / MYANMAR"
    ttw = tw(tag, 2) + 16
    fill_rect(M + 8, y0 + 10, ttw, 20, NAVY)
    draw_text(tag, M + 16, y0 + 13, WHITE, 2)

    # Justice Scales Icon
    icon_scales(W - M - 75, y0 + 68, 46)

    # Big Headlines (scale 4 = 24px char, bold & legible at 300px)
    draw_text("ICJ: MYANMAR GUILTY", M + 8, y0 + 38, BLACK, 4)
    draw_text("OF ROHINGYA GENOCIDE", M + 8, y0 + 74, BLACK, 4)

    # Subheadline (scale 2)
    draw_text("HISTORIC 9-6 RULING: FIRST SOVEREIGN STATE CONVICTED BY WORLD COURT", M + 8, y0 + 114, DRED, 2)

    # Divider rule
    fill_rect(M + 8, y0 + 134, lw - 16, 1, LGRAY)

    # Two-column story labels (scale 2, comfortably fitting within columns)
    col_w = (lw - 40) // 2
    c1_x = M + 8
    c2_x = M + 8 + col_w + 24

    draw_text("• UN COURT FINDS MYANMAR VIOLATED", c1_x, y0 + 144, DARK, 2)
    draw_text("  1948 GENOCIDE CONVENTION IN 9-6 VOTE", c1_x, y0 + 164, DARK, 2)
    draw_text("• SYSTEMATIC ATROCITIES IN RAKHINE", c1_x, y0 + 188, DARK, 2)
    draw_text("  PROVE DIRECT STATE GENOCIDAL INTENT", c1_x, y0 + 208, DARK, 2)
    draw_text("• DECISION BREAKS 80-YEAR PRECEDENT", c1_x, y0 + 232, DARK, 2)

    draw_text("• MYANMAR ORDERED TO COMPENSATE", c2_x, y0 + 144, DARK, 2)
    draw_text("  ROHINGYA SURVIVORS WITHIN 2 YEARS", c2_x, y0 + 164, DARK, 2)
    draw_text("• JUNTA DEFENSE REJECTED BY JUDGES;", c2_x, y0 + 188, DARK, 2)
    draw_text("  RIGHTS GROUPS HAIL HISTORIC RULING", c2_x, y0 + 208, DARK, 2)
    draw_text("• GLOBAL ACCOUNTABILITY BENCHMARK SET", c2_x, y0 + 232, DARK, 2)

    # Vertical column separator
    fill_rect(c1_x + col_w + 11, y0 + 140, 1, 114, LGRAY)

    # Bottom border
    fill_rect(M, y0 + lh, lw, 2, DARK)
    return y0 + lh + 4


def draw_mid_row(y0):
    """
    Middle Row: Two major international political stories.
    Left: Trump-Xi-Putin Trilateral Summit.
    Right: US Senate Iran War Powers Rejection.
    """
    card_w = (W - M * 2 - 12) // 2
    card_h = 276

    # ──── STORY 2: TRILATERAL SUMMIT ────
    x1 = M
    fill_rect(x1, y0, card_w, card_h, SBG)
    fill_rect(x1, y0, card_w, 3, DRED)

    tag1 = "DIPLOMACY: APEC / SHENZHEN"
    fill_rect(x1 + 8, y0 + 8, tw(tag1, 1) + 10, 13, NAVY)
    draw_text(tag1, x1 + 13, y0 + 11, WHITE, 1)

    icon_summit(x1 + card_w - 52, y0 + 44, 32)

    draw_text("TRUMP, XI & PUTIN", x1 + 8, y0 + 28, BLACK, 3)
    draw_text("IN HISTORIC SUMMIT", x1 + 8, y0 + 54, BLACK, 3)

    draw_text("LEADERS SIGN JOINT DECLARATION AT APEC", x1 + 8, y0 + 84, DRED, 2)
    fill_rect(x1 + 8, y0 + 104, card_w - 16, 1, LGRAY)

    draw_text("• UNPRECEDENTED 80-MIN TRILATERAL", x1 + 8, y0 + 114, DARK, 2)
    draw_text("  MEETING AT KYLIN VILLA IN SHENZHEN", x1 + 8, y0 + 134, DARK, 2)
    draw_text("• SIGNED JOINT STATEMENT REAFFIRMS:", x1 + 8, y0 + 158, DARK, 2)
    draw_text("  NUCLEAR WAR CANNOT BE WON OR FOUGHT", x1 + 8, y0 + 178, DARK, 2)
    draw_text("• ACCORD TOUCHES OIL FLOWS & UN REFORM", x1 + 8, y0 + 202, DARK, 2)
    draw_text("• ALLIES CONCERNED ON GREAT-POWER PACT", x1 + 8, y0 + 226, DARK, 2)

    # ──── STORY 3: SENATE WAR POWERS ────
    x2 = M + card_w + 12
    fill_rect(x2, y0, card_w, card_h, SBG)
    fill_rect(x2, y0, card_w, 3, DRED)

    tag2 = "CONGRESS: WASHINGTON, D.C."
    fill_rect(x2 + 8, y0 + 8, tw(tag2, 1) + 10, 13, NAVY)
    draw_text(tag2, x2 + 13, y0 + 11, WHITE, 1)

    icon_capitol(x2 + card_w - 52, y0 + 44, 32)

    draw_text("SENATE REJECTS", x2 + 8, y0 + 28, BLACK, 3)
    draw_text("IRAN WAR LIMITS", x2 + 8, y0 + 54, BLACK, 3)

    draw_text("51-48 VOTE BACKS PRESIDENTIAL AUTHORITY", x2 + 8, y0 + 84, DRED, 2)
    fill_rect(x2 + 8, y0 + 104, card_w - 16, 1, LGRAY)

    draw_text("• HOUSE WAR POWERS MEASURE DEFEATED", x2 + 8, y0 + 114, DARK, 2)
    draw_text("  IN KEY POST-MIDTERMS TEST VOTE", x2 + 8, y0 + 134, DARK, 2)
    draw_text("• GOP SENATORS COLLINS, MURKOWSKI", x2 + 8, y0 + 158, DARK, 2)
    draw_text("  AND RAND PAUL BREAK PARTY RANKS", x2 + 8, y0 + 178, DARK, 2)
    draw_text("• FETTERMAN SOLE DEMOCRAT DISSENTING", x2 + 8, y0 + 202, DARK, 2)
    draw_text("• PENTAGON SAYS WAR SPENDING TOPS $48B", x2 + 8, y0 + 226, DARK, 2)

    fill_rect(M, y0 + card_h, W - M * 2, 2, DARK)
    return y0 + card_h + 4


def draw_bot_row(y0):
    """
    Bottom Row: Three stories across different fields.
    Left: Middle East strikes (Military/Geopolitics).
    Center: IAEA Yongbyon expansion (Nuclear/Asia).
    Right: Voyager 1 one light-day milestone (Space/Science).
    """
    card_w = (W - M * 2 - 20) // 3
    card_h = 230

    # ──── STORY 4: HODEIDAH STRIKES ────
    x1 = M
    fill_rect(x1, y0, card_w, card_h, SBG)
    fill_rect(x1, y0, card_w, 3, DRED)

    tag1 = "MIDDLE EAST | YEMEN"
    fill_rect(x1 + 6, y0 + 6, tw(tag1, 1) + 8, 12, NAVY)
    draw_text(tag1, x1 + 10, y0 + 8, WHITE, 1)

    icon_missile(x1 + card_w - 38, y0 + 38, 24)

    draw_text("COALITION HITS", x1 + 6, y0 + 24, BLACK, 2)
    draw_text("HODEIDAH PORT", x1 + 6, y0 + 42, BLACK, 2)
    draw_text("HOUTHIS THREATEN RIYADH & JEDDAH", x1 + 6, y0 + 60, DRED, 1)
    fill_rect(x1 + 6, y0 + 72, card_w - 12, 1, LGRAY)

    draw_text("• Saudi jets strike Red Sea port of", x1 + 6, y0 + 80, DARK, 1)
    draw_text("  Hodeidah and missile workshops.", x1 + 6, y0 + 94, DARK, 1)
    draw_text("• Houthis warn Saudi commercial", x1 + 6, y0 + 110, DARK, 1)
    draw_text("  airspace is unsafe for airlines.", x1 + 6, y0 + 124, DARK, 1)
    draw_text("• Threats made on Riyadh financial", x1 + 6, y0 + 140, DARK, 1)
    draw_text("  district and oil power plants.", x1 + 6, y0 + 154, DARK, 1)
    draw_text("• UN sounds alarm on food supply.", x1 + 6, y0 + 170, DARK, 1)
    draw_text("• GCC condemns cross-border attacks.", x1 + 6, y0 + 184, DARK, 1)

    # ──── STORY 5: IAEA NORTH KOREA ────
    x2 = M + card_w + 10
    fill_rect(x2, y0, card_w, card_h, SBG)
    fill_rect(x2, y0, card_w, 3, DRED)

    tag2 = "SECURITY | NORTH KOREA"
    fill_rect(x2 + 6, y0 + 6, tw(tag2, 1) + 8, 12, NAVY)
    draw_text(tag2, x2 + 10, y0 + 8, WHITE, 1)

    icon_atom(x2 + card_w - 38, y0 + 38, 24)

    draw_text("IAEA: N. KOREA", x2 + 6, y0 + 24, BLACK, 2)
    draw_text("EXPANDS YONGBYON", x2 + 6, y0 + 42, BLACK, 2)
    draw_text("URANIUM ENRICHMENT EXTENSION", x2 + 6, y0 + 60, DRED, 1)
    fill_rect(x2 + 6, y0 + 72, card_w - 12, 1, LGRAY)

    draw_text("• IAEA Chief Grossi reports new", x2 + 6, y0 + 80, DARK, 1)
    draw_text("  extension at Yongbyon site.", x2 + 6, y0 + 94, DARK, 1)
    draw_text("• Centrifuge facility structure", x2 + 6, y0 + 110, DARK, 1)
    draw_text("  externally completed in Oct.", x2 + 6, y0 + 124, DARK, 1)
    draw_text("• 5-megawatt reactor operates in", x2 + 6, y0 + 140, DARK, 1)
    draw_text("  seventh cycle for plutonium.", x2 + 6, y0 + 154, DARK, 1)
    draw_text("• Light-water reactor active;", x2 + 6, y0 + 170, DARK, 1)
    draw_text("  UN Security resolutions breached.", x2 + 6, y0 + 184, DARK, 1)

    # ──── STORY 6: VOYAGER 1 ────
    x3 = M + (card_w + 10) * 2
    fill_rect(x3, y0, card_w, card_h, SBG)
    fill_rect(x3, y0, card_w, 3, DRED)

    tag3 = "SCIENCE | DEEP SPACE"
    fill_rect(x3 + 6, y0 + 6, tw(tag3, 1) + 8, 12, NAVY)
    draw_text(tag3, x3 + 10, y0 + 8, WHITE, 1)

    icon_voyager(x3 + card_w - 38, y0 + 38, 24)

    draw_text("VOYAGER 1 PASSES", x3 + 6, y0 + 24, BLACK, 2)
    draw_text("ONE LIGHT-DAY", x3 + 6, y0 + 42, BLACK, 2)
    draw_text("16.1 BILLION MILES FROM EARTH", x3 + 6, y0 + 60, DRED, 1)
    fill_rect(x3 + 6, y0 + 72, card_w - 12, 1, LGRAY)

    draw_text("• NASA confirms Voyager 1 crossed", x3 + 6, y0 + 80, DARK, 1)
    draw_text("  historic one light-day mark.", x3 + 6, y0 + 94, DARK, 1)
    draw_text("• Distance reaches 25.9B km, or", x3 + 6, y0 + 110, DARK, 1)
    draw_text("  173 Astronomical Units away.", x3 + 6, y0 + 124, DARK, 1)
    draw_text("• Radio signals require exactly", x3 + 6, y0 + 140, DARK, 1)
    draw_text("  24 hours each direction.", x3 + 6, y0 + 154, DARK, 1)
    draw_text("• 49-year journey since 1977;", x3 + 6, y0 + 170, DARK, 1)
    draw_text("  farthest human-made explorer.", x3 + 6, y0 + 184, DARK, 1)

    fill_rect(M, y0 + card_h, W - M * 2, 2, DARK)
    return y0 + card_h + 4


def draw_footer(y0):
    """Bottom Gazette information panels, markets, weather, and legal imprint."""
    # Motto banner
    fill_rect(0, y0, W, 22, NAVY)
    draw_text_c("* INDEPENDENT * IMPARTIAL * OBJECTIVE GLOBAL RECORD *", y0 + 4, GOLD, 2)
    y0 += 26

    # 3 Summary panels
    bw = (W - M * 2 - 16) // 3
    bh = 46

    # Panel 1: World Weather
    b1_x = M
    fill_rect(b1_x, y0, bw, bh, SBG)
    fill_rect(b1_x, y0, bw, 2, DBLUE)
    draw_text("WORLD WEATHER", b1_x + 6, y0 + 4, NAVY, 2)
    draw_text("NEW YORK: 48F CLOUDY  |  LONDON: 9C RAIN", b1_x + 6, y0 + 20, DARK, 1)
    draw_text("TOKYO: 14C SUNNY      |  GENEVA: 6C CLEAR", b1_x + 6, y0 + 32, DARK, 1)

    # Panel 2: Markets
    b2_x = M + bw + 8
    fill_rect(b2_x, y0, bw, bh, SBG)
    fill_rect(b2_x, y0, bw, 2, DBLUE)
    draw_text("FINANCIAL MARKETS", b2_x + 6, y0 + 4, NAVY, 2)
    draw_text("DOW JONES: 42,318 (+0.4%) | S&P 500: 5,891", b2_x + 6, y0 + 20, DARK, 1)
    draw_text("BRENT CRUDE: $78.42/BBL    | GOLD: $2,640", b2_x + 6, y0 + 32, DARK, 1)

    # Panel 3: Inside Today
    b3_x = M + (bw + 8) * 2
    fill_rect(b3_x, y0, bw, bh, SBG)
    fill_rect(b3_x, y0, bw, 2, DBLUE)
    draw_text("INSIDE THIS ISSUE", b3_x + 6, y0 + 4, NAVY, 2)
    draw_text("APEC SUMMIT PAPERS...A2-A5 | ICJ FULL TEXT...A6-A8", b3_x + 6, y0 + 20, DARK, 1)
    draw_text("MIDTERM ANALYSIS....A9-A11 | SCIENCE & TECH....B1-B4", b3_x + 6, y0 + 32, DARK, 1)

    y0 += bh + 6

    # Imprint
    fill_rect(0, y0, W, 2, DARK)
    draw_text_c("COPYRIGHT 2026 THE WORLD GAZETTE PUBLISHING GROUP. ALL RIGHTS RESERVED.", y0 + 4, GRAY, 1)

    # Bottom edge rule
    fill_rect(0, H - 4, W, 4, NAVY)


# ───────────────────────── PNG ENCODER ──────────────────────────────────

def encode_png(width, height, pixel_data):
    """
    Pure Python PNG encoder (IHDR, IDAT with zlib, IEND).
    Standard library only.
    """
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


# ───────────────────────── MAIN EXECUTION ───────────────────────────────

def main():
    draw_masthead()
    draw_date_bar()
    y = draw_lead_story()
    y = draw_mid_row(y)
    y = draw_bot_row(y)
    draw_footer(y)

    png_bytes = encode_png(W, H, pixels)
    with open(OUT_PATH, 'wb') as f:
        f.write(png_bytes)

    size_kb = len(png_bytes) / 1024
    print(f"Generated {OUT_PATH}: {size_kb:.1f} KiB ({W}x{H})")
    assert size_kb < 1024, f"PNG exceeds 1 MiB limit: {size_kb:.1f} KiB"


if __name__ == "__main__":
    main()

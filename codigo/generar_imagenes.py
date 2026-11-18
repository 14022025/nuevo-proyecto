"""
Genera las imágenes "realistas" de la invitación (versión verde y crema):
  python3 generar_imagenes.py seal     -> assets/seal_real_wine.png  (sello de cera vino con la K)
  python3 generar_imagenes.py emboss   -> fondos de papel con relieve (marco verde, esquinas con flores, crema liso)
  python3 generar_imagenes.py env      -> sobre verde con encaje (no se usa en la versión final, queda como extra)
Requiere: pip install numpy scipy pillow
"""
import math, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from scipy import ndimage as ndi

import os
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "assets") + "/"
rng = np.random.default_rng(11)
F32 = np.float32
LIGHT = np.array([-0.55, -0.7, 0.75], F32); LIGHT /= np.linalg.norm(LIGHT)


def shade(h, albedo, amb=0.42, ks=0.0, shin=30, ks2=0.0, shin2=6):
    gy, gx = np.gradient(h.astype(F32))
    l = np.sqrt(gx * gx + gy * gy + 1)
    nx, ny, nz = -gx / l, -gy / l, 1 / l
    diff = np.clip(nx * LIGHT[0] + ny * LIGHT[1] + nz * LIGHT[2], 0, 1) / LIGHT[2]
    out = albedo * (amb + (1 - amb) * diff)[..., None]
    if ks or ks2:
        Hv = LIGHT + np.array([0, 0, 1], F32); Hv /= np.linalg.norm(Hv)
        nh = np.clip(nx * Hv[0] + ny * Hv[1] + nz * Hv[2], 0, 1)
        out = out + (ks * 255 * nh ** shin + ks2 * 255 * nh ** shin2)[..., None]
    return np.clip(out, 0, 255)


def smooth_noise(shape, sigma, amp):
    n = rng.standard_normal(shape).astype(F32)
    n = ndi.gaussian_filter(n, sigma)
    return n / (n.std() + 1e-6) * amp


def mask_from(shape, draw_fn):
    m = Image.new("L", (shape[1], shape[0]), 0)
    draw_fn(ImageDraw.Draw(m))
    return np.array(m) > 127


def dome(mask, height, soft, power=0.6):
    if not mask.any():
        return np.zeros(mask.shape, F32)
    dt = ndi.distance_transform_edt(mask).astype(F32)
    return height * np.clip(dt / soft, 0, 1) ** power


def ell(cx, cy, a, b, ang, n=48):
    ca, sa = math.cos(ang), math.sin(ang)
    return [(cx + a * math.cos(t) * ca - b * math.sin(t) * sa, cy + a * math.cos(t) * sa + b * math.sin(t) * ca)
            for t in np.linspace(0, 2 * math.pi, n, endpoint=False)]


def leaf_poly(x, y, ang, L, w, n=30):
    pts = [(L * t / math.pi, w * math.sin(t) ** 0.9) for t in np.linspace(0, math.pi, n)]
    pts += [(L * t / math.pi, -w * math.sin(t) ** 0.9) for t in np.linspace(math.pi, 0, n)]
    ca, sa = math.cos(ang), math.sin(ang)
    return [(x + px * ca - py * sa, y + px * sa + py * ca) for px, py in pts]


# ------------------------------------------------------------------ WAX SEAL
def wax_seal(color, letters, name, S=1400, fscale=0.12):
    yy, xx = np.mgrid[0:S, 0:S].astype(F32)
    cx = cy = S / 2
    ang = np.arctan2(yy - cy, xx - cx)
    rx, ry = 0.355 * S, 0.43 * S
    k = np.arange(2, 30)
    amps = 0.05 / k ** 1.05 * rng.uniform(0.4, 1.2, len(k)); phs = rng.uniform(0, 6.3, len(k))
    pert = 1 + sum(a * np.sin(kk * ang + p) for a, kk, p in zip(amps, k, phs)).astype(F32)
    r = np.sqrt(((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2) / pert
    d_p = (1 - r) * min(rx, ry)
    h = 40 * np.clip(d_p / 55, 0, 1) ** 0.55

    srx, sry = 0.25 * S, 0.325 * S
    rs = np.sqrt(((xx - cx) / srx) ** 2 + ((yy - cy) / sry) ** 2)
    d_s = (rs - 1) * min(srx, sry)  # <0 inside stamp
    h = h + 20 * np.exp(-((d_s - 16) / 20) ** 2) * (d_p > 0)
    blend = np.clip(-d_s / 7, 0, 1)
    field = 16.0

    rel = np.zeros((S, S), F32)
    rel = np.maximum(rel, 8 * np.exp(-((d_s + 20) / 4.5) ** 2))  # inner border line
    # beaded ring
    dots = mask_from((S, S), lambda d: [d.ellipse([cx + (srx - 40) * math.cos(t) - 7, cy + (sry - 40) * math.sin(t) - 7,
                                                   cx + (srx - 40) * math.cos(t) + 7, cy + (sry - 40) * math.sin(t) + 7], fill=255)
                                        for t in np.linspace(0, 2 * math.pi, 64, endpoint=False)])
    rel = np.maximum(rel, dome(dots, 7, 6))

    # rose sprig (upper half)
    fx, fy = cx, cy - 0.15 * S
    k = 1.25
    def cup(d):
        pts = [(fx + 64 * k * math.cos(t), fy + 72 * k * math.sin(t)) for t in np.linspace(0, math.pi, 40)]
        pts += [(fx - 64 * k + 32 * k * i / 10, fy - 6 * k + 18 * k * math.sin(math.pi * i / 20)) for i in range(11)]
        pts += [(fx + 32 * k * i / 10 - 0 * k, fy + 12 * k - 18 * k * i / 10 * 0.9) for i in range(11)]
        d.polygon(pts, fill=255)
    parts = [
        lambda d: d.polygon(ell(fx, fy - 30 * k, 46 * k, 36 * k, 0), fill=255),
        lambda d: d.polygon(ell(fx - 40 * k, fy - 8 * k, 50 * k, 32 * k, -0.95), fill=255),
        lambda d: d.polygon(ell(fx + 40 * k, fy - 8 * k, 50 * k, 32 * k, 0.95), fill=255),
        lambda d: d.polygon(ell(fx + 2 * k, fy - 18 * k, 22 * k, 16 * k, 0.3), fill=255),
        cup,
        lambda d: d.line([(fx, fy + 70 * k), (fx + 8, fy + 150 * k), (fx - 2, fy + 220 * k)], width=13, fill=255, joint="curve"),
        lambda d: d.polygon(leaf_poly(fx + 5, fy + 125 * k, -0.6, 105 * k, 27 * k), fill=255),
        lambda d: d.polygon(leaf_poly(fx + 2, fy + 168 * k, math.pi + 0.55, 100 * k, 26 * k), fill=255),
    ]
    for p in parts:
        rel = np.maximum(rel, dome(mask_from((S, S), p), 12, 10))
    # letters
    font = ImageFont.truetype(os.path.join(HERE, "fuentes", "CormorantGaramond-Bold.ttf"), int(fscale * S))
    def draw_letters(d):
        bb = d.textbbox((0, 0), letters, font=font)
        d.text((cx - (bb[2] + bb[0]) / 2, cy + 0.185 * S - (bb[3] + bb[1]) / 2), letters, font=font, fill=255)
    rel = np.maximum(rel, dome(mask_from((S, S), draw_letters), 10, 4.5))
    rel = ndi.gaussian_filter(rel, 1.4)

    h = h * (1 - blend) + (field + rel) * blend
    h += smooth_noise((S, S), 6, 0.12) + smooth_noise((S, S), 45, 2.0)
    alpha = np.clip(d_p / 2 + 0.5, 0, 1)

    alb = np.ones((S, S, 3), F32) * np.array(color, F32)
    alb *= (1 + 0.06 * np.tanh(smooth_noise((S, S), 30, 1)))[..., None]
    alb *= (1 + 0.18 * np.clip(1 - d_p / 30, 0, 1))[..., None]  # thin translucent edge
    alb *= (1 - 0.08 * blend)[..., None]
    rgb = shade(h, alb, amb=0.30, ks=0.45, shin=70, ks2=0.05, shin2=6)

    # drop shadow
    pad = 0
    sh = ndi.gaussian_filter(np.roll(np.roll(alpha, 18, 0), 11, 1), 16) * 0.55
    out = np.zeros((S, S, 4), F32)
    a = alpha + sh * (1 - alpha)
    out[..., :3] = np.where(a[..., None] > 0, rgb * (alpha / np.maximum(a, 1e-6))[..., None], 0)
    out[..., 3] = a * 255
    img = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), "RGBA")
    img = img.crop(img.getbbox())
    img = img.resize((img.width // 2, img.height // 2), Image.LANCZOS)
    img.save(OUT + name)
    print("seal", img.size)


if __name__ == "__main__" and "seal" in sys.argv:
    wax_seal((104, 16, 30), "K", "seal_real_wine.png", fscale=0.17)


# ------------------------------------------------------------------ PAPER
def paper_rgb(base, w, h, crumple=1.0, mottle=10, grain=6):
    alb = np.ones((h, w, 3), F32) * np.array(base, F32)
    alb *= (1 + smooth_noise((h, w), 50, 0.035 * mottle / 10))[..., None]
    alb += (rng.standard_normal((h, w)).astype(F32) * grain * 0.5)[..., None]
    # fibres
    fib = ndi.gaussian_filter(rng.standard_normal((h, w)).astype(F32), (0.6, 5))
    alb *= (1 + 0.025 * fib / fib.std())[..., None]
    ht = (smooth_noise((h, w), 160, 14) + smooth_noise((h, w), 40, 1.6) + smooth_noise((h, w), 6, 0.25)) * crumple
    return shade(ht, alb, amb=0.55)


# ------------------------------------------------------------------ LACE
def lace_strip(L, P=104):
    Hs = 250
    hgt = np.zeros((Hs, L), F32)
    def add(mask, h, soft=2.0):
        nonlocal hgt
        hgt = np.maximum(hgt, dome(mask, h, soft, 0.7))
    yy, xx = np.mgrid[0:Hs, 0:L].astype(F32)
    # header: solid woven band with eyelets
    band = (yy > 10) & (yy < 40)
    eyelets = mask_from((Hs, L), lambda d: [d.ellipse([x - 5, 20, x + 5, 30], fill=255) for x in range(8, L, 17)])
    add(band & ~eyelets, 3.0, 3)
    add(np.abs(yy - 9) < 3.5, 4.2, 3)
    add(np.abs(yy - 41) < 2.6, 3.6, 2.5)
    # net (diagonal mesh)
    sp = 13.0
    net = (((xx + yy) % sp) < 2.6) | (((xx - yy) % sp) < 2.6)
    netzone = (yy >= 41) & (yy < 156)
    add(net & netzone, 1.8, 1.2)
    # motifs + scallops
    def motifs(d):
        for k in range(-1, L // P + 2):
            x = k * P + P / 2
            for i in range(6):
                a = i * math.pi / 3 + 0.26
                d.polygon(ell(x + 15 * math.cos(a), 98 + 15 * math.sin(a), 15, 7.5, a), fill=255)
            d.ellipse([x - 7, 91, x + 7, 105], fill=255)
            xl = k * P
            d.polygon(leaf_poly(xl, 74, -0.9, 30, 8), fill=255)
            d.polygon(leaf_poly(xl, 74, math.pi + 0.9, 30, 8), fill=255)
            d.ellipse([xl - 5, 118, xl + 5, 128], fill=255)
    add(mask_from((Hs, L), motifs), 3.4, 2.6)
    holes = mask_from((Hs, L), lambda d: [d.ellipse([k * P + P / 2 - 3, 95, k * P + P / 2 + 3, 101], fill=255) for k in range(-1, L // P + 2)])
    hgt[holes] = 0
    add(np.abs(yy - 156) < 3, 3.6, 2.5)
    # scallops: semicircle bands hanging below y=156
    cxs = (np.floor(xx / P) * P + P / 2)
    rr = np.sqrt((xx - cxs) ** 2 + (yy - 156) ** 2)
    below = yy >= 156
    add(below & (rr > 36) & (rr < 50), 3.2, 3)
    fan_ang = np.arctan2(yy - 156, xx - cxs)
    fan = below & (rr < 36) & (rr > 9) & ((np.abs(((fan_ang * 180 / math.pi) % 15) - 7.5) < 1.7))
    add(fan, 2.0, 1.2)
    add(below & (rr < 9), 2.6, 2)
    # picots
    def pic(d):
        for k in range(-1, L // P + 2):
            c = k * P + P / 2
            for a in np.linspace(math.radians(8), math.radians(172), 11):
                px, py = c + 55 * math.cos(a), 156 + 55 * math.sin(a)
                d.ellipse([px - 5, py - 5, px + 5, py + 5], fill=255)
    add(mask_from((Hs, L), pic), 2.8, 2.5)
    # woven texture on solids
    weave = 1 + 0.18 * np.sin(xx * 1.9) * np.sin(yy * 1.9)
    hgt = hgt * weave
    hgt = ndi.gaussian_filter(hgt, 0.7)
    alpha = np.clip(hgt / 0.6, 0, 1)
    return hgt, alpha


def place_strip(canvas_hw, strip_h, strip_a, p0, p1, voff):
    """Map a horizontal strip so its row `voff` lies on segment p0->p1 (strip x=0 at p0)."""
    H, W = canvas_hw
    th = math.atan2(p1[1] - p0[1], p1[0] - p0[0])
    c, s = math.cos(th), math.sin(th)
    x0, y0 = p0
    data = (c, s, -(x0 * c + y0 * s), -s, c, x0 * s - y0 * c + voff)
    out = []
    for arr in (strip_h, strip_a):
        im = Image.fromarray(arr.astype(F32), "F")
        out.append(np.array(im.transform((W, H), Image.AFFINE, data, resample=Image.BILINEAR), F32))
    return out


def envelope(base, lace_col, name, W=2160, H=3840):
    rgb = paper_rgb(base, W, H, crumple=0.9)
    apex = (W / 2, H * 0.47)
    # body flaps (shading) & flap with shadow
    def poly_mask(pts):
        return mask_from((H, W), lambda d: d.polygon(pts, fill=255)).astype(F32)
    left = poly_mask([(0, H * 0.30), (W / 2, H * 0.63), (0, H)])
    right = poly_mask([(W, H * 0.30), (W / 2, H * 0.63), (W, H)])
    bottom = poly_mask([(0, H), (W / 2, H * 0.63), (W, H)])
    rgb *= (1 - 0.07 * ndi.gaussian_filter(left + right, 1.5))[..., None]
    rgb *= (1 + 0.03 * ndi.gaussian_filter(bottom, 1.5))[..., None]
    # crease highlight/shadow lines along flap folds
    for a, b in (((0, H * 0.30), (W / 2, H * 0.63)), ((W, H * 0.30), (W / 2, H * 0.63))):
        ln = mask_from((H, W), lambda d: d.line([a, b], fill=255, width=3)).astype(F32)
        rgb *= (1 - 0.10 * ndi.gaussian_filter(ln, 2))[..., None]
    flap_pts = [(0, 0), (W, 0), (W, H * 0.12), apex, (0, H * 0.12)]
    flap = poly_mask(flap_pts)
    sh = ndi.gaussian_filter(np.roll(flap, 26, 0), 26)
    rgb *= (1 - 0.38 * sh * (1 - flap))[..., None]
    flap_rgb = paper_rgb(tuple(min(255, c * 1.035) for c in base), W, H, crumple=0.9)
    fa = ndi.gaussian_filter(flap, 1.0)[..., None]
    rgb = rgb * (1 - fa) + flap_rgb * fa
    # lace along flap edges
    L = int(math.hypot(W / 2, H * 0.47 - H * 0.12)) + 400
    sh_, sa_ = lace_strip(int(L / 1.5))
    sh_ = ndi.zoom(sh_, 1.5, order=1) * 1.2; sa_ = np.clip(ndi.zoom(sa_, 1.5, order=1), 0, 1)
    hL, aL = place_strip((H, W), sh_, sa_, (-220 * math.cos(math.atan2(H * 0.35, W / 2)), H * 0.12 - 220 * math.sin(math.atan2(H * 0.35, W / 2))), apex, 60)
    # right strip: from apex going up-right; build from right side mirrored direction
    ang = math.atan2(H * 0.12 - H * 0.47, W / 2)
    hR, aR = place_strip((H, W), sh_, sa_, (apex[0] - 160 * math.cos(ang), apex[1] - 160 * math.sin(ang)), (W, H * 0.12), 60)
    hl = np.maximum(hL, hR); al = np.maximum(aL, aR)
    shadow = ndi.gaussian_filter(np.roll(np.roll(al, 12, 0), 7, 1), 7)
    rgb *= (1 - 0.45 * shadow * (1 - al))[..., None]
    lalb = np.ones((H, W, 3), F32) * np.array(lace_col, F32)
    lalb *= (1 + smooth_noise((H, W), 1.2, 0.04))[..., None]
    lrgb = shade(hl * 1.3, lalb, amb=0.5, ks=0.06, shin=12)
    rgb = rgb * (1 - al[..., None]) + lrgb * al[..., None]
    Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8)).resize((W // 2, H // 2), Image.LANCZOS).save(OUT + name)
    print("envelope", name)


if __name__ == "__main__" and "env" in sys.argv:
    envelope((108, 120, 70), (238, 229, 210), "envelope_real_green.png")


# ------------------------------------------------------------------ EMBOSS
def floral_cluster(C=820):
    """height map of a corner floral cluster, corner at (0,0)"""
    h = np.zeros((C, C), F32)
    def add(fn, ht, soft, power=0.55):
        nonlocal h
        h = np.maximum(h, dome(mask_from((C, C), fn), ht, soft, power))
    # stems
    add(lambda d: d.line([(230, 230), (300, 160), (470, 140), (640, 95)], fill=255, width=10, joint="curve"), 7, 5)
    add(lambda d: d.line([(230, 230), (160, 300), (140, 470), (95, 640)], fill=255, width=10, joint="curve"), 7, 5)
    # leaves
    for (x, y, a) in ((330, 150, -0.9), (420, 150, 0.7), (560, 125, -1.2), (150, 330, math.pi / 2 + 0.9),
                      (150, 420, math.pi / 2 - 0.7), (125, 560, math.pi / 2 + 1.2), (250, 140, 0.9), (140, 250, math.pi / 2 - 0.9)):
        add(lambda d, x=x, y=y, a=a: d.polygon(leaf_poly(x, y, a, 95, 26), fill=255), 11, 12)
    # flowers: 5 petals each dome separately -> seams
    def flower(fx, fy, R, rot):
        nonlocal h
        for i in range(5):
            a = rot + i * 2 * math.pi / 5
            add(lambda d, a=a: d.polygon(ell(fx + R * 0.55 * math.cos(a), fy + R * 0.55 * math.sin(a), R * 0.55, R * 0.36, a), fill=255), 13, R * 0.22)
        add(lambda d: d.ellipse([fx - R * 0.22, fy - R * 0.22, fx + R * 0.22, fy + R * 0.22], fill=255), 17, R * 0.12, 0.8)
    flower(230, 230, 120, 0.3)
    flower(470, 105, 78, 0.9)
    flower(105, 470, 78, 0.1)
    flower(650, 90, 50, 0.5)
    flower(90, 650, 50, 1.1)
    for (x, y) in ((360, 70), (70, 360), (330, 310)):
        add(lambda d, x=x, y=y: d.ellipse([x - 22, y - 22, x + 22, y + 22], fill=255), 12, 10, 0.7)
    # fade the far edge of the crop to avoid hard cut
    return ndi.gaussian_filter(h, 2.2)


def box_frame_height(W, H, inset, band, small_P=46, big_n=(3, 5)):
    yy, xx = np.mgrid[0:H, 0:W].astype(F32)
    x0, y0, x1, y1 = inset, inset, W - inset, H - inset
    dl, dr, dt_, db = xx - x0, x1 - xx, yy - y0, y1 - yy
    dmin = np.minimum(np.minimum(dl, dr), np.minimum(dt_, db))
    horiz = np.minimum(dt_, db) <= np.minimum(dl, dr)
    s_small = np.where(horiz, (xx - x0) / small_P, (yy - y0) / small_P)
    s_big = np.where(horiz, (xx - x0) / (x1 - x0) * big_n[0], (yy - y0) / (y1 - y0) * big_n[1])
    bump_s = np.abs(np.sin(math.pi * s_small))
    bump_b = np.abs(np.sin(math.pi * s_big))
    d_out = dmin + 12 * bump_s           # outer scalloped line at d_out==0
    d_in = dmin - (band + 70 * bump_b)  # inner wave line at d_in==0
    h = np.zeros((H, W), F32)
    h = np.maximum(h, 9 * np.exp(-((d_out - 6) / 6) ** 2))
    h = np.maximum(h, 10 * np.exp(-(d_in / 6.5) ** 2))
    h = np.maximum(h, 5 * np.exp(-((d_in - 22) / 3) ** 2))
    zone = (d_out > 14) & (d_in < -10)
    net = ((((xx + yy) % 18) < 3.2) | (((xx - yy) % 18) < 3.2)) & zone
    h = np.maximum(h, 3.2 * net.astype(F32))
    h = np.maximum(h, 2.0 * zone.astype(F32))  # raised band plate
    # picot dots on inner side
    return ndi.gaussian_filter(h, 1.6)


def emboss_page(base, name, frame=True, crumple=0.25, mottle=2, corners=("tl", "tr", "bl", "br"), cluster_scale=1.0, W=2160, H=3840, strength=1.0):
    alb_rgb = paper_rgb(base, W, H, crumple=crumple, mottle=mottle)
    h = box_frame_height(W, H, 110, 120) if frame else np.zeros((H, W), F32)
    cl = floral_cluster()
    if cluster_scale != 1.0:
        cl = ndi.zoom(cl, cluster_scale, order=1)
    C = cl.shape[0]
    off = 40 if frame else 60
    for c in corners:
        piece = cl
        if "r" in c: piece = piece[:, ::-1]
        if "b" in c: piece = piece[::-1, :]
        ys = slice(off, off + C) if "t" in c else slice(H - off - C, H - off)
        xs = slice(off, off + C) if "l" in c else slice(W - off - C, W - off)
        h[ys, xs] = np.maximum(h[ys, xs], piece)
    # emboss shading applied on top of paper colour
    gy, gx = np.gradient(h * strength)
    l = np.sqrt(gx * gx + gy * gy + 1)
    diff = np.clip((-gx * LIGHT[0] - gy * LIGHT[1] + LIGHT[2]) / l, 0, 1) / LIGHT[2]
    k = 0.55 + 0.45 * diff
    # soft occlusion around raised parts
    occ = 1 - 0.10 * np.clip(ndi.gaussian_filter(h, 10) - h, 0, 6) / 6
    rgb = alb_rgb * (k * occ)[..., None]
    # gentle diagonal window light
    yy, xx = np.mgrid[0:H, 0:W].astype(F32)
    ray = np.exp(-(((xx * 0.8 + yy * 0.6) - 0.62 * (W * 0.8 + H * 0.6)) / (W * 0.25)) ** 2)
    rgb *= (1 + 0.06 * ray)[..., None]
    Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8)).resize((W // 2, H // 2), Image.LANCZOS).save(OUT + name)
    print("emboss", name)


if __name__ == "__main__" and "emboss" in sys.argv:
    emboss_page((108, 120, 70), "emboss_frame_green.png", cluster_scale=1.12, strength=1.35)
    emboss_page((244, 238, 226), "emboss_corners_cream.png", frame=False, corners=("tl", "br"), cluster_scale=1.0, strength=1.3, crumple=0.1, mottle=1)
    emboss_page((244, 238, 226), "emboss_corners_cream_b.png", frame=False, corners=("tr", "bl"), cluster_scale=1.0, strength=1.3, crumple=0.1, mottle=1)
    emboss_page((108, 120, 70), "emboss_corners_green.png", frame=False, corners=("tl", "tr", "bl", "br"), cluster_scale=0.9, strength=1.35)
    emboss_page((244, 238, 226), "cream_plain.png", frame=False, corners=(), strength=1.3, crumple=0.1, mottle=1)
    # la invitación usa los fondos en JPG (archivo más liviano)
    for n in ("emboss_frame_green", "emboss_corners_cream", "emboss_corners_cream_b", "emboss_corners_green", "cream_plain"):
        Image.open(OUT + n + ".png").convert("RGB").save(OUT + n + ".jpg", quality=92)
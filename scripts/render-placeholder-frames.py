#!/usr/bin/env python3
"""
Render placeholder cinematic frame sequences for the Vastra scroll site.

These stand in for the Higgsfield-generated clips until credits are available.
Two sequences, matching the planned clips:
  frames/hero  - slow push-in through drifting silk waves + rising gold bokeh
  frames/zari  - a gold zari mandala weaving itself together while rotating

Usage: python3 scripts/render-placeholder-frames.py [frame_count]
"""
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

W, H = 1600, 900
N_FRAMES = int(sys.argv[1]) if len(sys.argv) > 1 else 160
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Vastra palette
ESPRESSO = np.array([31, 18, 10], dtype=np.float32)
UMBER = np.array([62, 33, 18], dtype=np.float32)
TERRACOTTA = np.array([176, 74, 23], dtype=np.float32)
GOLD = np.array([214, 164, 78], dtype=np.float32)
CHAMPAGNE = np.array([240, 220, 178], dtype=np.float32)

YY, XX = np.mgrid[0:H, 0:W].astype(np.float32)
NX = (XX - W / 2) / (W / 2)   # -1..1
NY = (YY - H / 2) / (H / 2)
RAD = np.sqrt(NX**2 + (NY * H / W) ** 2)
VIGNETTE = np.clip(1.0 - 0.55 * RAD**2.2, 0.0, 1.0)[..., None]

rng = np.random.default_rng(7)
BOKEH = [
    dict(x=rng.uniform(0, 1), y=rng.uniform(0, 1.4), r=rng.uniform(3, 16),
         speed=rng.uniform(0.10, 0.35), drift=rng.uniform(-0.05, 0.05),
         a=rng.uniform(0.25, 0.8))
    for _ in range(70)
]


def lerp3(c1, c2, t):
    return c1[None, None, :] * (1 - t[..., None]) + c2[None, None, :] * t[..., None]


def silk_field(t, zoom):
    """Layered flowing sine fields that read as backlit silk."""
    x = NX / zoom
    y = NY / zoom
    v = np.zeros((H, W), dtype=np.float32)
    layers = [
        (2.1, 0.9, 0.55, 0.15),
        (3.4, 1.7, 0.30, -0.22),
        (5.9, 2.6, 0.15, 0.31),
    ]
    for fx, fy, amp, spin in layers:
        ang = spin * (0.6 + 0.25 * t)
        xr = x * math.cos(ang) - y * math.sin(ang)
        yr = x * math.sin(ang) + y * math.cos(ang)
        ph = t * math.tau
        v += amp * np.sin(fx * xr + 1.5 * np.sin(fy * yr + ph * 0.7) + ph)
    return (v - v.min()) / (v.max() - v.min() + 1e-6)


def bokeh_layer(t):
    im = Image.new("L", (W // 2, H // 2), 0)
    d = ImageDraw.Draw(im)
    for b in BOKEH:
        y = (b["y"] - t * b["speed"] * 1.6) % 1.4 - 0.2
        x = (b["x"] + t * b["drift"]) % 1.0
        px, py, r = x * W / 2, y * H / 2, b["r"] / 2
        d.ellipse([px - r, py - r, px + r, py + r], fill=int(255 * b["a"]))
    im = im.filter(ImageFilter.GaussianBlur(5)).resize((W, H), Image.BILINEAR)
    return np.asarray(im, dtype=np.float32)[..., None] / 255.0


def hero_frame(i, n):
    t = i / (n - 1)
    zoom = 1.0 + 0.22 * t  # slow cinematic push-in
    silk = silk_field(t, zoom)

    base = lerp3(ESPRESSO, UMBER, np.clip(NY * 0.5 + 0.5, 0, 1))
    cloth = lerp3(TERRACOTTA * 0.45, GOLD, silk**1.3)
    img = base * 0.30 + cloth * (0.25 + 0.75 * silk[..., None])
    # specular sheen along the fold ridges
    sheen = np.clip(silk - 0.72, 0, 1) * 3.2
    img += CHAMPAGNE[None, None, :] * sheen[..., None] * 0.55
    # deep shadow in the folds
    img *= (0.55 + 0.45 * np.clip(silk * 1.6, 0, 1))[..., None]

    # travelling warm key-light
    lx, ly = -0.6 + 1.2 * t, -0.25 + 0.15 * math.sin(t * math.tau)
    glow = np.exp(-(((NX - lx) ** 2 + (NY - ly) ** 2) / 0.55)).astype(np.float32)
    img += CHAMPAGNE[None, None, :] * glow[..., None] * 0.28

    img += CHAMPAGNE[None, None, :] * bokeh_layer(t) * 0.5
    img *= VIGNETTE
    img += rng.normal(0, 2.2, (H, W, 1)).astype(np.float32)  # film grain
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))


def zari_overlay(t):
    """Gold mandala line-work weaving itself in, rotating slowly. 2x supersampled."""
    S = 2
    im = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    cx, cy = W * S / 2, H * S / 2
    rot = math.radians(20 + 55 * t)
    scale = (1.28 - 0.28 * t) * H * S * 0.40
    n_pet = 24
    gold = (222, 178, 96)

    for k in range(n_pet):
        appear = np.clip((t * 1.25 - k / n_pet) * 6, 0, 1)
        if appear <= 0:
            continue
        a = rot + k * math.tau / n_pet
        alpha = int(230 * appear)
        for rr, wgt in [(1.0, 5), (0.78, 3), (0.55, 2)]:
            r = scale * rr * (0.6 + 0.4 * appear)
            x1, y1 = cx + math.cos(a) * r * 0.35, cy + math.sin(a) * r * 0.35
            x2, y2 = cx + math.cos(a) * r, cy + math.sin(a) * r
            mx = cx + math.cos(a + 0.16) * r * 0.72
            my = cy + math.sin(a + 0.16) * r * 0.72
            d.line([x1, y1, mx, my, x2, y2], fill=gold + (alpha,), width=wgt * S)
            pr = 7 * S * appear
            d.ellipse([x2 - pr, y2 - pr, x2 + pr, y2 + pr], fill=gold + (alpha,))

    for ring, wgt in [(0.35, 4), (0.72, 2), (1.02, 3)]:
        vis = np.clip(t * 2.2 - ring * 0.6, 0, 1)
        if vis <= 0:
            continue
        r = scale * ring
        sweep = 360 * vis
        d.arc([cx - r, cy - r, cx + r, cy + r], start=math.degrees(rot),
              end=math.degrees(rot) + sweep, fill=gold + (int(200 * vis),), width=wgt * S)

    im = im.resize((W, H), Image.LANCZOS)
    halo = im.filter(ImageFilter.GaussianBlur(6))
    return Image.alpha_composite(halo, im)


def zari_frame(i, n):
    t = i / (n - 1)
    base = lerp3(np.array([38, 16, 12], np.float32), np.array([24, 10, 8], np.float32),
                 np.clip(RAD, 0, 1))
    sheen = silk_field(t * 0.5, 1.4)
    base += lerp3(TERRACOTTA * 0.25, GOLD * 0.30, sheen**2)* 0.8
    base *= VIGNETTE
    base += rng.normal(0, 2.0, (H, W, 1)).astype(np.float32)
    img = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8)).convert("RGBA")
    img = Image.alpha_composite(img, zari_overlay(t))
    return img.convert("RGB")


def render(name, fn):
    out = os.path.join(ROOT, "frames", name)
    os.makedirs(out, exist_ok=True)
    for i in range(N_FRAMES):
        fn(i, N_FRAMES).save(os.path.join(out, f"frame_{i:04d}.jpg"),
                             quality=85, optimize=True)
        if i % 20 == 0:
            print(f"{name}: {i}/{N_FRAMES}", flush=True)
    print(f"{name}: done ({N_FRAMES} frames)", flush=True)


if __name__ == "__main__":
    render("hero", hero_frame)
    render("zari", zari_frame)

# -*- coding: utf-8 -*-
"""Lenta s nazvaniem. Forma snyata s obrazca zakazchika (list s krabom):
proporcii polotna, naklon bokov, progib verhnego i nizhnego kraya, hvosty.
Risuetsya rovnymi krivymi, poetomu kray gladkiy i odinakovoy tolshchiny.

Koordinaty nizhe v tochkah zamera s obrazca. Seredina po x = 925.
"""
import pymupdf

CX = 925.0

TOP = [(394, 114), (485, 96), (605, 84), (804, 72), (1051, 72), (1301, 88), (1456, 114)]
BOT = [(425, 294), (693, 282), (1100, 282), (1426, 293)]
TAIL = [(396, 182), (321, 192), (242, 208), (298, 278), (254, 366), (348, 354), (466, 344)]
WEDGE = [(430, 293), (500, 291), (500, 345)]

STROKE = 8.0
INNER_H = 210.0


def _cr(sh, pts, T):
    p = [T(q) for q in pts]
    n = len(p)
    for i in range(n - 1):
        p0 = p[i - 1] if i > 0 else p[0]
        p1, p2 = p[i], p[i + 1]
        p3 = p[i + 2] if i + 2 < n else p[n - 1]
        c1 = pymupdf.Point(p1.x + (p2.x - p0.x) / 6.0, p1.y + (p2.y - p0.y) / 6.0)
        c2 = pymupdf.Point(p2.x - (p3.x - p1.x) / 6.0, p2.y - (p3.y - p1.y) / 6.0)
        sh.draw_bezier(p1, c1, c2, p2)


def draw(page, cx, y_center, inner_h, inner_w, color=(0, 0, 0)):
    sc = float(inner_h) / INNER_H
    own_w = TOP[-1][0] - TOP[0][0]
    e = max(0.0, inner_w - own_w * sc)
    seam = own_w * 0.20
    ycen = (72.0 + 282.0) / 2.0

    def T(q):
        x, y = q
        d = x - CX
        if d <= -seam:
            dx = -e / 2
        elif d >= seam:
            dx = e / 2
        else:
            dx = (e / 2) * (d / seam)
        return pymupdf.Point(cx + (x - CX) * sc + dx, y_center + (y - ycen) * sc)

    def mirror(q):
        return (2 * CX - q[0], q[1])

    w = STROKE * sc

    for pts in (TAIL, [mirror(q) for q in TAIL]):
        sh = page.new_shape()
        p = [T(q) for q in pts]
        sh.draw_polyline(p + [p[0]])
        sh.finish(color=color, fill=(1, 1, 1), width=w, closePath=True, lineJoin=1)
        sh.commit()

    for pts in (WEDGE, [mirror(q) for q in WEDGE]):
        sh = page.new_shape()
        sh.draw_polyline([T(q) for q in pts] + [T(pts[0])])
        sh.finish(color=None, fill=color, width=0, closePath=True)
        sh.commit()

    sh = page.new_shape()
    _cr(sh, TOP, T)
    sh.draw_line(T(TOP[-1]), T(BOT[-1]))
    _cr(sh, list(reversed(BOT)), T)
    sh.draw_line(T(BOT[0]), T(TOP[0]))
    sh.finish(color=color, fill=(1, 1, 1), width=w, closePath=True, lineJoin=1)
    sh.commit()

    a, b = T(TOP[0]), T(BOT[-1])
    return pymupdf.Rect(a.x, T((0, 72.0)).y, b.x, T((0, 282.0)).y)

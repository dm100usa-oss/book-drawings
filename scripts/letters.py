"""Скелеты букв: пунктирная линия внутри буквы, точка начала, стрелка.
Порядок движений сверян с Zaner-Bloser Manuscript Stroke Descriptions."""
import math


def _ang(x1, y1, x2, y2):
    return math.degrees(math.atan2(y2 - y1, x2 - x1))


def strokes(ch, g):
    """g: словарь с координатами. Возвращает список (path, arrow_xy, arrow_deg)."""
    Lx, Rx = g['L'], g['R']
    T, B = g['T'], g['B']          # верх и низ тела буквы (по осевой)
    xt = g.get('xt', T)            # линия строчных букв
    at = g.get('at', T)            # линия высоких букв
    db = g.get('db', B)            # низ хвоста
    cx, cy = (Lx + Rx) / 2, (T + B) / 2
    w, h = Rx - Lx, B - T
    S = []

    def line(x1, y1, x2, y2):
        S.append((f'M {x1:.2f} {y1:.2f} L {x2:.2f} {y2:.2f}',
                  (x2, y2), _ang(x1, y1, x2, y2)))

    def circ(x0, y0, x1_, y1_, rx, ry, large, sweep, ax, ay, adeg):
        S.append((f'M {x0:.2f} {y0:.2f} A {rx:.2f} {ry:.2f} 0 {large} {sweep} '
                  f'{x1_:.2f} {y1_:.2f}', (ax, ay), adeg))

    def full_circle(ccx, ccy, rx, ry, adeg=180):
        S.append((f'M {ccx:.2f} {ccy-ry:.2f} '
                  f'A {rx:.2f} {ry:.2f} 0 1 0 {ccx:.2f} {ccy+ry:.2f} '
                  f'A {rx:.2f} {ry:.2f} 0 1 0 {ccx:.2f} {ccy-ry:.2f}',
                  (ccx + rx * 0.42, ccy - ry * 0.9), adeg))

    def cback(x0, y0, x1_, y1_, rx, ry, a1, a2, ccx, ccy):
        S.append((f'M {x0:.2f} {y0:.2f} A {rx:.2f} {ry:.2f} 0 1 0 '
                  f'{x1_:.2f} {y1_:.2f}', (x1_, y1_),
                  math.degrees(math.atan2(-ry * math.cos(math.radians(a2)),
                                          rx * math.sin(math.radians(a2))))))

    def arcpt(ccx, ccy, rx, ry, a):
        t = math.radians(a)
        return ccx + rx * math.cos(t), ccy - ry * math.sin(t)

    # ---------------- заглавные ----------------
    if ch == 'A':
        ax_, ay_ = cx, T
        line(ax_, ay_, Lx, B)
        line(ax_, ay_, Rx, B)
        yy = T + 0.66 * h
        x1 = ax_ + (Lx - ax_) * 0.66
        x2 = ax_ + (Rx - ax_) * 0.66
        line(x1, yy, x2, yy)
    elif ch == 'B':
        line(Lx, T, Lx, B)
        m = (T + B) / 2
        circ(Lx, T, Lx, m, w * 0.92, (m - T) / 2, 0, 1, Lx, m, 180)
        circ(Lx, m, Lx, B, w, (B - m) / 2, 0, 1, Lx, B, 180)
    elif ch in 'CG':
        rx, ry = w / 2, h / 2
        p1 = arcpt(cx, cy, rx, ry, 55)
        e = -55 if ch == 'C' else -20
        p2 = arcpt(cx, cy, rx, ry, e)
        cback(p1[0], p1[1], p2[0], p2[1], rx, ry, 55, e, cx, cy)
        if ch == 'G':
            line(p2[0], p2[1], cx + rx * 0.1, p2[1])
    elif ch == 'D':
        line(Lx, T, Lx, B)
        circ(Lx, T, Lx, B, w, h / 2, 0, 1, Lx, B, 180)
    elif ch in 'EF':
        line(Lx, T, Lx, B)
        line(Lx, T, Rx, T)
        line(Lx, cy, Lx + w * 0.82, cy)
        if ch == 'E':
            line(Lx, B, Rx, B)
    elif ch == 'H':
        line(Lx, T, Lx, B)
        line(Rx, T, Rx, B)
        line(Lx, cy, Rx, cy)
    elif ch == 'I':
        line(cx, T, cx, B)
        line(Lx, T, Rx, T)
        line(Lx, B, Rx, B)
    elif ch == 'J':
        r = w / 2
        S.append((f'M {Rx:.2f} {T:.2f} L {Rx:.2f} {B-r:.2f} '
                  f'A {r:.2f} {r:.2f} 0 0 0 {Rx-2*r:.2f} {B-r:.2f}',
                  (Rx - 2 * r, B - r), 270))
    elif ch == 'K':
        line(Lx, T, Lx, B)
        mx, my = Lx + w * 0.12, cy
        line(Rx, T, mx, my)
        line(mx, my, Rx, B)
    elif ch == 'L':
        line(Lx, T, Lx, B)
        line(Lx, B, Rx, B)
    elif ch == 'M':
        line(Lx, T, Lx, B)
        line(Lx, T, cx, T + h * 0.72)
        line(cx, T + h * 0.72, Rx, T)
        line(Rx, T, Rx, B)
    elif ch == 'O':
        full_circle(cx, cy, w / 2, h / 2)
    elif ch in 'PR':
        line(Lx, T, Lx, B)
        bm = T + h * 0.54
        circ(Lx, T, Lx, bm, w * 0.95, (bm - T) / 2, 0, 1, Lx, bm, 180)
        if ch == 'R':
            line(Lx + w * 0.1, bm, Rx, B)
    elif ch == 'S':
        S.append((f'M {Rx:.2f} {T+0.17*h:.2f} '
                  f'C {Rx:.2f} {T:.2f} {Lx:.2f} {T:.2f} {Lx:.2f} {T+0.3*h:.2f} '
                  f'C {Lx:.2f} {T+0.5*h:.2f} {Rx:.2f} {T+0.5*h:.2f} '
                  f'{Rx:.2f} {T+0.72*h:.2f} '
                  f'C {Rx:.2f} {B:.2f} {Lx:.2f} {B:.2f} '
                  f'{Lx:.2f} {B-0.17*h:.2f}',
                  (Lx, B - 0.17 * h), 200))
    elif ch == 'T':
        line(cx, T, cx, B)
        line(Lx, T, Rx, T)
    elif ch == 'U':
        r = w / 2
        S.append((f'M {Lx:.2f} {T:.2f} L {Lx:.2f} {B-r:.2f} '
                  f'A {r:.2f} {r:.2f} 0 0 0 {Rx:.2f} {B-r:.2f} '
                  f'L {Rx:.2f} {T:.2f}', (Rx, T), 270))
    elif ch == 'W':
        p = [(Lx, T), (Lx + w * 0.22, B), (cx, T + h * 0.3),
             (Rx - w * 0.22, B), (Rx, T)]
        for i in range(4):
            line(*p[i], *p[i + 1])
    elif ch == 'Y':
        line(Lx, T, cx, cy)
        line(Rx, T, cx, cy)
        line(cx, cy, cx, B)
    elif ch == 'Z':
        line(Lx, T, Rx, T)
        line(Rx, T, Lx, B)
        line(Lx, B, Rx, B)

    # ---------------- строчные ----------------
    elif ch == 'a':
        rx, ry = w / 2, (B - xt) / 2
        full_circle(cx, (xt + B) / 2, rx, ry, 270)
        line(Rx, xt, Rx, B)
    elif ch == 'b':
        line(Lx, at, Lx, B)
        circ(Lx, xt, Lx, B, w, (B - xt) / 2, 1, 1, Lx, B, 180)
    elif ch == 'c':
        rx, ry = w / 2, (B - xt) / 2
        ccy = (xt + B) / 2
        p1 = arcpt(cx, ccy, rx, ry, 55)
        p2 = arcpt(cx, ccy, rx, ry, -55)
        cback(p1[0], p1[1], p2[0], p2[1], rx, ry, 55, -55, cx, ccy)
    elif ch == 'd':
        rx, ry = w / 2, (B - xt) / 2
        full_circle(cx, (xt + B) / 2, rx, ry, 270)
        line(Rx, at, Rx, B)
    elif ch == 'e':
        ccy = (xt + B) / 2
        rx, ry = w / 2, (B - xt) / 2
        line(Lx, ccy, Rx, ccy)
        p2 = arcpt(cx, ccy, rx, ry, -60)
        cback(Rx, ccy, p2[0], p2[1], rx, ry, 0, -60, cx, ccy)
    elif ch == 'f':
        hr = w * 0.34
        sx = Rx - 2 * hr
        S.append((f'M {Rx:.2f} {at+hr:.2f} '
                  f'A {hr:.2f} {hr:.2f} 0 0 0 {sx:.2f} {at+hr:.2f} '
                  f'L {sx:.2f} {B:.2f}', (sx, B), 90))
        line(Lx, xt, Rx, xt)
    elif ch == 'g':
        rx, ry = w / 2, (B - xt) / 2
        full_circle(cx, (xt + B) / 2, rx, ry, 270)
        r = w / 2.4
        S.append((f'M {Rx:.2f} {xt:.2f} L {Rx:.2f} {db-r:.2f} '
                  f'A {r:.2f} {r:.2f} 0 0 0 {Rx-2*r:.2f} {db-r:.2f}',
                  (Rx - 2 * r, db - r), 250))
    elif ch == 'h':
        line(Lx, at, Lx, B)
        r = w / 2
        S.append((f'M {Lx:.2f} {B:.2f} L {Lx:.2f} {xt+r:.2f} '
                  f'A {r:.2f} {r:.2f} 0 0 1 {Rx:.2f} {xt+r:.2f} '
                  f'L {Rx:.2f} {B:.2f}', (Rx, B), 90))
    elif ch == 'i':
        line(cx, xt, cx, B)
        S.append(('DOT', (cx, g['dot']), 0))
    elif ch == 'j':
        r = w / 2.0
        S.append((f'M {Rx:.2f} {xt:.2f} L {Rx:.2f} {db-r:.2f} '
                  f'A {r:.2f} {r:.2f} 0 0 0 {Rx-2*r:.2f} {db-r:.2f}',
                  (Rx - 2 * r, db - r), 255))
        S.append(('DOT', (Rx, g['dot']), 0))
    elif ch == 'k':
        line(Lx, at, Lx, B)
        mx, my = Lx + w * 0.14, xt + (B - xt) * 0.55
        line(Rx, xt, mx, my)
        line(mx, my, Rx, B)
    elif ch == 'l':
        line(cx, at, cx, B)
    elif ch == 'm':
        line(Lx, xt, Lx, B)
        r = w / 4
        S.append((f'M {Lx:.2f} {B:.2f} L {Lx:.2f} {xt+r:.2f} '
                  f'A {r:.2f} {r:.2f} 0 0 1 {cx:.2f} {xt+r:.2f} '
                  f'L {cx:.2f} {B:.2f}', (cx, B), 90))
        S.append((f'M {cx:.2f} {B:.2f} L {cx:.2f} {xt+r:.2f} '
                  f'A {r:.2f} {r:.2f} 0 0 1 {Rx:.2f} {xt+r:.2f} '
                  f'L {Rx:.2f} {B:.2f}', (Rx, B), 90))
    elif ch == 'o':
        full_circle(cx, (xt + B) / 2, w / 2, (B - xt) / 2)
    elif ch == 'p':
        line(Lx, xt, Lx, db)
        circ(Lx, xt, Lx, B, w, (B - xt) / 2, 1, 1, Lx, B, 180)
    elif ch == 'r':
        line(Lx, xt, Lx, B)
        r = (B - xt) * 0.38
        ex, ey = Rx - (Rx - Lx) * 0.12, xt + r * 0.75
        S.append((f'M {Lx:.2f} {B:.2f} L {Lx:.2f} {xt+r:.2f} '
                  f'A {r:.2f} {r:.2f} 0 0 1 {ex:.2f} {ey:.2f}', (ex, ey), -15))
    elif ch == 's':
        hh = B - xt
        S.append((f'M {Rx:.2f} {xt+0.17*hh:.2f} '
                  f'C {Rx:.2f} {xt:.2f} {Lx:.2f} {xt:.2f} '
                  f'{Lx:.2f} {xt+0.3*hh:.2f} '
                  f'C {Lx:.2f} {xt+0.5*hh:.2f} {Rx:.2f} {xt+0.5*hh:.2f} '
                  f'{Rx:.2f} {xt+0.72*hh:.2f} '
                  f'C {Rx:.2f} {B:.2f} {Lx:.2f} {B:.2f} '
                  f'{Lx:.2f} {B-0.17*hh:.2f}', (Lx, B - 0.17 * hh), 200))
    elif ch == 't':
        line(cx, at, cx, B)
        line(Lx, xt, Rx, xt)
    elif ch == 'u':
        r = w / 2
        S.append((f'M {Lx:.2f} {xt:.2f} L {Lx:.2f} {B-r:.2f} '
                  f'A {r:.2f} {r:.2f} 0 0 0 {Rx:.2f} {B-r:.2f} '
                  f'L {Rx:.2f} {xt:.2f}', (Rx, xt), 270))
        line(Rx, xt, Rx, B)
    elif ch == 'w':
        p = [(Lx, xt), (Lx + w * 0.22, B), (cx, xt + (B - xt) * 0.3),
             (Rx - w * 0.22, B), (Rx, xt)]
        for i in range(4):
            line(*p[i], *p[i + 1])
    elif ch == 'y':
        line(Lx, xt, cx, B)
        line(Rx, xt, Lx + w * 0.2, db)
    elif ch == 'z':
        line(Lx, xt, Rx, xt)
        line(Rx, xt, Lx, B)
        line(Lx, B, Rx, B)
    return S

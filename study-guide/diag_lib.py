"""Small diagram toolkit on top of reportlab.graphics, with a top-left origin."""
import math
from reportlab.graphics.shapes import Drawing, Rect, Line, String, Polygon, Circle, PolyLine, Group, Path
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

F = '/usr/share/fonts/truetype/'
for name, path in [('Sans', 'liberation/LiberationSans-Regular.ttf'), ('Sans-B', 'liberation/LiberationSans-Bold.ttf'),
                   ('Serif', 'liberation/LiberationSerif-Regular.ttf'), ('Serif-B', 'liberation/LiberationSerif-Bold.ttf'),
                   ('Serif-I', 'liberation/LiberationSerif-Italic.ttf'), ('Mono', 'dejavu/DejaVuSansMono.ttf'),
                   ('Mono-B', 'dejavu/DejaVuSansMono-Bold.ttf'), ('Sym', 'dejavu/DejaVuSans.ttf'), ('Sym-B', 'dejavu/DejaVuSans-Bold.ttf')]:
    try: pdfmetrics.getFont(name)
    except KeyError: pdfmetrics.registerFont(TTFont(name, F + path))

from reportlab.graphics.shapes import STATE_DEFAULTS
STATE_DEFAULTS['fontName'] = 'Sans'  # diagrams default to an embedded font
H = colors.HexColor
INK, MUTED, LINE, PANEL = H('#1d2330'), H('#5a6474'), H('#c3cad4'), H('#f4f6f9')
WHITE = colors.white
KIND = {  # stroke, fill, text
    'n': (H('#8a94a3'), H('#ffffff'), INK),
    'p': (H('#c3cad4'), H('#f4f6f9'), INK),
    'acc': (H('#1f5fd1'), H('#e6eefc'), H('#163f8c')),
    'ok': (H('#1c7a48'), H('#e3f3ea'), H('#145a35')),
    'bad': (H('#c0392b'), H('#fbe7e5'), H('#8e2318')),
    'warn': (H('#b26a00'), H('#fdf1dc'), H('#7a4a00')),
    'oob': (H('#6a3fb5'), H('#efe9fa'), H('#4b2a85')),
    'cu': (H('#b45f2a'), H('#fbefe6'), H('#7d3f17')),
    'ghost': (H('#b9c0ca'), H('#ffffff'), H('#8a94a3')),
    'dark': (H('#1d2330'), H('#1d2330'), H('#ffffff')),
}
C = {k: v[0] for k, v in KIND.items()}
W = {k: v[1] for k, v in KIND.items()}


class D:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.d = Drawing(w, h)

    def Y(self, y): return self.h - y

    # ---- primitives
    def rect(self, x, y, w, h, kind='n', r=5, sw=1, dash=None, fill=None, stroke=None):
        s, f, _ = KIND[kind]
        fc = None if fill == 'none' else (fill if fill is not None else f)
        self.d.add(Rect(x, self.Y(y + h), w, h, rx=r, ry=r, strokeColor=stroke or s, fillColor=fc,
                        strokeWidth=sw, strokeDashArray=dash))

    def text(self, x, y, s, fs=8, color=INK, anchor='start', font='Sans'):
        self.d.add(String(x, self.Y(y), s, fontName=font, fontSize=fs, fillColor=color, textAnchor=anchor))

    def lines(self, x, y, rows, fs=8, color=INK, anchor='start', font='Sans', lead=None):
        lead = lead or fs * 1.25
        for i, s in enumerate(rows): self.text(x, y + i * lead, s, fs, color, anchor, font)

    def box(self, x, y, w, h, title, sub=None, kind='n', fs=9, sfs=7.2, r=5, sw=1.1, dash=None, align='c'):
        self.rect(x, y, w, h, kind, r=r, sw=sw, dash=dash)
        tc = KIND[kind][2]
        subs = sub if isinstance(sub, (list, tuple)) else ([sub] if sub else [])
        tot = fs + len(subs) * (sfs * 1.25)
        ty = y + (h - tot) / 2 + fs * 0.82
        ax, an = (x + w / 2, 'middle') if align == 'c' else (x + 7, 'start')
        self.text(ax, ty, title, fs, tc, an, 'Sans-B')
        for i, s in enumerate(subs):
            self.text(ax, ty + (i + 1) * sfs * 1.25 + 1, s, sfs, MUTED if kind in ('n', 'p', 'ghost') else tc, an, 'Sans')

    def line(self, x1, y1, x2, y2, kind='n', sw=1.2, dash=None, color=None):
        self.d.add(Line(x1, self.Y(y1), x2, self.Y(y2), strokeColor=color or C[kind], strokeWidth=sw, strokeDashArray=dash))

    def head(self, x1, y1, x2, y2, color, size=5.5):
        a = math.atan2(self.Y(y2) - self.Y(y1), x2 - x1)
        X, Yy = x2, self.Y(y2)
        p = [X, Yy, X - size * math.cos(a - 0.42), Yy - size * math.sin(a - 0.42), X - size * math.cos(a + 0.42), Yy - size * math.sin(a + 0.42)]
        self.d.add(Polygon(p, fillColor=color, strokeColor=color, strokeWidth=0.5))

    def arrow(self, pts, kind='n', label=None, sw=1.3, dash=None, both=False, lfs=7.2, lpos=0.5, ldy=-4, lcolor=None, color=None, lanchor='middle'):
        col = color or C[kind]
        flat = []
        for x, y in pts: flat += [x, self.Y(y)]
        self.d.add(PolyLine(flat, strokeColor=col, strokeWidth=sw, strokeDashArray=dash))
        self.head(*pts[-2], *pts[-1], col)
        if both: self.head(*pts[1], *pts[0], col)
        if label:
            # label at lpos along the longest segment
            segs = list(zip(pts, pts[1:]))
            (ax, ay), (bx, by) = max(segs, key=lambda s: math.hypot(s[1][0] - s[0][0], s[1][1] - s[0][1]))
            lx, ly = ax + (bx - ax) * lpos, ay + (by - ay) * lpos
            for i, row in enumerate(label.split('\n')):
                self.text(lx, ly + ldy + i * lfs * 1.2, row, lfs, lcolor or col, lanchor, 'Sans-B' if i == 0 else 'Sans')

    def cross(self, x, y, s=6, color=None, sw=2.2):
        c = color or C['bad']
        self.line(x - s, y - s, x + s, y + s, sw=sw, color=c); self.line(x - s, y + s, x + s, y - s, sw=sw, color=c)

    def tick(self, x, y, s=6, color=None, sw=2.2):
        c = color or C['ok']
        self.d.add(PolyLine([x - s, self.Y(y), x - s * 0.3, self.Y(y + s * 0.7), x + s, self.Y(y - s * 0.8)], strokeColor=c, strokeWidth=sw))

    def badge(self, x, y, n, kind='acc', r=7.5, fs=8):
        self.d.add(Circle(x, self.Y(y), r, fillColor=C[kind], strokeColor=WHITE, strokeWidth=1))
        self.text(x, y + fs * 0.35, str(n), fs, WHITE, 'middle', 'Sans-B')

    def circle(self, x, y, r, kind='n', sw=1, fill=None, stroke=None):
        self.d.add(Circle(x, self.Y(y), r, fillColor=fill if fill is not None else W[kind], strokeColor=stroke or C[kind], strokeWidth=sw))

    def poly(self, pts, kind='n', sw=1, fill=None, stroke=None):
        flat = []
        for x, y in pts: flat += [x, self.Y(y)]
        self.d.add(Polygon(flat, fillColor=fill if fill is not None else W[kind], strokeColor=stroke or C[kind], strokeWidth=sw))

    def curve(self, pts, kind='n', sw=1.6, color=None, dash=None):
        flat = []
        for x, y in pts: flat += [x, self.Y(y)]
        self.d.add(PolyLine(flat, strokeColor=color or C[kind], strokeWidth=sw, strokeDashArray=dash))

    def pill(self, x, y, s, kind='acc', fs=7.2, pad=5, h=13):
        w = pdfmetrics.stringWidth(s, 'Sans-B', fs) + pad * 2
        self.rect(x, y, w, h, kind, r=h / 2, sw=0.9)
        self.text(x + w / 2, y + h / 2 + fs * 0.35, s, fs, KIND[kind][2], 'middle', 'Sans-B')
        return w

    def title(self, x, y, s, fs=8.5, color=MUTED):
        self.text(x, y, s.upper(), fs, color, 'start', 'Sans-B')

    # ---- hardware illustrations (all drawn, no photos)
    def dimm(self, x, y, w=150, h=34, chips=9, ecc=True, bad_chip=None, label=None, kind='n', dim=False):
        board = H('#2f7d4f') if not dim else H('#c9d3cc')
        self.d.add(Rect(x, self.Y(y + h), w, h, rx=2, ry=2, fillColor=board, strokeColor=H('#1f5a37'), strokeWidth=0.8))
        cw = (w - 16) / chips
        for i in range(chips):
            cx = x + 8 + i * cw
            fill = H('#1b1f27')
            if ecc and i == chips - 1: fill = C['acc']
            if bad_chip is not None and i == bad_chip: fill = C['bad']
            if dim: fill = H('#9aa3ad')
            self.d.add(Rect(cx + 1, self.Y(y + h * 0.66), cw - 3, h * 0.48, fillColor=fill, strokeColor=None))
        # gold fingers + notch
        nx = x + w * 0.42
        for i in range(int(w / 4)):
            fx = x + 3 + i * 4
            if abs(fx - nx) < 4: continue
            self.d.add(Rect(fx, self.Y(y + h), 2.4, 5, fillColor=H('#d4a72c'), strokeColor=None))
        if label: self.text(x + w / 2, y + h + 11, label, 7.2, INK, 'middle', 'Sans-B')

    def card(self, x, y, w=120, h=46, lanes=16, label='PCIe card', kind='n', bracket=True, fill=None):
        self.d.add(Rect(x, self.Y(y + h), w, h, rx=2, ry=2, fillColor=fill or H('#2f7d4f'), strokeColor=H('#1f5a37'), strokeWidth=0.8))
        self.d.add(Rect(x + w * 0.35, self.Y(y + h * 0.7), w * 0.3, h * 0.42, fillColor=H('#1b1f27'), strokeColor=None))
        fw = min(w - 10, lanes * 4.2)
        self.d.add(Rect(x + 6, self.Y(y + h + 5), fw, 5, fillColor=H('#d4a72c'), strokeColor=None))
        if bracket: self.d.add(Rect(x - 5, self.Y(y + h + 2), 5, h + 8, fillColor=H('#aab3bd'), strokeColor=H('#7d8794'), strokeWidth=0.6))
        self.text(x + w / 2, y + 11, label, 7, WHITE, 'middle', 'Sans-B')

    def slot(self, x, y, lanes, label=True, sc=3.0):
        w = 12 + lanes * sc
        self.d.add(Rect(x, self.Y(y + 9), w, 9, rx=1.5, ry=1.5, fillColor=H('#2b2f36'), strokeColor=None))
        self.d.add(Rect(x + 4, self.Y(y + 6), 3, 3, fillColor=H('#5d6470'), strokeColor=None))
        if label: self.text(x + w / 2, y + 21, f'x{lanes}', 7.5, INK, 'middle', 'Sans-B')
        return w

    def gpu(self, x, y, w=128, h=44, label='GPU', kind=None, power=True, dim=False):
        body = H('#3a3f48') if not dim else H('#c4c9d0')
        self.d.add(Rect(x, self.Y(y + h), w, h, rx=4, ry=4, fillColor=body, strokeColor=H('#22262c'), strokeWidth=0.8))
        for cx in (x + w * 0.28, x + w * 0.66):
            self.d.add(Circle(cx, self.Y(y + h / 2), h * 0.36, fillColor=H('#22262c') if not dim else H('#aeb4bc'), strokeColor=H('#5b6270'), strokeWidth=0.8))
            self.d.add(Circle(cx, self.Y(y + h / 2), h * 0.09, fillColor=H('#5b6270'), strokeColor=None))
        self.d.add(Rect(x + 8, self.Y(y + h + 5), w * 0.55, 5, fillColor=H('#d4a72c'), strokeColor=None))
        if power: self.d.add(Rect(x + w - 26, self.Y(y + 1), 18, 6, fillColor=H('#111'), strokeColor=H('#777'), strokeWidth=0.5))
        self.text(x + w / 2, y - 4, label, 7.2, INK, 'middle', 'Sans-B')

    def nvme_u2(self, x, y, w=54, h=70, label='U.2 NVMe', kind='n'):
        self.d.add(Rect(x, self.Y(y + h), w, h, rx=3, ry=3, fillColor=H('#c8ced6'), strokeColor=H('#7d8794'), strokeWidth=0.9))
        self.d.add(Rect(x + 6, self.Y(y + 22), w - 12, 14, fillColor=WHITE, strokeColor=H('#9aa3ad'), strokeWidth=0.5))
        self.text(x + w / 2, y + 17, 'NVMe', 6.5, INK, 'middle', 'Sans-B')
        self.d.add(Rect(x + 8, self.Y(y + h + 3), w - 16, 4, fillColor=H('#d4a72c'), strokeColor=None))
        self.text(x + w / 2, y + h + 14, label, 7, INK, 'middle', 'Sans-B')

    def m2(self, x, y, w=110, h=20, label='M.2 NVMe'):
        self.d.add(Rect(x, self.Y(y + h), w, h, rx=2, ry=2, fillColor=H('#2f7d4f'), strokeColor=H('#1f5a37'), strokeWidth=0.8))
        for i in range(3): self.d.add(Rect(x + 14 + i * 28, self.Y(y + h - 4), 22, h - 8, fillColor=H('#1b1f27'), strokeColor=None))
        self.d.add(Rect(x + w - 2, self.Y(y + h - 3), 5, h - 6, fillColor=H('#d4a72c'), strokeColor=None))
        self.text(x + w / 2, y + h + 11, label, 7, INK, 'middle', 'Sans-B')

    def server(self, x, y, w=220, h=34, label=None, leds=('ok',), kind='n', rear=False, uid=False):
        self.d.add(Rect(x, self.Y(y + h), w, h, rx=3, ry=3, fillColor=H('#e9edf2'), strokeColor=H('#7d8794'), strokeWidth=1))
        if not rear:
            for i in range(max(1, min(6, int((w - 40) / 22)))):
                bx = x + 10 + i * 22
                self.d.add(Rect(bx, self.Y(y + h - 6), 18, h - 12, rx=1.5, ry=1.5, fillColor=H('#d3d9e0'), strokeColor=H('#9aa3ad'), strokeWidth=0.6))
            for i, k in enumerate(leds):
                self.d.add(Circle(x + w - 16 - i * 12, self.Y(y + h / 2), 3.4, fillColor=C[k], strokeColor=None))
            if uid: self.d.add(Circle(x + w - 16 - len(leds) * 12, self.Y(y + h / 2), 3.4, fillColor=C['acc'], strokeColor=None))
        if label: self.text(x + w / 2, y + h + 11, label, 7.4, INK, 'middle', 'Sans-B')

    def rear(self, x, y, w=300, h=40, bmc_fault=False, nic_link=True, psu=('ok', 'ok')):
        self.d.add(Rect(x, self.Y(y + h), w, h, rx=3, ry=3, fillColor=H('#e9edf2'), strokeColor=H('#7d8794'), strokeWidth=1))
        # PSUs
        for i, k in enumerate(psu):
            px = x + 8 + i * 52
            self.d.add(Rect(px, self.Y(y + h - 6), 46, h - 12, rx=2, ry=2, fillColor=H('#cfd5dc'), strokeColor=H('#8a94a3'), strokeWidth=0.6))
            self.d.add(Circle(px + 38, self.Y(y + 12), 3, fillColor=C[k], strokeColor=None))
            self.text(px + 18, y + h - 12, f'PSU{i + 1}', 6.3, INK, 'middle', 'Sans-B')
        # BMC port
        bx = x + 124
        self.d.add(Rect(bx, self.Y(y + 26), 20, 15, fillColor=H('#2b2f36'), strokeColor=C['oob'], strokeWidth=1.6))
        self.text(bx + 10, y + 36, 'BMC', 6.3, C['oob'], 'middle', 'Sans-B')
        # NIC ports
        for i in range(2):
            nx = x + 160 + i * 26
            self.d.add(Rect(nx, self.Y(y + 26), 20, 15, fillColor=H('#2b2f36'), strokeColor=C['acc'], strokeWidth=1.2))
            self.d.add(Circle(nx + 4, self.Y(y + 14), 1.8, fillColor=C['ok'] if nic_link else H('#7d8794'), strokeColor=None))
        self.text(x + 183, y + 36, 'NIC ports', 6.3, C['acc'], 'middle', 'Sans-B')
        # VGA/serial
        self.d.add(Rect(x + 222, self.Y(y + 24), 30, 11, rx=2, ry=2, fillColor=H('#3c5ea8'), strokeColor=None))
        self.text(x + 237, y + 36, 'VGA', 6.3, INK, 'middle', 'Sans-B')
        self.d.add(Rect(x + 262, self.Y(y + 24), 26, 11, rx=2, ry=2, fillColor=H('#2b2f36'), strokeColor=None))
        self.text(x + 275, y + 36, 'USB', 6.3, INK, 'middle', 'Sans-B')

    def cpu(self, x, y, w=70, h=56, label='CPU 1', kind='n', sub=None):
        s, f, t = KIND[kind]
        self.d.add(Rect(x, self.Y(y + h), w, h, rx=4, ry=4, fillColor=f, strokeColor=s, strokeWidth=1.4))
        self.d.add(Rect(x + 8, self.Y(y + h - 8), w - 16, h - 16, rx=3, ry=3, fillColor=WHITE, strokeColor=s, strokeWidth=0.8))
        self.text(x + w / 2, y + h / 2 + 1, label, 8.5, t, 'middle', 'Sans-B')
        if sub: self.text(x + w / 2, y + h / 2 + 11, sub, 6.5, MUTED, 'middle', 'Sans')

    def laptop(self, x, y, w=62, label='Your laptop'):
        self.d.add(Rect(x + 6, self.Y(y + 34), w - 12, 34, rx=2, ry=2, fillColor=H('#2b2f36'), strokeColor=H('#1d2330'), strokeWidth=0.8))
        self.d.add(Rect(x + 9, self.Y(y + 31), w - 18, 28, fillColor=H('#0f1f33'), strokeColor=None))
        self.text(x + 13, y + 14, '$ _', 7, H('#7ee2a8'), 'start', 'Mono')
        self.d.add(Polygon([x, self.Y(y + 34), x + w, self.Y(y + 34), x + w - 4, self.Y(y + 40), x + 4, self.Y(y + 40)], fillColor=H('#9aa3ad'), strokeColor=None))
        if label: self.text(x + w / 2, y + 51, label, 7.2, INK, 'middle', 'Sans-B')

    def switch(self, x, y, w=120, h=26, label='Switch', ports=12, hi=None, hik='warn'):
        self.d.add(Rect(x, self.Y(y + h), w, h, rx=3, ry=3, fillColor=H('#dfe4ea'), strokeColor=H('#7d8794'), strokeWidth=1))
        pw = (w - 14) / ports
        for i in range(ports):
            col = C[hik] if hi == i else H('#2b2f36')
            self.d.add(Rect(x + 7 + i * pw, self.Y(y + h - 6), pw - 2, 9, fillColor=col, strokeColor=None))
        self.text(x + w / 2, y + 9, label, 6.8, INK, 'middle', 'Sans-B')

    def cylinder(self, x, y, w, h, title, sub=None, kind='n'):
        s, f, t = KIND[kind]
        e = 7
        self.d.add(Rect(x, self.Y(y + h), w, h - e / 2, fillColor=f, strokeColor=None))
        self.d.add(Line(x, self.Y(y + e / 2), x, self.Y(y + h), strokeColor=s, strokeWidth=1))
        self.d.add(Line(x + w, self.Y(y + e / 2), x + w, self.Y(y + h), strokeColor=s, strokeWidth=1))
        from reportlab.graphics.shapes import Ellipse
        self.d.add(Ellipse(x + w / 2, self.Y(y + h), w / 2, e / 2, fillColor=f, strokeColor=s, strokeWidth=1))
        self.d.add(Ellipse(x + w / 2, self.Y(y + e / 2), w / 2, e / 2, fillColor=f, strokeColor=s, strokeWidth=1))
        self.text(x + w / 2, y + h / 2 + 4, title, 8.5, t, 'middle', 'Sans-B')
        if sub: self.text(x + w / 2, y + h / 2 + 14, sub, 6.8, MUTED, 'middle', 'Sans')

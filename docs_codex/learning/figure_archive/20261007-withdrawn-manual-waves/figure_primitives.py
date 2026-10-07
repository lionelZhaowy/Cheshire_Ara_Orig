"""Explicit SVG primitives shared by the 2026-10-07 scientific figure masters.

Only the editable SVG/PPTX skill subset is emitted. No CSS, markers, images,
transforms, text outlines or browser-dependent layout.
"""
from html import escape
import math
import re
import unicodedata

INK = '#19364B'
MUTED = '#536B7D'
LINE = '#B9CAD6'
BLUE = '#216BB1'
TEAL = '#087E83'
ORANGE = '#B76315'
PURPLE = '#7555A3'
RED = '#A43D42'
PALE = {'blue': '#EDF4FC', 'teal': '#EAF6F3', 'orange': '#FFF3E7',
        'purple': '#F3EFF9', 'red': '#FBEFF0', 'gray': '#F3F6F8'}
COLORS = {'blue': BLUE, 'teal': TEAL, 'orange': ORANGE, 'purple': PURPLE,
          'red': RED, 'gray': MUTED}
FONT = 'WenQuanYi Zen Hei'


def units(s):
    return sum(1 if unicodedata.east_asian_width(c) in 'WF' else .57 for c in s)


def wrap(s, width, size):
    """Deterministic line breaking; actual browser bounds are checked separately."""
    result = []
    for paragraph in str(s).split('\n'):
        line = ''
        tokens = re.findall(r'[A-Za-z0-9_$]+(?:[./_-][A-Za-z0-9_$]+)*|.', paragraph)
        tokens = [piece for token in tokens for piece in (list(token) if units(token)*size > width else [token])]
        for char in tokens:
            if line and units(line + char) * size > width:
                result.append(line.rstrip()); line = ''
            line += char
        if line.strip(): result.append(line.strip())
    return result


class Figure:
    W, H = 1800, 1125

    def __init__(self, title, subtitle, source, status='源码结构 / 教学示意'):
        self.title, self.subtitle, self.source, self.status = title, subtitle, source, status
        self.back, self.wires, self.front = [], [], []
        self.nodes = {}
        self.rect(0, 0, self.W, self.H, '#FFFFFF', '#FFFFFF', layer=self.back)
        self.rect(40, 40, 8, 62, BLUE, BLUE, layer=self.back)
        self.text(68, 77, title, 36, bold=True)
        self.text(68, 120, subtitle, 23, MUTED)
        self.line(40, 148, 1760, 148, LINE, 1.5, layer=self.back)
        self.line(40, 1045, 1760, 1045, LINE, 1.5, layer=self.back)
        self.text(48, 1077, status, 21, TEAL)
        self.text(48, 1108, source, 20, MUTED)

    def emit(self, tag, attrs, body=None, layer=None):
        attrs = ' '.join(f'{k.replace("_", "-")}="{escape(str(v), quote=True)}"' for k, v in attrs.items())
        (self.front if layer is None else layer).append(
            f'<{tag} {attrs}/>' if body is None else f'<{tag} {attrs}>{escape(str(body))}</{tag}>')

    def rect(self, x, y, w, h, fill='#FFFFFF', stroke=LINE, r=0, layer=None):
        self.emit('rect', dict(x=x, y=y, width=w, height=h, rx=r, fill=fill,
                              stroke=stroke, stroke_width=1.5), layer=layer)

    def line(self, x1, y1, x2, y2, color=MUTED, width=2, layer=None):
        self.emit('line', dict(x1=x1, y1=y1, x2=x2, y2=y2, stroke=color,
                              stroke_width=width, fill='none'), layer=layer)

    def text(self, x, y, value, size=24, color=INK, bold=False, anchor='start', box=None):
        attrs = dict(x=x, y=y, fill=color, font_family=FONT, font_size=size,
                     font_weight='bold' if bold else 'normal', text_anchor=anchor)
        if box: attrs['data_box'] = box
        self.emit('text', attrs, value)

    def lines(self, x, y, values, width, size=24, color=MUTED, step=33, box=None):
        if isinstance(values, str): values = [values]
        for value in values:
            for ln in wrap(value, width, size):
                self.text(x, y, ln, size, color, box=box); y += step
        return y

    def panel(self, x, y, w, h, label, color='gray'):
        self.rect(x, y, w, h, PALE[color], LINE, 12, self.back)
        self.text(x + 18, y + 35, label, 25, COLORS[color], True)

    def node(self, key, x, y, w, h, title, body=(), color='blue', size=24):
        self.nodes[key] = (x, y, w, h)
        self.emit('rect', dict(id=key, x=x, y=y, width=w, height=h, rx=7,
                              fill=PALE[color], stroke=COLORS[color], stroke_width=1.6))
        self.rect(x, y, 5, h, COLORS[color], COLORS[color])
        yy = y + 32
        title_size = 26
        if h <= 105:
            while units(title) * title_size > w - 34 and title_size > 20:
                title_size -= 1
        for ln in wrap(title, w - 34, title_size):
            self.text(x + 17, yy, ln, title_size, COLORS[color], True, box=key); yy += 32
        if body: yy = self.lines(x + 17, yy + 4, body, w - 34, size, step=30, box=key)
        if yy - 24 > y + h: raise ValueError(f'Node too short: {key}: {yy}, {y+h}')
        return key

    def port(self, key, side='r', frac=.5):
        x, y, w, h = self.nodes[key]
        return {'l': (x, y + h * frac), 'r': (x + w, y + h * frac),
                't': (x + w * frac, y), 'b': (x + w * frac, y + h)}[side]

    def arrow(self, points, color=BLUE, width=3, head=True):
        self.emit('polyline', dict(points=' '.join(f'{x},{y}' for x, y in points),
                                  fill='none', stroke=color, stroke_width=width), layer=self.wires)
        if head:
            (x0, y0), (x, y) = points[-2:]
            angle = math.atan2(y - y0, x - x0); c, s = math.cos(angle), math.sin(angle)
            pts = [(x, y), (x - 12*c + 5*s, y - 12*s - 5*c), (x - 12*c - 5*s, y - 12*s + 5*c)]
            self.emit('polygon', dict(points=' '.join(f'{a:.2f},{b:.2f}' for a, b in pts),
                                      fill=color, stroke=color, stroke_width=1), layer=self.wires)

    def connect(self, a, b, sa='r', sb='l', color=BLUE, via=None, fa=.5, fb=.5):
        p, q = self.port(a, sa, fa), self.port(b, sb, fb)
        self.arrow([p] + (via or []) + [q], color)

    def curve(self, start, end, color=LINE, width=1.6, head=False):
        x,y=start; a,b=end; dx=(a-x)*.5
        self.emit('path', dict(d=f'M {x} {y} C {x+dx} {y} {a-dx} {b} {a} {b}',
                               fill='none', stroke=color, stroke_width=width), layer=self.wires)
        if head: self.arrow([(a-14,b),(a,b)],color,width)

    def note(self, x, y, w, title, body, color='gray', h=115):
        return self.node('note-'+str(len(self.nodes)), x,y,w,h,title,body,color,22)

    def save(self, path):
        svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.W}" height="{self.H}" viewBox="0 0 {self.W} {self.H}" role="img">\n'
        svg += f'<title>{escape(self.title)}</title>\n<desc>{escape(self.subtitle+"；"+self.source)}</desc>\n'
        svg += '\n'.join(self.back + self.wires + self.front) + '\n</svg>\n'
        path.write_text(svg)

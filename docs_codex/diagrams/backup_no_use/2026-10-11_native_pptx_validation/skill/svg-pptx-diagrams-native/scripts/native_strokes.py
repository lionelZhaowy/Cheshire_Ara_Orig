"""Validated SVG arrow markers and DrawingML line decoration (one object)."""
import math
import re

SVG = 'http://www.w3.org/2000/svg'


def values(s):
    result = [float(v) for v in re.split(r'[ ,\s]+', s.strip()) if v]
    if not all(math.isfinite(v) for v in result):
        raise ValueError('Non-finite stroke or marker coordinate')
    return result


def markers_from(root):
    """Only the documented triangle profile is accepted; never guess a marker."""
    result = {}
    for defs in root.findall(f'{{{SVG}}}defs'):
        if defs.attrib:
            raise ValueError('Use plain top-level defs without styling')
        for marker in defs:
            if marker.tag != f'{{{SVG}}}marker':
                raise ValueError('defs supports triangle markers only')
            allowed = {'id','markerUnits','markerWidth','markerHeight','viewBox','refX','refY','orient'}
            if set(marker.attrib)-allowed:
                raise ValueError('Unsupported marker attributes')
            name = marker.get('id')
            if not name or name in result:
                raise ValueError('Marker needs a unique id')
            expected = {'markerWidth':3, 'markerHeight':3, 'refX':3, 'refY':1.5}
            if any(values(marker.get(k,'')) != [v] for k,v in expected.items()):
                raise ValueError(f'{name}: use 3×3 triangle marker, refX=3/refY=1.5')
            if values(marker.get('viewBox','')) != [0,0,3,3] or marker.get('markerUnits') != 'strokeWidth':
                raise ValueError(f'{name}: require viewBox="0 0 3 3" and markerUnits="strokeWidth"')
            if marker.get('orient') not in ('auto','auto-start-reverse'):
                raise ValueError(f'{name}: require auto or auto-start-reverse orientation')
            if len(marker)!=1 or marker[0].tag != f'{{{SVG}}}polygon':
                raise ValueError(f'{name}: use a single filled triangle polygon')
            tri=marker[0]
            if list(tri) or set(tri.attrib)-{'points','fill','stroke'}:
                raise ValueError(f'{name}: unsupported triangle decoration')
            if values(tri.get('points','')) != [0,0,3,1.5,0,3] or tri.get('stroke','none') != 'none':
                raise ValueError(f'{name}: triangle points must be 0,0 3,1.5 0,3 with no stroke')
            fill=tri.get('fill','')
            if not re.fullmatch(r'#[0-9a-fA-F]{6}',fill):
                raise ValueError(f'{name}: explicit six-digit triangle fill required')
            result[name]={'fill':fill.lower(),'orient':marker.get('orient')}
    return result


def parse_stroke(tag, attrs, commands, markers):
    """Return normalized semantic properties, separate from visual SVG objects."""
    result={'dash': [], 'start':False, 'end':False}
    width=float(attrs['stroke-width'].strip().removesuffix('px'))
    dash=attrs.get('stroke-dasharray','none')
    if dash != 'none':
        parts=values(dash)
        if not parts or min(parts)<=0 or width<=0 or attrs['stroke']=='none' or tag=='text':
            raise ValueError('Dash requires positive lengths and a visible positive-width shape stroke')
        if len(parts)%2: parts*=2  # SVG repeats odd-length dash arrays.
        result['dash']=parts
    for end in ('start','end'):
        ref=attrs.get('marker-'+end,'none')
        if ref=='none':continue
        match=re.fullmatch(r'url\(#([^\s()]+)\)',ref)
        if not match or match[1] not in markers:
            raise ValueError(f'Unknown/local-only marker reference {ref!r}')
        if tag not in ('line','polyline','path') or attrs['fill']!='none' or attrs['stroke']=='none' or width<=0:
            raise ValueError('Arrow markers require an unfilled, visible open line/polyline/path')
        if commands and any(k=='Z' for k,_ in commands):
            raise ValueError('Arrow markers on closed paths are not supported')
        marker=markers[match[1]]
        if marker['fill']!=attrs['stroke'].lower():
            raise ValueError('Native arrowhead must use the same colour as the line')
        if end=='start' and marker['orient']!='auto-start-reverse':
            raise ValueError('Start arrow requires orient="auto-start-reverse"')
        if tag=='line':
            pts=[(float(attrs['x1'].strip().removesuffix('px')),float(attrs['y1'].strip().removesuffix('px'))),(float(attrs['x2'].strip().removesuffix('px')),float(attrs['y2'].strip().removesuffix('px')))]
        else: pts=[p for _,points in commands for p in points]
        if len(pts)<2 or all(p==pts[0] for p in pts):
            raise ValueError('Arrow requires a nonzero path')
        # End tangents must exist: reject degenerate segments instead of guessing.
        if pts[0]==pts[1] or pts[-1]==pts[-2]:
            raise ValueError('Arrow path needs nonzero endpoint tangents')
        result[end]=True
    return result


def apply_stroke(line, spec, width):
    from pptx.oxml.xmlchemy import OxmlElement
    from pptx.oxml.ns import qn
    for name in ('prstDash','custDash','headEnd','tailEnd'):
        for old in list(line.findall(qn('a:'+name))):line.remove(old)
    # CT_LineProperties order: fill, dash, join, headEnd, tailEnd, extensions.
    if spec['dash']:
        dash=OxmlElement('a:custDash')
        for d,g in zip(spec['dash'][::2],spec['dash'][1::2]):
            stop=OxmlElement('a:ds')
            stop.set('d',str(max(1,round(d/width*100000))))
            stop.set('sp',str(max(1,round(g/width*100000))))
            dash.append(stop)
        line.insert_element_before(dash,'a:round','a:bevel','a:miter','a:headEnd','a:tailEnd','a:extLst')
    for end,tag in [('start','headEnd'),('end','tailEnd')]:
        if spec[end]:
            node=OxmlElement('a:'+tag)
            node.set('type','triangle');node.set('w','med');node.set('len','med')
            line.insert_element_before(node,*(['a:tailEnd','a:extLst'] if end=='start' else ['a:extLst']))

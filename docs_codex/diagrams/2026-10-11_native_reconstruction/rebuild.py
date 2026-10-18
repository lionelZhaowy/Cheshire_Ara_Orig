#!/usr/bin/env python3
"""Replay reviewed object mappings; never infer arrows from nearby geometry.

Run with the native skill's Python, from the repository root, with a NEW
--out-dir. The checked-in reconstruction_plan.json pins every input hash.
"""
import argparse
import copy
import hashlib
import html
import json
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from diagram_paths import resolve_asset
NS = 'http://www.w3.org/2000/svg'
ET.register_namespace('', NS)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=Path.cwd())
    parser.add_argument('--skill', type=Path,
                        default=Path.home()/'.codex/skills/svg-pptx-diagrams-native')
    parser.add_argument('--plan', type=Path,
                        default=Path(__file__).with_name('reconstruction_plan.json'))
    parser.add_argument('--out-dir', type=Path)
    parser.add_argument('--check-inputs-only', action='store_true', help='Check source paths/hashes without producing files')
    args = parser.parse_args()
    if not args.check_inputs_only and args.out_dir is None:
        parser.error('--out-dir is required unless --check-inputs-only is used')
    if args.out_dir and args.out_dir.exists() and any(args.out_dir.iterdir()):
        parser.error('Refusing to overwrite a nonempty output directory')
    sys.path.insert(0, str(args.skill/'scripts'))
    from svg_to_pptx import read_svg, create_deck, path_commands
    plan = json.loads(args.plan.read_text())
    for entry in plan:
        assert digest(resolve_asset(args.repo, entry['source'])) == entry['sha256'], entry['source']
    if args.check_inputs_only:
        print(f'PASS: {len(plan)} original source paths and SHA-256 hashes; no output generated')
        return
    args.out_dir.mkdir(parents=True, exist_ok=True)
    reports, figures = [], []
    for entry in plan:
        original = read_svg(resolve_asset(args.repo, entry['source']))
        root = copy.deepcopy(original['svg'])
        objects = {e.get('id'): e for e in root}
        defs = ET.Element(f'{{{NS}}}defs')
        colors = sorted({a['color'] for a in entry['arrows']})
        marker_ids = {color: 'native-arrow-'+color[1:] for color in colors}
        for color, ident in marker_ids.items():
            marker = ET.SubElement(defs, f'{{{NS}}}marker', {
                'id': ident, 'markerUnits': 'strokeWidth', 'markerWidth': '3',
                'markerHeight': '3', 'viewBox': '0 0 3 3', 'refX': '3',
                'refY': '1.5', 'orient': 'auto-start-reverse'})
            ET.SubElement(marker, f'{{{NS}}}polygon', {
                'points': '0,0 3,1.5 0,3', 'fill': color})
        if colors:
            root.insert(0, defs)
        removed = set()
        for arrow in entry['arrows']:
            body = objects[arrow['body']]
            tip = arrow['tip']
            start = arrow['end'] == 'start'
            tag = body.tag.rsplit('}', 1)[-1]
            if tag == 'line':
                suffix = '1' if start else '2'
                body.set('x'+suffix, str(tip[0]))
                body.set('y'+suffix, str(tip[1]))
            else:
                if tag == 'polyline':
                    pts = [tuple(map(float, p.split(','))) for p in body.get('points').split()]
                    pts[0 if start else -1] = tip
                    body.set('points', ' '.join(f'{x:g},{y:g}' for x, y in pts))
                else:
                    commands = path_commands(body.get('d'))
                    commands[0 if start else -1][1][0 if start else -1] = tuple(tip)
                    body.set('d', ' '.join(cmd+' '+' '.join(f'{x:g} {y:g}' for x, y in pts)
                                          for cmd, pts in commands))
            body.set('fill', 'none')
            body.set('marker-'+arrow['end'], 'url(#'+marker_ids[arrow['color']]+')')
            removed.add(arrow['head'])
            removed.update(arrow['remove'])
        for dash in entry['dashes']:
            body = objects[dash['body']]
            body.set('stroke', dash['color'])
            body.set('stroke-width', str(dash['width']))
            body.set('stroke-dasharray', dash['dash'])
            removed.update(dash['remove'])
        for ident in removed:
            root.remove(objects[ident])
        destination = args.out_dir/(entry['name']+'.svg')
        ET.indent(root, space='  ')
        ET.ElementTree(root).write(destination, encoding='utf-8', xml_declaration=True)
        figure = read_svg(destination)
        before_text = [i for i in original['items'] if i['tag'] == 'text']
        after_text = [i for i in figure['items'] if i['tag'] == 'text']
        assert before_text == after_text, entry['name']
        assert original['view'] == figure['view']
        assert len(figure['items']) == len(original['items'])-len(removed)
        assert not any(i['tag'] == 'polygon' for i in figure['items'])
        modified = {a['body'] for a in entry['arrows']} | {d['body'] for d in entry['dashes']}
        remaining = {i['attrs']['id']: i for i in figure['items']}
        for item in original['items']:
            ident = item['attrs']['id']
            if ident not in removed | modified:
                assert item == remaining[ident], (entry['name'], ident)
        report = create_deck([figure], args.out_dir/(entry['name']+'.pptx'), 'source')[0]
        assert report['native_arrow_objects'] == len({a['body'] for a in entry['arrows']})
        assert report['native_dashed_objects'] == len(entry['dashes'])
        report.update(name=entry['name'], title=before_text[0]['text'],
                      source=entry['source'], source_sha256=entry['sha256'],
                      viewBox=figure['view'], original_objects=len(original['items']),
                      removed_arrowheads=len(entry['arrows']),
                      removed_curve_stubs=sum(len(a['remove']) for a in entry['arrows']),
                      removed_dash_segments=sum(len(d['remove']) for d in entry['dashes']),
                      text_and_unrelated_objects_preserved=True)
        reports.append(report)
        figures.append(figure)
        print(entry['name'], report['objects'], 'objects', report['native_arrow_objects'], 'arrows', flush=True)
    combined = create_deck(figures, args.out_dir/'all_diagrams.pptx', 'source')
    assert len(combined) == len(plan)
    for entry in plan:
        assert digest(resolve_asset(args.repo, entry['source'])) == entry['sha256']
    report = dict(skill='svg-pptx-diagrams-native', figures=reports, slides=len(plan),
                  total_omitted_canvas_backgrounds=sum(len(r['omitted_canvas_background_ids']) for r in reports),
                  total_native_arrows=sum(r['native_arrow_objects'] for r in reports),
                  total_native_dashed_objects=sum(r['native_dashed_objects'] for r in reports),
                  source_hashes_unchanged=True, office_display_editing_tested=False,
                  validation='SVG semantics and reopened native PPTX objects/text/arrow/dash/ZIP checks passed')
    (args.out_dir/'export_report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
    sections = []
    for n, r in enumerate(reports, 1):
        stem = r['name']
        sections.append(f'<section id="{stem}"><h2>{n:02d} · {html.escape(r["title"])}</h2>'
                        f'<p><a href="{stem}.svg">SVG 母版</a> · <a href="{stem}.png">PNG</a> · '
                        f'<a href="{stem}.pptx">单图 PPTX</a> · {r["native_arrow_objects"]} 个完整箭头</p>'
                        f'<a href="{stem}.svg"><img loading="lazy" src="{stem}.svg" alt="{html.escape(r["title"])}"></a></section>')
    index = '''<!doctype html><html lang="zh-CN"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Native reconstruction 图稿总览</title>
<style>body{font-family:system-ui,sans-serif;max-width:1450px;margin:auto;padding:28px;background:#eef2f6;color:#18364d}
section{background:white;padding:20px;margin:25px 0;border:1px solid #ced8e3}img{width:100%;height:auto}
a{color:#28619b}h2{font-size:20px}p{line-height:1.8}</style><h1>原生可编辑图稿 · 45 张</h1>
<p>保留原版配色、文字和自由画布。箭头、双向线和虚线边框采用完整对象。全部产物集中在本目录。</p>
<p><a href="all_diagrams.pptx">下载 45 页合辑 PPTX</a> · <a href="README.md">范围与检查说明</a> ·
<a href="export_report.json">结构验证报告</a></p>'''+''.join(sections)+'</html>\n'
    (args.out_dir/'index.html').write_text(index)


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Add the approved compact pixel bypass to the original single-page v1 PPT.

Build in a fresh temporary directory, inspect, then replace delivery files.
The original PPT is read-only; earlier editors are preserved in evidence archives.
"""
import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import subprocess
from zipfile import ZIP_DEFLATED, ZipFile
from lxml import etree as E

NS = {"p": "http://schemas.openxmlformats.org/presentationml/2006/main",
      "a": "http://schemas.openxmlformats.org/drawingml/2006/main"}
SVG = "http://www.w3.org/2000/svg"
SCALE = 12192000 / 3600
SOURCE_HASH = "a4a552ca74684711df8ce78528c7b50d923d77b47e5f299b16918bd8208fe2d0"
WIDTH, HEIGHT = 3600, 2025
ORANGE, PURPLE = "#B96043", "#765489"


def serial(node):
    return E.tostring(node, encoding="UTF-8", xml_declaration=True, standalone=True)


def name(shape):
    node = shape.find(".//p:cNvPr", NS)
    return node.get("name") if node is not None else ""


def set_box(shape, x=None, y=None, w=None, h=None):
    xf = shape.find("p:spPr/a:xfrm", NS)
    for tag, key, val in (("off", "x", x), ("off", "y", y), ("ext", "cx", w), ("ext", "cy", h)):
        if val is not None:
            xf.find("a:" + tag, NS).set(key, str(round(val * SCALE)))


def build(source, out, native_root):
    assert hashlib.sha256(source.read_bytes()).hexdigest() == SOURCE_HASH, "Input revision changed"
    out.mkdir(parents=True, exist_ok=False)
    with ZipFile(source) as z:
        parts = {p: z.read(p) for p in z.namelist()}
    original = E.fromstring(parts["ppt/slides/slide1.xml"])
    slide = deepcopy(original)
    tree = slide.find("p:cSld/p:spTree", NS)
    objs = {name(s): s for s in tree if name(s)}

    def find(prefix):
        matches = [s for k, s in objs.items() if k == prefix or k.startswith(prefix + ":")]
        assert len(matches) == 1, (prefix, len(matches))
        return matches[0]

    def text_change(prefix, value, **bounds):
        shape = find(prefix)
        nodes = shape.findall(".//a:t", NS)
        assert nodes
        nodes[0].text = value
        for node in nodes[1:]:
            node.text = ""
        if bounds:
            set_box(shape, **bounds)
        shape.find(".//p:cNvPr", NS).set("name", prefix + ": " + value)

    svg = E.Element("{" + SVG + "}svg", nsmap={None: SVG}, width=str(WIDTH),
                    height=str(HEIGHT), viewBox=f"0 0 {WIDTH} {HEIGHT}")
    defs = E.SubElement(svg, "{" + SVG + "}defs")
    for colour in (ORANGE, PURPLE):
        marker = E.SubElement(defs, "{" + SVG + "}marker", id="arr" + colour[1:],
                              markerUnits="strokeWidth", markerWidth="3", markerHeight="3",
                              viewBox="0 0 3 3", refX="3", refY="1.5", orient="auto-start-reverse")
        E.SubElement(marker, "{" + SVG + "}polygon", points="0,0 3,1.5 0,3", fill=colour)

    def add(tag, **attrs):
        return E.SubElement(svg, "{" + SVG + "}" + tag,
                            {k.replace("_", "-"): str(v) for k, v in attrs.items()})

    def path(id, d, colour=ORANGE):
        add("path", id=id, d=d, fill="none", stroke=colour,
            stroke_width=4.8 if colour == ORANGE else 3.2, stroke_linejoin="miter",
            marker_end="url(#arr" + colour[1:] + ")")

    path("pixel-bypass", "M 3060 543.1 L 3060 590 L 3335 590 L 3335 1635 L 3290 1635")
    path("geometry-vdma-pixels", "M 3265 1583.1 L 3265 1605")
    path("pixel-select-to-fifo", "M 3240 1635 L 3220 1635")
    path("tx-register-to-select", "M 3265 1688.1 L 3265 1665", PURPLE)
    add("rect", id="pixel-source-select", x=3240, y=1605, width=50, height=60,
        fill="#FFFFFF", stroke="#29292D", stroke_width=3.8)
    text = add("text", id="pixel-select-label", x=3265, y=1644, font_family="Microsoft YaHei",
               font_size=26, text_anchor="middle", fill="#29292D")
    text.text = "2:1"
    text = add("text", id="pixel-bypass-label", x=3195, y=575, font_family="Microsoft YaHei",
               font_size=28, text_anchor="middle", fill=ORANGE)
    text.text = "像素流直通"
    svg_path = out / "minimal-native-elements.svg"
    E.ElementTree(svg).write(str(svg_path), encoding="utf-8", xml_declaration=True, pretty_print=True)
    subprocess.run([str(native_root / ".venv/bin/python"), "-B", str(native_root / "scripts/run.py"),
                    "--input", str(svg_path), "--out-dir", str(out / "native-elements"),
                    "--aspect", "source", "--slide-width-in", str(WIDTH * SCALE / 914400)], check=True)
    with ZipFile(out / "native-elements/diagrams.pptx") as z:
        fresh = E.fromstring(z.read("ppt/slides/slide1.xml")).find("p:cSld/p:spTree", NS)
    new_objs = {name(s): s for s in fresh if name(s)}
    old_pr = find("vdma-pixels").find("p:spPr", NS)
    new_pr = new_objs["geometry-vdma-pixels"].find("p:spPr", NS)
    for tag in ("xfrm", "custGeom", "prstGeom"):
        previous, current = old_pr.find("a:" + tag, NS), new_pr.find("a:" + tag, NS)
        if previous is not None:
            old_pr.remove(previous)
        if current is not None:
            old_pr.insert(0 if tag == "xfrm" else 1, deepcopy(current))

    # Insert one jump in the existing eMMC path; every original vertex/style stays.
    emmc = find("emmc-physical")
    xf = emmc.find("p:spPr/a:xfrm", NS)
    offset_x = int(xf.find("a:off", NS).get("x"))
    extent_x = int(xf.find("a:ext", NS).get("cx"))
    extent_y = int(xf.find("a:ext", NS).get("cy"))
    route = emmc.find("p:spPr/a:custGeom/a:pathLst/a:path", NS)
    def px(x):
        return str(round((x * SCALE - offset_x) * int(route.get("w")) / extent_x))
    def py(y):
        return str(round(y * SCALE * int(route.get("h")) / extent_y))
    jump_start = E.Element("{" + NS["a"] + "}lnTo")
    E.SubElement(jump_start, "{" + NS["a"] + "}pt", x=px(3343), y="0")
    jump = E.Element("{" + NS["a"] + "}cubicBezTo")
    for x, y in ((3335 + 8/3, 32/3), (3335 - 8/3, 32/3), (3327, 0)):
        E.SubElement(jump, "{" + NS["a"] + "}pt", x=px(x), y=py(y))
    route.insert(2, jump_start)
    route.insert(3, jump)

    set_box(find("roi-fifo"), w=190)
    for key in ("roi-fifo-t0", "roi-fifo-t1"):
        off = find(key).find("p:spPr/a:xfrm/a:off", NS)
        off.set("x", str(int(off.get("x")) - round(35 * SCALE)))
    text_change("roi-title", "图像输出")
    text_change("lvds-tx-detail", "全帧 / ROI 封装", x=3035, w=250)

    new_id = max(int(n.get("id")) for n in slide.findall(".//p:cNvPr", NS)) + 1
    added = []
    for key, shape in new_objs.items():
        if key.startswith("geometry-"):
            continue
        el = deepcopy(shape)
        el.find(".//p:cNvPr", NS).set("id", str(new_id))
        new_id += 1
        tree.append(el)
        added.append(key)
    parts["ppt/slides/slide1.xml"] = serial(slide)
    result = out / "soc_lvds_bypass.pptx"
    with ZipFile(result, "w", ZIP_DEFLATED) as z:
        for p, raw in parts.items():
            z.writestr(p, raw)

    def shapes(root):
        return {s.find(".//p:cNvPr", NS).get("id"): s for s in root.find("p:cSld/p:spTree", NS)
                if E.QName(s).localname in ("sp", "cxnSp")}
    old_shapes, current_shapes = shapes(original), shapes(slide)
    changed = [{"id": sid, "name": name(old)} for sid, old in old_shapes.items()
               if serial(old) != serial(current_shapes[sid])]
    assert len(changed) == 7 and len(added) == 6
    report = dict(source_sha256=SOURCE_HASH, output_sha256=hashlib.sha256(result.read_bytes()).hexdigest(),
                  canvas=[WIDTH, HEIGHT], input_shapes=len(old_shapes), output_shapes=len(current_shapes),
                  changed_existing_objects=changed, removed_objects=[], added_objects=added,
                  unchanged_existing_objects=len(old_shapes) - len(changed),
                  modified_package_parts=["ppt/slides/slide1.xml"], office_tested=False, hardware_tested=False)
    (out / "edit_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"output": str(result), "changed": len(changed), "added": len(added)}, ensure_ascii=False))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--out-dir", required=True, type=Path)
    parser.add_argument("--native-skill-root", required=True, type=Path)
    args = parser.parse_args()
    build(args.input, args.out_dir, args.native_skill_root)

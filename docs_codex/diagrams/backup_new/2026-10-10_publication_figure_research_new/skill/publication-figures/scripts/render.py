"""Local SVG rendering and PDF checks; does not test PowerPoint appearance."""
from pathlib import Path


def render(svg, output, width_mm):
    import cairosvg
    import pymupdf
    from PIL import Image
    stem = svg.stem.removesuffix('.editable')
    pdf, png = output / (stem + '.pdf'), output / (stem + '.png')
    cairosvg.svg2pdf(url=str(svg), write_to=str(pdf))
    cairosvg.svg2png(url=str(svg), write_to=str(png),
                    output_width=round(width_mm / 25.4 * 300))
    with Image.open(png) as src:
        # White background is necessary for transparent SVG outside objects.
        background = Image.new('RGBA', src.size, 'white')
        background.alpha_composite(src.convert('RGBA'))
        background.convert('RGB').save(png, dpi=(300, 300))
        background.convert('L').save(output / (stem + '.gray.png'), dpi=(300, 300))
    with pymupdf.open(pdf) as doc:
        page = doc[0]
        fonts = []
        for row in page.get_fonts(full=True):
            name, ext, kind, data = doc.extract_font(row[0])
            fonts.append({'name': name, 'embedded': bool(data), 'type': kind})
        if abs(page.rect.width * 25.4 / 72 - width_mm) > 0.05:
            raise RuntimeError('PDF physical width mismatch')
        if any(not f['embedded'] for f in fonts):
            raise RuntimeError('PDF has unembedded fonts')
        if page.get_images():
            raise RuntimeError('Pure vector figure unexpectedly contains PDF images')
        return {'pdf': pdf.name, 'png': png.name, 'dpi': 300,
                'page_mm': [page.rect.width*25.4/72, page.rect.height*25.4/72],
                'fonts': fonts, 'pdf_images': len(page.get_images()),
                'office_rendered': False}

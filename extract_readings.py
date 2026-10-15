"""Extract readings page by page and preserve every page as an image. Requires PyMuPDF.

Text-layer PDFs use the embedded text. Scanned PDFs use cached OCR line data in
extract-readings/ocr/<stem>.json (produced with Windows.Media.Ocr; rerunning this
script does not need OCR). Readings not listed in READINGS are skipped.
"""
from pathlib import Path
import json
import re
import pymupdf

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'extract-readings'

# printed: function from PDF page number to the printed page label, or None.
READINGS = [
    dict(file='ecosystemservices.pdf', title='What Are Ecosystem Services?',
         source='Ecological Society of America (ESA) fact sheet, Summer 2000.',
         printed=lambda n: None),
    dict(file='Folke_etal_2004 regime shifts and resilience.pdf',
         title='Regime Shifts, Resilience, and Biodiversity in Ecosystem Management',
         source='Folke, C., Carpenter, S., Walker, B., Scheffer, M., Elmqvist, T., Gunderson, L. & Holling, C.S. (2004). '
                '*Annual Review of Ecology, Evolution, and Systematics* 35:557–581. doi:10.1146/annurev.ecolsys.35.021103.105711. '
                'PDF pages 26–27 are the journal volume contents, not part of the article.',
         printed=lambda n: str(556 + n) if n <= 25 else None),
    dict(file='Foley 2003 regime shifts.pdf',
         title='Regime Shifts in the Sahara and Sahel: Interactions between Ecological and Climatic Systems in Northern Africa',
         source='Foley, J.A., Coe, M.T., Scheffer, M. & Wang, G. (2003). *Ecosystems* 6:524–539. © 2003 Springer-Verlag.',
         printed=lambda n: str(523 + n)),
    dict(file='Strahler_Modern_Physical_Geography_Chapter9.pdf',
         title='Strahler, Modern Physical Geography — Chapter 9: The Soil-Water Balance and Climate',
         source='Strahler, A.N. & Strahler, A.H., *Modern Physical Geography* (course-pack scan). '
                'The scan has no text layer; text below is OCR. Course-pack page numbers (bottom of page) run 155–178. '
                'PDF pages 1–10 are Chapter 9 (book pages 161–170); PDF pages 11–24 are Chapter 16, “Runoff, Streams, and Ground Water” '
                '(book pages 298–311). Book page numbers are recorded below only where OCR read the running header.',
         printed=lambda n: str(154 + n), scanned=True),
]


def ocr_text(rows, width=1700):
    """Order OCR lines into reading order for a two-column page."""
    mid = width / 2
    rows = [r for r in rows if 60 < r[0] < 1620]  # drop binding-hole and margin marks
    rows.sort(key=lambda r: r[1])
    out, left, right = [], [], []
    def flush():
        out.extend(r[3] for r in sorted(left, key=lambda r: r[1]))
        out.extend(r[3] for r in sorted(right, key=lambda r: r[1]))
        left.clear(); right.clear()
    for r in rows:
        x, _, x2, _ = r
        if x2 <= mid + 30:
            left.append(r)
        elif x >= mid - 30:
            right.append(r)
        else:  # spans both columns: chapter title or wide figure label
            flush(); out.append(r[3])
    flush()
    return '\n'.join(out)


def book_page(rows):
    for x, y, x2, t in rows:
        if y < 240 and re.fullmatch(r'\d{3}', t.strip()):
            return t.strip()
    return None


def main():
    for spec in READINGS:
        source = ROOT / 'readings' / spec['file']
        stem = source.stem
        assets = OUT / 'assets' / stem
        assets.mkdir(parents=True, exist_ok=True)
        ocr = None
        if spec.get('scanned'):
            ocr = json.loads((OUT / 'ocr' / (stem + '.json')).read_text(encoding='utf-8'))
        with pymupdf.open(source) as doc:
            sections = [f'# {spec["title"]}', '', '[Back to course index](../Course-KB.md) · [Reading extracts](README.md)', '',
                        f'> Source: [original PDF](<../readings/{source.name}>). {len(doc)} PDF pages. {spec["source"]}', '',
                        'Headings follow PDF page order. Text below is extracted from the original file; source wording and spelling '
                        'are retained, and figures, tables, and layout are preserved in the page images. '
                        + ('OCR text can contain misread characters and stray figure labels, and is ordered by column; the page image is authoritative. '
                           if ocr else 'Two-column text follows the PDF block order. ')
                        + 'These are source extracts, not study notes.']
            for number, page in enumerate(doc, 1):
                image_path = assets / f'page-{number:02}.png'
                if not image_path.exists():
                    page.get_pixmap(matrix=pymupdf.Matrix(1400 / page.rect.width, 1400 / page.rect.width), alpha=False).save(image_path)
                if ocr:
                    rows = ocr['pages'][str(number)]
                    content, label = ocr_text(rows), 'OCR text'
                    bp = book_page(rows)
                else:
                    content, label, bp = page.get_text(sort=False).strip(), 'Extracted text', None
                printed = spec['printed'](number)
                meta = []
                if printed:
                    meta.append(f'course-pack page {printed}' if ocr else f'page {printed}')
                if bp:
                    meta.append(f'book page {bp}')
                sections += ['', f'## PDF page {number}', '']
                if meta:
                    sections += ['Printed: ' + '; '.join(meta) + '.', '']
                sections += [f'[Original page](<../readings/{source.name}#page={number}>)', '',
                             f'![PDF page {number}](<assets/{stem}/{image_path.name}>)', '', f'### {label}', '']
                fence = '`' * max(3, max((len(x) for x in re.findall(r'`+', content)), default=0) + 1)
                sections += [fence + 'text', content or '[No text on this page; see page image.]', fence]
            (OUT / (stem + '.md')).write_text('\n'.join(sections) + '\n', encoding='utf-8')
            print(f'{source.name}: {len(doc)} pages' + (' (cached OCR)' if ocr else ''))


if __name__ == '__main__':
    main()

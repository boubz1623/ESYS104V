"""Build page-referenced reading extracts. Requires PyMuPDF.

Scanned-page OCR is cached in reading-ocr.json. Reviewed descriptions are in
reading-visual-descriptions.json; rerunning this script preserves both.

Shorter readings in SHORT_READINGS also get a rendered image per page. The
Strahler scan's OCR line data (with coordinates, for two-column ordering) is
cached in extract-readings/ocr/<stem>.json.
"""
from pathlib import Path
import json
import re
import pymupdf

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'extract-readings'
BOOK = 'AhrensMeteorologyToday'
TITLES = {
    'The_Earth_System_Chapter_3': 'The Earth System - Chapter 3: Global Energy Balance: The Greenhouse Effect',
    'The_Earth_System_Chapter_4': 'The Earth System - Chapter 4: The Atmospheric Circulation System',
    'The_Earth_System_Chapter_5': 'The Earth System - Chapter 5: The Circulation of the Oceans',
}


def text_block(text):
    fence = '`' * max(3, max((len(x) for x in re.findall(r'`+', text)), default=0)+1)
    return [fence+'text', text.strip(), fence]


def write(path, lines):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('\n'.join(lines)+'\n', encoding='utf-8')


def page_section(doc, number, stem, source_link, ocr, visuals):
    page=doc[number-1]
    cached=ocr.get(stem, {}).get(str(number))
    text=page.get_text(sort=False).strip()
    if not text:
        if not cached:
            raise ValueError(f'Missing OCR or reviewed transcription: {stem} page {number}')
        text=cached['text']
    label=cached.get('printed_page') if cached else page.get_label()
    lines=['',f'## PDF page {number}', '',f'[Original PDF page](<{source_link}#page={number}>)','']
    if label:
        lines += [f'Printed page: {label}.', '']
    if cached and cached.get('scan_footer'):
        lines += [f'Additional scan footer: {cached["scan_footer"]}.', '']
    lines += ['### OCR text' if cached else '### Extracted text', '']
    lines += text_block(text)
    note=visuals.get(stem,{}).get(str(number))
    if note:
        lines += ['', '### Graphic description (editorial)', '', note]
    return lines


def book_groups(doc):
    toc=[x for x in doc.get_toc() if x[0]==1 and x[2]>=24]
    groups=[('Front matter',1,23,'00-Front-matter.md')]
    for i,(_,title,start) in enumerate(toc):
        end=toc[i+1][2]-1 if i+1<len(toc) else len(doc)
        safe=re.sub(r'[^A-Za-z0-9]+','-',title).strip('-')
        groups.append((title,start,end,f'{i+1:02}-{safe}.md'))
    return groups


# printed: function from PDF page number to the printed page label, or None.
SHORT_READINGS = [
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


def short_readings():
    for spec in SHORT_READINGS:
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


def main():
    ocr=json.loads((ROOT/'reading-ocr.json').read_text(encoding='utf-8'))
    visuals=json.loads((ROOT/'reading-visual-descriptions.json').read_text(encoding='utf-8'))
    for stem,title in TITLES.items():
        with pymupdf.open(ROOT/'readings'/f'{stem}.pdf') as doc:
            link=f'../readings/{stem}.pdf'
            lines=[f'# {title}', '', '[Reading index](README.md)', '',
                   f'> Source: [original PDF](<{link}>). All {len(doc)} supplied PDF pages.', '',
                   'The source consists of scanned pages. OCR text is searchable but has not been '
                   'proofread word for word; symbols, numbers, and small figure labels may be misrecognized. '
                   'Use the linked PDF page to verify exact wording and notation. Graphic descriptions '
                   'are separately labelled editorial additions based on visual review. Source-era values are retained.', '']
            if stem.endswith('_5'):
                lines += ['**Source pagination issue:** Printed pages 90-91 are absent from the supplied PDF. '
                          'Printed page 95 appears twice (PDF pages 10 and 11). Both copies are retained; '
                          'no missing source pages have been invented.', '']
            for n in range(1,len(doc)+1):
                lines += page_section(doc,n,stem,link,ocr,visuals)
            write(OUT/f'{stem}.md',lines)
            print(stem,len(doc),flush=True)
    with pymupdf.open(ROOT/'readings'/f'{BOOK}.pdf') as doc:
        groups=book_groups(doc)
        index=['# Meteorology Today - complete reading index', '', '[All readings](../README.md)', '',
               '> Source: [original textbook](../../readings/AhrensMeteorologyToday.pdf). '
               'All 621 PDF pages are included, including front matter, 19 chapters, appendices, glossary, reading list, and index.', '',
               'PDF page numbers identify the physical file pages. Printed page labels are recorded separately. '
               'Source text, including captions, is retained in fenced blocks; graphic descriptions are labelled editorial additions. '
               'Text extraction may not preserve mathematical layout or every label embedded in an image. '
               'Numerical values and dated examples are those of the supplied edition.', '',
               '| Section | PDF pages | Printed labels | Extract |','| --- | --- | --- | --- |']
        for title,start,end,filename in groups:
            lines=[f'# Meteorology Today - {title}', '', '[Book index](Index.md)', '',
                   f'> Source: [original PDF](<../../readings/{BOOK}.pdf#page={start}>). '
                   f'PDF pages {start}-{end}.', '',
                   'Source text and captions are extracted in source order. Graphic descriptions are editorial additions. '
                   'Refer to the PDF for exact graphic labels, tables, and mathematical layout.', '']
            for _,heading,n in [t for t in doc.get_toc() if t[0]==2 and start<=t[2]<=end]:
                lines.append(f'- [{heading.strip()}](#pdf-page-{n})')
            for n in range(start,end+1):
                lines += page_section(doc,n,BOOK,f'../../readings/{BOOK}.pdf',ocr,visuals)
            write(OUT/BOOK/filename,lines)
            index.append(f'| {title} | {start}-{end} | {doc[start-1].get_label()} to {doc[end-1].get_label()} | [Text](<{filename}>) |')
        write(OUT/BOOK/'Index.md',index)
        print(BOOK,len(doc),len(groups),'sections',flush=True)
    short_readings()


if __name__=='__main__':
    main()

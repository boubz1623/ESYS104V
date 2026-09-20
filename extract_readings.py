"""Build page-referenced reading extracts. Requires PyMuPDF.

Scanned-page OCR is cached in reading-ocr.json. Reviewed descriptions are in
reading-visual-descriptions.json; rerunning this script preserves both.
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


if __name__=='__main__':
    main()

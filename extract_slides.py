"""Extract lecture text and preserve every slide as an image. Requires PyMuPDF.

For the ODP, text and embedded figures come directly from its ZIP contents.
Reviewed additions are stored in lecture-transcriptions.json and survive reruns.
Visual descriptions and review coverage are in lecture-visual-descriptions.json.
"""
from pathlib import Path
import json
import re
import xml.etree.ElementTree as ET
import zipfile
import pymupdf

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'extract-slides'
NS = {k: f'urn:oasis:names:tc:opendocument:xmlns:{v}:1.0' for k, v in
      [('draw', 'drawing'), ('text', 'text'), ('office', 'office'), ('presentation', 'presentation')]}


def odp_text(path):
    with zipfile.ZipFile(path) as archive:
        root = ET.fromstring(archive.read('content.xml'))
    pages = root.findall('./office:body/office:presentation/draw:page', NS)
    def text(node):
        value = node.text or ''
        for child in node:
            if child.tag == '{' + NS['text'] + '}s':
                value += ' ' * int(child.get('{' + NS['text'] + '}c', '1'))
            elif child.tag == '{' + NS['text'] + '}tab':
                value += '\t'
            elif child.tag == '{' + NS['text'] + '}line-break':
                value += '\n'
            elif child.tag != '{' + NS['text'] + '}page-number':
                value += text(child)
            value += child.tail or ''
        return value
    output = []
    for page in pages:
        # Speaker notes are not visible slide content.
        for notes in page.findall('presentation:notes', NS):
            page.remove(notes)
        lines = [text(p).strip() for p in page.findall('.//text:p', NS)]
        output.append('\n'.join(line for line in lines if line and line != '<number>'))
    return output


def main():
    additions_path = ROOT / 'lecture-transcriptions.json'
    additions = json.loads(additions_path.read_text(encoding='utf-8')) if additions_path.exists() else {}
    visuals_path = ROOT / 'lecture-visual-descriptions.json'
    visuals = json.loads(visuals_path.read_text(encoding='utf-8')) if visuals_path.exists() else {}
    for source in sorted((ROOT / 'slides').iterdir()):
        if source.suffix.lower() not in ('.pdf', '.odp'):
            continue
        is_pdf = source.suffix.lower() == '.pdf'
        if not is_pdf:
            extract_odp(source, additions, visuals)
            continue
        with pymupdf.open(source) as doc:
            # Source block order avoids interleaving side-by-side text columns.
            texts = [page.get_text(sort=False).strip() for page in doc]
            assets = OUT / 'assets' / source.stem
            assets.mkdir(parents=True, exist_ok=True)
            sections = [f'# {source.stem}', '', '[Back to course index](../Course-KB.md)', '',
                        f'> Source: [original lecture](<../slides/{source.name}>). {len(doc)} slides.', '',
                        'Slide numbers follow source order. Text below is extracted from the original file; '
                        'source wording and spelling are retained. The text layer can contain hidden or covered text; the slide image shows what is visible. Each slide image preserves figures, layout, '
                        'and text embedded in images. Image text is searchable only where a labelled visual transcription is included. '
                        'Labelled visual descriptions explain the visible content and relationships; they are editorial descriptions, not instructor quotations. '
                        'Repeated slides are retained. These are source extracts, not study notes.']
            for number, (page, content) in enumerate(zip(doc, texts), 1):
                image_path = assets / f'slide-{number:03}.png'
                if not image_path.exists():
                    page.get_pixmap(matrix=pymupdf.Matrix(1600 / page.rect.width, 1600 / page.rect.width), alpha=False).save(image_path)
                link = f'../slides/{source.name}' + (f'#page={number}' if source.suffix.lower() == '.pdf' else '')
                sections += ['', f'## Slide {number}', '', f'[Original source](<{link}>)', '',
                             f'![Slide {number}](<assets/{source.stem}/{image_path.name}>)', '', '### Extracted text', '']
                fence = '`' * max(3, max((len(x) for x in re.findall(r'`+', content)), default=0) + 1)
                sections += [fence + 'text', content or '[No embedded text on this slide; see slide image.]', fence]
                extra = additions.get(source.stem, {}).get(str(number))
                if extra:
                    sections += ['', '### Visual transcription / extraction note', '', extra]
                append_visual(sections, visuals, source.stem, number)
            (OUT / (source.stem + '.md')).write_text('\n'.join(sections) + '\n', encoding='utf-8')
            print(f'{source.name}: {len(doc)} slides')


def append_visual(sections, visuals, stem, number):
    entry = visuals.get(stem, {}).get(str(number), {})
    if entry.get('description'):
        sections += ['', '### Visual description', '', entry['description']]


def extract_odp(source, additions, visuals):
    texts = odp_text(source)
    assets = OUT / 'assets' / source.stem
    assets.mkdir(parents=True, exist_ok=True)
    sections = [f'# {source.stem}', '', '[Back to course index](../Course-KB.md)', '',
                f'> Source: [original ODP](<../slides/{source.name}>). {len(texts)} slides.', '',
                'Text and embedded figures are extracted directly from the ODP. Slide order and source wording are retained. '
                'Figures below are original embedded assets, not full-slide previews; positions, crops, arrows, '
                'and other drawing objects remain in the ODP. PowerPoint conversion was checked and rejected because it omitted content. '
                'Visual descriptions use the embedded figures together with slide text and the ODP object positions, crops, and drawing geometry; they are editorial descriptions, not instructor quotations. '
                'Speaker-note page-number placeholders are excluded. These are source extracts, not study notes.']
    with zipfile.ZipFile(source) as archive:
        root = ET.fromstring(archive.read('content.xml'))
        pages = root.findall('./office:body/office:presentation/draw:page', NS)
        for number, (page, content) in enumerate(zip(pages, texts), 1):
            sections += ['', f'## Slide {number}', '', f'[Original ODP](<../slides/{source.name}>)', '', '### Extracted text', '',
                         '```text', content or '[No embedded text on this slide; see original figures below.]', '```']
            figures = []
            for notes in page.findall('presentation:notes', NS):
                page.remove(notes)
            for element in page.findall('.//draw:image', NS):
                href = element.get('{http://www.w3.org/1999/xlink}href')
                if not href or href in figures:
                    continue
                if href not in archive.namelist():
                    raise ValueError(f'Missing ODP image: {href}')
                figures.append(href)
                target = assets / Path(href).name
                target.write_bytes(archive.read(href))
            if figures:
                sections += ['', '### Original embedded figures', '']
                sections += [f'![Slide {number}, figure {i}](<assets/{source.stem}/{Path(href).name}>)' for i, href in enumerate(figures, 1)]
            extra = additions.get(source.stem, {}).get(str(number))
            if extra:
                sections += ['', '### Visual transcription / extraction note', '', extra]
            append_visual(sections, visuals, source.stem, number)
    (OUT / (source.stem + '.md')).write_text('\n'.join(sections) + '\n', encoding='utf-8')
    print(f'{source.name}: {len(texts)} slides (native ODP text and figures)')


if __name__ == '__main__':
    main()

# Reading extracts

[Back to course index](../Course-KB.md)

Full page-by-page extracts are available for all eight supplied readings. Each page section identifies its PDF page, links to that page in the original, records a printed page label when available, and keeps extracted/OCR text distinct from editorial graphic descriptions.

| Reading | PDF pages | Extract |
| --- | ---: | --- |
| The Earth System, Chapter 3 | 21 | [Chapter 3](The_Earth_System_Chapter_3.md) |
| The Earth System, Chapter 4 | 27 | [Chapter 4](The_Earth_System_Chapter_4.md) |
| The Earth System, Chapter 5 | 23 | [Chapter 5](The_Earth_System_Chapter_5.md) |
| Ahrens, *Meteorology Today*, ninth edition | 621 | [Book index and chapter extracts](AhrensMeteorologyToday/Index.md) |

The textbook is split into 33 navigable files: front matter, 19 chapters, appendices A–J, glossary, additional reading, and index. The chapters and reference sections include descriptions of informative diagrams, maps, plots, and tables based on visual review. Captions remain part of the source text.

The three *Earth System* PDFs are scans and were transcribed with OCR. Their text has not been proofread word for word; small labels, symbols, and numbers may be misread, so consult the linked source for exact wording and notation. Printed page numbers are recorded separately from PDF page numbers. In Chapter 5, printed pages 90–91 are absent from the supplied file and printed page 95 is duplicated on PDF pages 10–11; the supplied pages are retained without inventing missing content.

The textbook has embedded text, while some equations and labels are part of images. Check the original page for exact table values and complex mathematical or graphic layout. Historical values and examples reflect the supplied edition.

## Short readings (with page images)

| Reading | Pages | Method |
| --- | --- | --- |
| [Strahler — Modern Physical Geography, Ch. 9](Strahler_Modern_Physical_Geography_Chapter9.md) | 24 (course-pack 155–178) | OCR (scan has no text layer) |
| [Folke et al. 2004](<Folke_etal_2004 regime shifts and resilience.md>) | 27 (printed 557–581, plus 2 journal contents pages) | Text layer |
| [Foley et al. 2003](<Foley 2003 regime shifts.md>) | 16 (printed 524–539) | Text layer |
| [ESA — What are ecosystem services?](ecosystemservices.md) | 2 | Text layer |

Every page also has a rendered image. The Strahler scan also covers Chapter 16 ground-water pages (PDF pages 11–24). Its OCR text is ordered by column and contains stray figure labels and some misread characters; the page images are authoritative.

## Regeneration

From the parent directory (`ESYS104V`), run `python extract_readings.py` (requires PyMuPDF). It regenerates every reading from saved data without rerunning OCR: The Earth System and Ahrens from `../reading-ocr.json` and `../reading-visual-descriptions.json`, and the short readings from the script's `SHORT_READINGS` table, with Strahler OCR line data cached in `ocr/<stem>.json` (Windows.Media.Ocr, pages at 200 dpi). Page PNGs for the short readings are cached; delete them to re-render.

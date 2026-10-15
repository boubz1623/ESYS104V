# Reading extracts

[Back to course index](../Course-KB.md)

Future searchable Markdown versions of readings go here. Short readings can use one file each. For a long book, create a source folder with an `Index.md` and separate chapter or section files once its contents have been inspected.

Each extract should identify the original in `../readings/`, its chapter or section, and its page range. Retain stable PDF page headings such as `## PDF page 25` and record printed page numbers separately when they differ. The index should track which chapters have been extracted and reviewed.

Keep the full original intact. Preserve source text separately from summaries and label any figure descriptions or editorial additions.

## Extracted

| Reading | Pages | Method |
| --- | --- | --- |
| [Strahler — Modern Physical Geography, Ch. 9](Strahler_Modern_Physical_Geography_Chapter9.md) | 24 (course-pack 155–178) | OCR (scan has no text layer) |
| [Folke et al. 2004](<Folke_etal_2004 regime shifts and resilience.md>) | 27 (printed 557–581, plus 2 journal contents pages) | Text layer |
| [Foley et al. 2003](<Foley 2003 regime shifts.md>) | 16 (printed 524–539) | Text layer |
| [ESA — What are ecosystem services?](ecosystemservices.md) | 2 | Text layer |

Every page also has a rendered image. The Strahler scan also covers Chapter 16 ground-water pages (PDF pages 11–24). Its OCR text is ordered by column and contains stray figure labels and some misread characters; the page images are authoritative.

Pending: The Earth System chapters 3–5 and Ahrens, *Meteorology Today*.

## Regeneration

Run `python extract_readings.py` (requires PyMuPDF). Readings are listed in the script's `READINGS` table. OCR for scanned readings is cached in `ocr/<stem>.json` (Windows.Media.Ocr, pages at 200 dpi), so regenerating does not rerun OCR. Page PNGs are cached; delete them to re-render.

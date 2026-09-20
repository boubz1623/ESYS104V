# Lecture extracts

[Back to course index](../Course-KB.md)

Lectures 1–5 are available from the course index: **262 slides** in five Markdown files. Headings such as `## Slide 1` provide stable `#slide-1` anchors. Slide numbers are positions in the original file, including repeated slides.

## What is preserved

- Embedded source text, with original wording and spelling, in fenced text blocks. PDF text uses source block order to avoid interleaving adjacent columns.
- A rendered image for each of the 204 PDF pages, with a direct original-PDF page link.
- All 66 unique embedded figures from the 58-slide ODP, placed under the slides where they occur. These are uncropped source assets; the ODP retains their exact placement, crops, arrows, and other drawing objects.
- Labelled visual transcriptions or extraction notes on 99 slides, including the image-based schedule, composition tables, mineral tables, resource tables, and energy-balance equations. These additions describe the supplied material; they do not answer exercises or add study notes.

## Review and limitations

All PDF pages and all unique ODP figures were visually inspected using contact sheets, with larger views for selected tables and formulas. Embedded text was reviewed separately. Native ODP text was used after visual checks showed that PowerPoint's PDF conversion omitted content. The incomplete conversion is not used in these extracts.

The PDF text layer sometimes contains hidden or covered titles; the visible slide image takes precedence. Some graph labels, screenshot body text, and numerical flow diagrams are preserved visually without exhaustive transcription. These extracts do not claim that every pixel of text is searchable. Original spelling, dates, data, and differing formulas are retained, with selected discrepancies explicitly noted. This is extraction review, not external fact-checking of the instructor's claims.

## Regeneration

From the vault folder, run `python extract_slides.py` (requires PyMuPDF). The script reads originals in `slides/` and regenerates Markdown plus assets. Reviewed transcriptions are stored in `lecture-transcriptions.json` and reapplied by source filename and slide number.

When replacing a source or reordering slides, review those transcriptions against the new source. The script caches existing PDF page PNGs: remove the affected lecture's generated PNGs before regenerating changed slides. Original PDFs and the ODP are never edited by the extractor.

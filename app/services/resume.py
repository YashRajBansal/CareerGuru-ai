"""Text extraction and a documented resume review rubric, not a commercial ATS."""
import io
import re
import zipfile
from pathlib import Path
from pypdf import PdfReader
from docx import Document

def extract(upload):
    ext = Path(upload.filename or '').suffix.lower()
    raw = upload.read(4*1024*1024+1)
    if len(raw) > 4*1024*1024:
        raise ValueError('Resume must be under 4 MB.')
    try:
        if ext == '.txt':
            text = raw.decode('utf-8-sig')
        elif ext == '.pdf' and raw.startswith(b'%PDF'):
            pdf = PdfReader(io.BytesIO(raw))
            if len(pdf.pages) > 15 or pdf.is_encrypted:
                raise ValueError('Use an unencrypted resume with at most 15 pages.')
            text = '\n'.join(page.extract_text() or '' for page in pdf.pages)
        elif ext == '.docx' and raw.startswith(b'PK'):
            with zipfile.ZipFile(io.BytesIO(raw)) as archive:
                if sum(x.file_size for x in archive.infolist()) > 20*1024*1024:
                    raise ValueError('The document expands beyond the supported size.')
            doc = Document(io.BytesIO(raw))
            text = '\n'.join(p.text for p in doc.paragraphs)
            text += '\n' + '\n'.join(' | '.join(c.text for c in r.cells) for t in doc.tables for r in t.rows)
        else:
            raise ValueError('Upload a valid PDF, DOCX or UTF-8 TXT file.')
    except ValueError:
        raise
    except Exception as exc:
        raise ValueError('We could not read this document. Try a text-based PDF or TXT file.') from exc
    if len(text.strip()) < 80:
        raise ValueError('Not enough readable text. Scanned PDFs need OCR first; try pasting text instead.')
    return text[:16000]


# Keep the original import contract while using the career/evidence scoring service.
from services.resume_scoring import evaluate

import pdfplumber
from .utils import parse_date_ddmmyyyy

def parse_pdf_file(pdf_file_obj):
    registros = []
    with pdfplumber.open(pdf_file_obj) as pdf:
        for page in pdf.pages:
            table = page.extract_table()
            if not table:
                continue
            for row in table:
                if not row or not row[0]:
                    continue
                try:
                    fecha = parse_date_ddmmyyyy(row[0])
                except Exception:
                    continue

                # HI y HF están en las columnas 15 y 16
                hi = row[15] if len(row) > 15 else None
                hf = row[16] if len(row) > 16 else None

                # Guardamos el registro aunque falte HI/HF
                registros.append({
                    'fecha': fecha,
                    'hi': hi,
                    'hf': hf
                })
    return registros


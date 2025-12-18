import re
from datetime import datetime
import pdfplumber

def extraer_horas(cell):
    """Devuelve todas las horas válidas encontradas en una celda multilínea."""
    horas = []
    if not cell:
        return horas
    for line in cell.splitlines():
        line = line.strip()
        if re.match(r"^\d{2}:\d{2}$", line):
            horas.append(line)
    return horas

def parse_pdf(path_pdf):
    registros = []
    with pdfplumber.open(path_pdf) as pdf:
        for page in pdf.pages:
            table = page.extract_table()
            if not table:
                continue

            for row in table[1:]:  # saltar cabecera
                fecha_str = (row[0] or "").strip()
                try:
                    datetime.strptime(fecha_str, "%d/%m/%Y")
                except Exception:
                    continue

                hi_vals = extraer_horas(row[1] or "")
                hf_vals = extraer_horas(row[2] or "")

                for hi_str, hf_str in zip(hi_vals, hf_vals):
                    registros.append({
                        "fecha": fecha_str,
                        "HI": hi_str,
                        "HF": hf_str
                    })
    return registros

# Ejemplo de uso
if __name__ == "__main__":
    datos = parse_pdf("octubre.pdf")
    for d in datos:
        print(d)

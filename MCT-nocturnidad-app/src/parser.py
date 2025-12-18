import re
import pdfplumber
from datetime import datetime

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

                # Validación: si faltan horas, saltamos la fila
                if not hi_vals or not hf_vals:
                    continue

                # Emparejar todas las horas posibles
                max_pairs = min(len(hi_vals), len(hf_vals))
                for i in range(max_pairs):
                    registros.append({
                        "fecha": fecha_str,
                        "HI": hi_vals[i],
                        "HF": hf_vals[i]
                    })

                # Advertencia opcional si hay desajuste
                if len(hi_vals) != len(hf_vals):
                    print(f"Advertencia: desajuste en {fecha_str} (HI={hi_vals}, HF={hf_vals})")

    return registros

# --- Ejemplo de uso ---
if __name__ == "__main__":
    datos = parse_pdf("octubre.pdf")
    for d in datos:
        print(d)

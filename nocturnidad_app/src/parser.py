import pdfplumber
import re

def parse_pdf(file):
    registros = []
    try:
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                # 1) Intento con tabla
                table = page.extract_table()
                if table:
                    header = table[0]
                    if "HI" in header and "HF" in header:
                        idx_hi = header.index("HI")
                        idx_hf = header.index("HF")
                        for row in table[1:]:
                            fecha = row[0]
                            hi_cell = row[idx_hi] if len(row) > idx_hi else None
                            hf_cell = row[idx_hf] if len(row) > idx_hf else None
                            if hi_cell and hf_cell:
                                hi_list = hi_cell.split()
                                hf_list = hf_cell.split()
                                for hi, hf in zip(hi_list, hf_list):
                                    registros.append({"fecha": fecha, "hi": hi.strip(), "hf": hf.strip()})

                # 2) Fallback: buscar en texto con regex
                if not registros:
                    text = page.extract_text() or ""
                    for line in text.splitlines():
                        fecha_m = re.search(r"\b(\d{2}/\d{2}/\d{4})\b", line)
                        hi_m = re.findall(r"\b([0-2]?\d:[0-5]\d)\b", line)
                        hf_m = re.findall(r"\b([0-2]?\d:[0-5]\d)\b", line)
                        if fecha_m and hi_m and hf_m:
                            fecha = fecha_m.group(1)
                            # Emparejar horas de dos en dos
                            for i in range(0, len(hi_m), 2):
                                try:
                                    registros.append({
                                        "fecha": fecha,
                                        "hi": hi_m[i],
                                        "hf": hi_m[i+1]
                                    })
                                except IndexError:
                                    continue
    except Exception as e:
        print("Error al leer PDF:", e)

    print("Registros extraídos:", registros)  # 🔎 debug
    return registros

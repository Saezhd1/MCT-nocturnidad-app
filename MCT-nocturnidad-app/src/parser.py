# parser.py
import pdfplumber
import re

def extraer_fechas_horas(pdf_path):
    resultados = []

    # Abrimos el PDF
    with pdfplumber.open(pdf_path) as pdf:
        for pagina in pdf.pages:
            texto = pagina.extract_text()
            if not texto:
                continue

            # Dividimos por líneas
            for linea in texto.split("\n"):
                # Detectar fecha en formato dd/mm/yyyy
                match_fecha = re.match(r"(\d{2}/\d{2}/\d{4})", linea)
                if match_fecha:
                    fecha = match_fecha.group(1)

                    # Buscar horarios en la línea (formato HH:MM)
                    horarios = re.findall(r"\d{2}:\d{2}", linea)

                    if len(horarios) >= 2:
                        hi = horarios[0]  # primer horario
                        hf = horarios[1]  # segundo horario
                        resultados.append({
                            "fecha": fecha,
                            "HI": hi,
                            "HF": hf
                        })

    return resultados


if __name__ == "__main__":
    archivo_pdf = "Realizado_agosto_2022_12832.pdf"  # cambia por tu ruta real
    datos = extraer_fechas_horas(archivo_pdf)

    # Mostrar resultados
    for item in datos:
        print(f"{item['fecha']} | HI: {item['HI']} | HF: {item['HF']}")


def parse_pdf(file):
    registros = []
    current_fecha = None
    try:
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                cols = _find_columns(page)
                # Palabras con tolerancias pequeñas para que se agrupen por línea
                words = page.extract_words(x_tolerance=3, y_tolerance=3, use_text_flow=False)
                
                # Agrupar por línea (clave: y redondeada)
                lines = {}
                for w in words:
                    if w["top"] <= cols["header_bottom"]:
                        continue
                    y_key = round(w["top"], 1)
                    lines.setdefault(y_key, []).append(w)

                # Ordenar por vertical
                for y in sorted(lines.keys()):
                    row_words = sorted(lines[y], key=lambda k: k["x0"])
                    
                    fecha_tokens, hi_tokens, hf_tokens = [], [], []
                    for w in row_words:
                        t = (w.get("text") or "").strip()
                        xmid = (w["x0"] + w["x1"]) / 2.0
                        if _in_range(xmid, cols["fecha"]):
                            fecha_tokens.append(t)
                        elif _in_range(xmid, cols["hi"]):
                            hi_tokens.append(t)
                        elif _in_range(xmid, cols["hf"]):
                            hf_tokens.append(t)

                    # Consolidar
                    fecha_val = " ".join(fecha_tokens).strip()
                    hi_raw = " ".join(hi_tokens).strip()
                    hf_raw = " ".join(hf_tokens).strip()

                    # Si aparece una nueva fecha, actualiza el marcador
                    if fecha_val:
                        current_fecha = fecha_val
                        continue  # no asociar horas en la misma línea que la fecha
                    
                    # Si hay horas y ya tenemos una fecha activa, asociarlas a esa fecha
                    if current_fecha and (hi_raw or hf_raw):
                        hi_list = [x for x in hi_raw.split() if ":" in x and x.count(":") == 1]
                        hf_list = [x for x in hf_raw.split() if ":" in x and x.count(":") == 1]

                        # Asociar todas las combinaciones de HI y HF
                        for hi in hi_list:
                            for hf in hf_list:
                                registros.append({
                                    "fecha": current_fecha,
                                    "hi": hi,
                                    "hf": hf,
                                    "principal": True
                                })

        print(f"[parser] Total registros extraídos: {len(registros)}")
    except Exception as e:
        print("[parser] Error al leer PDF:", e)
    return registros
    
# 🔑 NUEVO: función para varios PDFs
def parse_multiple_pdfs(files):
    """
    files: lista de rutas de archivos PDF
    Devuelve un diccionario con resultados por archivo
    """
    resultados = {}
    for f in files:
        print(f"[parser] Procesando: {os.path.basename(f)}")
        registros = parse_pdf(f)
        # Añadir origen al registro
    for r in registros:
        r["archivo"] = os.path.basename(f)
        resultados[f] = registros
        print(f"[parser] {len(registros)} registros extraídos de {os.path.basename(f)}")
    return resultados
    
    print(f"[parser] Registros extraídos: {len(registros)}")
    for r in registros[:6]:
        print("[parser] Ej:", r)
    return registros









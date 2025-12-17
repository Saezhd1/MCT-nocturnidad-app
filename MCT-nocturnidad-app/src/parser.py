import pdfplumber
import re

def _in_range(xmid, xr, tol=2):
    return xr[0] - tol <= xmid <= xr[1] + tol

def _find_columns(page):
    words = page.extract_words(use_text_flow=True)
    fecha_x = hi_x = hf_x = None
    header_bottom = page.bbox[1] + 40  # fallback

    for w in words:
        t = (w.get("text") or "").strip().lower()
        if t == "fecha":
            fecha_x = (w["x0"], w["x1"]); header_bottom = max(header_bottom, w["bottom"])
        elif t == "hi":
            hi_x = (w["x0"], w["x1"]); header_bottom = max(header_bottom, w["bottom"])
        elif t == "hf":
            hf_x = (w["x0"], w["x1"]); header_bottom = max(header_bottom, w["bottom"])

    # Fallback si no encuentra cabeceras (ajustado al modelo)
    if not (fecha_x and hi_x and hf_x):
        x0_page, x1_page = page.bbox[0], page.bbox[2]
        width = x1_page - x0_page
        fecha_x = (x0_page + 0.06 * width, x0_page + 0.22 * width)
        hi_x    = (x0_page + 0.69 * width, x0_page + 0.81 * width)
        hf_x    = (x0_page + 0.81 * width, x0_page + 0.95 * width)

    # Margen adicional bajo cabeceras
    header_bottom += 4
    return {"fecha": fecha_x, "hi": hi_x, "hf": hf_x, "header_bottom": header_bottom}

def _horas_validas(tokens):
    return [x for x in tokens.split() if x.count(":") == 1]

def _normalizar_hora(hhmm):
    # Convierte "27:00" -> "03:00" sin cambiar fecha
    try:
        hh, mm = hhmm.split(":")
        hh_i, mm_i = int(hh), int(mm)
        hh_i = hh_i % 24
        return f"{hh_i:02d}:{mm_i:02d}"
    except Exception:
        return hhmm

def parse_pdf(file):
    registros = []
    try:
        with pdfplumber.open(file) as pdf:
            last_fecha = None
            pending_rows = []  # filas con horas pero sin fecha; se asignan a la próxima fecha válida

            for page in pdf.pages:
                cols = _find_columns(page)
                words = page.extract_words(x_tolerance=2, y_tolerance=2, use_text_flow=False)

                # Agrupar por y
                lines = {}
                for w in words:
                    if w["top"] <= cols["header_bottom"]:
                        continue
                    y_key = round(w["top"], 1)
                    lines.setdefault(y_key, []).append(w)

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

                    fecha_val = " ".join(fecha_tokens).strip()
                    hi_raw = " ".join(hi_tokens).strip()
                    hf_raw = " ".join(hf_tokens).strip()

                    hi_list = _horas_validas(hi_raw)
                    hf_list = _horas_validas(hf_raw)

                    # Si hay nueva fecha, actualizar y volcar pendientes
                    if fecha_val:
                        last_fecha = fecha_val
                        # Volcar cualquier fila pendiente asociándola a esta fecha
                        for pr in pending_rows:
                            pr["fecha"] = last_fecha
                            registros.append(pr)
                        pending_rows = []

                    # Si no hay horas, saltar
                    if not (hi_list or hf_list):
                        continue

                    # Normalizar horas
                    hi_list = [_normalizar_hora(x) for x in hi_list]
                    hf_list = [_normalizar_hora(x) for x in hf_list]

                    # Regla principal/secundaria de Daniel
                    if hi_list and hf_list:
                        # Principal
                        principal_hi = hi_list[0]
                        principal_hf = hf_list[-1]
                        row = {
                            "fecha": last_fecha if last_fecha else "",  # se corregirá vía buffer si aún no hay fecha
                            "hi": principal_hi,
                            "hf": principal_hf,
                            "principal": True
                        }
                        if last_fecha:
                            registros.append(row)
                        else:
                            pending_rows.append(row)

                        # Secundaria si hay dos y dos
                        if len(hi_list) >= 2 and len(hf_list) >= 2:
                            row2 = {
                                "fecha": last_fecha if last_fecha else "",
                                "hi": hi_list[1],
                                "hf": hf_list[0],
                                "principal": False
                            }
                            if last_fecha:
                                registros.append(row2)
                            else:
                                pending_rows.append(row2)

            # Si quedan pendientes al final del documento sin fecha, no emitirlos
            if pending_rows:
                print(f"[parser] Filas pendientes descartadas por falta de fecha: {len(pending_rows)}")

    except Exception as e:
        print("[parser] Error al leer PDF:", e)

    print(f"[parser] Registros extraídos: {len(registros)}")
    for r in registros[:6]:
        print("[parser] Ej:", r)
    return registros

import re
import pdfplumber

def normalizar_hora(h):
    """
    Convierte horas como '5:00', '05.00' en formato uniforme 'HH:MM'
    """
    partes = h.replace(".", ":").split(":")
    return f"{int(partes[0]):02d}:{partes[1]}"

def parse_pdf(file):
    registros = []

    with pdfplumber.open(file) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            text = page.extract_text()
            if not text:
                continue

            for line in text.splitlines():
                # Buscar fecha en formato DD/MM/AAAA o DD-MM-AAAA
                fecha_match = re.search(r"\d{2}[/-]\d{2}[/-]\d{4}", line)
                if not fecha_match:
                    continue
                fecha = fecha_match.group(0).replace("-", "/")

                # Buscar horas (acepta 05:00, 5:00, 05.00, 5.00)
                horas = re.findall(r"\d{1,2}[:.]\d{2}", line)

                if len(horas) >= 2:
                    hi = normalizar_hora(horas[0])
                    hf = normalizar_hora(horas[1])

                    registros.append({
                        "fecha": fecha,
                        "hi": hi,
                        "hf": hf,
                        "principal": line.strip()
                    })

    print("[parser] Registros extraídos:", len(registros))
    return registros

import pdfplumber

def parse_pdf(file):
    """
    Extrae registros de HI y HF desde un PDF subido.
    Devuelve una lista de diccionarios con {'fecha': str, 'hi': str, 'hf': str}.
    """
    registros = []
    try:
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                table = page.extract_table()
                if not table:
                    continue
                for row in table[1:]:  # saltamos cabecera
                    try:
                        fecha = row[0]
                        hi = row[15] if len(row) > 15 else None
                        hf = row[16] if len(row) > 16 else None
                        if hi and hf:
                            registros.append({
                                "fecha": fecha,
                                "hi": hi,
                                "hf": hf
                            })
                    except Exception:
                        continue
    except Exception as e:
        print("Error al leer PDF:", e)

    return registros

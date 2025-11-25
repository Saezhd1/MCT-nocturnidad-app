import pdfplumber

def parse_pdf(file):
    registros = []
    try:
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                table = page.extract_table()
                if not table:
                    continue
                for row in table[1:]:
                    fecha = row[0]
                    hi_cell = row[15] if len(row) > 15 else None
                    hf_cell = row[16] if len(row) > 16 else None
                    if fecha and hi_cell and hf_cell:
                        hi_list = hi_cell.split()
                        hf_list = hf_cell.split()
                        if hi_list and hf_list:
                            # tramo principal: primera HI con última HF
                            registros.append({
                                "fecha": fecha,
                                "hi": hi_list[0],
                                "hf": hf_list[-1],
                                "principal": True
                            })
                            # tramos secundarios: pares intermedios
                            for i in range(1, min(len(hi_list), len(hf_list))):
                                registros.append({
                                    "fecha": fecha,
                                    "hi": hi_list[i],
                                    "hf": hf_list[i-1],
                                    "principal": False
                                })
    except Exception as e:
        print("Error al leer PDF:", e)

    print("Registros extraídos:", registros)
    return registros

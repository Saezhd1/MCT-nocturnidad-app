from collections import defaultdict

def agregar_resumen(resultados):
    """
    Construye resumen mensual y global a partir de los registros procesados.
    Cada registro debe ser un dict con al menos:
      - 'fecha' en formato DD/MM/AAAA
      - 'minutos' (int)
      - 'importe' (float)
    """

    resumen_mensual = defaultdict(lambda: {"minutos": 0, "importe": 0.0, "dias": 0})
    total_minutos = 0
    total_importe = 0.0
    total_dias = 0

    for r in resultados:
        # Asegurar que r es un dict
        if not isinstance(r, dict):
            continue

        fecha = str(r.get("fecha", "")).strip()
        if not fecha:
            continue

        partes = fecha.split("/")
        if len(partes) < 3:
            continue

        dia, mes, anio = partes[0], partes[1], partes[2]

        minutos = r.get("minutos", 0)
        importe = r.get("importe", 0.0)

        # Solo contar si hay minutos nocturnos > 0
        if minutos > 0:
            clave = f"{mes}/{anio}"
            resumen_mensual[clave]["minutos"] += minutos
            resumen_mensual[clave]["importe"] += importe
            resumen_mensual[clave]["dias"] += 1

            total_minutos += minutos
            total_importe += importe
            total_dias += 1

    # Convertir a lista ordenada por mes/año
    resumen_mensual_list = []
    for clave, datos in sorted(resumen_mensual.items()):
        resumen_mensual_list.append({
            "mes_anio": clave,
            "minutos": datos["minutos"],
            "importe": round(datos["importe"], 2),
            "dias": datos["dias"]
        })

    resumen_global = {
        "total_minutos": total_minutos,
        "total_importe": round(total_importe, 2),
        "total_dias": total_dias
    }

    return resumen_mensual_list, resumen_global

from collections import defaultdict

def agregar_resumen(resultados_por_pdf):
    resumen = {
        "por_mes": defaultdict(lambda: {"minutos": 0, "importe": 0.0, "dias": 0}),
        "global": {"minutos": 0, "importe": 0.0, "dias": 0}
    }

    for doc in resultados_por_pdf:
        dias_con_nocturnidad = set()
        for d in doc.get("dias", []):
            minutos = d.get("minutos_nocturnos", 0)
            importe = float(d.get("importe", 0.0))
            fecha = d.get("fecha", "")

            if minutos > 0 and fecha:
                partes = fecha.split("/")
                if len(partes) == 3:
                    dia, mes, anio = partes
                    clave = f"{mes}/{anio}"

                    resumen["por_mes"][clave]["minutos"] += minutos
                    resumen["por_mes"][clave]["importe"] += importe

                    if fecha not in dias_con_nocturnidad:
                        resumen["por_mes"][clave]["dias"] += 1
                        resumen["global"]["dias"] += 1
                        dias_con_nocturnidad.add(fecha)

                    resumen["global"]["minutos"] += minutos
                    resumen["global"]["importe"] += importe
                else:
                    print(f"[aggregator] Fecha inválida: {fecha}")

    return resumen

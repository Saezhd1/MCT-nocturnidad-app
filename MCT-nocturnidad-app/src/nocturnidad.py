from datetime import datetime, timedelta, time
from src.parser import parse_pdf

# --- Definición de franjas de nocturnidad ---
FRANJAS_NOCTURNIDAD = [
    (time(4,0), time(6,0)),     # tramo 1: 04:00–06:00
    (time(22,0), time(0,59))    # tramo 2: 22:00–00:59
]

# --- Funciones auxiliares ---
def parse_hora(hora_str, fecha):
    """Convierte 'HH:MM' en datetime con la fecha dada."""
    return datetime.combine(fecha, datetime.strptime(hora_str, "%H:%M").time())

def minutos_nocturnos(hi, hf):
    """Calcula minutos dentro de las franjas de nocturnidad especificadas."""
    total = 0
    for inicio_franja, fin_franja in FRANJAS_NOCTURNIDAD:
        noct_start = hi.replace(hour=inicio_franja.hour, minute=inicio_franja.minute)
        noct_end = hi.replace(hour=fin_franja.hour, minute=fin_franja.minute)
        # Si la franja cruza medianoche, sumamos un día
        if noct_end <= noct_start:
            noct_end += timedelta(days=1)

        inicio = max(hi, noct_start)
        fin = min(hf, noct_end)
        if inicio < fin:
            total += int((fin - inicio).total_seconds() / 60)
    return total

def calcular_nocturnidad(path_pdf, precio_minuto=0.5):
    """Procesa el PDF y calcula minutos e importe de nocturnidad."""
    registros = parse_pdf(path_pdf)
    resultados = []

    for r in registros:
        fecha = datetime.strptime(r["fecha"], "%d/%m/%Y").date()
        hi = parse_hora(r["HI"], fecha)
        hf = parse_hora(r["HF"], fecha)
        if hf < hi:
            hf += timedelta(days=1)

        noct = minutos_nocturnos(hi, hf)
        importe = noct * precio_minuto

        resultados.append({
            "fecha": r["fecha"],
            "HI": r["HI"],
            "HF": r["HF"],
            "minutos_nocturnos": noct,
            "importe": round(importe, 2)
        })
    return resultados

# --- Exportación HTML ---
def generar_html(resultados, output_path="resultados.html"):
    """Genera un informe HTML con los resultados de nocturnidad."""
    html = "<html><head><meta charset='utf-8'><title>Resultados Nocturnidad</title></head><body>"
    html += "<h1>Resultados de Nocturnidad</h1>"
    html += "<table border='1'><tr><th>Fecha</th><th>HI</th><th>HF</th><th>Minutos Nocturnos</th><th>Importe (€)</th></tr>"
    for r in resultados:
        html += f"<tr><td>{r['fecha']}</td><td>{r['HI']}</td><td>{r['HF']}</td><td>{r['minutos_nocturnos']}</td><td>{r['importe']}</td></tr>"
    html += "</table></body></html>"

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

# --- Ejemplo de uso ---
if __name__ == "__main__":
    datos = calcular_nocturnidad("octubre.pdf", precio_minuto=0.5)
    for d in datos:
        print(d)
    generar_html(datos, "resultados_octubre.html")


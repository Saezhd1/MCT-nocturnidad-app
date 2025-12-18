from flask import Flask, jsonify, request
from src.nocturnidad import calcular_nocturnidad_por_dia

app = Flask(__name__)

@app.route("/nocturnidad", methods=["POST"])
def nocturnidad_endpoint():
    """
    Endpoint que recibe un PDF y devuelve los cálculos de nocturnidad.
    Espera un JSON con {"pdf_path": "ruta/al/pdf", "precio_minuto": 0.5}
    """
    data = request.get_json()
    pdf_path = data.get("pdf_path")
    precio_minuto = data.get("precio_minuto", 0.5)

    resultados = calcular_nocturnidad_por_dia(pdf_path, precio_minuto)
    return jsonify(resultados)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv

from services import data_service as ds
from services import ai_service

load_dotenv()  # carrega variáveis de ambiente do arquivo .env
app = Flask(__name__)
CORS(app)  # em produção, restrinja à origem do Quasar


@app.get("/api/kpis")
def kpis():
    return jsonify(ds.get_kpis())


@app.get("/api/charts/orders-by-hour")
def orders_by_hour():
    return jsonify(ds.sales_by_hour())


@app.get("/api/charts/sales-by-month")
def sales_by_month():
    return jsonify(ds.sales_by_month())


@app.get("/api/charts/payments")
def payments():
    return jsonify(ds.payment_distribution())


@app.get("/api/charts/top-states")
def top_states():
    return jsonify(ds.top_states())


@app.get("/api/charts/top-categories")
def top_categories():
    return jsonify(ds.top_categories())


@app.get("/api/charts/delivery-vs-score")
def delivery_vs_score():
    return jsonify(ds.delivery_vs_score())


@app.post("/api/ai-insight")
def ai_insight():
    body = request.get_json(silent=True) or {}
    preset = body.get("preset")
    question = ai_service.PRESETS.get(preset) or (body.get("question") or "").strip()

    if not question:
        return jsonify({"error": "Envie 'preset' ou 'question'."}), 400
    if len(question) > 500:
        return jsonify({"error": "Pergunta muito longa (máx. 500 caracteres)."}), 400

    try:
        return jsonify({"insight": ai_service.ask(question, ds.SUMMARY)})
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 500
    except Exception:
        return jsonify({"error": "Falha ao consultar a IA. Tente novamente."}), 502


if __name__ == "__main__":
    app.run(debug=True, port=5000)
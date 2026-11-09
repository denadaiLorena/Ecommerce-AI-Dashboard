import os
import traceback

from dotenv import load_dotenv
from flask import Flask, Response, jsonify, request
from flask_cors import CORS

load_dotenv()

from services import data_service as ds  # noqa: E402
from services import ai_service  # noqa: E402

app = Flask(__name__)
CORS(app)  # Permite requisições CORS (em produção pode ser restringido via env CORS_ORIGINS)


@app.get("/")
@app.get("/health")
def health_check():
    return jsonify({
        "status": "healthy",
        "service": "FoodCommerce AI Backend",
        "version": "1.0.0"
    })


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


@app.get("/api/charts/anomalies")
def anomalies():
    return jsonify(ds.anomaly_data())


@app.get("/api/charts/forecast")
def forecast():
    metric = request.args.get("metric", "orders")
    return jsonify(ds.forecast_data(metric=metric))


@app.get("/api/charts/lead-time")
def lead_time():
    return jsonify(ds.lead_time_funnel())


@app.get("/api/charts/freight-by-region")
def freight_by_region():
    return jsonify(ds.freight_by_region())


@app.get("/api/charts/installments-ticket")
def installments_ticket():
    return jsonify(ds.installments_vs_ticket())


@app.get("/api/charts/reviews-distribution")
def reviews_distribution():
    return jsonify(ds.reviews_distribution())


@app.get("/api/charts/review-topics")
def review_topics():
    return jsonify(ds.review_topics())


@app.post("/api/simulate")
def simulate():
    body = request.get_json(silent=True) or {}
    delivery = float(body.get("delivery_reduction", 0.0))
    installments = float(body.get("installments_boost", 0.0))
    freight = float(body.get("freight_discount_ne", 0.0))
    return jsonify(ds.simulate_scenario(
        delivery_reduction=delivery,
        installments_boost=installments,
        freight_discount_ne=freight
    ))


@app.get("/api/export/csv")
def export_csv():
    csv_text = ds.generate_csv_report()
    csv_bytes = ("\ufeff" + csv_text).encode("utf-8")
    return Response(
        csv_bytes,
        mimetype="text/csv; charset=utf-8",
        headers={"Content-Disposition": "attachment; filename=relatorio_executivo_ecommerce.csv"}
    )


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
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": f"Falha ao consultar a IA: {type(e).__name__}"}), 502


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug_mode = os.environ.get("FLASK_DEBUG", "false").lower() in ("true", "1")
    app.run(host="0.0.0.0", port=port, debug=debug_mode)

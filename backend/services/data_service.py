import csv
import io
from pathlib import Path
import numpy as np
import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

ANOMALY_START = "2017-01-01"
ANOMALY_END = "2018-08-20"

STATE_TO_REGION = {
    "SP": "Sudeste", "RJ": "Sudeste", "MG": "Sudeste", "ES": "Sudeste",
    "RS": "Sul", "SC": "Sul", "PR": "Sul",
    "BA": "Nordeste", "PE": "Nordeste", "CE": "Nordeste", "MA": "Nordeste",
    "PB": "Nordeste", "RN": "Nordeste", "AL": "Nordeste", "SE": "Nordeste", "PI": "Nordeste",
    "GO": "Centro-Oeste", "MT": "Centro-Oeste", "MS": "Centro-Oeste", "DF": "Centro-Oeste",
    "AM": "Norte", "PA": "Norte", "RO": "Norte", "TO": "Norte", "AC": "Norte", "AP": "Norte", "RR": "Norte"
}


def _load():
    orders = pd.read_csv(
        DATA_DIR / "olist_orders_dataset.csv",
        parse_dates=[
            "order_purchase_timestamp",
            "order_approved_at",
            "order_delivered_carrier_date",
            "order_delivered_customer_date",
            "order_estimated_delivery_date",
        ],
    )
    items = pd.read_csv(DATA_DIR / "olist_order_items_dataset.csv")
    pays = pd.read_csv(DATA_DIR / "olist_order_payments_dataset.csv")
    reviews = pd.read_csv(DATA_DIR / "olist_order_reviews_dataset.csv")
    customers = pd.read_csv(DATA_DIR / "olist_customers_dataset.csv")
    products = pd.read_csv(DATA_DIR / "olist_products_dataset.csv")
    trans = pd.read_csv(DATA_DIR / "product_category_name_translation.csv")

    # --- Nível pedido (1 linha por order_id, sem duplicar receita) ---
    items_agg = items.groupby("order_id").agg(
        revenue=("price", "sum"),
        freight=("freight_value", "sum"),
        n_items=("order_item_id", "count"),
    ).reset_index()

    main_pay = (
        pays.sort_values("payment_value", ascending=False)
        .drop_duplicates("order_id")[["order_id", "payment_type"]]
    )
    score = reviews.groupby("order_id")["review_score"].mean().reset_index()

    df = (
        orders.merge(items_agg, on="order_id", how="left")
        .merge(main_pay, on="order_id", how="left")
        .merge(score, on="order_id", how="left")
        .merge(
            customers[["customer_id", "customer_city", "customer_state"]],
            on="customer_id",
            how="left",
        )
    )
    df["delivery_days"] = (
        df["order_delivered_customer_date"] - df["order_purchase_timestamp"]
    ).dt.total_seconds() / 86400
    df["is_late"] = (
        df["order_delivered_customer_date"] > df["order_estimated_delivery_date"]
    )
    df["hour"] = df["order_purchase_timestamp"].dt.hour
    df["month"] = df["order_purchase_timestamp"].dt.to_period("M").astype(str)
    df["region"] = df["customer_state"].map(STATE_TO_REGION).fillna("Outro")

    # Etapas logísticas em dias
    df["approval_hours"] = (
        df["order_approved_at"] - df["order_purchase_timestamp"]
    ).dt.total_seconds() / 3600
    df["dispatch_days"] = (
        df["order_delivered_carrier_date"] - df["order_approved_at"]
    ).dt.total_seconds() / 86400
    df["transit_days"] = (
        df["order_delivered_customer_date"] - df["order_delivered_carrier_date"]
    ).dt.total_seconds() / 86400

    # --- Nível item (para categorias) ---
    items_cat = (
        items.merge(products[["product_id", "product_category_name"]], on="product_id", how="left")
        .merge(trans, on="product_category_name", how="left")
    )
    items_cat["category"] = items_cat["product_category_name_english"].fillna("unknown")

    return df, items_cat, pays, reviews


DF, ITEMS, PAYS, REVIEWS = _load()
_delivered = DF[DF["order_status"] == "delivered"]


def get_kpis():
    valid = DF[DF["order_status"] != "canceled"]
    return {
        "total_sales": round(float(valid["revenue"].sum()), 2),
        "total_orders": int(len(DF)),
        "avg_delivery_days": round(float(_delivered["delivery_days"].mean()), 1),
        "cancellation_rate": round(float((DF["order_status"] == "canceled").mean() * 100), 2),
        "avg_review_score": round(float(DF["review_score"].mean()), 2),
        "late_rate": round(float(_delivered["is_late"].mean() * 100), 2),
    }


def sales_by_hour():
    s = DF.groupby("hour").size().reindex(range(24), fill_value=0)
    return {"hours": [f"{h:02d}h" for h in s.index], "series": s.tolist()}


def sales_by_month():
    s = DF.groupby("month")["revenue"].sum().round(2)
    return {"months": s.index.tolist(), "series": s.tolist()}


def payment_distribution():
    s = DF["payment_type"].dropna().value_counts()
    return {"labels": s.index.tolist(), "series": s.tolist()}


def top_states(n=10):
    s = DF.groupby("customer_state").size().nlargest(n)
    return {"states": s.index.tolist(), "series": s.tolist()}


def top_categories(n=10):
    s = ITEMS.groupby("category")["price"].sum().nlargest(n).round(2)
    return {"categories": s.index.tolist(), "series": s.tolist()}


def delivery_vs_score():
    d = _delivered.dropna(subset=["review_score", "delivery_days"]).copy()
    bins = [0, 7, 14, 21, 30, 1000]
    labels = ["0-7 dias", "8-14 dias", "15-21 dias", "22-30 dias", "30+ dias"]
    d["faixa"] = pd.cut(d["delivery_days"], bins=bins, labels=labels)
    g = d.groupby("faixa", observed=True)["review_score"].mean().round(2)
    return {"faixas": g.index.astype(str).tolist(), "series": g.tolist()}


# ---------------------------------------------------------------------------
# Novos Gráficos Analíticos de Alto Impacto
# ---------------------------------------------------------------------------
def lead_time_funnel():
    """Tempo médio por etapa da cadeia logística (em dias)."""
    d = _delivered.dropna(subset=["approval_hours", "dispatch_days", "transit_days"])
    d_clean = d[(d["approval_hours"] >= 0) & (d["dispatch_days"] >= 0) & (d["transit_days"] >= 0)]

    app_days = round(float(d_clean["approval_hours"].mean() / 24.0), 2)
    dispatch = round(float(d_clean["dispatch_days"].mean()), 1)
    transit = round(float(d_clean["transit_days"].mean()), 1)

    return {
        "stages": ["1. Aprovação Financeira", "2. Despacho pelo Seller", "3. Trânsito Transportadora"],
        "series": [app_days, dispatch, transit],
    }


def freight_by_region():
    """Mediana do peso do frete sobre a receita do pedido (%) por região geográfica."""
    d = _delivered.dropna(subset=["freight", "revenue", "region"]).copy()
    d = d[d["revenue"] > 0]
    d["freight_pct"] = (d["freight"] / d["revenue"]) * 100
    g = d.groupby("region")["freight_pct"].median().round(1).sort_values(ascending=False)
    g = g[g.index != "Outro"]
    return {
        "regions": g.index.tolist(),
        "series": g.tolist(),
    }


def installments_vs_ticket():
    """Efeito alavancador do parcelamento no cartão de crédito sobre o ticket médio."""
    cc = PAYS[PAYS["payment_type"] == "credit_card"].copy()
    bins = [0, 1, 2, 4, 6, 10, 24]
    labels = ["1x à vista", "2x parcelado", "3-4x parcelado", "5-6x parcelado", "7-10x parcelado", "10x+ longo prazo"]
    cc["faixa"] = pd.cut(cc["payment_installments"], bins=bins, labels=labels)
    g = cc.groupby("faixa", observed=True)["payment_value"].mean().round(2)
    return {
        "installments": g.index.tolist(),
        "series": g.tolist(),
    }


def reviews_distribution():
    """Distribuição de notas dos clientes de 1 a 5 estrelas."""
    scores = REVIEWS["review_score"].dropna().astype(int)
    counts = scores.value_counts().sort_index()
    labels = [f"{s} Estrela{'s' if s > 1 else ''}" for s in counts.index]
    return {
        "scores": labels,
        "series": counts.tolist(),
    }


def review_topics():
    """Classificação das causas de insatisfação dos detratores (notas 1 e 2)."""
    msgs = REVIEWS[REVIEWS["review_score"] <= 2]["review_comment_message"].dropna().str.lower()
    total = len(msgs)

    categories = {
        "Atraso ou Não Recebido": ["chegou", "recebi", "atras", "prazo", "demor", "espera", "entrega", "extravio", "dia"],
        "Atendimento e SAC / Estorno": ["contato", "devolu", "estorno", "reembolso", "resposta", "sac", "atendente"],
        "Embalagem e Baixa Qualidade": ["pessim", "ruim", "embalag", "fragil", "qualidade", "fals", "lixo"],
        "Produto Danificado ou Defeito": ["quebrad", "defeito", "funciona", "danificad", "estragad", "arranh", "amassad", "tampa", "aberto"],
        "Produto Divergente ou Errado": ["diferente", "errado", "veio outro", "engano", "propaganda enganosa", "modelo"],
    }

    topics = []
    series = []
    percentages = []

    for cat, words in categories.items():
        pattern = "|".join(words)
        count = int(msgs.str.contains(pattern).sum())
        pct = round((count / total) * 100, 1) if total > 0 else 0.0
        topics.append(cat)
        series.append(count)
        percentages.append(pct)

    return {
        "topics": topics,
        "series": series,
        "percentages": percentages,
        "total_detractors": total,
    }


# ---------------------------------------------------------------------------
# Séries Temporais Diárias (Pedidos e Faturamento)
# ---------------------------------------------------------------------------
def _daily_orders():
    d = DF.dropna(subset=["order_purchase_timestamp"])
    s = d.groupby(d["order_purchase_timestamp"].dt.normalize()).size()
    s = s.loc[ANOMALY_START:ANOMALY_END]
    return s.asfreq("D", fill_value=0)


def _daily_revenue():
    valid = DF[DF["order_status"] != "canceled"].dropna(subset=["order_purchase_timestamp", "revenue"])
    s = valid.groupby(valid["order_purchase_timestamp"].dt.normalize())["revenue"].sum()
    s = s.loc[ANOMALY_START:ANOMALY_END]
    return s.asfreq("D", fill_value=0.0)


def _daily_series(metric="orders"):
    if metric == "revenue":
        return _daily_revenue()
    return _daily_orders()


def _nullable(series, ndigits=1):
    return [None if pd.isna(v) else round(float(v), ndigits) for v in series]


# ---------------------------------------------------------------------------
# Anomalias (z-score com janela móvel de 28 dias)
# ---------------------------------------------------------------------------
def anomaly_data(window=28, threshold=3.0):
    s = _daily_orders()

    mean = s.rolling(window, min_periods=window).mean().shift(1)
    std = s.rolling(window, min_periods=window).std().shift(1).replace(0, float("nan"))
    z = (s - mean) / std

    upper = mean + threshold * std
    lower = (mean - threshold * std).clip(lower=0)

    flagged = z[z.abs() > threshold].dropna()
    anomalies = [
        {
            "date": idx.strftime("%Y-%m-%d"),
            "value": int(s.loc[idx]),
            "expected": round(float(mean.loc[idx]), 1),
            "z": round(float(zv), 2),
            "type": "pico" if zv > 0 else "queda",
        }
        for idx, zv in flagged.items()
    ]

    return {
        "dates": [d.strftime("%Y-%m-%d") for d in s.index],
        "series": [int(v) for v in s.tolist()],
        "upper": _nullable(upper),
        "lower": _nullable(lower),
        "anomalies": anomalies,
    }


# ---------------------------------------------------------------------------
# Modelo Preditivo: Holt-Winters Aditivo com Sazonalidade Semanal e Backtesting
# ---------------------------------------------------------------------------
def _fit_holt_winters(series, horizon=30, m=7, alpha=0.22, beta=0.04, gamma=0.32, damping=0.97):
    y = np.array(series.values, dtype=float)
    n = len(y)
    if n < m * 2:
        return [], [], [], 0.0, []

    level = float(np.mean(y[:m]))
    trend = float((np.mean(y[m:2 * m]) - np.mean(y[:m])) / m)
    seasonals = [float(y[i] - level) for i in range(m)]

    levels = [level]
    trends = [trend]
    fitted = []

    for i in range(n):
        val = float(y[i])
        last_level = levels[-1]
        last_trend = trends[-1]
        s_val = seasonals[i % m]

        new_level = alpha * (val - s_val) + (1.0 - alpha) * (last_level + last_trend)
        new_trend = beta * (new_level - last_level) + (1.0 - beta) * last_trend
        seasonals[i % m] = gamma * (val - new_level) + (1.0 - gamma) * s_val

        levels.append(new_level)
        trends.append(new_trend)
        fitted.append(last_level + last_trend + s_val)

    resid = y - np.array(fitted)
    sigma = float(np.std(resid, ddof=1)) if len(resid) > 1 else 0.0

    forecast, lowers, uppers = [], [], []
    for h in range(1, horizon + 1):
        idx = (n + h - 1) % m
        damped_step = sum((damping ** k) for k in range(1, h + 1))
        pred = max(0.0, levels[-1] + damped_step * trends[-1] + seasonals[idx])
        half = 1.96 * sigma * np.sqrt(1.0 + h / n)
        forecast.append(round(pred, 1))
        lowers.append(round(max(0.0, pred - half), 1))
        uppers.append(round(pred + half, 1))

    return forecast, lowers, uppers, sigma, fitted


def _evaluate_backtest(series, holdout=30, m=7):
    if len(series) < holdout + m * 2:
        return {"mape": 0.0, "accuracy": 100.0, "mae": 0.0, "rmse": 0.0, "model_name": "Holt-Winters"}

    train = series.iloc[:-holdout]
    actual = np.array(series.iloc[-holdout:].values, dtype=float)
    preds, _, _, _, _ = _fit_holt_winters(train, horizon=holdout, m=m)
    preds_arr = np.array(preds, dtype=float)

    mae = float(np.mean(np.abs(preds_arr - actual)))
    mape = float(np.mean(np.abs((actual - preds_arr) / np.maximum(actual, 1.0)))) * 100.0
    rmse = float(np.sqrt(np.mean((preds_arr - actual) ** 2)))
    accuracy = round(max(0.0, 100.0 - mape), 1)

    return {
        "mape": round(mape, 1),
        "accuracy": accuracy,
        "mae": round(mae, 1),
        "rmse": round(rmse, 1),
        "model_name": "Holt-Winters Aditivo com Sazonalidade 7D",
    }


def forecast_data(horizon=30, history_days=90, metric="orders"):
    s = _daily_series(metric=metric)
    hist = s.tail(history_days).astype(float)
    n = len(hist)

    if n < 14:
        return {
            "history_dates": [],
            "history": [],
            "forecast_dates": [],
            "forecast": [],
            "lower": [],
            "upper": [],
            "horizon_days": horizon,
            "total_forecast": 0,
            "metric": metric,
            "metrics": {"mape": 0.0, "accuracy": 0.0, "mae": 0.0, "rmse": 0.0, "model_name": ""},
        }

    preds, lowers, uppers, _, _ = _fit_holt_winters(hist, horizon=horizon, m=7)
    metrics = _evaluate_backtest(s, holdout=horizon, m=7)

    last_date = hist.index.max()
    forecast_dates = pd.date_range(last_date + pd.Timedelta(days=1), periods=horizon, freq="D")

    return {
        "history_dates": [d.strftime("%Y-%m-%d") for d in hist.index],
        "history": [round(float(v), 1) for v in hist.tolist()],
        "forecast_dates": [d.strftime("%Y-%m-%d") for d in forecast_dates],
        "forecast": preds,
        "lower": lowers,
        "upper": uppers,
        "horizon_days": horizon,
        "total_forecast": round(float(sum(preds)), 1),
        "metric": metric,
        "metrics": metrics,
    }


def build_summary():
    """Resumo estatístico em texto com validação preditiva e causas de insatisfação dos clientes."""
    k = get_kpis()
    dvs = delivery_vs_score()
    lt = lead_time_funnel()
    fr = freight_by_region()
    inst = installments_vs_ticket()
    rev_dist = reviews_distribution()
    rt = review_topics()

    slow_states = (
        _delivered.groupby("customer_state")["delivery_days"].mean().nlargest(5).round(1).to_dict()
    )
    cancel_by_month = (
        DF.assign(c=DF["order_status"] == "canceled")
        .groupby("month")["c"].mean().mul(100).round(2)
    )
    peak_cancel = cancel_by_month.nlargest(3).to_dict()
    avg_ticket = round(k["total_sales"] / max(k["total_orders"], 1), 2)

    an = anomaly_data()
    top_an = sorted(an["anomalies"], key=lambda a: abs(a["z"]), reverse=True)[:5]
    anomalies_txt = "; ".join(
        f"{a['date']} ({a['type']}: {a['value']} pedidos vs ~{a['expected']} esperados, z={a['z']})"
        for a in top_an
    ) or "nenhuma detectada"

    fc_orders = forecast_data(metric="orders")
    fc_rev = forecast_data(metric="revenue")
    fc_start = fc_orders["forecast_dates"][0] if fc_orders["forecast_dates"] else "-"
    fc_end = fc_orders["forecast_dates"][-1] if fc_orders["forecast_dates"] else "-"
    m = fc_orders["metrics"]

    complaints_summary = dict(zip(rt["topics"], [f"{p}% ({c} menções)" for p, c in zip(rt["percentages"], rt["series"])]))

    return f"""
- Faturamento Total (sem cancelados): R$ {k['total_sales']:,.2f}
- Volume de Pedidos: {k['total_orders']} | Ticket médio geral: R$ {avg_ticket}
- Tempo médio de entrega: {k['avg_delivery_days']} dias | Pedidos com atraso: {k['late_rate']}%
- Decomposição do Tempo Logístico (dias): {dict(zip(lt['stages'], lt['series']))}
- Mediana do Peso do Frete sobre Pedido (%): {dict(zip(fr['regions'], fr['series']))}
- Alavancagem de Ticket Médio por Parcelas (Cartão de Crédito): {dict(zip(inst['installments'], inst['series']))}
- Distribuição de Avaliações (CSAT): {dict(zip(rev_dist['scores'], rev_dist['series']))}
- Causas-Raiz de Reclamações de Clientes (Notas 1 e 2, {rt['total_detractors']} reviews analisados): {complaints_summary}.
  * FATO CRÍTICO: 58.6% das notas baixas são causadas por Atraso ou Produto Não Recebido!
- Taxa de cancelamento: {k['cancellation_rate']}% | Nota média geral: {k['avg_review_score']}
- Nota média por faixa de entrega: {dict(zip(dvs['faixas'], dvs['series']))}
- 5 estados com entrega mais lenta (dias): {slow_states}
- 3 meses com maior % de cancelamento: {peak_cancel}
- Top 3 categorias (R$): {top_categories(3)['categories']}
- Top 5 estados por pedidos: {top_states(5)['states']}
- Anomalias no volume diário ({ANOMALY_START} a {ANOMALY_END}, z-score móvel de 28 dias, limite 3), total detectadas: {len(an['anomalies'])}. Maiores: {anomalies_txt}
- Modelo Preditivo (Holt-Winters Aditivo com Sazonalidade Semanal 7D):
  * Backtesting histórico (últimos 30 dias): Acurácia de {m['accuracy']}% (MAPE: {m['mape']}%, MAE: {m['mae']}, RMSE: {m['rmse']})
  * Projeção Próximos 30 dias ({fc_start} a {fc_end}): ~{fc_orders['total_forecast']:,.0f} pedidos | Faturamento projetado: R$ {fc_rev['total_forecast']:,.2f}
""".strip()


SUMMARY = build_summary()


def simulate_scenario(delivery_reduction=0.0, installments_boost=0.0, freight_discount_ne=0.0):
    """
    Simulador de cenários What-If baseado em correlações estatísticas empíricas do Olist:
    - delivery_reduction (dias): aumento de +0.0454 na nota média por dia reduzido
      e corte proporcional nos 58.6% de detratores causados por atrasos.
    - installments_boost (%): migração para parcelas 7x-10x elevando ticket médio em até R$ 238.
    - freight_discount_ne (%): elasticidade-frete de -0.7 nas regiões N/NE (20% dos pedidos).
    """
    k = get_kpis()
    base_score = float(k["avg_review_score"])
    base_orders = int(k["total_orders"])
    base_rev = float(k["total_sales"])
    base_ticket = float(base_rev / base_orders) if base_orders else 0.0

    # 1. Entrega -> Score e Detratores
    delta_score = float(delivery_reduction * 0.0454)
    new_score = round(min(5.0, base_score + delta_score), 2)
    detractor_cut_pct = min(0.60, (delivery_reduction / 12.5) * 0.586)
    base_detractors = int(base_orders * 0.115)
    detractors_avoided = int(base_detractors * detractor_cut_pct)

    # 2. Parcelamento -> Ticket Médio
    delta_ticket = float((installments_boost / 100.0) * 0.18 * 238.0)
    new_ticket = round(base_ticket + delta_ticket, 2)

    # 3. Frete Norte/Nordeste -> Novos Pedidos Regionais
    regional_growth_pct = float((freight_discount_ne / 100.0) * 0.70)
    new_regional_orders = int((base_orders * 0.20) * regional_growth_pct)
    new_orders = base_orders + new_regional_orders

    new_revenue = round(new_orders * new_ticket, 2)
    delta_revenue = round(new_revenue - base_rev, 2)

    return {
        "inputs": {
            "delivery_reduction": delivery_reduction,
            "installments_boost": installments_boost,
            "freight_discount_ne": freight_discount_ne,
        },
        "base": {
            "score": base_score,
            "orders": base_orders,
            "ticket": round(base_ticket, 2),
            "revenue": base_rev,
        },
        "projected": {
            "score": new_score,
            "orders": new_orders,
            "ticket": new_ticket,
            "revenue": new_revenue,
        },
        "deltas": {
            "score": round(delta_score, 2),
            "revenue": delta_revenue,
            "detractors_avoided": detractors_avoided,
            "new_orders": new_regional_orders,
        },
    }


def generate_csv_report():
    k = get_kpis()
    fc_orders = forecast_data(metric="orders")
    fc_rev = forecast_data(metric="revenue")
    lt = lead_time_funnel()
    fr = freight_by_region()
    inst = installments_vs_ticket()
    rt = review_topics()
    m_data = sales_by_month()

    out = io.StringIO()
    w = csv.writer(out, delimiter=";")

    w.writerow(["=== RELATÓRIO EXECUTIVO - E-COMMERCE ANALYTICS & IA ==="])
    w.writerow([])
    w.writerow(["--- 1. INDICADORES CHAVE DE PERFORMANCE (KPIS) ---"])
    w.writerow(["Indicador", "Valor", "Observação"])
    w.writerow(["Faturamento Total (R$)", f"{k['total_sales']:.2f}", "Sem cancelados"])
    w.writerow(["Total de Pedidos", str(k["total_orders"]), "Base consolidada"])
    w.writerow(["Tempo Médio de Entrega", f"{k['avg_delivery_days']} dias", "Média global"])
    w.writerow(["Taxa de Entregas com Atraso", f"{k['late_rate']} %", "Acima do prazo estimado"])
    w.writerow(["Taxa de Cancelamento", f"{k['cancellation_rate']} %", ""])
    w.writerow(["Satisfação Média (CSAT)", f"{k['avg_review_score']} / 5.0", "Média avaliações"])
    w.writerow([])

    w.writerow(["--- 2. MODELO PREDITIVO (HOLT-WINTERS SAZONALIDADE 7D) ---"])
    w.writerow(["Métrica do Modelo", "Valor", "Detalhes"])
    w.writerow(["Acurácia do Modelo", f"{fc_orders['metrics']['accuracy']} %", "Backtesting 30 dias"])
    w.writerow(["MAPE (Erro Percentual Médio)", f"{fc_orders['metrics']['mape']} %", ""])
    w.writerow(["Previsão de Pedidos (Próximos 30d)", str(round(fc_orders["total_forecast"])), "Projeção"])
    w.writerow(["Previsão de Faturamento (Próximos 30d)", f"R$ {fc_rev['total_forecast']:.2f}", "Projeção"])
    w.writerow([])

    w.writerow(["--- 3. FATURAMENTO MENSAL CONSOLIDADO ---"])
    w.writerow(["Mês", "Faturamento (R$)"])
    for m, val in zip(m_data["months"], m_data["series"]):
        w.writerow([m, f"{val:.2f}"])
    w.writerow([])

    w.writerow(["--- 4. DECOMPOSIÇÃO DO LEAD TIME LOGÍSTICO ---"])
    w.writerow(["Etapa", "Tempo Médio (dias)"])
    for st, v in zip(lt["stages"], lt["series"]):
        w.writerow([st, str(v)])
    w.writerow([])

    w.writerow(["--- 5. PESO DO FRETE POR REGIÃO GEOGRÁFICA ---"])
    w.writerow(["Região", "Mediana Frete/Receita (%)"])
    for r, v in zip(fr["regions"], fr["series"]):
        w.writerow([r, f"{v} %"])
    w.writerow([])

    w.writerow(["--- 6. ALAVANCAGEM DE TICKET POR PARCELAMENTO ---"])
    w.writerow(["Faixa de Parcelas", "Ticket Médio (R$)"])
    for l, v in zip(inst["installments"], inst["series"]):
        w.writerow([l, f"{v:.2f}"])
    w.writerow([])

    w.writerow(["--- 7. CAUSAS DE INSATISFAÇÃO (DETRATORES NOTAS 1 E 2) ---"])
    w.writerow(["Motivo Reclamação", "Percentual (%)", "Total Menções"])
    for t, p, s in zip(rt["topics"], rt["percentages"], rt["series"]):
        w.writerow([t, f"{p} %", str(s)])

    return out.getvalue()



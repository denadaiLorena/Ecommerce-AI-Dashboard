from pathlib import Path
import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

ANOMALY_START = "2017-01-01"
ANOMALY_END = "2018-08-31"


def _load():
    orders = pd.read_csv(
        DATA_DIR / "olist_orders_dataset.csv",
        parse_dates=[
            "order_purchase_timestamp",
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

    # --- Nível item (para categorias) ---
    items_cat = (
        items.merge(products[["product_id", "product_category_name"]], on="product_id", how="left")
        .merge(trans, on="product_category_name", how="left")
    )
    items_cat["category"] = items_cat["product_category_name_english"].fillna("unknown")

    return df, items_cat


DF, ITEMS = _load()
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
# Anomalias (z-score com janela móvel)
# ---------------------------------------------------------------------------
def _daily_orders():
    d = DF.dropna(subset=["order_purchase_timestamp"])
    s = d.groupby(d["order_purchase_timestamp"].dt.normalize()).size()
    s = s.loc[ANOMALY_START:ANOMALY_END]
    return s.asfreq("D", fill_value=0)


def _nullable(series, ndigits=1):
    return [None if pd.isna(v) else round(float(v), ndigits) for v in series]


def anomaly_data(window=28, threshold=3.0):
    s = _daily_orders()

    # shift(1): cada dia é comparado com a janela dos dias ANTERIORES,
    # para o próprio pico não inflar a média/desvio que o avalia.
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
# Previsão simples: tendência linear + sazonalidade semanal (próximos 30 dias)
# ---------------------------------------------------------------------------
def forecast_data(horizon=30, history_days=90):
    s = _daily_orders()
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
        }

    t = pd.Series(range(n), index=hist.index, dtype=float)
    t_mean = float(t.mean())
    y_mean = float(hist.mean())
    denom = float(((t - t_mean) ** 2).sum())
    slope = float(((t - t_mean) * (hist - y_mean)).sum() / denom) if denom else 0.0
    intercept = y_mean - slope * t_mean

    trend_fit = intercept + slope * t
    resid = hist - trend_fit
    seasonal = resid.groupby(resid.index.dayofweek).mean()
    resid_adj = resid - resid.index.map(lambda d: float(seasonal.get(d.dayofweek, 0)))
    sigma = float(resid_adj.std(ddof=1) or 0.0)

    last_date = hist.index.max()
    forecast_dates = pd.date_range(last_date + pd.Timedelta(days=1), periods=horizon, freq="D")

    preds, lowers, uppers = [], [], []
    for i, d in enumerate(forecast_dates, start=1):
        base = intercept + slope * (n - 1 + i)
        pred = max(0.0, base + float(seasonal.get(d.dayofweek, 0)))
        half = 1.96 * sigma * (1 + i / n) ** 0.5
        preds.append(round(pred, 1))
        lowers.append(round(max(0.0, pred - half), 1))
        uppers.append(round(pred + half, 1))

    return {
        "history_dates": [d.strftime("%Y-%m-%d") for d in hist.index],
        "history": [int(v) for v in hist.tolist()],
        "forecast_dates": [d.strftime("%Y-%m-%d") for d in forecast_dates],
        "forecast": preds,
        "lower": lowers,
        "upper": uppers,
        "horizon_days": horizon,
        "total_forecast": round(sum(preds), 1),
    }


def build_summary():
    """Resumo estatístico em texto, enviado como contexto à LLM."""
    k = get_kpis()
    dvs = delivery_vs_score()
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

    fc = forecast_data()
    fc_start = fc["forecast_dates"][0] if fc["forecast_dates"] else "-"
    fc_end = fc["forecast_dates"][-1] if fc["forecast_dates"] else "-"

    return f"""
- Faturamento (sem cancelados): R$ {k['total_sales']:,.2f}
- Pedidos: {k['total_orders']} | Ticket médio: R$ {avg_ticket}
- Tempo médio de entrega: {k['avg_delivery_days']} dias | Pedidos atrasados: {k['late_rate']}%
- Taxa de cancelamento: {k['cancellation_rate']}% | Nota média: {k['avg_review_score']}
- Nota média por faixa de entrega: {dict(zip(dvs['faixas'], dvs['series']))}
- 5 estados com entrega mais lenta (dias): {slow_states}
- 3 meses com maior % de cancelamento: {peak_cancel}
- Top 3 categorias (R$): {top_categories(3)['categories']}
- Top 5 estados por pedidos: {top_states(5)['states']}
- Anomalias no volume diário de pedidos ({ANOMALY_START} a {ANOMALY_END}, z-score móvel de 28 dias, limite 3), {len(an['anomalies'])} no total. Maiores: {anomalies_txt}
- Previsão simples de pedidos ({fc_start} a {fc_end}): ~{fc['total_forecast']} pedidos no horizonte de {fc['horizon_days']} dias (tendência linear + sazonalidade semanal, intervalo ~95%)
""".strip()


SUMMARY = build_summary()
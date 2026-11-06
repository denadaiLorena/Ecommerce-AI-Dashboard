from pathlib import Path
import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


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
""".strip()


SUMMARY = build_summary()
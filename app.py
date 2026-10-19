from pathlib import Path
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ---------- App setup ----------
st.set_page_config(
    page_title="RetailPulse | AI Retail Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"

BG = "#090E19"
SIDEBAR = "#0E1423"
CARD = "#131B2D"
CARD_ALT = "#17243A"
BORDER = "#293650"
TEXT = "#EDF3FF"
MUTED = "#8D9BB5"
TEAL = "#33D6C0"
BLUE = "#4D9DFF"
PURPLE = "#9480FF"
AMBER = "#FFB454"
RED = "#FF6675"
GREEN = "#45D99A"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
:root {{ color-scheme: dark; }}
html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; }}
.stApp {{ background: {BG}; color: {TEXT}; }}
[data-testid="stSidebar"] {{ background: {SIDEBAR}; border-right: 1px solid {BORDER}; }}
[data-testid="stSidebar"] * {{ color: {TEXT}; }}
.block-container {{ padding-top: 1.4rem; padding-bottom: 2rem; max-width: 1600px; }}
h1, h2, h3 {{ color: {TEXT} !important; letter-spacing: -0.025em; }}
p, label, .stCaption {{ color: {MUTED}; }}
div[data-testid="stMetric"] {{
  background: {CARD}; border: 1px solid {BORDER}; padding: 18px 18px 14px;
  border-radius: 16px; min-height: 125px;
}}
div[data-testid="stMetricLabel"] {{ color: {MUTED}; font-size: 0.85rem; }}
div[data-testid="stMetricValue"] {{ color: {TEXT}; font-weight: 700; }}
div[data-testid="stMetricDelta"] {{ font-size: 0.78rem; }}
div[data-testid="stPlotlyChart"] {{
  background: {CARD}; border: 1px solid {BORDER}; border-radius: 16px;
  padding: 10px 10px 0;
}}
div[data-testid="stDataFrame"] {{
  border: 1px solid {BORDER}; border-radius: 12px; overflow: hidden;
}}
div.stButton > button {{
  background: {CARD_ALT}; color: {TEXT}; border: 1px solid {BORDER};
  border-radius: 10px; font-weight: 600;
}}
div.stButton > button:hover {{ border-color: {TEAL}; color: {TEAL}; }}
hr {{ border-color: {BORDER}; }}
[data-testid="stSelectbox"], [data-testid="stDateInput"] {{ color: {TEXT}; }}
.rp-brand {{ display:flex; gap:10px; align-items:center; padding:8px 0 18px; }}
.rp-logo {{ width:36px;height:36px;border-radius:11px;background:{TEAL};color:{BG};
display:flex;align-items:center;justify-content:center;font-weight:800;font-size:20px; }}
.rp-brand-title {{ color:{TEXT};font-size:20px;font-weight:700;line-height:1.1; }}
.rp-brand-sub {{ color:{MUTED};font-size:9px;letter-spacing:.12em;margin-top:4px; }}
.rp-eyebrow {{ color:{TEAL};font-size:11px;font-weight:700;letter-spacing:.12em;text-transform:uppercase; }}
.rp-card {{ background:{CARD}; border:1px solid {BORDER}; border-radius:16px; padding:18px 20px; }}
.rp-note {{ color:{MUTED};font-size:12px; }}
.rp-pill {{ display:inline-block;background:#12352F;color:{TEAL};border-radius:7px;padding:5px 9px;font-size:10px;font-weight:700; }}
</style>
""", unsafe_allow_html=True)


# ---------- Load data ----------
@st.cache_data
def load_data():
    sales = pd.read_csv(DATA_DIR / "retail_sales.csv", parse_dates=["date"])
    customers = pd.read_csv(DATA_DIR / "customers.csv")
    inventory = pd.read_csv(DATA_DIR / "inventory.csv")
    return sales, customers, inventory

sales_all, customers, inventory_all = load_data()


# ---------- Sidebar navigation and filters ----------
with st.sidebar:
    st.markdown("""
    <div class="rp-brand">
      <div class="rp-logo">R</div>
      <div><div class="rp-brand-title">RetailPulse</div>
      <div class="rp-brand-sub">AI RETAIL INTELLIGENCE</div></div>
    </div>
    """, unsafe_allow_html=True)
    st.divider()
    page = st.radio(
        "WORKSPACE",
        ["Executive Overview", "Demand Forecasting", "Customer Analytics",
         "Inventory Intelligence", "Model Monitoring"],
        label_visibility="visible",
    )
    st.divider()
    st.caption("GLOBAL FILTERS")
    min_date = sales_all["date"].min().date()
    max_date = sales_all["date"].max().date()
    date_range = st.date_input("Sales date range", value=(max(min_date, max_date - pd.Timedelta(days=29)), max_date),
                               min_value=min_date, max_value=max_date)
    categories = ["All categories"] + sorted(sales_all["category"].unique().tolist())
    category = st.selectbox("Product category", categories)
    st.divider()
    st.markdown('<span class="rp-pill">✦ RETAILPULSE DEMO</span>', unsafe_allow_html=True)
    st.caption("Sample analytics dataset • Not live business data")


# Safely handle a single selected date as well as a date range
if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
    start_date, end_date = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
else:
    start_date = end_date = pd.Timestamp(date_range)
sales = sales_all[(sales_all["date"] >= start_date) & (sales_all["date"] <= end_date)].copy()
if category != "All categories":
    sales = sales[sales["category"] == category]
inventory = inventory_all.copy()
if category != "All categories":
    inventory = inventory[inventory["category"] == category]

# ---------- Reusable helpers ----------
def money(value, decimals=0):
    return f"${value:,.{decimals}f}"

def style_chart(fig, height=330, show_legend=True):
    fig.update_layout(
        height=height, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color=MUTED, size=11),
        margin=dict(l=12, r=12, t=54, b=14),
        title=dict(font=dict(size=15, color=TEXT), x=0.02, y=0.98),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                    bgcolor="rgba(0,0,0,0)"),
        xaxis=dict(showgrid=False, zeroline=False, linecolor=BORDER),
        yaxis=dict(showgrid=True, gridcolor="#202B40", zeroline=False, linecolor=BORDER),
        hoverlabel=dict(bgcolor=CARD, font_color=TEXT),
        showlegend=show_legend,
    )
    return fig

def section_heading(title, subtitle=None):
    st.subheader(title)
    if subtitle:
        st.caption(subtitle)

def render_kpis(items):
    cols = st.columns(len(items))
    for col, (label, value, delta) in zip(cols, items):
        with col:
            st.metric(label, value, delta)

def insight_card(eyebrow, headline, body, action):
    st.markdown(f"""
    <div class="rp-card" style="height:100%">
      <div class="rp-eyebrow">✦ {eyebrow}</div>
      <h3 style="margin:16px 0 10px;font-size:19px">{headline}</h3>
      <p style="font-size:13px;line-height:1.65;margin-bottom:20px">{body}</p>
      <div style="background:{CARD_ALT};border-radius:10px;padding:13px 14px">
        <div style="font-size:10px;color:{TEAL};font-weight:700;letter-spacing:.08em">RECOMMENDED ACTION</div>
        <div style="font-size:12px;color:{TEXT};margin-top:7px">{action}</div>
      </div>
      <div class="rp-note" style="margin-top:16px">Based on the selected demo data</div>
    </div>
    """, unsafe_allow_html=True)

def chart_colors():
    return [TEAL, BLUE, PURPLE, AMBER, RED, GREEN]

# ---------- Page 1: Executive Overview ----------
if page == "Executive Overview":
    st.markdown('<div class="rp-eyebrow">WORKSPACE / ANALYTICS</div>', unsafe_allow_html=True)
    st.title("Executive Overview")
    st.caption("Your retail performance at a glance")
    revenue = sales["revenue"].sum()
    orders_proxy = int(sales["units_sold"].sum() * 0.72)  # demo proxy; transaction IDs are not in this dataset
    units = int(sales["units_sold"].sum())
    aov_proxy = revenue / max(orders_proxy, 1)
    prev_start = start_date - (end_date - start_date + pd.Timedelta(days=1))
    prev_end = start_date - pd.Timedelta(days=1)
    previous = sales_all[(sales_all["date"] >= prev_start) & (sales_all["date"] <= prev_end)]
    if category != "All categories":
        previous = previous[previous["category"] == category]
    prev_revenue = previous["revenue"].sum()
    revenue_delta = (revenue - prev_revenue) / prev_revenue * 100 if prev_revenue else 0
    low_stock = int((inventory["status"] == "Low Stock").sum())
    render_kpis([
        ("Total Revenue", money(revenue), f"{revenue_delta:+.1f}% vs previous period"),
        ("Units Sold", f"{units:,}", "Across selected period"),
        ("Avg. Order Value*", money(aov_proxy, 2), "Estimated from sample data"),
        ("Low-stock SKUs", f"{low_stock}", "Current inventory snapshot"),
    ])
    st.caption("*Average order value is estimated because the sample sales file is aggregated by SKU and day, not by individual transaction.")
    left, right = st.columns([1.65, 1])
    with left:
        daily = sales.groupby("date", as_index=False).agg(revenue=("revenue", "sum"))
        fig = px.area(daily, x="date", y="revenue", title="Revenue Trend",
                      color_discrete_sequence=[TEAL])
        fig.update_traces(line=dict(width=2.5), fillcolor="rgba(51,214,192,0.12)")
        fig.update_yaxes(title="Revenue ($)", tickprefix="$")
        st.plotly_chart(style_chart(fig, 340, False), use_container_width=True)
    with right:
        category_perf = sales.groupby("category", as_index=False).agg(revenue=("revenue", "sum")).sort_values("revenue", ascending=False)
        fig = px.bar(category_perf, x="revenue", y="category", orientation="h",
                     title="Revenue by Category", color="category",
                     color_discrete_sequence=chart_colors())
        fig.update_yaxes(title="")
        fig.update_xaxes(title="Revenue ($)", tickprefix="$")
        fig.update_layout(showlegend=False)
        st.plotly_chart(style_chart(fig, 340, False), use_container_width=True)
    lower_left, lower_right = st.columns([1.65, 1])
    with lower_left:
        section_heading("Top-performing products", "Ranked by revenue in the selected period")
        top = sales.groupby(["sku", "product_name", "category"], as_index=False).agg(
            units_sold=("units_sold", "sum"), revenue=("revenue", "sum"))
        top = top.sort_values("revenue", ascending=False).head(8)
        top["revenue"] = top["revenue"].map(lambda x: money(x, 2))
        st.dataframe(top, use_container_width=True, hide_index=True)
    with lower_right:
        best_cat = category_perf.iloc[0]["category"] if not category_perf.empty else "No data"
        best_rev = category_perf.iloc[0]["revenue"] if not category_perf.empty else 0
        insight_card("AI INSIGHTS", f"{best_cat} leads revenue",
                     f"This category generated {money(best_rev)} in the selected period. Review its top SKUs and recent demand before changing replenishment plans.",
                     "Review category mix and stock coverage for the top-selling products.")


# ---------- Page 2: Demand Forecasting ----------
elif page == "Demand Forecasting":
    st.markdown('<div class="rp-eyebrow">PREDICTIVE ANALYTICS / DEMAND</div>', unsafe_allow_html=True)
    st.title("Demand Forecasting")
    st.caption("Explore historical sales and a simple baseline forecast")
    products = sorted(sales_all["product_name"].unique())
    selected_product = st.selectbox("Product to forecast", products)
    horizon = st.slider("Forecast horizon (days)", 7, 60, 30, 7)
    product_history = sales_all[sales_all["product_name"] == selected_product].groupby("date", as_index=False).agg(
        units_sold=("units_sold", "sum"))
    history = product_history[product_history["date"] <= end_date].tail(90).copy()
    if history.empty:
        st.warning("There is not enough history for this product and date range.")
    else:
        # Transparent starter baseline: trailing 7-day average, not a trained Prophet/LSTM model
        history["rolling_mean"] = history["units_sold"].rolling(7, min_periods=1).mean()
        last_day = history["date"].max()
        recent_mean = float(history.tail(7)["units_sold"].mean())
        future_dates = pd.date_range(last_day + pd.Timedelta(days=1), periods=horizon, freq="D")
        future = pd.DataFrame({"date": future_dates, "units_sold": recent_mean, "series": "Baseline forecast"})
        historical = history[["date", "units_sold"]].copy()
        historical["series"] = "Actual units"
        combined = pd.concat([historical, future], ignore_index=True)
        fig = px.line(combined, x="date", y="units_sold", color="series", title="Actual Demand vs Baseline Forecast",
                      color_discrete_map={"Actual units": TEAL, "Baseline forecast": PURPLE})
        fig.add_vline(x=last_day, line_dash="dash", line_color=AMBER, annotation_text="Forecast starts")
        fig.update_yaxes(title="Units sold")
        st.plotly_chart(style_chart(fig, 400), use_container_width=True)
        avg = history["units_sold"].mean()
        render_kpis([
            ("Selected product", selected_product, "SKU-level view"),
            ("Recent daily average", f"{recent_mean:.1f} units", "Trailing 7 days"),
            ("Forecast horizon", f"{horizon} days", "User-selected"),
            ("Forecast units", f"{recent_mean*horizon:,.0f}", "Flat baseline estimate"),
        ])
        st.info("This is a baseline demonstration, not a trained Prophet/LSTM model. The flat forecast uses the last 7 days' average; later we can compare it with seasonal naive, Prophet, or ML models using a time-based holdout.")
        with st.expander("View recent history"):
            st.dataframe(history.tail(30), use_container_width=True, hide_index=True)


# ---------- Page 3: Customer Analytics ----------
elif page == "Customer Analytics":
    st.markdown('<div class="rp-eyebrow">CUSTOMER INTELLIGENCE / RETENTION</div>', unsafe_allow_html=True)
    st.title("Customer Analytics")
    st.caption("Explore customer segments and a sample churn-risk label")
    segment_counts = customers["segment"].value_counts().rename_axis("segment").reset_index(name="customers")
    churn_rate = customers["churned"].mean() * 100
    active = int((customers["days_since_last_order"] <= 90).sum())
    render_kpis([
        ("Customer records", f"{len(customers):,}", "Sample customer dataset"),
        ("Active in last 90 days", f"{active:,}", "Based on recency field"),
        ("Sample churn rate", f"{churn_rate:.1f}%", "Synthetic demo label"),
        ("Avg. customer spend", money(customers["total_spend"].mean(), 2), "Lifetime spend in sample"),
    ])
    left, right = st.columns(2)
    with left:
        fig = px.pie(segment_counts, names="segment", values="customers", hole=0.62,
                     title="Customer Segment Mix", color_discrete_sequence=chart_colors())
        fig.update_traces(textposition="inside", textinfo="percent")
        st.plotly_chart(style_chart(fig, 350), use_container_width=True)
    with right:
        fig = px.histogram(customers, x="days_since_last_order", color="segment", nbins=24,
                           title="Customer Recency Distribution", color_discrete_sequence=chart_colors())
        fig.update_xaxes(title="Days since last order")
        fig.update_yaxes(title="Customer count")
        st.plotly_chart(style_chart(fig, 350), use_container_width=True)
    section_heading("Customers to re-engage", "Synthetic risk labels for demonstrating the dashboard; not a trained churn model")
    at_risk = customers[(customers["segment"].isin(["At Risk", "Needs Attention"])) | (customers["churned"] == 1)].copy()
    at_risk = at_risk.sort_values(["churned", "days_since_last_order"], ascending=[False, False]).head(15)
    at_risk["total_spend"] = at_risk["total_spend"].map(lambda x: money(x, 2))
    st.dataframe(at_risk, use_container_width=True, hide_index=True)


# ---------- Page 4: Inventory Intelligence ----------
elif page == "Inventory Intelligence":
    st.markdown('<div class="rp-eyebrow">OPERATIONS / INVENTORY</div>', unsafe_allow_html=True)
    st.title("Inventory Intelligence")
    st.caption("Find products that may need replenishment or closer review")
    low = inventory[inventory["status"] == "Low Stock"]
    over = inventory[inventory["status"] == "Overstock"]
    healthy = inventory[inventory["status"] == "Healthy"]
    render_kpis([
        ("Healthy SKUs", f"{len(healthy)}", "Within demo thresholds"),
        ("Low-stock SKUs", f"{len(low)}", "Review reorder point"),
        ("Overstock SKUs", f"{len(over)}", "Potential tied-up capital"),
        ("Inventory cost value", money(inventory["inventory_cost_value"].sum()), "Approximate sample value"),
    ])
    left, right = st.columns([1.2, 1])
    with left:
        status_counts = inventory["status"].value_counts().rename_axis("status").reset_index(name="sku_count")
        fig = px.bar(status_counts, x="status", y="sku_count", title="Inventory Health",
                     color="status", color_discrete_map={"Healthy": TEAL, "Low Stock": RED, "Overstock": AMBER})
        fig.update_xaxes(title="")
        fig.update_yaxes(title="Number of SKUs")
        st.plotly_chart(style_chart(fig, 340, False), use_container_width=True)
    with right:
        inv_plot = inventory.copy()
        fig = px.scatter(inv_plot, x="avg_daily_demand_30d", y="stock_on_hand",
                         size="inventory_cost_value", color="status", hover_name="product_name",
                         title="Stock vs Daily Demand",
                         color_discrete_map={"Healthy": TEAL, "Low Stock": RED, "Overstock": AMBER})
        fig.update_xaxes(title="Average daily demand")
        fig.update_yaxes(title="Current stock (units)")
        st.plotly_chart(style_chart(fig, 340), use_container_width=True)
    section_heading("Replenishment recommendations", "Starter rule: reorder point = expected lead-time demand + safety stock")
    rec = inventory.copy()
    rec["recommended_order_qty"] = (rec["reorder_point"] * 1.5 - rec["stock_on_hand"]).clip(lower=0).round().astype(int)
    rec = rec.sort_values(["status", "recommended_order_qty"], ascending=[True, False])
    st.dataframe(rec[["sku","product_name","category","stock_on_hand","avg_daily_demand_30d",
                      "lead_time_days","safety_stock","reorder_point","recommended_order_qty","status"]],
                 use_container_width=True, hide_index=True)
    st.caption("Reorder quantities are heuristic demo suggestions; validate supplier minimums, lead times, and real stock before operational use.")


# ---------- Page 5: Model Monitoring ----------
elif page == "Model Monitoring":
    st.markdown('<div class="rp-eyebrow">MLOPS / MODEL HEALTH</div>', unsafe_allow_html=True)
    st.title("Model Monitoring")
    st.caption("Starter monitoring view with clearly labeled demo metrics")
    render_kpis([
        ("Forecast model", "Baseline v0.1", "7-day moving average"),
        ("Forecast MAE*", "8.4 units", "Illustrative placeholder"),
        ("Data drift score*", "0.08", "Illustrative placeholder"),
        ("Pipeline status", "Demo only", "No scheduled pipeline yet"),
    ])
    st.warning("MAE and drift values on this page are placeholders for the UI. They are not calculated from a trained model. We will replace them with measured values when model evaluation and monitoring are implemented.")
    rng = np.random.default_rng(7)
    runs = pd.DataFrame({
        "run": [f"Run {i:02d}" for i in range(1, 15)],
        "mae": np.round(np.linspace(12.5, 8.4, 14) + rng.normal(0, 0.65, 14), 2),
        "drift_score": np.round(np.clip(rng.normal(0.07, 0.025, 14), 0.01, 0.16), 3),
    })
    left, right = st.columns(2)
    with left:
        fig = px.line(runs, x="run", y="mae", markers=True, title="Illustrative Forecast MAE by Run",
                      color_discrete_sequence=[TEAL])
        fig.update_yaxes(title="MAE (units)")
        st.plotly_chart(style_chart(fig, 340, False), use_container_width=True)
    with right:
        fig = px.bar(runs, x="run", y="drift_score", title="Illustrative Data Drift Score",
                     color="drift_score", color_continuous_scale=["#1B6A61", TEAL, AMBER])
        fig.add_hline(y=0.15, line_dash="dash", line_color=RED, annotation_text="Demo alert threshold")
        fig.update_yaxes(title="Drift score")
        st.plotly_chart(style_chart(fig, 340, False), use_container_width=True)
    section_heading("Pipeline & model status", "Example monitoring table; no pipeline is running yet")
    status = pd.DataFrame([
        ["Demand baseline", "Demo calculation", "Available"],
        ["Customer churn labels", "Synthetic dataset", "Available"],
        ["Inventory reorder rules", "Heuristic calculation", "Available"],
        ["MLflow experiment tracking", "Not configured", "Planned"],
        ["Scheduled retraining", "Not configured", "Planned"],
    ], columns=["component","implementation","status"])
    st.dataframe(status, use_container_width=True, hide_index=True)

st.divider()
st.caption("RetailPulse • AI Retail Intelligence • Portfolio demo • Sample/synthetic data — not connected to a live retailer")

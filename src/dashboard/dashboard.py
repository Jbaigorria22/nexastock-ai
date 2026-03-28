# src/dashboard/dashboard.py
import streamlit as st
import requests
import plotly.graph_objects as go
import streamlit.components.v1 as components

API_BASE = "https://l5onbag8e6.execute-api.us-east-1.amazonaws.com/prod"

st.set_page_config(
    page_title="Inventory Decision Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── CSS corporativo ────────────────────────────────────────────────────────────
st.markdown("""
<style>
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 0 !important; max-width: 100% !important; }
.topbar {
    background: #0d2b5e; padding: 14px 32px;
    display: flex; align-items: center; justify-content: space-between;
}
.topbar-title { color: #ffffff; font-size: 16px; font-weight: 600; margin: 0; }
.topbar-sub   { color: #7fa8d8; font-size: 12px; margin: 2px 0 0; }
.topbar-badge {
    background: #1a4a8a; border: 1px solid #2d6ab0;
    border-radius: 6px; padding: 4px 12px; font-size: 11px; color: #7fa8d8;
}
.main-content { padding: 24px 32px; }
.kpi-grid {
    display: grid; grid-template-columns: repeat(5, minmax(0, 1fr));
    gap: 12px; margin-bottom: 24px;
}
.kpi-card { background: #ffffff; border: 1px solid #dde3ef; border-radius: 10px; padding: 16px 18px; }
.kpi-card.red   { border-left: 4px solid #e24b4a; border-radius: 0 10px 10px 0; }
.kpi-card.amber { border-left: 4px solid #ef9f27; border-radius: 0 10px 10px 0; }
.kpi-card.blue  { border-left: 4px solid #185fa5; border-radius: 0 10px 10px 0; }
.kpi-label { font-size: 10px; font-weight: 600; color: #6b7a99; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 6px; }
.kpi-value { font-size: 28px; font-weight: 600; color: #0d2b5e; line-height: 1; }
.kpi-value.danger  { color: #c0392b; }
.kpi-value.warning { color: #b8640a; }
.kpi-delta { font-size: 11px; margin-top: 5px; color: #6b7a99; }
.kpi-delta.ok      { color: #1e7e4a; }
.kpi-delta.danger  { color: #c0392b; }
.kpi-delta.warning { color: #b8640a; }
.section-label {
    font-size: 10px; font-weight: 600; color: #6b7a99;
    text-transform: uppercase; letter-spacing: 0.1em; margin: 0 0 12px; padding: 0;
}
.panel { background: #ffffff; border: 1px solid #dde3ef; border-radius: 10px; padding: 18px 20px; margin-bottom: 16px; }
.panel-title { font-size: 13px; font-weight: 600; color: #0d2b5e; margin-bottom: 14px; display: flex; align-items: center; gap: 8px; }
.dot { width: 8px; height: 8px; border-radius: 50%; display: inline-block; }
</style>
""", unsafe_allow_html=True)


# ── API functions ──────────────────────────────────────────────────────────────

def api_get(path):
    try:
        r = requests.get(f"{API_BASE}{path}", timeout=5)
        r.raise_for_status()
        return r.json()
    except Exception:
        return None

def api_post(path, payload):
    try:
        r = requests.post(f"{API_BASE}{path}", json=payload, timeout=15)
        r.raise_for_status()
        return r.json()
    except Exception:
        return None


# ── Load data ──────────────────────────────────────────────────────────────────

inventory = api_get("/inventory/") or []
risk      = api_get("/risk/analysis") or {}
purchase  = api_get("/purchase/plan") or {}
connected = bool(inventory)


# ── Helpers ────────────────────────────────────────────────────────────────────

def val(p, *keys, default=0):
    for k in keys:
        if k in p and p[k] is not None:
            return p[k]
    return default


# ── Topbar ─────────────────────────────────────────────────────────────────────

status_badge = "API connected" if connected else "API offline"
st.markdown(f"""
<div class="topbar">
  <div>
    <p class="topbar-title">Inventory Decision Dashboard</p>
    <p class="topbar-sub">AI-powered · Real-time analysis</p>
  </div>
  <span class="topbar-badge">{status_badge}</span>
</div>
<div class="main-content">
""", unsafe_allow_html=True)

if not connected:
    st.error("Cannot connect to API. Start the FastAPI backend first.")
    st.stop()


# ── Métricas ───────────────────────────────────────────────────────────────────

total      = len(inventory)
avg_stock  = round(sum(val(p, "stock") for p in inventory) / total, 1) if total else 0
total_val  = sum(val(p, "stock") * val(p, "price") for p in inventory)
critical   = risk.get("critical", [])
high_risk  = risk.get("high_risk", [])
ok_prods   = risk.get("ok", [])
plan       = purchase.get("plan", [])
total_cost = purchase.get("total_estimated_cost", 0)

st.markdown('<p class="section-label">Key metrics</p>', unsafe_allow_html=True)
st.markdown(f"""
<div class="kpi-grid">
  <div class="kpi-card">
    <div class="kpi-label">Total products</div>
    <div class="kpi-value">{total}</div>
    <div class="kpi-delta ok">All tracked</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-label">Avg stock level</div>
    <div class="kpi-value">{avg_stock}</div>
    <div class="kpi-delta">units per product</div>
  </div>
  <div class="kpi-card red">
    <div class="kpi-label">Critical</div>
    <div class="kpi-value danger">{len(critical)}</div>
    <div class="kpi-delta danger">{"Restock immediately" if critical else "None right now"}</div>
  </div>
  <div class="kpi-card amber">
    <div class="kpi-label">High risk</div>
    <div class="kpi-value warning">{len(high_risk)}</div>
    <div class="kpi-delta warning">{"Plan restocking" if high_risk else "None right now"}</div>
  </div>
  <div class="kpi-card blue">
    <div class="kpi-label">Inventory value</div>
    <div class="kpi-value" style="font-size:20px">${total_val:,.0f}</div>
    <div class="kpi-delta ok">Estimated</div>
  </div>
</div>
""", unsafe_allow_html=True)


# ── Gráficos ───────────────────────────────────────────────────────────────────

st.markdown('<p class="section-label">Analysis</p>', unsafe_allow_html=True)

col_chart, col_risk = st.columns([3, 2])

with col_chart:
    status_map = {p["name"]: p.get("status", "OK") for p in critical + high_risk + ok_prods}
    color_map  = {"CRITICAL": "#e24b4a", "HIGH_RISK": "#ef9f27", "OK": "#185fa5"}

    names    = [p.get("name", "?") for p in inventory]
    stocks   = [val(p, "stock") for p in inventory]
    reorders = [val(p, "reorder_level") for p in inventory]
    colors   = [color_map.get(status_map.get(n, "OK"), "#185fa5") for n in names]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=names, y=stocks,
        marker_color=colors,
        name="Current stock",
        hovertemplate="<b>%{x}</b><br>Stock: %{y}<extra></extra>"
    ))
    fig.add_trace(go.Scatter(
        x=names, y=reorders,
        mode="lines+markers",
        line=dict(color="#0d2b5e", width=1.5, dash="dot"),
        marker=dict(size=6, color="#0d2b5e"),
        name="Reorder level",
        hovertemplate="<b>%{x}</b><br>Reorder at: %{y}<extra></extra>"
    ))
    fig.update_layout(
        plot_bgcolor="#ffffff", paper_bgcolor="#ffffff",
        margin=dict(l=0, r=0, t=8, b=0),
        height=240,
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02,
            font=dict(size=11, color="#6b7a99"),
            bgcolor="rgba(0,0,0,0)"
        ),
        xaxis=dict(showgrid=False, tickfont=dict(size=11, color="#6b7a99"), linecolor="#dde3ef"),
        yaxis=dict(showgrid=True, gridcolor="#f4f6f9", tickfont=dict(size=11, color="#6b7a99"), zeroline=False),
        bargap=0.35,
    )
    st.markdown('<div class="panel"><div class="panel-title"><span class="dot" style="background:#185fa5"></span>Stock levels vs reorder threshold</div>', unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)


# ── Risk snapshot — usa components.html para CSS propio ────────────────────────

def badge_html(status):
    if status == "CRITICAL":
        return '<span class="badge badge-critical">Critical</span>'
    elif status == "HIGH_RISK":
        return '<span class="badge badge-high">High risk</span>'
    return '<span class="badge badge-ok">OK</span>'

all_classified = critical + high_risk + ok_prods
rows_html = ""
for p in all_classified:
    name    = p.get("name", "Unknown")
    stock   = val(p, "stock")
    reorder = val(p, "reorder_level")
    status  = p.get("status", "OK")
    rows_html += f"""
    <div class="risk-row">
      <div>
        <div class="risk-name">{name}</div>
        <div class="risk-stock">Stock: {stock} &nbsp;·&nbsp; Reorder: {reorder}</div>
      </div>
      {badge_html(status)}
    </div>"""

with col_risk:
    components.html(f"""
    <!DOCTYPE html><html><head>
    <style>
      * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, sans-serif; }}
      .panel {{ background: #fff; border: 1px solid #dde3ef; border-radius: 10px; padding: 18px 20px; }}
      .panel-title {{ font-size: 13px; font-weight: 600; color: #0d2b5e; margin-bottom: 14px; display: flex; align-items: center; gap: 8px; }}
      .dot {{ width: 8px; height: 8px; border-radius: 50%; display: inline-block; background: #e24b4a; }}
      .risk-row {{ display: flex; align-items: center; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #f4f6f9; }}
      .risk-row:last-child {{ border-bottom: none; }}
      .risk-name  {{ font-size: 13px; font-weight: 500; color: #1a2540; }}
      .risk-stock {{ font-size: 11px; color: #6b7a99; margin-top: 2px; }}
      .badge {{ font-size: 10px; font-weight: 600; padding: 3px 9px; border-radius: 4px; }}
      .badge-critical {{ background: #fdeaea; color: #a32d2d; }}
      .badge-high     {{ background: #fdf3e3; color: #854f0b; }}
      .badge-ok       {{ background: #eaf5ef; color: #1e7e4a; }}
    </style>
    </head><body>
    <div class="panel">
      <div class="panel-title"><span class="dot"></span>Risk snapshot</div>
      {rows_html}
    </div>
    </body></html>
    """, height=320)


# ── Purchase plan ──────────────────────────────────────────────────────────────

if plan:
    st.markdown('<p class="section-label">Purchase plan</p>', unsafe_allow_html=True)
    rows = ""
    for item in plan:
        dot_color = "#e24b4a" if item.get("current_stock", 0) == 0 else "#ef9f27"
        rows += f"""<tr>
          <td><span style="width:7px;height:7px;border-radius:50%;background:{dot_color};display:inline-block;margin-right:6px"></span>{item.get('product','')}</td>
          <td>{item.get('current_stock', 0)}</td>
          <td>{item.get('reorder_level', 0)}</td>
          <td style="font-weight:600">{item.get('suggested_order', 0)}</td>
          <td>${item.get('unit_price', 0):.2f}</td>
          <td style="font-weight:600;color:#0d2b5e">${item.get('estimated_cost', 0):,.2f}</td>
        </tr>"""

    st.markdown(f"""
    <div class="panel">
      <div class="panel-title">
        <span class="dot" style="background:#1d9e75"></span>
        {len(plan)} items to restock &nbsp;·&nbsp; Estimated total: <span style="color:#1e7e4a">${total_cost:,.2f}</span>
      </div>
      <table style="width:100%;border-collapse:collapse;font-size:12px">
        <thead>
          <tr style="border-bottom:1px solid #dde3ef">
            <th style="text-align:left;font-size:10px;font-weight:600;color:#6b7a99;text-transform:uppercase;letter-spacing:.06em;padding:0 12px 8px 0">Product</th>
            <th style="text-align:left;font-size:10px;font-weight:600;color:#6b7a99;text-transform:uppercase;letter-spacing:.06em;padding:0 12px 8px 0">Current stock</th>
            <th style="text-align:left;font-size:10px;font-weight:600;color:#6b7a99;text-transform:uppercase;letter-spacing:.06em;padding:0 12px 8px 0">Reorder level</th>
            <th style="text-align:left;font-size:10px;font-weight:600;color:#6b7a99;text-transform:uppercase;letter-spacing:.06em;padding:0 12px 8px 0">Order qty</th>
            <th style="text-align:left;font-size:10px;font-weight:600;color:#6b7a99;text-transform:uppercase;letter-spacing:.06em;padding:0 12px 8px 0">Unit price</th>
            <th style="text-align:left;font-size:10px;font-weight:600;color:#6b7a99;text-transform:uppercase;letter-spacing:.06em;padding:0 12px 8px 0">Est. cost</th>
          </tr>
        </thead>
        <tbody>{rows}</tbody>
      </table>
    </div>
    """, unsafe_allow_html=True)


# ── AI Summary ─────────────────────────────────────────────────────────────────

st.markdown('<p class="section-label">AI insights</p>', unsafe_allow_html=True)

if "ai_summary" not in st.session_state:
    st.session_state.ai_summary = None

col_sum, _ = st.columns([2, 1])
with col_sum:
    if st.button("Generate executive summary", key="btn_summary"):
        with st.spinner("Analyzing inventory..."):
            result = api_get("/ai/summary")
            st.session_state.ai_summary = result.get("summary", "No summary.") if result else "API unavailable."

if st.session_state.ai_summary:
    st.markdown(f"""
    <div class="panel" style="border-left: 3px solid #185fa5; border-radius: 0 10px 10px 0;">
      <div class="panel-title"><span class="dot" style="background:#185fa5"></span>Executive summary</div>
      <p style="font-size:13px;color:#1a2540;line-height:1.7;margin:0">{st.session_state.ai_summary}</p>
    </div>
    """, unsafe_allow_html=True)


# ── AI Copilot ─────────────────────────────────────────────────────────────────

st.markdown('<p class="section-label">AI Copilot</p>', unsafe_allow_html=True)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

col_input, col_btn = st.columns([5, 1])
with col_input:
    user_input = st.text_input(
        "question",
        placeholder="e.g. What should I restock first? Which products are critical?",
        label_visibility="collapsed",
        key="copilot_input"
    )
with col_btn:
    ask = st.button("Ask AI", key="btn_copilot", use_container_width=True)

if ask and user_input.strip():
    with st.spinner("Analyzing..."):
        result = api_post("/ai/copilot", {"question": user_input})
        answer = result.get("answer", "No response.") if result else "API unavailable."
    st.session_state.chat_history.append(("you", user_input.strip()))
    st.session_state.chat_history.append(("ai", answer))

if st.session_state.chat_history:
    messages_html = ""
    for role, msg in reversed(st.session_state.chat_history):
        safe_msg = msg.replace("\n", "<br>")
        if role == "you":
            messages_html += f"""
            <div class="msg-you">
              <div class="msg-label">You</div>
              <div class="msg-bubble-you">{safe_msg}</div>
            </div>"""
        else:
            messages_html += f"""
            <div class="msg-ai">
              <div class="msg-label-ai">AI Analyst</div>
              <div class="msg-bubble-ai">{safe_msg}</div>
            </div>"""

    components.html(f"""
    <!DOCTYPE html><html><head>
    <style>
      * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, sans-serif; }}
      body {{ background: transparent; padding: 0; }}
      .chat-wrap {{
        background: #ffffff; border: 1px solid #dde3ef;
        border-radius: 10px; padding: 16px 20px;
        display: flex; flex-direction: column; gap: 12px;
      }}
      .msg-label    {{ font-size: 10px; font-weight: 600; color: #6b7a99; text-transform: uppercase; letter-spacing: .06em; margin-bottom: 4px; }}
      .msg-label-ai {{ font-size: 10px; font-weight: 600; color: #185fa5; text-transform: uppercase; letter-spacing: .06em; margin-bottom: 4px; }}
      .msg-bubble-you {{
        background: #f0f4fb; border-radius: 8px;
        padding: 10px 14px; font-size: 13px; color: #0d2b5e; font-weight: 500;
      }}
      .msg-bubble-ai {{
        background: #ffffff; border: 1px solid #dde3ef;
        border-left: 3px solid #185fa5; border-radius: 0 8px 8px 0;
        padding: 12px 16px; font-size: 13px; color: #1a2540;
        line-height: 1.7; white-space: pre-wrap;
      }}
      strong {{ color: #0d2b5e; font-weight: 600; }}
    </style>
    </head><body>
    <div class="chat-wrap">{messages_html}</div>
    </body></html>
    """, height=min(120 + len(st.session_state.chat_history) * 80, 600), scrolling=True)

else:
    st.markdown("""
    <div class="panel" style="text-align:center;padding:32px">
      <p style="font-size:14px;font-weight:600;color:#0d2b5e;margin:0 0 6px">AI Inventory Analyst</p>
      <p style="font-size:13px;color:#6b7a99;margin:0">Ask anything about your inventory.<br>
      <span style="font-size:11px">Try: "What should I restock first?" · "Which products are critical?" · "How much will restocking cost?"</span></p>
    </div>
    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
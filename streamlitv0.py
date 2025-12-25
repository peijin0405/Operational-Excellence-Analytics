import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import re
import hashlib
from datetime import date

# ======================
# Page config
# ======================
st.set_page_config(page_title="Sorting Volume Dashboard", layout="wide")

# ======================
# CSS (卡片化、留白、字体)
# ======================
st.markdown("""
<style>
.block-container { padding-top: 1.2rem; padding-bottom: 2rem; }
h1 { font-size: 2.1rem; margin-bottom: 0.2rem; }
.small-note { color: #6b7280; font-size: 0.92rem; }
.card {
  background: #ffffff;
  border: 1px solid rgba(0,0,0,0.06);
  border-radius: 16px;
  padding: 14px 14px 10px 14px;
}
hr.soft {
  border: none; height: 1px; background: rgba(0,0,0,0.08);
  margin: 0.6rem 0 0.9rem 0;
}
div[data-testid="stMetric"]{
  background: #ffffff;
  border: 1px solid rgba(0,0,0,0.06);
  border-radius: 14px;
  padding: 10px 12px;
  box-shadow: 0 6px 18px rgba(0,0,0,0.05);
}
</style>
""", unsafe_allow_html=True)

# ======================
# Config
# ======================
DEFAULT_FILE_PATH = "data/scanRecord_1766632272775.xlsx"
DEFAULT_SORTER_NAME = "sorter"  # 仍保留 sorter 概念（图1需要）
SHIFT_OPTIONS = ["Early (07-15)", "Mid (15-23)", "Night (23-07)"]
SORTING_CENTER = "MIA.H"

# ======================
# Helpers
# ======================

def get_dataset_id(uploaded, default_path: str) -> str:
    """
    用于判断当前数据集是否发生变化
    """
    if uploaded is None:
        return f"default::{default_path}"
    b = uploaded.getvalue()
    return "upload::" + hashlib.md5(b).hexdigest()

def read_current_raw(uploaded, default_path: str) -> pd.DataFrame:
    """
    读取当前数据源：上传文件优先，否则默认文件
    """
    if uploaded is None:
        return load_raw(default_path)
    return pd.read_excel(uploaded)



def bin_start(tb: str) -> int:
    return int(str(tb).split("-")[0])

@st.cache_data
def load_raw(file_path: str) -> pd.DataFrame:
    return pd.read_excel(file_path)

def preprocess(df: pd.DataFrame) -> pd.DataFrame:
    needed = {"Operation time", "Operator", "Waybill No."}
    miss = needed - set(df.columns)
    if miss:
        raise ValueError(f"Missing columns: {miss}")

    df = df.copy()

    # 时间解析：如 "14:59:55 13/12/2025"
    df["op_time"] = pd.to_datetime(df["Operation time"], dayfirst=True, errors="coerce")

    # Operator 清洗
    df["Operator"] = df["Operator"].astype(str).str.strip()
    df = df[
        df["Operator"].notna()
        & (df["Operator"] != "")
        & (df["Operator"].str.lower() != "nan")
    ].copy()

    # 去掉时间解析失败
    df = df[df["op_time"].notna()].copy()

    # date / hour / time_bin
    df["op_date"] = df["op_time"].dt.date
    df["hour"] = df["op_time"].dt.hour
    df["time_bin"] = df["hour"].astype(int).astype(str) + "-" + (df["hour"] + 1).astype(int).astype(str)

    return df

def build_pivot(df: pd.DataFrame) -> tuple[pd.DataFrame, list]:
    agg = (
        df.groupby(["Operator", "time_bin"])["Waybill No."]
          .nunique()
          .reset_index(name="scan_cnt")
    )

    time_bins = sorted(agg["time_bin"].unique(), key=bin_start)

    pivot = (
        agg.pivot_table(index="Operator", columns="time_bin", values="scan_cnt", fill_value=0)
           .reindex(columns=time_bins)
           .sort_index()
    )

    pivot = pivot.loc[:, (pivot != 0).any(axis=0)]
    pivot = pivot.loc[(pivot != 0).any(axis=1), :]

    time_bins = [c for c in time_bins if c in pivot.columns]
    return pivot, time_bins

def compute_time_context(df: pd.DataFrame) -> str:
    """
    专业面板时间显示：
    - 同日：YYYY-MM-DD | HH:MM–HH:MM
    - 跨日：YYYY-MM-DD HH:MM → YYYY-MM-DD HH:MM
    """
    t_start = df["op_time"].min()
    t_end = df["op_time"].max()

    if pd.isna(t_start) or pd.isna(t_end):
        return "-"

    same_day = (t_start.date() == t_end.date())
    if same_day:
        return f'{t_start.strftime("%Y-%m-%d")} | {t_start.strftime("%H:%M")}–{t_end.strftime("%H:%M")}'
    else:
        return f'{t_start.strftime("%Y-%m-%d %H:%M")} → {t_end.strftime("%Y-%m-%d %H:%M")}'

def kpi_summary(pivot: pd.DataFrame, time_bins: list, sorter_name: str):
    if pivot.empty or len(time_bins) == 0:
        total_series = pd.Series([], dtype=float)
        sorter_series = pd.Series([], dtype=float)
    else:
        total_series = pivot.reindex(columns=time_bins).sum(axis=0)
        sorter_series = (
            pivot.loc[sorter_name].reindex(time_bins) if sorter_name in pivot.index
            else pd.Series(0, index=time_bins)
        ).fillna(0)

    total_all = int(total_series.sum()) if len(total_series) else 0
    sorter_all = int(sorter_series.sum()) if len(sorter_series) else 0
    share = (sorter_all / total_all * 100) if total_all > 0 else 0.0

    if len(total_series) > 0:
        peak_tb = str(total_series.idxmax())
        peak_val = int(total_series.max())
    else:
        peak_tb, peak_val = "-", 0

    return total_all, sorter_all, share, peak_tb, peak_val

def style_layout_common(fig, time_bins, y_title):
    fig.update_layout(
        height=520,
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=62, r=26, t=24, b=54),
        legend=dict(
            orientation="h",
            yanchor="top",
            y=1.14,
            xanchor="left",
            x=0,
            font=dict(size=12),
            title=""
        ),
        xaxis=dict(
            title="Time Bin",
            type="category",
            categoryorder="array",
            categoryarray=time_bins,
            showline=True,
            linecolor="rgba(0,0,0,0.55)",
            linewidth=1,
            ticks="outside",
            tickfont=dict(size=12),
            gridcolor="rgba(0,0,0,0.05)",
        ),
        yaxis=dict(
            title=y_title,
            showline=True,
            linecolor="rgba(0,0,0,0.55)",
            linewidth=1,
            ticks="outside",
            tickfont=dict(size=12),
            gridcolor="rgba(0,0,0,0.07)",
            zeroline=False,
            rangemode="tozero"
        ),
        hovermode="x unified",
    )
    return fig
# ************************ 各组数据可视化准备 **************************


def build_employee_efficiency_df(
    pivot: pd.DataFrame,
    include_pattern: str = None,
    exclude_pattern: str = None,
    drop_all_zero: bool = True
) -> pd.DataFrame:
    """
    从 pivot 表中，按正则筛选员工，返回 员工 × time_bin 的效率 DataFrame
    """

    df = pivot.copy()
    df.index = df.index.astype(str).str.strip()
    df.columns = [str(c).strip() for c in df.columns]

    # 自动按时间排序
    def bin_start(tb: str) -> int:
        return int(str(tb).split("-")[0])

    time_bins = sorted(df.columns, key=bin_start)
    df = df[time_bins]

    if include_pattern:
        mask = df.index.str.contains(include_pattern, flags=re.IGNORECASE, regex=True, na=False)
        df = df.loc[mask]

    if exclude_pattern:
        mask = ~df.index.str.contains(exclude_pattern, flags=re.IGNORECASE, regex=True, na=False)
        df = df.loc[mask]

    if drop_all_zero:
        df = df.loc[(df != 0).any(axis=1)]

    return df



def build_company_relative_efficiency_dfs(
    pivot: pd.DataFrame,
    employee_pattern: str,
    drop_all_zero: bool = True,
    eps: float = 1e-9,   # 防止除零
):
    """
    公司内比较版本：
    - hour_mean 用公司内部员工的每小时均值
    - residual 也用公司内部 hour_mean 做去趋势
    """

    df = pivot.copy()
    df.index = df.index.astype(str).str.strip()
    df.columns = [str(c).strip() for c in df.columns]

    def bin_start(tb: str) -> int:
        return int(str(tb).split("-")[0])

    time_bins = sorted(df.columns, key=bin_start)
    df = df[time_bins]

    # 选公司员工
    mask = df.index.str.contains(employee_pattern, flags=re.IGNORECASE, regex=True, na=False)
    df_emp = df.loc[mask].copy()

    if drop_all_zero:
        df_emp = df_emp.loc[(df_emp != 0).any(axis=1)]

    # ✅ 公司内部“货量基准”：每小时公司内部均值
    hour_mean_in_company = df_emp.mean(axis=0).replace(0, np.nan)

    # Relative Efficiency（公司内）
    df_rel_eff = df_emp.div(hour_mean_in_company + eps, axis=1)

    # De-trended residual（公司内）
    residual = df_emp.sub(hour_mean_in_company, axis=1)

    # 图3汇总指标
    df_summary = pd.DataFrame(index=df_emp.index)
    df_summary["Avg_Relative_Efficiency"] = df_rel_eff.mean(axis=1)
    df_summary["DeTrended_Std"] = residual.std(axis=1)
    df_summary["DeTrended_CV"] = df_summary["DeTrended_Std"] / df_summary["Avg_Relative_Efficiency"].replace(0, np.nan)

    return df_rel_eff, df_summary



# ===== Shift 过滤（重点：Night(23-07) 跨日但归属前一天）=====
def filter_by_shift(df_in: pd.DataFrame, start_date, end_date, shift_label: str) -> pd.DataFrame:
    df2 = df_in.copy()
    hr = df2["op_time"].dt.hour

    if shift_label == "Early (07-15)":
        df2["shift_date"] = df2["op_time"].dt.date
        cond_shift = (hr >= 7) & (hr < 15)

    elif shift_label == "Mid (15-23)":
        df2["shift_date"] = df2["op_time"].dt.date
        cond_shift = (hr >= 15) & (hr < 23)

    else:  # Night (23-07)
        # 23:00-23:59 => shift_date = 当天
        # 00:00-06:59 => shift_date = 前一天
        shift_date = df2["op_time"].dt.date
        shift_date = np.where(hr < 7, (df2["op_time"] - pd.Timedelta(days=1)).dt.date, shift_date)
        df2["shift_date"] = shift_date
        cond_shift = (hr >= 23) | (hr < 7)

    cond_date = (df2["shift_date"] >= start_date) & (df2["shift_date"] <= end_date)
    return df2[cond_shift & cond_date].copy()

# ===== 图1：柱顶 total + sorter% =====
def fig_sorter_vs_total(pivot: pd.DataFrame, time_bins: list, sorter_name: str):
    p = pivot.reindex(columns=time_bins).apply(pd.to_numeric, errors="coerce").fillna(0)

    total_series = p.sum(axis=0)
    sorter_series = p.loc[sorter_name] if sorter_name in p.index else pd.Series(0, index=time_bins)
    sorter_series = sorter_series.reindex(time_bins).fillna(0)
    others_series = total_series - sorter_series

    total_safe = total_series.replace(0, np.nan)
    share_pct = (sorter_series / total_safe * 100).round(1)
    share_text = ["" if pd.isna(v) else f"{v:.1f}%" for v in share_pct.values]

    fig = go.Figure()

    fig.add_bar(
        x=time_bins,
        y=others_series.values,
        name="Others (All non-sorter)",
        hovertemplate="Time Bin: %{x}<br>Others: %{y}<extra></extra>",
        marker=dict(opacity=0.85),
    )

    fig.add_bar(
        x=time_bins,
        y=sorter_series.values,
        name="Sorter",
        hovertemplate=(
            "Time Bin: %{x}<br>"
            "Sorter: %{y}<br>"
            "Sorter Share: %{customdata}%<extra></extra>"
        ),
        customdata=share_pct.values,
        marker=dict(opacity=0.95),
    )

    fig.add_scatter(
        x=time_bins,
        y=total_series.values,
        mode="text",
        text=[f"{int(v)}" for v in total_series.values],
        textposition="top center",
        textfont=dict(size=14),
        showlegend=False,
        hoverinfo="skip",
    )

    y_mid = (others_series + sorter_series / 2).values
    fig.add_scatter(
        x=time_bins,
        y=y_mid,
        mode="text",
        text=share_text,
        textposition="middle center",
        textfont=dict(size=14),
        showlegend=False,
        hoverinfo="skip",
    )

    fig.update_layout(barmode="stack", bargap=0.28)
    fig = style_layout_common(fig, time_bins, y_title="Scan Count")
    return fig

# ===== 图2：每个点显示数值 =====
def fig_labor_group_lines(pivot: pd.DataFrame, time_bins: list):
    p = pivot.reindex(columns=time_bins).apply(pd.to_numeric, errors="coerce").fillna(0)

    jou_sum = p.loc[p.index.str.startswith("JOU"), time_bins].sum(axis=0)
    rd_sum  = p.loc[p.index.str.startswith("RD"),  time_bins].sum(axis=0)
    pr_sum  = p.loc[p.index.str.startswith("pr"),  time_bins].sum(axis=0)

    def add_line(fig, name, y):
        fig.add_scatter(
            x=time_bins,
            y=y.values,
            mode="lines+markers+text",
            name=name,
            text=[int(v) for v in y.values],
            textposition="top center",
            textfont=dict(size=12),
            hovertemplate=f"Time Bin: %{{x}}<br>{name}: %{{y}}<extra></extra>",
        )

    fig = go.Figure()
    add_line(fig, "JOU", jou_sum)
    add_line(fig, "RD", rd_sum)
    add_line(fig, "pr", pr_sum)

    fig = style_layout_common(fig, time_bins, y_title="Total Volume")
    return fig

# ***************************** 各组数据可视化 *******************************************


def make_employee_curve_fig(df_emp: pd.DataFrame, title: str):
    plot_df = df_emp.copy()

    # time_bins：确保按列顺序显示
    time_bins = [str(c).strip() for c in plot_df.columns]
    n_emp = plot_df.shape[0]

    fig = go.Figure()

    # 1) 员工曲线
    for emp in plot_df.index:
        y = plot_df.loc[emp].values
        fig.add_scatter(
            x=time_bins,
            y=y,
            mode="lines+markers",
            name=str(emp),
            hovertemplate=f"Time Bin: %{{x}}<br>{emp}: %{{y}}<extra></extra>",
        )

    # 2) 全局平均值（所有员工 × 所有 time-bin）
    if not plot_df.empty:
        global_avg = float(np.nanmean(plot_df.to_numpy()))
    else:
        global_avg = 0.0

    benchmark = 600  # 写死

    # 3) benchmark 横线（细线 + 无文字）
    fig.add_hline(
        y=benchmark,
        line_width=1,
        line_dash="solid",
        line_color="rgba(0,0,0,0.55)"
    )

    # 4) 全局平均横线（细虚线 + 有文字）
    fig.add_hline(
        y=global_avg,
        line_width=1,
        line_dash="dash",
        line_color="rgba(0,0,0,0.55)",
        annotation_text=f"Overall Avg = {global_avg:.1f}",
        annotation_position="bottom right",
    )

    # 5) legend 位置保持不变
    fig.update_layout(
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.14,
            xanchor="left",
            x=0.02,
        ),
    )

    # 6) 统一风格
    fig = style_layout_common(fig, time_bins, y_title="Scan Count")
    return fig





def make_quadrant_fig(df_summary: pd.DataFrame, title: str, y_ref: str = "median"):
    dfp = (
        df_summary.replace([np.inf, -np.inf], np.nan)
                  .dropna(subset=["Avg_Relative_Efficiency", "DeTrended_CV"])
                  .copy()
    )
    n_emp = dfp.shape[0]

    x_ref = 1.0
    y_ref_val = dfp["DeTrended_CV"].median() if y_ref == "median" else dfp["DeTrended_CV"].mean()

    x_min, x_max = float(dfp["Avg_Relative_Efficiency"].min()), float(dfp["Avg_Relative_Efficiency"].max())
    y_min, y_max = float(dfp["DeTrended_CV"].min()), float(dfp["DeTrended_CV"].max())

    x_pad = (x_max - x_min) * 0.08 if x_max > x_min else 0.2
    y_pad = (y_max - y_min) * 0.10 if y_max > y_min else 0.2
    x_min -= x_pad; x_max += x_pad
    y_min = max(0, y_min - y_pad); y_max += y_pad

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=dfp["Avg_Relative_Efficiency"],
        y=dfp["DeTrended_CV"],
        mode="markers+text",
        text=[str(i) for i in dfp.index],
        textposition="top center",
        hovertemplate="Employee=%{text}<br>AvgRel=%{x:.2f}<br>DeTrendedCV=%{y:.2f}<extra></extra>",
        showlegend=False,
    ))

    # 四象限背景
    fig.add_shape(type="rect", x0=x_min, x1=x_ref, y0=y_min, y1=y_ref_val, layer="below",
                  line_width=0, fillcolor="rgba(0,0,0,0.03)")
    fig.add_shape(type="rect", x0=x_ref, x1=x_max, y0=y_min, y1=y_ref_val, layer="below",
                  line_width=0, fillcolor="rgba(0,0,0,0.03)")
    fig.add_shape(type="rect", x0=x_min, x1=x_ref, y0=y_ref_val, y1=y_max, layer="below",
                  line_width=0, fillcolor="rgba(220, 53, 69, 0.18)")
    fig.add_shape(type="rect", x0=x_ref, x1=x_max, y0=y_ref_val, y1=y_max, layer="below",
                  line_width=0, fillcolor="rgba(0,0,0,0.03)")

    fig.add_vline(x=x_ref, line_width=1, line_dash="dash")
    fig.add_hline(y=y_ref_val, line_width=1, line_dash="dash")

    # 象限标签
    x_left  = x_min + 0.5 * (x_ref - x_min)
    x_right = x_ref + 0.5 * (x_max - x_ref)
    y_low   = y_min + 0.5 * (y_ref_val - y_min)
    y_high  = y_ref_val + 0.5 * (y_max - y_ref_val)
    label_style = dict(showarrow=False, align="center",
                       bordercolor="rgba(0,0,0,0.15)", borderwidth=1,
                       bgcolor="rgba(255,255,255,0.9)", font=dict(size=12))
    fig.add_annotation(x=x_left,  y=y_high, text="Low & Unstable",  **label_style)
    fig.add_annotation(x=x_right, y=y_high, text="High & Unstable", **label_style)
    fig.add_annotation(x=x_left,  y=y_low,  text="Low & Stable",    **label_style)
    fig.add_annotation(x=x_right, y=y_low,  text="High & Stable",   **label_style)

    fig.update_layout(
        #title=dict(text=f"{title} (n={n_emp})", x=0.02, xanchor="left"),
        height=520,
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=60, r=40, t=70, b=60),
    )
    fig.update_xaxes(
        title="Avg Relative Efficiency (within company)",
        range=[x_min, x_max],
        showline=True, linecolor="rgba(0,0,0,0.55)", linewidth=1,
        ticks="outside",
        gridcolor="rgba(0,0,0,0.07)",
        zeroline=False,
    )
    fig.update_yaxes(
        title="De-trended CV (within company)",
        range=[y_min, y_max],
        showline=True, linecolor="rgba(0,0,0,0.55)", linewidth=1,
        ticks="outside",
        gridcolor="rgba(0,0,0,0.07)",
        zeroline=False,
    )
    return fig

# ======================
# Load & process (raw)
# ======================
try:
    raw_default = load_raw(DEFAULT_FILE_PATH)
    df0 = preprocess(raw_default)
except Exception as e:
    st.error(f"Failed to load default file: {e}")
    st.stop()

min_d, max_d = df0["op_date"].min(), df0["op_date"].max()

# ======================
# Sidebar (精简版：只保留 3 个控件)
# ======================
# ======================
# Sidebar: 先上传文件
# ======================
st.sidebar.header("Controls")
uploaded = st.sidebar.file_uploader("Upload Excel", type=["xlsx"], key="uploader")

# ======================
# 先确定数据源，再 preprocess 得到全量 df_all（未过滤）
# ======================
try:
    dataset_id = get_dataset_id(uploaded, DEFAULT_FILE_PATH)
    raw = read_current_raw(uploaded, DEFAULT_FILE_PATH)
    df_all = preprocess(raw)
except Exception as e:
    st.error(f"Failed to load/parse file: {e}")
    st.stop()

min_d = df_all["op_date"].min()
max_d = df_all["op_date"].max()

# ======================
# 数据集变化时：重置控件状态（关键）
# ======================
if "dataset_id" not in st.session_state:
    st.session_state["dataset_id"] = dataset_id

if dataset_id != st.session_state["dataset_id"]:
    st.session_state["date_range"] = (min_d, max_d)
    st.session_state["shift"] = SHIFT_OPTIONS[0]
    st.session_state["dataset_id"] = dataset_id
    st.rerun()

# ======================
# Sidebar: Date range / Shift（用当前数据源的 min/max）
# ======================
# 确保 session_state 里先有一个初始值（只在第一次）
if "date_range" not in st.session_state:
    st.session_state["date_range"] = (min_d, max_d)

date_range = st.sidebar.date_input(
    "Date range",
    min_value=min_d,
    max_value=max_d,
    key="date_range"
)


if "shift" not in st.session_state:
    st.session_state["shift"] = SHIFT_OPTIONS[0]

shift = st.sidebar.radio(
    "Shift",
    options=SHIFT_OPTIONS,
    key="shift"
)


# ======================
# 应用筛选
# ======================
if isinstance(date_range, tuple) and len(date_range) == 2:
    d0, d1 = date_range
else:
    d0, d1 = min_d, max_d

df = filter_by_shift(df_all, d0, d1, shift)


# ======================
# Build pivot + KPI + header context
# ======================
pivot, time_bins = build_pivot(df)

time_context = compute_time_context(df)
total_all, sorter_all, share, peak_tb, peak_val = kpi_summary(pivot, time_bins, DEFAULT_SORTER_NAME)

df_jou = build_employee_efficiency_df(pivot, include_pattern=r"^JOU")
df_rd  = build_employee_efficiency_df(pivot, include_pattern=r"^RD")
df_pr  = build_employee_efficiency_df(pivot, include_pattern=r"^pr")

df_jou_rel, df_jou_sum = build_company_relative_efficiency_dfs(pivot, r"^JOU")
df_rd_rel,  df_rd_sum  = build_company_relative_efficiency_dfs(pivot, r"^RD")
df_pr_rel,  df_pr_sum  = build_company_relative_efficiency_dfs(pivot, r"^pr")

# ======================
# Header
# ======================
left, right = st.columns([0.72, 0.28], vertical_alignment="bottom")
with left:
    st.title("📦 Operational Excellence Analytics")
    st.markdown(
        f'<div class="small-note">{time_context} · Shift: <b>{shift}</b> · Records: {len(df):,} · Operators: {df["Operator"].nunique():,}</div>',
        unsafe_allow_html=True
    )
with right:
    st.markdown(
        f'<div class="small-note" style="text-align:right;">Sorting center: <b>{SORTING_CENTER}</b></div>',
        unsafe_allow_html=True
    )


st.markdown('<hr class="soft"/>', unsafe_allow_html=True)

# KPI row
k1, k2, k3, k4 = st.columns(4)
k1.metric("Total Volume", f"{total_all:,}")
k2.metric("Sorter Volume", f"{sorter_all:,}")
k3.metric("Sorter Share", f"{share:.1f}%")
k4.metric("Peak Time Bin", f"{peak_tb}", f"{peak_val:,}")

st.write("")

# ======================
# Figures
# ======================
fig1 = fig_sorter_vs_total(pivot, time_bins, DEFAULT_SORTER_NAME)
fig2 = fig_labor_group_lines(pivot, time_bins)

# ======================
# Two cards side-by-side
# ======================
col1, col2 = st.columns(2, gap="large")

with col1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Sorter vs Total Volume")
    st.caption("Stacked hourly volume; top label = Total, inner label = Sorter share")
    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
    st.plotly_chart(fig1, use_container_width=True, config={"displayModeBar": False, "responsive": True})
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Total Sorting Volume by Labor Group")
    st.caption("Hourly throughput split by labor provider; each node shows volume")
    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
    st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False, "responsive": True})
    st.markdown('</div>', unsafe_allow_html=True)

st.write("")
st.markdown(
    """
    <div style="
        font-size: 28px;
        font-weight: 400;
        margin-bottom: 6px;
    ">
        🔍 Labor Group Deep Dive
    </div>
    """,
    unsafe_allow_html=True
)


################### 图下总结 ########################

def calc_team_avg_hourly_scan(df_emp: pd.DataFrame) -> float:
    """
    团队“平均每小时 Scan Count”：所有员工 × 所有 time-bin 的均值（= 一条横线的 y）
    """
    if df_emp is None or df_emp.empty:
        return 0.0
    return float(np.nanmean(df_emp.to_numpy()))

def pick_bottom_3_efficiency(df_sum: pd.DataFrame) -> list[str]:
    """
    从象限图来源 df_sum 中选效率最低 3 名员工：
    以 Avg_Relative_Efficiency 越小越低
    """
    if df_sum is None or df_sum.empty or "Avg_Relative_Efficiency" not in df_sum.columns:
        return []

    s = df_sum["Avg_Relative_Efficiency"].replace([np.inf, -np.inf], np.nan).dropna()
    if s.empty:
        return []

    return [str(x) for x in s.nsmallest(3).index.tolist()]



# ---- 2) 一个小 helper：每个劳务组渲染一行（两图并排）
def render_group_row(group_code: str, df_emp: pd.DataFrame, df_sum: pd.DataFrame):
    c1, c2 = st.columns(2, gap="large")

    with c1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader(f"{group_code} Employee Efficiency Curves")
        st.caption("Lines per employee; all employees included.")

        fig_emp = make_employee_curve_fig(df_emp, f"{group_code} Employees Efficiency Curve")
        st.plotly_chart(fig_emp, use_container_width=True, config={"displayModeBar": False, "responsive": True})
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader(f"{group_code} Relative Efficiency Quadrant")
        st.caption("Avg relative efficiency vs de-trended CV (within the same company).")

        fig_q = make_quadrant_fig(df_sum, f"{group_code} – Avg Relative Efficiency vs De-trended CV", y_ref="median")
        st.plotly_chart(fig_q, use_container_width=True, config={"displayModeBar": False, "responsive": True})
        st.markdown('</div>', unsafe_allow_html=True)

    # ✅ 图下总结（新增）
    team_avg = calc_team_avg_hourly_scan(df_emp)
    bottom3 = pick_bottom_3_efficiency(df_sum)

    # bottom3 不足 3 人时的兜底显示
    if len(bottom3) >= 3:
        low1, low2, low3 = bottom3[:3]
        low_txt = f"{low1}，{low2}，{low3}"
    elif len(bottom3) > 0:
        low_txt = "，".join(bottom3)
    else:
        low_txt = "（暂无）"

    st.markdown(
    f"""
    <div style="
        margin-top: 8px;
        font-size: 15px;
        line-height: 1.7;
        color: #374151;
    ">
    🚀 在 <b>{time_context}</b> 内，<b>{group_code}</b> 劳务团队员工的平均每小时
    Scan Count 为 <b>{team_avg:.1f}</b>。
    效率最低的三名员工分别是 <b>{low_txt}</b>，需要重点关注。
    </div>
    """,
    unsafe_allow_html=True
)

    st.write("")


# ---- 3) 依次渲染三行（每行一个劳务组）
render_group_row("JOU", df_jou, df_jou_sum)
render_group_row("RD",  df_rd,  df_rd_sum)
#render_group_row("pr",  df_pr,  df_pr_sum)

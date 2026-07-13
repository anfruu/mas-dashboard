import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(page_title="MAS Dashboard", layout="wide")

BASE_DIR = Path(__file__).parent
CALL_FILE = BASE_DIR / "MAS_Call_Grading_Raw_Data.xlsx"
BENCH_FILE = BASE_DIR / "MAS_Benchmarks.xlsx"

# =========================================
# STYLING
# =========================================
TEXT_COLOR = "#102033"
SUBTEXT_COLOR = "#556476"
BORDER = "#D9E2EC"
CARD_BG = "#F7FAFC"
PAGE_BG = "#F4F8FB"
SECTION_BG = "#FFFFFF"

PRIMARY = "#2F5D8C"
SECONDARY = "#4F8A8B"
ACCENT = "#7A6FA6"
WARM = "#C28B52"
SOFT_RED = "#B86A6A"
SLATE = "#60758A"

TEAM_COLORS = {
    "Katie": PRIMARY,
    "Charles": SECONDARY,
    "MAS": ACCENT
}

st.markdown(f"""
<style>
    .stApp {{
        background: linear-gradient(180deg, {PAGE_BG} 0%, #EEF3F7 100%);
    }}

    .block-container {{
        padding-top: 1rem;
        padding-bottom: 2rem;
        max-width: 1520px;
    }}

    html, body, [class*="css"] {{
        color: {TEXT_COLOR} !important;
        font-family: "Segoe UI", "Inter", sans-serif;
    }}

    h1 {{
        color: {TEXT_COLOR} !important;
        font-weight: 800 !important;
        letter-spacing: -0.03em;
        margin-bottom: 0.12rem !important;
    }}

    h2, h3, h4, h5, h6 {{
        color: {TEXT_COLOR} !important;
        font-weight: 700 !important;
        letter-spacing: -0.02em;
    }}

    p, label, .stCaption {{
        color: {SUBTEXT_COLOR} !important;
    }}

    div[data-testid="stMetric"] {{
        background: linear-gradient(180deg, #FFFFFF 0%, {CARD_BG} 100%);
        border: 1px solid {BORDER};
        border-radius: 16px;
        padding: 16px 18px;
        box-shadow: 0 3px 10px rgba(16, 32, 51, 0.04);
    }}

    div[data-testid="stMetricLabel"] {{
        color: {SUBTEXT_COLOR} !important;
        font-weight: 700 !important;
        font-size: 0.92rem !important;
    }}

    div[data-testid="stMetricValue"] {{
        color: {TEXT_COLOR} !important;
        font-weight: 800 !important;
        font-size: 1.65rem !important;
    }}

    .stSelectbox label {{
        color: {TEXT_COLOR} !important;
        font-weight: 700 !important;
    }}

    div[data-testid="stDataFrame"] {{
        border: 1px solid {BORDER};
        border-radius: 16px;
        overflow: hidden;
        box-shadow: 0 2px 8px rgba(16, 32, 51, 0.03);
    }}

    .section-shell {{
        background: {SECTION_BG};
        border: 1px solid {BORDER};
        border-radius: 18px;
        padding: 16px 18px;
        margin-top: 0.45rem;
        margin-bottom: 1rem;
        box-shadow: 0 3px 12px rgba(16, 32, 51, 0.04);
    }}

    .section-title {{
        color: {TEXT_COLOR};
        font-weight: 800;
        font-size: 1.05rem;
        margin-bottom: 0.18rem;
    }}

    .section-subtitle {{
        color: {SUBTEXT_COLOR};
        font-size: 0.92rem;
        margin-bottom: 0;
    }}

    .note-box {{
        background: #F8FBFE;
        border: 1px solid {BORDER};
        border-radius: 14px;
        padding: 12px 14px;
        margin-top: 0.25rem;
        margin-bottom: 1rem;
        color: {SUBTEXT_COLOR};
        font-size: 0.92rem;
    }}
</style>
""", unsafe_allow_html=True)

# =========================================
# HELPERS
# =========================================
def section_header(title: str, subtitle: str = ""):
    st.markdown(
        f"""
        <div class="section-shell">
            <div class="section-title">{title}</div>
            <div class="section-subtitle">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

def note_box(text: str):
    st.markdown(f'<div class="note-box">{text}</div>', unsafe_allow_html=True)

def clean_cols(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [str(c).strip().replace("\n", " ").replace("\r", "").replace("\xa0", " ") for c in df.columns]
    return df

def pick_col(df: pd.DataFrame, options: list[str], required: bool = True):
    lookup = {str(c).strip().lower(): c for c in df.columns}
    for opt in options:
        if opt.lower() in lookup:
            return lookup[opt.lower()]
    if required:
        raise KeyError(f"Missing one of columns: {options}. Found columns: {list(df.columns)}")
    return None

def normalize_yes_no(series: pd.Series) -> pd.Series:
    s = series.astype(str).str.strip().str.lower()
    mapping = {
        "yes": "Yes", "y": "Yes", "true": "Yes", "1": "Yes",
        "no": "No", "n": "No", "false": "No", "0": "No",
    }
    return s.map(mapping).fillna(series.astype(str).str.strip())

def normalize_percentage(series: pd.Series) -> pd.Series:
    s = pd.to_numeric(series, errors="coerce")
    if not s.dropna().empty and s.dropna().le(1).all():
        s = s * 100
    return s

def pct_text(num: int, den: int) -> str:
    if den == 0:
        return "0.0%"
    return f"{(num / den) * 100:.1f}%"

def avg_safe(series: pd.Series, decimals: int = 1) -> float:
    s = pd.to_numeric(series, errors="coerce")
    if s.dropna().empty:
        return 0.0
    return round(float(s.mean()), decimals)

def apply_layout(fig, height=360, show_legend=True):
    fig.update_layout(
        height=height,
        margin=dict(l=18, r=18, t=52, b=18),
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(color=TEXT_COLOR, size=13),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(color=TEXT_COLOR, size=12),
            title=None
        ),
        showlegend=show_legend
    )
    fig.update_xaxes(
        title_font=dict(color=TEXT_COLOR, size=13),
        tickfont=dict(color=TEXT_COLOR),
        gridcolor="#E6EDF3",
        zeroline=False
    )
    fig.update_yaxes(
        title_font=dict(color=TEXT_COLOR, size=13),
        tickfont=dict(color=TEXT_COLOR),
        gridcolor="#E6EDF3",
        zeroline=False
    )
    return fig

def month_label(dt_series: pd.Series) -> pd.Series:
    return dt_series.dt.strftime("%b %Y")

# --- CHANGED ---
# Was: dt_series.dt.to_period("Q").astype(str)  -> produced "2026Q2" / "2026Q3",
# which did not match the hardcoded "Q1" label coming from the benchmark file.
# Now emits clean "Q1" / "Q2" / "Q3" / "Q4" labels that line up with Q1.
def quarter_label(dt_series: pd.Series) -> pd.Series:
    q = dt_series.dt.quarter
    return q.apply(lambda x: f"Q{int(x)}" if pd.notna(x) else pd.NA)

# Sort key stays year-aware so quarters order correctly across years.
def quarter_sort(dt_series: pd.Series) -> pd.Series:
    return dt_series.dt.to_period("Q").astype(str)

MONTH_NUM = {
    "January": 1, "February": 2, "March": 3,
    "April": 4, "May": 5, "June": 6,
    "July": 7, "August": 8, "September": 9,
    "October": 10, "November": 11, "December": 12
}

MONTH_FIXES = {
    "janruary": "January",
    "janaury": "January",
    "january": "January",
    "janurary": "January",
    "januarry": "January",
    "febuary": "February",
    "februrary": "February",
    "marhc": "March",
    "aplir": "April",
    "agust": "August",
    "ocotber": "October",
    "novemeber": "November",
    "decemeber": "December",
}

def normalize_month_name(value: str) -> str:
    s = str(value).strip()
    if not s:
        return s
    s_lower = s.lower()
    if s_lower in MONTH_FIXES:
        return MONTH_FIXES[s_lower]
    s_title = s.title()
    if s_title in MONTH_NUM:
        return s_title
    return s_title

def view_avg(df: pd.DataFrame, score_col: str, individual_view: bool) -> float:
    if df.empty:
        return 0.0
    if individual_view:
        return avg_safe(df[score_col])
    employee_avg = (
        df.groupby("AssociateName", as_index=False)[score_col]
        .mean()[score_col]
    )
    return round(float(employee_avg.mean()), 1) if not employee_avg.empty else 0.0

# =========================================
# LOAD CURRENT CALL DATA
# =========================================
@st.cache_data
def load_call_data() -> pd.DataFrame:
    df = pd.read_excel(CALL_FILE, sheet_name="Raw_Data")
    df = clean_cols(df)
    df = df.dropna(how="all")

    assoc = pick_col(df, ["AssociateName", "Associate Name"])
    team = pick_col(df, ["ManagerTeam", "Manager Team"])
    date = pick_col(df, ["DateOfCall", "Date Of Call"])
    fcr = pick_col(df, ["IssueResolvedFirstContact", "Issue Resolved First Contact"])
    failed = pick_col(df, ["CallFailed", "Call Failed"])
    total = pick_col(df, ["TotalScore", "Total Score"])
    pct = pick_col(df, ["Percentage"], required=False)

    out = pd.DataFrame({
        "AssociateName": df[assoc].astype(str).str.strip(),
        "ManagerTeam": df[team].astype(str).str.strip(),
        "DateOfCall": pd.to_datetime(df[date], errors="coerce"),
        "IssueResolvedFirstContact": normalize_yes_no(df[fcr]),
        "CallFailed": normalize_yes_no(df[failed]),
        "TotalScore": pd.to_numeric(df[total], errors="coerce"),
    })

    if pct:
        out["Percentage"] = normalize_percentage(df[pct])
    else:
        out["Percentage"] = out["TotalScore"]

    out = out.dropna(subset=["AssociateName", "ManagerTeam", "DateOfCall"], how="all")
    out["MonthLabel"] = month_label(out["DateOfCall"])
    out["QuarterLabel"] = quarter_label(out["DateOfCall"])      # <-- now "Q2" / "Q3"
    out["MonthSort"] = out["DateOfCall"].dt.to_period("M").astype(str)
    out["QuarterSort"] = quarter_sort(out["DateOfCall"])        # <-- "2026Q2" (sort only)
    out["MonthNum"] = out["DateOfCall"].dt.month
    return out

# =========================================
# LOAD Q1 CALL-LEVEL DATA
# =========================================
@st.cache_data
def load_q1_data() -> pd.DataFrame:
    df = pd.read_excel(BENCH_FILE, sheet_name="Benchmark_Data")
    df = clean_cols(df)
    df = df.dropna(how="all")

    assoc = pick_col(df, ["AssociateName", "Associate Name"])
    team = pick_col(df, ["ManagerTeam", "Manager Team"])
    month = pick_col(df, ["BenchmarkMonth", "Benchmark Month"])
    quarter = pick_col(df, ["BenchmarkQuarter", "Benchmark Quarter"])
    score = pick_col(df, ["Score"])

    out = pd.DataFrame({
        "AssociateName": df[assoc].astype(str).str.strip(),
        "ManagerTeam": df[team].astype(str).str.strip(),
        "Q1Month": df[month].astype(str).apply(normalize_month_name),
        "Q1Quarter": df[quarter].astype(str).str.strip(),
        "Score": pd.to_numeric(df[score], errors="coerce"),
    })

    out = out.dropna(subset=["AssociateName", "ManagerTeam", "Q1Month", "Score"], how="any")

    out["Q1Quarter"] = out["Q1Quarter"].replace({
        "1": "Q1", "2": "Q2", "3": "Q3", "4": "Q4",
        1: "Q1", 2: "Q2", 3: "Q3", 4: "Q4"
    })

    out["Q1MonthNum"] = out["Q1Month"].map(MONTH_NUM)
    out = out.dropna(subset=["Q1MonthNum"]).copy()
    out["Q1MonthNum"] = out["Q1MonthNum"].astype(int)
    return out

# =========================================
# DATA INIT
# =========================================
st.title("MAS Dashboard")
st.caption("Managed Accounts Service metrics, Q1 comparison, and live grading insights")

try:
    call_df = load_call_data()
except Exception as e:
    st.error(f"Could not load current call grading data: {e}")
    call_df = pd.DataFrame()

try:
    q1_df = load_q1_data()
except Exception as e:
    st.error(f"Could not load Q1 data: {e}")
    q1_df = pd.DataFrame()

# =========================================
# TOP DISCLAIMER
# =========================================
note_box(
    "Q1 metrics are considered the benchmark and are based on January through March scored call records. "
    "Q1 records are score-only and do not include call dates. "
    "Q2 (April 1 through June 30, 2026) is final. Q3 is in progress. "
    "Call Failed Rate and First Call Resolution Rate are calculated using April 1, 2026 forward live grading data only."
)

# =========================================
# FILTERS
# =========================================
section_header(
    "Dashboard Filters",
    "Use team, employee, and current-period filters to compare Q1 performance against April-forward live grading."
)

f1, f2, f3 = st.columns([1, 1, 1])

with f1:
    view_by = st.selectbox(
        "View By",
        ["All Teams", "Katie", "Charles", "Individual Associate"],
        index=0
    )

all_associates = sorted(
    pd.concat([
        call_df["AssociateName"] if not call_df.empty else pd.Series(dtype=str),
        q1_df["AssociateName"] if not q1_df.empty else pd.Series(dtype=str)
    ]).dropna().astype(str).str.strip().unique().tolist()
)

selected_associate = None
with f2:
    if view_by == "Individual Associate":
        selected_associate = st.selectbox("Associate Name", all_associates)

# --- CHANGED ---
# Quarter options are built from whatever quarters actually exist in the call file.
# Q4 will appear on its own in October; Q1 2027 on its own in January. No code edit ever.
# The newest quarter is labeled "Current Quarter"; every closed quarter is labeled "Final".
quarter_options = []
quarter_lookup = {}
if not call_df.empty:
    q_sorted = (
        call_df[["QuarterLabel", "QuarterSort"]]
        .dropna()
        .drop_duplicates()
        .sort_values("QuarterSort")
    )
    q_labels = q_sorted["QuarterLabel"].tolist()
    for i, q in enumerate(q_labels):
        suffix = "Current Quarter" if i == len(q_labels) - 1 else "Final"
        opt = f"{q} ({suffix})"
        quarter_options.append(opt)
        quarter_lookup[opt] = q

# Change index=0 to index=1 if you want the dashboard to open on the first quarter
# in the list (Q2 today) instead of blended "All Current Data".
with f3:
    time_view = st.selectbox(
        "Current Data View",
        ["All Current Data"] + quarter_options + ["Current Month", "Specific Month"],
        index=0
    )

selected_month = None
if not call_df.empty and time_view == "Specific Month":
    month_options = sorted(
        call_df["MonthLabel"].dropna().unique().tolist(),
        key=lambda x: pd.to_datetime(x, format="%b %Y")
    )
    selected_month = st.selectbox("Select Current Month", month_options)

# =========================================
# FILTER DATA
# =========================================
call_filtered = call_df.copy()
q1_filtered = q1_df.copy()

# --- CHANGED --- quarter-aware period filtering, driven by the dynamic lookup above
if not call_filtered.empty:
    if time_view in quarter_lookup:
        call_filtered = call_filtered[call_filtered["QuarterLabel"] == quarter_lookup[time_view]]
    elif time_view == "Current Month":
        latest_month = sorted(call_filtered["MonthSort"].dropna().unique().tolist())[-1]
        call_filtered = call_filtered[call_filtered["MonthSort"] == latest_month]
    elif time_view == "Specific Month" and selected_month:
        call_filtered = call_filtered[call_filtered["MonthLabel"] == selected_month]

if view_by in ["Katie", "Charles"]:
    call_filtered = call_filtered[call_filtered["ManagerTeam"] == view_by]
    q1_filtered = q1_filtered[q1_filtered["ManagerTeam"] == view_by]
elif view_by == "Individual Associate" and selected_associate:
    call_filtered = call_filtered[call_filtered["AssociateName"] == selected_associate]
    q1_filtered = q1_filtered[q1_filtered["AssociateName"] == selected_associate]

call_selected_full = call_df.copy()
q1_selected_full = q1_df.copy()

if view_by in ["Katie", "Charles"]:
    call_selected_full = call_selected_full[call_selected_full["ManagerTeam"] == view_by]
    q1_selected_full = q1_selected_full[q1_selected_full["ManagerTeam"] == view_by]
elif view_by == "Individual Associate" and selected_associate:
    call_selected_full = call_selected_full[call_selected_full["AssociateName"] == selected_associate]
    q1_selected_full = q1_selected_full[q1_selected_full["AssociateName"] == selected_associate]

individual_view = view_by == "Individual Associate"

# =========================================
# OVERVIEW
# =========================================
section_header(
    "Performance Overview",
    "Q1 and current performance metrics for the selected view."
)

q1_calls = len(q1_filtered)
q1_total_score = pd.to_numeric(q1_filtered["Score"], errors="coerce").sum()
q1_avg = view_avg(q1_filtered, "Score", individual_view)

current_calls = len(call_filtered)
current_total_score = pd.to_numeric(call_filtered["TotalScore"], errors="coerce").sum()
current_avg = view_avg(call_filtered, "TotalScore", individual_view)

failed_rate = pct_text((call_filtered["CallFailed"] == "Yes").sum(), current_calls)
fcr_rate = pct_text((call_filtered["IssueResolvedFirstContact"] == "Yes").sum(), current_calls)

ytd_calls = q1_calls + current_calls

if individual_view:
    ytd_avg = round(((q1_total_score + current_total_score) / ytd_calls), 1) if ytd_calls > 0 else 0.0
else:
    q1_emp = (
        q1_filtered.groupby("AssociateName", as_index=False)
        .agg(Q1Score=("Score", "sum"), Q1Calls=("Score", "size"))
    ) if not q1_filtered.empty else pd.DataFrame(columns=["AssociateName", "Q1Score", "Q1Calls"])

    current_emp = (
        call_filtered.groupby("AssociateName", as_index=False)
        .agg(CurrentScore=("TotalScore", "sum"), CurrentCalls=("TotalScore", "size"))
    ) if not call_filtered.empty else pd.DataFrame(columns=["AssociateName", "CurrentScore", "CurrentCalls"])

    ytd_emp = q1_emp.merge(current_emp, on="AssociateName", how="outer").fillna(0)
    if not ytd_emp.empty:
        ytd_emp["YTDCalls"] = ytd_emp["Q1Calls"] + ytd_emp["CurrentCalls"]
        ytd_emp["YTDScore"] = ytd_emp["Q1Score"] + ytd_emp["CurrentScore"]
        ytd_emp["YTDAvg"] = ytd_emp.apply(
            lambda r: (r["YTDScore"] / r["YTDCalls"]) if r["YTDCalls"] > 0 else pd.NA,
            axis=1
        )
        ytd_avg = round(pd.to_numeric(ytd_emp["YTDAvg"], errors="coerce").dropna().mean(), 1) if not ytd_emp["YTDAvg"].dropna().empty else 0.0
    else:
        ytd_avg = 0.0

delta_vs_q1 = round(current_avg - q1_avg, 1) if q1_calls > 0 and current_calls > 0 else 0.0

m1, m2, m3, m4, m5, m6 = st.columns(6)
m1.metric("Q1 Calls", q1_calls)
m2.metric("Q1 Avg", q1_avg)
m3.metric("Current Calls", current_calls)
m4.metric("Current Avg", current_avg)
m5.metric("Call Failed Rate", failed_rate)
m6.metric("First Call Resolution Rate", fcr_rate)

st.markdown("<br>", unsafe_allow_html=True)

d1, d2, d3 = st.columns(3)
d1.metric("YTD Calls", ytd_calls)
d2.metric("YTD Avg", ytd_avg)
d3.metric("Current vs Q1", f"{delta_vs_q1:+.1f}")

# =========================================
# MONTH-TO-MONTH COMPARISON
# =========================================
section_header(
    "Month-to-Month Comparison",
    "Q1 months are compared to April-forward live grading months for the selected view."
)

q1_monthly = pd.DataFrame()
if not q1_selected_full.empty:
    q1_month_emp = (
        q1_selected_full.groupby(["Q1Month", "Q1MonthNum", "AssociateName"], as_index=False)
        .agg(EmployeeAvg=("Score", "mean"))
    )
    q1_month_calls = (
        q1_selected_full.groupby(["Q1Month", "Q1MonthNum"], as_index=False)
        .agg(CallCount=("Score", "size"))
    )
    q1_month_avg = (
        q1_month_emp.groupby(["Q1Month", "Q1MonthNum"], as_index=False)
        .agg(AvgScore=("EmployeeAvg", "mean"))
    )
    q1_monthly = q1_month_avg.merge(q1_month_calls, on=["Q1Month", "Q1MonthNum"], how="left")
    q1_monthly["PeriodLabel"] = q1_monthly["Q1Month"]
    q1_monthly["PeriodSort"] = q1_monthly["Q1MonthNum"]
    q1_monthly["Source"] = "Q1"

current_monthly = pd.DataFrame()
if not call_selected_full.empty:
    current_month_emp = (
        call_selected_full.groupby(["MonthLabel", "MonthSort", "MonthNum", "AssociateName"], as_index=False)
        .agg(EmployeeAvg=("TotalScore", "mean"))
    )
    current_month_calls = (
        call_selected_full.groupby(["MonthLabel", "MonthSort", "MonthNum"], as_index=False)
        .agg(CallCount=("TotalScore", "size"))
    )
    current_month_avg = (
        current_month_emp.groupby(["MonthLabel", "MonthSort", "MonthNum"], as_index=False)
        .agg(AvgScore=("EmployeeAvg", "mean"))
    )
    current_monthly = current_month_avg.merge(
        current_month_calls, on=["MonthLabel", "MonthSort", "MonthNum"], how="left"
    )
    current_monthly["PeriodLabel"] = current_monthly["MonthLabel"]
    current_monthly["PeriodSort"] = current_monthly["MonthNum"]
    current_monthly["Source"] = "Current"

monthly_compare = pd.concat(
    [
        q1_monthly[["PeriodLabel", "PeriodSort", "AvgScore", "CallCount", "Source"]] if not q1_monthly.empty else pd.DataFrame(),
        current_monthly[["PeriodLabel", "PeriodSort", "AvgScore", "CallCount", "Source"]] if not current_monthly.empty else pd.DataFrame()
    ],
    ignore_index=True
)

if not monthly_compare.empty:
    monthly_compare = monthly_compare.sort_values("PeriodSort").reset_index(drop=True)
    monthly_compare["BarLabel"] = monthly_compare.apply(
        lambda r: f"{r['AvgScore']:.1f}<br>{int(r['CallCount'])} calls",
        axis=1
    )

    fig_month = px.bar(
        monthly_compare,
        x="PeriodLabel",
        y="AvgScore",
        color="Source",
        text="BarLabel",
        barmode="group",
        title="Average Score by Month"
    )
    fig_month.update_traces(textposition="outside")
    fig_month = apply_layout(fig_month, height=360, show_legend=True)
    fig_month.update_xaxes(title="")
    fig_month.update_yaxes(title="Avg Score")
    st.plotly_chart(fig_month, use_container_width=True)
else:
    st.info("No monthly comparison data available for the selected view.")

# =========================================
# QUARTER COMPARISON
# =========================================
section_header(
    "Quarter Comparison",
    "Q1 benchmark against finalized Q2 and the in-progress current quarter. Bar labels show quarter-over-quarter movement."
)

quarter_compare_rows = []

if not q1_selected_full.empty:
    if individual_view:
        q1_quarter_avg = avg_safe(q1_selected_full["Score"])
    else:
        q1_quarter_emp = (
            q1_selected_full.groupby("AssociateName", as_index=False)
            .agg(EmployeeAvg=("Score", "mean"))
        )
        q1_quarter_avg = round(q1_quarter_emp["EmployeeAvg"].mean(), 1) if not q1_quarter_emp.empty else 0.0

    quarter_compare_rows.append({
        "Quarter": "Q1",
        "QuarterSort": "2026Q1",
        "AvgScore": float(q1_quarter_avg),
        "CallCount": int(len(q1_selected_full))
    })

if not call_selected_full.empty:
    current_quarter_emp = (
        call_selected_full.groupby(["QuarterLabel", "QuarterSort", "AssociateName"], as_index=False)
        .agg(EmployeeAvg=("TotalScore", "mean"))
    )
    current_quarter_calls = (
        call_selected_full.groupby(["QuarterLabel", "QuarterSort"], as_index=False)
        .agg(CallCount=("TotalScore", "size"))
    )
    current_quarter_avg = (
        current_quarter_emp.groupby(["QuarterLabel", "QuarterSort"], as_index=False)
        .agg(AvgScore=("EmployeeAvg", "mean"))
    ).merge(current_quarter_calls, on=["QuarterLabel", "QuarterSort"], how="left").sort_values("QuarterSort")

    for _, row in current_quarter_avg.iterrows():
        quarter_compare_rows.append({
            "Quarter": row["QuarterLabel"],
            "QuarterSort": row["QuarterSort"],
            "AvgScore": float(row["AvgScore"]),
            "CallCount": int(row["CallCount"])
        })

quarter_compare_df = pd.DataFrame(quarter_compare_rows)

if not quarter_compare_df.empty:
    quarter_compare_df = quarter_compare_df.sort_values("QuarterSort").reset_index(drop=True)

    # --- NEW --- quarter-over-quarter delta
    quarter_compare_df["QoQ"] = quarter_compare_df["AvgScore"].diff().round(1)

    # Latest quarter is still open; flag it so nobody reads a partial quarter as final.
    latest_quarter = quarter_compare_df["Quarter"].iloc[-1]
    quarter_compare_df["Status"] = quarter_compare_df["Quarter"].apply(
        lambda q: "In Progress" if q == latest_quarter else "Final"
    )

    def _bar_label(r):
        base = f"{r['AvgScore']:.1f}<br>{int(r['CallCount'])} calls"
        if pd.notna(r["QoQ"]):
            base += f"<br>{r['QoQ']:+.1f} QoQ"
        return base

    quarter_compare_df["BarLabel"] = quarter_compare_df.apply(_bar_label, axis=1)

    fig_quarter = px.bar(
        quarter_compare_df,
        x="Quarter",
        y="AvgScore",
        text="BarLabel",
        color="Status",
        color_discrete_map={"Final": PRIMARY, "In Progress": SLATE},
        title="Average Score by Quarter"
    )
    fig_quarter.update_traces(textposition="outside")
    fig_quarter = apply_layout(fig_quarter, height=330, show_legend=True)
    fig_quarter.update_xaxes(title="", categoryorder="array", categoryarray=quarter_compare_df["Quarter"].tolist())
    fig_quarter.update_yaxes(title="Avg Score")
    st.plotly_chart(fig_quarter, use_container_width=True)
else:
    st.info("No quarter comparison data available for the selected view.")

# =========================================
# RANKING
# =========================================
section_header(
    "YTD Ranking",
    "Ranks each employee by individual YTD average."
)

q1_rank = (
    q1_selected_full.groupby(["ManagerTeam", "AssociateName"], as_index=False)
    .agg(Q1Score=("Score", "sum"), Q1Calls=("Score", "size"))
) if not q1_selected_full.empty else pd.DataFrame(columns=["ManagerTeam", "AssociateName", "Q1Score", "Q1Calls"])

current_rank = (
    call_selected_full.groupby(["ManagerTeam", "AssociateName"], as_index=False)
    .agg(CurrentScore=("TotalScore", "sum"), CurrentCalls=("TotalScore", "size"))
) if not call_selected_full.empty else pd.DataFrame(columns=["ManagerTeam", "AssociateName", "CurrentScore", "CurrentCalls"])

ranking_df = q1_rank.merge(current_rank, on=["ManagerTeam", "AssociateName"], how="outer").fillna(0)

if not ranking_df.empty:
    ranking_df["YTDCalls"] = ranking_df["Q1Calls"] + ranking_df["CurrentCalls"]
    ranking_df["YTDScore"] = ranking_df["Q1Score"] + ranking_df["CurrentScore"]
    ranking_df["YTDAvg"] = ranking_df.apply(
        lambda r: (r["YTDScore"] / r["YTDCalls"]) if r["YTDCalls"] > 0 else pd.NA,
        axis=1
    )
    ranking_df["YTDRank"] = ranking_df["YTDAvg"].rank(method="dense", ascending=False).astype("Int64")
    display_rank = ranking_df.sort_values(["YTDRank", "AssociateName"]).copy()

    if view_by == "All Teams":
        st.dataframe(
            display_rank[["ManagerTeam", "AssociateName", "YTDRank"]].rename(columns={"YTDRank": "YTD Rank"}),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.dataframe(
            display_rank[["AssociateName", "YTDRank"]].rename(columns={"YTDRank": "YTD Rank"}),
            use_container_width=True,
            hide_index=True
        )
else:
    st.info("No YTD ranking available for the selected view.")

# =========================================
# LIVE CURRENT DETAIL
# =========================================
if view_by != "All Teams":
    section_header(
        "Current Graded Call Detail",
        "April 1, 2026 forward on any graded call."
    )

    if call_filtered.empty:
        st.info("No current graded call detail available for the selected filters.")
    else:
        current_detail = call_filtered[[
            "AssociateName",
            "ManagerTeam",
            "DateOfCall",
            "TotalScore",
            "Percentage",
            "CallFailed",
            "IssueResolvedFirstContact"
        ]].copy()

        current_detail = current_detail.sort_values("DateOfCall", ascending=False)
        current_detail["DateOfCall"] = pd.to_datetime(current_detail["DateOfCall"], errors="coerce").dt.strftime("%m/%d/%Y")
        current_detail["Percentage"] = current_detail["Percentage"].round(1)

        st.dataframe(
            current_detail,
            use_container_width=True,
            hide_index=True
        )

# =========================================
# Q1 CALL SCORES
# =========================================
section_header(
    "Q1 Call Scores",
    "January through March call scores are listed by month because historical Q1 records do not include call dates."
)

if q1_filtered.empty:
    st.info("No Q1 call scores available for the selected filters.")
else:
    q1_detail = q1_filtered[[
        "AssociateName",
        "ManagerTeam",
        "Q1Month",
        "Q1Quarter",
        "Q1MonthNum",
        "Score"
    ]].copy()

    q1_detail = q1_detail.sort_values(
        ["Q1Quarter", "Q1MonthNum", "AssociateName"]
    )

    st.dataframe(
        q1_detail[[
            "AssociateName",
            "ManagerTeam",
            "Q1Month",
            "Q1Quarter",
            "Score"
        ]].rename(columns={
            "Q1Month": "Month",
            "Q1Quarter": "Quarter"
        }),
        use_container_width=True,
        hide_index=True
    )

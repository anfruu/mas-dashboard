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
    df.columns = [str(c).strip().replace("\\n", " ").replace("\\r", "").replace("\\xa0", " ") for c in df.columns]
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

def quarter_label(dt_series: pd.Series) -> pd.Series:
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
    "september": "September",
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
    out["QuarterLabel"] = quarter_label(out["DateOfCall"])
    out["MonthSort"] = out["DateOfCall"].dt.to_period("M").astype(str)
    out["QuarterSort"] = out["DateOfCall"].dt.to_period("Q").astype(str)
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

with f3:
    time_view = st.selectbox(
        "Current Data View",
        ["All Current Data", "Current Month", "Specific Month"],
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

if time_view == "Current Month" and not call_filtered.empty:
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

# =========================================
# OVERVIEW
# =========================================
section_header(
    "Performance Overview",
    "Q1 metrics are considered the benchmark and are based on January through March scored call records. Q1 records are score-only and do not include call dates. Call Failed Rate and First Call Resolution Rate are calculated using April 1, 2026 forward live grading data only."
)

q1_calls = len(q1_filtered)
q1_avg = avg_safe(q1_filtered["Score"])
q1_total_score = pd.to_numeric(q1_filtered["Score"], errors="coerce").sum()

current_calls = len(call_filtered)
current_avg = avg_safe(call_filtered["TotalScore"])
current_total_score = pd.to_numeric(call_filtered["TotalScore"], errors="coerce").sum()

failed_rate = pct_text((call_filtered["CallFailed"] == "Yes").sum(), current_calls)
fcr_rate = pct_text((call_filtered["IssueResolvedFirstContact"] == "Yes").sum(), current_calls)

ytd_calls = q1_calls + current_calls
ytd_avg = round(((q1_total_score + current_total_score) / (ytd_calls * 100)) * 100, 1) if ytd_calls > 0 else 0.0
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
    q1_monthly = (
        q1_selected_full.groupby(["Q1Month", "Q1MonthNum"], as_index=False)
        .agg(
            AvgScore=("Score", "mean"),
            CallCount=("Score", "size")
        )
        .sort_values("Q1MonthNum")
    )
    q1_monthly["PeriodLabel"] = q1_monthly["Q1Month"]
    q1_monthly["PeriodSort"] = q1_monthly["Q1MonthNum"]
    q1_monthly["Source"] = "Q1"

current_monthly = pd.DataFrame()
if not call_selected_full.empty:
    current_monthly = (
        call_selected_full.groupby(["MonthLabel", "MonthSort"], as_index=False)
        .agg(
            AvgScore=("TotalScore", "mean"),
            CallCount=("TotalScore", "size")
        )
        .sort_values("MonthSort")
    )
    current_monthly["PeriodLabel"] = current_monthly["MonthLabel"]
    current_monthly["PeriodSort"] = range(4, 4 + len(current_monthly))
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
    "Compares Q1 average against live current quarter averages."
)

quarter_compare_rows = []

if not q1_selected_full.empty:
    quarter_compare_rows.append({
        "Quarter": "Q1",
        "AvgScore": avg_safe(q1_selected_full["Score"]),
        "CallCount": int(len(q1_selected_full))
    })

if not call_selected_full.empty:
    current_quarter = (
        call_selected_full.groupby(["QuarterLabel", "QuarterSort"], as_index=False)
        .agg(
            AvgScore=("TotalScore", "mean"),
            CallCount=("TotalScore", "size")
        )
        .sort_values("QuarterSort")
    )
    for _, row in current_quarter.iterrows():
        quarter_compare_rows.append({
            "Quarter": row["QuarterLabel"],
            "AvgScore": float(row["AvgScore"]),
            "CallCount": int(row["CallCount"])
        })

quarter_compare_df = pd.DataFrame(quarter_compare_rows)

if not quarter_compare_df.empty:
    quarter_compare_df["BarLabel"] = quarter_compare_df.apply(
        lambda r: f"{r['AvgScore']:.1f}<br>{int(r['CallCount'])} calls",
        axis=1
    )
    fig_quarter = px.bar(
        quarter_compare_df,
        x="Quarter",
        y="AvgScore",
        text="BarLabel",
        title="Average Score by Quarter"
    )
    fig_quarter.update_traces(marker_color=PRIMARY, textposition="outside")
    fig_quarter = apply_layout(fig_quarter, height=330, show_legend=False)
    fig_quarter.update_xaxes(title="")
    fig_quarter.update_yaxes(title="Avg Score")
    st.plotly_chart(fig_quarter, use_container_width=True)
else:
    st.info("No quarter comparison data available for the selected view.")

# =========================================
# RANKING COMPARISON
# =========================================
section_header(
    "Ranking Comparison",
    "Shows Prior Rank from Q1 next to Current Rank."
)

q1_rank = pd.DataFrame()
if not q1_selected_full.empty:
    q1_rank = (
        q1_selected_full.groupby(["ManagerTeam", "AssociateName"], as_index=False)
        .agg(Q1AvgScore=("Score", "mean"))
    )
    q1_rank["Prior Rank"] = (
        q1_rank.groupby("ManagerTeam")["Q1AvgScore"]
        .rank(method="dense", ascending=False)
        .astype(int)
    )
    q1_rank["Prior Rank MAS"] = (
        q1_rank["Q1AvgScore"]
        .rank(method="dense", ascending=False)
        .astype(int)
    )

current_rank = pd.DataFrame()
if not call_selected_full.empty:
    current_rank = (
        call_selected_full.groupby(["ManagerTeam", "AssociateName"], as_index=False)
        .agg(CurrentAvgScore=("TotalScore", "mean"))
    )
    current_rank["Current Rank"] = (
        current_rank.groupby("ManagerTeam")["CurrentAvgScore"]
        .rank(method="dense", ascending=False)
        .astype(int)
    )
    current_rank["Current Rank MAS"] = (
        current_rank["CurrentAvgScore"]
        .rank(method="dense", ascending=False)
        .astype(int)
    )

ranking_df = q1_rank.merge(
    current_rank,
    on=["ManagerTeam", "AssociateName"],
    how="outer"
)

if not ranking_df.empty:
    if view_by == "All Teams":
        display_rank = ranking_df.sort_values(
            ["Prior Rank MAS", "Current Rank MAS", "AssociateName"]
        ).copy()
        st.dataframe(
            display_rank[[
                "ManagerTeam",
                "AssociateName",
                "Prior Rank MAS",
                "Current Rank MAS"
            ]].rename(columns={
                "Prior Rank MAS": "Prior Rank",
                "Current Rank MAS": "Current Rank"
            }),
            use_container_width=True,
            hide_index=True
        )
    elif view_by in ["Katie", "Charles"]:
        display_rank = ranking_df.sort_values(
            ["Prior Rank", "Current Rank", "AssociateName"]
        ).copy()
        st.dataframe(
            display_rank[[
                "AssociateName",
                "Prior Rank",
                "Current Rank"
            ]],
            use_container_width=True,
            hide_index=True
        )
    else:
        display_rank = ranking_df.sort_values(
            ["Prior Rank MAS", "Current Rank MAS", "AssociateName"]
        ).copy()
        st.dataframe(
            display_rank[[
                "ManagerTeam",
                "AssociateName",
                "Prior Rank MAS",
                "Current Rank MAS"
            ]].rename(columns={
                "Prior Rank MAS": "Prior Rank",
                "Current Rank MAS": "Current Rank"
            }),
            use_container_width=True,
            hide_index=True
        )
else:
    st.info("No ranking comparison available for the selected view.")

# =========================================
# LIVE CURRENT DETAIL
# =========================================
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
    current_detail["Percentage"] = current_detail["Percentage"].round(1)
    st.dataframe(
        current_detail.sort_values("DateOfCall", ascending=False),
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

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

st.set_page_config(page_title="MAS Dashboard", layout="wide")

BASE_DIR = Path(__file__).parent
CALL_FILE = BASE_DIR / "MAS_Call_Grading_Raw_Data.xlsx"
BENCH_FILE = BASE_DIR / "MAS_Benchmarks.xlsx"

# Onboarding scores live in their own file and are deliberately kept out of every
# other metric on this dashboard. Nothing here feeds the Summary or Detail tabs.
# Rename the file below if yours is named differently. The first sheet is read
# unless NEW_HIRE_SHEET is set to a specific sheet name.
NEW_HIRE_FILE = BASE_DIR / "NEW_HIRE_MAS_Scores.xlsx"
NEW_HIRE_SHEET = 0

# =========================================
# CONFIG
# =========================================
# The Q1 file carries no call dates. This year is used only to build
# readable month labels ("Jan 2026") for the Q1 months in the period list.
Q1_YEAR = 2026

# =========================================
# LPL PALETTE
# =========================================
LPL_NAVY = "#1F3864"
LPL_NAVY_SOFT = "#8FA6C4"
LPL_ORANGE = "#E87722"

TEXT_COLOR = "#1B2430"
SUBTEXT_COLOR = "#5C6875"
BORDER = "#DCE2EA"
CARD_BG = "#FFFFFF"
PAGE_BG = "#F4F6F9"
GRID = "#E8ECF2"

SRC_Q1 = LPL_NAVY_SOFT
SRC_LIVE = LPL_NAVY
STATUS_FINAL = LPL_NAVY
STATUS_OPEN = LPL_ORANGE

st.markdown(f"""
<style>
    .stApp {{ background: {PAGE_BG}; }}

    .block-container {{
        padding-top: 1rem;
        padding-bottom: 2.5rem;
        max-width: 1520px;
    }}

    html, body, [class*="css"] {{
        color: {TEXT_COLOR} !important;
        font-family: "Segoe UI", "Inter", sans-serif;
    }}

    h1 {{
        color: {LPL_NAVY} !important;
        font-weight: 800 !important;
        letter-spacing: -0.03em;
        margin-bottom: 0.12rem !important;
    }}

    h2, h3, h4, h5, h6 {{
        color: {LPL_NAVY} !important;
        font-weight: 700 !important;
        letter-spacing: -0.02em;
    }}

    p, label, .stCaption {{ color: {SUBTEXT_COLOR} !important; }}

    div[data-testid="stMetric"] {{
        background: {CARD_BG};
        border: 1px solid {BORDER};
        border-left: 4px solid {LPL_NAVY};
        border-radius: 10px;
        padding: 15px 16px;
        box-shadow: 0 2px 6px rgba(31, 56, 100, 0.06);
        height: 100%;
    }}

    div[data-testid="stMetricLabel"] {{
        color: {SUBTEXT_COLOR} !important;
        font-weight: 600 !important;
        font-size: 0.76rem !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        line-height: 1.35;
    }}

    div[data-testid="stMetricValue"] {{
        color: {LPL_NAVY} !important;
        font-weight: 800 !important;
        font-size: 1.65rem !important;
    }}

    div[data-testid="stMetricDelta"] {{
        font-size: 0.8rem !important;
    }}

    .stSelectbox label {{
        color: {TEXT_COLOR} !important;
        font-weight: 700 !important;
    }}

    div[data-testid="stDataFrame"] {{
        border: 1px solid {BORDER};
        border-radius: 10px;
        overflow: hidden;
    }}

    .stTabs [data-baseweb="tab-list"] {{
        gap: 4px;
        border-bottom: 2px solid {BORDER};
    }}

    .stTabs [data-baseweb="tab"] {{
        font-weight: 700;
        color: {SUBTEXT_COLOR};
        padding: 10px 24px;
    }}

    .stTabs [aria-selected="true"] {{
        color: {LPL_NAVY} !important;
        border-bottom: 3px solid {LPL_ORANGE};
    }}

    .section-shell {{
        background: {CARD_BG};
        border: 1px solid {BORDER};
        border-radius: 10px;
        border-top: 3px solid {LPL_NAVY};
        padding: 14px 18px;
        margin-top: 1.4rem;
        margin-bottom: 1rem;
    }}

    .section-title {{
        color: {LPL_NAVY};
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
        background: {CARD_BG};
        border: 1px solid {BORDER};
        border-left: 4px solid {LPL_ORANGE};
        border-radius: 8px;
        padding: 12px 14px;
        margin-top: 0.25rem;
        margin-bottom: 1rem;
        color: {SUBTEXT_COLOR};
        font-size: 0.9rem;
        line-height: 1.5;
    }}

    .slide-band {{
        background: {LPL_NAVY};
        border-radius: 10px 10px 0 0;
        padding: 18px 26px 14px 26px;
        margin-top: 0.4rem;
    }}

    .slide-band h2 {{
        color: #FFFFFF !important;
        font-size: 1.5rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: -0.02em;
    }}

    .slide-band p {{
        color: #C3D0E4 !important;
        font-size: 0.9rem;
        margin: 4px 0 0 0;
    }}

    .slide-rule {{
        height: 4px;
        background: {LPL_ORANGE};
        border-radius: 0 0 2px 2px;
        margin-bottom: 1.2rem;
    }}

    .group-label {{
        color: {SUBTEXT_COLOR};
        font-weight: 700;
        font-size: 0.78rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin: 1.1rem 0 0.6rem 0;
        padding-bottom: 5px;
        border-bottom: 1px solid {BORDER};
    }}

    .chart-cap {{
        color: {LPL_NAVY};
        font-weight: 700;
        font-size: 1rem;
        margin: 0.2rem 0 0.4rem 0;
    }}

    .foot-note {{
        color: {SUBTEXT_COLOR};
        font-size: 0.82rem;
        margin-top: 2rem;
        padding-top: 0.8rem;
        border-top: 1px solid {BORDER};
    }}
</style>
""", unsafe_allow_html=True)

# =========================================
# HELPERS
# =========================================
def section_header(title: str, subtitle: str = ""):
    st.markdown(
        f'<div class="section-shell"><div class="section-title">{title}</div>'
        f'<div class="section-subtitle">{subtitle}</div></div>',
        unsafe_allow_html=True
    )

def note_box(text: str):
    st.markdown(f'<div class="note-box">{text}</div>', unsafe_allow_html=True)

def group_label(text: str):
    st.markdown(f'<div class="group-label">{text}</div>', unsafe_allow_html=True)

def clean_cols(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [str(c).strip().replace("\n", " ").replace("\r", "").replace("\xa0", " ") for c in df.columns]
    return df

def pick_col(df: pd.DataFrame, options: list, required: bool = True):
    lookup = {str(c).strip().lower(): c for c in df.columns}
    for opt in options:
        if opt.lower() in lookup:
            return lookup[opt.lower()]
    if required:
        raise KeyError(f"Missing one of columns: {options}. Found columns: {list(df.columns)}")
    return None

def normalize_yes_no(series: pd.Series) -> pd.Series:
    s = series.astype(str).str.strip().str.lower()
    mapping = {"yes": "Yes", "y": "Yes", "true": "Yes", "1": "Yes",
               "no": "No", "n": "No", "false": "No", "0": "No"}
    return s.map(mapping).fillna(series.astype(str).str.strip())

def normalize_percentage(series: pd.Series) -> pd.Series:
    s = pd.to_numeric(series, errors="coerce")
    if not s.dropna().empty and s.dropna().le(1).all():
        s = s * 100
    return s

def avg_safe(series: pd.Series, decimals: int = 1) -> float:
    s = pd.to_numeric(series, errors="coerce")
    if s.dropna().empty:
        return 0.0
    return round(float(s.mean()), decimals)

def rate(df: pd.DataFrame, col: str):
    """Percent of Yes in a live-data column. None when there are no rows."""
    n = len(df)
    if n == 0:
        return None
    return round((df[col] == "Yes").sum() / n * 100, 1)

def fmt_pct(v):
    return "N/A" if v is None or pd.isna(v) else f"{v:.1f}%"

def fmt_score(v):
    return "N/A" if v is None or pd.isna(v) else f"{v:.1f}"

def apply_layout(fig, height=360, show_legend=True):
    fig.update_layout(
        height=height,
        margin=dict(l=18, r=18, t=52, b=18),
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(color=TEXT_COLOR, size=13, family="Segoe UI, Inter, sans-serif"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                    font=dict(color=TEXT_COLOR, size=12), title=None),
        showlegend=show_legend
    )
    fig.update_xaxes(title_font=dict(color=SUBTEXT_COLOR, size=12),
                     tickfont=dict(color=TEXT_COLOR), gridcolor=GRID, zeroline=False)
    fig.update_yaxes(title_font=dict(color=SUBTEXT_COLOR, size=12),
                     tickfont=dict(color=TEXT_COLOR), gridcolor=GRID, zeroline=False)
    return fig

MONTH_NUM = {"January": 1, "February": 2, "March": 3, "April": 4, "May": 5, "June": 6,
             "July": 7, "August": 8, "September": 9, "October": 10, "November": 11, "December": 12}
MONTH_ABBR = {v: k[:3] for k, v in MONTH_NUM.items()}

MONTH_FIXES = {"janruary": "January", "janaury": "January", "january": "January",
               "janurary": "January", "januarry": "January", "febuary": "February",
               "februrary": "February", "marhc": "March", "aplir": "April",
               "agust": "August", "ocotber": "October", "novemeber": "November",
               "decemeber": "December"}

def normalize_month_name(value: str) -> str:
    s = str(value).strip()
    if not s:
        return s
    if s.lower() in MONTH_FIXES:
        return MONTH_FIXES[s.lower()]
    return s.title()

def view_avg(df: pd.DataFrame, score_col: str) -> float:
    """Average of each associate's own average, so associates weigh equally.

    With a single associate selected this reduces to that person's plain mean,
    so no separate individual code path is needed.
    """
    if df.empty:
        return 0.0
    e = df.groupby("AssociateName", as_index=False)[score_col].mean()[score_col]
    return round(float(e.mean()), 1) if not e.empty else 0.0

# =========================================
# LOAD DATA
# =========================================
@st.cache_data
def load_graded_calls(path, sheet) -> pd.DataFrame:
    """Load a graded call file. The department file and the onboarding file
    share this schema, so both go through here and are treated identically."""
    df = clean_cols(pd.read_excel(path, sheet_name=sheet)).dropna(how="all")

    assoc = pick_col(df, ["AssociateName", "Associate Name"])
    team = pick_col(df, ["ManagerTeam", "Manager Team"])
    date = pick_col(df, ["DateOfCall", "Date Of Call"])
    res = pick_col(df, ["IssueResolvedFirstContact", "Issue Resolved First Contact"])
    failed = pick_col(df, ["CallFailed", "Call Failed"])
    total = pick_col(df, ["TotalScore", "Total Score"])
    pct = pick_col(df, ["Percentage"], required=False)

    out = pd.DataFrame({
        "AssociateName": df[assoc].astype(str).str.strip(),
        "ManagerTeam": df[team].astype(str).str.strip(),
        "DateOfCall": pd.to_datetime(df[date], errors="coerce"),
        "IssueResolvedFirstContact": normalize_yes_no(df[res]),
        "CallFailed": normalize_yes_no(df[failed]),
        "TotalScore": pd.to_numeric(df[total], errors="coerce"),
    })
    out["Percentage"] = normalize_percentage(df[pct]) if pct else out["TotalScore"]
    out = out.dropna(subset=["AssociateName", "ManagerTeam", "DateOfCall"], how="all")
    out = out[out["AssociateName"].str.strip() != ""]

    out["MonthLabel"] = out["DateOfCall"].dt.strftime("%b %Y")
    out["MonthSort"] = out["DateOfCall"].dt.to_period("M").astype(str)
    out["QuarterLabel"] = out["DateOfCall"].dt.quarter.apply(lambda x: f"Q{int(x)}" if pd.notna(x) else pd.NA)
    out["QuarterSort"] = out["DateOfCall"].dt.to_period("Q").astype(str)
    return out

def load_call_data() -> pd.DataFrame:
    return load_graded_calls(CALL_FILE, "Raw_Data")

@st.cache_data
def load_q1_data() -> pd.DataFrame:
    df = clean_cols(pd.read_excel(BENCH_FILE, sheet_name="Benchmark_Data")).dropna(how="all")

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
    }).dropna(subset=["AssociateName", "ManagerTeam", "Q1Month", "Score"], how="any")

    out["Q1Quarter"] = out["Q1Quarter"].replace(
        {"1": "Q1", "2": "Q2", "3": "Q3", "4": "Q4", 1: "Q1", 2: "Q2", 3: "Q3", 4: "Q4"})
    out["Q1MonthNum"] = out["Q1Month"].map(MONTH_NUM)
    out = out.dropna(subset=["Q1MonthNum"]).copy()
    out["Q1MonthNum"] = out["Q1MonthNum"].astype(int)
    out["Q1MonthLabel"] = out["Q1MonthNum"].map(lambda n: f"{MONTH_ABBR[n]} {Q1_YEAR}")
    return out

def load_new_hire_data() -> pd.DataFrame:
    """The onboarding file uses the same columns as the department file, so it
    goes through the same loader and gets identical treatment."""
    return load_graded_calls(NEW_HIRE_FILE, NEW_HIRE_SHEET)

st.title("MAS Dashboard")
st.caption("Managed Accounts Service call grading, year to date")

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

# Loaded quietly. A missing onboarding file must never break the main dashboard,
# so the error is surfaced inside the Onboarding tab instead of at the top.
new_hire_df = pd.DataFrame()
new_hire_error = None
try:
    new_hire_df = load_new_hire_data()
except FileNotFoundError:
    new_hire_error = (
        f"No onboarding file found. Expected it at **{NEW_HIRE_FILE.name}** next to this app. "
        "Add the file and redeploy, or update NEW_HIRE_FILE at the top of the script."
    )
except Exception as e:
    new_hire_error = f"Could not load the onboarding file: {e}"

note_box(
    "Q1 covers January through March scored call records. Those records are score-only and "
    "carry no call dates, so First Call Resolution Rate and Call Failed Rate begin at "
    "April 1, 2026 and are never reported for Q1. "
    "Q2 (April through June) is final. Q3 is in progress and currently holds July scores."
)

# =========================================
# VIEW SCOPE (applies to both tabs)
# =========================================
w1, w2 = st.columns([1, 1])

with w1:
    view_by = st.selectbox("View By", ["All Teams", "Katie", "Charles", "Individual Associate"], index=0)

all_associates = sorted(
    pd.concat([
        call_df["AssociateName"] if not call_df.empty else pd.Series(dtype=str),
        q1_df["AssociateName"] if not q1_df.empty else pd.Series(dtype=str)
    ]).dropna().astype(str).str.strip().unique().tolist()
)

selected_associate = None
with w2:
    if view_by == "Individual Associate":
        selected_associate = st.selectbox("Associate", all_associates)

def by_team(df):
    if df.empty:
        return df
    if view_by in ["Katie", "Charles"]:
        return df[df["ManagerTeam"] == view_by]
    if view_by == "Individual Associate" and selected_associate:
        return df[df["AssociateName"] == selected_associate]
    return df

call_scope = by_team(call_df)
q1_scope = by_team(q1_df)
individual_view = view_by == "Individual Associate"  # display only, not a math switch

# =========================================
# QUARTER TABLE + YEAR TO DATE TOTALS
# =========================================
def build_quarters() -> pd.DataFrame:
    rows = []

    if not q1_scope.empty:
        rows.append({
            "Quarter": "Q1", "Sort": f"{Q1_YEAR}Q1", "Status": "Score only",
            "Calls": int(len(q1_scope)),
            "Quality": view_avg(q1_scope, "Score"),
            "Resolution": None, "Failed": None,
        })

    if not call_scope.empty:
        live_qs = sorted(call_scope["QuarterSort"].dropna().unique().tolist())
        newest = live_qs[-1] if live_qs else None
        for qsort in live_qs:
            g = call_scope[call_scope["QuarterSort"] == qsort]
            rows.append({
                "Quarter": g["QuarterLabel"].iloc[0], "Sort": qsort,
                "Status": "In Progress" if qsort == newest else "Final",
                "Calls": int(len(g)),
                "Quality": view_avg(g, "TotalScore"),
                "Resolution": rate(g, "IssueResolvedFirstContact"),
                "Failed": rate(g, "CallFailed"),
            })

    return pd.DataFrame(rows).sort_values("Sort").reset_index(drop=True) if rows else pd.DataFrame()

quarters = build_quarters()

def combined_quality(q1_part: pd.DataFrame, live_part: pd.DataFrame) -> float:
    """Quality across Q1 and live data: average of each associate's own average."""
    if len(q1_part) + len(live_part) == 0:
        return 0.0

    a = q1_part.groupby("AssociateName", as_index=False).agg(S=("Score", "sum"), N=("Score", "size")) \
        if not q1_part.empty else pd.DataFrame(columns=["AssociateName", "S", "N"])
    b = live_part.groupby("AssociateName", as_index=False).agg(S2=("TotalScore", "sum"), N2=("TotalScore", "size")) \
        if not live_part.empty else pd.DataFrame(columns=["AssociateName", "S2", "N2"])
    m = a.merge(b, on="AssociateName", how="outer").fillna(0)
    if m.empty:
        return 0.0
    m["N_all"] = m["N"] + m["N2"]
    m["S_all"] = m["S"] + m["S2"]
    vals = pd.to_numeric(
        m.apply(lambda r: r["S_all"] / r["N_all"] if r["N_all"] > 0 else pd.NA, axis=1),
        errors="coerce"
    ).dropna()
    return round(vals.mean(), 1) if not vals.empty else 0.0

ytd_calls = len(q1_scope) + len(call_scope)
ytd_quality = combined_quality(q1_scope, call_scope)
ytd_resolution = rate(call_scope, "IssueResolvedFirstContact")
ytd_failed = rate(call_scope, "CallFailed")

def build_ranking(q1_part: pd.DataFrame, live_part: pd.DataFrame) -> pd.DataFrame:
    """Rank across every associate in the period, so a filtered view still
    shows a true standing rather than everyone starting at rank 1."""
    a = q1_part.groupby(["ManagerTeam", "AssociateName"], as_index=False).agg(S=("Score", "sum"), N=("Score", "size")) \
        if not q1_part.empty else pd.DataFrame(columns=["ManagerTeam", "AssociateName", "S", "N"])
    b = live_part.groupby(["ManagerTeam", "AssociateName"], as_index=False).agg(S2=("TotalScore", "sum"), N2=("TotalScore", "size")) \
        if not live_part.empty else pd.DataFrame(columns=["ManagerTeam", "AssociateName", "S2", "N2"])
    rk = a.merge(b, on=["ManagerTeam", "AssociateName"], how="outer").fillna(0)
    if rk.empty:
        return rk
    rk["Calls"] = (rk["N"] + rk["N2"]).astype(int)
    rk = rk[rk["Calls"] > 0].copy()
    if rk.empty:
        return rk
    rk["Quality"] = rk.apply(lambda r: round((r["S"] + r["S2"]) / r["Calls"], 1), axis=1)
    rk["Rank"] = rk["Quality"].rank(method="dense", ascending=False).astype("Int64")
    return rk.sort_values(["Rank", "AssociateName"]).reset_index(drop=True)


tab_summary, tab_detail, tab_onboarding = st.tabs(["Summary", "Detail", "Onboarding"])

# =========================================
# SUMMARY TAB
# =========================================
with tab_summary:
    scope_label = selected_associate if individual_view and selected_associate else view_by
    st.markdown(
        f'<div class="slide-band"><h2>Call Grading Year to Date</h2>'
        f'<p>Managed Accounts Service &nbsp;|&nbsp; {scope_label} &nbsp;|&nbsp; '
        f'Q1 through current quarter</p></div><div class="slide-rule"></div>',
        unsafe_allow_html=True
    )

    if quarters.empty:
        st.info("No call grading data available for this view.")
    else:
        group_label("Year to Date Totals")
        y1, y2, y3, y4 = st.columns(4)
        y1.metric("Total Calls Graded", f"{ytd_calls:,}")
        y2.metric("Average Quality Score", fmt_score(ytd_quality))
        y3.metric("First Call Resolution Rate", fmt_pct(ytd_resolution))
        y4.metric("Call Failed Rate", fmt_pct(ytd_failed))
        st.caption(
            "First Call Resolution Rate and Call Failed Rate cover April 1, 2026 forward only. "
            "Average Quality Score covers the full year, including Q1."
        )

        group_label("Average Quality Score by Quarter")
        qcols = st.columns(len(quarters))
        for i, (_, r) in enumerate(quarters.iterrows()):
            tag = " (In Progress)" if r["Status"] == "In Progress" else ""
            qcols[i].metric(
                f"{r['Quarter']}{tag}",
                fmt_score(r["Quality"]),
                f"{int(r['Calls']):,} calls graded",
                delta_color="off"
            )

        st.markdown("<br>", unsafe_allow_html=True)
        left, right = st.columns(2)

        with left:
            st.markdown('<div class="chart-cap">First Call Resolution Rate</div>', unsafe_allow_html=True)
            res_df = quarters[quarters["Resolution"].notna()].copy()
            if res_df.empty:
                st.info("Begins at Q2. Q1 records are score-only.")
            else:
                fig = go.Figure(go.Bar(
                    x=res_df["Quarter"], y=res_df["Resolution"],
                    marker_color=[STATUS_OPEN if s == "In Progress" else LPL_NAVY for s in res_df["Status"]],
                    text=[f"{v:.1f}%" for v in res_df["Resolution"]],
                    textposition="outside", width=0.5,
                ))
                fig = apply_layout(fig, height=340, show_legend=False)
                fig.update_yaxes(title="First Call Resolution Rate", range=[70, 100], ticksuffix="%")
                fig.update_xaxes(title="")
                st.plotly_chart(fig, use_container_width=True)

        with right:
            st.markdown('<div class="chart-cap">Average Quality Score</div>', unsafe_allow_html=True)
            fig = go.Figure(go.Bar(
                x=quarters["Quarter"], y=quarters["Quality"],
                marker_color=[STATUS_OPEN if s == "In Progress" else
                              (SRC_Q1 if s == "Score only" else LPL_NAVY) for s in quarters["Status"]],
                text=[f"{v:.1f}" for v in quarters["Quality"]],
                textposition="outside", width=0.5,
            ))
            fig = apply_layout(fig, height=340, show_legend=False)
            fig.update_yaxes(title="Average Quality Score", range=[70, 100])
            fig.update_xaxes(title="")
            st.plotly_chart(fig, use_container_width=True)

        tbl = quarters[["Quarter", "Calls", "Quality", "Resolution", "Failed"]].copy()
        tbl = pd.concat([tbl, pd.DataFrame([{
            "Quarter": "Year to Date", "Calls": ytd_calls,
            "Quality": ytd_quality, "Resolution": ytd_resolution, "Failed": ytd_failed,
        }])], ignore_index=True)

        tbl["Calls"] = tbl["Calls"].map(lambda v: f"{int(v):,}")
        tbl["Quality"] = tbl["Quality"].map(fmt_score)
        tbl["Resolution"] = tbl["Resolution"].map(fmt_pct)
        tbl["Failed"] = tbl["Failed"].map(fmt_pct)
        tbl.columns = ["Quarter", "Calls Graded", "Average Quality Score",
                       "First Call Resolution Rate", "Call Failed Rate"]
        st.dataframe(tbl, use_container_width=True, hide_index=True)

# =========================================
# DETAIL TAB
# =========================================
with tab_detail:
    period_options = ["All Year"]
    period_map = {}

    if not q1_scope.empty:
        period_options.append("Q1")
        period_map["Q1"] = ("q1_quarter", None)
    if not call_scope.empty:
        for q in sorted(call_scope["QuarterSort"].dropna().unique().tolist()):
            lab = call_scope[call_scope["QuarterSort"] == q]["QuarterLabel"].iloc[0]
            period_options.append(lab)
            period_map[lab] = ("live_quarter", q)
    if not q1_scope.empty:
        for _, r in q1_scope[["Q1MonthLabel", "Q1Month", "Q1MonthNum"]].drop_duplicates().sort_values("Q1MonthNum").iterrows():
            period_options.append(r["Q1MonthLabel"])
            period_map[r["Q1MonthLabel"]] = ("q1_month", r["Q1Month"])
    if not call_scope.empty:
        for _, r in call_scope[["MonthLabel", "MonthSort"]].drop_duplicates().sort_values("MonthSort").iterrows():
            period_options.append(r["MonthLabel"])
            period_map[r["MonthLabel"]] = ("live_month", r["MonthLabel"])

    period = st.selectbox("Period", period_options, index=0)
    kind, val = period_map.get(period, (None, None))

    def slice_period(q1_src, live_src):
        e_q1, e_lv = q1_src.iloc[0:0], live_src.iloc[0:0]
        if kind is None:
            return q1_src, live_src
        if kind == "q1_quarter":
            return q1_src, e_lv
        if kind == "q1_month":
            return q1_src[q1_src["Q1Month"] == val], e_lv
        if kind == "live_quarter":
            return e_q1, live_src[live_src["QuarterSort"] == val]
        return e_q1, live_src[live_src["MonthLabel"] == val]

    # Scoped to the current View By, for tiles and the detail tables
    q1_period, call_period = slice_period(q1_scope, call_scope)
    # Whole population, so ranks are true standings rather than rank 1 of 1
    q1_all_period, call_all_period = slice_period(q1_df, call_df)

    has_q1 = not q1_period.empty
    has_live = not call_period.empty
    plabel = "Year to Date" if kind is None else period

    # ---------------- Overview ----------------
    section_header(
        f"{plabel} Overview",
        "Every figure below reflects the selected period. Year to date totals are shown alongside for reference."
    )

    p_calls = len(q1_period) + len(call_period)
    p_quality = combined_quality(q1_period, call_period)
    p_resolution = rate(call_period, "IssueResolvedFirstContact")
    p_failed = rate(call_period, "CallFailed")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Calls Graded", f"{p_calls:,}")
    m2.metric("Average Quality Score", fmt_score(p_quality))
    m3.metric("First Call Resolution Rate", fmt_pct(p_resolution))
    m4.metric("Call Failed Rate", fmt_pct(p_failed))

    if has_q1 and not has_live:
        st.caption(
            "Q1 records are score-only, so First Call Resolution Rate and "
            "Call Failed Rate are not available for this period."
        )

    st.markdown("<br>", unsafe_allow_html=True)
    group_label("Year to Date, All Periods")
    d1, d2, d3, d4 = st.columns(4)
    d1.metric("Total Calls Graded", f"{ytd_calls:,}")
    d2.metric("Average Quality Score", fmt_score(ytd_quality))
    d3.metric("First Call Resolution Rate", fmt_pct(ytd_resolution))
    d4.metric("Call Failed Rate", fmt_pct(ytd_failed))

    # ---------------- Trend charts: only across the whole year ----------------
    # A single quarter or month renders as one bar, which says nothing the tiles
    # above have not already said. Quarter-over-quarter lives on the Summary tab.
    if kind is None:
        section_header("Average Quality Score by Month",
                       "January through March scores alongside April-forward live grading months.")

        parts = []
        if not q1_scope.empty:
            e = q1_scope.groupby(["Q1MonthNum", "AssociateName"], as_index=False).agg(E=("Score", "mean"))
            a = e.groupby("Q1MonthNum", as_index=False).agg(Quality=("E", "mean"))
            c = q1_scope.groupby("Q1MonthNum", as_index=False).agg(Calls=("Score", "size"))
            d = a.merge(c, on="Q1MonthNum")
            d["Label"] = d["Q1MonthNum"].map(lambda n: f"{MONTH_ABBR[n]} {Q1_YEAR}")
            d["Sort"] = d["Q1MonthNum"].map(lambda n: f"{Q1_YEAR}-{n:02d}")
            d["Source"] = "Q1 (Jan-Mar)"
            parts.append(d[["Label", "Sort", "Quality", "Calls", "Source"]])

        if not call_scope.empty:
            e = call_scope.groupby(["MonthSort", "MonthLabel", "AssociateName"], as_index=False).agg(E=("TotalScore", "mean"))
            a = e.groupby(["MonthSort", "MonthLabel"], as_index=False).agg(Quality=("E", "mean"))
            c = call_scope.groupby(["MonthSort", "MonthLabel"], as_index=False).agg(Calls=("TotalScore", "size"))
            d = a.merge(c, on=["MonthSort", "MonthLabel"]).rename(columns={"MonthLabel": "Label", "MonthSort": "Sort"})
            d["Source"] = "Live Grading"
            parts.append(d[["Label", "Sort", "Quality", "Calls", "Source"]])

        if parts:
            monthly = pd.concat(parts, ignore_index=True).sort_values("Sort").reset_index(drop=True)
            monthly["Quality"] = monthly["Quality"].round(1)
            fig = px.bar(
                monthly, x="Label", y="Quality", color="Source",
                text=monthly.apply(lambda r: f"{r['Quality']:.1f}<br>{int(r['Calls'])} calls", axis=1),
                barmode="group",
                color_discrete_map={"Q1 (Jan-Mar)": SRC_Q1, "Live Grading": SRC_LIVE},
            )
            fig.update_traces(textposition="outside")
            fig = apply_layout(fig, height=380)
            fig.update_xaxes(title="", categoryorder="array", categoryarray=monthly["Label"].tolist())
            fig.update_yaxes(title="Average Quality Score", range=[0, 105])
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No monthly data available for this view.")

        section_header("Average Quality Score by Quarter",
                       "Q1 scores, closed quarters, and the quarter in progress.")

        if quarters.empty:
            st.info("No quarterly data available for this view.")
        else:
            fig = px.bar(
                quarters, x="Quarter", y="Quality", color="Status",
                text=quarters.apply(lambda r: f"{r['Quality']:.1f}<br>{int(r['Calls'])} calls", axis=1),
                color_discrete_map={"Score only": SRC_Q1, "Final": STATUS_FINAL, "In Progress": STATUS_OPEN},
            )
            fig.update_traces(textposition="outside", width=0.5)
            fig = apply_layout(fig, height=360)
            fig.update_xaxes(title="", categoryorder="array", categoryarray=quarters["Quarter"].tolist())
            fig.update_yaxes(title="Average Quality Score", range=[0, 105])
            st.plotly_chart(fig, use_container_width=True)

    # ---------------- Ranking: true standing across every associate ----------------
    section_header(f"{plabel} Ranking",
                   "Every associate ranked by their own average quality score for this period. "
                   "Ranks are calculated across the whole department, so a filtered view still "
                   "shows a true standing.")

    ranking_all = build_ranking(q1_all_period, call_all_period)

    if ranking_all.empty:
        st.info(f"No graded calls in {plabel}.")
    else:
        total_ranked = len(ranking_all)

        if view_by in ["Katie", "Charles"]:
            shown = ranking_all[ranking_all["ManagerTeam"] == view_by]
        elif individual_view and selected_associate:
            shown = ranking_all[ranking_all["AssociateName"] == selected_associate]
        else:
            shown = ranking_all

        if shown.empty:
            st.info(f"No graded calls in {plabel} for this view.")
        else:
            cols = ["ManagerTeam", "AssociateName", "Calls", "Quality", "Rank"] if view_by == "All Teams" \
                else ["AssociateName", "Calls", "Quality", "Rank"]
            st.dataframe(
                shown[cols].rename(columns={
                    "ManagerTeam": "Team", "AssociateName": "Associate",
                    "Calls": "Calls Graded", "Quality": "Average Quality Score", "Rank": "Rank"}),
                use_container_width=True, hide_index=True
            )
            if individual_view and selected_associate:
                st.caption(f"Rank {int(shown['Rank'].iloc[0])} of {total_ranked} associates graded in {plabel}.")
            elif view_by in ["Katie", "Charles"]:
                st.caption(f"Ranked against all {total_ranked} associates graded in {plabel}.")

    # ---------------- Call detail, only what the period contains ----------------
    if has_live:
        section_header("Graded Call Detail", f"Individual live graded calls in {plabel}.")
        det = call_period[["AssociateName", "ManagerTeam", "DateOfCall", "TotalScore",
                           "Percentage", "CallFailed", "IssueResolvedFirstContact"]].copy()
        det = det.sort_values("DateOfCall", ascending=False)
        det["DateOfCall"] = det["DateOfCall"].dt.strftime("%m/%d/%Y")
        det["Percentage"] = det["Percentage"].round(1)
        det.columns = ["Associate", "Team", "Date of Call", "Total Score", "Percentage",
                       "Call Failed", "Resolved on First Contact"]
        st.dataframe(det, use_container_width=True, hide_index=True)
        st.caption(f"{len(det):,} graded calls.")

    if has_q1:
        section_header("Q1 Call Scores",
                       "Listed by month, since Q1 records carry no call dates.")
        d = q1_period[["AssociateName", "ManagerTeam", "Q1Month", "Q1MonthNum", "Score"]].copy()
        d = d.sort_values(["Q1MonthNum", "AssociateName"])
        d = d[["AssociateName", "ManagerTeam", "Q1Month", "Score"]]
        d.columns = ["Associate", "Team", "Month", "Score"]
        st.dataframe(d, use_container_width=True, hide_index=True)
        st.caption(f"{len(d):,} Q1 call scores.")

    if not has_live and not has_q1:
        st.info(f"No call records in {plabel} for this view.")

# =========================================
# ONBOARDING TAB
# =========================================
# Entirely self-contained. Reads only NEW_HIRE_FILE and touches nothing that
# feeds the Summary or Detail tabs, so onboarding scores never move the
# department numbers. The View By control above does not apply here either.
with tab_onboarding:
    st.markdown(
        '<div class="slide-band"><h2>Onboarding Call Grading</h2>'
        '<p>Managed Accounts Service &nbsp;|&nbsp; Associates in training &nbsp;|&nbsp; '
        'Excluded from department performance</p>'
        '</div><div class="slide-rule"></div>',
        unsafe_allow_html=True
    )

    note_box(
        "<strong>Associates in training.</strong> The individuals shown here are still completing "
        "onboarding. Their scores are maintained in a separate record and are excluded from all "
        "department, team, and quarterly figures reported on the Summary and Detail tabs, so "
        "overall performance reflects fully ramped associates only. "
        "These results are intended to track individual progress through training and should not "
        "be read as department performance or compared directly against tenured associate results."
    )

    if new_hire_error:
        st.warning(new_hire_error)
    elif new_hire_df.empty:
        st.info("The onboarding file loaded but contains no scored calls yet.")
    else:
        nh = new_hire_df
        nh_names = sorted(nh["AssociateName"].unique().tolist())

        # Per associate, then the average of those, so each weighs the same
        # regardless of how many of their calls have been graded.
        per_hire = (
            nh.groupby(["AssociateName", "ManagerTeam"], as_index=False)
              .agg(Calls=("TotalScore", "size"), Quality=("TotalScore", "mean"))
        )
        per_hire["Quality"] = per_hire["Quality"].round(1)
        per_hire = per_hire.sort_values("Quality", ascending=False).reset_index(drop=True)

        overall_quality = round(float(per_hire["Quality"].mean()), 1)
        overall_calls = int(len(nh))

        group_label("All Associates in Training")
        n1, n2, n3, n4 = st.columns(4)
        n1.metric("Associates in Training", f"{len(nh_names):,}")
        n2.metric("Total Calls Graded", f"{overall_calls:,}")
        n3.metric("Average Quality Score", fmt_score(overall_quality))
        n4.metric("First Call Resolution Rate", fmt_pct(rate(nh, "IssueResolvedFirstContact")))

        st.markdown("<br>", unsafe_allow_html=True)
        e1, e2, e3, e4 = st.columns(4)
        e1.metric("Call Failed Rate", fmt_pct(rate(nh, "CallFailed")))
        latest = nh["DateOfCall"].max()
        e2.metric("Most Recent Graded Call", latest.strftime("%m/%d/%Y") if pd.notna(latest) else "N/A")
        e3.metric("Highest Score", fmt_score(nh["TotalScore"].max()))
        e4.metric("Lowest Score", fmt_score(nh["TotalScore"].min()))

        st.caption(
            "Averages are calculated using the same methodology as the rest of the dashboard, "
            "so onboarding results remain directly comparable once an associate completes training."
        )

        group_label("By Associate")
        hcols = st.columns(min(len(per_hire), 4))
        for i, (_, r) in enumerate(per_hire.iterrows()):
            if i < len(hcols):
                hcols[i].metric(
                    r["AssociateName"], fmt_score(r["Quality"]),
                    f"{int(r['Calls']):,} calls graded", delta_color="off"
                )

        st.markdown("<br>", unsafe_allow_html=True)
        left, right = st.columns(2)

        with left:
            st.markdown('<div class="chart-cap">Average Quality Score by Associate</div>',
                        unsafe_allow_html=True)
            fig = go.Figure(go.Bar(
                x=per_hire["AssociateName"], y=per_hire["Quality"],
                marker_color=LPL_NAVY,
                text=[f"{v:.1f}" for v in per_hire["Quality"]],
                textposition="outside", width=0.5,
            ))
            fig.add_hline(
                y=overall_quality, line_dash="dash", line_color=LPL_ORANGE,
                annotation_text=f"Onboarding average {overall_quality:.1f}",
                annotation_position="top left",
                annotation_font_color=LPL_ORANGE,
            )
            fig = apply_layout(fig, height=340, show_legend=False)
            fig.update_yaxes(title="Average Quality Score", range=[0, 105])
            fig.update_xaxes(title="")
            st.plotly_chart(fig, use_container_width=True)

        with right:
            st.markdown('<div class="chart-cap">Average Quality Score by Month</div>',
                        unsafe_allow_html=True)
            monthly_nh = (
                nh.groupby(["MonthSort", "MonthLabel"], as_index=False)
                  .agg(Calls=("TotalScore", "size"), Quality=("TotalScore", "mean"))
                  .sort_values("MonthSort")
            )
            monthly_nh["Quality"] = monthly_nh["Quality"].round(1)
            fig = go.Figure(go.Bar(
                x=monthly_nh["MonthLabel"], y=monthly_nh["Quality"],
                marker_color=LPL_NAVY,
                text=[f"{q:.1f}<br>{int(c)} calls"
                      for q, c in zip(monthly_nh["Quality"], monthly_nh["Calls"])],
                textposition="outside", width=0.5,
            ))
            fig = apply_layout(fig, height=340, show_legend=False)
            fig.update_yaxes(title="Average Quality Score", range=[0, 105])
            fig.update_xaxes(title="", categoryorder="array",
                             categoryarray=monthly_nh["MonthLabel"].tolist())
            st.plotly_chart(fig, use_container_width=True)

        section_header("Onboarding Summary",
                       "One row per associate in training, with the combined onboarding average.")
        summary_tbl = per_hire.copy()
        summary_tbl["Resolution"] = summary_tbl["AssociateName"].map(
            lambda n: rate(nh[nh["AssociateName"] == n], "IssueResolvedFirstContact"))
        summary_tbl["Failed"] = summary_tbl["AssociateName"].map(
            lambda n: rate(nh[nh["AssociateName"] == n], "CallFailed"))

        summary_tbl = summary_tbl[["AssociateName", "ManagerTeam", "Calls",
                                   "Quality", "Resolution", "Failed"]]
        summary_tbl.columns = ["Associate", "Team", "Calls Graded",
                               "Average Quality Score", "First Call Resolution Rate",
                               "Call Failed Rate"]
        summary_tbl["Calls Graded"] = summary_tbl["Calls Graded"].map(lambda v: f"{int(v):,}")
        summary_tbl["Average Quality Score"] = summary_tbl["Average Quality Score"].map(fmt_score)
        summary_tbl["First Call Resolution Rate"] = summary_tbl["First Call Resolution Rate"].map(fmt_pct)
        summary_tbl["Call Failed Rate"] = summary_tbl["Call Failed Rate"].map(fmt_pct)

        summary_tbl = pd.concat([summary_tbl, pd.DataFrame([{
            "Associate": "All in Training", "Team": "",
            "Calls Graded": f"{overall_calls:,}",
            "Average Quality Score": fmt_score(overall_quality),
            "First Call Resolution Rate": fmt_pct(rate(nh, "IssueResolvedFirstContact")),
            "Call Failed Rate": fmt_pct(rate(nh, "CallFailed")),
        }])], ignore_index=True)
        st.dataframe(summary_tbl, use_container_width=True, hide_index=True)

        section_header("Graded Call Detail",
                       "Every graded call recorded during onboarding.")
        det = nh[["AssociateName", "ManagerTeam", "DateOfCall", "TotalScore",
                  "Percentage", "CallFailed", "IssueResolvedFirstContact"]].copy()
        det = det.sort_values("DateOfCall", ascending=False)
        det["DateOfCall"] = det["DateOfCall"].dt.strftime("%m/%d/%Y")
        det["Percentage"] = det["Percentage"].round(1)
        det.columns = ["Associate", "Team", "Date of Call", "Total Score", "Percentage",
                       "Call Failed", "Resolved on First Contact"]
        st.dataframe(det, use_container_width=True, hide_index=True)
        st.caption(f"{len(det):,} graded calls across {len(nh_names)} associates in training.")

        # Safeguard: the same person in both files would be counted twice
        if not call_df.empty:
            overlap = sorted(set(nh_names) & set(call_df["AssociateName"].unique()))
            if overlap:
                st.warning(
                    "These associates appear in both the onboarding file and the main call grading file, "
                    "so their calls are also counted in the department metrics: "
                    + ", ".join(overlap)
                    + ". Remove them from one file to keep onboarding fully separate."
                )

st.markdown(
    '<div class="foot-note">Quality scores are calculated as the average of each associate\'s own '
    'average, so associates are weighted equally regardless of how many of their calls were graded.</div>',
    unsafe_allow_html=True
)

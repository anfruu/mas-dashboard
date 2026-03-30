import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(page_title="MAS Dashboard", layout="wide")

BASE_DIR = Path(__file__).parent
CALL_FILE = BASE_DIR / "MAS_Call_Grading_Raw_Data.xlsx"
BENCH_FILE = BASE_DIR / "MAS_Benchmarks.xlsx"
TRACKER_FILE = BASE_DIR / "MAS_90Day_Tracker.xlsx"
SURVEY_FILE = BASE_DIR / "MAS_Survey.xlsx"

# =========================================
# POLISHED ENTERPRISE STYLING
# =========================================
TEXT_COLOR = "#102033"
SUBTEXT_COLOR = "#556476"
BORDER = "#D9E2EC"
CARD_BG = "#F7FAFC"
PAGE_BG = "#F4F8FB"
SECTION_BG = "#FFFFFF"

PRIMARY = "#2F5D8C"      # muted blue
SECONDARY = "#4F8A8B"    # muted teal
ACCENT = "#7A6FA6"       # muted violet
WARM = "#C28B52"         # muted amber
SOFT_RED = "#B86A6A"     # muted red
SLATE = "#60758A"
LIGHT_SLATE = "#A8B6C3"

TEAM_COLORS = {
    "Katie": PRIMARY,
    "Charles": SECONDARY,
    "MAS": ACCENT
}

CATEGORY_COLORS = [
    PRIMARY,
    SECONDARY,
    ACCENT,
    WARM,
    SLATE,
    SOFT_RED
]

STATUS_COLORS = {
    "Completed": SECONDARY,
    "In Progress": PRIMARY
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

    .stTabs [data-baseweb="tab-list"] {{
        gap: 12px;
        border-bottom: none;
        padding-bottom: 8px;
    }}

    .stTabs [data-baseweb="tab"] {{
        height: 44px;
        background-color: #FFFFFF;
        border: 1px solid {BORDER};
        border-radius: 12px;
        padding-left: 18px;
        padding-right: 18px;
        color: {TEXT_COLOR} !important;
        font-weight: 700;
        box-shadow: 0 1px 2px rgba(16, 32, 51, 0.04);
    }}

    .stTabs [aria-selected="true"] {{
        background: linear-gradient(180deg, #F7FBFF 0%, #EEF5FB 100%) !important;
        border-color: #C9D8E6 !important;
        color: {PRIMARY} !important;
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

    .phase-card {{
        background: linear-gradient(180deg, #FFFFFF 0%, #F7FAFC 100%);
        border: 1px solid {BORDER};
        border-radius: 18px;
        padding: 16px;
        min-height: 220px;
        box-shadow: 0 2px 8px rgba(16, 32, 51, 0.04);
    }}

    .phase-title {{
        color: {TEXT_COLOR};
        font-weight: 800;
        font-size: 1.0rem;
        margin-bottom: 0.7rem;
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

def phase_card_start(title: str):
    st.markdown(
        f"""
        <div class="phase-card">
            <div class="phase-title">{title}</div>
        """,
        unsafe_allow_html=True
    )

def phase_card_end():
    st.markdown("</div>", unsafe_allow_html=True)

def clean_cols(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]
    return df

def pick_col(df: pd.DataFrame, options: list[str], required: bool = True):
    lookup = {str(c).strip().lower(): c for c in df.columns}
    for opt in options:
        if opt.lower() in lookup:
            return lookup[opt.lower()]
    if required:
        raise KeyError(f"Missing one of columns: {options}")
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

def quarter_label(dt_series: pd.Series) -> pd.Series:
    return dt_series.dt.to_period("Q").astype(str)

def month_label(dt_series: pd.Series) -> pd.Series:
    return dt_series.dt.strftime("%b %Y")

# =========================================
# LOAD DATA
# =========================================
@st.cache_data
def load_call_data() -> pd.DataFrame:
    df = pd.read_excel(CALL_FILE)
    df = clean_cols(df)

    assoc = pick_col(df, ["AssociateName", "Associate Name"])
    team = pick_col(df, ["ManagerTeam", "Manager Team"])
    date = pick_col(df, ["DateOfCall", "Date Of Call"])
    total = pick_col(df, ["TotalScore", "Total Score"])
    pct = pick_col(df, ["Percentage"])
    fcr = pick_col(df, ["IssueResolvedFirstContact", "Issue Resolved First Contact"])
    tried = pick_col(df, ["TriedToResolveBeforeCalling", "Tried To Resolve Before Calling"])
    failed = pick_col(df, ["CallFailed", "Call Failed"])

    intro = pick_col(df, ["IntroductionAuthentication", "Introduction Authentication"])
    call_handling = pick_col(df, ["CallHandlingProfessionalism", "Call Handling Professionalism"])
    empathy = pick_col(df, ["EngagementEmpathy", "Engagement Empathy"])
    discovery = pick_col(df, ["DiscoveryUnderstanding", "Discovery Understanding"])
    ownership = pick_col(df, ["AccuracyAdvocacyOwnership", "Accuracy Advocacy Ownership"])
    documentation = pick_col(df, ["Documentation"])

    out = pd.DataFrame({
        "AssociateName": df[assoc].astype(str).str.strip(),
        "ManagerTeam": df[team].astype(str).str.strip(),
        "DateOfCall": pd.to_datetime(df[date], errors="coerce"),
        "TotalScore": pd.to_numeric(df[total], errors="coerce"),
        "Percentage": normalize_percentage(df[pct]),
        "IssueResolvedFirstContact": normalize_yes_no(df[fcr]),
        "TriedToResolveBeforeCalling": normalize_yes_no(df[tried]),
        "CallFailed": normalize_yes_no(df[failed]),
        "IntroductionAuthentication": pd.to_numeric(df[intro], errors="coerce"),
        "CallHandlingProfessionalism": pd.to_numeric(df[call_handling], errors="coerce"),
        "EngagementEmpathy": pd.to_numeric(df[empathy], errors="coerce"),
        "DiscoveryUnderstanding": pd.to_numeric(df[discovery], errors="coerce"),
        "AccuracyAdvocacyOwnership": pd.to_numeric(df[ownership], errors="coerce"),
        "Documentation": pd.to_numeric(df[documentation], errors="coerce"),
    })

    out = out.dropna(subset=["AssociateName", "ManagerTeam"], how="all")
    out["MonthLabel"] = month_label(out["DateOfCall"])
    out["QuarterLabel"] = quarter_label(out["DateOfCall"])
    out["MonthSort"] = out["DateOfCall"].dt.to_period("M").astype(str)
    out["QuarterSort"] = out["DateOfCall"].dt.to_period("Q").astype(str)
    return out

@st.cache_data
def load_benchmark_data() -> pd.DataFrame:
    df = pd.read_excel(BENCH_FILE, sheet_name="Benchmark_Data")
    df = clean_cols(df)

    team = pick_col(df, ["ManagerTeam", "Manager Team"])
    assoc = pick_col(df, ["AssociateName", "Associate Name"])
    avg = pick_col(df, ["BenchmarkAverageScore", "Benchmark Average Score"])
    rank = pick_col(df, ["BenchmarkRank", "Benchmark Rank"])

    out = pd.DataFrame({
        "ManagerTeam": df[team].astype(str).str.strip(),
        "AssociateName": df[assoc].astype(str).str.strip(),
        "BenchmarkAverageScore": pd.to_numeric(df[avg], errors="coerce"),
        "BenchmarkRank": pd.to_numeric(df[rank], errors="coerce"),
    })
    return out

@st.cache_data
def load_tracker_data() -> pd.DataFrame:
    df = pd.read_excel(TRACKER_FILE)
    df = clean_cols(df)

    task = pick_col(df, ["TaskName", "Task Name"])
    phase = pick_col(df, ["Phase"])
    section = pick_col(df, ["Section"])
    focus = pick_col(df, ["FocusArea", "Focus Area"])
    desc = pick_col(df, ["TaskDescription", "Task Description"])
    start = pick_col(df, ["StartDate", "Start Date"])
    due = pick_col(df, ["DueDate", "Due Date"])
    status = pick_col(df, ["Status"])
    notes = pick_col(df, ["Notes"], required=False)
    updated = pick_col(df, ["LastUpdated", "Last Updated"], required=False)

    out = pd.DataFrame({
        "TaskName": df[task].astype(str).str.strip(),
        "Phase": df[phase].astype(str).str.strip(),
        "Section": df[section].astype(str).str.strip(),
        "FocusArea": df[focus].astype(str).str.strip(),
        "TaskDescription": df[desc].astype(str).str.strip(),
        "StartDate": pd.to_datetime(df[start], errors="coerce"),
        "DueDate": pd.to_datetime(df[due], errors="coerce"),
        "Status": df[status].astype(str).str.strip(),
        "Notes": df[notes].astype(str).str.strip() if notes else "",
        "LastUpdated": pd.to_datetime(df[updated], errors="coerce") if updated else pd.NaT,
    })
    return out

@st.cache_data
def load_survey_data() -> pd.DataFrame:
    df = pd.read_excel(SURVEY_FILE, sheet_name="Categorical_Summary")
    df = clean_cols(df)

    q = pick_col(df, ["Question"])
    r = pick_col(df, ["Response"])
    c = pick_col(df, ["Count"])
    t = pick_col(df, ["Total Responses", "TotalResponses"])
    p = pick_col(df, ["Percent"])

    out = pd.DataFrame({
        "Question": df[q].astype(str).str.strip(),
        "Response": df[r].astype(str).str.strip(),
        "Count": pd.to_numeric(df[c], errors="coerce"),
        "TotalResponses": pd.to_numeric(df[t], errors="coerce"),
        "Percent": pd.to_numeric(df[p], errors="coerce"),
    })

    # If percentages came in as 0-1 decimals, convert to 0-100
    if not out["Percent"].dropna().empty and out["Percent"].dropna().le(1).all():
        out["Percent"] = out["Percent"] * 100

    return out.dropna(subset=["Question", "Response"], how="all")

# =========================================
# DATA INIT
# =========================================
st.title("MAS Dashboard")
st.caption("Managed Accounts Service metrics, benchmarking, survey insights, and 90-day execution tracking")

try:
    call_df = load_call_data()
except Exception as e:
    st.error(f"Could not load call grading data: {e}")
    call_df = pd.DataFrame()

try:
    bench_df = load_benchmark_data()
except Exception as e:
    st.error(f"Could not load benchmark data: {e}")
    bench_df = pd.DataFrame()

try:
    tracker_df = load_tracker_data()
except Exception as e:
    st.error(f"Could not load 90-day tracker data: {e}")
    tracker_df = pd.DataFrame()

try:
    survey_df = load_survey_data()
except Exception as e:
    st.error(f"Could not load survey data: {e}")
    survey_df = pd.DataFrame()

tab1, tab2, tab3, tab4 = st.tabs(["Call Grading", "Benchmarks", "90-Day Tracker", "Service Survey"])

# =========================================
# TAB 1 - CALL GRADING
# =========================================
with tab1:
    section_header(
        "Call Grading Overview",
        "Quality performance, monthly/quarterly comparisons, and category breakdowns."
    )

    if call_df.empty:
        st.warning("No call grading data loaded.")
    else:
        available_months = sorted(call_df["MonthSort"].dropna().unique().tolist())
        latest_month = available_months[-1] if available_months else None

        available_quarters = sorted(call_df["QuarterSort"].dropna().unique().tolist())
        latest_quarter = available_quarters[-1] if available_quarters else None

        f1, f2, f3, f4 = st.columns([1, 1, 1, 1])

        with f1:
            time_view = st.selectbox("Time View", ["All-Time", "Current Month", "Specific Month"], index=0)

        selected_month = None
        if time_view == "Specific Month":
            month_options = sorted(
                call_df["MonthLabel"].dropna().unique().tolist(),
                key=lambda x: pd.to_datetime(x, format="%b %Y")
            )
            with f2:
                selected_month = st.selectbox("Select Month", month_options)

        with f3:
            view_by = st.selectbox(
                "View By",
                ["All Teams", "Katie", "Charles", "Individual Associate"],
                index=0
            )

        associate_filter = None
        if view_by == "Individual Associate":
            with f4:
                associate_filter = st.selectbox(
                    "Associate Name",
                    sorted(call_df["AssociateName"].dropna().unique().tolist())
                )

        filtered = call_df.copy()

        if time_view == "Current Month" and latest_month:
            filtered = filtered[filtered["MonthSort"] == latest_month]
        elif time_view == "Specific Month" and selected_month:
            filtered = filtered[filtered["MonthLabel"] == selected_month]

        if view_by in ["Katie", "Charles"]:
            filtered = filtered[filtered["ManagerTeam"] == view_by]
        elif view_by == "Individual Associate" and associate_filter:
            filtered = filtered[filtered["AssociateName"] == associate_filter]

        total_calls = len(filtered)
        avg_score = avg_safe(filtered["TotalScore"])
        failed_rate = pct_text((filtered["CallFailed"] == "Yes").sum(), total_calls)
        fcr_rate = pct_text((filtered["IssueResolvedFirstContact"] == "Yes").sum(), total_calls)
        tried_rate = pct_text((filtered["TriedToResolveBeforeCalling"] == "Yes").sum(), total_calls)

        month_compare_df = call_df.copy()
        quarter_compare_df = call_df.copy()

        if view_by in ["Katie", "Charles"]:
            month_compare_df = month_compare_df[month_compare_df["ManagerTeam"] == view_by]
            quarter_compare_df = quarter_compare_df[quarter_compare_df["ManagerTeam"] == view_by]
        elif view_by == "Individual Associate" and associate_filter:
            month_compare_df = month_compare_df[month_compare_df["AssociateName"] == associate_filter]
            quarter_compare_df = quarter_compare_df[quarter_compare_df["AssociateName"] == associate_filter]

        monthly_avg = avg_safe(
            month_compare_df[month_compare_df["MonthSort"] == latest_month]["TotalScore"]
        ) if latest_month else 0

        quarterly_avg = avg_safe(
            quarter_compare_df[quarter_compare_df["QuarterSort"] == latest_quarter]["TotalScore"]
        ) if latest_quarter else 0

        m1, m2, m3, m4, m5, m6, m7 = st.columns(7)
        m1.metric("Total Calls", total_calls)
        m2.metric("Avg Call Score", avg_score)
        m3.metric("Failed Call Rate", failed_rate)
        m4.metric("FCR Rate", fcr_rate)
        m5.metric("Tried Before Calling", tried_rate)
        m6.metric("Monthly Avg", monthly_avg)
        m7.metric("Quarterly Avg", quarterly_avg)

        st.markdown("<br>", unsafe_allow_html=True)

        if view_by == "All Teams":
            team_summary = (
                filtered.groupby("ManagerTeam", as_index=False)
                .agg(AverageScore=("TotalScore", "mean"))
            )

            fig_team = px.bar(
                team_summary,
                x="ManagerTeam",
                y="AverageScore",
                color="ManagerTeam",
                color_discrete_map={"Katie": TEAM_COLORS["Katie"], "Charles": TEAM_COLORS["Charles"]},
                text_auto=".1f",
                title="Average Score by Team"
            )
            fig_team = apply_layout(fig_team, height=285)
            st.plotly_chart(fig_team, use_container_width=True)

        else:
            trend_df = filtered.copy()
            if not trend_df.empty:
                trend_df["TrendMonth"] = trend_df["DateOfCall"].dt.strftime("%b %Y")
                trend_plot = (
                    trend_df.groupby(["TrendMonth", "MonthSort"], as_index=False)
                    .agg(TotalScore=("TotalScore", "mean"))
                    .sort_values("MonthSort")
                )

                fig_trend = px.line(
                    trend_plot,
                    x="TrendMonth",
                    y="TotalScore",
                    markers=True,
                    title="Average Score Trend by Month"
                )
                fig_trend.update_traces(line=dict(width=3, color=PRIMARY), marker=dict(size=9, color=PRIMARY))
                fig_trend = apply_layout(fig_trend, height=315, show_legend=False)
                fig_trend.update_xaxes(title="")
                fig_trend.update_yaxes(title="Avg Total Score")
                st.plotly_chart(fig_trend, use_container_width=True)

        st.markdown("<br>", unsafe_allow_html=True)

        if view_by != "Individual Associate":
            assoc_avg = (
                filtered.groupby("AssociateName", as_index=False)
                .agg(AverageScore=("TotalScore", "mean"))
                .sort_values("AverageScore", ascending=False)
            )

            c1, c2 = st.columns(2)
            with c1:
                section_header("Top Percentile", "Highest average scoring associates in current view.")
                st.dataframe(assoc_avg.head(5), use_container_width=True, hide_index=True)

            with c2:
                section_header("Bottom Percentile", "Lowest average scoring associates in current view.")
                st.dataframe(
                    assoc_avg.tail(5).sort_values("AverageScore", ascending=True),
                    use_container_width=True,
                    hide_index=True
                )

            st.markdown("<br>", unsafe_allow_html=True)

        category_map = {
            "Introduction & Authentication": ("IntroductionAuthentication", 5),
            "Call Handling & Professionalism": ("CallHandlingProfessionalism", 20),
            "Engagement & Empathy": ("EngagementEmpathy", 30),
            "Discovery & Understanding": ("DiscoveryUnderstanding", 20),
            "Accuracy, Advocacy & Ownership": ("AccuracyAdvocacyOwnership", 20),
            "Documentation": ("Documentation", 5),
        }

        cat_rows = []
        for label, (col, max_score) in category_map.items():
            val = filtered[col].mean()
            pct_val = 0 if pd.isna(val) else (val / max_score) * 100
            cat_rows.append({"Category": label, "AveragePercent": pct_val})

        category_df = pd.DataFrame(cat_rows).sort_values("AveragePercent", ascending=True)

        fig_cat = px.bar(
            category_df,
            x="AveragePercent",
            y="Category",
            orientation="h",
            color="Category",
            color_discrete_sequence=CATEGORY_COLORS,
            text="AveragePercent",
            title="Category Performance"
        )
        fig_cat.update_traces(texttemplate="%{text:.1f}%", textposition="outside", showlegend=False)
        fig_cat.update_layout(
            height=390,
            margin=dict(l=18, r=18, t=52, b=18),
            plot_bgcolor="white",
            paper_bgcolor="white",
            font=dict(color=TEXT_COLOR, size=13)
        )
        fig_cat.update_xaxes(title="Average % of Possible Score", gridcolor="#E6EDF3")
        fig_cat.update_yaxes(title="")
        st.plotly_chart(fig_cat, use_container_width=True)

        st.markdown("<br>", unsafe_allow_html=True)
        section_header("Call Detail Table", "Underlying call-level details for the selected filters.")

        detail_cols = [
            "AssociateName", "ManagerTeam", "DateOfCall", "TotalScore", "Percentage",
            "CallFailed", "IssueResolvedFirstContact", "TriedToResolveBeforeCalling"
        ]
        detail_df = filtered[detail_cols].copy()
        detail_df["Percentage"] = detail_df["Percentage"].round(1)
        st.dataframe(
            detail_df.sort_values("DateOfCall", ascending=False),
            use_container_width=True,
            hide_index=True
        )

# =========================================
# TAB 2 - BENCHMARKS
# =========================================
with tab2:
    section_header(
        "Benchmark Comparison",
        "Benchmark ranking and current performance comparisons across Katie, Charles, and MAS."
    )

    if bench_df.empty:
        st.warning("No benchmark data loaded.")
    else:
        current_assoc = pd.DataFrame()
        if not call_df.empty:
            current_assoc = (
                call_df.groupby(["ManagerTeam", "AssociateName"], as_index=False)
                .agg(CurrentAverageScore=("TotalScore", "mean"))
            )
            current_assoc["CurrentRankWithinTeam"] = (
                current_assoc.groupby("ManagerTeam")["CurrentAverageScore"]
                .rank(method="dense", ascending=False)
                .astype(int)
            )

        bench_combined = bench_df.copy().sort_values("BenchmarkAverageScore", ascending=False).reset_index(drop=True)
        bench_combined["ServiceBenchmarkRank"] = bench_combined["BenchmarkAverageScore"].rank(method="dense", ascending=False).astype(int)

        if not current_assoc.empty:
            current_combined = current_assoc.copy().sort_values("CurrentAverageScore", ascending=False).reset_index(drop=True)
            current_combined["ServiceCurrentRank"] = current_combined["CurrentAverageScore"].rank(method="dense", ascending=False).astype(int)
        else:
            current_combined = pd.DataFrame(columns=["AssociateName", "CurrentAverageScore", "ServiceCurrentRank"])

        benchmark_compare = pd.DataFrame({
            "Group": ["Katie", "Charles", "MAS"],
            "BenchmarkAverage": [
                avg_safe(bench_df[bench_df["ManagerTeam"] == "Katie"]["BenchmarkAverageScore"]),
                avg_safe(bench_df[bench_df["ManagerTeam"] == "Charles"]["BenchmarkAverageScore"]),
                avg_safe(bench_df["BenchmarkAverageScore"])
            ],
            "CurrentAverage": [
                avg_safe(current_assoc[current_assoc["ManagerTeam"] == "Katie"]["CurrentAverageScore"]) if not current_assoc.empty else 0,
                avg_safe(current_assoc[current_assoc["ManagerTeam"] == "Charles"]["CurrentAverageScore"]) if not current_assoc.empty else 0,
                avg_safe(current_assoc["CurrentAverageScore"]) if not current_assoc.empty else 0
            ]
        })

        k1, k2 = st.columns(2)
        k1.metric("Benchmark Avg (MAS)", avg_safe(bench_df["BenchmarkAverageScore"]))
        k2.metric("Current Avg (MAS)", avg_safe(current_assoc["CurrentAverageScore"]) if not current_assoc.empty else 0)

        st.markdown("<br>", unsafe_allow_html=True)

        fig_bench = px.bar(
            benchmark_compare.melt(id_vars="Group", var_name="Metric", value_name="Score"),
            x="Group",
            y="Score",
            color="Metric",
            barmode="group",
            title="Benchmark vs Current Average Score",
            color_discrete_map={
                "BenchmarkAverage": ACCENT,
                "CurrentAverage": PRIMARY
            },
            text_auto=".1f"
        )
        fig_bench = apply_layout(fig_bench, height=320)
        st.plotly_chart(fig_bench, use_container_width=True)

        st.markdown("<br>", unsafe_allow_html=True)
        section_header("Team Benchmark Snapshot", "Average benchmark and current score comparison by team and department.")
        st.dataframe(benchmark_compare, use_container_width=True, hide_index=True)

        st.markdown("<br>", unsafe_allow_html=True)
        section_header("MAS Combined Ranking", "Service-wide reranking across all associates regardless of team.")

        combined_merge = bench_combined.merge(
            current_combined[["AssociateName", "CurrentAverageScore", "ServiceCurrentRank"]],
            on="AssociateName",
            how="left"
        )
        st.dataframe(
            combined_merge[[
                "AssociateName",
                "BenchmarkAverageScore",
                "ServiceBenchmarkRank",
                "CurrentAverageScore",
                "ServiceCurrentRank"
            ]].sort_values("ServiceBenchmarkRank"),
            use_container_width=True,
            hide_index=True
        )

        st.markdown("<br>", unsafe_allow_html=True)

        team1, team2 = st.columns(2)

        with team1:
            section_header("Katie Team Rankings", "Benchmark ranking compared to current team ranking.")
            katie_merge = bench_df[bench_df["ManagerTeam"] == "Katie"].merge(
                current_assoc[current_assoc["ManagerTeam"] == "Katie"][["AssociateName", "CurrentAverageScore", "CurrentRankWithinTeam"]],
                on="AssociateName",
                how="left"
            )
            st.dataframe(
                katie_merge[[
                    "AssociateName", "BenchmarkAverageScore", "BenchmarkRank",
                    "CurrentAverageScore", "CurrentRankWithinTeam"
                ]].sort_values("BenchmarkRank"),
                use_container_width=True,
                hide_index=True
            )

        with team2:
            section_header("Charles Team Rankings", "Benchmark ranking compared to current team ranking.")
            charles_merge = bench_df[bench_df["ManagerTeam"] == "Charles"].merge(
                current_assoc[current_assoc["ManagerTeam"] == "Charles"][["AssociateName", "CurrentAverageScore", "CurrentRankWithinTeam"]],
                on="AssociateName",
                how="left"
            )
            st.dataframe(
                charles_merge[[
                    "AssociateName", "BenchmarkAverageScore", "BenchmarkRank",
                    "CurrentAverageScore", "CurrentRankWithinTeam"
                ]].sort_values("BenchmarkRank"),
                use_container_width=True,
                hide_index=True
            )

# =========================================
# TAB 3 - 90 DAY TRACKER
# =========================================
with tab3:
    section_header(
        "90-Day Tracker",
        "Execution progress across all phases with streamlined status tracking."
    )

    if tracker_df.empty:
        st.warning("No tracker data loaded.")
    else:
        phase_filter = st.selectbox("Phase", ["All Phases", "Phase 1", "Phase 2", "Phase 3"])

        tfiltered = tracker_df.copy()
        if phase_filter != "All Phases":
            tfiltered = tfiltered[tfiltered["Phase"] == phase_filter]

        tfiltered = tfiltered[tfiltered["Status"].isin(["In Progress", "Completed"])]

        total_tasks = len(tfiltered)
        completed = int((tfiltered["Status"] == "Completed").sum())
        in_progress = int((tfiltered["Status"] == "In Progress").sum())
        completion_rate = pct_text(completed, total_tasks)

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Tasks", total_tasks)
        m2.metric("Completed", completed)
        m3.metric("In Progress", in_progress)
        m4.metric("Completion Rate", completion_rate)

        st.markdown("<br>", unsafe_allow_html=True)

        phase_summary = (
            tfiltered.groupby("Phase", as_index=False)
            .agg(
                TotalTasks=("TaskName", "count"),
                Completed=("Status", lambda s: (s == "Completed").sum()),
                InProgress=("Status", lambda s: (s == "In Progress").sum())
            )
        )

        if not phase_summary.empty:
            phase_summary["CompletionRate"] = (
                (phase_summary["Completed"] / phase_summary["TotalTasks"]) * 100
            ).round(1).fillna(0)

        if phase_filter == "All Phases":
            p1, p2, p3 = st.columns(3)
            phase_lookup = {
                "Phase 1": {"TotalTasks": 0, "Completed": 0, "InProgress": 0, "CompletionRate": 0},
                "Phase 2": {"TotalTasks": 0, "Completed": 0, "InProgress": 0, "CompletionRate": 0},
                "Phase 3": {"TotalTasks": 0, "Completed": 0, "InProgress": 0, "CompletionRate": 0},
            }

            for _, row in phase_summary.iterrows():
                phase_lookup[row["Phase"]] = {
                    "TotalTasks": int(row["TotalTasks"]),
                    "Completed": int(row["Completed"]),
                    "InProgress": int(row["InProgress"]),
                    "CompletionRate": row["CompletionRate"]
                }

            for col, phase_name in zip([p1, p2, p3], ["Phase 1", "Phase 2", "Phase 3"]):
                with col:
                    phase_card_start(phase_name)
                    st.metric("Total Tasks", phase_lookup[phase_name]["TotalTasks"])
                    st.metric("Completed", phase_lookup[phase_name]["Completed"])
                    st.metric("In Progress", phase_lookup[phase_name]["InProgress"])
                    st.metric("Completion %", f'{phase_lookup[phase_name]["CompletionRate"]:.1f}%')
                    phase_card_end()
        else:
            if not phase_summary.empty:
                row = phase_summary.iloc[0]
                phase_card_start(phase_filter)
                a, b, c, d = st.columns(4)
                a.metric("Total Tasks", int(row["TotalTasks"]))
                b.metric("Completed", int(row["Completed"]))
                c.metric("In Progress", int(row["InProgress"]))
                d.metric("Completion %", f'{row["CompletionRate"]:.1f}%')
                phase_card_end()

        st.markdown("<br>", unsafe_allow_html=True)

        left, right = st.columns(2)

        with left:
            phase_melt = phase_summary.melt(
                id_vars="Phase",
                value_vars=["Completed", "InProgress"],
                var_name="StatusGroup",
                value_name="Count"
            ) if not phase_summary.empty else pd.DataFrame()

            if not phase_melt.empty:
                fig_phase = px.bar(
                    phase_melt,
                    x="Phase",
                    y="Count",
                    color="StatusGroup",
                    barmode="group",
                    title="Status by Phase",
                    color_discrete_map={
                        "Completed": STATUS_COLORS["Completed"],
                        "InProgress": STATUS_COLORS["In Progress"]
                    },
                    text_auto=True
                )
                fig_phase = apply_layout(fig_phase, height=330)
                st.plotly_chart(fig_phase, use_container_width=True)

        with right:
            status_counts = (
                tfiltered.groupby("Status", as_index=False)
                .agg(Count=("TaskName", "count"))
            )

            if not status_counts.empty:
                fig_status = px.pie(
                    status_counts,
                    values="Count",
                    names="Status",
                    title="Overall Status Breakdown",
                    color="Status",
                    color_discrete_map=STATUS_COLORS,
                    hole=0.58
                )
                fig_status = apply_layout(fig_status, height=330)
                st.plotly_chart(fig_status, use_container_width=True)

        st.markdown("<br>", unsafe_allow_html=True)

        focus_status = (
            tfiltered.groupby(["FocusArea", "Status"], as_index=False)
            .agg(TaskCount=("TaskName", "count"))
        )

        if not focus_status.empty:
            focus_totals = (
                focus_status.groupby("FocusArea", as_index=False)["TaskCount"]
                .sum()
                .sort_values("TaskCount", ascending=False)
            )
            focus_order = focus_totals["FocusArea"].tolist()

            fig_focus = px.bar(
                focus_status,
                x="TaskCount",
                y="FocusArea",
                color="Status",
                orientation="h",
                barmode="stack",
                category_orders={"FocusArea": focus_order[::-1]},
                title="Progress by Focus Area",
                color_discrete_map=STATUS_COLORS,
                text_auto=True
            )
            fig_focus = apply_layout(fig_focus, height=420, show_legend=True)
            fig_focus.update_yaxes(title="")
            fig_focus.update_xaxes(title="Task Count", gridcolor="#E6EDF3")
            st.plotly_chart(fig_focus, use_container_width=True)

        st.markdown("<br>", unsafe_allow_html=True)
        section_header("Phase Summary", "Condensed summary table for phase-level progress.")
        if not phase_summary.empty:
            st.dataframe(
                phase_summary[["Phase", "TotalTasks", "Completed", "InProgress", "CompletionRate"]],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No phase summary available.")

# =========================================
# TAB 4 - SERVICE SURVEY
# =========================================
with tab4:
    section_header(
        "Service Survey",
        "Anonymous service-level insights grouped into recognition, training, support, manual feedback, and peer coaching themes."
    )

    if survey_df.empty:
        st.warning("No survey data loaded.")
    else:
        total_responses = int(survey_df["TotalResponses"].max()) if not survey_df["TotalResponses"].dropna().empty else 0
        total_questions = int(survey_df["Question"].nunique())
        total_themes = int(survey_df["Response"].nunique())

        yes_df = survey_df[survey_df["Response"].str.strip().str.lower() == "yes"].copy()
        dynamics_yes = yes_df[yes_df["Question"].str.contains("Dynamics", case=False, na=False)]["Percent"]
        manual_search_yes = yes_df[yes_df["Question"].str.contains("search within the MAS manual", case=False, na=False)]["Percent"]
        manual_ease_yes = yes_df[yes_df["Question"].str.contains("user-friendly and easy to navigate", case=False, na=False)]["Percent"]
        peer_yes = yes_df[yes_df["Question"].str.contains("peer-to-peer coaching", case=False, na=False)]["Percent"]

        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Total Responses", total_responses)
        k2.metric("Dynamics Confidence % Yes", f"{avg_safe(dynamics_yes):.1f}%")
        k3.metric("MAS Manual Ease % Yes", f"{avg_safe(manual_ease_yes):.1f}%")
        k4.metric("Peer Coaching % Yes", f"{avg_safe(peer_yes):.1f}%")

        st.markdown("<br>", unsafe_allow_html=True)

        question_options = ["All Questions"] + sorted(survey_df["Question"].dropna().unique().tolist())
        selected_question = st.selectbox("Survey Focus", question_options)

        survey_filtered = survey_df.copy()
        if selected_question != "All Questions":
            survey_filtered = survey_filtered[survey_filtered["Question"] == selected_question]

        # Recognition
        recognition = survey_filtered[
            survey_filtered["Question"].str.contains("recognized for achievements", case=False, na=False)
        ].sort_values("Count", ascending=True)

        # Training
        training = survey_filtered[
            survey_filtered["Question"].str.contains("Improve Training|Onboarding", case=False, na=False)
        ].sort_values("Count", ascending=True)

        # Knowledge
        knowledge = survey_filtered[
            survey_filtered["Question"].str.contains("benefit from additional knowledge", case=False, na=False)
        ].sort_values("Count", ascending=True)

        # Support
        support = survey_filtered[
            survey_filtered["Question"].str.contains("Additional Support|Resources|Tools", case=False, na=False)
        ].sort_values("Count", ascending=True)

        # Manual feedback
        manual_fb = survey_filtered[
            survey_filtered["Question"].str.contains("Feedback on MAS Manual", case=False, na=False)
        ].sort_values("Count", ascending=True)

        # Peer coaching
        peer = survey_filtered[
            survey_filtered["Question"].str.contains("peer-to-peer coaching", case=False, na=False)
        ].sort_values("Count", ascending=True)

        # Additional feedback
        addl = survey_filtered[
            survey_filtered["Question"].str.contains("Additional Feedback", case=False, na=False)
        ].sort_values("Count", ascending=True)

        top_left, top_right = st.columns(2)

        with top_left:
            if not recognition.empty:
                fig_rec = px.bar(
                    recognition,
                    x="Count",
                    y="Response",
                    orientation="h",
                    text="Percent",
                    color="Response",
                    color_discrete_sequence=CATEGORY_COLORS,
                    title="Recognition Preference Breakdown"
                )
                fig_rec.update_traces(texttemplate="%{text:.1f}%", textposition="outside", showlegend=False)
                fig_rec = apply_layout(fig_rec, height=340, show_legend=False)
                fig_rec.update_yaxes(title="")
                st.plotly_chart(fig_rec, use_container_width=True)

        with top_right:
            yesno_questions = survey_df[
                survey_df["Response"].str.strip().str.lower().isin(["yes", "no"])
            ].copy()
            if selected_question != "All Questions":
                yesno_questions = yesno_questions[yesno_questions["Question"] == selected_question]

            if not yesno_questions.empty:
                fig_yesno = px.bar(
                    yesno_questions,
                    x="Percent",
                    y="Question",
                    color="Response",
                    orientation="h",
                    barmode="group",
                    text="Percent",
                    title="Yes / No Survey Snapshot",
                    color_discrete_map={"Yes": SECONDARY, "No": SOFT_RED}
                )
                fig_yesno.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
                fig_yesno = apply_layout(fig_yesno, height=340, show_legend=True)
                fig_yesno.update_yaxes(title="")
                fig_yesno.update_xaxes(title="Percent of Responses")
                st.plotly_chart(fig_yesno, use_container_width=True)

        st.markdown("<br>", unsafe_allow_html=True)

        mid_left, mid_right = st.columns(2)

        with mid_left:
            if not training.empty:
                fig_train = px.bar(
                    training,
                    x="Count",
                    y="Response",
                    orientation="h",
                    text="Count",
                    color="Response",
                    color_discrete_sequence=CATEGORY_COLORS,
                    title="Training & Onboarding Themes"
                )
                fig_train.update_traces(textposition="outside", showlegend=False)
                fig_train = apply_layout(fig_train, height=360, show_legend=False)
                fig_train.update_yaxes(title="")
                st.plotly_chart(fig_train, use_container_width=True)

        with mid_right:
            if not knowledge.empty:
                fig_know = px.bar(
                    knowledge,
                    x="Count",
                    y="Response",
                    orientation="h",
                    text="Count",
                    color="Response",
                    color_discrete_sequence=CATEGORY_COLORS,
                    title="Knowledge & Development Themes"
                )
                fig_know.update_traces(textposition="outside", showlegend=False)
                fig_know = apply_layout(fig_know, height=360, show_legend=False)
                fig_know.update_yaxes(title="")
                st.plotly_chart(fig_know, use_container_width=True)

        st.markdown("<br>", unsafe_allow_html=True)

        low_left, low_right = st.columns(2)

        with low_left:
            if not support.empty:
                fig_support = px.bar(
                    support,
                    x="Count",
                    y="Response",
                    orientation="h",
                    text="Count",
                    color="Response",
                    color_discrete_sequence=CATEGORY_COLORS,
                    title="Support / Resources Themes"
                )
                fig_support.update_traces(textposition="outside", showlegend=False)
                fig_support = apply_layout(fig_support, height=360, show_legend=False)
                fig_support.update_yaxes(title="")
                st.plotly_chart(fig_support, use_container_width=True)

        with low_right:
            if not manual_fb.empty:
                fig_manual = px.bar(
                    manual_fb,
                    x="Count",
                    y="Response",
                    orientation="h",
                    text="Count",
                    color="Response",
                    color_discrete_sequence=CATEGORY_COLORS,
                    title="MAS Manual Feedback Themes"
                )
                fig_manual.update_traces(textposition="outside", showlegend=False)
                fig_manual = apply_layout(fig_manual, height=360, show_legend=False)
                fig_manual.update_yaxes(title="")
                st.plotly_chart(fig_manual, use_container_width=True)

        st.markdown("<br>", unsafe_allow_html=True)

        bottom_left, bottom_right = st.columns(2)

        with bottom_left:
            if not peer.empty:
                fig_peer = px.bar(
                    peer,
                    x="Count",
                    y="Response",
                    orientation="h",
                    text="Percent",
                    color="Response",
                    color_discrete_map={"Yes": SECONDARY, "No": SOFT_RED},
                    title="Peer Coaching Interest"
                )
                fig_peer.update_traces(texttemplate="%{text:.1f}%", textposition="outside", showlegend=False)
                fig_peer = apply_layout(fig_peer, height=300, show_legend=False)
                fig_peer.update_yaxes(title="")
                st.plotly_chart(fig_peer, use_container_width=True)

        with bottom_right:
            if not addl.empty:
                fig_addl = px.bar(
                    addl,
                    x="Count",
                    y="Response",
                    orientation="h",
                    text="Count",
                    color="Response",
                    color_discrete_sequence=CATEGORY_COLORS,
                    title="Additional Feedback Themes"
                )
                fig_addl.update_traces(textposition="outside", showlegend=False)
                fig_addl = apply_layout(fig_addl, height=300, show_legend=False)
                fig_addl.update_yaxes(title="")
                st.plotly_chart(fig_addl, use_container_width=True)

        st.markdown("<br>", unsafe_allow_html=True)
        section_header("Survey Summary Table", "Grouped survey responses used to power the charts above.")
        display_survey = survey_filtered.copy()
        display_survey["Percent"] = display_survey["Percent"].round(1)
        st.dataframe(display_survey, use_container_width=True, hide_index=True)

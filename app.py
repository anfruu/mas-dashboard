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

CATEGORY_COLORS = [
    PRIMARY,
    SECONDARY,
    ACCENT,
    WARM,
    SLATE,
    SOFT_RED
]

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

def quarter_label(dt_series: pd.Series) -> pd.Series:
    return dt_series.dt.to_period("Q").astype(str)

def month_label(dt_series: pd.Series) -> pd.Series:
    return dt_series.dt.strftime("%b %Y")

def add_simple_percentile_labels(df: pd.DataFrame, score_col: str, group_col: str | None = None) -> pd.DataFrame:
    out_frames = []

    if group_col is None:
        groups = [("ALL", df.copy())]
    else:
        groups = list(df.groupby(group_col, dropna=False))

    for _, g in groups:
        g = g.sort_values(score_col, ascending=False).reset_index(drop=True).copy()
        n = len(g)

        if n == 0:
            g["PercentileGroup"] = ""
            out_frames.append(g)
            continue

        top_n = max(1, round(n * 0.2))
        bottom_n = max(1, round(n * 0.2))

        labels = []
        for i in range(n):
            if i < top_n:
                labels.append("Top 20%")
            elif i >= n - bottom_n:
                labels.append("Bottom 20%")
            else:
                labels.append("Middle 60%")

        g["PercentileGroup"] = labels
        out_frames.append(g)

    return pd.concat(out_frames, ignore_index=True)

# =========================================
# LOAD CALL DATA
# =========================================
@st.cache_data
def load_call_data() -> pd.DataFrame:
    df = pd.read_excel(CALL_FILE, sheet_name="Raw_Data")
    df = clean_cols(df)
    df = df.dropna(how="all")

    assoc = pick_col(df, ["AssociateName", "Associate Name"])
    team = pick_col(df, ["ManagerTeam", "Manager Team"])
    date = pick_col(df, ["DateOfCall", "Date Of Call"])
    total = pick_col(df, ["TotalScore", "Total Score"])
    pct = pick_col(df, ["Percentage"], required=False)
    fcr = pick_col(df, ["IssueResolvedFirstContact", "Issue Resolved First Contact"])
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
        "IssueResolvedFirstContact": normalize_yes_no(df[fcr]),
        "CallFailed": normalize_yes_no(df[failed]),
        "IntroductionAuthentication": pd.to_numeric(df[intro], errors="coerce"),
        "CallHandlingProfessionalism": pd.to_numeric(df[call_handling], errors="coerce"),
        "EngagementEmpathy": pd.to_numeric(df[empathy], errors="coerce"),
        "DiscoveryUnderstanding": pd.to_numeric(df[discovery], errors="coerce"),
        "AccuracyAdvocacyOwnership": pd.to_numeric(df[ownership], errors="coerce"),
        "Documentation": pd.to_numeric(df[documentation], errors="coerce"),
    })

    if pct:
        out["Percentage"] = normalize_percentage(df[pct])
    else:
        out["Percentage"] = out["TotalScore"]

    out = out.dropna(subset=["AssociateName", "ManagerTeam"], how="all")
    out["MonthLabel"] = month_label(out["DateOfCall"])
    out["QuarterLabel"] = quarter_label(out["DateOfCall"])
    out["MonthSort"] = out["DateOfCall"].dt.to_period("M").astype(str)
    out["QuarterSort"] = out["DateOfCall"].dt.to_period("Q").astype(str)
    return out

# =========================================
# LOAD BENCHMARK DATA
# =========================================
@st.cache_data
def load_benchmark_data() -> pd.DataFrame:
    raw = pd.read_excel(BENCH_FILE, sheet_name="Benchmark_Data", header=0)
    raw = raw.dropna(how="all")
    raw = raw.iloc[:, 0:3].copy()
    raw.columns = ["ManagerTeam", "AssociateName", "BenchmarkAverageScore"]

    raw["ManagerTeam"] = raw["ManagerTeam"].astype(str).str.strip()
    raw["AssociateName"] = raw["AssociateName"].astype(str).str.strip()
    raw["BenchmarkAverageScore"] = pd.to_numeric(raw["BenchmarkAverageScore"], errors="coerce")

    raw = raw.dropna(subset=["ManagerTeam", "AssociateName", "BenchmarkAverageScore"]).reset_index(drop=True)

    raw["BenchmarkRank"] = (
        raw.groupby("ManagerTeam")["BenchmarkAverageScore"]
        .rank(method="dense", ascending=False)
        .astype(int)
    )

    raw = add_simple_percentile_labels(raw, "BenchmarkAverageScore", "ManagerTeam")
    return raw

# =========================================
# DATA INIT
# =========================================
st.title("MAS Dashboard")
st.caption("Managed Accounts Service metrics and benchmark tracking")

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

tab1, tab2 = st.tabs(["Call Grading", "Benchmarks"])

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

        m1, m2, m3, m4, m5, m6 = st.columns(6)
        m1.metric("Total Calls", total_calls)
        m2.metric("Avg Call Score", avg_score)
        m3.metric("Failed Call Rate", failed_rate)
        m4.metric("FCR Rate", fcr_rate)
        m5.metric("Monthly Avg", monthly_avg)
        m6.metric("Quarterly Avg", quarterly_avg)

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
                .reset_index(drop=True)
            )
            assoc_avg.insert(0, "Rank", range(1, len(assoc_avg) + 1))

            if view_by == "All Teams":
                ranking_df = assoc_avg.head(10).copy()
            else:
                ranking_df = assoc_avg.copy()

            section_header("Associate Rankings", "Highest to lowest average score in current view.")
            st.dataframe(
                ranking_df,
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
            "CallFailed", "IssueResolvedFirstContact"
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
        "Benchmark averages, auto-calculated ranks, and current performance comparisons."
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
        bench_combined["ServiceBenchmarkRank"] = (
            bench_combined["BenchmarkAverageScore"].rank(method="dense", ascending=False).astype(int)
        )

        if not current_assoc.empty:
            current_combined = current_assoc.copy().sort_values("CurrentAverageScore", ascending=False).reset_index(drop=True)
            current_combined["ServiceCurrentRank"] = (
                current_combined["CurrentAverageScore"].rank(method="dense", ascending=False).astype(int)
            )
        else:
            current_combined = pd.DataFrame(
                columns=["AssociateName", "CurrentAverageScore", "ServiceCurrentRank"]
            )

        benchmark_compare = pd.DataFrame({
            "Group": ["Katie", "Charles", "MAS"],
            "BenchmarkAverage": [
                avg_safe(bench_df.loc[bench_df["ManagerTeam"] == "Katie", "BenchmarkAverageScore"]),
                avg_safe(bench_df.loc[bench_df["ManagerTeam"] == "Charles", "BenchmarkAverageScore"]),
                avg_safe(bench_df["BenchmarkAverageScore"])
            ],
            "CurrentAverage": [
                avg_safe(current_assoc.loc[current_assoc["ManagerTeam"] == "Katie", "CurrentAverageScore"]) if not current_assoc.empty else 0,
                avg_safe(current_assoc.loc[current_assoc["ManagerTeam"] == "Charles", "CurrentAverageScore"]) if not current_assoc.empty else 0,
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
        section_header("Team Benchmark Snapshot", "Average benchmark and current score comparison by team.")
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
            section_header("Katie Team Rankings", "Benchmark rank compared to current team rank.")
            katie_merge = bench_df.loc[bench_df["ManagerTeam"] == "Katie"].merge(
                current_assoc.loc[current_assoc["ManagerTeam"] == "Katie", ["AssociateName", "CurrentAverageScore", "CurrentRankWithinTeam"]],
                on="AssociateName",
                how="left"
            )
            st.dataframe(
                katie_merge[[
                    "AssociateName",
                    "BenchmarkAverageScore",
                    "BenchmarkRank",
                    "CurrentAverageScore",
                    "CurrentRankWithinTeam"
                ]].sort_values("BenchmarkRank"),
                use_container_width=True,
                hide_index=True
            )

        with team2:
            section_header("Charles Team Rankings", "Benchmark rank compared to current team rank.")
            charles_merge = bench_df.loc[bench_df["ManagerTeam"] == "Charles"].merge(
                current_assoc.loc[current_assoc["ManagerTeam"] == "Charles", ["AssociateName", "CurrentAverageScore", "CurrentRankWithinTeam"]],
                on="AssociateName",
                how="left"
            )
            st.dataframe(
                charles_merge[[
                    "AssociateName",
                    "BenchmarkAverageScore",
                    "BenchmarkRank",
                    "CurrentAverageScore",
                    "CurrentRankWithinTeam"
                ]].sort_values("BenchmarkRank"),
                use_container_width=True,
                hide_index=True
            )

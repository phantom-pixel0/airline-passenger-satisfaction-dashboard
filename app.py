"""Airline Passenger Satisfaction Dashboard.

Sections: Executive Overview | Passenger Analysis |
          Flight & Service Experience | Business Insights

Run with:  streamlit run app.py
"""

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

# ======================================================================
# 1. SETTINGS
# ======================================================================
# Relative path: works on any computer if the folder layout is kept.
DATA_PATH = Path(__file__).parent / "data" / "airline_cleaned.csv"

# Column names exactly as they appear in the CSV.
SAT = "satisfaction"
SATISFIED = "satisfied"
DEP = "Departure Delay in Minutes"
ARR = "Arrival Delay in Minutes"
AGE = "Age"
DISTANCE = "Flight Distance"
GENDER = "Gender"
CUSTOMER = "Customer Type"
TRAVEL = "Type of Travel"
CLASS = "Class"
OVERVIEW_COLUMNS = [SAT, DEP, ARR]  # a record with none of these is "blank"

SERVICE_COLUMNS = [
    "Inflight wifi service",
    "Departure/Arrival time convenient",
    "Ease of Online booking",
    "Gate location",
    "Food and drink",
    "Online boarding",
    "Seat comfort",
    "Inflight entertainment",
    "On-board service",
    "Leg room service",
    "Baggage handling",
    "Checkin service",
    "Inflight service",
    "Cleanliness",
]
# Rating scale is 1-5. A 0 is treated as "not applicable" (see the notes on the
# Flight & Service Experience page). Set to None to treat 0 as a normal rating.
NOT_APPLICABLE_RATING = 0

# Columns created by this app (the CSV is never changed).
AGE_GROUP = "Age Group"
DEP_BAND = "Departure Delay Band"
ARR_BAND = "Arrival Delay Band"

# Age groups are a presentation choice, not part of your CSV: edit freely.
# Each bin is (lower, upper], so age 24 is "Under 25" and age 25 is "25-39".
AGE_BINS = [0, 24, 39, 54, float("inf")]
AGE_LABELS = ["Under 25", "25-39", "40-54", "55 and over"]

# Delay categories: (lower, upper]. 60 minutes is Short, 61 is Moderate.
DELAY_BINS = [-float("inf"), 0, 60, 180, 360, float("inf")]
DELAY_LABELS = [
    "No delay (0 min)",
    "Short (>0-60 min)",
    "Moderate (>60-180 min)",
    "Long (>180-360 min)",
    "Very long (>360 min)",
]

# Insights ignore groups smaller than this (tiny groups give unstable rates).
MIN_GROUP = 100

RATE = "Satisfaction rate (%)"

# Colours and chart settings
NAVY = "#0B2545"
NAVY_MID = "#13315C"
TEAL = "#0E9488"
LIGHT = "#F4F7FA"
INK = "#24364B"
MUTED = "#6B7A8F"
GRID = "#E9EDF2"
PALETTE = [TEAL, "#3F6FA8", "#E9A23B", "#8EB5A6", "#8A7FC0", "#D98E73"]
SAT_COLORS = {"Satisfied": TEAL, "Neutral or dissatisfied": NAVY_MID}
FONT = "Arial, sans-serif"
CHART_HEIGHT = 420

PAGES = [
    "Executive Overview",
    "Passenger Analysis",
    "Flight & Service Experience",
    "Business Insights",
]

# ======================================================================
# 2. STYLING
# ======================================================================
APP_CSS = f"""
<style>
  :root {{ color-scheme: light; }}
  .stApp {{ background: {LIGHT}; color: {INK}; }}
  [data-testid="stHeader"] {{ background: rgba(244,247,250,.92); }}
  [data-testid="stSidebar"] {{ background: {NAVY}; }}
  [data-testid="stSidebar"] * {{ color: #F7F9FC; }}
  [data-testid="stSidebar"] [data-baseweb="select"] div {{ color: {INK}; }}
  [data-testid="stSidebar"] [data-baseweb="tag"] {{ background: {TEAL}; }}
  h1, h2, h3 {{ color: {NAVY}; letter-spacing: -.025em; }}
  .hero {{ background: linear-gradient(115deg,{NAVY},{NAVY_MID}); padding: 1.65rem 1.9rem 1.3rem;
    border-radius: 20px; margin: .3rem 0 1.35rem; box-shadow: 0 10px 28px rgba(11,37,69,.16); }}
  .hero h1 {{ color: white; margin: 0; font-size: 2rem; }}
  .hero p {{ color: #CFE0EC; margin: .35rem 0 0; font-size: 1rem; max-width: 70ch; }}
  .hero::after {{ content: ""; display: block; margin-top: 1.1rem; border-top: 2px dashed rgba(255,255,255,.28); }}
  .eyebrow {{ color: #5EEAD4; text-transform: uppercase; letter-spacing: .12em; font-size: .75rem;
    font-weight: 700; margin-bottom: .45rem; }}
  .kpi-card {{ background: #fff; border: 1px solid #E4E9F0; border-top: 4px solid {NAVY_MID};
    border-radius: 16px; padding: 1rem 1.1rem; min-height: 148px; box-shadow: 0 5px 16px rgba(11,37,69,.055); }}
  .kpi-card.accent {{ border-top-color: {TEAL}; }}
  .kpi-label {{ color: {MUTED}; font-size: .9rem; font-weight: 600; }}
  .kpi-value {{ color: {NAVY}; font-size: 2rem; font-weight: 700; line-height: 1.2; margin: .3rem 0 .2rem; }}
  .kpi-card.accent .kpi-value {{ color: {TEAL}; }}
  .kpi-sub {{ color: {INK}; font-size: .88rem; }}
  .kpi-note {{ color: {MUTED}; font-size: .8rem; }}
  .insight {{ background: white; border: 1px solid #E4E9F0; border-left: 4px solid {TEAL};
    border-radius: 12px; padding: .9rem 1rem; margin: .55rem 0; box-shadow: 0 4px 12px rgba(11,37,69,.04); }}
  .section-note {{ color: {MUTED}; margin-top: -.35rem; margin-bottom: 1.1rem; }}
  [data-testid="stPlotlyChart"] {{ background: white; border: 1px solid #E7EBF1; border-radius: 16px;
    padding: .4rem; box-shadow: 0 5px 16px rgba(11,37,69,.045); }}
  .block-container {{ padding-top: 1.6rem; padding-bottom: 2.5rem; max-width: 1500px; }}
  footer {{ visibility: hidden; }}
  @media (max-width: 640px) {{
    .hero h1 {{ font-size: 1.5rem; }}
    .hero {{ padding: 1.2rem 1.2rem 1rem; }}
    .kpi-value {{ font-size: 1.7rem; }}
  }}
</style>
"""


# ======================================================================
# 3. SMALL HELPERS
# ======================================================================
def has(data, *columns):
    """True if every named column exists in the table."""
    return all(column in data.columns for column in columns)


def fmt_fixed(value, decimals=1):
    """Fixed decimals, or 'N/A' when the value is missing."""
    if pd.isna(value):
        return "N/A"
    return f"{value:,.{decimals}f}"


def fmt_trimmed(value, decimals=1):
    """Like fmt_fixed but drops useless zeros (0.0 -> '0', 12.5 -> '12.5')."""
    if pd.isna(value):
        return "N/A"
    text = f"{value:,.{decimals}f}"
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text


def plural(count, word):
    """plural(1, 'record') -> '1 record'; plural(2, 'record') -> '2 records'."""
    return f"{count:,} {word}" + ("" if count == 1 else "s")


# ======================================================================
# 4. DATA FUNCTIONS (pure pandas: no Streamlit or Plotly, easy to test)
# ======================================================================
def find_missing_columns(df):
    """Required columns that are not in the file."""
    return [column for column in OVERVIEW_COLUMNS if column not in df.columns]


def find_blank_rows(df):
    """True for records with no usable Executive Overview value at all
    (satisfaction, departure delay AND arrival delay all missing)."""
    return df[OVERVIEW_COLUMNS].isna().all(axis=1)


def categorise_delay(minutes):
    """Turn delay minutes into the five categories. Missing stays missing."""
    return pd.cut(minutes, bins=DELAY_BINS, labels=DELAY_LABELS, right=True)


def prepare_data(raw):
    """Exclude blank records and add the derived columns (CSV is untouched)."""
    missing = find_missing_columns(raw)
    if missing:
        raise ValueError(f"The CSV is missing required column(s): {', '.join(missing)}")
    blank = find_blank_rows(raw)
    clean = raw.loc[~blank].copy()
    if has(clean, AGE):
        clean[AGE_GROUP] = pd.cut(clean[AGE], bins=AGE_BINS, labels=AGE_LABELS, right=True)
    clean[DEP_BAND] = categorise_delay(clean[DEP])
    clean[ARR_BAND] = categorise_delay(clean[ARR])
    return clean, int(blank.sum())


@st.cache_data(show_spinner="Loading data...")
def load_clean_data(path):
    """Read the CSV and prepare it. Returns (data, rows_in_file, blank_rows_excluded)."""
    raw = pd.read_csv(path)
    clean, excluded = prepare_data(raw)
    return clean, len(raw), excluded


def calculate_kpis(data):
    """Every KPI is calculated from the data. Nothing is hard-coded."""
    satisfaction = data[SAT].dropna()
    departure = data[DEP].dropna()
    arrival = data[ARR].dropna()
    satisfied_count = int((satisfaction == SATISFIED).sum())
    return {
        "total_passengers": len(data),
        "satisfied_count": satisfied_count,
        "satisfaction_n": len(satisfaction),
        "satisfaction_rate": (
            satisfied_count / len(satisfaction) * 100 if len(satisfaction) else float("nan")
        ),
        "departure_n": len(departure),
        "departure_mean": departure.mean(),
        "departure_median": departure.median(),
        "arrival_n": len(arrival),
        "arrival_mean": arrival.mean(),
        "arrival_median": arrival.median(),
    }


def build_satisfaction_table(data):
    """Count and percentage per satisfaction answer (missing excluded)."""
    counts = data[SAT].dropna().value_counts()
    table = counts.rename_axis("Response").reset_index(name="Passengers")
    table["Response"] = table["Response"].astype(str).str.capitalize()
    table["Percent"] = table["Passengers"] / table["Passengers"].sum() * 100
    table["Valid responses"] = int(table["Passengers"].sum())
    return table


def build_delay_table(data):
    """Passengers and % per delay category for departure and arrival.
    Each percentage uses its OWN valid-observation count as denominator."""
    rows = []
    for delay_type, column in [("Departure", DEP), ("Arrival", ARR)]:
        valid = data[column].dropna()
        total = len(valid)
        categories = categorise_delay(valid)
        for label in DELAY_LABELS:
            count = int((categories == label).sum())
            rows.append(
                {
                    "Delay type": delay_type,
                    "Category": label,
                    "Passengers": count,
                    "Percent": count / total * 100 if total else 0.0,
                    "Valid observations": total,
                }
            )
    return pd.DataFrame(rows)


def counts_table(data, column):
    """Passengers and share per value of a categorical column (missing excluded)."""
    series = data[column].dropna()
    counts = series.value_counts()
    if isinstance(data[column].dtype, pd.CategoricalDtype):
        counts = counts.reindex(data[column].cat.categories, fill_value=0)
        counts = counts[counts > 0]
    table = counts.rename_axis(column).reset_index(name="Passengers")
    table[column] = table[column].astype(str)
    table["Share"] = table["Passengers"] / table["Passengers"].sum() * 100
    return table


def rate_by_group(data, group):
    """Satisfaction rate per group. Denominator = valid satisfaction answers in
    that group. Ordered categories keep their order; others sort high to low."""
    valid = data.dropna(subset=[group, SAT])
    if valid.empty:
        return pd.DataFrame(columns=[group, "Passengers", "Satisfied", RATE])
    flag = valid[SAT].eq(SATISFIED)
    table = flag.groupby(valid[group], observed=True).agg(["size", "sum"]).reset_index()
    table.columns = [group, "Passengers", "Satisfied"]
    table["Passengers"] = table["Passengers"].astype(int)
    table["Satisfied"] = table["Satisfied"].astype(int)
    table[RATE] = table["Satisfied"] / table["Passengers"] * 100
    if not isinstance(valid[group].dtype, pd.CategoricalDtype):
        table = table.sort_values(RATE, ascending=False).reset_index(drop=True)
    table[group] = table[group].astype(str)
    return table


def service_rating_table(data):
    """Mean rating per service. Ratings equal to NOT_APPLICABLE_RATING and missing
    values are excluded from means and counted separately."""
    rows = []
    is_satisfied = data[SAT].eq(SATISFIED)
    is_not_satisfied = data[SAT].notna() & ~is_satisfied
    for service in SERVICE_COLUMNS:
        if service not in data.columns:
            continue
        column = data[service]
        usable = column.notna()
        if NOT_APPLICABLE_RATING is not None:
            usable = usable & (column != NOT_APPLICABLE_RATING)
        mean_sat = column[usable & is_satisfied].mean()
        mean_not = column[usable & is_not_satisfied].mean()
        rows.append(
            {
                "Service": service,
                "Mean rating": column[usable].mean(),
                "Valid ratings": int(usable.sum()),
                "Not applicable (0)": int((column == 0).sum()) if NOT_APPLICABLE_RATING is not None else 0,
                "Missing": int(column.isna().sum()),
                "Mean (satisfied)": mean_sat,
                "Mean (neutral or dissatisfied)": mean_not,
                "Gap": mean_sat - mean_not,
            }
        )
    return pd.DataFrame(rows)


def rating_distribution(data, service):
    """Passengers giving each rating 1-5 for one service (N/A and missing excluded)."""
    column = data[service]
    valid = column[column.isin([1, 2, 3, 4, 5])].astype(int)
    counts = valid.value_counts().reindex([1, 2, 3, 4, 5], fill_value=0)
    table = counts.rename_axis("Rating").reset_index(name="Passengers")
    table["Rating"] = table["Rating"].astype(str)
    total = table["Passengers"].sum()
    table["Share"] = table["Passengers"] / total * 100 if total else 0.0
    table["Valid ratings"] = int(total)
    return table


# ---- Insights: every sentence below is calculated from the filtered data ----
SEGMENTS = [
    (CLASS, "travel class"),
    (TRAVEL, "type of travel"),
    (CUSTOMER, "customer type"),
    (GENDER, "gender"),
    (AGE_GROUP, "age group"),
]
DELAY_SEGMENTS = [(DEP_BAND, "departure delay band"), (ARR_BAND, "arrival delay band")]


def eligible_groups(data, group):
    """Groups with at least MIN_GROUP valid answers."""
    if group not in data.columns:
        return pd.DataFrame()
    table = rate_by_group(data, group)
    return table[table["Passengers"] >= MIN_GROUP].reset_index(drop=True)


def compute_insights(data):
    """Return a list of HTML sentences, each backed by a calculation."""
    insights = []
    for group, label in SEGMENTS + DELAY_SEGMENTS:
        table = eligible_groups(data, group)
        if len(table) < 2:
            continue
        high = table.loc[table[RATE].idxmax()]
        low = table.loc[table[RATE].idxmin()]
        insights.append(
            f"By <b>{label}</b>, the satisfaction rate is highest for <b>{high[group]}</b> "
            f"({high[RATE]:.1f}%, n = {int(high['Passengers']):,}) and lowest for "
            f"<b>{low[group]}</b> ({low[RATE]:.1f}%, n = {int(low['Passengers']):,})."
        )

    services = service_rating_table(data)
    if not services.empty and services["Mean rating"].notna().any():
        best = services.loc[services["Mean rating"].idxmax()]
        worst = services.loc[services["Mean rating"].idxmin()]
        insights.append(
            f"Highest-rated service: <b>{best['Service']}</b> (mean {best['Mean rating']:.2f}, "
            f"{int(best['Valid ratings']):,} valid ratings). Lowest-rated: <b>{worst['Service']}</b> "
            f"(mean {worst['Mean rating']:.2f}, {int(worst['Valid ratings']):,} valid ratings)."
        )
        if services["Gap"].notna().any():
            widest = services.loc[services["Gap"].idxmax()]
            insights.append(
                f"The widest rating gap between satisfied and neutral/dissatisfied passengers is for "
                f"<b>{widest['Service']}</b>: {widest['Mean (satisfied)']:.2f} vs "
                f"{widest['Mean (neutral or dissatisfied)']:.2f} (gap {widest['Gap']:.2f})."
            )

    satisfied_delay = data.loc[data[SAT].eq(SATISFIED), ARR].mean()
    other_delay = data.loc[data[SAT].notna() & ~data[SAT].eq(SATISFIED), ARR].mean()
    if pd.notna(satisfied_delay) and pd.notna(other_delay):
        insights.append(
            f"Average arrival delay is <b>{satisfied_delay:.1f} min</b> for satisfied passengers and "
            f"<b>{other_delay:.1f} min</b> for neutral or dissatisfied passengers."
        )
    pairs = data[[DEP, ARR]].dropna()
    if len(pairs) > 2:
        insights.append(
            f"Departure and arrival delays have a Pearson correlation of "
            f"<b>{pairs[DEP].corr(pairs[ARR]):.2f}</b> (n = {len(pairs):,} flights with both values)."
        )
    return insights


def compute_focus_areas(data):
    """Rule-based 'where to look first' notes, each tied to a calculated number."""
    areas = []
    services = service_rating_table(data)
    if not services.empty:
        lowest = services.nsmallest(3, "Mean rating")
        areas.append(
            "Services with the lowest mean ratings: "
            + "; ".join(f"<b>{row['Service']}</b> ({row['Mean rating']:.2f})" for _, row in lowest.iterrows())
            + "."
        )
        gaps = services.dropna(subset=["Gap"]).nlargest(3, "Gap")
        if not gaps.empty:
            areas.append(
                "Services whose ratings differ most between satisfied and other passengers: "
                + "; ".join(f"<b>{row['Service']}</b> (gap {row['Gap']:.2f})" for _, row in gaps.iterrows())
                + "."
            )
    candidates = []
    for group, label in SEGMENTS:
        table = eligible_groups(data, group)
        for _, row in table.iterrows():
            candidates.append((row[RATE], label, row[group], int(row["Passengers"])))
    if candidates:
        rate, label, value, n = min(candidates, key=lambda item: item[0])
        areas.append(
            f"Passenger segment with the lowest satisfaction rate: <b>{value}</b> ({label}) at "
            f"{rate:.1f}% (n = {n:,})."
        )
    return areas


# ======================================================================
# 5. CHART HELPERS
# ======================================================================
def chart_layout(fig, height=CHART_HEIGHT, legend="none"):
    """One shared look for every chart.

    legend: "none" | "top" (above the plot, below the title) | "bottom".
    Margins reserve room for the title and legend, and automargin lets Plotly
    add space for axis labels and titles, so nothing is clipped.
    """
    fig.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"family": FONT, "color": INK, "size": 12},
        title={
            "font": {"size": 16, "color": NAVY},
            "x": 0.03,
            "xanchor": "left",
            "y": 0.97,
            "yanchor": "top",
        },
        hoverlabel={"bgcolor": "white", "font": {"color": NAVY}},
    )
    if legend == "top":
        fig.update_layout(
            showlegend=True,
            margin={"l": 24, "r": 24, "t": 96, "b": 24},
            legend={"orientation": "h", "yanchor": "bottom", "y": 1.02, "xanchor": "left", "x": 0,
                    "title": {"text": ""}, "font": {"size": 13}},
        )
    elif legend == "bottom":
        fig.update_layout(
            showlegend=True,
            margin={"l": 24, "r": 24, "t": 64, "b": 96},
            legend={"orientation": "h", "yanchor": "top", "y": -0.04, "xanchor": "center", "x": 0.5,
                    "title": {"text": ""}, "font": {"size": 13}},
        )
    else:
        fig.update_layout(showlegend=False, margin={"l": 24, "r": 24, "t": 64, "b": 24})
    fig.update_xaxes(showgrid=False, zeroline=False, automargin=True, title_standoff=12,
                     title_font_color=MUTED)
    fig.update_yaxes(gridcolor=GRID, zeroline=False, automargin=True, title_standoff=12,
                     title_font_color=MUTED)
    return fig


def show_chart(fig, key, height=CHART_HEIGHT, legend="none"):
    st.plotly_chart(
        chart_layout(fig, height=height, legend=legend),
        width="stretch",
        key=key,
        theme=None,
        config={"displayModeBar": False},
    )


def satisfaction_donut(table, rate, key):
    fig = px.pie(
        table, names="Response", values="Passengers", hole=0.62, color="Response",
        color_discrete_map=SAT_COLORS, custom_data=["Valid responses"],
        title="Passenger satisfaction",
    )
    fig.update_traces(
        sort=False, textinfo="percent", textfont_size=15, textfont_color="white",
        marker_line_color="white", marker_line_width=3,
        hovertemplate=(
            "<b>%{label}</b><br>Passengers: %{value:,}<br>"
            "Share: %{percent:.1%} of %{customdata[0]:,} valid responses<extra></extra>"
        ),
    )
    if pd.notna(rate):
        fig.add_annotation(text=f"<b>{rate:.1f}%</b><br>satisfied", x=0.5, y=0.5,
                           showarrow=False, font={"size": 22, "color": NAVY})
    show_chart(fig, key, legend="bottom")


def delay_overview_chart(table, key):
    fig = px.bar(
        table, x="Category", y="Percent", color="Delay type", barmode="group",
        category_orders={"Category": DELAY_LABELS, "Delay type": ["Departure", "Arrival"]},
        color_discrete_map={"Departure": NAVY_MID, "Arrival": TEAL},
        custom_data=["Passengers", "Valid observations"],
        title="Flight delay overview",
    )
    fig.update_traces(
        texttemplate="%{y:.1f}%", textposition="outside", textfont_size=11, cliponaxis=False,
        hovertemplate=(
            "<b>%{x}</b><br>%{fullData.name} delay<br>Passengers: %{customdata[0]:,}<br>"
            "Share: %{y:.1f}% of %{customdata[1]:,} valid observations<extra></extra>"
        ),
    )
    top = table["Percent"].max()
    fig.update_layout(bargap=0.2, bargroupgap=0.06)
    fig.update_xaxes(
        title_text="", tickmode="array", tickvals=DELAY_LABELS,
        ticktext=[label.replace(" (", "<br>(") for label in DELAY_LABELS], tickfont_size=12,
    )
    fig.update_yaxes(title_text="Share of passengers (%)", ticksuffix="%",
                     range=[0, top * 1.2 if top > 0 else 1])
    show_chart(fig, key, legend="top")


def counts_chart(data, column, title, key, horizontal=False):
    if not has(data, column):
        return
    table = counts_table(data, column)
    if table.empty:
        return
    order = table[column].tolist()
    if horizontal:
        fig = px.bar(table, x="Passengers", y=column, orientation="h", title=title,
                     custom_data=["Share"], text="Passengers", category_orders={column: order})
        fig.update_traces(marker_color=TEAL)
        fig.update_yaxes(autorange="reversed", title_text="")
        fig.update_xaxes(title_text="Passengers")
    else:
        fig = px.bar(table, x=column, y="Passengers", title=title, custom_data=["Share"],
                     color=column, color_discrete_sequence=PALETTE, text="Passengers",
                     category_orders={column: order})
        fig.update_xaxes(title_text="")
    fig.update_traces(
        textposition="outside", cliponaxis=False, texttemplate="%{text:,}",
        hovertemplate=f"<b>%{{{'y' if horizontal else 'x'}}}</b><br>Passengers: %{{{'x' if horizontal else 'y'}:,}}"
                      "<br>Share: %{customdata[0]:.1f}%<extra></extra>",
    )
    show_chart(fig, key)


def numeric_hist(data, column, title, key, nbins=30, color=TEAL):
    valid = data[column].dropna() if column in data else pd.Series(dtype=float)
    if valid.empty:
        st.info(f"No valid values available for {column}.")
        return
    fig = px.histogram(data, x=column, nbins=nbins, title=title, color_discrete_sequence=[color])
    fig.update_traces(
        marker_line_color="white", marker_line_width=1,
        hovertemplate=f"{column}: %{{x}}<br>Passengers: %{{y:,}}<extra></extra>",
    )
    fig.update_layout(bargap=0.04)
    fig.update_xaxes(title_text=column)
    fig.update_yaxes(title_text="Passengers")
    show_chart(fig, key)


def rate_chart(data, group, title, key, horizontal=False):
    """Satisfaction rate per group, with counts and denominator on hover."""
    if not has(data, group):
        return
    table = rate_by_group(data, group)
    if table.empty:
        return
    order = table[group].tolist()
    hover_tail = (
        "<br>Satisfied: %{customdata[0]:,} of %{customdata[1]:,} passengers<extra></extra>"
    )
    if horizontal:
        fig = px.bar(table, x=RATE, y=group, orientation="h", title=title,
                     custom_data=["Satisfied", "Passengers"], category_orders={group: order})
        fig.update_traces(hovertemplate="<b>%{y}</b><br>Satisfaction rate: %{x:.1f}%" + hover_tail)
        fig.update_xaxes(range=[0, 100], ticksuffix="%", title_text="Satisfaction rate (%)")
        fig.update_yaxes(autorange="reversed", title_text="")
    else:
        fig = px.bar(table, x=group, y=RATE, title=title,
                     custom_data=["Satisfied", "Passengers"], category_orders={group: order})
        fig.update_traces(hovertemplate="<b>%{x}</b><br>Satisfaction rate: %{y:.1f}%" + hover_tail)
        fig.update_yaxes(range=[0, 100], ticksuffix="%", title_text="Satisfaction rate (%)")
        fig.update_xaxes(title_text="")
    fig.update_traces(marker_color=TEAL, texttemplate="%{" + ("x" if horizontal else "y") + ":.1f}%",
                      textposition="outside", cliponaxis=False)
    show_chart(fig, key)


def mean_rating_chart(table, key):
    ordered = table.sort_values("Mean rating")  # lowest first = bottom of chart
    fig = px.bar(ordered, x="Mean rating", y="Service", orientation="h",
                 title="Average rating by service (1-5 scale)", custom_data=["Valid ratings"],
                 category_orders={"Service": ordered["Service"].tolist()})
    fig.update_traces(
        marker_color=TEAL, texttemplate="%{x:.2f}", textposition="outside", cliponaxis=False,
        hovertemplate="<b>%{y}</b><br>Mean rating: %{x:.2f}<br>Valid ratings: %{customdata[0]:,}<extra></extra>",
    )
    fig.update_xaxes(range=[0, 5.5], dtick=1, title_text="Mean rating")
    fig.update_yaxes(title_text="")
    show_chart(fig, key, height=560)


def rating_by_satisfaction_chart(table, key):
    ordered = table.sort_values("Mean rating")["Service"].tolist()
    # Keep only the columns being reshaped, so the new "Mean rating" column
    # cannot clash with the existing "Mean rating" column of the full table.
    long = table[["Service", "Mean (satisfied)", "Mean (neutral or dissatisfied)"]].melt(
        id_vars="Service", var_name="Group", value_name="Mean rating",
    )
    long["Group"] = long["Group"].map(
        {"Mean (satisfied)": "Satisfied", "Mean (neutral or dissatisfied)": "Neutral or dissatisfied"}
    )
    fig = px.bar(
        long, x="Mean rating", y="Service", color="Group", orientation="h", barmode="group",
        title="Average rating: satisfied vs neutral or dissatisfied passengers",
        category_orders={"Service": ordered, "Group": ["Satisfied", "Neutral or dissatisfied"]},
        color_discrete_map=SAT_COLORS,
    )
    fig.update_traces(hovertemplate="<b>%{y}</b><br>%{fullData.name}: %{x:.2f}<extra></extra>")
    fig.update_xaxes(range=[0, 5], dtick=1, title_text="Mean rating")
    fig.update_yaxes(title_text="")
    show_chart(fig, key, height=700, legend="top")


def rating_distribution_chart(table, service, key):
    fig = px.bar(table, x="Rating", y="Passengers", title=f"Rating distribution: {service}",
                 custom_data=["Share", "Valid ratings"], text="Passengers",
                 color_discrete_sequence=[TEAL], category_orders={"Rating": ["1", "2", "3", "4", "5"]})
    fig.update_traces(
        textposition="outside", cliponaxis=False, texttemplate="%{text:,}",
        hovertemplate=("Rating %{x}<br>Passengers: %{y:,}<br>"
                       "Share: %{customdata[0]:.1f}% of %{customdata[1]:,} valid ratings<extra></extra>"),
    )
    fig.update_xaxes(title_text="Rating (1 = lowest, 5 = highest)")
    fig.update_yaxes(title_text="Passengers")
    show_chart(fig, key)


# ======================================================================
# 6. PAGE PIECES
# ======================================================================
def title_block(title, description):
    st.markdown(f"## {title}")
    st.markdown(f'<div class="section-note">{description}</div>', unsafe_allow_html=True)


def add_insight(message):
    st.markdown(f'<div class="insight">{message}</div>', unsafe_allow_html=True)


def kpi_card(label, value, lines=(), accent=False):
    """HTML for one KPI card. Kept on one line: Markdown treats indented HTML as code."""
    css_class = "kpi-card accent" if accent else "kpi-card"
    body = "".join(f'<div class="{cls}">{text}</div>' for cls, text in lines)
    return (
        f'<div class="{css_class}"><div class="kpi-label">{label}</div>'
        f'<div class="kpi-value">{value}</div>{body}</div>'
    )


def show_kpi(column, label, value, lines=(), accent=False):
    column.markdown(kpi_card(label, value, lines, accent), unsafe_allow_html=True)


def render_hero():
    st.markdown(
        '<div class="hero"><div class="eyebrow">Aviation data analytics</div>'
        "<h1>Airline Passenger Satisfaction Dashboard</h1>"
        "<p>How satisfied are our passengers, which services matter most to them, and how "
        "punctual are our flights? Explore satisfaction, passenger profiles, service ratings "
        "and delays.</p></div>",
        unsafe_allow_html=True,
    )


def apply_sidebar_filters(df):
    """Sidebar filters. Untouched filters never remove any rows."""
    st.sidebar.markdown("### Filter passengers")
    filtered = df
    for column, label in [
        (GENDER, "Gender"), (CUSTOMER, "Customer type"), (TRAVEL, "Type of travel"),
        (CLASS, "Class"), (AGE_GROUP, "Age group"),
    ]:
        if column not in df.columns:
            continue
        if isinstance(df[column].dtype, pd.CategoricalDtype):
            options = [str(value) for value in df[column].cat.categories]
        else:
            options = sorted(df[column].dropna().astype(str).unique())
        selected = st.sidebar.multiselect(label, options, default=options, key=f"filter_{column}")
        if set(selected) != set(options):
            filtered = filtered[filtered[column].astype("string").isin(selected)]
    st.sidebar.caption(f"Showing **{len(filtered):,}** of **{len(df):,}** passengers")
    st.sidebar.caption("Age groups (set in app.py): under 25, 25-39, 40-54, 55 and over.")
    return filtered


# ======================================================================
# 7. PAGES
# ======================================================================
def page_overview(data, total_rows, excluded, all_rows):
    title_block("Executive Overview", "Headline satisfaction and punctuality figures for the selected passengers.")
    kpis = calculate_kpis(data)

    cols = st.columns(4, gap="medium")
    total_lines = [("kpi-note", f"{plural(excluded, 'blank record')} excluded from {total_rows:,} rows")]
    if len(data) != all_rows:
        total_lines.append(("kpi-note", f"Filters active: {len(data):,} of {all_rows:,}"))
    show_kpi(cols[0], "Total passengers", f"{kpis['total_passengers']:,}", total_lines)
    show_kpi(
        cols[1], "Passenger satisfaction rate", f"{fmt_fixed(kpis['satisfaction_rate'])}%",
        [("kpi-note", f"{kpis['satisfied_count']:,} of {kpis['satisfaction_n']:,} valid responses")],
         accent=True,
    )
    show_kpi(
        cols[2], "Average departure delay", f"{fmt_fixed(kpis['departure_mean'])} min",
        [("kpi-sub", f"Median: {fmt_trimmed(kpis['departure_median'])} min"),
         ("kpi-note", f"Based on {kpis['departure_n']:,} valid flights")],
    )
    show_kpi(
        cols[3], "Average arrival delay", f"{fmt_fixed(kpis['arrival_mean'])} min",
        [("kpi-sub", f"Median: {fmt_trimmed(kpis['arrival_median'])} min"),
         ("kpi-note", f"Based on {kpis['arrival_n']:,} valid flights")],
    )
    st.write("")

    left, right = st.columns([4, 6], gap="large")
    with left:
        satisfaction_donut(build_satisfaction_table(data), kpis["satisfaction_rate"], "overview_donut")
    with right:
        delay_overview_chart(build_delay_table(data), "overview_delay")
    st.caption("Delay percentages use each delay type's own count of valid observations as the denominator.")

    negatives = int((data[DEP] < 0).sum() + (data[ARR] < 0).sum())
    lines = [
        f"- **Rows in the CSV file:** {total_rows:,} (the file is only read, never modified).",
        f"- **Blank records excluded:** {excluded:,}. A record is blank when satisfaction, departure "
        "delay and arrival delay are all missing.",
        f"- **Passengers analysed:** {len(data):,}. Partly filled records are kept; each metric "
        "skips only its own missing values.",
        f"- **Satisfaction rate:** {kpis['satisfaction_n']:,} valid responses "
        f"({len(data) - kpis['satisfaction_n']:,} missing).",
        f"- **Departure delay:** {kpis['departure_n']:,} valid observations "
        f"({len(data) - kpis['departure_n']:,} missing).",
        f"- **Arrival delay:** {kpis['arrival_n']:,} valid observations "
        f"({len(data) - kpis['arrival_n']:,} missing).",
        "- **Delay categories** are built from the raw minute columns; the upper bound is inclusive "
        "(60 min is Short, 61 min is Moderate).",
    ]
    if negatives:
        lines.append(f"- **Warning:** {negatives:,} negative delay value(s) are counted as 'No delay'.")
    with st.expander("Data notes: how these numbers are calculated"):
        st.markdown("\n".join(lines))


def page_passengers(data):
    title_block("Passenger Analysis", "Who is travelling, how they travel, and how satisfaction differs between groups.")

    cols = st.columns(3, gap="medium")
    if has(data, AGE) and data[AGE].notna().any():
        show_kpi(cols[0], "Average age", f"{fmt_fixed(data[AGE].mean())} yr",
                 [("kpi-sub", f"Median: {fmt_trimmed(data[AGE].median())} yr"),
                  ("kpi-note", f"Based on {int(data[AGE].notna().sum()):,} passengers")])
    if has(data, DISTANCE) and data[DISTANCE].notna().any():
        show_kpi(cols[1], "Average flight distance", fmt_fixed(data[DISTANCE].mean(), 0),
                 [("kpi-sub", f"Median: {fmt_trimmed(data[DISTANCE].median(), 0)}"),
                  ("kpi-note", "Units as recorded in the dataset")])
    if has(data, CLASS) and data[CLASS].notna().any():
        counts = data[CLASS].value_counts()
        show_kpi(cols[2], "Most common travel class", str(counts.idxmax()),
                 [("kpi-sub", f"{counts.max() / counts.sum() * 100:.1f}% of passengers"),
                  ("kpi-note", f"{int(counts.max()):,} of {int(counts.sum()):,}")], accent=True)
    st.write("")

    st.markdown("### Passenger profile")
    left, right = st.columns(2, gap="large")
    with left:
        numeric_hist(data, AGE, "Age distribution", "pax_age")
        counts_chart(data, GENDER, "Passengers by gender", "pax_gender")
    with right:
        counts_chart(data, AGE_GROUP, "Passengers by age group", "pax_age_group")
        counts_chart(data, CUSTOMER, "Passengers by customer type", "pax_customer")

    st.markdown("### Travel characteristics")
    left, right = st.columns(2, gap="large")
    with left:
        counts_chart(data, TRAVEL, "Passengers by type of travel", "pax_travel")
    with right:
        counts_chart(data, CLASS, "Passengers by travel class", "pax_class")
    numeric_hist(data, DISTANCE, "Flight distance distribution", "pax_distance", nbins=40, color="#3F6FA8")

    st.markdown("### Satisfaction by passenger segment")
    st.markdown('<div class="section-note">Share of passengers who are satisfied, per group. '
                "Hover to see the counts behind each rate.</div>", unsafe_allow_html=True)
    left, right = st.columns(2, gap="large")
    with left:
        rate_chart(data, CLASS, "Satisfaction rate by travel class", "rate_class")
        rate_chart(data, CUSTOMER, "Satisfaction rate by customer type", "rate_customer")
        rate_chart(data, AGE_GROUP, "Satisfaction rate by age group", "rate_age")
    with right:
        rate_chart(data, TRAVEL, "Satisfaction rate by type of travel", "rate_travel")
        rate_chart(data, GENDER, "Satisfaction rate by gender", "rate_gender")


def page_service(data):
    title_block("Flight & Service Experience",
                "How passengers rate each service, how ratings relate to satisfaction, and how delays relate to satisfaction.")
    services = service_rating_table(data)
    if services.empty:
        st.info("No service rating columns were found in the dataset.")
    else:
        if NOT_APPLICABLE_RATING is not None:
            na_total = int(services["Not applicable (0)"].sum())
            add_insight(
                f"<b>About ratings of 0:</b> the scale is 1-5, but some columns also contain 0 "
                f"({na_total:,} such ratings across all services). They are treated as "
                "<b>not applicable</b> and left out of every average. This is an assumption based on the "
                "public documentation of this dataset; your CSV does not define 0, so please confirm it "
                "against your source. The counts per service are in the table at the bottom of this section."
            )
        mean_rating_chart(services, "svc_mean")
        rating_by_satisfaction_chart(services, "svc_by_sat")

        st.markdown("### Explore one service")
        choice = st.selectbox("Choose a service", services["Service"].tolist(), key="svc_choice")
        dist = rating_distribution(data, choice)
        left, right = st.columns([6, 4], gap="large")
        with left:
            rating_distribution_chart(dist, choice, "svc_dist")
        with right:
            row = services[services["Service"] == choice].iloc[0]
            show_kpi(right, "Average rating", fmt_fixed(row["Mean rating"], 2),
                     [("kpi-note", f"{int(row['Valid ratings']):,} valid ratings")], accent=True)
            st.write("")
            na_text = (f"{int(row['Not applicable (0)']):,} rated 0 (not applicable), "
                       if NOT_APPLICABLE_RATING is not None else "")
            add_insight(f"{na_text}{int(row['Missing']):,} missing. "
                        f"Mean for satisfied passengers: <b>{fmt_fixed(row['Mean (satisfied)'], 2)}</b>; "
                        f"for neutral or dissatisfied: <b>{fmt_fixed(row['Mean (neutral or dissatisfied)'], 2)}</b>.")

    st.markdown("### Delays and satisfaction")
    st.markdown('<div class="section-note">Satisfaction rate by delay band. Each rate uses the valid '
                "satisfaction answers within that band; hover for counts. Small bands can be unstable.</div>",
                unsafe_allow_html=True)
    left, right = st.columns(2, gap="large")
    with left:
        rate_chart(data, DEP_BAND, "Satisfaction rate by departure delay", "delay_dep_rate", horizontal=True)
    with right:
        rate_chart(data, ARR_BAND, "Satisfaction rate by arrival delay", "delay_arr_rate", horizontal=True)

    if not services.empty:
        with st.expander("Rating data table (valid, not applicable and missing counts)"):
            table = services[["Service", "Mean rating", "Valid ratings", "Not applicable (0)", "Missing"]].copy()
            table["Mean rating"] = table["Mean rating"].round(2)
            st.dataframe(table, hide_index=True)


def page_insights(data):
    title_block("Business Insights",
                "Findings recalculated from the selected passengers. They describe associations, not causes.")
    st.markdown("### Key findings")
    insights = compute_insights(data)
    if not insights:
        st.info("Not enough data in the current selection to calculate insights.")
    for message in insights:
        add_insight(message)
    st.caption(f"Groups with fewer than {MIN_GROUP} valid answers are left out of highest/lowest comparisons.")

    st.markdown("### Where to look first")
    st.markdown('<div class="section-note">Starting points drawn directly from the numbers above. '
                "They show where differences are largest; they do not prove what causes them.</div>",
                unsafe_allow_html=True)
    for message in compute_focus_areas(data):
        add_insight(message)
    st.caption("Descriptive analysis only. Ratings and satisfaction are associated in this dataset; "
               "that does not show that improving a service would change satisfaction.")


# ======================================================================
# 8. MAIN APP
# ======================================================================
def main():
    st.set_page_config(
        page_title="Airline Passenger Satisfaction Dashboard",
        page_icon="✈️",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.markdown(APP_CSS, unsafe_allow_html=True)

    if not DATA_PATH.exists():
        render_hero()
        st.error(f"Dataset not found. Expected the file at: {DATA_PATH}\n\n"
                 "Place airline_cleaned.csv inside the 'data' folder next to app.py.")
        st.stop()
    try:
        df, total_rows, excluded = load_clean_data(str(DATA_PATH))
    except ValueError as exc:
        render_hero()
        st.error(str(exc))
        st.stop()
    except (pd.errors.ParserError, UnicodeDecodeError, OSError) as exc:
        render_hero()
        st.error(f"Could not read the dataset: {exc}")
        st.stop()

    st.sidebar.markdown("# ✈️ Airline Analytics")
    st.sidebar.caption("Passenger satisfaction · descriptive exploration")
    st.sidebar.markdown("---")
    page = st.sidebar.radio("DASHBOARD", PAGES)
    st.sidebar.markdown("---")
    filtered = apply_sidebar_filters(df)

    render_hero()
    if filtered.empty:
        st.warning("No passengers match the selected filters. Adjust the sidebar filters to continue.")
        st.stop()

    if page == "Executive Overview":
        page_overview(filtered, total_rows, excluded, len(df))
    elif page == "Passenger Analysis":
        page_passengers(filtered)
    elif page == "Flight & Service Experience":
        page_service(filtered)
    else:
        page_insights(filtered)

    st.markdown("---")
    st.caption("Airline Passenger Satisfaction Dashboard · Built with Streamlit, Pandas and Plotly · "
               "Source: airline_cleaned.csv")


if __name__ == "__main__":
    main()
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from footy_data_analysis import FootyDataAnalysis

class FootyDash:
    def __init__(self):
        self.footy_data_analysis = FootyDataAnalysis()

    # --------------------------------------------------
    # Page configuration
    # --------------------------------------------------

    st.set_page_config(
        page_title="Football Performance Analytics",
        page_icon="⚽",
        layout="wide"
    )

    st.title("⚽ Football Performance Analytics")
    st.caption(
        "Analyze player performance against expected goals "
        "and expected assists."
    )


    # --------------------------------------------------
    # Load and process data
    # --------------------------------------------------

    @st.cache_data
    def load_data():
        footy_data = FootyDataAnalysis()

        leagues = [
            "ENG-Premier League",
            "ITA-Serie A"
        ]

        seasons = [
            "2023/2024",
            "2024/2025",
            "2025/2026"
        ]

        df = footy_data.get_dataframe(leagues, seasons)

        if df.empty:
            return None, None

        goal_df, assist_df = footy_data.filter_and_analyze_data(df)

        goal_df, assist_df = footy_data.group_and_aggregate(
            [goal_df, assist_df]
        )

        return goal_df, assist_df


    goal_df, assist_df = load_data()


    if goal_df is None or assist_df is None:
        st.error(
            "No football data available. "
            "Please fetch the data before running the dashboard."
        )
        st.stop()


    # --------------------------------------------------
    # Sidebar controls
    # --------------------------------------------------

    st.sidebar.header("Dashboard Settings")

    view = st.sidebar.radio(
        "Analysis View",
        ["Goals", "Assists"],
        horizontal=True
    )


    # --------------------------------------------------
    # Select analysis dataset and metrics
    # --------------------------------------------------

    if view == "Goals":
        analysis_df = goal_df.copy()

        actual_col = "goals"
        expected_col = "xg"
        rate_col = "goal_conversion_rate"
        efficiency_col = "goals_per_shot"

        volume_label = "Goals"
        expected_label = "Expected Goals (xG)"
        rate_label = "Goals / xG"
        efficiency_label = "Goals per Shot"

    else:
        analysis_df = assist_df.copy()

        actual_col = "assists"
        expected_col = "xa"
        rate_col = "assist_conversion_rate"
        efficiency_col = "assists_per_key_pass"

        volume_label = "Assists"
        expected_label = "Expected Assists (xA)"
        rate_label = "Assists / xA"
        efficiency_label = "Assists per Key Pass"


    # --------------------------------------------------
    # Calculate actual vs. expected performance
    # --------------------------------------------------

    analysis_df["actual_minus_expected"] = (
        analysis_df[actual_col] - analysis_df[expected_col]
    )


    # --------------------------------------------------
    # Sidebar filters
    # --------------------------------------------------

    st.sidebar.subheader("Player Filters")

    min_minutes = st.sidebar.slider(
        "Minimum minutes played",
        min_value=0,
        max_value=3000,
        value=500,
        step=100
    )

    min_expected = st.sidebar.slider(
        f"Minimum {expected_col.upper()}",
        min_value=0.0,
        max_value=30.0,
        value=5.0,
        step=1.0
    )

    filtered_df = analysis_df[
        (analysis_df["minutes"] >= min_minutes)
        & (analysis_df[expected_col] >= min_expected)
    ].copy()


    # --------------------------------------------------
    # Summary metrics
    # --------------------------------------------------

    st.subheader(f"{volume_label} Overview")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Players Analyzed",
        len(filtered_df)
    )

    col2.metric(
        f"Total {volume_label}",
        int(filtered_df[actual_col].sum())
    )

    col3.metric(
        f"Total {expected_col.upper()}",
        round(filtered_df[expected_col].sum(), 2)
    )


    # --------------------------------------------------
    # Scatter plot
    # --------------------------------------------------

    st.subheader(f"{volume_label} vs. {expected_label}")

    if filtered_df.empty:
        st.info(
            "No players match the selected filters. "
            "Try lowering the minimum minutes or expected-value threshold."
        )

    else:
        max_value = max(
            filtered_df[actual_col].max(),
            filtered_df[expected_col].max(),
            1
        ) * 1.05

        fig = px.scatter(
            filtered_df,
            x=expected_col,
            y=actual_col,
            hover_name="player",
            hover_data={
                "player_id": True,
                "minutes": True,
                "actual_minus_expected": ":.2f",
                rate_col: ":.2f",
                efficiency_col: ":.3f"
            },
            labels={
                expected_col: expected_label,
                actual_col: f"Actual {volume_label}",
                "actual_minus_expected": "Actual - Expected",
                rate_col: rate_label,
                efficiency_col: efficiency_label
            },
            title=f"{volume_label} Performance by Player"
        )

        # Reference line: actual output equals expected output
        fig.add_trace(
            go.Scatter(
                x=[0, max_value],
                y=[0, max_value],
                mode="lines",
                name="Actual = Expected",
                line=dict(dash="dash")
            )
        )

        fig.update_layout(
            xaxis_title=expected_label,
            yaxis_title=f"Actual {volume_label}",
            xaxis_range=[0, max_value],
            yaxis_range=[0, max_value],
            height=600,
            hovermode="closest"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


        # --------------------------------------------------
        # Player rankings
        # --------------------------------------------------

        st.subheader(f"{volume_label} Player Rankings")

        sort_option = st.selectbox(
            "Rank players by",
            [
                "Actual - Expected",
                f"Actual {volume_label}",
                expected_label,
                "Minutes Played"
            ]
        )

        sort_columns = {
            "Actual - Expected": "actual_minus_expected",
            f"Actual {volume_label}": actual_col,
            expected_label: expected_col,
            "Minutes Played": "minutes"
        }

        ranking_df = filtered_df.sort_values(
            by=sort_columns[sort_option],
            ascending=(sort_option == "Actual - Expected")
            if False else False
        )

        # Positive overperformance first for the default ranking
        if sort_option == "Actual - Expected":
            ranking_df = filtered_df.sort_values(
                "actual_minus_expected",
                ascending=False
            )

        display_cols = [
            "player",
            "player_id",
            "matches",
            "minutes",
            actual_col,
            expected_col,
            "actual_minus_expected",
            rate_col,
            efficiency_col
        ]

        st.dataframe(
            ranking_df[display_cols],
            hide_index=True,
            use_container_width=True,
            column_config={
                "actual_minus_expected": st.column_config.NumberColumn(
                    "Actual - Expected",
                    format="%.2f"
                ),
                rate_col: st.column_config.NumberColumn(
                    rate_label,
                    format="%.2f"
                ),
                efficiency_col: st.column_config.NumberColumn(
                    efficiency_label,
                    format="%.3f"
                )
            }
        )


    # --------------------------------------------------
    # Interpretation guide
    # --------------------------------------------------

    with st.expander("How to interpret this dashboard"):

        st.markdown(
            """
            **Scatter plot**
            - Above the diagonal: actual output exceeds expected output.
            - Below the diagonal: actual output is below expected output.
            - Near the diagonal: actual output is close to expected output.

            **Actual - Expected**
            - Positive: overperformance relative to xG or xA.
            - Negative: underperformance relative to xG or xA.
            - Near zero: actual output is close to expected output.

            **Important:** Overperformance in one season does not
            guarantee future regression or prove that a player is
            inherently more clinical. Sample size and consistency
            across seasons should also be considered.
            """
        )

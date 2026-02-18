"""Health Economics — QALY simulation, cost-effectiveness, and treatment optimization."""

from __future__ import annotations

import plotly.graph_objects as go
import streamlit as st

from finbot.dashboard.disclaimer import show_sidebar_accessibility, show_sidebar_disclaimer

st.set_page_config(page_title="Health Economics — Finbot", layout="wide")

# Show disclaimer (includes medical disclaimer) and accessibility info
show_sidebar_disclaimer()
show_sidebar_accessibility()

st.title("Health Economics Analysis")
st.markdown(
    "Monte Carlo QALY simulation, cost-effectiveness analysis (ICER/NMB/CEAC), and treatment schedule optimization."
)

# Add specific health economics disclaimer
st.warning(
    """
    **⚠️ MEDICAL DISCLAIMER**: The health economics tools are for EDUCATIONAL and RESEARCH purposes only.
    This is NOT medical advice. Do not use these tools for actual clinical decisions, treatment planning, or
    patient care. Always consult qualified healthcare professionals and follow established clinical guidelines.
    """
)

tab_qaly, tab_cea, tab_opt, tab_scenarios = st.tabs(
    ["QALY Simulation", "Cost-Effectiveness Analysis", "Treatment Optimizer", "Clinical Scenarios"]
)

# ==========================================================================
# Tab 1 — QALY Monte Carlo Simulation
# ==========================================================================
with tab_qaly:
    st.header("QALY Monte Carlo Simulator")

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Intervention")
        interv_name = st.text_input("Intervention name", value="Drug A", key="q_name")
        cost_year = st.number_input("Annual cost ($)", value=5000.0, step=500.0, key="q_cost")
        cost_std = st.number_input("Cost std dev ($)", value=500.0, step=100.0, key="q_cost_std")
        util_gain = st.number_input("Utility gain (0-1)", value=0.10, step=0.01, key="q_util", format="%.3f")
        util_std = st.number_input("Utility gain std", value=0.02, step=0.005, key="q_util_std", format="%.3f")

    with c2:
        st.subheader("Simulation Parameters")
        base_util = st.number_input("Baseline utility", value=0.70, step=0.05, key="q_base", format="%.2f")
        base_mort = st.number_input("Baseline mortality", value=0.02, step=0.005, key="q_mort", format="%.3f")
        mort_red = st.number_input("Mortality reduction", value=0.005, step=0.001, key="q_mred", format="%.4f")
        time_hz = st.number_input("Time horizon (years)", value=10, min_value=1, max_value=50, key="q_hz")
        n_sims_q = st.number_input("Simulations", value=5000, min_value=100, max_value=50000, step=1000, key="q_nsim")

    if st.button("Run QALY Simulation", type="primary", key="q_run"):
        with st.spinner("Running QALY simulation..."):
            try:
                from finbot.services.health_economics.qaly_simulator import (
                    HealthIntervention,
                    simulate_qalys,
                )

                interv = HealthIntervention(
                    name=interv_name,
                    cost_per_year=cost_year,
                    cost_std=cost_std,
                    utility_gain=util_gain,
                    utility_gain_std=util_std,
                    mortality_reduction=mort_red,
                    mortality_reduction_std=0.001,
                )
                result = simulate_qalys(
                    interv,
                    baseline_utility=base_util,
                    baseline_mortality=base_mort,
                    time_horizon=int(time_hz),
                    n_sims=int(n_sims_q),
                )
                st.session_state["qaly_result"] = result
                st.session_state["qaly_name"] = interv_name
            except Exception as e:
                st.error(f"Simulation failed: {e}")

    if "qaly_result" in st.session_state:
        res = st.session_state["qaly_result"]
        name = st.session_state["qaly_name"]

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Mean Total QALYs", f"{res['mean_qaly']:.2f}")
        m2.metric("Mean Total Cost", f"${res['mean_cost']:,.0f}")
        m3.metric("Cost per QALY", f"${res['mean_cost'] / max(res['mean_qaly'], 0.01):,.0f}")
        m4.metric("Simulations", f"{len(res['total_qalys']):,}")

        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("#### QALY Distribution")
            fig_q = go.Figure()
            fig_q.add_trace(go.Histogram(x=res["total_qalys"].values, nbinsx=50, name="QALYs"))
            fig_q.add_vline(x=res["mean_qaly"], line_dash="dash", line_color="red", annotation_text="Mean")
            fig_q.update_layout(xaxis_title="Total QALYs", yaxis_title="Count", template="plotly_white")
            st.plotly_chart(fig_q, use_container_width=True)

        with col_b:
            st.markdown("#### Cost Distribution")
            fig_c = go.Figure()
            fig_c.add_trace(go.Histogram(x=res["total_costs"].values, nbinsx=50, name="Cost"))
            fig_c.add_vline(x=res["mean_cost"], line_dash="dash", line_color="red", annotation_text="Mean")
            fig_c.update_layout(xaxis_title="Total Cost ($)", yaxis_title="Count", template="plotly_white")
            st.plotly_chart(fig_c, use_container_width=True)

        st.markdown("#### Mean Survival Curve")
        surv_mean = res["survival_curves"].mean()
        fig_s = go.Figure()
        fig_s.add_trace(go.Scatter(x=list(surv_mean.index), y=surv_mean.values, mode="lines+markers"))
        fig_s.update_layout(xaxis_title="Year", yaxis_title="Survival Probability", template="plotly_white")
        st.plotly_chart(fig_s, use_container_width=True)


# ==========================================================================
# Tab 2 — Cost-Effectiveness Analysis
# ==========================================================================
with tab_cea:
    st.header("Cost-Effectiveness Analysis")
    st.markdown("Compare an intervention against no treatment using ICER, NMB, and CEAC.")

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Intervention")
        cea_name = st.text_input("Name", value="Drug A", key="cea_name")
        cea_cost = st.number_input("Annual cost ($)", value=5000.0, step=500.0, key="cea_cost")
        cea_cost_std = st.number_input("Cost std ($)", value=500.0, step=100.0, key="cea_cstd")
        cea_util = st.number_input("Utility gain", value=0.10, step=0.01, key="cea_util", format="%.3f")
        cea_util_std = st.number_input("Utility std", value=0.02, step=0.005, key="cea_ustd", format="%.3f")

    with c2:
        st.subheader("Parameters")
        cea_base = st.number_input("Baseline utility", value=0.70, step=0.05, key="cea_base", format="%.2f")
        cea_mort = st.number_input("Baseline mortality", value=0.02, step=0.005, key="cea_mort", format="%.3f")
        cea_hz = st.number_input("Time horizon (years)", value=10, min_value=1, max_value=50, key="cea_hz")
        cea_nsim = st.number_input("Simulations", value=5000, min_value=100, max_value=50000, step=1000, key="cea_nsim")

    if st.button("Run CEA", type="primary", key="cea_run"):
        with st.spinner("Running cost-effectiveness analysis..."):
            try:
                from finbot.services.health_economics.cost_effectiveness import (
                    cost_effectiveness_analysis,
                )
                from finbot.services.health_economics.qaly_simulator import (
                    HealthIntervention,
                    simulate_qalys,
                )

                drug = HealthIntervention(
                    name=cea_name,
                    cost_per_year=cea_cost,
                    cost_std=cea_cost_std,
                    utility_gain=cea_util,
                    utility_gain_std=cea_util_std,
                )
                none = HealthIntervention(name="No Treatment")
                sim_drug = simulate_qalys(
                    drug,
                    baseline_utility=cea_base,
                    baseline_mortality=cea_mort,
                    time_horizon=int(cea_hz),
                    n_sims=int(cea_nsim),
                )
                sim_none = simulate_qalys(
                    none,
                    baseline_utility=cea_base,
                    baseline_mortality=cea_mort,
                    time_horizon=int(cea_hz),
                    n_sims=int(cea_nsim),
                )

                cea_result = cost_effectiveness_analysis(
                    sim_results={cea_name: sim_drug, "No Treatment": sim_none},
                    comparator="No Treatment",
                )
                st.session_state["cea_result"] = cea_result
                st.session_state["cea_drug_name"] = cea_name
            except Exception as e:
                st.error(f"CEA failed: {e}")

    if "cea_result" in st.session_state:
        cea = st.session_state["cea_result"]
        drug_name = st.session_state["cea_drug_name"]
        icer_row = cea["icer"].iloc[0]

        m1, m2, m3 = st.columns(3)
        m1.metric("ICER ($/QALY)", f"${icer_row['ICER']:,.0f}")
        m2.metric("Incremental QALYs", f"{icer_row['Incremental QALYs']:.3f}")
        m3.metric("Incremental Cost", f"${icer_row['Incremental Cost']:,.0f}")

        # Summary table
        st.markdown("#### Summary")
        st.dataframe(
            cea["summary"].style.format(
                {"Mean Cost": "${:,.0f}", "Std Cost": "${:,.0f}", "Mean QALYs": "{:.3f}", "Std QALYs": "{:.3f}"}
            ),
            use_container_width=True,
        )

        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("#### Cost-Effectiveness Plane")
            plane = cea["ce_plane"][drug_name]
            fig_ce = go.Figure()
            fig_ce.add_trace(
                go.Scatter(
                    x=plane["Delta QALYs"],
                    y=plane["Delta Cost"],
                    mode="markers",
                    marker={"size": 3, "opacity": 0.3},
                    name=drug_name,
                )
            )
            fig_ce.add_hline(y=0, line_dash="dot", line_color="gray")
            fig_ce.add_vline(x=0, line_dash="dot", line_color="gray")
            fig_ce.update_layout(
                xaxis_title="Incremental QALYs",
                yaxis_title="Incremental Cost ($)",
                template="plotly_white",
            )
            st.plotly_chart(fig_ce, use_container_width=True)

        with col_b:
            st.markdown("#### Cost-Effectiveness Acceptability Curve")
            ceac = cea["ceac"]
            fig_ceac = go.Figure()
            for col in ceac.columns:
                fig_ceac.add_trace(
                    go.Scatter(
                        x=ceac.index,
                        y=ceac[col],
                        mode="lines",
                        name=col,
                    )
                )
            fig_ceac.update_layout(
                xaxis_title="WTP Threshold ($/QALY)",
                yaxis_title="P(Cost-Effective)",
                template="plotly_white",
                yaxis_range=[0, 1],
            )
            st.plotly_chart(fig_ceac, use_container_width=True)

        st.markdown("#### Net Monetary Benefit")
        nmb = cea["nmb"]
        fig_nmb = go.Figure()
        for col in nmb.columns:
            fig_nmb.add_trace(go.Scatter(x=nmb.index, y=nmb[col], mode="lines", name=col))
        fig_nmb.add_hline(y=0, line_dash="dash", line_color="red")
        fig_nmb.update_layout(
            xaxis_title="WTP Threshold ($/QALY)",
            yaxis_title="Net Monetary Benefit ($)",
            template="plotly_white",
        )
        st.plotly_chart(fig_nmb, use_container_width=True)


# ==========================================================================
# Tab 3 — Treatment Schedule Optimizer
# ==========================================================================
with tab_opt:
    st.header("Treatment Schedule Optimizer")
    st.markdown("Grid search over dose frequency and treatment duration to find the optimal schedule.")

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Treatment Parameters")
        opt_cpd = st.number_input("Cost per dose ($)", value=500.0, step=100.0, key="opt_cpd")
        opt_cpd_std = st.number_input("Cost std ($)", value=50.0, step=10.0, key="opt_cpd_std")
        opt_qgpd = st.number_input("QALY gain per dose", value=0.02, step=0.005, key="opt_qgpd", format="%.3f")
        opt_qgpd_std = st.number_input("QALY gain std", value=0.005, step=0.001, key="opt_qstd", format="%.4f")

    with c2:
        st.subheader("Search Parameters")
        opt_base = st.number_input("Baseline utility", value=0.70, step=0.05, key="opt_base", format="%.2f")
        opt_mort = st.number_input("Baseline mortality", value=0.02, step=0.005, key="opt_mort", format="%.3f")
        opt_wtp = st.number_input("WTP threshold ($/QALY)", value=50000.0, step=10000.0, key="opt_wtp")
        opt_nsim = st.number_input("Sims per combo", value=2000, min_value=100, max_value=20000, step=500, key="opt_ns")

    if st.button("Optimize", type="primary", key="opt_run"):
        with st.spinner("Searching treatment schedules..."):
            try:
                from finbot.services.health_economics.treatment_optimizer import optimize_treatment

                opt_out = optimize_treatment(
                    cost_per_dose=opt_cpd,
                    cost_per_dose_std=opt_cpd_std,
                    qaly_gain_per_dose=opt_qgpd,
                    qaly_gain_per_dose_std=opt_qgpd_std,
                    baseline_utility=opt_base,
                    baseline_mortality=opt_mort,
                    wtp_threshold=opt_wtp,
                    n_sims=int(opt_nsim),
                )
                st.session_state["opt_result"] = opt_out
            except Exception as e:
                st.error(f"Optimization failed: {e}")

    if "opt_result" in st.session_state:
        opt_df = st.session_state["opt_result"]
        best = opt_df.iloc[0]

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Best Frequency", f"{int(best['Frequency'])} doses/yr")
        m2.metric("Best Duration", f"{int(best['Duration'])} years")
        m3.metric("ICER", f"${best['ICER']:,.0f}/QALY")
        m4.metric("NMB", f"${best['NMB']:,.0f}")

        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("#### NMB by Schedule")
            fig_nmb = go.Figure()
            for dur in sorted(opt_df["Duration"].unique()):
                subset = opt_df[opt_df["Duration"] == dur]
                fig_nmb.add_trace(
                    go.Scatter(
                        x=subset["Frequency"],
                        y=subset["NMB"],
                        mode="lines+markers",
                        name=f"{int(dur)}yr",
                    )
                )
            fig_nmb.add_hline(y=0, line_dash="dash", line_color="red")
            fig_nmb.update_layout(
                xaxis_title="Doses per Year",
                yaxis_title="Net Monetary Benefit ($)",
                template="plotly_white",
            )
            st.plotly_chart(fig_nmb, use_container_width=True)

        with col_b:
            st.markdown("#### ICER by Schedule")
            fig_icer = go.Figure()
            for dur in sorted(opt_df["Duration"].unique()):
                subset = opt_df[opt_df["Duration"] == dur]
                # Clip infinite ICERs for display
                icer_vals = subset["ICER"].clip(upper=500_000)
                fig_icer.add_trace(
                    go.Scatter(
                        x=subset["Frequency"],
                        y=icer_vals,
                        mode="lines+markers",
                        name=f"{int(dur)}yr",
                    )
                )
            fig_icer.add_hline(y=opt_wtp, line_dash="dash", line_color="green", annotation_text="WTP")
            fig_icer.update_layout(
                xaxis_title="Doses per Year",
                yaxis_title="ICER ($/QALY)",
                template="plotly_white",
            )
            st.plotly_chart(fig_icer, use_container_width=True)

        st.markdown("#### Full Results")
        st.dataframe(
            opt_df.style.format(
                {
                    "Annual_Cost": "${:,.0f}",
                    "Total_Cost": "${:,.0f}",
                    "Total_QALYs": "{:.3f}",
                    "Baseline_QALYs": "{:.3f}",
                    "Incremental_Cost": "${:,.0f}",
                    "Incremental_QALYs": "{:.4f}",
                    "ICER": "${:,.0f}",
                    "NMB": "${:,.0f}",
                }
            ),
            use_container_width=True,
            hide_index=True,
        )


# ==========================================================================
# Tab 4 — Clinical Scenarios
# ==========================================================================
with tab_scenarios:
    st.header("Clinical Scenarios")
    st.markdown(
        "Pre-built real-world clinical scenarios using the health economics modules above. "
        "Each scenario models a published health intervention against a comparator using "
        "Monte Carlo QALY simulation and cost-effectiveness analysis."
    )

    wtp_input = st.number_input(
        "Willingness-to-pay threshold ($/QALY)",
        value=100_000.0,
        step=10_000.0,
        min_value=10_000.0,
        max_value=500_000.0,
        key="scen_wtp",
    )
    n_sims_scen = st.number_input(
        "Simulations per scenario",
        value=2_000,
        min_value=100,
        max_value=20_000,
        step=500,
        key="scen_nsim",
    )

    if st.button("Run All Scenarios", type="primary", key="scen_run"):
        with st.spinner("Running 3 clinical scenarios..."):
            try:
                from finbot.services.health_economics.scenarios.cancer_screening import (
                    run_cancer_screening_scenario,
                )
                from finbot.services.health_economics.scenarios.hypertension import (
                    run_hypertension_scenario,
                )
                from finbot.services.health_economics.scenarios.vaccine import (
                    run_vaccine_scenario,
                )

                results = {
                    "cancer": run_cancer_screening_scenario(
                        n_sims=int(n_sims_scen), wtp_threshold=float(wtp_input), seed=42
                    ),
                    "hypertension": run_hypertension_scenario(
                        n_sims=int(n_sims_scen), wtp_threshold=float(wtp_input), seed=42
                    ),
                    "vaccine": run_vaccine_scenario(n_sims=int(n_sims_scen), wtp_threshold=float(wtp_input), seed=42),
                }
                st.session_state["scen_results"] = results
            except Exception as e:
                st.error(f"Scenario run failed: {e}")

    if "scen_results" in st.session_state:
        scenarios = st.session_state["scen_results"]

        # Summary metrics table
        st.markdown("### Summary")
        summary_rows = []
        for res in scenarios.values():
            icer_str = f"${res.icer:,.0f}" if res.icer is not None else "Dominated / Dominant"
            summary_rows.append(
                {
                    "Scenario": res.scenario_name,
                    "Intervention": res.intervention_name,
                    "vs.": res.comparator_name,
                    "ICER ($/QALY)": icer_str,
                    "NMB ($)": f"${res.nmb:,.0f}",
                    "Cost-Effective?": "✅ Yes" if res.is_cost_effective else "❌ No",
                    "QALY Gain": f"{res.qaly_gain:.4f}",
                    "Cost Difference": f"${res.cost_difference:,.0f}",
                }
            )
        import pandas as pd

        st.dataframe(pd.DataFrame(summary_rows), use_container_width=True, hide_index=True)

        # Detailed expandable cards per scenario
        st.markdown("### Scenario Details")
        for res in scenarios.values():
            with st.expander(res.scenario_name, expanded=False):
                st.markdown(f"**Description:** {res.description}")
                st.markdown(f"**Simulations:** {res.n_simulations:,}")

                c1, c2, c3, c4 = st.columns(4)
                c1.metric("QALY Gain", f"{res.qaly_gain:.4f}")
                c2.metric("Cost Difference", f"${res.cost_difference:,.0f}")
                c3.metric("NMB", f"${res.nmb:,.0f}")
                c4.metric(
                    "ICER",
                    f"${res.icer:,.0f}" if res.icer is not None else "N/A",
                )

                if res.summary_stats:
                    st.markdown("**Additional Statistics**")
                    stats_df = pd.DataFrame([{"Metric": k, "Value": f"{v:,.4f}"} for k, v in res.summary_stats.items()])
                    st.dataframe(stats_df, use_container_width=True, hide_index=True)

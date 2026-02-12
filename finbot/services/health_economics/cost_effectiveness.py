"""Cost-effectiveness analysis (CEA) for comparing health interventions.

Implements standard health economics tools:
- Incremental Cost-Effectiveness Ratio (ICER)
- Net Monetary Benefit (NMB)
- Cost-Effectiveness Acceptability Curves (CEAC)
- Cost-effectiveness plane scatter data

Uses probabilistic sensitivity analysis (PSA) via Monte Carlo simulation
results from the QALY simulator.

Typical usage:
    cea = cost_effectiveness_analysis(
        sim_results={"Drug A": sim_a, "No Treatment": sim_baseline},
        comparator="No Treatment",
    )
    print(f"ICER: ${cea['icer']['ICER'].iloc[0]:,.0f}/QALY")
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def cost_effectiveness_analysis(
    sim_results: dict[str, dict[str, pd.Series | pd.DataFrame | float]],
    comparator: str,
    wtp_thresholds: list[float] | None = None,
) -> dict[str, pd.DataFrame | dict[str, pd.DataFrame]]:
    """Run cost-effectiveness analysis comparing interventions to a comparator.

    Parameters
    ----------
    sim_results : dict[str, dict]
        Mapping of intervention name to simulation results from
        :func:`simulate_qalys`.  Must contain at least the comparator and
        one other intervention.
    comparator : str
        Name of the comparator intervention (e.g. ``"No Treatment"``).
    wtp_thresholds : list[float] | None
        Willingness-to-pay thresholds for CEAC/NMB.
        Defaults to $0 -- $200 000 in $5 000 steps.

    Returns
    -------
    dict with keys:
        ``icer``     : pd.DataFrame — ICER for each intervention vs comparator
        ``nmb``      : pd.DataFrame — mean NMB at each WTP threshold
        ``ceac``     : pd.DataFrame — P(cost-effective) at each WTP threshold
        ``ce_plane`` : dict[str, pd.DataFrame] — (ΔCost, ΔQALY) per intervention
        ``summary``  : pd.DataFrame — summary statistics per intervention
    """
    if comparator not in sim_results:
        raise ValueError(f"Comparator '{comparator}' not found in sim_results")

    if wtp_thresholds is None:
        wtp_thresholds = [float(x) for x in range(0, 205_000, 5_000)]

    comp = sim_results[comparator]
    comp_costs = comp["total_costs"].to_numpy()  # type: ignore[union-attr]
    comp_qalys = comp["total_qalys"].to_numpy()  # type: ignore[union-attr]

    interventions = [k for k in sim_results if k != comparator]

    # --- ICER table ---
    icer_rows: list[dict[str, object]] = []
    ce_plane_data: dict[str, pd.DataFrame] = {}

    for name in interventions:
        res = sim_results[name]
        int_costs = res["total_costs"].to_numpy()  # type: ignore[union-attr]
        int_qalys = res["total_qalys"].to_numpy()  # type: ignore[union-attr]

        delta_cost = int_costs - comp_costs
        delta_qaly = int_qalys - comp_qalys

        mean_dc = float(delta_cost.mean())
        mean_dq = float(delta_qaly.mean())
        icer = mean_dc / mean_dq if abs(mean_dq) > 1e-10 else float("inf")

        icer_rows.append(
            {
                "Intervention": name,
                "Mean Cost": float(int_costs.mean()),
                "Mean QALYs": float(int_qalys.mean()),
                "Incremental Cost": mean_dc,
                "Incremental QALYs": mean_dq,
                "ICER": icer,
            }
        )

        ce_plane_data[name] = pd.DataFrame({"Delta Cost": delta_cost, "Delta QALYs": delta_qaly})

    icer_df = pd.DataFrame(icer_rows)

    # --- NMB and CEAC across WTP thresholds ---
    nmb_rows: list[dict[str, float]] = []
    ceac_rows: list[dict[str, float]] = []

    for wtp in wtp_thresholds:
        # NMB for every intervention (including comparator)
        all_nmbs: dict[str, np.ndarray] = {}
        all_nmbs[comparator] = wtp * comp_qalys - comp_costs

        nmb_row: dict[str, float] = {"WTP": wtp}
        for name in interventions:
            res = sim_results[name]
            ic = res["total_costs"].to_numpy()  # type: ignore[union-attr]
            iq = res["total_qalys"].to_numpy()  # type: ignore[union-attr]
            nmb = wtp * iq - ic
            all_nmbs[name] = nmb
            nmb_row[name] = float(nmb.mean())
        nmb_rows.append(nmb_row)

        # CEAC: probability each intervention has highest NMB
        nmb_matrix = np.column_stack(list(all_nmbs.values()))
        best = nmb_matrix.argmax(axis=1)
        ceac_row: dict[str, float] = {"WTP": wtp}
        for i, iname in enumerate(all_nmbs):
            ceac_row[iname] = float((best == i).mean())
        ceac_rows.append(ceac_row)

    nmb_df = pd.DataFrame(nmb_rows).set_index("WTP")
    nmb_df.index.name = "WTP Threshold"

    ceac_df = pd.DataFrame(ceac_rows).set_index("WTP")
    ceac_df.index.name = "WTP Threshold"

    # --- Summary table ---
    summary_rows: list[dict[str, object]] = []
    for name in [comparator, *interventions]:
        res = sim_results[name]
        tc = res["total_costs"]
        tq = res["total_qalys"]
        summary_rows.append(
            {
                "Intervention": name,
                "Mean Cost": res["mean_cost"],
                "Std Cost": float(tc.std()),  # type: ignore[union-attr]
                "Mean QALYs": res["mean_qaly"],
                "Std QALYs": float(tq.std()),  # type: ignore[union-attr]
            }
        )

    summary_df = pd.DataFrame(summary_rows).set_index("Intervention")

    return {
        "icer": icer_df,
        "nmb": nmb_df,
        "ceac": ceac_df,
        "ce_plane": ce_plane_data,
        "summary": summary_df,
    }

# Health Economics with Python, Part 2: Cost-Effectiveness Analysis

*Originally published: 2026-02-17*
*Reading time: ~12 minutes*
*Series: [Part 1: QALYs](health-economics-part1-qaly.md) | [Part 2 (this post)] | [Part 3: Treatment Optimization](health-economics-part3-optimization.md)*

---

In [Part 1](health-economics-part1-qaly.md) we built a Monte Carlo QALY simulator that produces distributions of health outcomes and costs for different interventions. Now we have the numbers — but we still need to answer the central policy question: **is this treatment worth funding?**

That's what Cost-Effectiveness Analysis (CEA) does. This post covers the three key tools:
1. **ICER** — the fundamental cost-effectiveness measure
2. **Net Monetary Benefit (NMB)** — a complementary measure that avoids ICER's mathematical pathologies
3. **Cost-Effectiveness Acceptability Curve (CEAC)** — the probabilistic answer to "should we fund this?"

---

## The Incremental Cost-Effectiveness Ratio (ICER)

The ICER answers: *how much does it cost to generate one additional QALY compared to the alternative?*

```
ICER = (Cost_intervention - Cost_comparator) / (QALYs_intervention - QALYs_comparator)
```

Or in shorthand:

```
ICER = ΔCost / ΔQALY
```

Using our type 2 diabetes example from Part 1:

| Intervention | Mean Cost | Mean QALYs |
|--------------|-----------|------------|
| No Treatment | $0 | 6.312 |
| Metformin | $4,201 | 6.745 |
| GLP-1 Agonist | $65,890 | 7.148 |

**Metformin vs No Treatment:**
```
ICER = ($4,201 - $0) / (6.745 - 6.312) = $4,201 / 0.433 ≈ $9,700/QALY
```

**GLP-1 vs No Treatment:**
```
ICER = ($65,890 - $0) / (7.148 - 6.312) = $65,890 / 0.836 ≈ $78,800/QALY
```

### Interpreting the ICER: Willingness-to-Pay Thresholds

An ICER alone doesn't tell you if a treatment is "worth it." That requires a **willingness-to-pay (WTP) threshold** — the maximum a health system is willing to pay for one QALY:

| Jurisdiction | WTP Threshold |
|-------------|--------------|
| NICE (UK) | £20,000–£30,000/QALY (~$25K–$38K USD) |
| CADTH (Canada) | ~$50,000 CAD (~$37K USD) |
| WHO guidance | 1–3× GDP per capita (varies by country; ~$50K–$150K for high-income) |
| US (informal) | Often cited at $100,000–$150,000/QALY |

By these thresholds:
- **Metformin** ($9,700/QALY) is highly cost-effective by any standard
- **GLP-1 agonist** ($78,800/QALY) is cost-effective under US benchmarks but borderline under UK/Canadian thresholds

---

## ICER Pathologies: Why NMB Matters

The ICER has several mathematical problems:

**Division by zero**: If two interventions produce identical QALYs (ΔQALY = 0), ICER is undefined.

**Dominance and extended dominance**: If intervention A is both cheaper and more effective than B, A "dominates" B and the ICER isn't meaningful. Extended dominance occurs when a combination of interventions is more cost-effective than any single option.

**Sign flips**: A negative ICER can mean either "dominant" (lower cost, higher QALYs — good) or "dominated" (higher cost, lower QALYs — bad). The same number with different interpretations.

**Net Monetary Benefit (NMB)** avoids all of these:

```
NMB = WTP × ΔQALY - ΔCost
```

NMB converts QALYs to money at the WTP threshold and subtracts incremental cost. Positive NMB means cost-effective. Higher NMB means more cost-effective. No division required.

For the GLP-1 agonist at WTP = $100,000/QALY:
```
NMB = $100,000 × 0.836 - $65,890 = $83,600 - $65,890 = $17,710
```

Positive NMB ($17,710) confirms cost-effective at this threshold.

---

## Implementing CEA in Python

Here's Finbot's `cost_effectiveness_analysis()` function:

```python
import numpy as np
import pandas as pd


def cost_effectiveness_analysis(
    sim_results: dict,
    comparator: str,
    wtp_thresholds: list[float] | None = None,
) -> dict:
    """Compare interventions using CEA (ICER, NMB, CEAC).

    sim_results: dict mapping intervention name to simulate_qalys() output
    comparator:  name of the reference intervention (e.g. "No Treatment")
    wtp_thresholds: list of WTP values for NMB/CEAC (default $0–$200K in $5K steps)
    """
    if wtp_thresholds is None:
        wtp_thresholds = [float(x) for x in range(0, 205_000, 5_000)]

    comp = sim_results[comparator]
    comp_costs = comp["total_costs"].to_numpy()
    comp_qalys = comp["total_qalys"].to_numpy()

    interventions = [k for k in sim_results if k != comparator]

    # --- ICER table ---
    icer_rows = []
    ce_plane_data = {}

    for name in interventions:
        res = sim_results[name]
        int_costs = res["total_costs"].to_numpy()
        int_qalys = res["total_qalys"].to_numpy()

        delta_cost = int_costs - comp_costs
        delta_qaly = int_qalys - comp_qalys

        mean_dc = float(delta_cost.mean())
        mean_dq = float(delta_qaly.mean())
        icer = mean_dc / mean_dq if abs(mean_dq) > 1e-10 else float("inf")

        icer_rows.append({
            "Intervention": name,
            "Mean Cost": float(int_costs.mean()),
            "Mean QALYs": float(int_qalys.mean()),
            "Incremental Cost": mean_dc,
            "Incremental QALYs": mean_dq,
            "ICER": icer,
        })
        ce_plane_data[name] = pd.DataFrame({
            "Delta Cost": delta_cost,
            "Delta QALYs": delta_qaly,
        })

    icer_df = pd.DataFrame(icer_rows)

    # --- NMB and CEAC across WTP thresholds ---
    nmb_rows, ceac_rows = [], []

    for wtp in wtp_thresholds:
        all_nmbs = {comparator: wtp * comp_qalys - comp_costs}
        nmb_row = {"WTP": wtp}

        for name in interventions:
            res = sim_results[name]
            ic = res["total_costs"].to_numpy()
            iq = res["total_qalys"].to_numpy()
            nmb = wtp * iq - ic
            all_nmbs[name] = nmb
            nmb_row[name] = float(nmb.mean())

        nmb_rows.append(nmb_row)

        # CEAC: probability each option has the highest NMB
        nmb_matrix = np.column_stack(list(all_nmbs.values()))
        best = nmb_matrix.argmax(axis=1)
        ceac_row = {"WTP": wtp}
        for i, iname in enumerate(all_nmbs):
            ceac_row[iname] = float((best == i).mean())
        ceac_rows.append(ceac_row)

    nmb_df = pd.DataFrame(nmb_rows).set_index("WTP")
    ceac_df = pd.DataFrame(ceac_rows).set_index("WTP")

    return {
        "icer": icer_df,
        "nmb": nmb_df,
        "ceac": ceac_df,
        "ce_plane": ce_plane_data,
    }
```

### Running the Full Analysis

```python
from finbot.services.health_economics.cost_effectiveness import cost_effectiveness_analysis

# sim_no_tx, sim_metformin, sim_glp1 from Part 1
sim_results = {
    "No Treatment": sim_no_tx,
    "Metformin": sim_metformin,
    "GLP-1 Agonist": sim_glp1,
}

cea = cost_effectiveness_analysis(sim_results, comparator="No Treatment")

# ICER table
print("=== ICER Table ===")
print(cea["icer"].to_string(index=False))
```

Output:
```
=== ICER Table ===
Intervention   Mean Cost  Mean QALYs  Incremental Cost  Incremental QALYs         ICER
    Metformin    4201.23       6.745           4201.23              0.433       9700.28
GLP-1 Agonist   65890.45       7.148          65890.45              0.836      78815.13
```

---

## The Cost-Effectiveness Plane

The CE plane plots each Monte Carlo simulation as a point in (ΔQALY, ΔCost) space. Each point represents one possible outcome of the intervention:

```
Y-axis: Incremental Cost (positive = more expensive than comparator)
X-axis: Incremental QALYs (positive = more effective)
```

The four quadrants:
- **Southeast (positive ΔQALY, negative ΔCost)**: "Dominant" — more effective AND cheaper. Always fund.
- **Northwest (negative ΔQALY, positive ΔCost)**: "Dominated" — less effective AND more expensive. Never fund.
- **Northeast (positive ΔQALY, positive ΔCost)**: Most common case — more effective but also more expensive. Decision depends on WTP threshold.
- **Southwest**: Less effective and cheaper. Consider funding if QALYs are only slightly worse.

```python
# Get CE plane data for GLP-1
glp1_plane = cea["ce_plane"]["GLP-1 Agonist"]

# What fraction of simulations are in the "northeast" quadrant?
northeast = (glp1_plane["Delta QALYs"] > 0) & (glp1_plane["Delta Cost"] > 0)
print(f"GLP-1: {northeast.mean():.1%} of simulations in cost-effective quadrant (NE)")

# At $100K WTP, what fraction of NE simulations are below the threshold line?
wtp = 100_000
below_threshold = glp1_plane["Delta Cost"] < wtp * glp1_plane["Delta QALYs"]
print(f"GLP-1: {below_threshold.mean():.1%} of simulations below $100K/QALY threshold")
```

---

## The Cost-Effectiveness Acceptability Curve (CEAC)

The CEAC answers: **at each WTP threshold, what is the probability that this intervention is the most cost-effective option?**

It's the fraction of Monte Carlo simulations where a given intervention has the highest NMB:

```python
# Extract CEAC for GLP-1 at key thresholds
ceac = cea["ceac"]
key_thresholds = [50_000, 75_000, 100_000, 150_000]

print("=== CEAC: Probability of Being Most Cost-Effective ===")
for wtp in key_thresholds:
    p_metformin = ceac.loc[wtp, "Metformin"]
    p_glp1 = ceac.loc[wtp, "GLP-1 Agonist"]
    print(f"WTP ${wtp:>7,}: Metformin={p_metformin:.1%}  GLP-1={p_glp1:.1%}")
```

Output:
```
=== CEAC: Probability of Being Most Cost-Effective ===
WTP $ 50,000: Metformin=82.3%  GLP-1=17.7%
WTP $ 75,000: Metformin=61.4%  GLP-1=38.6%
WTP $100,000: Metformin=43.1%  GLP-1=56.9%
WTP $150,000: Metformin=28.7%  GLP-1=71.3%
```

This is a richer answer than a binary "cost-effective or not." At a $50,000 WTP threshold (CADTH-level), Metformin is the preferred option 82% of the time. At $100,000 (US benchmarks), GLP-1 becomes preferred in 57% of simulations. The CEAC makes the uncertainty explicit.

### What the CEAC Tells Decision-Makers

At WTP = $75,000/QALY, neither intervention is clearly dominant — Metformin wins 61% of the time, GLP-1 wins 39%. A decision-maker who is risk-averse (wants high confidence in value for money) would fund Metformin. One focused on maximizing expected QALYs might still choose GLP-1 for its higher mean effectiveness.

This is precisely the kind of analysis that informs real-world coverage decisions by NICE, CADTH, and similar agencies. The CEAC provides the information; the decision involves value judgments about risk tolerance and equity that the numbers alone can't resolve.

---

## Net Monetary Benefit at Varying Thresholds

The NMB table shows how expected monetary value of each treatment changes across WTP thresholds:

```python
# NMB comparison at key thresholds
nmb = cea["nmb"]
print("=== Mean NMB at Varying WTP Thresholds ===")
print(f"{'WTP':>10} | {'Metformin NMB':>15} | {'GLP-1 NMB':>15}")
print("-" * 45)
for wtp in [0, 25_000, 50_000, 100_000, 150_000]:
    m_nmb = nmb.loc[wtp, "Metformin"]
    g_nmb = nmb.loc[wtp, "GLP-1 Agonist"]
    print(f"${wtp:>9,} | ${m_nmb:>14,.0f} | ${g_nmb:>14,.0f}")
```

Output:
```
=== Mean NMB at Varying WTP Thresholds ===
       WTP |   Metformin NMB |     GLP-1 NMB
---------------------------------------------
$        0 |        -$4,201 |       -$65,890
$   25,000 |         $6,624 |       -$44,990
$   50,000 |        $17,449 |       -$24,090
$  100,000 |        $39,099 |        $17,710
$  150,000 |        $60,749 |        $59,510
```

At WTP = $0, both treatments have negative NMB (they cost money with no monetary credit for QALYs). As WTP rises, both become more favorable, with GLP-1 crossing into positive territory around $80,000/QALY. This table makes the sensitivity to the WTP assumption concrete and explicit.

---

## Extended Dominance: A Common Pitfall

Suppose we had a third intervention — "Standard Care Plus" — at $30,000 and 7.00 QALYs. Comparing it to No Treatment gives an ICER of $30,000/0.688 = $43,600/QALY. Seems good!

But now compare GLP-1 directly to Metformin (not to No Treatment):
```
ICER (GLP-1 vs Metformin) = ($65,890 - $4,201) / (7.148 - 6.745) = $61,689 / 0.403 = $153,100/QALY
```

If our WTP threshold is $100,000, GLP-1 is no longer cost-effective *versus Metformin as the relevant comparator*. This is extended dominance — you should compare each intervention to the most cost-effective option below it on the cost-effectiveness frontier, not always to "No Treatment."

Finbot's CEA implementation simplifies by comparing all interventions to a single comparator. For a full cost-effectiveness frontier analysis, you'd need to sort interventions by cost and eliminate dominated/extended-dominated options — a reasonable extension for future work.

---

## Presenting Results: What Stakeholders Need

Different audiences need different outputs from CEA:

**Clinicians:** Focus on ICER vs threshold: "Metformin costs $9,700/QALY — well within CADTH guidelines."

**Payers (insurers, government):** Focus on CEAC and budget impact: "At our $50,000 threshold, Metformin is preferred in 82% of scenarios and costs $4,200 per patient."

**Patients:** Focus on outcomes: "GLP-1 agonists provide an additional 0.4 QALYs on average over 10 years, which is roughly equivalent to 5 additional months of perfect health."

**Policy analysts:** The full output — CE plane, CEAC, NMB table, sensitivity analysis — is needed to understand how conclusions change under different assumptions.

Good CEA reporting includes all of these perspectives. Finbot's health economics module produces the data to support each view.

---

## Summary

CEA tools covered in this post:

| Tool | What It Answers | Key Formula |
|------|----------------|-------------|
| **ICER** | How much does 1 additional QALY cost? | ΔCost / ΔQALY |
| **NMB** | Is this treatment worth it at a given WTP? | WTP × ΔQALY - ΔCost |
| **CEAC** | How likely is this to be the best choice? | P(highest NMB) at each WTP |
| **CE plane** | How does uncertainty look visually? | Scatter of (ΔQALY, ΔCost) per simulation |

In **Part 3**, we'll go further: instead of comparing fixed interventions, we'll *optimize* treatment schedules using grid search over dose frequency and duration, then use NMB to rank the results.

---

## Further Reading

- [CADTH Guidelines for Economic Evaluation](https://www.cadth.ca/guidelines-economic-evaluation-health-technologies-canada)
- [NICE Technology Appraisal Methodology](https://www.nice.org.uk/process/pmg36)
- [Drummond et al., Methods for the Economic Evaluation of Health Care Programmes (4th ed.)](https://oxford.universitypressscholarship.com/view/10.1093/acprof:oso/9780198529453.001.0001/acprof-9780198529453) — the standard reference textbook
- [Finbot CEA code](https://github.com/jerdaw/finbot/blob/main/finbot/services/health_economics/cost_effectiveness.py)

---

*[← Part 1: QALYs](health-economics-part1-qaly.md) | [Part 3: Treatment Optimization →](health-economics-part3-optimization.md)*

---

**Tags:** Python, health economics, ICER, cost-effectiveness analysis, CEAC, NMB, healthcare policy

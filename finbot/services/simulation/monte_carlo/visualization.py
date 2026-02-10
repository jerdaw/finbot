import numpy as np
from matplotlib import pyplot as plt


def plot_trials(trials_df):
    for _i, t in trials_df.iterrows():
        plt.plot(t)
    plt.xlabel(trials_df.columns.name)
    plt.ylabel(trials_df.index.name)
    plt.suptitle("Monte Carlo Trial Results")
    plt.show()


def plot_hist(trials_df, bins=100):
    trial_closes = trials_df[trials_df.columns[-1]]
    start_price = trials_df[trials_df.columns[0]][trials_df.index[0]]
    sim_periods = len(trials_df.columns)

    plt.title(f"Price distribution after {sim_periods} periods", weight="bold")
    plt.hist(trial_closes, bins=bins)

    quants = (5, 25, 50, 75, 95)
    info_str = f"Start Price: ${round(start_price, 2)}"
    info_str += f"\n\nMean Final Price: ${round(trial_closes.mean(), 2)}"
    sp = "\n    "
    quant_str = (
        f"Percentiles: {', '.join(f'{sp}{n}th: ' + str(round(np.percentile(trial_closes, n), 2)) for n in quants)}"
    )
    info_str += "\n\n" + quant_str

    plt.figtext(0.6, 0.7, info_str)

    plt.axvline(start_price, color="k", linestyle="solid", linewidth=1)
    plt.axvline(np.mean(trial_closes), color="r", linestyle="dashed", linewidth=1)
    for quant in quants:
        plt.axvline(np.percentile(trial_closes, quant), color="blue", linestyle="dashed", linewidth=1)

    plt.show()

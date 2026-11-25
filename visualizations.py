import numpy as np
import pandas as pd
import matplotlib
# so charts save to files without opening any windows (need when making charts in Flask)
matplotlib.use("Agg")
import matplotlib.pyplot as plt


# import the analysis functions
from analysis import (MEASURES, get_state_data, correlation, trend_line, all_correlations)

# readable names from the estimate types
ESTIMATE_LABELS = {
    "CrudePrev": "Crude Estimate",
    "AdjPrev": "Age-adjusted estimate"
}

# the three comparisons from project plan
SCATTER_PLOT_COMPARISONS = [
    ("Obesity", "Depression"),
    ("Physical inactivity", "Depression"),
    ("Short sleep", "Depression")
]

def make_histogram(df, measure, my_county, estimate="CrudePrev",
                   filename="static/charts/histogram.png"):

    # define the column name for chosen measure
    column = MEASURES[measure] + "_" + estimate

    # subset to the counties with data
    values = df[column].dropna()
    excluded = int(df[column].isna().sum())

    # return None if no counties have data
    if len(values) == 0:
        return None
    
    # make new figure
    fig, ax = plt.subplots(figsize=(8,5))

    # pot the hisogram of county values
    ax.hist(values, bins=10, color="lightgray", edgecolor="black")

    # mark the user's county with red line
    my_row = df[df["CountyName"]== my_county]
    if my_row.empty:
        # county not found
        pass
        
    elif np.isnan(my_row[column].iloc[0]):
        # county has no value
        pass
    else:
        # mark the county value with a red line
        my_value = my_row[column].iloc[0]
        ax.axvline(my_value, color="red", linewidth=2,
                   label=f"{my_county}: {my_value}%")
        ax.legend()

    # add labels to chart
    ax.set_title(f"{measure} ({ESTIMATE_LABELS[estimate]})\n"
                 f"{len(values)} counties included, {excluded} excluded")
    ax.set_xlabel(f"{measure} (% of adults)")
    ax.set_ylabel("Number of counties")
    ax.grid(linestyle="--", linewidth=0.5, alpha=0.5)

    # save the figure to file
    fig.tight_layout()
    fig.savefig(filename)
    plt.close(fig)
    return filename

def make_county_bar_chart():
    pass

def make_scatter_plot():
    pass

def make_correlation_heatmap():
    pass

if __name__ == "__main__":
    ca = get_state_data("CA")
    print(make_histogram(ca, "Obesity", "Los Angeles"))
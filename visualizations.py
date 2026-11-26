import numpy as np
import pandas as pd
import matplotlib
# so charts save to files without opening any windows (need when making charts in Flask)
matplotlib.use("Agg")
import matplotlib.pyplot as plt


# import the analysis functions
from analysis import (MEASURES, get_state_data, summary_stats, correlation, trend_line, all_correlations)

# readable names from the estimate types
ESTIMATE_LABELS = {
    "CrudePrev": "Actual % of adults",
    "AdjPrev": "Adjusted for age difference"
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

    # make bin edges
    bin_width = 2.5
    start = np.floor(values.min() / 5) * 5
    stop = np.ceil(values.max() / 5) * 5
    bins = np.arange(start, stop + bin_width, bin_width)

    # pot the hisogram of county values
    ax.hist(values, bins=bins, color="lightgray", edgecolor="black")

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
    ax.set_ylabel("Number of counties in this range")
    ax.grid(linestyle="--", linewidth=0.5, alpha=0.5)

    # save the figure to file
    fig.tight_layout()
    fig.savefig(filename)
    plt.close(fig)
    return filename

def make_county_bar_chart(df, measure, my_county, estimate="CrudePrev",
                          top_n=10, filename="static/charts/bar_chart.png"):
    
    # define the column name for chosen measure
    column = MEASURES[measure] + "_" + estimate

    # subset to the counties with data, highest to lowest
    data = df[["CountyName", column]].dropna()
    data = data.sort_values(by=column, ascending=False)
    excluded = int(df[column].isna().sum())

    # return None if no counties have data
    if len(data) == 0:
        return None

    # decide which counties to include (top_n)
    if len(data) <= 2*top_n:
        included = data
        title_part = "All counties"
    else:
        # large state: show the highest and lowest top_n counties
        included = pd.concat([data.head(top_n), data.tail(top_n)])
        title_part = f"Top {top_n} and bottom {top_n} counties"

    # add user's county if not already included
    if my_county not in included["CountyName"].values:
        my_row = data[data["CountyName"] == my_county]
        if not my_row.empty:
            included = pd.concat([included, my_row])
            included = included.sort_values(column, ascending=False)

    # color the user's county reed and the others as gray
    colors = []
    for name in included["CountyName"].values:
        if name == my_county:
            colors.append("red")
        else:
            colors.append("lightgray")

    # make figure and axis
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(included["CountyName"], included[column], color=colors, edgecolor="black")
    ax.invert_yaxis()

    # average of county estimates
    avg = np.mean(data[column])
    ax.axvline(avg, color="black", linestyle="--", linewidth=1, 
               label=f"Average of all counties: {avg:.1f}%")
    ax.legend(loc="lower right")

    # add label to the chart
    ax.set_title(f"{measure} ({ESTIMATE_LABELS[estimate]}): {title_part}\n"
                 f"{len(data)} counties included, {excluded} excluded")
    ax.set_xlabel(f"{measure} (% of adults)")
    ax.tick_params(axis="y", labelsize=10)

    # save figure and closeit
    fig.tight_layout()
    fig.savefig(filename)
    plt.close(fig)
    return filename



def make_scatter_plot(df, my_county, estimate="CrudePrev", pairs=SCATTER_PLOT_COMPARISONS,
                      filename="static/charts/scatter_plot.png"):

    # make one figure with a panel for each pair of measures
    fig, axes = plt.subplots(1, len(pairs), figsize=(5*len(pairs), 5), squeeze=False)
    axes = axes[0]  # flatten the axes array for easier indexing
    for ax, (x_measure, y_measure) in zip(axes, pairs):
        # define the column names for both measures
        x_col = MEASURES[x_measure] + "_" + estimate
        y_col = MEASURES[y_measure] + "_" + estimate

        # subset to the counties with both values
        both = df[["CountyName", x_col, y_col]].dropna()

        # compute correlation for this pair
        result = correlation(df, x_measure, y_measure, estimate)

        # skip this panel if there is not enough data
        if result is None:
            ax.text(0.5, 0.5, "Not enough data", ha="center", transform=ax.transAxes)
            ax.set_title(f"{y_measure} vs {x_measure}")
            continue

        # plot every county in gray
        ax.scatter(both[x_col], both[y_col], color="lightgray", edgecolor="black", alpha=0.7)

        # plot trend line
        fit = trend_line(df, x_measure, y_measure, estimate)
        x_line = np.linspace(both[x_col].min(), both[x_col].max(), 100)
        y_line = fit["slope"] * x_line + fit["intercept"]
        ax.plot(x_line, y_line, "b--", label="Overall trend")

        # mark user's county in red
        mine = both[both["CountyName"] == my_county]
        if mine.empty:
            pass
        else:
            ax.scatter(mine[x_col], mine[y_col], color="red", s=100, zorder=3, label=my_county)

        # display for small p_values
        if result["p"] < 0.001:
            p_text = "p < 0.001"
        else:
            p_text = f"p = {result['p']:.3f}"


        # add labels
        ax.set_title(f"{y_measure} vs {x_measure}\n"
                     f"r = {result['r']}, {p_text}, "
                     f"{result['counties_included']} included, "
                     f"{result['counties_excluded']} excluded",
                     fontsize=10)
        ax.set_xlabel(f"% of adults: {x_measure}")
        ax.set_ylabel(f"% of adults: {y_measure}")
        ax.grid(linestyle="--", linewidth=0.5, alpha=0.5)
        ax.legend(fontsize=8)

    # add overall tile with estimate type
    fig.suptitle(ESTIMATE_LABELS[estimate])

    # save figure and close it
    fig.tight_layout()
    fig.savefig(filename)
    plt.close(fig)
    return filename
    

def make_correlation_heatmap(df, estimate="CrudePrev", filename="static/charts/correlation_heatmap.png"):
    # build an empty grid of correlations, with 1 on the diagonal
    names = list(MEASURES)
    grid = np.full((len(names), len(names)), np.nan)
    np.fill_diagonal(grid, 1)

    # get correlation of every pair of measures
    table = all_correlations(df, estimate)

    # return None if no pairs can be compared
    if table.empty:
        return None

    # fill grid with each pair's r value
    for _, row in table.iterrows():
        i = names.index(row["measure1"])
        j = names.index(row["measure2"])
        grid[i, j] = row["r"]
        grid[j, i] = row["r"]  # symmetric

    # make new figure
    fig, ax = plt.subplots(figsize=(10, 8))
    #plot grid with red-blue color map from -1 to 1
    C = ax.imshow(grid, cmap="RdBu_r", vmin=-1, vmax=1)
    fig.colorbar(C, label="Correlation (r)")

    # write the r value in each square
    for i in range(len(names)):
        for j in range(len(names)):
            if np.isnan(grid[i, j]):
                pass
            elif abs(grid[i, j]) > 0.6:
                ax.text(j, i, f"{grid[i, j]:.2f}", ha="center", va="center", color="white")
            else:
                ax.text(j, i, f"{grid[i, j]:.2f}", ha="center", va="center", color="black")

    ax.set_xticks(range(len(names)))
    ax.set_yticks(range(len(names)))
    ax.set_xticklabels(names, rotation=45, ha="right")
    ax.set_yticklabels(names)

    ax.set_title(f"How strongly each pair of measures moves together\n"
                 f"({ESTIMATE_LABELS[estimate]})")

    fig.tight_layout()
    fig.savefig(filename)
    plt.close(fig)
    return filename

if __name__ == "__main__":
    ca = get_state_data("CA")
    print(make_histogram(ca, "Obesity", "Los Angeles"))
    print(make_county_bar_chart(ca, "Obesity", "Los Angeles"))
    print(make_scatter_plot(ca, "Los Angeles"))
    print(make_scatter_plot(ca, "Los Angeles", pairs=[("Obesity", "Diabetes")],
          filename="static/charts/scatter_obesity_diabetes.png"))
    print(make_correlation_heatmap(ca))
    tx = get_state_data("TX")
    print(make_correlation_heatmap(tx, filename="static/charts/correlation_heatmap_tx.png"))
    de = get_state_data("DE")
    print(correlation(de, "Obesity", "Diabetes"))
    print(make_county_bar_chart(de, "Obesity", "Kent",
                                filename="static/charts/bar_de.png"))
    print(make_scatter_plot(de, "Kent",
                            filename="static/charts/scatter_de.png"))
    print(make_correlation_heatmap(de, filename="static/charts/heatmap_de.png"))
import numpy as np
import pandas as pd
from scipy.stats import pearsonr
from itertools import combinations

# define the path to the PLACES county data csv file
DATA_PATH = "data/Places_County_Data.csv"

# link the readable measure names to the column prefixes
MEASURES = {
    "Obesity": "OBESITY",
    "Diabetes": "DIABETES",
    "Physical inactivity": "LPA",
    "Depression": "DEPRESSION",
    "Short sleep": "SLEEP"
}

def get_state_data(state):
    # read in the data to a dataframe
    df = pd.read_csv(DATA_PATH, thousands=",",
                    dtype={"CountyFIPS":str})
    # subset the dataframe to the selected state
    state_df = df[df["StateAbbr"] == state]
    return state_df

def get_states():
    df = pd.read_csv(DATA_PATH)
    return sorted(df["StateAbbr"].dropna().unique().tolist())

def get_counties(df):
    # make a sorted list of the county names for dropdown
    return sorted(df["CountyName"].dropna().unique().tolist())

def summary_stats(df, measure, estimate ="CrudePrev"):
    # define column name for chosen measure
    column = MEASURES[measure] + "_" + estimate
    # subset to the counties that have data
    values = df[column].dropna()

    # return None if no counties have data
    if len(values) == 0:
        return None

    # compute the statistics with numpy
    stats = {
        "measure": measure,
        "mean": round(float(np.mean(values)), 2),
        "median": round(float(np.median(values)), 2),
        "min": float(np.min(values)),
        "max": float(np.max(values)),
        "counties_with_data": len(values),
        "counties_without_data": int(df[column].isna().sum())
    }
    return stats

def county_summary(df, measure, county, estimate="CrudePrev"):
    # define the column name for the hosen measure
    column = MEASURES[measure] + "_" + estimate
    # subset to the counties with data
    values = df[column].dropna()
    #find row for selected county
    row = df[df["CountyName"] == county]

    # return None if county is not found or has no data
    if row.empty or pd.isna(row[column].iloc[0]):
        return None

    # get county's value
    value = float(row[column].iloc[0])

    # compute average of the county estimates
    county_avg = float(np.mean(values))

    # compute the rank of the county within the state
    rank = int(np.sum(values > value)) + 1

    return {
        "county": county,
        "measure": measure,
        "value": value,
        "state_county_avg": round(county_avg, 2),
        "difference": round(value - county_avg, 2),
        "rank": rank,
        "out_of": len(values)
    }

def correlation(df, measure1, measure2, estimate="CrudePrev"):
    # define column names for chosen measures
    col1 = MEASURES[measure1] + "_" + estimate
    col2 = MEASURES[measure2] + "_" + estimate
    # find the countries that have both values
    values1 = df[col1]
    values2 = df[col2]
    valid = values1.notna() & values2.notna()

    # return None if less than 3 counties have both values
    if valid.sum() < 6:
        return None

    # compute the correlation and p-value 
    r, p = pearsonr(values1[valid], values2[valid])

    return {
        "measure1": measure1,
        "measure2": measure2,
        "r": round(float(r), 2),
        "p": float(p),
        "counties_included": int(valid.sum()),
        "counties_excluded": int((~valid).sum())
    }

def trend_line(df, measure1, measure2, estimate="CrudePrev"):
    # define the column names for the two measures
    col1 = MEASURES[measure1] + "_" + estimate
    col2 = MEASURES[measure2] + "_" + estimate
    #subset to the counties with both values
    both = df[[col1, col2]].dropna()

    # return None if less than 3 counties have both values
    if len(both) < 6:
        return None

   # compute the coefficient (slope and intercept) of the trend line (y = mx + b)
    p = np.polyfit(both[col1], both[col2], 1)

    return {
        "slope": round(float(p[0]), 2),
        "intercept": round(float(p[1]), 2)
    }

def describe_correlations(result):
    if result is None:
        return "Not enough data to calculate correlation."

    r = result["r"]
    p = result["p"]

    if abs(r) < 0.3:
        strength = "Weak"
    elif abs(r) < 0.7:
        strength = "Moderate"
    else:
        strength = "Strong"

    if r > 0:
        direction = "Positive"
    else:
        direction = "Negative"

    if p < 0.05:
        significance = "Significant"
    else:
        significance = "Not significant"

    # display for small p_value
    if p < 0.001:
        p_text = "p < 0.001"
    else:
        p_text = f"p = {p:.3f}"

    return (f"{strength} {direction} relationship, {significance} " 
        f"(r = {r}, {p_text}).")

def all_correlations(df, estimate="CrudePrev"):
    # loop through every pair of measures
    results = []
    for measure1, measure2 in combinations(MEASURES, 2):
        # compute the correlation for this pair of measures
        result = correlation(df, measure1, measure2, estimate)
        # skip pairs without enough data to calculate correlation
        if result is not None:
            results.append(result)

    # make a dataframe of the results, strongest first
    table = pd.DataFrame(results)
    if not table.empty:
        table = table.sort_values("r", key=abs, ascending=False)
    return table

if __name__ == "__main__":
    ca = get_state_data("CA")
    print(len(ca))
    print(summary_stats(ca, "Obesity"))
    print(correlation(ca, "Depression", "Obesity"))
    print(describe_correlations(correlation(ca, "Depression", "Obesity")))
    print(get_counties(ca)[:5])
    print(county_summary(ca, "Obesity", "Santa Clara"))
    print(trend_line(ca, "Obesity", "Depression"))
    print(all_correlations(ca)[["measure1", "measure2", "r", "p"]])

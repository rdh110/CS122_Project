import pandas as pd

DATA_PATH = "data/Places_County_Data.csv"

MEASURES = {
    "Obesity": "OBESITY",
    "Diabetes": "DIABETES",
    "Physical inactivity": "LPA",
    "Depression": "DEPRESSION",
    "Short sleep": "SLEEP"
}

def get_state_data(state):
    df = pd.read_csv(DATA_PATH, thousands=",",
                    dtype={"CountyFIPS":str})
    state_df = df[df["StateAbbr"] == state]
    return state_df

if __name__ == "__main__":
    ca = get_state_data("CA")
    print(len(ca))
    print(ca["CountyName"].head())
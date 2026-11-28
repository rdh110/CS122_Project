# import the Flask class , render template, and request
from flask import Flask, render_template, request, Response

# import from analysis
from analysis import (MEASURES, get_states, get_state_data, get_counties, summary_stats, county_summary,
                        correlation, describe_correlations)

import time
from visualizations import (make_histogram, make_county_bar_chart, make_scatter_plot, 
                            make_correlation_heatmap)

# create a Flask object called app
app = Flask(__name__)

# define a route to the analysis page
@app.route('/analysis', methods=['GET'])
def analysis_page():
    # get user's choice from form
    state = request.args.get('state')
    county = request.args.get('county')
    measure = request.args.get('measure')
    estimate = request.args.get('estimate', 'CrudePrev')

    # get the counties for selected state
    if state:
        counties = get_counties(get_state_data(state))
    else:
        counties = [] 

    # clear county if not in chosen state
    if county not in counties:
        county = None

    # run analysis once users has picked everything
    stats = None
    my_county = None
    histogram = None
    bar_chart = None
    scatter = None
    scatter_results = []
    heatmap = None

    if state and county and measure:
        df = get_state_data(state)
        stats = summary_stats(df, measure, estimate)
        my_county = county_summary(df, measure, county, estimate)
        histogram = make_histogram(df, measure, county, estimate)
        bar_chart = make_county_bar_chart(df, measure, county, estimate)

        # compare chosen measure against every other measure
        pairs = []
        for other in MEASURES:
            if other != measure:
                pairs.append((other, measure))
        scatter = make_scatter_plot(df, county, estimate, pairs=pairs)
        for x_measure, y_measure in pairs:
            result = correlation(df, x_measure, y_measure, estimate)
            scatter_results.append(
                f"{y_measure} vs {x_measure}: {describe_correlations(result)}"
            )

        heatmap = make_correlation_heatmap(df, estimate)

    # pass the list of measures and choice to the page
    return render_template('analysis.html',
                            states = get_states(),
                            counties=counties,
                            measures=list(MEASURES),
                            state= state,
                            county=county,
                            measure=measure,
                            estimate=estimate,
                            stats=stats,
                            my_county=my_county,
                            histogram=histogram,
                            bar_chart=bar_chart,
                            scatter=scatter,
                            scatter_results=scatter_results,
                            heatmap=heatmap,
                            version=int(time.time()))


# define a route that downloads charts asa csv file
@app.route('/download', methods=['GET'])
def download_chart():
    # get user choices from link
    state = request.args.get('state')
    measure = request.args.get('measure')
    estimate = request.args.get('estimate', 'CrudePrev')

    # stop if user hasn't provided required parameters
    if not state or not measure:
        return "Choose a state and health measure first."

    # get the counties with data, ranked highest to lowest
    df = get_state_data(state)
    column = MEASURES[measure] + "_" + estimate
    results = df[['CountyName', column]].dropna()
    results = results.sort_values(column, ascending=False)

    # give the columns readable names and add a rank column
    results.columns = ['County', f"{measure} (%)"]
    results.insert(0, 'Rank',
                   results[f'{measure} (%)'].rank(ascending=False, method='min').astype(int))

    # turn table into csv text and send it as a file
    csv_text = results.to_csv(index=False)
    filename = f"{state}_{measure}_results.csv".replace(" ", "_")
    return Response(csv_text, mimetype="text/csv", headers={"Content-Disposition": f"attachment; filename={filename}"})

# run the app 
if __name__ == '__main__':
    app.run(debug=True)
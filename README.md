# County Health Explorer

CS 122  Project - Fall 2026







Author 1: Huu Tinh Nguyen (Data collection and storage)

Author 2: Ramjot Dhillon (Data analysis and visualization)

Ramjot Dhillon, Huu Tinh Nguyen



Project Description (5 sentences):

Our project will use the CDC PLACES county dataset to compare health estimates across counties. We will focus on obesity, diabetes, and physical inactivity. Users will be able to choose a state and health measure and see county results on a website. The program will download the data, save cleaned records in a local database, and create charts. We will explain missing values and avoid treating county comparisons as proof of cause and effect.



Project Outline/Plan

- Download the county CSV from the CDC website.
- Check the columns, county IDs, and missing values.
- Save cleaned data in a local SQLite database.
- Build a Data page and an Analysis page with Flask.
- Calculate county summaries and compare health measures.
- Make charts and let users download results.
- Test the download, filters, database, and charts.



Interface Plan

We plan to make a two page Flask website. I will build the Data page so users can download the CSV, see when it was last downloaded, and browse county records. Ramjot will build the Analysis page so users can choose measures, see summaries, and make charts. We will connect both pages to the same SQLite database.

The website will have at least ten controls: a Download Data button, a Reload Saved Data button, a state dropdown, a county search box, a health measure dropdown, a crude or adjusted estimate selector, an Apply Filters button, a Reset Filters button, a chart type selector, a Compare Measures button, a Download Results button, and a Save Chart button. We will also include links between the two pages. If a selection has no usable data, the page will show a message explaining that.



Data Collection and Storage Plan (Author 1: Huu Tinh Nguyen)

I will make the program download the county CSV from the public CDC PLACES dataset at https://data.cdc.gov/d/i46a-9kgh. I will keep a copy of the original download and record the source and date. I will use the supplied CSV to test the import first.

The supplied file has 3,143 county rows and 167 columns. I will check for required columns and duplicate county FIPS codes. I will store FIPS codes as text so leading zeroes stay intact, remove commas before converting population values to numbers, and keep blank estimates as missing values instead of turning them into zeroes.

I plan to use Python's sqlite3 library. One table will store county names, states, FIPS codes, and populations. A second table will store health measures, estimates, and confidence intervals for each county. The import will report invalid data and avoid creating duplicate records when the file is downloaded again.




Data Analysis and Visualization Plan (Author 2: Ramjot Dhillon)

Ramjot will focus on obesity, diabetes, and physical inactivity. For a selected state and measure, she plans to calculate the number of counties with data, the number with missing values, and the mean, median, lowest, and highest available estimates. We will label county averages clearly because an average of county estimates is not the same as an official state estimate.

Ramjot plans to use Matplotlib to make a county comparison chart, a histogram, and a scatterplot comparing two measures. She will label each chart with the measure, type of estimate, and number of counties included. When a comparison needs two measures, she will use counties with both values and report how many were excluded. We will treat the results as county level patterns, not as proof of cause and effect.

## Data Source

CDC PLACES: County Data (GIS Friendly Format), 2025 release
https://catalog.data.gov/dataset/places-county-data-gis-friendly-format-2025-release-ddbcc

This README describes our plan for the final project. The program has not been built yet.


from flask import Flask, jsonify
from data.data_scraper import scrape_average_salary_all_years, scrape_dollar_rate_all_years, scrape_unemployment_data, \
    scrape_dollar_rate_certain_year
from data.db_handler import check_connection, create_databases, insert_salary_data as db_insert_salary_data, \
    insert_unemployment_data, \
    insert_dollar_rate_data as db_insert_dollar_rate_data, clear_table

from salary_predictor.salary_predictor import prediction_for_all_regions, prediction_for_certain_region

app = Flask(__name__)


@app.route('/api/check_connection', methods=['GET'])
def check_db_connection():
    if check_connection():
        return jsonify({'status': 'success', 'message': 'Database connection is successful'})
    else:
        return jsonify({'status': 'error', 'message': 'Failed to establish a connection to the database'})


@app.route('/api/salary_data', methods=['GET'])
def get_salary_data():
    results = scrape_average_salary_all_years()
    return jsonify(results)


@app.route('/api/dollar_rate_data/', methods=['GET'])
def get_dollar_rate_data():
    results = scrape_dollar_rate_all_years()
    return jsonify(results)


@app.route('/api/dollar_rate_data/<int:year>', methods=['GET'])
def scrape_dollar_rate_for_year(year):
    dollar_rates = scrape_dollar_rate_certain_year(year)
    return jsonify(dollar_rates)


@app.route('/api/unemployment_rate_data', methods=['GET'])
def get_unemployment_rate_data():
    results = scrape_unemployment_data()
    return jsonify(results)


@app.route('/api/create_dbs', methods=['GET'])
def create_dbs():
    create_databases()
    return jsonify({'status': 'success', 'message': 'Databases were created successfully'})


@app.route('/api/insert_salary_data', methods=['POST'])
def insert_salary_data():
    try:
        results = scrape_average_salary_all_years()

        for year, regions in results.items():
            for region, months in regions.items():
                for month, average_salary in months.items():
                    db_insert_salary_data(year, region, month, average_salary)
        return jsonify({"status": "success", "message": "Average salary data inserted successfully."})
    except Exception as e:
        return jsonify({"status": "error", "message": f"Error: {e}"})


@app.route('/api/insert_dollar_rate_data', methods=['POST'])
def insert_dollar_rate_data():
    try:
        dollar_rates = scrape_dollar_rate_all_years()
        for year, months_data in dollar_rates.items():
            for month, rates in months_data.items():
                db_insert_dollar_rate_data(year, month, rates.get('buy', 0), rates.get('sell', 0))

        return jsonify({"status": "success", "message": "Dollar rate data inserted successfully."})

    except Exception as e:
        return jsonify({"status": "error", "message": f"Error: {e}"})


@app.route('/api/insert_unemployment_rate_data', methods=['POST'])
def insert_unemployment_rate_data():
    try:
        results = scrape_unemployment_data()
        for year, rate in results.items():
            insert_unemployment_data(year, rate)
        return jsonify({"status": "success", "message": "Unemployment rate data inserted successfully."})
    except Exception as e:
        return jsonify({"status": "error", "message": f"Error: {e}"})


@app.route('/api/clear_table/<string:table>', methods=['DELETE'])
def clear_selected_table(table):
    clear_table(table)
    return jsonify({"status": "success", "message": "Selected table was cleared successfully."})


@app.route('/api/predict_all_regions/<int:year>', methods=['GET'])
def predict_all_regions(year):
    return jsonify(prediction_for_all_regions(year - 1))


@app.route('/api/predict_certain_region/<int:year>/<string:region>', methods=['GET'])
def predict_certain_region(year, region):
    return jsonify(prediction_for_certain_region(year, region))


if __name__ == '__main__':
    app.run(debug=True)

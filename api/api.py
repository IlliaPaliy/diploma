from flask import Flask, jsonify
from data.data_scraper import scrape_all_years
from data.db_handler import check_connection

app = Flask(__name__)

# Check if the database connection is successful
@app.route('/api/check_connection', methods=['GET'])
def check_db_connection():
    if check_connection():
        return jsonify({'status': 'success', 'message': 'Database connection is successful'})
    else:
        return jsonify({'status': 'error', 'message': 'Failed to establish a connection to the database'})

# API endpoint to get all salary data
@app.route('/api/salary_data', methods=['GET'])
def get_salary_data():
    results = scrape_all_years()
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)
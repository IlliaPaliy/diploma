from flask import Flask, jsonify
from data.data_scraper import scrape_all_years
from data.db_handler import check_connection, create_databases

app = Flask(__name__)

@app.route('/api/check_connection', methods=['GET'])
def check_db_connection():
    if check_connection():
        return jsonify({'status': 'success', 'message': 'Database connection is successful'})
    else:
        return jsonify({'status': 'error', 'message': 'Failed to establish a connection to the database'})

@app.route('/api/salary_data', methods=['GET'])
def get_salary_data():
    results = scrape_all_years()
    return jsonify(results)

@app.route('/api/create_dbs', methods=['GET'])
def create_dbs():
    create_databases()
    return jsonify({'status': 'success', 'message': 'Databases were created successfully'})

if __name__ == '__main__':
    app.run(debug=True)
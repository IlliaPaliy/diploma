from salary_scraper import scrape_all_years, scrape_certain_year
from db_handler import create_database, insert_data, check_connection

if __name__ == "__main__":
    create_database()

    if check_connection():
        print("Connection to the database established successfully.")
    else:
        print("Failed to establish a connection to the database.")

    results = scrape_all_years()

    for year, regions in results.items():
        for region, months in regions.items():
            for month, average_salary in months.items():
                insert_data(year, region, month, average_salary)

    print("Data successfully stored in the database.")
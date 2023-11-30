import re
import requests
from bs4 import BeautifulSoup

salaries = {}

def scrape_salary_data(url, data_selector_table, salaries_array):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            tables = soup.select(data_selector_table);
            all_rows = []
            pattern = re.compile(r'>\s*(.*?)\s*<')
            for table in tables:
                rows = table.select('tr')
                all_rows.extend(rows)
            for row in all_rows:
                td_elements = row.select('td')
                month_counter = 0
                finished = False
                for cell in td_elements:
                    if("first-column" in str(cell)):
                        region_name = pattern.findall(str(cell))
                        if(region_name[0] in salaries_array):
                            continue
                        else:
                            salaries_array[region_name[0]] = {}
                    else:
                        salary_element = cell
                        if salary_element:
                            try:
                                average_salary = float(salary_element.text.replace(',', ''))
                                # print(f'Average Salary on {region_name[0]}: {average_salary}')
                                if(len(salaries_array[region_name[0]])<3):
                                    if(month_counter==0):
                                        salaries_array[region_name[0]]["січень"] = average_salary
                                    elif month_counter==1:
                                        salaries_array[region_name[0]]["лютий"] = average_salary
                                    else:
                                        salaries_array[region_name[0]]["березень"] = average_salary
                                        finished = True
                                if (3 <= len(salaries_array[region_name[0]]) < 6 and finished == False):
                                    if (month_counter == 0):
                                        salaries_array[region_name[0]]["квітень"] = average_salary
                                    elif month_counter == 1:
                                        salaries_array[region_name[0]]["травень"] = average_salary
                                    else:
                                        salaries_array[region_name[0]]["червень"] = average_salary
                                        finished = True
                                if (6 <= len(salaries_array[region_name[0]]) < 9 and finished == False):
                                    if (month_counter == 0):
                                        salaries_array[region_name[0]]["липень"] = average_salary
                                    elif month_counter == 1:
                                        salaries_array[region_name[0]]["серпень"] = average_salary
                                    else:
                                        salaries_array[region_name[0]]["вересень"] = average_salary
                                        finished = True
                                if (len(salaries_array[region_name[0]]) >= 9 and finished == False):
                                    if (month_counter == 0):
                                        salaries_array[region_name[0]]["жовтень"] = average_salary
                                    elif month_counter == 1:
                                        salaries_array[region_name[0]]["листопад"] = average_salary
                                    else:
                                        salaries_array[region_name[0]]["грудень"] = average_salary
                                        finished = True
                                month_counter+=1
                            except Exception as e:
                                continue
                        else:
                            print('Could not find the salary data element in a row.')
        else:
            print(f'Failed to retrieve data. Status code: {response.status_code}')
    except Exception as e:
        print(f'Error: {e}')
    return salaries_array

def scrape_all_years():
    for year in range(2010, 2023):
        salaries[str(year)] = {}
        salaries[str(year)] = scrape_salary_data('https://index.minfin.com.ua/ua/labour/salary/average/' + str(year), '.glue-table', salaries[str(year)])
    return salaries

def scrape_certain_year(year):
    salaries[str(year)] = {}
    salaries[str(year)] = scrape_salary_data('https://index.minfin.com.ua/ua/labour/salary/average/' + str(year),'.glue-table', salaries[str(year)])
    return salaries
# if __name__ == "__main__":



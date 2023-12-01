import requests
from bs4 import BeautifulSoup
import re


salaries = {}
dollar_rates = {}
months_dictionary = {"1": "січень", "2": "лютий", "3": "березень",
          "4": "квітень", "5": "травень", "6":"червень",
          "7": "липень", "8": "серпень", "9": "вересень",
          "10": "жовтень", "11": "листопад", "12": "грудень"}


def scrape_unemployment_data(url="https://index.minfin.com.ua/ua/labour/unemploy/"):
    unemployment_rates = {}
    year = 2000
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            table = soup.select("#idx-wrapper table")
            rows = table[1].select("big")
            for row in rows:
                unemployment_rate = float(row.text.replace(',', '.'))
                unemployment_rates[str(year)] = unemployment_rate
                year+=1
        else:
            return (f'Failed to retrieve data. Status code: {response.status_code}')
    except Exception as e:
        return (f'Error: {e}')
    return unemployment_rates


def scrape_dollar_rate(url, dollar_rate_array):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            tables = soup.select('.idx-currency table')
            for table in tables:
                caption = table.select("caption")
                if('Середній курс обміну валют' in str(caption[0])):
                    rows = table.select("tr")
                    for row in rows:
                        if('долар США' in str(row)):
                            buy_rate_cell = row.select("td:nth-child(3)")
                            sell_rate_cell = row.select("td:nth-child(6)")
                            buy_rate = float(buy_rate_cell[0].text.replace(',', '.'))
                            sell_rate = float(sell_rate_cell[0].text.replace(',', '.'))
                            dollar_rate_array['buy'] = buy_rate
                            dollar_rate_array['sell'] = sell_rate
                            break
                    break
            return dollar_rate_array
        else:
            print(f'Failed to retrieve data. Status code: {response.status_code}')
    except Exception as e:
        print(f'Error: {e}')


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
                            print ('Could not find the salary data element in a row.')
        else:
            return (f'Failed to retrieve data. Status code: {response.status_code}')
    except Exception as e:
        return (f'Error: {e}')
    return salaries_array

def scrape_average_salary_all_years():
    for year in range(2010, 2023):
        salaries[str(year)] = {}
        salaries[str(year)] = scrape_salary_data('https://index.minfin.com.ua/ua/labour/salary/average/' + str(year), '.glue-table', salaries[str(year)])
    return salaries

def scrape_average_salary_certain_year(year):
    salaries[str(year)] = {}
    salaries[str(year)] = scrape_salary_data('https://index.minfin.com.ua/ua/labour/salary/average/' + str(year),'.glue-table', salaries[str(year)])
    return salaries

def scrape_dollar_rate_all_years():
    for year in range(2010, 2022):
        dollar_rates[str(year)] = {}
        for month in range(1, 13):
            if (month < 10):
                month_str = '0' + str(month)
            else:
                month_str = str(month)
            dollar_rates[str(year)][months_dictionary[str(month)]] = {}
            dollar_rates[str(year)][months_dictionary[str(month)]] = scrape_dollar_rate('https://index.minfin.com.ua/ua/exchange/archive/' + str(year) +'-'+ month_str +'-10', dollar_rates[str(year)][months_dictionary[str(month)]])
    return dollar_rates

def scrape_dollar_rate_certain_year(year):
    dollar_rates[str(year)] = {}
    for month in range(1, 13):
        if (month < 10):
            month_str = '0' + str(month)
        else:
            month_str = str(month)
        dollar_rates[str(year)][months_dictionary[str(month)]] = {}
        dollar_rates[str(year)][months_dictionary[str(month)]] = scrape_dollar_rate('https://index.minfin.com.ua/ua/exchange/archive/' + str(year) + '-' + month_str + '-10', dollar_rates[str(year)][months_dictionary[str(month)]])
    return dollar_rates


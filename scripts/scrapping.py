from multiprocessing.pool import ThreadPool
from selenium import webdriver
from selenium.webdriver.common.by import By


def get_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome('bins/chromedriver', options = options)
    return driver

def get_paths(path):
    driver = get_driver()
    driver.get(path)
    
    match_paths = list(map(lambda x: x.get_dom_attribute('href'), 
                           driver.find_elements(By.CLASS_NAME, 'ind_match_wrapper')))
    match_paths = match_paths[1:]
    match_paths = list(map(lambda x: 'https://www.xscores.com/' + x, match_paths))
    teams = list(map(lambda x: x.split('/')[-3].split('-vs-'), match_paths))
    
    driver.close()
    driver.quit()
    return match_paths, teams

def get_info(path):
    driver = get_driver()
    driver.get(path)
        
    date = driver.find_element(By.CLASS_NAME, 'match_details_date').text
    bets = driver.find_element(By.CLASS_NAME, 'mDetails-odds').text.split('\n')[1::2]
        
    driver.close()
    driver.quit()
    return date, bets
    
def get_stats(paths):
    with ThreadPool(40) as p:
        results = p.map(get_info, paths)
    return results

def get_data(website_path):
    #path = 'https://www.xscores.com/soccer/england/premier-league'
    paths, teams = get_paths(website_path)
    stats = get_stats(paths)
    data = list(zip(teams, stats))
    return data
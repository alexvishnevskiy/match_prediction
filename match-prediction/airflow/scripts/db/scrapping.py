from datetime import datetime
from typing import Iterable
from tqdm import tqdm
import time
import re

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.command import Command
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException


def get_driver():
    def _driver():
        options = webdriver.ChromeOptions()
        options.add_argument('--no-sandbox')
        options.add_argument("--headless")
        driver = webdriver.Chrome(ChromeDriverManager().install(), options = options)
        return driver

    def get_status(driver):
        try:
            driver.execute(Command.STATUS)
            return True
        except:
            return False

    start_time = time.time()
    driver = _driver()
    while not get_status(driver):
        driver = _driver()
        if time.time() - start_time > 30:
            raise TimeoutError("driver is not initialized")
    return driver

def get_paths(driver):
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, 'ind_match_wrapper')))
    match_paths = list(map(lambda x: x.get_dom_attribute('href'), 
                           driver.find_elements(By.CLASS_NAME, 'ind_match_wrapper')))
    match_paths = match_paths[1:]
    match_paths = list(map(lambda x: 'https://www.xscores.com/' + x, match_paths))
    teams = list(map(lambda x: x.split('/')[-3].split('-vs-'), match_paths))
    return match_paths, teams

def get_match_stats(driver, path):
    def get_ftr(score_1, score_2):
        if score_1 > score_2:
            return 'H'
        elif score_1 < score_2:
            return 'A'
        else:
            return 'D'
        
    try:       
        driver.get(path)

        regex_ref = re.compile("Referee: ((\w+|\s*)+)\n*")
        regex_stat = lambda x: re.compile(f"{x}\n(\d+)\n(\d+)")

        stats_dict = dict()
        stat_attrs = [
            ('Goal Attempts', 'hs', 'as'), 
            ('Fouls Commited', 'hf', 'af'), 
            ('Corners', 'hc', 'ac'),
            ('Yellow Cards', 'hy', 'ay'), 
            ('Red Cards', 'hr', 'ar')
        ]

        score = (
            WebDriverWait(driver, 20)
            .until(EC.presence_of_element_located((By.CLASS_NAME, 'match_details_score'))).text.split(' - ')
            )
        date = (
            WebDriverWait(driver, 20)
            .until(EC.presence_of_element_located((By.CLASS_NAME, 'match_details_date'))).text
        )
        date = datetime.strptime(date, 'Match date: %d-%m-%Y / %H:%M')
        try:
            game_info_overview = (
                WebDriverWait(driver, 20)
                .until(EC.presence_of_element_located((By.CLASS_NAME, 'game_info_overview'))).text
            )
            bet1x, betx, bet2x = (
                WebDriverWait(driver, 20)
                .until(EC.presence_of_element_located((By.CLASS_NAME, 'mDetails-odds'))).text.split('\n')[1::2]
            )
            referee = regex_ref.search(game_info_overview).group(1)
        except:
            referee, bet1x, betx, bet2x = None, None, None, None

        stats_dict['Date'] = date
        stats_dict['referee'] = referee
        stats_dict['B365H'] = bet1x
        stats_dict['B365D'] = betx
        stats_dict['B365A'] = bet2x
        stats_dict['played'] = 0

        stats_dict['fthg'] = None
        stats_dict['ftag'] = None
        stats_dict['ftr'] = None
        for stat_name, h_stat, a_stat in stat_attrs:
            stats_dict[h_stat] = None
            stats_dict[a_stat] = None

        #if match has been played
        if len(score) != 1:
            stats_dict['played'] = 1
            stats_dict['fthg'] = score[0]
            stats_dict['ftag'] = score[1]
            stats_dict['ftr'] = get_ftr(score[0], score[1])

            element = (
                WebDriverWait(driver, 20)
                .until(EC.element_to_be_clickable((By.XPATH, '//*[@id="scoretable"]/div/div[6]/div/div/div/div[4]')))
                .click()
            )
            start_time = time.time()
            stats = ''
            while stats == '':
                stats = driver.find_element(By.CLASS_NAME, 'match_info_wrapper').text
                time.sleep(0.5)
                if time.time() - start_time > 10:
                    raise TimeoutError

            for stat_name, h_stat, a_stat in stat_attrs:
                match_info = regex_stat(stat_name).search(stats)
                stats_dict[h_stat] = match_info.group(1)
                stats_dict[a_stat] = match_info.group(2)
    except Exception as e:
        print(e)

    return stats_dict

def max_rounds(path):
    driver = get_driver()
    driver.get(path)
    round_select = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, 'round_select')))
    max_rounds = int(round_select.text.split('\n')[-1])
    return max_rounds

def get_round_links(path: str, rounds_n: Iterable):
    try:
        driver = get_driver()
        driver.get(path)

        round_selection = lambda x: (
            WebDriverWait(driver, 20, ignored_exceptions=StaleElementReferenceException)
            .until(EC.presence_of_element_located((By.CLASS_NAME, 'round_select')))
            .find_elements_by_tag_name("option")[x-1].click()
        )

        match_paths, pair_teams = [], []
        for n in tqdm(rounds_n, desc = 'getting round links'):
            round_selection(n)
            time.sleep(1)
            paths, teams = get_paths(driver)
            match_paths.extend(paths)
            pair_teams.extend(teams)
    except Exception as e:
        print(e)
    finally:
        driver.close()
        driver.quit()
    return match_paths, pair_teams

def get_matches_stats(path, rounds_n: Iterable):
    stats_data = []
    driver = get_driver()
    links, matches = get_round_links(path, rounds_n)
    
    for link in tqdm(links, desc = 'getting stats about matches'):
        match_stats = get_match_stats(driver, link)
        if match_stats['B365H'] != 'OFF':
            stats_data.append(match_stats)
        
    for stat_dict, teams in zip(stats_data, matches):
        stat_dict['HomeTeam'] = teams[0]
        stat_dict['AwayTeam'] = teams[1]
        
    driver.close()
    driver.quit()
    return stats_data

def get_all_matches_stats(path):
    #rounds_n = range(1, max_rounds(path)+1)
    rounds_n = range(1, 17)
    stats_data = get_matches_stats(path, rounds_n)
    return stats_data
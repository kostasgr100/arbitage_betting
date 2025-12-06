import selenium
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time, csv
import pandas as pd

#################################### Football ####################################################

def novibet_football_text(page_url: str, driver: selenium.webdriver.chrome.webdriver.WebDriver) -> str:    
    driver.get(page_url)
    try:
        cookies = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.CLASS_NAME, 'acceptCookies_button')))
        cookies.click()
    except:
        pass
        
    try:
        x_button = driver.find_element(By.CSS_SELECTOR, '[data-cy="closeBtn"]')
        x_button.click()
    except:
        pass

    # Click Daily Coupon (Football)
    try:
        daily_coupon_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'a.ng-star-inserted[title="Daily coupon"]')))
        daily_coupon_button.click()
    except:
        print("Could not find Daily Coupon button")

    time.sleep(5)
    wait = WebDriverWait(driver, 10)
    daily_coupon_body = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'dailyCoupon_body')))
    return daily_coupon_body.text


def novibet_football_export(football_string: str): 
    initial_list = football_string.split('\n')
    remove_elements = ['Daily coupon','Football','Tennis','Basketball',
                       '24 hours','12 hours','3 hours','Popular First','SO']
    football_list = [x for x in initial_list if x not in remove_elements]

    # Padding logic for 'Markets are not available'
    index = 0
    consecutive_count = 0
    while index < len(football_list):
        if football_list[index] == 'Markets are not available':
            football_list.insert(index+1, 'No_market')
            football_list.insert(index+2, 'No_market')
            football_list.insert(index+3, 'No_market')
            index += 4
            consecutive_count += 1 
            if consecutive_count == 3:
                 football_list.insert(index, 'No_market')
                 consecutive_count = 0
        else:
            index += 1
            consecutive_count = 0
    
    # Create sublists based on Championship
    index_championship = [i for i,x in enumerate(football_list) if ' - ' in x]
    sublists_championships = [football_list[i:j] for i, j in zip([0]+index_championship, index_championship + [len(football_list)])]
    sublists_championships = sublists_championships[1:]
    
    # Prepare list for DataFrame
    all_data = []

    for j in range(len(sublists_championships)):          
        teams_only_lst = sublists_championships[j][1:]
        championship_name = sublists_championships[j][0]
        
        # Process in chunks of 18 (Novibet structure)
        for i in range(0, len(teams_only_lst), 18):
            chunk = teams_only_lst[i:i+18]
            if len(chunk) == 18:
                all_data.append({
                    'Championship': championship_name,
                    'Team1': chunk[0],
                    'Team2': chunk[1],
                    'Time': chunk[2],
                    'One': chunk[3], 'One_odd': chunk[4],
                    'X': chunk[5], 'X_odd': chunk[6],
                    'Two': chunk[7], 'Two_odd': chunk[8],
                    'Over': chunk[9], 'O_odd': chunk[10],
                    'Under': chunk[11], 'U_odd': chunk[12],
                    'GG': chunk[13], 'GG_odd': chunk[14],
                    'NG': chunk[15], 'NG_odd': chunk[16]
                })

    # Create DataFrame once
    df_football = pd.DataFrame(all_data)
    
    # Save
    output_file = 'data/novibet_football.csv'
    df_football.to_csv(output_file, index=False, encoding='utf-8')


#################################### Basketball #########################################################     

def novibet_basketball_text(driver: selenium.webdriver.chrome.webdriver.WebDriver) -> str:  
    driver.get("https://www.novibet.gr/en/sports")
    time.sleep(3)
    try:
        basketball_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '[class*="BASKETBALL_GAME"]')))
        basketball_button.click()
    except:
        pass
        
    time.sleep(5)
    wait = WebDriverWait(driver, 10)
    daily_coupon_body = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'dailyCoupon_body')))
    return daily_coupon_body.text


def novibet_basketball_export(basketball_string: str):
    initial_list = basketball_string.split('\n')
    remove_elements = ['Daily coupon','Football','Tennis','Basketball',
                    '24 hours','12 hours','3 hours','Popular First','SO']
    basketball_list = [x for x in initial_list if x not in remove_elements]

    index = 0
    consecutive_count = 0
    while index < len(basketball_list):
        if basketball_list[index] == 'Markets are not available':
            basketball_list.insert(index+1, 'No_market')
            basketball_list.insert(index+2, 'No_market')
            basketball_list.insert(index+3, 'No_market')
            index += 4
            consecutive_count += 1 
            if consecutive_count == 3:
                 basketball_list.insert(index, 'No_market')
                 consecutive_count = 0
        else:
            index += 1
            consecutive_count = 0

    index_championship = [i for i,x in enumerate(basketball_list) if ' - ' in x]
    sublists_championships = [basketball_list[i:j] for i, j in zip([0]+index_championship, index_championship + [len(basketball_list)])]
    sublists_championships = sublists_championships[1:]

    all_data = []

    for j in range(len(sublists_championships)):          
        teams_only_lst = sublists_championships[j][1:]
        championship_name = sublists_championships[j][0]

        for i in range(0, len(teams_only_lst), 16):
            chunk = teams_only_lst[i:i+16]
            if len(chunk) == 16:
                all_data.append({
                    'Championship': championship_name,
                    'Team1': chunk[0], 'Team2': chunk[1], 'Time': chunk[2],
                    'Win1': chunk[3], 'Win1_odd': chunk[4],
                    'Win2': chunk[5], 'Win2_odd': chunk[6],
                    'Over': chunk[7], 'O_odd': chunk[8],
                    'Under': chunk[9], 'U_odd': chunk[10],
                    'One': chunk[11], 'One_odd': chunk[12],
                    'Two': chunk[13], 'Two_odd': chunk[14]
                })

    df_basketball = pd.DataFrame(all_data)
    output_file = "data/novibet_basketball.csv"
    df_basketball.to_csv(output_file, index=False, encoding='utf-8')


#################################### Tennis ######################################################### 

def novibet_tennis_text(driver: selenium.webdriver.chrome.webdriver.WebDriver) -> str:  
    driver.get("https://www.novibet.gr/en/sports")
    time.sleep(3)
    try:
        tennis_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '[class*="TENNIS_SINGLES_MATCH"]')))
        tennis_button.click()
    except:
        pass
        
    time.sleep(5)
    wait = WebDriverWait(driver, 10)
    daily_coupon_body = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'dailyCoupon_body')))
    return daily_coupon_body.text


def novibet_tennis_export(tennis_string: str):
    initial_list = tennis_string.split('\n')
    remove_elements = ['Daily coupon','Football','Tennis','Basketball',
                    '24 hours','12 hours','3 hours','Popular First','SO']
    tennis_list = [x for x in initial_list if x not in remove_elements]

    index = 0
    consecutive_count = 0
    while index < len(tennis_list):
        if tennis_list[index] == 'Markets are not available':
            tennis_list.insert(index+1, 'No_market')
            tennis_list.insert(index+2, 'No_market')
            tennis_list.insert(index+3, 'No_market')
            index += 4
            consecutive_count += 1 
            if consecutive_count == 3:
                 tennis_list.insert(index, 'No_market')
                 consecutive_count = 0 
        else:
            index += 1
            consecutive_count = 0

    index_championship = [i for i,x in enumerate(tennis_list) if ' - ' in x]
    sublists_championships = [tennis_list[i:j] for i, j in zip([0]+index_championship, index_championship + [len(tennis_list)])]
    sublists_championships = sublists_championships[1:]

    all_data = []

    for j in range(len(sublists_championships)):       
        teams_only_lst = sublists_championships[j][1:]
        championship_name = sublists_championships[j][0]

        for i in range(0, len(teams_only_lst), 16):
            chunk = teams_only_lst[i:i+16]
            if len(chunk) == 16:
                all_data.append({
                    'Championship': championship_name,
                    'Player1': chunk[0], 'Player2': chunk[1], 'Time': chunk[2],
                    'One': chunk[3], 'One_odd': chunk[4],
                    'Two': chunk[5], 'Two_odd': chunk[6],
                    'Over': chunk[7], 'O_odd': chunk[8],
                    'Under': chunk[9], 'U_odd': chunk[10],
                    'Win1': chunk[11], 'Win1_odd': chunk[12],
                    'Win2': chunk[13], 'Win2_odd': chunk[14]
                })

    df_tennis = pd.DataFrame(all_data)
    output_file = "data/novibet_tennis.csv"
    df_tennis.to_csv(output_file, index=False, encoding='utf-8')

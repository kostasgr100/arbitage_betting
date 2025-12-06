import selenium
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time, csv
import re

######################################### Football ####################################################

def efbet_football_text(driver: selenium.webdriver.chrome.webdriver.WebDriver) -> str:
    # Direct deep link to Soccer
    url = 'https://www.efbet.gr/en/sports/pre-match/event-view/Soccer'
    driver.get(url)
    
    # Wait for SPA to load
    wait = WebDriverWait(driver, 15)
    time.sleep(3)

    # 1. Handle Cookie Consent
    try:
        # Generic XPath to find any "Accept" button for cookies
        cookie_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Accept') or contains(text(), 'Agree')]")))
        cookie_btn.click()
        time.sleep(1)
    except:
        pass # Cookies might be already accepted or banner not present

    # 2. Apply "24h" or "Today" Filter
    try:
        # Efbet time filters are usually spans or buttons. We look for '24h' or 'Today'.
        filter_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), '24h') or contains(text(), 'Today')]")))
        filter_btn.click()
        time.sleep(3) # Allow DOM to update
    except Exception as e:
        print(f"Efbet Football: Could not find or click 24h filter. Proceeding with default view. ({e})")

    # 3. Infinite Scroll to load all matches
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2) # Wait for lazy load
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    # 4. Extract Text from Main Container
    try:
        # 'center-view-content' is the standard class for the middle betting column on Efbet
        container = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.center-view-content")))
        football_string = container.text
    except Exception as e:
        print(f"Efbet Football: Error extracting text. {e}")
        football_string = ""

    return football_string 


def efbet_football_export(football_string: str):
    initial_list = football_string.split('\n')
    
    # Garbage cleaning - remove headers and non-match text
    remove_elements = [
        'Soccer', 'All', '1', 'X', '2', 'Over', 'Under', 'BTS', 
        'Double Chance', 'Draw No Bet', 'Winner', 'Handicap', 'Goals', 
        'Halftime', 'Corners', 'Cards'
    ]
    # Filter out garbage and short strings
    clean_lines = [x for x in initial_list if x not in remove_elements and len(x) > 1]
    
    # Identify match rows based on Time (HH:MM) or Date (DD/MM) pattern at the start
    # Regex checks for "14:00" or "24/03"
    indices = [i for i, x in enumerate(clean_lines) if (re.match(r'^\d{2}:\d{2}$', x) or re.match(r'^\d{2}/\d{2}$', x))]
    
    sublists_matches = []
    if indices:
        # Slice the list into chunks based on match start indices
        sublists_matches = [clean_lines[i:j] for i, j in zip(indices, indices[1:] + [len(clean_lines)])]
        
        # Standardize columns to 15 to match the database schema
        # Expected structure: [Time, Team1, Team2, 1, X, 2, O_odds, U_odds, ...]
        target_len = 15
        for sublist in sublists_matches:
            if len(sublist) < target_len:
                sublist.extend(['No_bet'] * (target_len - len(sublist)))
            elif len(sublist) > target_len:
                sublist[:] = sublist[:target_len]
    
    # Save to CSV
    output_file = "data/efbet_football.csv"
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        # Headers compatible with your DuckDB queries
        writer.writerow(['Time', 'Team1', 'Team2', '1', 'X', '2', 'O_odds', 'U_odds', 
                         'misc1', 'misc2', 'misc3', 'misc4', 'misc5', 'misc6', 'misc7'])
        for row in sublists_matches:
            writer.writerow(row)


######################################## Basketball ####################################################

def efbet_basketball_text(driver: selenium.webdriver.chrome.webdriver.WebDriver) -> str:
    url = 'https://www.efbet.gr/en/sports/pre-match/event-view/Basketball'
    driver.get(url)
    wait = WebDriverWait(driver, 15)
    time.sleep(3)

    # 1. Cookie
    try:
        wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Accept') or contains(text(), 'Agree')]"))).click()
        time.sleep(1)
    except:
        pass

    # 2. Filter
    try:
        wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), '24h') or contains(text(), 'Today')]"))).click()
        time.sleep(3)
    except:
        pass

    # 3. Scroll
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    # 4. Extract
    try:
        container = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.center-view-content")))
        basketball_string = container.text
    except:
        basketball_string = ""
        
    return basketball_string


def efbet_basketball_export(basketball_string: str):
    initial_list = basketball_string.split('\n')
    
    # Garbage cleaning
    remove_elements = ['Basketball', 'Winner', 'Handicap', 'Over/Under', 'Total', '1', '2', 'Points', 'Half', 'Quarter']
    clean_lines = [x for x in initial_list if x not in remove_elements and len(x) > 1]
    
    # Identify Matches
    indices = [i for i, x in enumerate(clean_lines) if re.match(r'^\d{2}:\d{2}$', x) or re.match(r'^\d{2}/\d{2}$', x)]
    
    sublists_matches = []
    if indices:
        sublists_matches = [clean_lines[i:j] for i, j in zip(indices, indices[1:] + [len(clean_lines)])]
        
        target_len = 12
        for sublist in sublists_matches:
            if len(sublist) < target_len:
                sublist.extend(['No_bet'] * (target_len - len(sublist)))
            elif len(sublist) > target_len:
                sublist[:] = sublist[:target_len]

    # Save to CSV
    output_file = "data/efbet_basketball.csv"
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Time', 'Team1', 'Team2', '1', '2', 'Hand_Val', 'H1', 'H2', 'Tot_Val', 'O', 'U', 'misc'])
        for row in sublists_matches:
            writer.writerow(row)


########################################## Tennis ######################################################

def efbet_tennis_text(driver: selenium.webdriver.chrome.webdriver.WebDriver) -> str:
    url = 'https://www.efbet.gr/en/sports/pre-match/event-view/Tennis'
    driver.get(url)
    wait = WebDriverWait(driver, 15)
    time.sleep(3)

    # 1. Cookie
    try:
        wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Accept') or contains(text(), 'Agree')]"))).click()
        time.sleep(1)
    except:
        pass

    # 2. Filter
    try:
        wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), '24h') or contains(text(), 'Today')]"))).click()
        time.sleep(3)
    except:
        pass

    # 3. Scroll
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    # 4. Extract
    try:
        container = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.center-view-content")))
        tennis_string = container.text
    except:
        tennis_string = ""
        
    return tennis_string


def efbet_tennis_export(tennis_string: str):
    initial_list = tennis_string.split('\n')
    
    # Garbage cleaning
    remove_elements = ['Tennis', 'Winner', 'Handicap', 'Over/Under', 'Total', '1', '2', 'Sets', 'Games']
    clean_lines = [x for x in initial_list if x not in remove_elements and len(x) > 1]
    
    # Identify Matches
    indices = [i for i, x in enumerate(clean_lines) if re.match(r'^\d{2}:\d{2}$', x) or re.match(r'^\d{2}/\d{2}$', x)]
    
    sublists_matches = []
    if indices:
        sublists_matches = [clean_lines[i:j] for i, j in zip(indices, indices[1:] + [len(clean_lines)])]
        
        target_len = 10
        for sublist in sublists_matches:
            if len(sublist) < target_len:
                sublist.extend(['No_bet'] * (target_len - len(sublist)))
            elif len(sublist) > target_len:
                sublist[:] = sublist[:target_len]

    # Save to CSV
    output_file = "data/efbet_tennis.csv"
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Time', 'Player1', 'Player2', '1', '2', 'Set1', 'Set2', 'Games_O', 'Games_U', 'misc'])
        for row in sublists_matches:
            writer.writerow(row)
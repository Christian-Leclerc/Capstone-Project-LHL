from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from IPython.display import display, clear_output # for Jupyter Notebook only
import subprocess # for VSCode
import json
import time

# Environment variable
import os
sensitive_url = os.getenv('SENSITIVE_URL').split(',')

# Clear terminal screen
def clear_terminal():
    os.system('clear')  # For macOS and Linux
    # os.system('cls')  # For Windows

# Bring Safari to focus
def focus_on_safari():
    script = '''
    tell application "Safari"
        activate
    end tell
    '''
    subprocess.run(["osascript", "-e", script])

# Scrape each house
def scrape_house(driver):
    wait = WebDriverWait(driver, 10)
    scraped_data = {}
    
    try:
        # Addresse, YearBuilt
        for css, key in [('.d-mega', 'Addresse'), ('.d-textSoft .formula', 'YearBuilt')]:
            elem = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, css))).text
            scraped_data[key] = ' '.join(elem.split('\n')).strip()  # Remove newlines
        print("Address good")
        
        # Containers 1
        container = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.col-sm-6.d-borderWidthLeft--1')))
        rows = container.find_elements(By.CSS_SELECTOR, '.row')
        for row in rows:
            scrape_row(row, scraped_data)
        print("container 1 good")
        
        # Container 2
        container2 = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.col-sm-6.d-bgcolor--systemLightest')))
        direct_children = container2.find_elements(By.XPATH, './div[contains(@class, "row")]')

        for i in range(len(direct_children)):
            # Re-fetch the container and its children to avoid stale element issues
            container2 = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.col-sm-6.d-bgcolor--systemLightest')))
            direct_children = container2.find_elements(By.XPATH, './div[contains(@class, "row")]')
    
            if i+1 in [5, 6, 7, 8, 9]:  # 1-based indexing for nth-child
                scrape_row(direct_children[i], scraped_data)
        print("container 2 good")
    
        # Container 3
        # Handle 2nd child specifically (container3)
        container3 = direct_children[1]
        rows_in_container3 = container3.find_elements(By.CSS_SELECTOR, '.row:not(.hidden-xs.hidden-sm)')

        # Scrape rows in container3 using a special scrape_row function
        for row in rows_in_container3:
            special_scrape_row(row, scraped_data) 
        print("container 3 good")
    
        # Special Case
        special_row = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.d-subtextSoft.d-fontSize--smallest')))
        special_text = special_row.text

        # Use string methods to find the number after "No Centris : "
        start_index = special_text.find("No Centris : ")
        if start_index != -1:
            start_index += len("No Centris : ")
            end_index = special_text.find("Date d'envoi : ")
            if end_index == -1:
                end_index = None  # Take until the end of the string if "Date d'envoi : " is not found
            no_centris_number = special_text[start_index:end_index].strip()
            scraped_data["No Centris"] = no_centris_number
        print("special case good")
        
    except Exception as e:
        print(f"An error occurred: {e}")
        driver.quit()  # Close the driver
        exit(1)  # Stop the program
    
    return scraped_data

def scrape_row(row, scraped_data):
    try:
        param_names = row.find_elements(By.CSS_SELECTOR, '.d-textStrong, .d-section')
        param_values = row.find_elements(By.CSS_SELECTOR, '.d-fontSize--smallest:not(.d-textStrong), .d-fontSize--smaller:not(.d-textStrong), .formula')
        
        for name, value in zip(param_names, param_values):
            clean_value = value.text.replace('\xa0', ' ').strip()
            scraped_data[name.text.replace('\n', ' ').strip()] = clean_value
            #print(name.text.replace('\n', ' ').strip(), clean_value)
            
    except Exception as e:
        print(f"An error occurred in scrape_row: {e}")
        raise  # Re-raise the caught exception

def special_scrape_row(row, scraped_data):
    try:
        param_names = row.find_elements(By.CSS_SELECTOR, '.d-textStrong, .d-section:not(.d-fontWeight--semibold)')
        param_values = row.find_elements(By.CSS_SELECTOR, '.d-fontSize--smallest:not(.d-textStrong), .d-fontSize--smaller, .formula')
        
        for name, value in zip(param_names, param_values):
            clean_value = value.text.replace('\xa0', ' ').strip()
            scraped_data[name.text.replace('\n', ' ').strip()] = clean_value
            
    except Exception as e:
        print(f"An error occurred in special_scrape_row: {e}")
        raise  # Re-raise the caught exception

# Find the last existing JSON file
last_file_index = -1
max_houses_per_file = 500

for i in range(len(sensitive_url)):
    try:
        with open(f"all_houses_{i+1}.json", 'r') as f:
            all_houses = json.load(f)
        last_file_index = i
    except FileNotFoundError:
        break

# Main loop starts from the last found file index
for i in range(last_file_index, len(sensitive_url)):
    if last_file_index != -1 and i == last_file_index:
        # If we found a last file, and we are on it, use its data
        with open(f"all_houses_{i+1}.json", 'r') as f:
            all_houses = json.load(f)
    else:
        # Otherwise, start fresh for this URL
        all_houses = []
    
    print(f"Starting with json file no.: {i + 1}")

    try:
        # Main
        driver = webdriver.Safari()
        driver.get(sensitive_url[i])
        focus_on_safari()  # Bring Safari to focus

        # Wait for the page to load
        wait = WebDriverWait(driver, 30)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, f"a[href*='Redisplay|20547,,0']")))

        # Click to get the first house
        clickable_element = driver.find_element(By.CSS_SELECTOR, f"a[href*='Redisplay|20547,,0']")
        
        #clickable_element.click()
        driver.execute_script("arguments[0].click();", clickable_element)

        # Wait for the house details to load
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.d-mega')))
    
        # Extract the total number of houses
        total_houses_element = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="_ctl0_m_lblPagingSummary"]/ul/b[2]')))
        total_houses = int(total_houses_element.text)
    
        # Skip to the house where you left off, if any
        if len(all_houses) > 0:
            for _ in range(len(all_houses)):
                next_button = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'a.glyphicon.glyphicon-chevron-right'))
                )
                next_button.click()
                time.sleep(2)

        # Loop through each house
        for j in range(len(all_houses), total_houses):
            print(f"Url no.: {i+1}")
            print(f"House no.{j} out of {total_houses}")
        
            try:
                scraped_data = scrape_house(driver)
                all_houses.append(scraped_data)

                # Dump the data to a JSON file
                with open(f"all_houses_{i+1}.json", 'w') as f:
                    json.dump(all_houses, f)

                # Clear terminal
                clear_output(wait=True) # For Notebook
                clear_terminal() # VSCode

                # Click the "Next" button to go to the next house
                if j < total_houses - 1:
                    next_button = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, 'a.glyphicon.glyphicon-chevron-right'))
                    )
                    next_button.click()
                    time.sleep(2)

            except Exception as e:
                print(f"An error occurred: {e}")
                driver.quit()
                exit(1)
            
    except Exception as e:
        print(f"An error occurred: {e}")
        driver.quit()
        exit(1)
        
    print("quitting driver")
    driver.quit()
    time.sleep(2)  
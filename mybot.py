
#import schedule
import os

import time
import requests  # We'll use this to make the AJAX call
import json
from selenium import webdriver
from selenium.webdriver.common.by import By

from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# Path to Edge WebDriver
#EDGE_DRIVER_PATH = r"C:\Users\20232036\OneDrive - TU Eindhoven\Desktop\webdriver\msedgedriver.exe"

PLAZA_URL = "https://plaza.newnewnew.space/en/availables-places/living-place#?gesorteerd-op=publicatiedatum-&locatie=Eindhoven-Nederland%2B-%2BNoord-Brabant"
# AJAX API Endpoint (Example, adjust with actual found in DevTools)
AJAX_URL = "https://mosaic-plaza-aanbodapi.zig365.nl/api/v1/actueel-aanbod?limit=60&locale=en_GB&page=0&sort=%2BreactionData.aangepasteTotaleHuurprijs"

# Login details
USERNAME = "Sani@tue"
PASSWORD = "Scorpion31$?"

# Refresh interval & timeout settings
CHECK_INTERVAL = 2
TIMEOUT = 60*60*1.5

def fetch_listings():
    """Fetches the latest listings using an AJAX request."""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json"
        }
        response = requests.get(AJAX_URL, headers=headers)
        if response.status_code == 200:
            return response.json()  # Convert response to JSON
        else:
            print(f"Failed to fetch listings, status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error fetching listings: {e}")
        return None
def load_reacted_listings():
    """Loads previously reacted listings from a file."""
    try:
        with open("reacted_listings.txt", "r") as file:
            return set(file.read().splitlines())
    except FileNotFoundError:
        return set()

def save_reacted_listing(url_key):
    """Saves a newly reacted listing to the file."""
    with open("reacted_listings.txt", "a") as file:
        file.write(url_key + "\n")


def run_bot():
    print("Running bot at:", time.strftime("%H:%M:%S"))

   # service = Service(EDGE_DRIVER_PATH)
    options = Options()
    options.binary_location = os.environ.get('CHROMIUM_BIN', '/usr/bin/chromium-browser')  # Default path for the runner
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    print("Launching Chrome WebDriver...", flush=True)
    driver = webdriver.Chrome(options=options)

    # options.add_argument("--headless")  # Headless mode (commented out so we can see it)
    # options.add_argument("--disable-gpu")  # Sometimes needed for stability (commented out)
    options.add_argument("--log-level=3")
    
    #driver = webdriver.Edge(service=service, options=options)
    driver.get(PLAZA_URL)

    # Allow cookies
    WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.ID, "CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll"))
    ).click()

    # Log in
    account_icon = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.XPATH, "//*[@id='main-navigation']/zds-navigation-body[5]/zds-navigation-link"))
    )
    account_icon.click()

    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "username"))).send_keys(USERNAME)
    
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "password"))).send_keys(PASSWORD)
    
    #driver.find_element(By.ID, "password").send_keys(PASSWORD)
    driver.find_element(By.XPATH, "//*[@id='account-frontend-login']/login/login-form/div[1]/form").submit()
    WebDriverWait(driver, 10).until(EC.url_changes(driver.current_url))

    driver.execute_script(f"window.open('{PLAZA_URL}', '_blank');")
    driver.switch_to.window(driver.window_handles[1])

    start_time = time.time()

    while True:
        if time.time() - start_time > TIMEOUT:
            print("Timeout reached. Stopping search.")
            break

        print("Checking listings using AJAX...")
        listings = driver.find_elements(By.XPATH, "//div[contains(@id, 'object-tile-')]/a")


        listings_data = fetch_listings()

##        if "data" in listings_data:
##            for listing in listings_data["data"]:
##                gemeente = listing.get("gemeenteGeoLocatieNaam", "")  # Avoid None errors
##                kan_reageren = listing.get("reactionData", {}).get("kanReageren", False)
##                title = listing.get("street", "Unknown Location")
##
##                print(f"DEBUG: Found listing - {title}, Gemeente: {gemeente}, kanReageren: {kan_reageren}")
##
##                gemeente = listing.get("gemeenteGeoLocatieNaam", "")
##                if isinstance(gemeente, str) and "eindhoven" in gemeente.lower() and kan_reageren:
##
##
##                #if "eindhoven" in gemeente.lower() and kan_reageren:
##                    print(f"✅ Valid listing found: {title} (Reacting...)")
##                else:
##                    print(f"❌ Skipping {title} - Conditions not met.")
##        else:
##            print("❌ No listings found in AJAX response!")
##        
##        if not listings_data:
##            print("Retrying in a few seconds...")
##            time.sleep(CHECK_INTERVAL)
##            continue

        

        # Check for "Lampendriessen" in the AJAX response
        for listing in listings_data.get("data"):  # Safely access the "data" key
            
            #gemeente = listing.get("gemeenteGeoLocatieNaam", "")  # Default to empty string if None
            street = listing.get("street", "")
            #kan_reageren = listing.get("reactionData", {}).get("kanReageren", False)
            
            title = listing.get("street", "Unknown Location")
            #print(f"DEBUG: Found listing - {title}, Gemeente: {gemeente}, kanReageren: {kan_reageren}")
            
            # Ensure gemeente is a string before calling .lower()
           
                
            if isinstance(street, str):
                street = street.lower()
            else:
                street = ""
                #print("street is empty for some reasons")
            
            #isinstance(street, str) and
                            
            # Check if Eindhoven is in the listing and if responding is allowed
            

            reacted_listings = load_reacted_listings()
            url_key = listing.get("urlKey", "")
            
            if  ("lampendriessen" in street.lower())  and (url_key not in reacted_listings):
                print(f"✅ Valid listing found: {title} (Reacting...)")
                #print(f"Found listing in de lampendriessen: {title}, navigating...")


                
                listing_url = "https://plaza.newnewnew.space/en/availables-places/living-place/details/" + listing.get("urlKey", "")
                
                driver.get(listing_url)

                save_reacted_listing(url_key)
                #print("navigated to listing link")
                try:
                    react_button = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, "//*[@id='object-details-reageren']/div/div[1]/div/form/input"))
                    )
                    react_button.click()
                    print("Successfully reacted!")
                    
                    
                except Exception as e:
                    print("Error clicking react button:", e)

                driver.quit()
                return  # Exit after successful reaction
            elif url_key in reacted_listings:
                print(f"Skipping {title} - Already reacted.")
            #elif not kan_reageren:
            #    print(f"Skipping {title} - Reactions not allowed.")

        #print("Lampendriessen not found. Waiting to check again...")
        time.sleep(CHECK_INTERVAL)

    driver.quit()

 #Schedule the bot to run at these times
##schedule.every().day.at("07:02").do(run_bot)    
##schedule.every().day.at("08:02").do(run_bot)
##schedule.every().day.at("09:02").do(run_bot)
##schedule.every().day.at("10:02").do(run_bot)
##schedule.every().day.at("11:02").do(run_bot)
##schedule.every().day.at("12:02").do(run_bot)
##schedule.every().day.at("13:02").do(run_bot)
##schedule.every().day.at("14:02").do(run_bot)
##schedule.every().day.at("15:02").do(run_bot)
##schedule.every().day.at("16:02").do(run_bot)
##schedule.every().day.at("17:02").do(run_bot)
##schedule.every().day.at("18:02").do(run_bot)

#print("Waiting for scheduled times...")
#while True:
#    schedule.run_pending()
#    time.sleep(30)

if __name__ == "__main__":
    run_bot()


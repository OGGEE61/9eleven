from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
import time

def scrape_listing(url, driver):
    driver.get(url)
    # Wait a bit for initial content load (use explicit waits in production)
    time.sleep(3)
    
    try:
        # Wait until the VIN container is present
        vin_container = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[@data-testid='advert-vin']"))
        )
        print("VIN container text before click:", vin_container.text)
        
        # Find the button inside the container
        vin_button = vin_container.find_element(By.XPATH, "./button")
        
        # Scroll the button into view
        driver.execute_script("arguments[0].scrollIntoView(true);", vin_button)
        
        # Option 1: Using JavaScript click
        driver.execute_script("arguments[0].click();", vin_button)
        
        # Option 2 (uncomment to try ActionChains instead):
        # actions = ActionChains(driver)
        # actions.move_to_element(vin_button).click().perform()
        
        # Wait until the VIN is revealed (i.e., container text changes)
        WebDriverWait(driver, 10).until(
            lambda d: "Wyświetl VIN" not in d.find_element(By.XPATH, "//div[@data-testid='advert-vin']").text
        )
        
        print("VIN container text after click:", vin_container.text)
    except Exception as e:
        print("Error during VIN button handling:", e)
    
    # Parse the updated page source with BeautifulSoup
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    
    # Extract offer title
    title_elem = soup.find('h1', class_='offer-title')
    title = title_elem.get_text(strip=True) if title_elem else None
    
    # Extract price details
    price_number = soup.find('h3', class_='offer-price__number')
    currency_elem = soup.find('p', class_='offer-price__currency')
    price = f"{price_number.get_text(strip=True)} {currency_elem.get_text(strip=True)}" if price_number and currency_elem else None
    
    # Extract mileage from an element containing "km"
    mileage_elem = soup.find('p', string=lambda text: text and "km" in text)
    mileage = mileage_elem.get_text(strip=True) if mileage_elem else None
    
    # Get the VIN text from the VIN container
    vin_container_bs = soup.find('div', {'data-testid': 'advert-vin'})
    vin = vin_container_bs.get_text(strip=True) if vin_container_bs else None
    
    return {
        "vin": vin,
        "title": title,
        "price": price,
        "mileage": mileage
    }
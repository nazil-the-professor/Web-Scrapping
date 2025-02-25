from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import random
from difflib import SequenceMatcher

# Configure Chrome options
chrome_options = Options()
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920x1080")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")

# Set up WebDriver
service = Service(ChromeDriverManager().install())  
driver = webdriver.Chrome(service=service, options=chrome_options)

query = input("Enter a product to search: ")

def get_amazon_prices(query):
    driver.get(f"https://www.amazon.in/s?k={query}")
    time.sleep(random.uniform(3, 7))
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 2);")
    time.sleep(random.uniform(2, 5))
    
    wait = WebDriverWait(driver, 15)
    prices = {}
    try:
        products = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "puisg-col-inner")))
        for product in products[:5]:  # Limit to first 5 results
            try:
                title = product.find_element(By.TAG_NAME, "h2").text
                price = product.find_element(By.CLASS_NAME, "a-price-whole").text
                prices[title] = int(price.replace(',', ''))
            except Exception:
                continue
    except Exception as e:
        print("Amazon Error:", e)
    return prices

def get_flipkart_prices(query):
    driver.get(f"https://www.flipkart.com/search?q={query}&otracker=search&otracker1=search&marketplace=FLIPKART&as-show=on&as=off")
    time.sleep(random.uniform(3, 7))
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 2);")
    time.sleep(random.uniform(2, 5))
    
    wait = WebDriverWait(driver, 15)
    prices = {}
    try:
        products = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "yKfJKb.row")))
        for product in products[:5]:  # Limit to first 5 results
            try:
                title = product.find_element(By.CLASS_NAME, "KzDlHZ").text
                price = product.find_element(By.CLASS_NAME, "Nx9bqj._4b5DiR").text
                prices[title] = int(price.replace('₹', '').replace(',', ''))
            except Exception:
                continue
    except Exception as e:
        print("Flipkart Error:", e)
    return prices

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

amazon_prices = get_amazon_prices(query)
flipkart_prices = get_flipkart_prices(query)

driver.quit()

# Comparing prices
print("\nPrice Comparison:")
for amazon_product in amazon_prices:
    amazon_price = amazon_prices[amazon_product]
    best_match = None
    highest_similarity = 0.0
    
    for flipkart_product in flipkart_prices:
        similarity = similar(amazon_product.lower(), flipkart_product.lower())
        if similarity > highest_similarity:
            highest_similarity = similarity
            best_match = flipkart_product
    
    if best_match and highest_similarity > 0.5:  # Threshold for similarity
        flipkart_price = flipkart_prices[best_match]
        cheaper = "Amazon" if amazon_price < flipkart_price else "Flipkart"
        print(f"{amazon_product} - Amazon: ₹{amazon_price}, Flipkart: ₹{flipkart_price} | Cheaper on: {cheaper}")
    else:
        print(f"{amazon_product} - Amazon: ₹{amazon_price}, Not found on Flipkart")

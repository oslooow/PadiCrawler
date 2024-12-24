from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

driver = None

def init_browser():
    """Initialize the Chrome driver"""
    global driver
    if driver is None:
        driver = webdriver.Chrome()

# Web scraping function
def fetch_products(search_term, nama_toko):

    global driver
    if driver is None:
        init_browser()

    driver.get(f"https://www.padiumkm.id/search?k={search_term}&tab=1")

    time.sleep(0.2)  # Adjust according to page load speed

    products = []
    product_elements = driver.find_elements(By.XPATH, "//*[contains(@class, 'cursor-pointer flex flex-col')]")

    for product in product_elements:
        try:
            name = product.find_element(By.CLASS_NAME, "font-normal").text
            vendor = product.find_element(By.XPATH, ".//span[contains(@class, 'font-medium') and contains(@class, 'font-ubuntu') and contains(@class, 'text-xs') and not(contains(@class, 'absolute'))]").text
            
            price_str = product.find_element(By.CLASS_NAME, "font-bold").text
            price_numeric = float(price_str.replace("Rp", "").replace(".", "").strip())  # Remove "Rp" and ".", then convert to float

            location = product.find_element(By.CLASS_NAME, "flex-1").text
            id_barang = search_term

            products.append({
                "name": name,
                "vendor": vendor,
                "price": price_numeric,
                "location": location,
                "id_barang": id_barang
            })
        except Exception as e:
            print(f"Error extracting product data: {e}")

    # Filter products by the search term
    filtered_products = [product for product in products if search_term in product["name"]]
    
    # Find the products from the specified 'nama_toko'
    toko_products = [product for product in filtered_products if product["vendor"] == nama_toko]
    
    print(toko_products)

    # Store results including 'nama_toko' products
    results = []

    if toko_products:
        # Compare 'nama_toko' products with other products that have the same or lower price
        for toko_product in toko_products:
            competitors = [product for product in filtered_products if product["vendor"] != nama_toko and product["price"] <= toko_product["price"]]

            if competitors:
                for competitor in competitors:
                    results.append({
                        "id_barang": toko_product["id_barang"],
                        "nama_barang": toko_product["name"],
                        "competitor_name": competitor["vendor"],
                        "competitor_price": competitor["price"],
                        "nama_toko_price": toko_product["price"]
                    })
    else:
        # If no toko_products found, return the cheapest product from filtered_products
        cheapest_product = min(filtered_products, key=lambda x: x["price"])
        print(cheapest_product)
        results.append({
            "id_barang": cheapest_product["id_barang"],
            "nama_barang": cheapest_product["name"],
            "competitor_name": "No competitor",
            "competitor_price": cheapest_product["price"],
            "nama_toko_price": cheapest_product["price"]
        })

    return results

def cleanup():
    """Clean up webdriver resources"""
    global driver
    if driver:
        try:
            driver.quit()
        except:
            pass
        finally:
            driver = None
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import re

driver = None

def init_browser():
    """Initialize the Chrome driver"""
    global driver
    if driver is None:
        driver = webdriver.Chrome()

def extract_kode_barang(nama_barang):
    """Extract Kode Barang from product name"""
    match = re.match(r'^(\d{12})', nama_barang)
    if match:
        return match.group(1)
    return "0"  # Return "0" if no valid kode barang found

def fetch_toko_products(store_code):
    """
    Fetch all products from a specific toko, including pagination
    Returns tuple of (store_name, products_list)
    """
    global driver
    if driver is None:
        init_browser()

    all_products = []
    store_name = "Unknown Store"
    page = 1
    products_found = True

    while products_found:
        # Construct URL with page number
        url = f"https://www.padiumkm.id/store/{store_code}?page={page}"
        print(f"Accessing page {page}: {url}")  # Debug print
        driver.get(url)
        
        # Wait for products to load
        time.sleep(0.5)  # Slightly increased wait time for reliability

        # Get store name if first page
        if page == 1:
            try:
                store_name_element = driver.find_element(By.XPATH, "//span[contains(@class, 'text-base') and contains(@class, 'font-semibold') and contains(@class, 'text-paletteText-primary')]")
                store_name = store_name_element.text
                print(f"Store name found: {store_name}")  # Debug print
            except Exception as e:
                print(f"Error getting store name: {e}")  # Debug print
                pass

        try:
            # Wait for product grid to load
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, "grid"))
            )

            # Find all product elements
            product_elements = driver.find_elements(By.XPATH, "//div[contains(@class, 'cursor-pointer flex flex-col')]")
            
            # If no products found, end pagination
            if not product_elements:
                print(f"No products found on page {page}, ending pagination")  # Debug print
                products_found = False
                break

            print(f"Found {len(product_elements)} products on page {page}")  # Debug print

            # Process products on current page
            for product in product_elements:
                try:
                    name = product.find_element(By.CLASS_NAME, "font-normal").text
                    
                    price_str = product.find_element(By.CLASS_NAME, "font-bold").text
                    price_numeric = float(price_str.replace("Rp", "").replace(".", "").strip())
                    
                    location = product.find_element(By.CLASS_NAME, "flex-1").text
                    
                    # Extract kode barang from the name
                    kode_barang = extract_kode_barang(name)

                    # Only append if we haven't seen this product before
                    if not any(p.get('kode_barang') == kode_barang for p in all_products):
                        all_products.append({
                            "name": name,
                            "price": price_numeric,
                            "location": location,
                            "kode_barang": kode_barang
                        })
                        print(f"Added product: {name} (Kode: {kode_barang})")  # Debug print
                except Exception as e:
                    print(f"Error extracting product data: {e}")

            # Increment page counter
            page += 1

        except TimeoutException:
            print(f"Timeout waiting for products on page {page}, ending pagination")  # Debug print
            products_found = False
        except Exception as e:
            print(f"Error processing page {page}: {e}")  # Debug print
            products_found = False

    print(f"Total products collected: {len(all_products)}")  # Debug print

    return store_name, all_products

def compare_multiple_products(toko1_products, toko2_list):
    """
    Compare products between the first store and multiple other stores primarily using Kode Barang
    Returns a list of products with their source store information
    
    Args:
        toko1_products: List of products from the first store
        toko2_list: List of tuples (store_name, products_list) for comparison stores
    
    Returns:
        List of unique products found in comparison stores but not in toko1,
        with added source_store information
    """
    # Create dictionaries for toko1 products
    toko1_kode_dict = {}  # For products with kode
    toko1_name_dict = {}  # For products without kode (kode="0")
    
    for product in toko1_products:
        kode = product.get('kode_barang', '0')
        if kode != "0":
            toko1_kode_dict[kode] = product
        else:
            toko1_name_dict[product['name'].lower()] = product
    
    # List to store all unique products with their source store
    all_unique_products = []
    
    # Compare with each toko2
    for toko2_name, toko2_products in toko2_list:
        for product in toko2_products:
            kode = product.get('kode_barang', '0')
            
            # Check if product should be added based on kode or name
            should_add = False
            
            if kode != "0":
                # If product has kode, check if it exists in toko1 kode dictionary
                if kode not in toko1_kode_dict:
                    should_add = True
            else:
                # If product has no kode, check by name
                if product['name'].lower() not in toko1_name_dict:
                    should_add = True
            
            if should_add:
                # Add store name to the product info
                product_with_store = product.copy()
                product_with_store['source_store'] = toko2_name
                all_unique_products.append(product_with_store)
    
    return all_unique_products

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
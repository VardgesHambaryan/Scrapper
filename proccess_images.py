import json
import os
from pathlib import Path
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
import coloredlogs
import time
from PIL import Image
from io import BytesIO
from datetime import datetime


from configurations.config import (
    BASE_IMAGE_URL, MAX_IMAGE_COUNT, DATA_DIR, POST_DATA_DIR, BASE_SIZE_URL,
    headers
)

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
coloredlogs.install(level='DEBUG', fmt='%(asctime)s - %(levelname)s - %(message)s')

def load_json(file_path):
    with open(file_path, 'r', encoding='UTF-8') as file:
        return json.load(file)

def save_json(file_path, data):
    with open(file_path, 'w', encoding='UTF-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

def create_directory(path):
    if not path.exists():
        path.mkdir(parents=True)

def download_image(image_url):
    try:
        response = requests.get(image_url)
        response.raise_for_status()
        
        image = Image.open(BytesIO(response.content))
        if image.size != (1024, 1024):
            return image_url
        else:
            logging.warning(f"Skipped image {image_url} due to size (1024, 1024)")
            return None
    except requests.HTTPError as http_err:
        logging.error(f"HTTP error occurred: {http_err}")
        return None
    except Exception as err:
        logging.error(f"An error occurred: {err}")
        return None

def download_images(product, color_code_to_color):
    tasks = []
    image_urls_by_color = {color.replace('/', '-'): [] for color in product['color_list']}
    
    with ThreadPoolExecutor(max_workers=50) as executor:  # Increased max workers for more concurrency
        for color_code in product['color_code_list']:
            for image_id in range(1, MAX_IMAGE_COUNT + 1):
                image_url = BASE_IMAGE_URL.format(product_id=product['id'], color_code=color_code, image_id=image_id)
                tasks.append(executor.submit(download_image, image_url))
        
        for task in as_completed(tasks):
            result = task.result()
            if result:
                color_code = result.split('_')[1]
                color = color_code_to_color.get(color_code, 'Unknown')
                if color != 'Unknown':
                    image_urls_by_color[color].append(result)
                else:
                    logging.warning(f"Unknown color code {color_code} for URL {result}")
    
    return image_urls_by_color


def get_sizes(product_id):
    url = BASE_SIZE_URL.format(product_id = product_id)

    data = requests.get(url=url, headers=headers).json()

    extracted_data = []

    # Navigate to the product information
    product_info = data.get("Response", {}).get("product", {})
    product_id = product_info.get("id")
    product_name = product_info.get("displayName")
    brand = product_info.get("dswBrand", {}).get("displayNameDefault")
    product_full_name = f"{brand} {product_name}"

    # Get the childSKUs list
    childSKUs = product_info.get("childSKUs", [])

    for sku in childSKUs:
        size_info = {
            "size": sku.get("size", {}).get("displayName"),
            "color": sku.get("color", {}).get("displayName"),
            "skuStockLevel": sku.get("skuStockLevel"),
            "dimension": sku.get("dimension", {}).get("displayName"),
            "upc": sku.get("upc", "")
        }
        extracted_data.append(size_info)

    return extracted_data



def process_products(products):
    products_list = []
    
    for product in products:
        color_code_to_color = {color_code: color.replace('/', '-') for color_code, color in zip(product['color_code_list'], product['color_list'])}
        image_urls_by_color = download_images(product, color_code_to_color)
        
        product_info = {
            "name": f"{product['brand'][0]} {product['name']}",
            "brand": product['brand'][0],
            "gender": product['gender'],
            "colors": {
                color: urls for color, urls in image_urls_by_color.items()
            },
            "price": product['clearance_price'],
            "price_min": product['clearance_price_min'],
            "price_max": product['clearance_price_max'],
            "discount_percentage": product['discount_percentage'],
            "stock_quantity": product['stock_quantity'],
            "product_id": product['id'],
            "sku": product['sku'],
            "sizes": get_sizes(product['id']),

            "CreateDate": datetime.now().strftime("%Y-%m/%d %H:%M:%S"),
            "PulledDate": datetime.now().strftime("%Y-%m/%d %H:%M:%S"),
            "ItemStateID":0,
            "NeedsMarketUpdate":0,
        }
        
        products_list.append(product_info)
        save_json(POST_DATA_DIR / 'filtered_products.json', products_list)  # Save after each product
    

def main():
    start_time = time.time()
    
    products = load_json(DATA_DIR / 'products1.json')
    process_products(products)
    
    end_time = time.time()
    logging.info(f"Execution time: {end_time - start_time:.2f} seconds")

if __name__ == "__main__":
    main()

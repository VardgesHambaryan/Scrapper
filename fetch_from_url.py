import asyncio
import aiohttp
import json
from urllib.parse import urlparse, parse_qs
import logging
from configurations.config import headers, POST_DATA_DIR

# Set up logging
logger = logging.getLogger('product_fetcher')
logger.setLevel(logging.INFO)

# File handler for writing logs to a file
file_handler = logging.FileHandler('logs/fetch_from_url.log')
file_handler.setLevel(logging.INFO)

# Stream handler for printing logs to the terminal
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)

# Formatter for the log messages
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
stream_handler.setFormatter(formatter)

# Adding handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(stream_handler)

def find_all_keys_with_paths(data, target_key):
    matches = []

    def recursive_search(data, target_key, current_path):
        if isinstance(data, dict):
            for key, value in data.items():
                new_path = current_path + [key]
                if key == target_key:
                    matches.append((new_path, value))
                recursive_search(value, target_key, new_path)
        elif isinstance(data, list):
            for index, item in enumerate(data):
                new_path = current_path + [index]
                recursive_search(item, target_key, new_path)

    recursive_search(data, target_key, [])
    return matches

def read_json_file(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def write_json_file(data, file_path):
    with open(file_path, 'w') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

def parse_url(url):
    parsed_url = urlparse(url)
    query = parsed_url.query
    params = parse_qs(query)

    if params:
        params = {key: [{"text": val} for val in value[0].split(',')] for key, value in params.items()}

    path_parts = parsed_url.path.strip('/').split('/')
    try:
        category_index = path_parts.index('category') + 1
        category = '/'.join(path_parts[category_index:])
    except ValueError:
        category = None

    return params, category

def update_response_with_params(response, params):
    if params:
        response['filter']["keys"]["brand"]["values"] = params.get('brand', [])
        response['filter']["keys"]["price_label"]["values"] = params.get('price', [])
    else:
        del response['filter']

    return response

async def fetch_page(session, api_url, response, page_number):
    path, _ = find_all_keys_with_paths(response, 'page_number')[0]
    response[path[0]][path[1]][path[2]] = page_number
    async with session.post(api_url, headers=headers, json=response) as resp:
        data = await resp.json()
        path, products = find_all_keys_with_paths(data, 'products')[0]
        logger.info(f"Fetching page: {page_number}")
        return data[path[0]][path[1]][path[2]]['value']

async def fetch_all_products(url, api_url_template):
    response = read_json_file('configurations/widgets.json')
    params, category = parse_url(url)
    response = update_response_with_params(response, params)
    api_url = api_url_template.format(category_name=category)
    
    async with aiohttp.ClientSession() as session:
        async with session.post(api_url, headers=headers, json=response) as resp:
            data = await resp.json()
            path, products = find_all_keys_with_paths(data, 'products')[0]
            pages = data[path[0]][path[1]][path[2]]['page_count']
        
        tasks = [fetch_page(session, api_url, response, i) for i in range(1, pages + 1)]
        all_products = await asyncio.gather(*tasks)
    
    return [product for sublist in all_products for product in sublist]

if __name__ == "__main__":
    url = "https://www.dsw.com/category/womens/shoes/casual/sandals"
    api_url_template = "https://api.dsw.com/content/api/v3/page?rfk_account=dswus_prod&banner=dswus&uri=/category/{category_name}"
    
    all_products = asyncio.run(fetch_all_products(url, api_url_template))
    log_message = f"Fetched {len(all_products)} products from {url} url."
    
    # Log to file and console
    logger.info(log_message)
    
    # Print only the last log message to the console
    # print(log_message)
    
    write_json_file(all_products, POST_DATA_DIR / "products.json")

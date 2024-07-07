import pyodbc
#----------------------------------------------------Connection---------------------------------------------------------
conn_str = (
    "Driver={ODBC Driver 18 for SQL Server};"
    "Server=WIN-OL3ORUKVEQC;"
    "Database=ScrapperDBDSW;"
    "Trusted_Connection=yes;"
    "TrustServerCertificate=yes;"  
)

try:
    cnxn = pyodbc.connect(conn_str)
    cursor = cnxn.cursor()

except pyodbc.Error as e:
    print(f"Error connecting to SQL Server: {e}")
#----------------------------------------------------Connection---------------------------------------------------------


def insert_product_data(cursor, product):

    model_data = {
        'url': product['url'],
        'Type': 'Type',  
        'Category': 'Category',  
        'SubCategory': 'SubCategory',  
        'Brand': product['brand'],
        'Product': product['name'],
        'PulledDate': datetime.now(),
        'CreateDate': datetime.now(),
        'PulledFrom': 'source',  
        'ItemStateID': 1,   
        'NeedsMarketUpdate': 0  
    }
    model_id = insert_model(cursor, model_data)

    for color, images in product['colors'].items():
        style_data = {
            'ColorSKU': 'SKU',  
            'ColorName': color,
            'DiscountPrice': product['price_min'],
            'OriginalPrice': product['price_max'],
        }
        style_id = insert_style(cursor, style_data, model_id)

        for image_url in images:
            insert_image(cursor, image_url, style_id)

        for size_info in product['sizes']:
            if size_info['color'] == color:
                stock_data = {
                    'StockSKU': size_info['skuStockLevel'],
                    'OnHand': size_info['skuStockLevel'],
                    'Size': size_info['size'],
                    'Width': size_info['dimension'],
                    'UPC': size_info['upc']
                }
                insert_stock(cursor, stock_data, style_id)

    insert_description(cursor, model_id, product['description'])

    for gender in product['gender']:
        insert_gender(cursor, model_id, gender)

products = [
    {
        "name": "Birkenstock Arizona Slide Sandal - Women's",
        "brand": "Birkenstock",
        "gender": ["Women"],
        "colors": {
            "Black": ["https://images.dsw.com/is/image/DSWShoes/171995_001_ss_02", "https://images.dsw.com/is/image/DSWShoes/171995_001_ss_01"],
            "Gold Metallic": ["https://images.dsw.com/is/image/DSWShoes/171995_750_ss_04", "https://images.dsw.com/is/image/DSWShoes/171995_750_ss_02"]
        },
        "price": 109.96,
        "price_min": 109.96,
        "price_max": 109.96,
        "discount_percentage": 0,
        "stock_quantity": 22515,
        "product_id": "171995",
        "sku": "58000000004744211000000N008.0",
        "sizes": [
            {"size": "EU 42 / US Womens 11-11.5 / Mens 9-9.5", "color": "Black", "skuStockLevel": 902, "dimension": "Medium", "upc": "886454234761"}
        ],
        "url": "https://example.com/product/171995",
        "description": "A comfortable sandal for women."
    }
]

try:
    for product in products:
        insert_product_data(cursor, product)

    cnxn.commit()
    cursor.close()
    cnxn.close()

except pyodbc.Error as e:
    print(f"Error inserting data into SQL Server: {e}")

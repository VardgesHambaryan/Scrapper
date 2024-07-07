from pathlib import Path

BASE_SIZE_URL = "https://www.dsw.com/api/v1/products/{product_id}?locale=en_US&pushSite=DSW"
BASE_IMAGE_URL = "https://images.dsw.com/is/image/DSWShoes/{product_id}_{color_code}_ss_{image_id:02d}"
MAX_IMAGE_COUNT = 10
DATA_DIR = Path('Data')
POST_DATA_DIR = DATA_DIR

headers = {
    "User-Agent": "*/*",
    "Accept-Encoding" : "gzip, deflate, br",
}

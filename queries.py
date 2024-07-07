def insert_model(cursor, model):
    cursor.execute("""
        INSERT INTO dbo.Models (url, Type, Category, SubCategory, Brand, Product, PulledDate, CreateDate, PulledFrom, ItemStateID, NeedsMarketUpdate) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, 
        model['url'], model['Type'], model['Category'], model['SubCategory'], model['Brand'], model['Product'], model['PulledDate'], 
        model['CreateDate'], model['PulledFrom'], model['ItemStateID'], model['NeedsMarketUpdate'])
    cursor.execute("SELECT @@IDENTITY AS id")
    model_id = cursor.fetchone()[0]
    return model_id

def insert_style(cursor, style, model_id):
    cursor.execute("""
        INSERT INTO dbo.Styles (ColorSKU, ColorName, DiscountPrice, OriginalPrice, ModelID)
        VALUES (?, ?, ?, ?, ?)
        """,
        style['ColorSKU'], style['ColorName'], style['DiscountPrice'], style['OriginalPrice'], model_id)
    cursor.execute("SELECT @@IDENTITY AS id")
    style_id = cursor.fetchone()[0]
    return style_id

def insert_stock(cursor, stock, style_id):
    cursor.execute("""
        INSERT INTO dbo.Stocks (StockSKU, OnHand, Size, Width, StyleID, UPC)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        stock['StockSKU'], stock['OnHand'], stock['Size'], stock['Width'], style_id, stock['UPC'])
    cursor.execute("SELECT @@IDENTITY AS id")
    stock_id = cursor.fetchone()[0]
    return stock_id

def insert_image(cursor, image_url, style_id):
    cursor.execute("""
        INSERT INTO dbo.Images (Image_url, StyleID)
        VALUES (?, ?)
        """,
        image_url, style_id)
    cursor.execute("SELECT @@IDENTITY AS id")
    image_id = cursor.fetchone()[0]
    return image_id

def insert_description(cursor, model_id, description):
    cursor.execute("""
        INSERT INTO dbo.Description (ModelID, Description)
        VALUES (?, ?)
        """,
        model_id, description)
    cursor.execute("SELECT @@IDENTITY AS id")
    description_id = cursor.fetchone()[0]
    return description_id

def insert_gender(cursor, model_id, gender):
    cursor.execute("""
        INSERT INTO dbo.Genders (Gender, ModelID)
        VALUES (?, ?)
        """,
        gender, model_id)
    cursor.execute("SELECT @@IDENTITY AS id")
    gender_id = cursor.fetchone()[0]
    return gender_id

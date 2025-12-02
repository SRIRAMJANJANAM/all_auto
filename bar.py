import os
import csv
from barcode import Code128
from barcode.writer import ImageWriter
from PIL import Image, ImageDraw, ImageFont
import qrcode

# Constants for shop info and greetings
SHOP_NAME = "My Awesome Shop"
SHOP_ADDRESS = "123 Market Street, Cityville"
OWNER_NAME = "John Doe"
GREETING = "Thank you for shopping with us!"

input_csv = "products.csv"
output_csv = "productnumb.csv"
output_folder = "productqr"

# Create output folder if it doesn't exist
os.makedirs(output_folder, exist_ok=True)

def generate_barcode_code(index):
    base = 100000000000  # 12-digit starting number
    return str(base + index)

# Load default font; replace with a TTF font file path if you want nicer fonts
font = ImageFont.load_default()

# Read products from CSV
products = []
with open(input_csv, newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        products.append(row)

with open(output_csv, 'w', newline='', encoding='utf-8') as outcsv:
    fieldnames = ['name', 'price', 'barcode_code']
    writer = csv.DictWriter(outcsv, fieldnames=fieldnames)
    writer.writeheader()

    for idx, product in enumerate(products):
        barcode_code = generate_barcode_code(idx)

        # 1. Generate barcode and save temporarily
        barcode = Code128(barcode_code, writer=ImageWriter())
        barcode_filepath = barcode.save(os.path.join(output_folder, barcode_code))
        barcode_img = Image.open(barcode_filepath)

        # 2. Generate QR code for the product info (can customize data inside QR)
        qr_data = f"Product Code: {barcode_code}\nName: {product['name']}\nPrice: {product['price']}"
        qr = qrcode.QRCode(
            version=2,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=8,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white").convert("RGB")

        # 3. Create new combined image: put barcode on top, QR code + text below
        barcode_width, barcode_height = barcode_img.size
        qr_width, qr_height = qr_img.size

        # Calculate combined image size
        padding = 20
        text_block_width = 400
        combined_width = max(barcode_width, qr_width + text_block_width + padding)
        combined_height = barcode_height + max(qr_height, 150) + padding * 2

        combined_img = Image.new("RGB", (combined_width, combined_height), "white")
        draw = ImageDraw.Draw(combined_img)

        # Paste barcode at top center
        barcode_x = (combined_width - barcode_width) // 2
        combined_img.paste(barcode_img, (barcode_x, padding))

        # Paste QR code below barcode on left side
        qr_x = padding
        qr_y = barcode_height + padding * 2
        combined_img.paste(qr_img, (qr_x, qr_y))

        # Write text details on right side of QR code
        text_x = qr_x + qr_width + padding
        text_y = qr_y
        line_height = 22

        draw.text((text_x, text_y), SHOP_NAME, font=font, fill="black")
        text_y += line_height
        draw.text((text_x, text_y), SHOP_ADDRESS, font=font, fill="black")
        text_y += line_height * 2

        draw.text((text_x, text_y), f"Product: {product['name']}", font=font, fill="black")
        text_y += line_height
        draw.text((text_x, text_y), f"Price: {product['price']}", font=font, fill="black")
        text_y += line_height
        draw.text((text_x, text_y), f"Code: {barcode_code}", font=font, fill="black")
        text_y += line_height * 2

        draw.text((text_x, text_y), f"Owner: {OWNER_NAME}", font=font, fill="black")
        text_y += line_height * 2

        draw.text((text_x, text_y), GREETING, font=font, fill="black")

        # Save combined image with barcode_code name + '_final.png'
        final_filename = os.path.join(output_folder, f"{barcode_code}_final.png")
        combined_img.save(final_filename)

        # Optional: remove the original barcode image file if you want
        os.remove(barcode_filepath)

        # Write product info + barcode code to CSV
        writer.writerow({
            'name': product['name'],
            'price': product['price'],
            'barcode_code': barcode_code
        })

print(f"Generated QR barcode images for {len(products)} products.")
print(f"Images saved in folder '{output_folder}'.")
print(f"Product info with barcode codes saved in '{output_csv}'.")

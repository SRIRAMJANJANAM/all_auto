import qrcode
from urllib.parse import urlparse


link = "https://www.orai-robotics.com/"


parsed_url = urlparse(link)
netloc = parsed_url.netloc

if netloc.startswith("www."):
    netloc = netloc[4:]

domain_name = netloc.replace('.', '_') 

filename = f"{domain_name}.png"


qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=6,
    border=6,
)
qr.add_data(link)
qr.make(fit=True)

img = qr.make_image(fill_color="black", back_color="white")
img.save(filename)
qr.print_ascii(invert=True)

print(f"\n✅ QR Code saved as '{filename}' for the link: {link}")

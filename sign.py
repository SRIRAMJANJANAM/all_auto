import cv2
import numpy as np

def extract_signature(input_path, output_path):
    # Load image
    img = cv2.imread(input_path, cv2.IMREAD_UNCHANGED)
    
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Thresholding to binary image
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # Find contours to isolate signature
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Create mask for signature
    mask = np.zeros_like(gray)

    # Draw contours (signature) on mask
    cv2.drawContours(mask, contours, -1, 255, thickness=cv2.FILLED)

    # Create transparent background
    b, g, r = cv2.split(img)
    alpha = mask

    # Merge with alpha channel
    rgba = cv2.merge([b, g, r, alpha])

    # Save result
    cv2.imwrite(output_path, rgba)
    print(f"Signature saved as: {output_path}")

# Example usage
extract_signature("signature.jpg", "digital_signature.png")

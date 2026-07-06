import cv2
import numpy as np

def extract_signature(input_path, output_path):
    # Load image (keep original channels)
    img = cv2.imread(input_path, cv2.IMREAD_UNCHANGED)

    if img is None:
        print("Error: Image not found.")
        return

    # If grayscale image, convert to BGR
    if len(img.shape) == 2:
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

    # If image has 4 channels (BGRA), convert to BGR
    if len(img.shape) == 3 and img.shape[2] == 4:
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Apply OTSU thresholding
    _, thresh = cv2.threshold(
        gray, 0, 255,
        cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
    )

    # Remove small noise using morphology
    kernel = np.ones((3, 3), np.uint8)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

    # Find contours (signature parts)
    contours, _ = cv2.findContours(
        thresh,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    # Create mask
    mask = np.zeros_like(gray)

    # Draw signature contours
    cv2.drawContours(mask, contours, -1, 255, thickness=cv2.FILLED)

    # Split BGR channels
    b, g, r = cv2.split(img)

    # Use mask as alpha channel
    alpha = mask

    # Merge into RGBA (transparent background)
    rgba = cv2.merge([b, g, r, alpha])

    # Save output PNG (must be PNG for transparency)
    cv2.imwrite(output_path, rgba)

    print(f"✅ Signature saved successfully as: {output_path}")


# Example usage
extract_signature("sign.png", "digital_signature.png")
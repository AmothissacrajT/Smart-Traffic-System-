from PIL import Image
import pytesseract

# If you're on Windows, you may need to specify the path to the tesseract executable
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Load the image
image = Image.open(r"C:\Users\Amoth issac raj\OneDrive\Desktop\Blaze trial 1.0\Images\Tamil_Nadu_Fancy_Number_Plate_75b7793a84.png")

# Use pytesseract to extract text
extracted_text = pytesseract.image_to_string(image)

print("Extracted Text:\n", extracted_text)
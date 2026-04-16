import pypdf
import os

pdf_path = r"e:\Software\multimodal-upi-fraud-detection\final draft.pdf"
output_path = r"e:\Software\multimodal-upi-fraud-detection\paper_text.txt"

def extract_text():
    if not os.path.exists(pdf_path):
        print(f"Error: {pdf_path} not found.")
        return

    try:
        reader = pypdf.PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"Successfully extracted text to {output_path}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    extract_text()

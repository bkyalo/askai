# test_pdf.py
import PyPDF2
import os

def test_pdf_reading(pdf_path):
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            print(f"\n=== Testing: {os.path.basename(pdf_path)} ===")
            print(f"Number of pages: {len(reader.pages)}")
            
            # Print first 500 chars from first page
            first_page = reader.pages[0].extract_text()
            print("\nFirst page content (first 500 chars):")
            print(first_page[:500])
            
    except Exception as e:
        print(f"Error reading {pdf_path}: {str(e)}")

# Test both PDFs
test_pdf_reading("documents/Covid-19_Knowledge.pdf")
test_pdf_reading("documents/health_guidelines.pdf")
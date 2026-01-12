try:
    from fpdf import FPDF
    print("FPDF import success")
except ImportError as e:
    print(f"FPDF import failed: {e}")

try:
    from docx import Document
    print("python-docx import success")
except ImportError as e:
    print(f"python-docx import failed: {e}")

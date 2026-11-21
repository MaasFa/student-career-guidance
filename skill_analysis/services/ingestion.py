import os
import re
import pdfplumber
import docx


def clean_text(text: str) -> str:
    """
    Cleans extracted text by standardizing bullets, removing excessive whitespace,
    and normalizing line breaks.
    """
    if not text:
        return ""
    
    # Replace common bullet characters with clean dash
    bullet_pattern = r'[\u2022\u2023\u25E6\u2043\u2219\u25AA\u25AB\u25CF\u25CB\u25A0\u25A1\u2713\u2714\u27A4\u25B6\u25BA*]'
    text = re.sub(bullet_pattern, '- ', text)
    
    # Standardize tab to spaces
    text = text.replace('\t', ' ')
    
    # Normalize multiple horizontal spaces
    text = re.sub(r'[^\S\r\n]+', ' ', text)
    
    # Remove leading/trailing space per line
    lines = [line.strip() for line in text.splitlines()]
    
    # Remove excessive blank lines (more than 2 consecutive newlines)
    cleaned_lines = []
    blank_count = 0
    for line in lines:
        if not line:
            blank_count += 1
            if blank_count <= 1:
                cleaned_lines.append("")
        else:
            blank_count = 0
            cleaned_lines.append(line)
            
    return "\n".join(cleaned_lines).strip()


def extract_text_from_pdf(file_path_or_buffer) -> str:
    """
    Extracts text from a PDF using pdfplumber.
    Raises ValueError if the PDF is scanned, empty, or has no extractable text.
    """
    full_text = []
    try:
        with pdfplumber.open(file_path_or_buffer) as pdf:
            if not pdf.pages:
                raise ValueError("The uploaded PDF has no pages.")
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    full_text.append(page_text)
    except Exception as e:
        if isinstance(e, ValueError):
            raise
        raise ValueError(f"Failed to read PDF file: {str(e)}")

    extracted = clean_text("\n\n".join(full_text))
    # Check if empty or likely scanned image
    alphanumeric_chars = len(re.findall(r'[a-zA-Z0-9]', extracted))
    if alphanumeric_chars < 50:
        raise ValueError(
            "Unable to extract readable text from the uploaded PDF. "
            "It appears to be scanned, image-only, or empty. "
            "Please upload a text-selectable PDF or DOCX file."
        )
    return extracted


def extract_text_from_docx(file_path_or_buffer) -> str:
    """
    Extracts text from a DOCX file using python-docx.
    """
    try:
        doc = docx.Document(file_path_or_buffer)
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        # Also extract table text if present
        table_text = []
        for table in doc.tables:
            for row in table.rows:
                row_cells = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                if row_cells:
                    table_text.append(" | ".join(row_cells))
        
        combined = "\n\n".join(paragraphs + table_text)
    except Exception as e:
        raise ValueError(f"Failed to read DOCX file: {str(e)}")

    extracted = clean_text(combined)
    alphanumeric_chars = len(re.findall(r'[a-zA-Z0-9]', extracted))
    if alphanumeric_chars < 30:
        raise ValueError("The DOCX document is empty or does not contain readable text.")
    return extracted


def extract_resume_text(uploaded_file) -> tuple[str, str]:
    """
    Detects file extension and extracts text.
    Returns (cleaned_text, file_type).
    """
    filename = uploaded_file.name.lower()
    if filename.endswith(".pdf"):
        return extract_text_from_pdf(uploaded_file), "pdf"
    elif filename.endswith(".docx") or filename.endswith(".doc"):
        return extract_text_from_docx(uploaded_file), "docx"
    else:
        raise ValueError("Unsupported file format. Please upload a .pdf or .docx file.")


def clean_job_description(jd_text: str) -> str:
    """
    Cleans and validates pasted Job Description text.
    """
    cleaned = clean_text(jd_text)
    if len(re.findall(r'[a-zA-Z0-9]', cleaned)) < 20:
        raise ValueError("Job description is too short. Please paste a complete job description.")
    return cleaned

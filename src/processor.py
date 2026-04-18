import PyPDF2
import io

def extract_text_from_pdf(uploaded_file) -> str:
    pdf_bytes = uploaded_file.read()
    pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
    text = ""
    for page in pdf_reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted + "\n"
    return text.strip()

def extract_text_from_txt(uploaded_file) -> str:
    return uploaded_file.read().decode("utf-8")

def extract_text_from_docx(uploaded_file) -> str:
    try:
        import docx
        doc = docx.Document(io.BytesIO(uploaded_file.read()))
        text = ""
        for para in doc.paragraphs:
            if para.text.strip():
                text += para.text + "\n"
        return text.strip()
    except Exception as e:
        return f"Error reading DOCX: {e}"

def process_file(uploaded_file) -> str:
    file_type = uploaded_file.type
    name = uploaded_file.name.lower()

    if file_type == "application/pdf" or name.endswith(".pdf"):
        return extract_text_from_pdf(uploaded_file)
    elif file_type == "text/plain" or name.endswith(".txt"):
        return extract_text_from_txt(uploaded_file)
    elif name.endswith(".docx") or "word" in file_type:
        return extract_text_from_docx(uploaded_file)
    else:
        raise ValueError(f"Unsupported file type: {file_type}")

def chunk_text(text: str, chunk_size: int = 2000) -> list:
    words = text.split()
    chunks = []
    current = []
    count = 0
    for word in words:
        current.append(word)
        count += len(word) + 1
        if count >= chunk_size:
            chunks.append(" ".join(current))
            current = []
            count = 0
    if current:
        chunks.append(" ".join(current))
    return chunks
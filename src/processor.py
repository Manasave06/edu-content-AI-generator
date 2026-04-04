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

def process_file(uploaded_file) -> str:
    if uploaded_file.type == "application/pdf":
        return extract_text_from_pdf(uploaded_file)
    elif uploaded_file.type == "text/plain":
        return extract_text_from_txt(uploaded_file)
    else:
        raise ValueError(f"Unsupported file type: {uploaded_file.type}")

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
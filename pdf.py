import os
from PyPDF2 import PdfReader
from docx import Document
from sentence_transformers import SentenceTransformer
import faiss
from transformers import pipeline


def extract_text(file_path):
    text = ""
    if file_path.lower().endswith(".pdf"):
        reader = PdfReader(file_path)
        for page in reader.pages:
            text += page.extract_text() or ""
    elif file_path.lower().endswith(".docx"):
        doc = Document(file_path)
        for para in doc.paragraphs:
            text += para.text + "\n"
    else:
        raise ValueError("Unsupported file type. Use PDF or DOCX.")
    return text.strip()


def chunk_text(text, chunk_size=500):
    words = text.split()
    return [" ".join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]


def build_index(chunks):
    model = SentenceTransformer("all-MiniLM-L6-v2")
    embeddings = model.encode(chunks)
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)
    return index, model


def answer_question(question, chunks, index, model, qa_pipeline, top_k=3):
    q_emb = model.encode([question])
    D, I = index.search(q_emb, top_k)
    context = "\n".join([chunks[i] for i in I[0]])

    # ✅ Correct way to call QA pipeline
    result = qa_pipeline(question=question, context=context)
    return result["answer"]


if __name__ == "__main__":
    file_path = input("Enter path to PDF or DOCX file: ").strip()
    print("Reading document...")
    text = extract_text(file_path)
    chunks = chunk_text(text)

    print("Building embeddings index (first time only)...")
    index, model = build_index(chunks)

    print("Loading local language model...")
    qa_pipeline = pipeline("question-answering", model="deepset/roberta-base-squad2")

    while True:
        q = input("\nAsk a question (or 'quit'): ")
        if q.lower() == "quit":
            break
        ans = answer_question(q, chunks, index, model, qa_pipeline)
        print("\nAnswer:", ans)

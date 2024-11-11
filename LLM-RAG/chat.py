from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from langchain_utls import response_to_query, load_document_and_split_text
import os
import tempfile

app = FastAPI()

# Temporary storage for document split text
doc_split = None


# Endpoint for uploading the document.
@app.post("/uploadfile")
async def upload_file(file: UploadFile = File(...)):
    global doc_split
    allowed_extensions = [".pdf", ".docx", ".html"]
    file_extension = os.path.splitext(file.filename)[1].lower()

    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed types are: {', '.join(allowed_extensions)}",
        )

    # Save the file temporarily and process it
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as tmp_file:
        tmp_file.write(await file.read())
        tmp_path = tmp_file.name
        print(tmp_path)

    # Load and split document text
    doc_split = load_document_and_split_text(tmp_path)
    os.remove(tmp_path)  # Clean up the temporary file

    return {"message": "File uploaded and processed successfully"}


# Main endpoint for the chatbot.
@app.get("/chat")
async def chat_llm(query: str):
    if doc_split is None:
        raise HTTPException(
            status_code=400,
            detail="No document uploaded. Please upload a document first.",
        )

    response = response_to_query(query, doc_split)
    return JSONResponse({"Response": response})

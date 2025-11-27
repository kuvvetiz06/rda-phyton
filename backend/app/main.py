from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.concurrency import run_in_threadpool

from app.models.schemas import ProcessResponse
from app.services import llm, ocr

app = FastAPI(title="OCR + LLM API", version="1.0.0")


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/process", response_model=ProcessResponse)
async def process_file(file: UploadFile = File(...)):
    if not file:
        raise HTTPException(status_code=400, detail="File upload is required")

    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    try:
        text = await run_in_threadpool(ocr.extract_text, file_bytes, file.filename, file.content_type)
    except Exception as exc:  # pragma: no cover - defensive catch for OCR errors
        raise HTTPException(status_code=500, detail=f"OCR processing failed: {exc}") from exc

    if not text:
        raise HTTPException(status_code=422, detail="No text extracted from the file")

    try:
        llm_result = await run_in_threadpool(llm.analyze_text, text)
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=f"LLM processing failed: {exc}") from exc

    return ProcessResponse(text=text, summary=llm_result.summary, key_points=llm_result.key_points)

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from uuid import uuid4
import os, shutil, threading, time
from PyPDF2 import PdfReader

app = FastAPI()

# Allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Session storage
sessions = {}
SESSION_EXPIRY = 3600  # 1 hour

# Folder to store user session files
BASE_DIR = "sessions"
os.makedirs(BASE_DIR, exist_ok=True)

# Delete session after expiry
def delete_session(session_id):
    time.sleep(SESSION_EXPIRY)
    if session_id in sessions:
        folder = sessions[session_id]['folder']
        shutil.rmtree(folder, ignore_errors=True)
        del sessions[session_id]
        print(f"[INFO] Session {session_id} expired and deleted.")

# Create new session
@app.get("/create-session")
def create_session():
    session_id = str(uuid4())
    folder = os.path.join(BASE_DIR, session_id)
    os.makedirs(folder, exist_ok=True)
    sessions[session_id] = {'folder': folder, 'questions': []}
    threading.Thread(target=delete_session, args=(session_id,), daemon=True).start()
    return {"session_id": session_id}

# Upload notes
@app.post("/upload/{session_id}")
async def upload_file(session_id: str, file: UploadFile = File(...)):
    if session_id not in sessions:
        return {"error": "Session expired"}
    file_location = os.path.join(sessions[session_id]['folder'], file.filename)
    with open(file_location, "wb") as f:
        shutil.copyfileobj(file.file, f)
    # Extract text if PDF
    if file.filename.lower().endswith(".pdf"):
        try:
            reader = PdfReader(file_location)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            sessions[session_id]['questions'].append(text)
        except:
            return {"status": "uploaded, but failed to parse PDF"}
    return {"status": "file uploaded", "filename": file.filename}

# Get question
@app.get("/question/{session_id}")
def get_question(session_id: str):
    if session_id not in sessions:
        return {"error": "Session expired"}
    # For prototype: pick first line from first uploaded note
    if not sessions[session_id]['questions']:
        return {"error": "No notes uploaded"}
    lines = sessions[session_id]['questions'][0].splitlines()
    lines = [line for line in lines if line.strip()]
    if not lines:
        return {"error": "No content in notes"}
    question = lines[0]
    # Prototype: random options (first line correct, next 2 dummy)
    return {
        "question": question,
        "options": [question, "Option 2", "Option 3"]
    }

# Run with: uvicorn main:app --reload

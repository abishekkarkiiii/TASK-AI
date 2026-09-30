from fastapi import FastAPI
from App.API.docs import router as rt
from App.API.Search import router as srt
from App.API.chat import router as crt

app = FastAPI(tags=["MAIN"])

app.include_router(rt)
app.include_router(srt)
app.include_router(crt)
@app.get("/")
def root():
    return {
        "message": "Palm Mind AI RAG API is running"
    }

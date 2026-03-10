from fastapi import FastAPI

app = FastAPI(title="Auto Trading API")

@app.get("/")
def root():
    return {"status": "running"}
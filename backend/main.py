from fastapi import FastAPI
import uvicorn
from routes import router

app = FastAPI()

# Include scraping routes
app.include_router(router)

@app.get("/")
def home():
    return {"message": "AutoSocial API is running!"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)

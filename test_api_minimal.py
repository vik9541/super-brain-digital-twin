"""
Минимальный тест Victor Bot API
"""

import uvicorn
from fastapi import FastAPI

app = FastAPI(title="Victor Bot Test")


@app.get("/")
def read_root():
    return {
        "service": "Victor Bot v2.0 API",
        "status": "running",
        "version": "2.0.0",
        "features": {
            "text_collection": True,
            "file_upload": True,
            "telegram_webhook": True,
            "background_processing": False,  # Disabled due to pooler
        },
    }


@app.get("/health")
def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    print("🚀 Starting Victor Bot v2.0 API (minimal)")
    uvicorn.run(app, host="0.0.0.0", port=8000)

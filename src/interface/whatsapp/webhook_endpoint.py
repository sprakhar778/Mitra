from fastapi import FastAPI
import uvicorn
from src.interface.whatsapp.whatsapp_response import whatsapp_router

app = FastAPI()
app.include_router(whatsapp_router)

if __name__ == "__main__":

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)

# python -m uvicorn src.interface.whatsapp.webhook_endpoint:app --host 0.0.0.0 --port 8000
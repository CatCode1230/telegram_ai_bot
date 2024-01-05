import settings
import uvicorn

if __name__ == '__main__':
    uvicorn.run("chatbot_service:app", host=settings.APP_HOST, port=settings.APP_PORT, log_level="debug", workers=1, reload=False)
    

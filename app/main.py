from fastapi import FastAPI
from routers import router
import logging

#Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Energy Billing API", description="API for energy consumption and billing calculations")

app.include_router(router)

@app.on_event("startup")
async def startup_event():
    logger.info("Starting Energy Billing API")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down Energy Billing API")
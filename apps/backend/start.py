#!/usr/bin/env python3
"""
Production startup script for Amciu Day API
"""
import uvicorn
from app.core.settings import settings

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        log_level=settings.log_level.lower()
    )
#!/usr/bin/env python3
"""
Debug startup script for the Tyro Batch Manager service.
This script enables remote debugging with debugpy.
"""
import logging
import os
import sys
import traceback
from typing import TYPE_CHECKING, Type

import uvicorn
from dotenv import load_dotenv

if TYPE_CHECKING:
    from types import TracebackType

if __name__ == "__main__":
    # Load environment variables from .env file
    load_dotenv()
    
    # Check if debug mode is enabled
    debug_mode = os.getenv("DEBUG_MODE", "false").lower() == "true"
    
    if debug_mode:
        import debugpy  # type: ignore
        # Start debugpy server
        debugpy.listen(("0.0.0.0", 5678))
        print("🐛 Debug server started on port 5678")
        print("📌 You can now attach your debugger to localhost:5678")
        
        # Configure debugpy to break on exceptions
        # This will make the debugger stop when exceptions are raised
        break_on_exceptions = os.getenv("BREAK_ON_EXCEPTIONS", "true").lower() == "true"
        if break_on_exceptions:
            print("🔥 Configured to break on exceptions")
        
        # Wait for debugger if explicitly requested
        wait_for_debugger = os.getenv("WAIT_FOR_DEBUGGER", "false").lower() == "true"
        if wait_for_debugger:
            print("⏳ Waiting for debugger to attach...")
            debugpy.wait_for_client()
            print("🔗 Debugger attached! Continuing execution...")
        else:
            print("🚀 Starting server (debugger can attach at any time)")
    
    # Configure comprehensive logging
    log_level = os.getenv("LOG_LEVEL", "info").lower()
    
    # Set up detailed logging configuration
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
        ]
    )
    
    # Enable exception logging
    def handle_exception(exc_type: Type[BaseException], exc_value: BaseException, exc_traceback: "TracebackType | None") -> None:
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        
        logging.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
        print(f"🚨 UNCAUGHT EXCEPTION: {exc_type.__name__}: {exc_value}")
        traceback.print_exception(exc_type, exc_value, exc_traceback)
    
    sys.excepthook = handle_exception
    
    try:
        # Run the FastAPI application
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8000,
            log_level=log_level,
            reload=True if os.getenv("ENVIRONMENT") == "development" else False
        )
    except Exception as e:
        logging.critical(f"Failed to start server: {e}")
        print(f"🚨 SERVER STARTUP FAILED: {e}")
        traceback.print_exc()
        raise

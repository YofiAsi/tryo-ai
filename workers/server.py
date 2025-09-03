#!/usr/bin/env python3
"""
Main server entry point for tyro-workers with debugpy support.

This server runs the FastAPI application with debugpy enabled for remote debugging.
It can be attached to from VS Code using the launch.json configuration.
"""

import os
import sys
from pathlib import Path

import debugpy  # type: ignore

# Add the current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def setup_debugpy() -> None:
    """Setup debugpy for remote debugging."""
    # Check if debugpy is enabled via environment variable
    if os.getenv("DEBUG_MODE", "false").lower() == "true":
        debug_port = int(os.getenv("DEBUG_PORT", "5679"))
        debug_host = os.getenv("DEBUG_HOST", "0.0.0.0")
        
        print(f"Starting debugpy server on {debug_host}:{debug_port}")
        debugpy.listen((debug_host, debug_port))
        
        # Wait for debugger to attach if specified
        if os.getenv("WAIT_FOR_DEBUGGER", "false").lower() == "true":
            print("Waiting for debugger to attach...")
            debugpy.wait_for_client()
        else:
            print("Debugpy server started. Attach debugger when ready.")
    else:
        print("Debug mode disabled. Set DEBUG_MODE=true to enable debugging.")

def main() -> None:
    """Main entry point for the server."""
    # Setup debugpy first
    setup_debugpy()
    
    # Import and run the FastAPI app
    try:
        import uvicorn
        
        # Get configuration from environment
        host = os.getenv("HOST", "0.0.0.0")
        port = int(os.getenv("PORT", "8002"))
        log_level = os.getenv("LOG_LEVEL", "info").lower()
        
        print(f"Starting FastAPI server on {host}:{port}")
        print(f"API documentation available at: http://{host}:{port}/docs")
        
        # Run the server with reload enabled in development
        reload_enabled = os.getenv("ENVIRONMENT", "production").lower() == "development"
        
        if reload_enabled:
            # Use import string for reload mode
            uvicorn.run(
                "api.test_api:app",
                host=host,
                port=port,
                log_level=log_level,
                reload=True,
                access_log=True
            )
        else:
            # Import app directly for production mode
            from api.test_api import app
            uvicorn.run(
                app,
                host=host,
                port=port,
                log_level=log_level,
                reload=False,
                access_log=True
            )
        
    except ImportError as e:
        print(f"Failed to import FastAPI app: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Failed to start server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

"""
Sentry utility functions for manual event capture and custom monitoring
"""
import logging
from typing import Any, Dict, Optional
from functools import wraps
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

_log = logging.getLogger(__name__)


def capture_exception(exc: Exception, context: Optional[Dict[str, Any]] = None) -> None:
    """
    Manually capture an exception in Sentry
    
    Args:
        exc: The exception to capture
        context: Optional context data to include with the event
    """
    if context:
        sentry_sdk.set_context("custom", context)
    
    sentry_sdk.capture_exception(exc)
    _log.debug(f"Exception captured in Sentry: {type(exc).__name__}: {str(exc)}")


def capture_message(message: str, level: str = "info", context: Optional[Dict[str, Any]] = None) -> None:
    """
    Manually capture a message in Sentry
    
    Args:
        message: The message to capture
        level: Log level (debug, info, warning, error, fatal)
        context: Optional context data to include with the event
    """
    if context:
        sentry_sdk.set_context("custom", context)
    
    sentry_sdk.capture_message(message, level=level)
    _log.debug(f"Message captured in Sentry: {level.upper()}: {message}")


def set_user_context(user_id: str, email: Optional[str] = None, username: Optional[str] = None) -> None:
    """
    Set user context for Sentry events
    
    Args:
        user_id: Unique identifier for the user
        email: User's email address
        username: User's username
    """
    sentry_sdk.set_user({
        "id": user_id,
        "email": email,
        "username": username
    })
    _log.debug(f"User context set in Sentry: {user_id}")


def set_tag(key: str, value: str) -> None:
    """
    Set a tag for Sentry events
    
    Args:
        key: Tag key
        value: Tag value
    """
    sentry_sdk.set_tag(key, value)
    _log.debug(f"Tag set in Sentry: {key}={value}")


def set_context(name: str, data: Dict[str, Any]) -> None:
    """
    Set context data for Sentry events
    
    Args:
        name: Context name
        data: Context data dictionary
    """
    sentry_sdk.set_context(name, data)
    _log.debug(f"Context set in Sentry: {name}: {data}")


def add_breadcrumb(message: str, category: str = "app", level: str = "info", data: Optional[Dict[str, Any]] = None) -> None:
    """
    Add a breadcrumb for Sentry events
    
    Args:
        message: Breadcrumb message
        category: Breadcrumb category
        level: Breadcrumb level
        data: Optional data to include
    """
    sentry_sdk.add_breadcrumb(
        message=message,
        category=category,
        level=level,
        data=data
    )
    _log.debug(f"Breadcrumb added to Sentry: {category}: {message}")


def sentry_monitor(func):
    """
    Decorator to monitor function execution with Sentry
    
    Args:
        func: Function to monitor
        
    Returns:
        Decorated function
    """
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        with sentry_sdk.start_span(op="function", description=f"{func.__name__}"):
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as exc:
                capture_exception(exc, {
                    "function": func.__name__,
                    "args": str(args),
                    "kwargs": str(kwargs)
                })
                raise
    
    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        with sentry_sdk.start_span(op="function", description=f"{func.__name__}"):
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as exc:
                capture_exception(exc, {
                    "function": func.__name__,
                    "args": str(args),
                    "kwargs": str(kwargs)
                })
                raise
    
    # Return appropriate wrapper based on function type
    if hasattr(func, '__code__') and func.__code__.co_flags & 0x80:  # CO_COROUTINE
        return async_wrapper
    return sync_wrapper


def start_transaction(name: str, op: str = "http.request") -> sentry_sdk.tracing.Span:
    """
    Start a custom transaction in Sentry
    
    Args:
        name: Transaction name
        op: Operation type
        
    Returns:
        Sentry span object
    """
    return sentry_sdk.start_transaction(name=name, op=op)


def is_sentry_initialized() -> bool:
    """
    Check if Sentry is currently initialized and active
    
    Returns:
        True if Sentry is initialized, False otherwise
    """
    return sentry_sdk.get_current_hub().client is not None

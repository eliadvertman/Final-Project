"""Centralized error handling for the ML prediction service."""

import traceback
from functools import wraps
from flask import jsonify, request

from .exceptions import ServiceException, InvalidJSONException


def handle_errors(func):
    """
    Smart decorator to handle all errors consistently across controller methods.
    
    This decorator:
    - Automatically detects and validates JSON for POST/PUT requests
    - Catches ServiceException and returns appropriate HTTP response
    - Catches generic exceptions and returns 500 with logging
    - Maintains consistent error response format
    - Centralizes error logging
    
    Usage:
        @handle_errors
        def my_controller_method():
            # For JSON endpoints, just use request.get_json(force=True)
            # JSON validation happens automatically
            pass
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            # Auto-detect and validate JSON for POST/PUT requests with content
            if request.method in ['POST', 'PUT'] and request.get_data():
                try:
                    data = request.get_json(force=True)
                    if data is None:
                        raise InvalidJSONException()
                except Exception:
                    raise InvalidJSONException()
            
            return func(*args, **kwargs)
            
        except ServiceException as e:
            # Handle custom service exceptions with proper status codes
            return jsonify({
                "code": e.status_code, 
                "message": e.message
            }), e.status_code
            
        except Exception as e:
            # Handle unexpected exceptions with logging
            print(f"Error in {func.__name__}: {str(e)}")
            traceback.print_exc()
            return jsonify({
                "code": 500, 
                "message": "Internal server error"
            }), 500
    
    return wrapper
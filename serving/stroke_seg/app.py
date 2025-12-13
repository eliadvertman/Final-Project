import time

from flask import Flask, jsonify
from flask_cors import CORS

from stroke_seg.controller import model_bp, prediction_bp
from stroke_seg.controller.training_controller import training_bp
from stroke_seg.controller.evaluation_controller import evaluation_bp
from stroke_seg.dao.database import get_pool_status, verify_connection, database
from stroke_seg.config import validate_template_files
from stroke_seg.logging_config import setup_logging, get_logger, add_request_id_to_request, log_request_info
from stroke_seg.bl.poller.poller_facade import PollerFacade

app = Flask(__name__)
CORS(app)

# Setup logging
setup_logging('pic_service')
logger = get_logger(__name__)

# Initialize job poller facade
poller_facade = PollerFacade()

# Verify database connection and create tables on startup
if verify_connection():
    logger.info("Database connection verified")
else:
    logger.error("Failed to connect to database - application may not work properly")

# Validate template files on startup
try:
    validate_template_files()
    logger.info("Template files validation successful")
except FileNotFoundError as e:
    logger.error(f"Template files validation failed: {str(e)}")
    logger.error("Application startup failed - missing required template files")
    exit(1)
except Exception as e:
    logger.error(f"Unexpected error during template validation: {str(e)}")
    exit(1)

# Start job poller
try:
    poller_facade.start()
    logger.info("Job poller started successfully")
except Exception as e:
    logger.error(f"Failed to start job poller: {str(e)}")

# Register blueprints
app.register_blueprint(training_bp)
app.register_blueprint(model_bp)
app.register_blueprint(prediction_bp)
app.register_blueprint(evaluation_bp)


# Request logging middleware
@app.before_request
def before_request():
    """Add request ID and start timing."""
    database.connect()
    add_request_id_to_request()
    from flask import request
    request.start_time = time.time()
    logger.info(f"Request started - {request.method} {request.path}")

@app.after_request
def after_request(response):
    """Log request completion."""
    from flask import request
    if hasattr(request, 'start_time'):
        log_request_info(logger, request.start_time, response.status_code)
    if not database.is_closed():
        database.close()
    return response

@app.route('/health/db')
def db_health():
    """Database connection pool health check endpoint."""
    try:
        logger.debug("Checking database connection pool health")
        pool_status = get_pool_status()
        logger.info(f"Database health check successful - Active connections: {pool_status.get('active_connections', 'unknown')}")
        return jsonify({
            "status": "healthy",
            "pool": pool_status
        })
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}", exc_info=True)
        return jsonify({
            "status": "unhealthy", 
            "error": str(e)
        }), 500

@app.route('/health/poller')
def poller_health():
    """Job poller health check endpoint."""
    try:
        logger.debug("Checking job poller health")
        poller_status = poller_facade.get_status()
        
        is_healthy = poller_status.get('facade_running', False) and poller_status.get('poller_status', {}).get('is_running', False)
        
        logger.info(f"Poller health check - Running: {is_healthy}")
        
        return jsonify({
            "status": "healthy" if is_healthy else "unhealthy",
            "poller": poller_status
        }), 200 if is_healthy else 503
        
    except Exception as e:
        logger.error(f"Poller health check failed: {str(e)}", exc_info=True)
        return jsonify({
            "status": "unhealthy",
            "error": str(e)
        }), 500

@app.route('/health')
def overall_health():
    """Overall application health check endpoint."""
    try:
        # Check database
        db_healthy = True
        try:
            get_pool_status()
        except Exception:
            db_healthy = False
        
        # Check poller
        poller_healthy = poller_facade.is_running
        
        overall_healthy = db_healthy and poller_healthy
        
        return jsonify({
            "status": "healthy" if overall_healthy else "unhealthy",
            "components": {
                "database": "healthy" if db_healthy else "unhealthy",
                "poller": "healthy" if poller_healthy else "unhealthy"
            }
        }), 200 if overall_healthy else 503
        
    except Exception as e:
        logger.error(f"Overall health check failed: {str(e)}", exc_info=True)
        return jsonify({
            "status": "unhealthy",
            "error": str(e)
        }), 500

# Error handling is now centralized in controllers using @handle_errors decorator

if __name__ == '__main__':
    logger.info("Starting POC ML Prediction Service on port 8080")
    app.run(debug=True, host='0.0.0.0', port=8080)
from flask import Flask, jsonify
from flask_cors import CORS

from .dao.database import database as db, get_pool_status
from .controller import model_bp, prediction_bp

app = Flask(__name__)
CORS(app)

# Register blueprints
app.register_blueprint(model_bp)
app.register_blueprint(prediction_bp)

# Connection pool handles connections automatically - no manual management needed

@app.route('/health/db')
def db_health():
    """Database connection pool health check endpoint."""
    try:
        pool_status = get_pool_status()
        return jsonify({
            "status": "healthy",
            "pool": pool_status
        })
    except Exception as e:
        return jsonify({
            "status": "unhealthy", 
            "error": str(e)
        }), 500

# Error handling is now centralized in controllers using @handle_errors decorator

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
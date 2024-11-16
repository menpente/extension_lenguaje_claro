from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import groq
import os
import redis
import hashlib
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Initialize Redis
redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
try:
    redis_client = redis.from_url(redis_url)
except:
    print(f"Warning: Could not connect to Redis at {redis_url}")
    redis_client = None

# Initialize rate limiter
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# Initialize Groq client
groq_client = groq.Groq(
    api_key=os.getenv('GROQ_API_KEY')
)

@app.route('/')
def index():
    """Root route that returns API status"""
    return jsonify({
        'status': 'online',
        'message': 'Text Simplification API is running',
        'endpoints': {
            'simplify': '/simplify',
            'health': '/health'
        },
        'version': '1.0.0'
    })

@app.route('/health')
def health_check():
    """Health check endpoint"""
    status = {
        'api': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'redis': 'connected' if redis_client else 'disconnected',
        'groq': 'configured' if os.getenv('GROQ_API_KEY') else 'not configured'
    }
    return jsonify(status)

@app.route('/simplify', methods=['POST'])
@limiter.limit("100/day;10/minute")
def simplify():
    """Text simplification endpoint"""
    try:
        data = request.json
        if not data:
            return jsonify({
                'error': 'No JSON data provided',
                'status': 'error'
            }), 400

        text = data.get('text', '')
        style = data.get('style', 'standard')

        if not text:
            return jsonify({
                'error': 'No text provided',
                'status': 'error'
            }), 400

        # Process the text (simplified version for testing)
        simplified_text = f"Simplified version of your text. Style: {style}"
        
        return jsonify({
            'simplified_text': simplified_text,
            'status': 'success',
            'style': style
        })

    except Exception as e:
        app.logger.error(f"Error processing request: {str(e)}")
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

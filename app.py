# app.py
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

# Initialize Redis for caching and rate limiting
redis_client = redis.from_url(os.getenv('REDIS_URL', 'redis://localhost:6379'))

# Initialize rate limiter
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    storage_uri=os.getenv('REDIS_URL', 'redis://localhost:6379')
)

# Initialize Groq client
groq_client = groq.Groq(
    api_key=os.getenv('GROQ_API_KEY')
)

class SimplificationCache:
    @staticmethod
    def get_cache_key(text):
        return f"simplify:{hashlib.md5(text.encode()).hexdigest()}"

    def get_cached_result(self, text):
        cache_key = self.get_cache_key(text)
        cached = redis_client.get(cache_key)
        return cached.decode() if cached else None

    def cache_result(self, text, result, expire_time=3600):  # Cache for 1 hour
        cache_key = self.get_cache_key(text)
        redis_client.setex(cache_key, expire_time, result)

cache = SimplificationCache()

def get_simplification_prompt(style='standard'):
    prompts = {
        'standard': """Eres un experto en lenguaje claro. Las pautas básicas para lenguaje claro son:
    - Expresar una idea por oración.
    - Utilizar oraciones de treinta palabras o menos.
    - Evitar la jerga.
    - Seguir el orden sujeto, verbo y predicado.
    - Utilizar una estructura lógica, organizando la información de manera clara y coherente.
    Evalúa la calidad del lenguaje de este texto y sugiere las correcciones oportunas. 
    Muestra siempre primero el texto corregido y a continuación las explicaciones. El texto generado debe estar siempre en español""",
        'elementary': """Rewrite this text for an elementary school student. 
                        Use very simple words and short sentences.""",
        'technical': """Simplify this technical content while maintaining accuracy. 
                       Define specialized terms and break down complex concepts."""
    }
    return prompts.get(style, prompts['standard'])

def simplify_text(text, style='standard'):
    # Check cache first
    cached_result = cache.get_cached_result(f"{style}:{text}")
    if cached_result:
        return cached_result

    prompt = f"""{get_simplification_prompt(style)}

    Text to simplify:
    {text}

    Simplified version:"""

    try:
        completion = groq_client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model="mixtral-8x7b-32768",
            temperature=0.3,
            max_tokens=4000,
        )
        
        result = completion.choices[0].message.content
        # Cache the result
        cache.cache_result(f"{style}:{text}", result)
        return result
    except Exception as e:
        raise Exception(f"Simplification error: {str(e)}")

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

@app.route('/simplify', methods=['POST'])
@limiter.limit("100/day;10/minute")  # Rate limiting
def simplify():
    try:
        data = request.json
        text = data.get('text', '')
        style = data.get('style', 'standard')

        if not text:
            return jsonify({
                'error': 'No text provided',
                'status': 'error'
            }), 400

        # Break text into chunks if it's too long
        max_chunk_size = 4000
        chunks = [text[i:i+max_chunk_size] for i in range(0, len(text), max_chunk_size)]
        
        # Process each chunk
        simplified_chunks = []
        for chunk in chunks:
            simplified_chunk = simplify_text(chunk, style)
            simplified_chunks.append(simplified_chunk)
        
        simplified_text = ' '.join(simplified_chunks)
        
        return jsonify({
            'simplified_text': simplified_text,
            'status': 'success',
            'style': style
        })

    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))

from flask import Flask, render_template, request, jsonify
import sys
import os
import requests
from urllib.parse import quote_plus
import time
import random

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fake_news_detector import FakeNewsDetector

app = Flask(__name__)

# Sample news database for fallback
SAMPLE_NEWS = [
    {"title": "Climate Change: New Report Shows Rising Sea Levels", "description": "Scientists warn about accelerating climate change impacts on coastal regions", "source": "Climate News"},
    {"title": "Tech Giants Report Record Quarterly Earnings", "description": "Major technology companies exceed analyst expectations", "source": "Business News"},
    {"title": "World Health Organization Updates Health Guidelines", "description": "New recommendations for public health safety", "source": "Health News"},
    {"title": "Scientists Discover New Deep Sea Species", "description": "Marine biologists find previously unknown fish species in Pacific Ocean", "source": "Science Daily"},
    {"title": "Global Markets React to Economic Policy Changes", "description": "Stock markets show mixed reactions to new policies", "source": "Financial Times"},
    {"title": "BREAKING: Scientists Find Miracle Cure for Cancer", "description": "Revolutionary treatment discovered in common household item", "source": "Unknown Source"},
    {"title": "Aliens Have Landed in Major City", "description": "Government officials confirm extraterrestrial contact", "source": "Unverified News"},
    {"title": "Government Admits to Secret Weather Control Program", "description": "Documents reveal hidden weather manipulation project", "source": "Conspiracy News"},
    {"title": "New Study Proves Eating Chocolate Makes You Smarter", "description": "Researchers claim chocolate improves cognitive function", "source": "Health Blog"},
    {"title": "Time Travel Now Possible Say Scientists", "description": "Quantum physics breakthrough enables time travel", "source": "Tech Speculation"},
    {"title": "International Space Station Conducts New Experiments", "description": "Astronauts work on cutting-edge research in microgravity", "source": "NASA News"},
    {"title": "Local School District Implements New Education Program", "description": "STEM curriculum to be introduced in elementary schools", "source": "Education News"},
]

# Initialize the fake news detector with pre-trained model
detector = FakeNewsDetector()

# Load the pre-trained model
try:
    detector.load_model('vectorizer.pkl', 'fake_news_model.pkl')
    print("Model loaded successfully!")
except Exception as e:
    print(f"Warning: Could not load pre-trained model: {e}")
    print("Using untrained model - predictions may not be accurate")


@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')


@app.route('/analyze', methods=['POST'])
def analyze():
    """Analyze text for fake news"""
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({'error': 'No text provided'}), 400
        
        text = data['text'].strip()
        
        if not text:
            return jsonify({'error': 'Empty text provided'}), 400
        
        if len(text) < 10:
            return jsonify({'error': 'Text is too short for analysis (minimum 10 characters)'}), 400
        
        # Make prediction
        result = detector.predict(text)
        
        # Format response
        response = {
            'success': True,
            'result': {
                'is_fake': result['is_fake'],
                'label': 'FAKE NEWS' if result['is_fake'] else 'REAL NEWS',
                'confidence': round(result['confidence'] * 100, 2),
                'probability_fake': round(result['probability_fake'] * 100, 2),
                'probability_real': round(result['probability_real'] * 100, 2)
            }
        }
        
        return jsonify(response)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/search-news', methods=['POST'])
def search_news():
    """Search news from multiple sources with fallback"""
    try:
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({'error': 'No search query provided'}), 400
        
        query = data['query'].strip().lower()
        
        if not query:
            return jsonify({'error': 'Empty search query'}), 400
        
        # Search results list
        results = []
        
        # Try Hacker News API first (most reliable)
        try:
            url = f"https://hn.algolia.com/api/v1/search?query={quote_plus(query)}&tags=story&hitsPerPage=10"
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers, timeout=5)
            
            if response.status_code == 200:
                json_data = response.json()
                hits = json_data.get('hits', [])
                
                for hit in hits:
                    results.append({
                        'title': hit.get('title', '')[:200],
                        'description': f"Points: {hit.get('points', 0)} | By: {hit.get('author', 'unknown')}",
                        'url': hit.get('url', f"https://news.ycombinator.com/item?id={hit.get('objectID', '')}"),
                        'source': 'Hacker News',
                        'published_at': ''
                    })
        except Exception as e:
            print(f"HN Error: {e}")
        
        # If no results from HN, use sample news filtered by query
        if not results:
            for news in SAMPLE_NEWS:
                if query in news['title'].lower() or query in news['description'].lower():
                    results.append({
                        'title': news['title'],
                        'description': news['description'],
                        'url': '#',
                        'source': news['source'],
                        'published_at': ''
                    })
            
            # If still no matches, return random sample news
            if not results:
                results = random.sample(SAMPLE_NEWS, min(6, len(SAMPLE_NEWS)))
                for r in results:
                    r['url'] = '#'
        
        # Remove duplicates
        seen = set()
        unique_results = []
        for item in results:
            title_lower = item['title'].lower().strip()
            if title_lower and title_lower not in seen:
                seen.add(title_lower)
                unique_results.append(item)
        
        # Analyze each news item
        analyzed_results = []
        for item in unique_results[:12]:
            full_text = f"{item['title']} {item.get('description', '')}"
            prediction = detector.predict(full_text)
            
            analyzed_results.append({
                'title': item['title'],
                'description': item.get('description', ''),
                'source': item['source'],
                'url': item['url'],
                'published_at': item.get('published_at', ''),
                'is_fake': prediction['is_fake'],
                'label': 'FAKE NEWS' if prediction['is_fake'] else 'REAL NEWS',
                'confidence': round(prediction['confidence'] * 100, 2),
                'probability_fake': round(prediction['probability_fake'] * 100, 2),
                'probability_real': round(prediction['probability_real'] * 100, 2)
            })
        
        return jsonify({
            'success': True,
            'query': query,
            'total_results': len(analyzed_results),
            'results': analyzed_results
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/batch-analyze', methods=['POST'])
def batch_analyze():
    """Analyze multiple texts for fake news"""
    try:
        data = request.get_json()
        
        if not data or 'texts' not in data:
            return jsonify({'error': 'No texts provided'}), 400
        
        texts = data['texts']
        
        if not isinstance(texts, list):
            return jsonify({'error': 'Texts must be a list'}), 400
        
        if len(texts) > 10:
            return jsonify({'error': 'Maximum 10 texts allowed at once'}), 400
        
        results = []
        for text in texts:
            if not text.strip():
                continue
            
            result = detector.predict(text.strip())
            results.append({
                'text': text[:100] + '...' if len(text) > 100 else text,
                'is_fake': result['is_fake'],
                'label': 'FAKE NEWS' if result['is_fake'] else 'REAL NEWS',
                'confidence': round(result['confidence'] * 100, 2)
            })
        
        return jsonify({
            'success': True,
            'results': results
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

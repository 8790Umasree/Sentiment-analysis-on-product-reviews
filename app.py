from flask import Flask, render_template, request, jsonify
import re
from collections import Counter

app = Flask(__name__)

class SimpleSentimentAnalyzer:
    def __init__(self):
        # Simple word lists for sentiment analysis
        self.positive_words = {
            'excellent', 'amazing', 'great', 'good', 'awesome', 'fantastic', 
            'wonderful', 'perfect', 'love', 'best', 'outstanding', 'brilliant',
            'superb', 'nice', 'beautiful', 'incredible', 'satisfied', 'happy',
            'pleased', 'delighted', 'impressive', 'quality', 'recommend',
            'worthwhile', 'useful', 'helpful', 'smooth', 'fast', 'efficient'
        }
        
        self.negative_words = {
            'terrible', 'awful', 'bad', 'horrible', 'worst', 'hate', 'disgusting',
            'disappointing', 'poor', 'useless', 'broken', 'defective', 'slow',
            'expensive', 'overpriced', 'waste', 'regret', 'unhappy', 'frustrated',
            'annoying', 'difficult', 'complicated', 'confusing', 'cheap',
            'fake', 'damaged', 'wrong', 'failed', 'problem', 'issue'
        }
    
    def preprocess_text(self, text):
        """Clean and preprocess the text"""
        text = text.lower()
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        words = text.split()
        return words
    
    def analyze_sentiment(self, text):
        """Analyze sentiment of the given text"""
        words = self.preprocess_text(text)
        
        positive_score = sum(1 for word in words if word in self.positive_words)
        negative_score = sum(1 for word in words if word in self.negative_words)
        
        # Calculate sentiment
        total_sentiment_words = positive_score + negative_score
        
        if total_sentiment_words == 0:
            return "neutral", 0.0
        
        sentiment_ratio = (positive_score - negative_score) / len(words)
        confidence = total_sentiment_words / len(words) if words else 0
        
        if positive_score > negative_score:
            return "positive", min(confidence * 100, 100)
        elif negative_score > positive_score:
            return "negative", min(confidence * 100, 100)
        else:
            return "neutral", min(confidence * 100, 100)

# Initialize the sentiment analyzer
analyzer = SimpleSentimentAnalyzer()

# Store reviews in memory (in production, use a database)
reviews_db = []

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze_review():
    try:
        data = request.get_json()
        review_text = data.get('review', '').strip()
        product_name = data.get('product', 'Unknown Product').strip()
        
        if not review_text:
            return jsonify({'error': 'Review text is required'}), 400
        
        # Analyze sentiment
        sentiment, confidence = analyzer.analyze_sentiment(review_text)
        
        # Store the review
        review_entry = {
            'id': len(reviews_db) + 1,
            'product': product_name,
            'review': review_text,
            'sentiment': sentiment,
            'confidence': round(confidence, 2)
        }
        reviews_db.append(review_entry)
        
        return jsonify({
            'sentiment': sentiment,
            'confidence': round(confidence, 2),
            'product': product_name,
            'review_id': review_entry['id']
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/reviews')
def get_reviews():
    """Get all stored reviews"""
    return jsonify({'reviews': reviews_db})

@app.route('/stats')
def get_stats():
    """Get sentiment statistics"""
    if not reviews_db:
        return jsonify({
            'total_reviews': 0,
            'positive': 0,
            'negative': 0,
            'neutral': 0
        })
    
    sentiment_counts = Counter(review['sentiment'] for review in reviews_db)
    
    return jsonify({
        'total_reviews': len(reviews_db),
        'positive': sentiment_counts.get('positive', 0),
        'negative': sentiment_counts.get('negative', 0),
        'neutral': sentiment_counts.get('neutral', 0)
    })

@app.route('/clear')
def clear_reviews():
    """Clear all reviews"""
    global reviews_db
    reviews_db = []
    return jsonify({'message': 'All reviews cleared'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
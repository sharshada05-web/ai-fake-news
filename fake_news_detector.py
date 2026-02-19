import os
import ssl
import re
import string
from typing import Dict, List, Tuple
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import joblib

# Fix SSL certificate verification for NLTK downloads
import ssl
if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
    getattr(ssl, '_create_unverified_context', None)): 
    ssl._create_default_https_context = ssl._create_unverified_context

nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)

class FakeNewsDetector:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1, 2))
        self.model = LogisticRegression(max_iter=1000)
        self.stop_words = set(stopwords.words('english'))
        
    def preprocess_text(self, text: str) -> str:
        """Clean and preprocess text data"""
        # Convert to lowercase
        text = text.lower()
        
        # Remove URLs
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        
        # Remove email addresses
        text = re.sub(r'\S+@\S+', '', text)
        
        # Remove special characters and digits
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Remove stopwords
        words = word_tokenize(text)
        words = [word for word in words if word not in self.stop_words]
        
        return ' '.join(words)
    
    def train(self, texts: List[str], labels: List[int]) -> Dict[str, float]:
        """Train the fake news detection model"""
        # Preprocess texts
        processed_texts = [self.preprocess_text(text) for text in texts]
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            processed_texts, labels, test_size=0.2, random_state=42
        )
        
        # Vectorize
        X_train_vec = self.vectorizer.fit_transform(X_train)
        X_test_vec = self.vectorizer.transform(X_test)
        
        # Train model
        self.model.fit(X_train_vec, y_train)
        
        # Evaluate
        y_pred = self.model.predict(X_test_vec)
        metrics = {
            'accuracy': accuracy_score(y_test, y_pred),
            'precision': precision_score(y_test, y_pred, zero_division=0),
            'recall': recall_score(y_test, y_pred, zero_division=0),
            'f1_score': f1_score(y_test, y_pred, zero_division=0)
        }
        
        return metrics
    
    def predict(self, text: str) -> Dict[str, any]:
        """Predict if a text is fake news"""
        processed_text = self.preprocess_text(text)
        text_vec = self.vectorizer.transform([processed_text])
        
        prediction = self.model.predict(text_vec)[0]
        probability = self.model.predict_proba(text_vec)[0]
        
        return {
            'is_fake': bool(prediction),
            'confidence': max(probability),
            'probability_fake': probability[1],
            'probability_real': probability[0]
        }
    
    def save_model(self, vectorizer_path: str, model_path: str):
        """Save the trained model and vectorizer"""
        joblib.dump(self.vectorizer, vectorizer_path)
        joblib.dump(self.model, model_path)
    
    def load_model(self, vectorizer_path: str, model_path: str):
        """Load a pre-trained model and vectorizer"""
        self.vectorizer = joblib.load(vectorizer_path)
        self.model = joblib.load(model_path)


def create_sample_dataset() -> Tuple[List[str], List[int]]:
    """Create a sample dataset for demonstration"""
    fake_news = [
        "Breaking: Aliens have landed in New York City! Government confirms extraterrestrial contact.",
        "Scientists discover a new planet made entirely of gold in our solar system.",
        "World leaders announce a secret pact to control the weather using advanced technology.",
        "Miracle cure for cancer found in common household plant, doctors amazed.",
        "Time travel is now possible, scientists reveal breakthrough in quantum physics.",
        "Government admits to hiding evidence of Bigfoot for decades.",
        "New study proves that eating chocolate for breakfast makes you smarter.",
        "Aliens built the pyramids, ancient astronaut theory confirmed.",
        "Secret society controls world governments, leaked documents reveal.",
        "Scientists create immortality pill, human trials begin next year."
    ]
    
    real_news = [
        "The Federal Reserve announced a 0.25% interest rate hike today.",
        "Local school district implements new STEM curriculum for elementary students.",
        "Researchers publish new findings on climate change impacts in coastal regions.",
        "Tech company unveils latest smartphone with advanced camera features.",
        "Government passes new healthcare legislation affecting millions of Americans.",
        "Stock market reaches record highs amid strong economic indicators.",
        "Scientists discover new species of deep-sea fish in Pacific Ocean.",
        "City council approves new public transportation infrastructure project.",
        "Study shows benefits of regular exercise on mental health and cognitive function.",
        "International space station crew conducts experiments in microgravity environment."
    ]
    
    texts = fake_news + real_news
    labels = [1] * len(fake_news) + [0] * len(real_news)  # 1 = fake, 0 = real
    
    return texts, labels

if __name__ == "__main__":
    # Create and train the detector
    detector = FakeNewsDetector()
    
    # Create sample dataset
    texts, labels = create_sample_dataset()
    
    # Train the model
    metrics = detector.train(texts, labels)
    print("Training Metrics:")
    for metric, value in metrics.items():
        print(f"  {metric}: {value:.4f}")
    
    # Test with some examples
    test_texts = [
        "Scientists discover a new planet made entirely of gold in our solar system.",
        "The Federal Reserve announced a 0.25% interest rate hike today.",
        "Aliens built the pyramids, ancient astronaut theory confirmed.",
        "Local school district implements new STEM curriculum for elementary students."
    ]
    
    print("\nPredictions:")
    for text in test_texts:
        result = detector.predict(text)
        print(f"Text: {text[:50]}...")
        print(f"  Is Fake: {result['is_fake']}")
        print(f"  Confidence: {result['confidence']:.4f}")
        print(f"  Probability Fake: {result['probability_fake']:.4f}")
        print(f"  Probability Real: {result['probability_real']:.4f}")
        print()
    
    # Save the model
    detector.save_model('vectorizer.pkl', 'fake_news_model.pkl')
    print("Model saved successfully!")
# Fake News Detector

An AI-powered fake news detection system using machine learning and natural language processing.

## Features

- **Text Preprocessing**: Cleans and normalizes text data
- **Machine Learning**: Uses TF-IDF vectorization and Logistic Regression
- **Prediction**: Classifies text as real or fake news with confidence scores
- **Model Persistence**: Save and load trained models
- **Comprehensive Testing**: Unit tests for all functionality

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

```python
from fake_news_detector import FakeNewsDetector

# Initialize detector
detector = FakeNewsDetector()

# Train with your own data
detector.train(texts, labels)

# Make predictions
result = detector.predict("Your news text here")
print(f"Is fake: {result['is_fake']}")
print(f"Confidence: {result['confidence']:.2f}")
```

### Using Pre-trained Model

```python
from fake_news_detector import FakeNewsDetector

detector = FakeNewsDetector()
detector.load_model('vectorizer.pkl', 'fake_news_model.pkl')

result = detector.predict("Your news text here")
```

## API

### FakeNewsDetector Class

#### Methods

- `preprocess_text(text: str) -> str`: Clean and preprocess text
- `train(texts: List[str], labels: List[int]) -> Dict[str, float]`: Train the model
- `predict(text: str) -> Dict[str, any]`: Predict if text is fake news
- `save_model(vectorizer_path: str, model_path: str)`: Save trained model
- `load_model(vectorizer_path: str, model_path: str)`: Load pre-trained model

#### Return Values

- `predict()` returns a dictionary with:
  - `is_fake`: Boolean indicating if text is fake news
  - `confidence`: Confidence score (0-1)
  - `probability_fake`: Probability of being fake news
  - `probability_real`: Probability of being real news

## Testing

Run the test suite:

```bash
python -m unittest test_fake_news_detector.py
```

## Sample Dataset

The detector includes a sample dataset with:
- **Fake News Examples**: Aliens, miracle cures, time travel, etc.
- **Real News Examples**: Financial news, education, science, etc.

## Performance Metrics

- **Accuracy**: Overall correctness of predictions
- **Precision**: How many predicted fake news are actually fake
- **Recall**: How many actual fake news are detected
- **F1 Score**: Harmonic mean of precision and recall

## Dependencies

- `numpy`: Numerical computing
- `scikit-learn`: Machine learning algorithms
- `nltk`: Natural language processing
- `joblib`: Model persistence

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request
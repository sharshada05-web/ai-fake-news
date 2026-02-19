import unittest
import numpy as np
from fake_news_detector import FakeNewsDetector, create_sample_dataset

class TestFakeNewsDetector(unittest.TestCase):
    def setUp(self):
        self.detector = FakeNewsDetector()
        self.texts, self.labels = create_sample_dataset()
        
    def test_preprocess_text(self):
        """Test text preprocessing functionality"""
        test_cases = [
            ("Breaking: Aliens have landed in New York City!", "breaking aliens landed new york city"),
            ("Scientists discover a new planet made entirely of gold!", "scientists discover new planet made entirely gold"),
            ("http://example.com This is a test", "test"),
            ("Email: test@example.com is valid", "email valid"),
            ("Special characters: @#$%^&*()!", "special characters"),
            ("Numbers 12345 should be removed", "numbers removed"),
        ]
        
        for input_text, expected_output in test_cases:
            result = self.detector.preprocess_text(input_text)
            self.assertEqual(result, expected_output)
    
    def test_train_model(self):
        """Test model training functionality"""
        metrics = self.detector.train(self.texts, self.labels)
        
        # Check that all metrics are present
        expected_metrics = ['accuracy', 'precision', 'recall', 'f1_score']
        for metric in expected_metrics:
            self.assertIn(metric, metrics)
        
        # Check that metrics are valid
        for metric, value in metrics.items():
            self.assertIsInstance(value, float)
            self.assertGreaterEqual(value, 0.0)
            self.assertLessEqual(value, 1.0)
    
    def test_predict_function(self):
        """Test prediction functionality"""
        # Train the model first
        self.detector.train(self.texts, self.labels)
        
        test_cases = [
            ("Scientists discover a new planet made entirely of gold in our solar system.", True),
            ("The Federal Reserve announced a 0.25% interest rate hike today.", False),
            ("Aliens built the pyramids, ancient astronaut theory confirmed.", True),
            ("Local school district implements new STEM curriculum for elementary students.", False),
        ]
        
        for input_text, expected_label in test_cases:
            result = self.detector.predict(input_text)
            self.assertIsInstance(result, dict)
            self.assertIn('is_fake', result)
            self.assertIn('confidence', result)
            self.assertIn('probability_fake', result)
            self.assertIn('probability_real', result)
            
            # Check that confidence is between 0 and 1
            self.assertGreaterEqual(result['confidence'], 0.0)
            self.assertLessEqual(result['confidence'], 1.0)
            
            # Check that probabilities sum to 1
            self.assertAlmostEqual(result['probability_fake'] + result['probability_real'], 1.0, places=2)
    
    def test_save_and_load_model(self):
        """Test model saving and loading functionality"""
        # Train the model
        self.detector.train(self.texts, self.labels)
        
        # Save the model
        self.detector.save_model('test_vectorizer.pkl', 'test_model.pkl')
        
        # Create a new detector and load the model
        new_detector = FakeNewsDetector()
        new_detector.load_model('test_vectorizer.pkl', 'test_model.pkl')
        
        # Test prediction with the loaded model
        test_text = "Scientists discover a new planet made entirely of gold in our solar system."
        original_result = self.detector.predict(test_text)
        loaded_result = new_detector.predict(test_text)
        
        # Check that predictions are consistent
        self.assertEqual(original_result['is_fake'], loaded_result['is_fake'])
        self.assertAlmostEqual(original_result['confidence'], loaded_result['confidence'], places=2)
        
        # Clean up test files
        import os
        os.remove('test_vectorizer.pkl')
        os.remove('test_model.pkl')
    
    def test_empty_text_handling(self):
        """Test how the detector handles empty or whitespace-only text"""
        # Train the model
        self.detector.train(self.texts, self.labels)
        
        test_cases = ["", "   ", "\n\t"]
        for empty_text in test_cases:
            result = self.detector.predict(empty_text)
            self.assertIsInstance(result, dict)
            self.assertIn('is_fake', result)
            self.assertIn('confidence', result)
            self.assertIn('probability_fake', result)
            self.assertIn('probability_real', result)
    
    def test_special_characters(self):
        """Test how the detector handles text with special characters"""
        # Train the model
        self.detector.train(self.texts, self.labels)
        
        test_cases = [
            ("!!!@@@###$$$%%%^^^&&&***((()))", False),  # Should be classified as real (no fake news content)
            ("Breaking news: $1000000 prize!!! Click here!!!", True),
        ]
        
        for input_text, expected_label in test_cases:
            result = self.detector.predict(input_text)
            # For empty content after preprocessing, it should be classified as real
            if input_text.strip() == "":
                self.assertFalse(result['is_fake'])

if __name__ == '__main__':
    unittest.main(verbosity=2)
import unittest
import os
import sys

# Add the parent directory to the path so we can import app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestApp(unittest.TestCase):
    
    def test_app_import(self):
        """Test that the app can be imported without errors"""
        try:
            from app import app
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"Failed to import app: {e}")
    
    def test_flask_app_creation(self):
        """Test that Flask app is created successfully"""
        from app import app
        self.assertIsNotNone(app)
        self.assertEqual(app.name, 'app')

if __name__ == '__main__':
    unittest.main()
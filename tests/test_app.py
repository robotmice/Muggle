import unittest
from flask import Flask
from muggle.app import create_app

class TestApp(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def test_app_factory(self):
        """Test that the application factory creates a Flask instance."""
        self.assertIsInstance(self.app, Flask)
        self.assertTrue(hasattr(self.app, 'processor'))
        self.assertTrue(hasattr(self.app, 'registry'))

    def test_health_endpoint_healthy(self):
        """Test the /health endpoint returns 200 when initialized."""
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['status'], 'healthy')

    def test_health_endpoint_unhealthy(self):
        """Test the /health endpoint returns 503 when processor is not ready."""
        # Manually set processor to not ready
        self.app.processor._ready = False
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json['status'], 'unhealthy')

    def test_chat_endpoint_routing(self):
        """Test that /chat is correctly routed to the chat blueprint."""
        # We don't need to test AI logic here, just that the route exists
        response = self.client.post('/chat', json={})
        self.assertEqual(response.status_code, 400) # Missing message field

    def test_static_index(self):
        """Test that the root route serves the index page."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()

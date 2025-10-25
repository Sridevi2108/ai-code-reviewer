import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from models import init_db, SessionLocal, CodeReview
import json

@pytest.fixture
def client():
    """Create test client"""
    app.config['TESTING'] = True
    
    # Initialize test database
    with app.app_context():
        init_db()
    
    with app.test_client() as client:
        yield client
    
    # Cleanup
    db = SessionLocal()
    try:
        db.query(CodeReview).delete()
        db.commit()
    finally:
        db.close()

@pytest.fixture
def sample_review(client):
    """Create a sample review for testing"""
    response = client.post('/api/review', 
        data=json.dumps({
            'code': 'def hello():\n    print("Hello World")',
            'language': 'python'
        }),
        content_type='application/json'
    )
    
    if response.status_code == 201:
        return response.get_json()['review']
    return None


class TestHealthEndpoint:
    """Tests for health check endpoint"""
    
    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get('/api/health')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'healthy'


class TestReviewCreation:
    """Tests for POST /api/review endpoint"""
    
    def test_create_review_success(self, client):
        """Test successful review creation"""
        response = client.post('/api/review',
            data=json.dumps({
                'code': 'def add(a, b):\n    return a + b',
                'language': 'python'
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['success'] is True
        assert 'review' in data
        assert 'quality_score' in data['review']
        assert 'review_text' in data['review']
    
    def test_create_review_missing_code(self, client):
        """Test review creation without code"""
        response = client.post('/api/review',
            data=json.dumps({
                'language': 'python'
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
    
    def test_create_review_missing_language(self, client):
        """Test review creation without language"""
        response = client.post('/api/review',
            data=json.dumps({
                'code': 'print("hello")'
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
    
    def test_create_review_empty_code(self, client):
        """Test review creation with empty code"""
        response = client.post('/api/review',
            data=json.dumps({
                'code': '',
                'language': 'python'
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 400
    
    def test_create_review_unsupported_language(self, client):
        """Test review creation with unsupported language"""
        response = client.post('/api/review',
            data=json.dumps({
                'code': 'some code',
                'language': 'brainfuck'
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 400
    
    def test_create_review_no_json(self, client):
        """Test review creation without JSON body"""
        response = client.post('/api/review',
            data='not json',
            content_type='text/plain'
        )
        
        assert response.status_code == 400


class TestReviewRetrieval:
    """Tests for GET /api/reviews endpoint"""
    
    def test_get_reviews_empty(self, client):
        """Test getting reviews when none exist"""
        response = client.get('/api/reviews')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert len(data['data']['reviews']) == 0
        assert data['data']['total'] == 0
    
    def test_get_reviews_with_data(self, client, sample_review):
        """Test getting reviews with existing data"""
        if not sample_review:
            pytest.skip("Could not create sample review")
        
        response = client.get('/api/reviews')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert len(data['data']['reviews']) > 0
    
    def test_get_reviews_pagination(self, client):
        """Test pagination parameters"""
        response = client.get('/api/reviews?page=1&per_page=5')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['data']['page'] == 1
        assert data['data']['per_page'] == 5
    
    def test_get_reviews_invalid_page(self, client):
        """Test with invalid page number"""
        response = client.get('/api/reviews?page=0')
        
        assert response.status_code == 400
    
    def test_get_reviews_invalid_per_page(self, client):
        """Test with invalid per_page"""
        response = client.get('/api/reviews?per_page=1000')
        
        assert response.status_code == 400
    
    def test_get_reviews_language_filter(self, client):
        """Test language filter"""
        response = client.get('/api/reviews?language=python')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True


class TestReviewByID:
    """Tests for GET /api/reviews/<id> endpoint"""
    
    def test_get_review_by_id_success(self, client, sample_review):
        """Test getting review by valid ID"""
        if not sample_review:
            pytest.skip("Could not create sample review")
        
        review_id = sample_review['id']
        response = client.get(f'/api/reviews/{review_id}')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['review']['id'] == review_id
    
    def test_get_review_by_id_not_found(self, client):
        """Test getting review with non-existent ID"""
        response = client.get('/api/reviews/99999')
        
        assert response.status_code == 404
        data = response.get_json()
        assert 'error' in data


class TestReviewDeletion:
    """Tests for DELETE /api/reviews/<id> endpoint"""
    
    def test_delete_review_success(self, client, sample_review):
        """Test successful review deletion"""
        if not sample_review:
            pytest.skip("Could not create sample review")
        
        review_id = sample_review['id']
        response = client.delete(f'/api/reviews/{review_id}')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        
        # Verify it's deleted
        get_response = client.get(f'/api/reviews/{review_id}')
        assert get_response.status_code == 404
    
    def test_delete_review_not_found(self, client):
        """Test deleting non-existent review"""
        response = client.delete('/api/reviews/99999')
        
        assert response.status_code == 404
        data = response.get_json()
        assert 'error' in data
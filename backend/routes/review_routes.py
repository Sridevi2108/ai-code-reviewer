from flask import Blueprint, request, jsonify
from services.review_service import ReviewService

review_bp = Blueprint('reviews', __name__)
review_service = ReviewService()

@review_bp.route('/api/review', methods=['POST'])
def create_review():
    """
    Create a new code review
    
    Request body:
        {
            "code": "code snippet",
            "language": "python"
        }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Request body must be JSON'}), 400
        
        code = data.get('code')
        language = data.get('language')
        
        if not code:
            return jsonify({'error': 'Code snippet is required'}), 400
        
        if not language:
            return jsonify({'error': 'Programming language is required'}), 400
        
        # Create review
        review = review_service.create_review(code, language)
        
        return jsonify({
            'success': True,
            'review': review
        }), 201
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    
    except Exception as e:
        return jsonify({'error': f'Failed to create review: {str(e)}'}), 500


@review_bp.route('/api/reviews', methods=['GET'])
def get_reviews():
    """
    Get paginated list of reviews
    
    Query parameters:
        - page: Page number (default: 1)
        - per_page: Items per page (default: 10, max: 100)
        - language: Filter by language
        - start_date: Filter by start date (ISO format)
        - end_date: Filter by end date (ISO format)
    """
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        language = request.args.get('language')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Validate pagination
        if page < 1:
            return jsonify({'error': 'Page must be >= 1'}), 400
        
        if per_page < 1 or per_page > 100:
            return jsonify({'error': 'Per page must be between 1 and 100'}), 400
        
        # Get reviews
        result = review_service.get_reviews(
            page=page,
            per_page=per_page,
            language=language,
            start_date=start_date,
            end_date=end_date
        )
        
        return jsonify({
            'success': True,
            'data': result
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'Failed to fetch reviews: {str(e)}'}), 500


@review_bp.route('/api/reviews/<int:review_id>', methods=['GET'])
def get_review(review_id):
    """
    Get a specific review by ID
    
    Path parameters:
        - review_id: Review ID
    """
    try:
        review = review_service.get_review_by_id(review_id)
        
        return jsonify({
            'success': True,
            'review': review
        }), 200
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    
    except Exception as e:
        return jsonify({'error': f'Failed to fetch review: {str(e)}'}), 500


@review_bp.route('/api/reviews/<int:review_id>', methods=['DELETE'])
def delete_review(review_id):
    """
    Delete a review by ID
    
    Path parameters:
        - review_id: Review ID
    """
    try:
        review_service.delete_review(review_id)
        
        return jsonify({
            'success': True,
            'message': f'Review {review_id} deleted successfully'
        }), 200
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    
    except Exception as e:
        return jsonify({'error': f'Failed to delete review: {str(e)}'}), 500


@review_bp.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Code Review API'
    }), 200
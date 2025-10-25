from models import CodeReview, SessionLocal
from services.llm_service import LLMService
from datetime import datetime
from sqlalchemy import desc

class ReviewService:
    """Service for managing code reviews"""
    
    SUPPORTED_LANGUAGES = ['python', 'javascript', 'java', 'c++', 'cpp', 'c', 'go', 'rust', 'typescript', 'ruby', 'php']
    MAX_CODE_LENGTH = 10000  # characters
    
    def __init__(self):
        self.llm_service = LLMService()
    
    def validate_input(self, code: str, language: str) -> tuple[bool, str]:
        """
        Validate code review input
        
        Returns:
            tuple: (is_valid, error_message)
        """
        if not code or not code.strip():
            return False, "Code snippet cannot be empty"
        
        if len(code) > self.MAX_CODE_LENGTH:
            return False, f"Code snippet too long (max {self.MAX_CODE_LENGTH} characters)"
        
        if not language or language.lower() not in self.SUPPORTED_LANGUAGES:
            return False, f"Unsupported language. Supported: {', '.join(self.SUPPORTED_LANGUAGES)}"
        
        return True, ""
    
    def create_review(self, code: str, language: str) -> dict:
        """
        Create a new code review
        
        Args:
            code: Code snippet to review
            language: Programming language
            
        Returns:
            dict: Review data
        """
        # Validate input
        is_valid, error_msg = self.validate_input(code, language)
        if not is_valid:
            raise ValueError(error_msg)
        
        # Get review from LLM
        try:
            review_data = self.llm_service.review_code(code, language)
        except Exception as e:
            raise Exception(f"Failed to generate review: {str(e)}")
        
        # Save to database
        db = SessionLocal()
        try:
            review = CodeReview(
                code_snippet=code,
                language=language.lower(),
                review_text=review_data['review_text'],
                suggestions=review_data['suggestions'],
                potential_bugs=review_data['potential_bugs'],
                quality_score=review_data['quality_score']
            )
            
            db.add(review)
            db.commit()
            db.refresh(review)
            
            result = review.to_dict()
            result['strengths'] = review_data.get('strengths', [])
            result['reasoning'] = review_data.get('reasoning', '')
            
            return result
        
        except Exception as e:
            db.rollback()
            raise Exception(f"Database error: {str(e)}")
        finally:
            db.close()
    
    def get_reviews(self, page: int = 1, per_page: int = 10, language: str = None, 
                    start_date: str = None, end_date: str = None) -> dict:
        """
        Get paginated list of reviews with optional filters
        
        Args:
            page: Page number (1-indexed)
            per_page: Items per page
            language: Filter by language
            start_date: Filter by start date (ISO format)
            end_date: Filter by end date (ISO format)
            
        Returns:
            dict: Paginated reviews
        """
        db = SessionLocal()
        try:
            query = db.query(CodeReview)
            
            # Apply filters
            if language:
                query = query.filter(CodeReview.language == language.lower())
            
            if start_date:
                try:
                    start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                    query = query.filter(CodeReview.created_at >= start_dt)
                except ValueError:
                    pass
            
            if end_date:
                try:
                    end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                    query = query.filter(CodeReview.created_at <= end_dt)
                except ValueError:
                    pass
            
            # Get total count
            total = query.count()
            
            # Apply pagination
            reviews = query.order_by(desc(CodeReview.created_at))\
                          .offset((page - 1) * per_page)\
                          .limit(per_page)\
                          .all()
            
            return {
                'reviews': [review.to_dict() for review in reviews],
                'total': total,
                'page': page,
                'per_page': per_page,
                'total_pages': (total + per_page - 1) // per_page
            }
        
        finally:
            db.close()
    
    def get_review_by_id(self, review_id: int) -> dict:
        """
        Get a specific review by ID
        
        Args:
            review_id: Review ID
            
        Returns:
            dict: Review data
        """
        db = SessionLocal()
        try:
            review = db.query(CodeReview).filter(CodeReview.id == review_id).first()
            
            if not review:
                raise ValueError(f"Review with ID {review_id} not found")
            
            return review.to_dict()
        
        finally:
            db.close()
    
    def delete_review(self, review_id: int) -> bool:
        """
        Delete a review by ID
        
        Args:
            review_id: Review ID
            
        Returns:
            bool: True if deleted
        """
        db = SessionLocal()
        try:
            review = db.query(CodeReview).filter(CodeReview.id == review_id).first()
            
            if not review:
                raise ValueError(f"Review with ID {review_id} not found")
            
            db.delete(review)
            db.commit()
            return True
        
        except Exception as e:
            db.rollback()
            raise Exception(f"Failed to delete review: {str(e)}")
        finally:
            db.close()
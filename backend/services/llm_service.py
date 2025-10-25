import os
import requests
import json
import time
from dotenv import load_dotenv

load_dotenv()

class LLMService:
    """Service for interacting with LLM API"""
    
    def __init__(self):
        self.api_key = os.getenv('LLM_API_KEY')
        self.base_url = os.getenv('LLM_BASE_URL')
        self.model = os.getenv('LLM_MODEL', 'gpt-4o-mini')
        self.test_mode = os.getenv('TEST_MODE', 'false').lower() == 'true'
        
        if not self.api_key or not self.base_url:
            raise ValueError("LLM_API_KEY and LLM_BASE_URL must be set in environment variables")
        
        if self.test_mode:
            print("⚠️  WARNING: Running in TEST MODE - using mock reviews")
    
    def create_review_prompt(self, code: str, language: str) -> str:
        """Create a structured prompt for code review"""
        prompt = f"""You are an expert code reviewer. Analyze the following {language} code and provide a comprehensive review.

Code to review:
```{language}
{code}
```

Please provide your review in the following JSON format:
{{
    "quality_score": <number between 1-10>,
    "summary": "<brief summary of the code>",
    "potential_bugs": [
        "<bug 1>",
        "<bug 2>"
    ],
    "suggestions": [
        "<suggestion 1>",
        "<suggestion 2>"
    ],
    "strengths": [
        "<strength 1>",
        "<strength 2>"
    ],
    "reasoning": "<explanation of the quality score>"
}}

Focus on:
1. Code quality and best practices
2. Potential bugs or errors
3. Performance issues
4. Security concerns
5. Readability and maintainability

Be specific and actionable in your feedback."""
        return prompt
    
    def review_code(self, code: str, language: str, max_retries: int = 3) -> dict:
        """
        Send code to LLM for review with retry logic
        
        Args:
            code: The code snippet to review
            language: Programming language of the code
            max_retries: Maximum number of retry attempts
            
        Returns:
            dict: Parsed review response
        """
        # Return mock review in test mode
        if self.test_mode:
            return self._create_mock_review(code, language)
        
        prompt = self.create_review_prompt(code, language)
        
        # Try different header formats for LiteLLM proxy
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}',
            'api-key': self.api_key,  # Some proxies use this
        }
        
        payload = {
            'model': self.model,
            'messages': [
                {
                    'role': 'user',
                    'content': prompt
                }
            ],
            'temperature': 0.3,
            'max_tokens': 1500
        }
        
        last_error = None
        
        for attempt in range(max_retries):
            try:
                print(f"Sending request to LLM API (attempt {attempt + 1}/{max_retries})...")
                
                response = requests.post(
                    f'{self.base_url}/chat/completions',
                    headers=headers,
                    json=payload,
                    timeout=30
                )
                
                print(f"Response status: {response.status_code}")
                print(f"Response text: {response.text[:200]}...")  # Print first 200 chars
                
                if response.status_code == 200:
                    result = response.json()
                    content = result['choices'][0]['message']['content']
                    
                    # Try to parse JSON from the response
                    try:
                        # Extract JSON if it's wrapped in code blocks
                        if '```json' in content:
                            json_start = content.find('```json') + 7
                            json_end = content.find('```', json_start)
                            content = content[json_start:json_end].strip()
                        elif '```' in content:
                            json_start = content.find('```') + 3
                            json_end = content.find('```', json_start)
                            content = content[json_start:json_end].strip()
                        
                        parsed_review = json.loads(content)
                        return self._format_review(parsed_review)
                    except json.JSONDecodeError:
                        # If JSON parsing fails, create structured response from text
                        return self._create_fallback_review(content, language)
                
                elif response.status_code == 429:
                    # Rate limit - wait and retry
                    wait_time = 2 ** attempt
                    time.sleep(wait_time)
                    last_error = f"Rate limit exceeded (attempt {attempt + 1}/{max_retries})"
                    continue
                
                else:
                    last_error = f"API error: {response.status_code} - {response.text}"
                    if attempt < max_retries - 1:
                        time.sleep(1)
                        continue
            
            except requests.Timeout:
                last_error = f"Request timeout (attempt {attempt + 1}/{max_retries})"
                if attempt < max_retries - 1:
                    time.sleep(2)
                    continue
            
            except requests.RequestException as e:
                last_error = f"Request failed: {str(e)}"
                if attempt < max_retries - 1:
                    time.sleep(2)
                    continue
        
        # All retries failed
        raise Exception(f"Failed to get code review after {max_retries} attempts. Last error: {last_error}")
    
    def _format_review(self, parsed_review: dict) -> dict:
        """Format the parsed review into standard structure"""
        return {
            'quality_score': float(parsed_review.get('quality_score', 5)),
            'review_text': parsed_review.get('summary', 'Review completed'),
            'suggestions': '\n'.join(parsed_review.get('suggestions', [])),
            'potential_bugs': '\n'.join(parsed_review.get('potential_bugs', [])),
            'strengths': parsed_review.get('strengths', []),
            'reasoning': parsed_review.get('reasoning', '')
        }
    
    def _create_mock_review(self, code: str, language: str) -> dict:
        """Create a mock review for testing with basic code analysis"""
        import random
        import re
        
        # Basic code analysis
        bugs = []
        suggestions = []
        quality_score = 8.0
        
        # Check for common issues
        code_lower = code.lower()
        lines = code.split('\n')
        
        # Common typos and errors
        if 'printIn' in code or 'printin' in code_lower:
            bugs.append('Syntax error: "printIn" should be "println" (lowercase L, not capital I)')
            quality_score -= 2.0
        
        # Java/JavaScript/C++/C specific checks
        if language.lower() in ['java', 'javascript', 'c++', 'c', 'typescript']:
            for i, line in enumerate(lines, 1):
                line_stripped = line.strip()
                # Skip empty lines, comments, and lines with braces only
                if not line_stripped or line_stripped.startswith('//') or line_stripped.startswith('/*'):
                    continue
                if line_stripped in ['{', '}', '};']:
                    continue
                
                # Check for missing semicolons
                if line_stripped and not line_stripped.endswith((';', '{', '}', ':')):
                    # Check if it's a statement that needs semicolon
                    if any(keyword in line_stripped for keyword in ['System.out', 'console.', 'printf', 'cout', 'return', 'int ', 'String ', 'var ', 'let ', 'const ']):
                        if 'class ' not in line_stripped and 'function' not in line_stripped and 'if ' not in line_stripped and 'for ' not in line_stripped and 'while ' not in line_stripped:
                            bugs.append(f'Missing semicolon at line {i}: "{line_stripped}"')
                            quality_score -= 1.5
                            break  # Only report first one to avoid spam
        
        if 'system.out.print' in code_lower and 'println' not in code_lower and 'printf' not in code_lower:
            suggestions.append('Consider using println() instead of print() for better output formatting')
        
        # Check for missing error handling
        if 'try' not in code_lower and 'catch' not in code_lower and language.lower() in ['java', 'python', 'javascript']:
            suggestions.append('Consider adding error handling (try-catch blocks)')
        
        # Check for missing comments
        if '//' not in code and '#' not in code and '/*' not in code:
            suggestions.append('Add comments to explain the code logic')
            quality_score -= 0.5
        
        # Check for very short variable names
        if ' i ' in code or ' j ' in code or ' k ' in code:
            suggestions.append('Consider using more descriptive variable names instead of single letters')
        
        # Language-specific checks
        if language.lower() == 'python':
            if 'def ' in code and '"""' not in code and "'''" not in code:
                suggestions.append('Add docstrings to your functions')
        
        if language.lower() == 'java':
            if 'public class' in code and '/**' not in code:
                suggestions.append('Add JavaDoc comments to your classes and methods')
            # Check for missing braces
            open_braces = code.count('{')
            close_braces = code.count('}')
            if open_braces != close_braces:
                bugs.append(f'Mismatched braces: {open_braces} opening vs {close_braces} closing')
                quality_score -= 2.0
        
        # Determine overall quality
        if len(bugs) > 0:
            quality_score = max(3.0, quality_score)
            review_summary = f'[TEST MODE] The {language} code has {len(bugs)} syntax error(s) that need to be fixed.'
        elif len(code.strip()) < 50:
            quality_score = max(5.0, quality_score)
            review_summary = f'[TEST MODE] The {language} code is very simple but functional.'
        else:
            quality_score = min(9.0, quality_score + random.uniform(0, 1.0))
            review_summary = f'[TEST MODE] The {language} code appears well-structured and functional.'
        
        # Format results
        bugs_text = '\n'.join(bugs) if bugs else 'No critical bugs identified in test mode'
        suggestions_text = '\n'.join(suggestions[:3]) if suggestions else 'Code looks good overall'
        
        strengths = []
        if 'class' in code_lower:
            strengths.append('Uses object-oriented structure')
        if len(code.split('\n')) > 5:
            strengths.append('Well-organized multi-line code')
        if not bugs:
            strengths.append('No syntax errors detected')
        
        return {
            'quality_score': round(quality_score, 1),
            'review_text': review_summary,
            'suggestions': suggestions_text,
            'potential_bugs': bugs_text,
            'strengths': strengths,
            'reasoning': f'Score based on: code structure ({len(bugs)} errors found), error detection, and best practices. Note: This is a simplified test mode review.'
        }
    
    def _create_fallback_review(self, content: str, language: str) -> dict:
        """Create a structured review when JSON parsing fails"""
        # Try to extract a quality score from the text
        quality_score = 5.0
        lines = content.lower().split('\n')
        for line in lines:
            if 'score' in line or 'rating' in line:
                # Try to find a number
                words = line.split()
                for word in words:
                    try:
                        score = float(word.strip('.,;:'))
                        if 1 <= score <= 10:
                            quality_score = score
                            break
                    except ValueError:
                        continue
        
        return {
            'quality_score': quality_score,
            'review_text': content[:500] if len(content) > 500 else content,
            'suggestions': 'See review text for suggestions',
            'potential_bugs': 'See review text for potential issues',
            'strengths': [],
            'reasoning': content
        }
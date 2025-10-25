# AI Code Reviewer 🤖

A web application that provides AI-powered code reviews using LLM technology. Submit your code snippets and get instant feedback on code quality, potential bugs, and suggestions for improvement.

## 🌟 Features

- **AI-Powered Code Analysis**: Get intelligent code reviews from advanced LLM models
- **Multiple Language Support**: Python, JavaScript, Java, and C++
- **Code Quality Scoring**: Receive a quality score from 1-10 with detailed explanations
- **Review History**: View and manage all your past code reviews
- **Filtering & Pagination**: Filter reviews by language and date
- **Rate Limiting**: Protected API with 10 requests per minute limit
- **Responsive Design**: Mobile-friendly interface

## 🚀 Live Demo

- **Live Application**: https://ai-code-reviewer-e1le.onrender.com/
- **GitHub Repository**: https://github.com/Sridevi2108/ai-code-reviewer

⚠️ **Note**: The application is hosted on Render's free tier, which may spin down after 15 minutes of inactivity. The first request after inactivity may take 30-60 seconds to respond.

## 🎥 Demo Video
https://drive.google.com/file/d/1PICCDL4qnyjKxM4ZAyDK2QAsiU-gqJm3/view?usp=sharing

## 🛠️ Tech Stack

### Backend
- **Framework**: Flask 3.0.0
- **Database**: SQLite with SQLAlchemy
- **LLM Integration**: Groq API (alternative LLM provider)
- **Rate Limiting**: Flask-Limiter
- **Testing**: Pytest

### Frontend
- **HTML5/CSS3/Vanilla JavaScript**
- **Responsive Design**
- **Fetch API for async requests**

## 📋 Prerequisites

- Python 3.8 or higher
- Git
- A Groq API key (or any OpenAI-compatible API)

## 🔧 Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/Sridevi2108/ai-code-reviewer.git
cd ai-code-reviewer
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Configuration

Create a `.env` file in the `backend` directory:

```bash
# Copy from example
cp .env.example .env
```

Edit `.env` and add your credentials:

```env
LLM_API_KEY=your_groq_api_key_here
LLM_BASE_URL=https://api.groq.com/openai/v1
LLM_MODEL=llama-3.1-70b-versatile
DATABASE_URL=sqlite:///reviews.db
FLASK_ENV=development
```

**Get a Free Groq API Key:**
1. Visit https://console.groq.com/
2. Sign up for a free account
3. Generate an API key
4. Copy it to your `.env` file

### 4. Initialize Database

```bash
python -c "from models import init_db; init_db()"
```

### 5. Run the Application

```bash
# Start backend server
python app.py
```

The backend will run on `http://localhost:5000`

### 6. Frontend Setup

Open `frontend/index.html` in your browser, or use a local server:

```bash
cd ../frontend

# Using Python's built-in HTTP server
python -m http.server 8000

# Or using Node.js http-server (if installed)
npx http-server -p 8000
```

Visit `http://localhost:8000` in your browser.

## 📡 API Documentation

### Base URL
```
Local: http://localhost:5000/api
Production: https://ai-code-reviewer-e1le.onrender.com/api
```

### Endpoints

#### 1. Submit Code for Review
```http
POST /api/review
Content-Type: application/json

{
  "code": "def hello():\n    print('Hello World')",
  "language": "python"
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "code_snippet": "def hello():\n    print('Hello World')",
  "language": "python",
  "quality_score": 7.5,
  "review_text": "The code is functional but could be improved...",
  "suggestions": [
    "Add a docstring to explain the function's purpose",
    "Consider adding type hints",
    "Add error handling if needed"
  ],
  "potential_bugs": [],
  "created_at": "2025-10-25T10:30:00"
}
```

**Validation Rules:**
- `code`: Required, 10-5000 characters
- `language`: Required, must be one of: `python`, `javascript`, `java`, `cpp`

#### 2. Get All Reviews
```http
GET /api/reviews?page=1&per_page=10&language=python&date=2025-10-01
```

**Query Parameters:**
- `page` (optional): Page number, default: 1
- `per_page` (optional): Items per page, default: 10, max: 50
- `language` (optional): Filter by language (`python`, `javascript`, `java`, `cpp`)
- `date` (optional): Filter by date (YYYY-MM-DD format)

**Response (200 OK):**
```json
{
  "reviews": [
    {
      "id": 1,
      "code_snippet": "def hello()...",
      "language": "python",
      "quality_score": 7.5,
      "created_at": "2025-10-25T10:30:00"
    }
  ],
  "total": 25,
  "page": 1,
  "per_page": 10,
  "total_pages": 3
}
```

#### 3. Get Specific Review
```http
GET /api/reviews/{id}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "code_snippet": "def hello():\n    print('Hello World')",
  "language": "python",
  "quality_score": 7.5,
  "review_text": "...",
  "suggestions": [...],
  "potential_bugs": [...],
  "created_at": "2025-10-25T10:30:00"
}
```

**Response (404 Not Found):**
```json
{
  "error": "Review not found"
}
```

#### 4. Delete Review
```http
DELETE /api/reviews/{id}
```

**Response (200 OK):**
```json
{
  "message": "Review deleted successfully"
}
```

**Response (404 Not Found):**
```json
{
  "error": "Review not found"
}
```

### Error Responses

All endpoints may return these error codes:

**400 Bad Request:**
```json
{
  "error": "Code is required"
}
```

**429 Too Many Requests:**
```json
{
  "error": "Rate limit exceeded. Please try again later."
}
```

**500 Internal Server Error:**
```json
{
  "error": "Failed to process review: [error details]"
}
```

## 🧪 Running Tests

```bash
cd backend

# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_routes.py -v
```

**Test Coverage:**
- ✅ POST /api/review endpoint
- ✅ GET /api/reviews endpoint
- ✅ Input validation
- ✅ Error handling

## 📁 Project Structure

```
ai-code-reviewer/
├── backend/
│   ├── app.py                 # Flask application entry point
│   ├── models.py              # Database models (SQLAlchemy)
│   ├── requirements.txt       # Python dependencies
│   ├── .env.example           # Environment variables template
│   ├── .env                   # Actual environment variables (not in git)
│   ├── reviews.db             # SQLite database (created automatically)
│   ├── services/
│   │   ├── __init__.py
│   │   ├── llm_service.py     # LLM API integration & retry logic
│   │   └── review_service.py  # Review business logic
│   ├── routes/
│   │   ├── __init__.py
│   │   └── review_routes.py   # API endpoints & validation
│   └── tests/
│       ├── __init__.py
│       └── test_routes.py     # Unit tests
├── frontend/
│   ├── index.html             # Main HTML page
│   ├── style.css              # Styles
│   └── script.js              # Frontend logic & API calls
├── .gitignore                 # Git ignore file
└── README.md                  # This file
```

## 🔒 Security Features

- ✅ API key stored in environment variables (never committed)
- ✅ Rate limiting (10 requests/minute per IP)
- ✅ Input validation and sanitization
- ✅ Error handling for all endpoints
- ✅ CORS configuration for secure cross-origin requests
- ✅ SQL injection protection (SQLAlchemy ORM)
- ✅ Character limits to prevent abuse


## 🚀 Deployment on Render

### Prerequisites
1. GitHub account with your code pushed
2. Render account (free tier available)
3. Groq API key

### Deployment Steps

1. **Push to GitHub:**
```bash
git add .
git commit -m "Ready for deployment"
git push origin main
```

2. **Create Web Service on Render:**
   - Go to https://dashboard.render.com/
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Configure as follows:

**Basic Settings:**
- **Name**: `ai-code-reviewer`
- **Region**: Oregon (US West)
- **Branch**: `main`
- **Root Directory**: `backend`
- **Runtime**: Python 3

**Build & Deploy:**
- **Build Command**: 
  ```bash
  pip install -r requirements.txt && python -c "from models import init_db; init_db()"
  ```
- **Start Command**: 
  ```bash
  gunicorn --bind 0.0.0.0:$PORT app:app
  ```

**Environment Variables:**
Add these in the "Environment" section:

| Key | Value |
|-----|-------|
| `LLM_API_KEY` | Your Groq API key |
| `LLM_BASE_URL` | `https://api.groq.com/openai/v1` |
| `LLM_MODEL` | `llama-3.1-70b-versatile` |
| `DATABASE_URL` | `sqlite:///reviews.db` |
| `FLASK_ENV` | `production` |

3. **Deploy:**
   - Click "Create Web Service"
   - Wait for build to complete (~2-3 minutes)
   - Your app will be live at: `https://your-app-name.onrender.com`

4. **Update Frontend:**
   - Edit `frontend/script.js`
   - Change `API_BASE_URL` to your Render URL:
   ```javascript
   const API_BASE_URL = 'https://ai-code-reviewer-e1le.onrender.com/api';
   ```

### Troubleshooting Deployment

**Issue: Build fails with SQLAlchemy error**
- **Solution**: Ensure `requirements.txt` has `sqlalchemy>=2.0.35`

**Issue: App doesn't start**
- **Solution**: Check environment variables are set correctly

**Issue: CORS errors**
- **Solution**: Verify CORS is configured in `app.py`:
  ```python
  CORS(app, origins=["*"])  # For production, specify your frontend domain
  ```

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

## 👨‍💻 Author

**Sridevi Raju**
- 📧 Email: sridevi21082003@gmail.com
- 🐙 GitHub: [@Sridevi2108](https://github.com/Sridevi2108)

## 🙏 Acknowledgments

- **Groq** for providing fast and free LLM API access
- **Render** for free hosting platform
- **Flask** community for excellent documentation
- **SQLAlchemy** for robust ORM
- **OpenAI** for pioneering LLM technology

## 📞 Support & Contact

**Found a bug or have a suggestion?**
1. Open an issue on [GitHub Issues](https://github.com/Sridevi2108/ai-code-reviewer/issues)
2. Email: sridevi21082003@gmail.com

**Want to contribute?**
Pull requests are welcome! Please read the contributing guidelines first.

---

⭐ **If you found this project helpful, please give it a star on GitHub!**

---

**Built with ❤️ for the Machine Learning InceptAI test**

Last Updated: October 25, 2025

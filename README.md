# Car Recommendation System

A complete car recommendation system with machine learning, FastAPI backend, and React frontend.

## Features
- ML-based car recommendations based on user preferences
- Content-based filtering with cosine similarity
- MLflow experiment tracking
- FastAPI REST API
- Beautiful React frontend

## Tech Stack
- **Backend**: Python, FastAPI, scikit-learn, MLflow
- **Frontend**: React, JavaScript, CSS
- **Database**: SQLite (MLflow tracking)
- **ML**: Content-based filtering, cosine similarity

## Project Structure


## Installation

### Backend Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the backend
python backend/run.py

```

### Frontend Setup
```bash
cd frontend
npm install
npm start
```

### Usage

1/ Open http://localhost:3000

2/ Fill in your preferences

3/ Get personalized car recommendations

4/ View MLflow experiments at http://localhost:5000

** ** 
### API Endpoints

POST /api/recommend/by-preferences - Get recommendations

GET /api/health - Health check

GET /api/features - Available features
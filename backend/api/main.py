"""
Main FastAPI application for Car Recommender System
"""

from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time
from datetime import datetime
import logging
from typing import List, Optional

from .models import (
    UserPreferenceRequest, 
    RecommendByUserIdRequest,
    RecommendationResponse, 
    CarResponse,
    HealthResponse,
    ErrorResponse
)
from .dependencies import recommender_service, RecommenderService

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Car Recommender API",
    description="API for getting car recommendations based on user preferences",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Add CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============= HELPER FUNCTIONS =============

def create_car_response(car_row, similarity_score):
    """Convert a car row to CarResponse"""
    return CarResponse(
        brand=car_row.get('brand', 'Unknown'),
        model=car_row.get('model', 'Unknown'),
        version=car_row.get('version', ''),
        price=float(car_row.get('price', 0)),
        fuel_type=car_row.get('fuel_type', 'Unknown'),
        body_type=car_row.get('body_type', 'Unknown'),
        power=car_row.get('power', 'N/A'),
        seats=int(car_row.get('seats', 5)) if car_row.get('seats') != 'N/A' else 5,
        transmission=car_row.get('transmission', 'N/A'),
        similarity_score=float(similarity_score),
        explanation=generate_explanation(car_row, similarity_score)
    )

def generate_explanation(car_row, score):
    """Generate a human-readable explanation"""
    reasons = []
    
    if score > 80:
        reasons.append("excellent match")
    elif score > 60:
        reasons.append("good match")
    
    if car_row.get('body_type'):
        reasons.append(f"{car_row['body_type']} body type")
    
    if car_row.get('fuel_type'):
        reasons.append(f"{car_row['fuel_type']} engine")
    
    if reasons:
        return f"This car is a {' and '.join(reasons)} for your preferences"
    return "This car matches your preferences"

# ============= API ENDPOINTS =============

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "message": "Car Recommender API",
        "docs": "/api/docs",
        "version": "1.0.0"
    }

@app.get("/api/health", response_model=HealthResponse, tags=["Health"])
async def health_check(service: RecommenderService = Depends(lambda: recommender_service)):
    """Health check endpoint"""
    return HealthResponse(
        status="healthy" if service.recommender else "unhealthy",
        version="1.0.0",
        timestamp=datetime.now().isoformat(),
        models_loaded=service.recommender is not None,
        cars_available=len(service.recommender.raw_cars) if service.recommender else 0
    )

@app.post("/api/recommend/by-user", 
          response_model=RecommendationResponse, 
          tags=["Recommendations"])
async def recommend_by_user_id(
    request: RecommendByUserIdRequest,
    service: RecommenderService = Depends(lambda: recommender_service)
):
    """
    Get recommendations for an existing user by their ID
    """
    start_time = time.time()
    
    try:
        # Check if recommender is loaded
        if service.recommender is None:
            raise HTTPException(status_code=503, detail="Recommender not loaded")
        
        # Check if user exists
        if request.user_id >= len(service.recommender.raw_users):
            raise HTTPException(
                status_code=404, 
                detail=f"User {request.user_id} not found"
            )
        
        # Get recommendations
        recommendations_df = service.get_recommendations_by_user_id(
            request.user_id, 
            request.top_n
        )
        
        # Convert to response model
        car_responses = []
        for _, car in recommendations_df.iterrows():
            # Make sure power is converted to string
            if 'power' in car and isinstance(car['power'], (int, float)):
                car['power'] = f"{car['power']} ch"
            car_responses.append(create_car_response(car, car['similarity_score']))
        
        # Get user preferences for response
        user = service.recommender.raw_users.iloc[request.user_id]
        
        processing_time = (time.time() - start_time) * 1000
        
        return RecommendationResponse(
            recommendations=car_responses,
            total_found=len(car_responses),
            user_preferences={
                "user_id": request.user_id,
                "budget": float(user.get('budget_max', 0)),
                "preferred_body": user.get('carrosserie_preferee', 'Unknown'),
                "preferred_energy": user.get('energie_preferee', 'Unknown')
            },
            processing_time_ms=round(processing_time, 2)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/recommend/by-preferences", 
          response_model=RecommendationResponse, 
          tags=["Recommendations"])
async def recommend_by_preferences(
    preferences: UserPreferenceRequest,
    top_n: int = Query(5, ge=1, le=20),
    service: RecommenderService = Depends(lambda: recommender_service)
):
    """
    Get recommendations based on user preferences (for new users)
    """
    start_time = time.time()
    
    try:
        # Check if recommender is loaded
        if service.recommender is None:
            raise HTTPException(status_code=503, detail="Recommender not loaded")
        
        # Convert preferences to dict
        prefs_dict = preferences.dict(exclude_none=True)
        
        # Get recommendations
        recommendations_df = service.get_recommendations_by_preferences(
            prefs_dict, 
            top_n
        )
        
        # Convert to response model
        car_responses = []
        for _, car in recommendations_df.iterrows():
            car_responses.append(create_car_response(car, car['similarity_score']))
        
        processing_time = (time.time() - start_time) * 1000
        
        return RecommendationResponse(
            recommendations=car_responses,
            total_found=len(car_responses),
            user_preferences=prefs_dict,
            processing_time_ms=round(processing_time, 2)
        )
        
    except Exception as e:
        logger.error(f"Error getting recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/cars/search", tags=["Cars"])
async def search_cars(
    query: str = Query(..., min_length=2),
    limit: int = Query(10, ge=1, le=50),
    service: RecommenderService = Depends(lambda: recommender_service)
):
    """
    Search cars by brand, model, or version
    """
    try:
        if service.recommender is None:
            raise HTTPException(status_code=503, detail="Recommender not loaded")
        
        # Search in raw cars
        cars_raw = service.recommender.raw_cars
        query_lower = query.lower()
        
        mask = (
            cars_raw['brand'].str.lower().str.contains(query_lower, na=False) |
            cars_raw['model'].str.lower().str.contains(query_lower, na=False) |
            cars_raw['version'].str.lower().str.contains(query_lower, na=False)
        )
        
        results = cars_raw[mask].head(limit)
        
        return {
            "query": query,
            "total_found": len(results),
            "results": [
                {
                    "brand": row['brand'],
                    "model": row['model'],
                    "version": row['version'],
                    "price": float(row['price']) if isinstance(row['price'], (int, float)) else 0
                }
                for _, row in results.iterrows()
            ]
        }
        
    except Exception as e:
        logger.error(f"Error searching cars: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/cars/{car_id}", tags=["Cars"])
async def get_car_details(
    car_id: int,
    service: RecommenderService = Depends(lambda: recommender_service)
):
    """
    Get detailed information about a specific car
    """
    try:
        if service.recommender is None:
            raise HTTPException(status_code=503, detail="Recommender not loaded")
        
        if car_id < 0 or car_id >= len(service.recommender.raw_cars):
            raise HTTPException(status_code=404, detail="Car not found")
        
        car_info = service.get_car_info(car_id)
        
        return {
            "id": car_id,
            **car_info
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting car details: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/features", tags=["Info"])
async def get_available_features():
    """
    Get all available features for filtering (body types, fuel types, etc.)
    """
    return {
        "body_types": ["Berline", "SUV", "Citadine", "Compacte", "Coupé", 
                       "Cabriolet", "Monospace", "Minibus", "Pick up", "Utilitaire"],
        "fuel_types": ["Essence", "Diesel", "Hybride", "Electrique"],
        "transmissions": ["Automatique", "Manuelle"],
        "importance_levels": [1, 2, 3, 4, 5]
    }

# ============= ERROR HANDLERS =============

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error="HTTP Error",
            detail=exc.detail,
            status_code=exc.status_code
        ).dict()
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal Server Error",
            detail=str(exc),
            status_code=500
        ).dict()
    )
"""
Pydantic models for request/response validation
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime

# ============= REQUEST MODELS =============

class UserPreferenceRequest(BaseModel):
    """
    User preferences for car recommendations
    """
    user_id: Optional[int] = Field(None, description="User ID if existing user")
    budget_max: float = Field(..., gt=0, description="Maximum budget in €")
    min_required_seats: int = Field(5, ge=1, le=9, description="Minimum number of seats needed")
    
    # Preferences
    prefere_electrique: bool = Field(False, description="Prefer electric vehicles")
    energie_preferee: Optional[str] = Field(None, description="Preferred energy type")
    carrosserie_preferee: Optional[str] = Field(None, description="Preferred body type")
    boite_preferee: str = Field("Automatique", description="Preferred transmission")
    
    # Importance scores (1-5)
    importance_consommation: int = Field(3, ge=1, le=5, description="Importance of fuel consumption")
    importance_performance: int = Field(3, ge=1, le=5, description="Importance of performance")
    importance_confort: int = Field(3, ge=1, le=5, description="Importance of comfort")
    importance_prix: int = Field(3, ge=1, le=5, description="Importance of price")
    
    # Usage
    needs_awd: bool = Field(False, description="Needs all-wheel drive")
    has_children: bool = Field(False, description="Has children")
    long_commute: bool = Field(False, description="Long daily commute")
    
    # Optional filters
    brands: Optional[List[str]] = Field(None, description="Preferred brands")
    
    @validator('energie_preferee')
    def validate_energie(cls, v):
        if v is not None:
            allowed = ['Essence', 'Diesel', 'Hybride', 'Electrique']
            if v not in allowed:
                raise ValueError(f'energie_preferee must be one of {allowed}')
        return v
    
    @validator('carrosserie_preferee')
    def validate_carrosserie(cls, v):
        if v is not None:
            allowed = ['Berline', 'SUV', 'Citadine', 'Compacte', 'Coupé', 
                      'Cabriolet', 'Monospace', 'Minibus', 'Pick up', 'Utilitaire']
            if v not in allowed:
                raise ValueError(f'carrosserie_preferee must be one of {allowed}')
        return v
    
    @validator('boite_preferee')
    def validate_boite(cls, v):
        allowed = ['Automatique', 'Manuelle']
        if v not in allowed:
            raise ValueError(f'boite_preferee must be one of {allowed}')
        return v

class RecommendByUserIdRequest(BaseModel):
    """
    Request recommendations by existing user ID
    """
    user_id: int = Field(..., gt=0, description="User ID")
    top_n: int = Field(5, ge=1, le=20, description="Number of recommendations")

# ============= RESPONSE MODELS =============

class CarResponse(BaseModel):
    """
    Car information for recommendations
    """
    brand: str
    model: str
    version: Optional[str] = ""
    price: float
    fuel_type: str
    body_type: str
    power: str  # Will convert to string
    seats: int
    transmission: str
    similarity_score: float
    explanation: Optional[str] = None
    
    @validator('power', pre=True)
    def convert_power_to_string(cls, v):
        """Convert power to string, handling int or float"""
        if isinstance(v, (int, float)):
            return f"{v} ch"
        return str(v) if v else "N/A"
    
    class Config:
        schema_extra = {
            "example": {
                "brand": "Toyota",
                "model": "RAV4",
                "version": "Hybrid",
                "price": 35000,
                "fuel_type": "Hybride",
                "body_type": "SUV",
                "power": "218 ch",
                "seats": 5,
                "transmission": "Automatique",
                "similarity_score": 85.5,
                "explanation": "This car matches your preferred SUV body type and hybrid energy preference"
            }
        }

class RecommendationResponse(BaseModel):
    """
    Complete recommendation response
    """
    recommendations: List[CarResponse]
    total_found: int
    user_preferences: Dict[str, Any]
    processing_time_ms: float
    
    class Config:
        schema_extra = {
            "example": {
                "recommendations": [],
                "total_found": 3,
                "user_preferences": {"budget_max": 40000},
                "processing_time_ms": 125.5
            }
        }

class HealthResponse(BaseModel):
    """
    Health check response
    """
    status: str
    version: str
    timestamp: str
    models_loaded: bool
    cars_available: int

class ErrorResponse(BaseModel):
    """
    Error response
    """
    error: str
    detail: Optional[str] = None
    status_code: int
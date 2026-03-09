"""
Dependencies for FastAPI - loads recommender and data
"""

import os
import sys
import pandas as pd
import pickle
from pathlib import Path
import logging

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from src.recommender.simplecarrecpmmender import simplecarrecpmmender

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RecommenderService:
    """
    Service that loads and provides the recommender
    """
    
    def __init__(self):
        self.recommender = None
        self.data_path = project_root / "data"
        self.mlflow_path = project_root / "mlflow"
        self.load_recommender()
    
    def load_recommender(self):
        """Load the recommender and data"""
        try:
            logger.info("📚 Loading data and recommender...")
            
            # Load data
            cars_processed = pd.read_csv(self.data_path / "cars_processed.csv")
            cars_raw = pd.read_csv(self.data_path / "cars_versions_specs.csv")
            users_processed = pd.read_csv(self.data_path / "users_processed.csv")
            users_raw = pd.read_csv(self.data_path / "users_dataset.csv")
            
            logger.info(f"   ✅ Loaded {len(cars_processed)} cars")
            logger.info(f"   ✅ Loaded {len(users_raw)} users")
            
            # Create recommender
            self.recommender = simplecarrecpmmender(
                cars_processed,
                cars_raw,
                users_processed,
                users_raw
            )
            
            # Try to load best model from MLflow if available
            self.load_best_model()
            
            logger.info("✅ Recommender ready!")
            
        except Exception as e:
            logger.error(f"❌ Failed to load recommender: {e}")
            self.recommender = None
    
    def load_best_model(self):
        """Try to load the best model from MLflow"""
        try:
            import mlflow
            
            mlflow.set_tracking_uri(f"sqlite:///{self.mlflow_path / 'experiments.db'}")
            experiments = mlflow.search_experiments()
            
            if experiments:
                # Get best run based on avg_similarity
                runs = mlflow.search_runs(experiment_ids=[experiments[0].experiment_id])
                if len(runs) > 0 and 'metrics.avg_similarity' in runs.columns:
                    best_run = runs.loc[runs['metrics.avg_similarity'].idxmax()]
                    logger.info(f"   🏆 Best model from MLflow: {best_run.get('run_name', 'Unknown')}")
        except Exception as e:
            logger.warning(f"   ⚠️ Could not load MLflow model: {e}")
    
    def get_recommendations_by_user_id(self, user_id: int, top_n: int = 5):
        """Get recommendations for existing user"""
        if self.recommender is None:
            raise RuntimeError("Recommender not loaded")
        
        recommendations = self.recommender.recommend(user_id, top_n=top_n)
        return recommendations
    
    def get_recommendations_by_preferences(self, preferences: dict, top_n: int = 5):
        """Get recommendations for new user preferences"""
        if self.recommender is None:
            raise RuntimeError("Recommender not loaded")
        
        try:
            # Use the new method if available
            if hasattr(self.recommender, 'recommend_by_preferences'):
                return self.recommender.recommend_by_preferences(preferences, top_n)
            else:
                # Fallback: use user 0 and filter
                logger.warning("recommend_by_preferences not found, using fallback")
                recommendations = self.recommender.recommend(0, top_n=top_n*5)
                
                # Apply filters
                if 'budget_max' in preferences:
                    recommendations = recommendations[
                        recommendations['price'] <= preferences['budget_max'] * 1.2
                    ]
                
                if 'carrosserie_preferee' in preferences and preferences['carrosserie_preferee']:
                    body_pref = preferences['carrosserie_preferee'].lower()
                    recommendations = recommendations[
                        recommendations['body_type'].str.lower() == body_pref
                    ]
                
                if 'energie_preferee' in preferences and preferences['energie_preferee']:
                    fuel_pref = preferences['energie_preferee'].lower()
                    recommendations = recommendations[
                        recommendations['fuel_type'].str.lower() == fuel_pref
                    ]
                
                return recommendations.head(top_n)
                
        except Exception as e:
            logger.error(f"Error in get_recommendations_by_preferences: {e}")
            import traceback
            traceback.print_exc()
            return pd.DataFrame()
    
    
    def get_car_info(self, car_index):
        """Get raw info for a car"""
        if self.recommender is None:
            raise RuntimeError("Recommender not loaded")
        
        return self.recommender._get_raw_car_info(car_index)

# Create singleton instance
recommender_service = RecommenderService()
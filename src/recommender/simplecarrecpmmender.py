

import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class simplecarrecpmmender:
    """
    Content-based car recommender for properly preprocessed data
    """
    
    def __init__(self, processed_cars_df, raw_cars_df, processed_users_df, raw_users_df):
        """
        Initialize with processed data (for calculations) and raw data (for display)
        """
        self.processed_cars = processed_cars_df.copy().reset_index(drop=True)
        self.raw_cars = raw_cars_df.copy().reset_index(drop=True)
        self.processed_users = processed_users_df.copy()
        self.raw_users = raw_users_df.copy()
        
        # Define feature columns to use for matching
        self.feature_columns = [
            # Body type (binary)
            'body_berline', 'body_suv', 'body_citadine', 'body_compacte',
            'body_coupé', 'body_cabriolet', 'body_monospace', 'body_utilitaire',
            'body_minibus', 'body_pick up',
            
            # Energy type (binary)
            'is_electric', 'is_hybrid', 'is_diesel', 'is_essence',
            
            # Transmission (binary)
            'transmission_boîte_automatique',
            'transmission_transmission_intégrale',
            
            # Numerical features (already scaled 0-1)
            'price',
            'caractéristiques_nombre_de_places',
            'motorisation_puissance_(ch.din)',
            'consommation_consommation_mixte'
        ]
        
        # Keep only features that exist in the dataframe
        self.feature_columns = [col for col in self.feature_columns 
                               if col in self.processed_cars.columns]
        
        logger.info(f"📊 Using {len(self.feature_columns)} features for matching")
        logger.info(f"Features: {self.feature_columns}")
        
    def _get_user_vector(self, user_id):
        """
        Get user preference vector from processed users data
        """
        # Find the user in processed data
        user_row = self.processed_users.iloc[user_id]
        
        user_vector = {}
        
        # Body type preference
        body_cols = [col for col in self.processed_users.columns if 'carrosserie_' in col]
        for col in body_cols:
            car_body_col = col.replace('carrosserie_', 'body_')
            if car_body_col in self.feature_columns:
                user_vector[car_body_col] = user_row[col]
        
        # Energy preference
        energy_cols = [col for col in self.processed_users.columns if 'energie_' in col]
        for col in energy_cols:
            car_energy_col = col.replace('energie_', 'is_')
            if car_energy_col in self.feature_columns:
                user_vector[car_energy_col] = user_row[col]
        
        # Transmission preference
        if 'transmission_boîte_automatique' in self.feature_columns:
            user_vector['transmission_boîte_automatique'] = user_row['boite_preferee']
        
        # AWD need
        if 'transmission_transmission_intégrale' in self.feature_columns:
            user_vector['transmission_transmission_intégrale'] = user_row['needs_awd']
        
        # Numerical preferences
        if 'price' in self.feature_columns:
            user_vector['price'] = user_row['budget_max']
        
        if 'caractéristiques_nombre_de_places' in self.feature_columns:
            user_vector['caractéristiques_nombre_de_places'] = user_row['min_required_seats']
        
        if 'motorisation_puissance_(ch.din)' in self.feature_columns:
            user_vector['motorisation_puissance_(ch.din)'] = user_row['importance_performance']
        
        if 'consommation_consommation_mixte' in self.feature_columns:
            # Invert so higher importance = want lower consumption
            user_vector['consommation_consommation_mixte'] = 1 - user_row['importance_consommation']
        
        return user_vector
    
    def _get_raw_car_info(self, car_index):
        """Get raw car information for display"""
        try:
            raw_car = self.raw_cars.iloc[car_index]
            
            # Get price (convert if string)
            price = raw_car.get('price', 0)
            if isinstance(price, str):
                price = float(price.replace(',', ''))
            
            # Get power
            power = raw_car.get('motorisation_puissance_(ch.din)', 'N/A')
            if isinstance(power, (int, float)):
                power = f"{power} ch"
            
            return {
                'brand': raw_car.get('brand', 'Unknown'),
                'model': raw_car.get('model', 'Unknown'),
                'version': raw_car.get('version', ''),
                'price': price,
                'fuel_type': raw_car.get('motorisation_energie', 'Unknown'),
                'body_type': raw_car.get('caractéristiques_carrosserie', 'Unknown'),
                'power': power,
                'seats': raw_car.get('caractéristiques_nombre_de_places', 'N/A'),
                'transmission': raw_car.get('transmission_boîte', 'N/A'),
            }
        except Exception as e:
            logger.error(f"Error getting raw car info: {e}")
            return {
                'brand': 'Unknown', 'model': 'Unknown', 'version': '', 'price': 0,
                'fuel_type': 'Unknown', 'body_type': 'Unknown', 'power': 'N/A',
                'seats': 'N/A', 'transmission': 'N/A',
            }
        

    def recommend_by_preferences(self, preferences, top_n=5):
        """
        Get recommendations directly from preferences dictionary.
        preferences should contain keys like:
            budget_max, carrosserie_preferee, energie_preferee, boite_preferee,
            importance_consommation, importance_performance, etc.
        """
        # Build user vector
        user_vector_dict = {}
        
        # Numerical features: scale using min/max from raw data
        # For price
        if 'budget_max' in preferences:
            max_price = self.raw_cars['price'].max()
            if isinstance(max_price, str):
                max_price = float(max_price.replace(',', ''))
            user_vector_dict['price'] = preferences['budget_max'] / max_price
        else:
            user_vector_dict['price'] = 0.5  # default
        
        # Seats
        if 'min_required_seats' in preferences:
            # Assuming max seats 9
            user_vector_dict['caractéristiques_nombre_de_places'] = preferences['min_required_seats'] / 9
        else:
            user_vector_dict['caractéristiques_nombre_de_places'] = 5/9
        
        # Body type
        body_pref = preferences.get('carrosserie_preferee', '')
        for body_col in self.feature_columns:
            if body_col.startswith('body_'):
                # Extract body type from column name
                body_type = body_col.replace('body_', '').replace('_', ' ').strip()
                user_vector_dict[body_col] = 1.0 if body_pref.lower() == body_type.lower() else 0.0
        
        # Energy type
        energy_pref = preferences.get('energie_preferee', '')
        energy_map = {
            'essence': 'is_essence',
            'diesel': 'is_diesel',
            'hybride': 'is_hybrid',
            'electrique': 'is_electric'
        }
        for key, col in energy_map.items():
            if col in self.feature_columns:
                user_vector_dict[col] = 1.0 if energy_pref.lower() == key else 0.0
        
        # Transmission
        trans_pref = preferences.get('boite_preferee', 'automatique')
        if 'transmission_boîte_automatique' in self.feature_columns:
            user_vector_dict['transmission_boîte_automatique'] = 1.0 if trans_pref.lower() == 'automatique' else 0.0
        
        # AWD
        needs_awd = preferences.get('needs_awd', False)
        if 'transmission_transmission_intégrale' in self.feature_columns:
            user_vector_dict['transmission_transmission_intégrale'] = 1.0 if needs_awd else 0.0
        
        # Performance importance (scale 1-5 to 0-1)
        if 'importance_performance' in preferences:
            user_vector_dict['motorisation_puissance_(ch.din)'] = preferences['importance_performance'] / 5
        else:
            user_vector_dict['motorisation_puissance_(ch.din)'] = 0.5
        
        # Consumption importance (inverted)
        if 'importance_consommation' in preferences:
            user_vector_dict['consommation_consommation_mixte'] = 1 - (preferences['importance_consommation'] / 5)
        else:
            user_vector_dict['consommation_consommation_mixte'] = 0.5
        
        # Build vector in feature order
        user_vector = []
        for col in self.feature_columns:
            user_vector.append(user_vector_dict.get(col, 0))
        user_vector = np.array(user_vector).reshape(1, -1)
        
        # Filter by budget if specified
        budget = preferences.get('budget_max', None)
        if budget:
            raw_prices = []
            for i in range(len(self.raw_cars)):
                price = self.raw_cars.iloc[i].get('price', 0)
                if isinstance(price, str):
                    price = float(price.replace(',', ''))
                raw_prices.append(price)
            budget_mask = np.array(raw_prices) <= (budget * 1.2)
            filtered_indices = np.where(budget_mask)[0].tolist()
        else:
            filtered_indices = list(range(len(self.processed_cars)))
        
        if len(filtered_indices) == 0:
            filtered_indices = list(range(len(self.processed_cars)))
        
        # Get car features for filtered cars
        car_features = self.processed_cars.iloc[filtered_indices][self.feature_columns].values
        
        # Calculate similarities
        similarities = cosine_similarity(user_vector, car_features)[0]
        
        # Get top indices
        top_indices = np.argsort(similarities)[-top_n:][::-1]
        
        # Build recommendations
        recommendations = []
        for idx in top_indices:
            car_idx = filtered_indices[idx]
            car_info = self._get_raw_car_info(car_idx)
            car_info['similarity_score'] = similarities[idx] * 100
            recommendations.append(car_info)
        
        return pd.DataFrame(recommendations)    
    
    def recommend(self, user_id, top_n=5):
        """
        Get recommendations for a user by ID
        """
        # Get user vector
        user_vector_dict = self._get_user_vector(user_id)
        
        # Convert to array in correct order
        user_vector = []
        for col in self.feature_columns:
            user_vector.append(user_vector_dict.get(col, 0))
        user_vector = np.array(user_vector).reshape(1, -1)
        
        print(f"\n🔍 User vector shape: {user_vector.shape}")
        print(f"   Sample values: {user_vector[0][:5]}...")
        
        # Filter by budget (using raw data for accurate filtering)
        raw_user = self.raw_users.iloc[user_id]
        budget = raw_user['budget_max']
        
        print(f"💰 Budget: {budget:,.0f} €")
        
        # Get raw prices for filtering
        raw_prices = []
        for i in range(len(self.raw_cars)):
            price = self.raw_cars.iloc[i].get('price', 0)
            if isinstance(price, str):
                price = float(price.replace(',', ''))
            raw_prices.append(price)
        
        # Filter cars within budget (±20% flexibility)
        budget_mask = np.array(raw_prices) <= (budget * 1.2)
        filtered_indices = np.where(budget_mask)[0].tolist()
        
        print(f"   Found {len(filtered_indices)} cars within budget")
        
        if len(filtered_indices) == 0:
            logger.warning("⚠️ No cars within budget, using all cars")
            filtered_indices = list(range(len(self.processed_cars)))
        
        # Get car features for filtered cars
        car_features = self.processed_cars.iloc[filtered_indices][self.feature_columns].values
        
        # Calculate similarities
        similarities = cosine_similarity(user_vector, car_features)[0]
        
        print(f"📊 Similarity scores: min={similarities.min():.3f}, max={similarities.max():.3f}")
        
        # Get top recommendations
        top_indices = np.argsort(similarities)[-top_n:][::-1]
        
        # Build recommendations
        recommendations = []
        for idx in top_indices:
            car_idx = filtered_indices[idx]
            car_info = self._get_raw_car_info(car_idx)
            car_info['similarity_score'] = similarities[idx] * 100  # Convert to percentage
            recommendations.append(car_info)
        
        return pd.DataFrame(recommendations)


# ============= TEST THE RECOMMENDER =============

if __name__ == "__main__":
    # Load data
    print("📚 Loading data...")
    cars_processed = pd.read_csv('../data/cars_processed.csv')
    cars_raw = pd.read_csv('../data/cars_versions_specs.csv')
    users_processed = pd.read_csv('../data/users_processed.csv')
    users_raw = pd.read_csv('../data/users_dataset.csv')

    print(f"   ✅ Processed cars: {len(cars_processed)} rows")
    print(f"   ✅ Raw cars: {len(cars_raw)} rows")
    print(f"   ✅ Processed users: {len(users_processed)} rows")
    print(f"   ✅ Raw users: {len(users_raw)} rows")

    # Create recommender
    print("\n🔧 Creating recommender...")
    rec = simplecarrecpmmender(cars_processed, cars_raw, users_processed, users_raw)

    # Test with first few users
    for user_id in range(min(3, len(users_raw))):
        print("\n" + "="*60)
        print(f"👤 USER {user_id + 1}")
        print("="*60)
        
        # Show user preferences
        raw_user = users_raw.iloc[user_id]
        print("\n📋 Preferences:")
        print(f"   Budget: {raw_user['budget_max']:,.0f} €")
        print(f"   Body type: {raw_user['carrosserie_preferee']}")
        print(f"   Energy: {raw_user['energie_preferee']}")
        print(f"   Transmission: {raw_user['boite_preferee']}")
        
        # Get recommendations
        print("\n🔍 Getting recommendations...")
        recommendations = rec.recommend(user_id, top_n=3)
        
        # Show results
        if len(recommendations) > 0:
            print("\n📊 TOP 3 RECOMMENDATIONS:")
            print("-" * 80)
            
            for idx, (_, car) in enumerate(recommendations.iterrows(), 1):
                print(f"\n{idx}. {car['brand']} {car['model']} {car['version']}".strip())
                print(f"   📊 Match: {car['similarity_score']:.1f}%")
                print(f"   💰 Price: {car['price']:,.0f} €")
                print(f"   ⛽ Fuel: {car['fuel_type']}")
                print(f"   🚗 Body: {car['body_type']}")
                print(f"   💺 Seats: {car['seats']}")
                if car['power'] != 'N/A':
                    print(f"   🔧 Power: {car['power']}")
        else:
            print("❌ No recommendations found")
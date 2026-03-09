import sys
import os
import pandas as pd
import mlflow

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from src.recommender.mlflow_tracking import MLflowTracker
from src.recommender.simplecarrecpmmender import simplecarrecpmmender

def main():
    print("="*60)
    print("🧪 TESTING MLFLOW TRACKING")
    print("="*60)
    
    # 0. Always end any active runs first
    print("\n🔄 Ending any active MLflow runs...")
    mlflow.end_run()
    
    # 1. Load data
    print("\n📚 Loading data...")
    data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    
    cars_processed = pd.read_csv(os.path.join(data_path, 'cars_processed.csv'))
    cars_raw = pd.read_csv(os.path.join(data_path, 'cars_versions_specs.csv'))
    users_processed = pd.read_csv(os.path.join(data_path, 'users_processed.csv'))
    users_raw = pd.read_csv(os.path.join(data_path, 'users_dataset.csv'))
    
    print(f"   ✅ Loaded {len(cars_processed)} cars")
    print(f"   ✅ Loaded {len(users_raw)} users")
    
    # 2. Create tracker
    print("\n🔧 Initializing MLflow tracker...")
    tracker = MLflowTracker("Car_Recommender_Tests")
    
    # 3. Show debug info
    tracker.debug_info()
    
    # 4. Create recommender
    print("\n🔧 Creating recommender...")
    recommender = simplecarrecpmmender(
        cars_processed, 
        cars_raw, 
        users_processed, 
        users_raw
    )
    
    # 5. Run different experiments - with clean runs
    experiments = [
        {
            'name': 'basic_recommender',
            'description': 'Basic recommender with default settings',
            'weights': None
        },
        {
            'name': 'weighted_recommender',
            'description': 'With feature weights for SUV and Hybrid',
            'weights': {'body_suv': 2.0, 'is_hybrid': 3.0}
        },
        {
            'name': 'family_focused',
            'description': 'Prioritizing family features',
            'weights': {'caractéristiques_nombre_de_places': 2.5, 'body_suv': 2.0}
        }
    ]
    
    results = []
    for i, exp in enumerate(experiments):
        print(f"\n{'─'*50}")
        print(f"📊 Experiment {i+1}/{len(experiments)}: {exp['name']}")
        print(f"{'─'*50}")
        
        # Make sure no active run before starting new one
        mlflow.end_run()
        
        try:
            result = tracker.log_experiment(
                run_name=exp['name'],
                recommender=recommender,
                users_raw=users_raw,
                feature_weights=exp['weights'],
                description=exp['description'],
                test_users=5
            )
            results.append(result)
            print(f"✅ {exp['name']} completed successfully")
        except Exception as e:
            print(f"❌ Error in {exp['name']}: {e}")
            # End run if there was an error
            mlflow.end_run()
            continue
    
    # 6. List all experiments
    print("\n" + "="*60)
    tracker.list_experiments()
    
    # 7. Show best run
    tracker.get_best_run()
    
    # 8. Show UI command
    tracker.view_ui_command()
    
    # 9. Final cleanup
    mlflow.end_run()
    
    print("\n" + "="*60)
    print("✅ Test complete! All data saved in mlflow/ folder")
    print("="*60)

if __name__ == "__main__":
    main()
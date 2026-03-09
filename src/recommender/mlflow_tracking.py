import mlflow
import pandas as pd
import numpy as np
import os
from datetime import datetime
import pickle
from src.recommender.simplecarrecpmmender import simplecarrecpmmender

class MLflowTracker:

    
    def __init__(self, experiment_name="Car_Recommender"):
        """
        Initialize MLflow with all data stored in mlflow/ folder
        """
        # Get project root (car-recommendation-system/)
        self.project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        
        # Create main mlflow folder
        self.mlflow_path = os.path.join(self.project_root, "mlflow")
        os.makedirs(self.mlflow_path, exist_ok=True)
        
        # Create subfolders
        self.models_path = os.path.join(self.mlflow_path, "models")
        os.makedirs(self.models_path, exist_ok=True)
        
        # Use SQLite database
        self.db_path = os.path.join(self.mlflow_path, "experiments.db")
        
        # IMPORTANT: Use file:/// for Windows paths
        db_uri = f"sqlite:///{self.db_path}"
        mlflow.set_tracking_uri(db_uri)
        
        # Set artifact location to use file:/// scheme for Windows
        artifact_uri = f"file:///{self.mlflow_path.replace(os.sep, '/')}"
        
        # Create or get experiment
        self.experiment_name = experiment_name
        try:
            # Try to get existing experiment
            experiment = mlflow.get_experiment_by_name(experiment_name)
            if experiment is None:
                self.experiment_id = mlflow.create_experiment(
                    experiment_name,
                    artifact_location=artifact_uri
                )
                print(f"✅ Created new experiment: {experiment_name}")
            else:
                self.experiment_id = experiment.experiment_id
                print(f"✅ Using existing experiment: {experiment_name}")
        except Exception as e:
            print(f"⚠️ Error with experiment: {e}")
            self.experiment_id = mlflow.create_experiment(
                experiment_name,
                artifact_location=artifact_uri
            )
        
        mlflow.set_experiment(experiment_name)
        
        print(f"📊 MLflow database: {self.db_path}")
        print(f"📊 MLflow artifact URI: {artifact_uri}")
        print(f"📊 MLflow tracking URI: {mlflow.get_tracking_uri()}")
        print("✅ All MLflow data will be stored in the mlflow/ folder")
    
    def log_experiment(self, 
                      run_name,
                      recommender,
                      users_raw,
                      feature_weights=None,
                      description="",
                      test_users=5):
        """
        Log one experiment run
        """
        with mlflow.start_run(run_name=run_name) as run:
            
            print(f"\n🚀 Logging run: {run_name}")
            print(f"   Run ID: {run.info.run_id}")
            
            # 1. Log parameters
            print("   📝 Logging parameters...")
            mlflow.log_param("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            mlflow.log_param("description", description)
            mlflow.log_param("num_features", len(recommender.feature_columns))
            mlflow.log_param("feature_list", str(recommender.feature_columns[:10]))
            
            if feature_weights:
                for name, weight in feature_weights.items():
                    mlflow.log_param(f"weight_{name}", weight)
            
            # 2. Calculate metrics
            print("   📊 Calculating metrics...")
            all_scores = []
            users_tested = 0
            
            for user_id in range(min(test_users, len(users_raw))):
                try:
                    recommendations = recommender.recommend(user_id, top_n=3)
                    if len(recommendations) > 0:
                        users_tested += 1
                        all_scores.extend(recommendations['similarity_score'].tolist())
                except Exception as e:
                    print(f"      ⚠️ User {user_id} failed: {e}")
            
            if all_scores:
                avg_score = np.mean(all_scores)
                max_score = np.max(all_scores)
                min_score = np.min(all_scores)
                std_score = np.std(all_scores)
                
                # Log metrics
                mlflow.log_metric("avg_similarity", avg_score)
                mlflow.log_metric("max_similarity", max_score)
                mlflow.log_metric("min_similarity", min_score)
                mlflow.log_metric("std_similarity", std_score)
                mlflow.log_metric("users_tested", users_tested)
                mlflow.log_metric("total_recommendations", len(all_scores))
                
                print(f"   ✅ Avg similarity: {avg_score:.2f}%")
                print(f"   ✅ Max similarity: {max_score:.2f}%")
                print(f"   ✅ Min similarity: {min_score:.2f}%")
            
            # 3. Save experiment note locally
            note_filename = f"{run_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            note_path = os.path.join(self.models_path, note_filename)
            
            with open(note_path, 'w') as f:
                f.write(f"Experiment Run: {run_name}\n")
                f.write(f"Run ID: {run.info.run_id}\n")
                f.write(f"Date: {datetime.now()}\n")
                f.write(f"Description: {description}\n")
                f.write(f"Features used: {len(recommender.feature_columns)}\n")
                f.write(f"Feature weights: {feature_weights}\n")
                f.write(f"\nResults:\n")
                if all_scores:
                    f.write(f"  - Avg similarity: {avg_score:.2f}%\n")
                    f.write(f"  - Max similarity: {max_score:.2f}%\n")
                    f.write(f"  - Min similarity: {min_score:.2f}%\n")
                    f.write(f"  - Std similarity: {std_score:.2f}%\n")
            
            # Try to log artifact
            try:
                mlflow.log_artifact(note_path)
                print(f"   ✅ Artifact logged: {note_filename}")
            except Exception as e:
                print(f"   ⚠️ Could not log artifact: {e}")
                print(f"   ✅ Note saved locally at: {note_path}")
            
            # 4. Save a copy of the recommender
            model_filename = f"{run_name}_model.pkl"
            model_path = os.path.join(self.models_path, model_filename)
            with open(model_path, 'wb') as f:
                pickle.dump(recommender, f)
            
            try:
                mlflow.log_artifact(model_path)
                print(f"   ✅ Model artifact logged: {model_filename}")
            except Exception as e:
                print(f"   ⚠️ Could not log model artifact: {e}")
                print(f"   ✅ Model saved locally at: {model_path}")
            
            return {
                'avg_similarity': avg_score if all_scores else 0,
                'max_similarity': max_score if all_scores else 0,
                'min_similarity': min_score if all_scores else 0,
                'run_id': run.info.run_id,
                'run_name': run_name
            }
    
    def list_experiments(self):
        """
        List all experiments and runs - FIXED VERSION
        """
        print("\n📋 Experiments in database:")
        experiments = mlflow.search_experiments()
        
        for exp in experiments:
            print(f"\n  📁 {exp.name} (ID: {exp.experiment_id})")
            print(f"     Location: {exp.artifact_location}")
            
            # Get runs for this experiment
            runs = mlflow.search_runs(experiment_ids=[exp.experiment_id])
            if len(runs) > 0:
                print(f"     Runs: {len(runs)}")
                
                # Check what columns are available
                print(f"     Available columns: {runs.columns.tolist()}")
                
                for idx, run in runs.iterrows():
                    # Get run name - try different possible column names
                    run_name = "Unknown"
                    if 'tags.mlflow.runName' in run:
                        run_name = run['tags.mlflow.runName']
                    elif 'run_name' in run:
                        run_name = run['run_name']
                    elif 'name' in run:
                        run_name = run['name']
                    
                    # Get similarity score
                    score = run.get('metrics.avg_similarity', 'N/A')
                    if score != 'N/A' and pd.notna(score):
                        print(f"       - {run_name}: {score:.2f}%")
                    else:
                        print(f"       - {run_name}: No score")
            else:
                print(f"     No runs yet")
    
    def view_ui_command(self):
        """
        Print the command to start MLflow UI
        """
        print("\n" + "="*60)
        print("📊 To view experiments in MLflow UI:")
        print("="*60)
        print(f"\n1. Open a NEW terminal")
        print(f"2. Navigate to your project:")
        print(f"   cd {self.project_root}")
        print(f"\n3. Run MLflow UI:")
        print(f"   mlflow ui --backend-store-uri sqlite:///mlflow/experiments.db")
        print(f"\n4. Open browser: http://127.0.0.1:5000")
        print("\n   If that doesn't work, try:")
        print(f"   mlflow ui --backend-store-uri sqlite:///{self.db_path}")

    def get_best_run(self, metric='avg_similarity'):
        """
        Get the best run based on a metric
        """
        runs = mlflow.search_runs(experiment_ids=[self.experiment_id])
        if len(runs) > 0 and metric in runs.columns:
            best_run = runs.loc[runs[metric].idxmax()]
            
            # Get run name
            run_name = "Unknown"
            if 'tags.mlflow.runName' in best_run:
                run_name = best_run['tags.mlflow.runName']
            elif 'run_name' in best_run:
                run_name = best_run['run_name']
            
            print(f"\n🏆 Best run: {run_name}")
            print(f"   {metric}: {best_run[metric]:.2f}%")
            return best_run
        else:
            print(f"\n⚠️ No runs found or metric '{metric}' not available")
            return None

    def debug_info(self):
        """
        Print debug information about MLflow setup
        """
        print("\n🔍 MLflow Debug Info:")
        print(f"   Tracking URI: {mlflow.get_tracking_uri()}")
        print(f"   Artifact URI: {mlflow.get_artifact_uri()}")
        
        # List all experiments
        experiments = mlflow.search_experiments()
        print(f"\n   Experiments found: {len(experiments)}")
        
        for exp in experiments:
            print(f"   - {exp.name}: {exp.experiment_id}")
            
            # Get runs for this experiment
            runs = mlflow.search_runs(experiment_ids=[exp.experiment_id])
            if len(runs) > 0:
                print(f"     Runs: {len(runs)}")
                print(f"     Columns: {runs.columns.tolist()}")
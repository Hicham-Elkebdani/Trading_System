"""
Script 2: Entraînement du modèle de Machine Learning
Usage: python scripts/02_train_model.py
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import logging
from datetime import datetime
from config.config import LOGS_DIR, PRIMARY_TIMEFRAME, MODELS_DIR
from data.data_manager import DataManager
from features.feature_engineering import FeatureEngineer
from models.xgboost_model import XGBoostModel

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOGS_DIR / 'model_training.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def main():
    """Fonction principale d'entraînement"""
    
    logger.info("="*60)
    logger.info("DÉMARRAGE DE L'ENTRAÎNEMENT DU MODÈLE")
    logger.info("="*60)
    
    try:
        # 1. Charger les données
        logger.info("Chargement des données...")
        data_manager = DataManager()
        
        df = data_manager.load_latest_raw_data(
            timeframe=PRIMARY_TIMEFRAME,
            suffix="historical"
        )
        
        if df is None:
            logger.error("Aucune donnée disponible. Exécutez d'abord 01_collect_data.py")
            return False
        
        logger.info(f"Données chargées: {len(df)} lignes")
        
        # 2. Créer les features
        logger.info("Création des features...")
        feature_engineer = FeatureEngineer()
        
        df_features = feature_engineer.create_all_features(df)
        logger.info(f"Features créées: {len(df_features.columns)} colonnes")
        
        # 3. Créer les labels
        logger.info("Création des labels...")
        df_labeled = feature_engineer.create_labels(
            df_features,
            method="future_return",
            threshold=0.0005  # 0.05% de mouvement
        )
        
        # 4. Sauvegarder les données avec features
        logger.info("Sauvegarde des données avec features...")
        data_manager.save_processed_data(
            df_labeled,
            PRIMARY_TIMEFRAME,
            stage="features_and_labels"
        )
        
        # 5. Préparer les données pour l'entraînement
        logger.info("Préparation des données pour l'entraînement...")
        model = XGBoostModel()
        
        feature_columns = feature_engineer.get_feature_names(df_labeled)
        logger.info(f"Nombre de features: {len(feature_columns)}")
        
        X_train, X_test, y_train, y_test = model.prepare_data(
            df_labeled,
            feature_columns,
            test_size=0.2
        )
        
        # 6. Entraîner le modèle
        logger.info("Entraînement du modèle XGBoost...")
        logger.info(f"Train set: {X_train.shape[0]} échantillons")
        logger.info(f"Test set: {X_test.shape[0]} échantillons")
        
        model.train(X_train, y_train)
        
        # 7. Évaluer le modèle
        logger.info("Évaluation du modèle...")
        metrics = model.evaluate(X_test, y_test)
        
        # 8. Sauvegarder le modèle
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        model_name = f"xgboost_model_{PRIMARY_TIMEFRAME}_{timestamp}"
        
        logger.info(f"Sauvegarde du modèle: {model_name}")
        model.save(model_name)
        
        # Sauvegarder aussi en tant que "latest"
        model.save(f"xgboost_model_{PRIMARY_TIMEFRAME}_latest")
        
        logger.info("="*60)
        logger.info("ENTRAÎNEMENT TERMINÉ AVEC SUCCÈS")
        logger.info("="*60)
        logger.info(f"\nModèle sauvegardé dans: {MODELS_DIR}")
        logger.info(f"Accuracy: {metrics['accuracy']:.4f}")
        logger.info(f"Precision: {metrics['precision']:.4f}")
        logger.info(f"Recall: {metrics['recall']:.4f}")
        logger.info(f"F1-Score: {metrics['f1_score']:.4f}")
        
        return True
        
    except Exception as e:
        logger.error(f"Erreur lors de l'entraînement: {e}", exc_info=True)
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

"""
Module pour le modèle XGBoost
"""
import xgboost as xgb
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import joblib
from pathlib import Path
import logging
from typing import Optional, Tuple
import json

from config.config import XGBOOST_CONFIG, MODELS_DIR, TRAIN_TEST_SPLIT, LABELS

logger = logging.getLogger(__name__)


class XGBoostModel:
    """Modèle XGBoost pour la prédiction de trading"""
    
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.feature_names = None
        self.config = XGBOOST_CONFIG
        self.is_trained = False
        
    def prepare_data(
        self,
        df: pd.DataFrame,
        feature_columns: list,
        test_size: float = None
    ) -> Tuple:
        """
        Préparer les données pour l'entraînement
        
        Args:
            df: DataFrame avec features et labels
            feature_columns: Liste des colonnes de features
            test_size: Proportion du test set
            
        Returns:
            Tuple (X_train, X_test, y_train, y_test)
        """
        if test_size is None:
            test_size = 1 - TRAIN_TEST_SPLIT
        
        # Extraire features et labels
        X = df[feature_columns].copy()
        y = df['label'].copy()
        
        # Sauvegarder les noms de features
        self.feature_names = feature_columns
        
        # Gérer les valeurs infinies ou NaN
        X = X.replace([np.inf, -np.inf], np.nan)
        X = X.fillna(X.mean())
        
        # Split temporel (pas de shuffle pour respecter la chronologie)
        split_idx = int(len(X) * (1 - test_size))
        X_train, X_test = X[:split_idx], X[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]
        
        # Normalisation
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        logger.info(f"Données préparées:")
        logger.info(f"Train: {X_train_scaled.shape}, Test: {X_test_scaled.shape}")
        logger.info(f"Distribution train: {np.bincount(y_train)}")
        logger.info(f"Distribution test: {np.bincount(y_test)}")
        
        return X_train_scaled, X_test_scaled, y_train.values, y_test.values
    
    def train(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_val: Optional[np.ndarray] = None,
        y_val: Optional[np.ndarray] = None,
        early_stopping_rounds: int = 50
    ):
        """
        Entraîner le modèle XGBoost
        
        Args:
            X_train: Features d'entraînement
            y_train: Labels d'entraînement
            X_val: Features de validation (optionnel)
            y_val: Labels de validation (optionnel)
            early_stopping_rounds: Nombre de rounds pour early stopping
        """
        logger.info("Démarrage de l'entraînement XGBoost...")
        
        # Créer le modèle
        self.model = xgb.XGBClassifier(**self.config)
        
        # Préparer les données de validation si fournies
        eval_set = None
        if X_val is not None and y_val is not None:
            eval_set = [(X_train, y_train), (X_val, y_val)]
        
        # Entraîner
        self.model.fit(
            X_train,
            y_train,
            eval_set=eval_set,
            verbose=True
        )
        
        self.is_trained = True
        logger.info("Entraînement terminé!")
        
        # Afficher l'importance des features
        self._log_feature_importance()
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Prédire les labels
        
        Args:
            X: Features
            
        Returns:
            Array des prédictions (0: HOLD, 1: BUY, 2: SELL)
        """
        if not self.is_trained or self.model is None:
            raise ValueError("Le modèle n'est pas entraîné")
        
        return self.model.predict(X)
    
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """
        Prédire les probabilités pour chaque classe
        
        Args:
            X: Features
            
        Returns:
            Array des probabilités (shape: n_samples x n_classes)
        """
        if not self.is_trained or self.model is None:
            raise ValueError("Le modèle n'est pas entraîné")
        
        return self.model.predict_proba(X)
    
    def evaluate(self, X_test: np.ndarray, y_test: np.ndarray) -> dict:
        """
        Évaluer le modèle sur le test set
        
        Args:
            X_test: Features de test
            y_test: Labels de test
            
        Returns:
            Dictionnaire avec les métriques
        """
        from sklearn.metrics import (
            accuracy_score, precision_score, recall_score,
            f1_score, confusion_matrix, classification_report
        )
        
        # Prédictions
        y_pred = self.predict(X_test)
        y_proba = self.predict_proba(X_test)
        
        # Métriques
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, average='weighted', zero_division=0)
        recall = recall_score(y_test, y_pred, average='weighted', zero_division=0)
        f1 = f1_score(y_test, y_pred, average='weighted', zero_division=0)
        
        # Matrice de confusion
        cm = confusion_matrix(y_test, y_pred)
        
        # Rapport de classification
        report = classification_report(
            y_test, y_pred,
            target_names=[LABELS[i] for i in sorted(LABELS.keys())],
            zero_division=0
        )
        
        metrics = {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1_score': f1,
            'confusion_matrix': cm.tolist(),
            'classification_report': report
        }
        
        logger.info(f"\n{'='*50}")
        logger.info("RÉSULTATS DE L'ÉVALUATION")
        logger.info(f"{'='*50}")
        logger.info(f"Accuracy: {accuracy:.4f}")
        logger.info(f"Precision: {precision:.4f}")
        logger.info(f"Recall: {recall:.4f}")
        logger.info(f"F1-Score: {f1:.4f}")
        logger.info(f"\nMatrice de confusion:\n{cm}")
        logger.info(f"\nRapport de classification:\n{report}")
        
        return metrics
    
    def _log_feature_importance(self, top_n: int = 20):
        """Afficher l'importance des features"""
        if self.model is None or self.feature_names is None:
            return
        
        importance = self.model.feature_importances_
        feature_importance = pd.DataFrame({
            'feature': self.feature_names,
            'importance': importance
        }).sort_values('importance', ascending=False)
        
        logger.info(f"\nTop {top_n} features les plus importantes:")
        logger.info(f"\n{feature_importance.head(top_n).to_string(index=False)}")
    
    def save(self, filename: str = "xgboost_model"):
        """
        Sauvegarder le modèle
        
        Args:
            filename: Nom du fichier (sans extension)
        """
        if not self.is_trained:
            raise ValueError("Le modèle n'est pas entraîné")
        
        model_path = MODELS_DIR / f"{filename}.json"
        scaler_path = MODELS_DIR / f"{filename}_scaler.pkl"
        metadata_path = MODELS_DIR / f"{filename}_metadata.json"
        
        # Sauvegarder le modèle XGBoost
        self.model.save_model(str(model_path))
        
        # Sauvegarder le scaler
        joblib.dump(self.scaler, scaler_path)
        
        # Sauvegarder les métadonnées
        metadata = {
            'feature_names': self.feature_names,
            'config': self.config,
            'n_features': len(self.feature_names) if self.feature_names else 0
        }
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=4)
        
        logger.info(f"Modèle sauvegardé: {model_path}")
    
    def load(self, filename: str = "xgboost_model"):
        """
        Charger un modèle sauvegardé
        
        Args:
            filename: Nom du fichier (sans extension)
        """
        model_path = MODELS_DIR / f"{filename}.json"
        scaler_path = MODELS_DIR / f"{filename}_scaler.pkl"
        metadata_path = MODELS_DIR / f"{filename}_metadata.json"
        
        if not model_path.exists():
            raise FileNotFoundError(f"Modèle non trouvé: {model_path}")
        
        # Charger le modèle XGBoost
        self.model = xgb.XGBClassifier()
        self.model.load_model(str(model_path))
        
        # Charger le scaler
        self.scaler = joblib.load(scaler_path)
        
        # Charger les métadonnées
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        
        self.feature_names = metadata['feature_names']
        self.config = metadata['config']
        self.is_trained = True
        
        logger.info(f"Modèle chargé: {model_path}")
        logger.info(f"Nombre de features: {metadata['n_features']}")
    
    def predict_single(self, features: dict) -> Tuple[int, np.ndarray]:
        """
        Prédire pour un seul échantillon
        
        Args:
            features: Dictionnaire {feature_name: value}
            
        Returns:
            Tuple (label, probabilités)
        """
        if not self.is_trained:
            raise ValueError("Le modèle n'est pas entraîné")
        
        # Créer un DataFrame avec les features
        df = pd.DataFrame([features])
        
        # S'assurer que toutes les features sont présentes
        for feature in self.feature_names:
            if feature not in df.columns:
                df[feature] = 0
        
        # Réorganiser les colonnes dans le bon ordre
        df = df[self.feature_names]
        
        # Normaliser
        X = self.scaler.transform(df)
        
        # Prédire
        label = self.predict(X)[0]
        proba = self.predict_proba(X)[0]
        
        return label, proba


# Exemple d'utilisation
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Créer des données synthétiques pour le test
    np.random.seed(42)
    n_samples = 10000
    n_features = 50
    
    X = np.random.randn(n_samples, n_features)
    y = np.random.randint(0, 3, n_samples)
    
    # Créer le modèle
    model = XGBoostModel()
    
    # Split des données
    split_idx = int(n_samples * 0.8)
    X_train, X_test = X[:split_idx], X[split_idx:]
    y_train, y_test = y[:split_idx], y[split_idx:]
    
    # Feature names
    model.feature_names = [f'feature_{i}' for i in range(n_features)]
    
    # Entraîner
    model.train(X_train, y_train)
    
    # Évaluer
    metrics = model.evaluate(X_test, y_test)
    
    # Sauvegarder
    model.save("test_model")
    
    # Charger
    model2 = XGBoostModel()
    model2.load("test_model")
    
    # Prédire
    predictions = model2.predict(X_test[:5])
    print(f"\nPrédictions: {predictions}")

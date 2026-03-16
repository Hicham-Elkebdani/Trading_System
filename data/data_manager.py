"""
Module de gestion et sauvegarde des données
"""
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import logging
from typing import Optional

from config.config import RAW_DATA_DIR, PROCESSED_DATA_DIR, SYMBOL

logger = logging.getLogger(__name__)


class DataManager:
    """Gestionnaire de données pour le système de trading"""
    
    def __init__(self):
        self.raw_dir = RAW_DATA_DIR
        self.processed_dir = PROCESSED_DATA_DIR
        self.symbol = SYMBOL
        
    def save_raw_data(
        self,
        df: pd.DataFrame,
        timeframe: str,
        suffix: str = ""
    ) -> Optional[Path]:
        """
        Sauvegarder les données brutes
        
        Args:
            df: DataFrame à sauvegarder
            timeframe: Période temporelle (H1, D1, etc.)
            suffix: Suffixe optionnel pour le nom de fichier
            
        Returns:
            Path: Chemin du fichier sauvegardé
        """
        try:
            # Créer le nom de fichier
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.symbol}_{timeframe}"
            if suffix:
                filename += f"_{suffix}"
            filename += f"_{timestamp}.csv"
            
            filepath = self.raw_dir / filename
            
            # Sauvegarder
            df.to_csv(filepath, index=False)
            logger.info(f"Données brutes sauvegardées: {filepath}")
            
            return filepath
            
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde des données brutes: {e}")
            return None
    
    def save_processed_data(
        self,
        df: pd.DataFrame,
        timeframe: str,
        stage: str = "features"
    ) -> Optional[Path]:
        """
        Sauvegarder les données traitées
        
        Args:
            df: DataFrame à sauvegarder
            timeframe: Période temporelle
            stage: Étape de traitement (features, labels, etc.)
            
        Returns:
            Path: Chemin du fichier sauvegardé
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.symbol}_{timeframe}_{stage}_{timestamp}.csv"
            filepath = self.processed_dir / filename
            
            df.to_csv(filepath, index=False)
            logger.info(f"Données traitées sauvegardées: {filepath}")
            
            return filepath
            
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde des données traitées: {e}")
            return None
    
    def load_latest_raw_data(
        self,
        timeframe: str,
        suffix: str = ""
    ) -> Optional[pd.DataFrame]:
        """
        Charger les dernières données brutes
        
        Args:
            timeframe: Période temporelle
            suffix: Suffixe du fichier
            
        Returns:
            DataFrame ou None
        """
        try:
            # Rechercher les fichiers correspondants
            pattern = f"{self.symbol}_{timeframe}"
            if suffix:
                pattern += f"_{suffix}"
            pattern += "*.csv"
            
            files = list(self.raw_dir.glob(pattern))
            if not files:
                logger.warning(f"Aucun fichier trouvé pour le pattern: {pattern}")
                return None
            
            # Prendre le fichier le plus récent
            latest_file = max(files, key=lambda p: p.stat().st_mtime)
            
            df = pd.read_csv(latest_file)
            df['time'] = pd.to_datetime(df['time'])
            
            logger.info(f"Données chargées depuis: {latest_file}")
            logger.info(f"Période: {df['time'].min()} à {df['time'].max()}, {len(df)} lignes")
            
            return df
            
        except Exception as e:
            logger.error(f"Erreur lors du chargement des données: {e}")
            return None
    
    def load_latest_processed_data(
        self,
        timeframe: str,
        stage: str = "features"
    ) -> Optional[pd.DataFrame]:
        """
        Charger les dernières données traitées
        
        Args:
            timeframe: Période temporelle
            stage: Étape de traitement
            
        Returns:
            DataFrame ou None
        """
        try:
            pattern = f"{self.symbol}_{timeframe}_{stage}_*.csv"
            files = list(self.processed_dir.glob(pattern))
            
            if not files:
                logger.warning(f"Aucun fichier trouvé pour le pattern: {pattern}")
                return None
            
            latest_file = max(files, key=lambda p: p.stat().st_mtime)
            
            df = pd.read_csv(latest_file)
            if 'time' in df.columns:
                df['time'] = pd.to_datetime(df['time'])
            
            logger.info(f"Données traitées chargées depuis: {latest_file}")
            
            return df
            
        except Exception as e:
            logger.error(f"Erreur lors du chargement des données traitées: {e}")
            return None
    
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Nettoyer les données (valeurs manquantes, doublons, etc.)
        
        Args:
            df: DataFrame à nettoyer
            
        Returns:
            DataFrame nettoyé
        """
        try:
            original_len = len(df)
            
            # Supprimer les doublons
            df = df.drop_duplicates(subset=['time'], keep='last')
            
            # Trier par date
            df = df.sort_values('time').reset_index(drop=True)
            
            # Vérifier les valeurs manquantes
            missing = df.isnull().sum()
            if missing.any():
                logger.warning(f"Valeurs manquantes détectées:\n{missing[missing > 0]}")
                # Remplir avec la méthode forward fill
                df = df.fillna(method='ffill').fillna(method='bfill')
            
            # Supprimer les lignes avec des prix <= 0
            df = df[(df['open'] > 0) & (df['high'] > 0) & (df['low'] > 0) & (df['close'] > 0)]
            
            # Vérifier la cohérence des prix (high >= low)
            invalid_prices = df[df['high'] < df['low']]
            if len(invalid_prices) > 0:
                logger.warning(f"{len(invalid_prices)} lignes avec high < low supprimées")
                df = df[df['high'] >= df['low']]
            
            cleaned_len = len(df)
            logger.info(f"Données nettoyées: {original_len} -> {cleaned_len} lignes")
            
            return df
            
        except Exception as e:
            logger.error(f"Erreur lors du nettoyage des données: {e}")
            return df
    
    def get_data_summary(self, df: pd.DataFrame) -> dict:
        """
        Obtenir un résumé des données
        
        Args:
            df: DataFrame à analyser
            
        Returns:
            Dictionnaire avec les statistiques
        """
        try:
            summary = {
                "rows": len(df),
                "columns": len(df.columns),
                "start_date": df['time'].min() if 'time' in df.columns else None,
                "end_date": df['time'].max() if 'time' in df.columns else None,
                "missing_values": df.isnull().sum().to_dict(),
                "price_range": {
                    "min": df['close'].min() if 'close' in df.columns else None,
                    "max": df['close'].max() if 'close' in df.columns else None,
                    "mean": df['close'].mean() if 'close' in df.columns else None,
                },
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Erreur lors du calcul du résumé: {e}")
            return {}


# Exemple d'utilisation
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Créer un exemple de données
    dates = pd.date_range(start='2024-01-01', end='2024-01-10', freq='H')
    df = pd.DataFrame({
        'time': dates,
        'open': np.random.uniform(2000, 2100, len(dates)),
        'high': np.random.uniform(2100, 2150, len(dates)),
        'low': np.random.uniform(1950, 2000, len(dates)),
        'close': np.random.uniform(2000, 2100, len(dates)),
        'tick_volume': np.random.randint(100, 1000, len(dates)),
    })
    
    # Tester le gestionnaire
    manager = DataManager()
    
    # Sauvegarder
    filepath = manager.save_raw_data(df, "H1", "test")
    
    # Charger
    loaded_df = manager.load_latest_raw_data("H1", "test")
    
    if loaded_df is not None:
        print("\nRésumé des données:")
        print(manager.get_data_summary(loaded_df))

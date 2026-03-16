"""
Script 1: Collecte des données historiques depuis MT5
Usage: python scripts/01_collect_data.py
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from datetime import datetime
import logging
from config.config import LOGS_DIR, PRIMARY_TIMEFRAME, START_DATE
from config.mt5_config import validate_mt5_config
from data.mt5_collector import MT5Collector
from data.data_manager import DataManager

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOGS_DIR / 'data_collection.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def main():
    """Fonction principale de collecte de données"""
    
    logger.info("="*60)
    logger.info("DÉMARRAGE DE LA COLLECTE DES DONNÉES")
    logger.info("="*60)
    
    try:
        # Valider la configuration MT5
        logger.info("Validation de la configuration MT5...")
        validate_mt5_config()
        
        # Créer les instances
        collector = MT5Collector()
        data_manager = DataManager()
        
        # Se connecter à MT5
        logger.info("Connexion à MetaTrader 5...")
        if not collector.connect():
            logger.error("Impossible de se connecter à MT5")
            return False
        
        # Récupérer les informations du symbole
        symbol_info = collector.get_symbol_info()
        if symbol_info:
            logger.info(f"Symbole: {symbol_info['name']}")
            logger.info(f"Spread: {symbol_info['spread']} points")
        
        # Récupérer les données historiques
        logger.info(f"Récupération des données depuis {START_DATE}...")
        df = collector.get_historical_data(
            timeframe=PRIMARY_TIMEFRAME,
            start_date=datetime.strptime(START_DATE, "%Y-%m-%d"),
            end_date=datetime.now()
        )
        
        if df is None or len(df) == 0:
            logger.error("Aucune donnée récupérée")
            return False
        
        logger.info(f"Données récupérées: {len(df)} barres")
        logger.info(f"Période: {df['time'].min()} à {df['time'].max()}")
        
        # Nettoyer les données
        logger.info("Nettoyage des données...")
        df_cleaned = data_manager.clean_data(df)
        
        # Afficher le résumé
        summary = data_manager.get_data_summary(df_cleaned)
        logger.info(f"\nRésumé des données:")
        logger.info(f"  - Lignes: {summary['rows']}")
        logger.info(f"  - Prix min: ${summary['price_range']['min']:.2f}")
        logger.info(f"  - Prix max: ${summary['price_range']['max']:.2f}")
        logger.info(f"  - Prix moyen: ${summary['price_range']['mean']:.2f}")
        
        # Sauvegarder les données
        logger.info("Sauvegarde des données...")
        filepath = data_manager.save_raw_data(
            df_cleaned,
            PRIMARY_TIMEFRAME,
            suffix="historical"
        )
        
        if filepath:
            logger.info(f"Données sauvegardées: {filepath}")
        
        logger.info("="*60)
        logger.info("COLLECTE TERMINÉE AVEC SUCCÈS")
        logger.info("="*60)
        
        return True
        
    except Exception as e:
        logger.error(f"Erreur lors de la collecte: {e}", exc_info=True)
        return False
        
    finally:
        # Déconnexion
        if collector.connected:
            collector.disconnect()
            logger.info("Déconnexion de MT5")


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

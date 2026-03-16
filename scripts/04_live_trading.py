"""
Script 4: Trading en temps réel (LIVE TRADING)
Usage: python scripts/04_live_trading.py

ATTENTION: Ce script effectue de véritables trades!
Utilisez-le uniquement sur un compte démo pour commencer.
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import logging
import time
from datetime import datetime
import pandas as pd

from config.config import LOGS_DIR, PRIMARY_TIMEFRAME
from config.mt5_config import validate_mt5_config
from data.mt5_collector import MT5Collector
from features.feature_engineering import FeatureEngineer
from models.xgboost_model import XGBoostModel
from trading.signal_generator import SignalGenerator, SignalValidator
from trading.risk_manager import RiskManager
from trading.order_executor import OrderExecutor

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOGS_DIR / 'live_trading.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class LiveTradingBot:
    """Bot de trading en temps réel"""
    
    def __init__(self):
        self.collector = MT5Collector()
        self.feature_engineer = FeatureEngineer()
        self.model = XGBoostModel()
        self.signal_generator = SignalGenerator()
        self.signal_validator = SignalValidator()
        self.risk_manager = RiskManager()
        self.executor = None  # Sera créé après connexion
        
        self.is_running = False
        self.loop_interval = 60  # Vérification toutes les 60 secondes
        
    def initialize(self) -> bool:
        """Initialiser le bot"""
        try:
            logger.info("Initialisation du bot...")
            
            # Valider la configuration
            validate_mt5_config()
            
            # Se connecter à MT5
            if not self.collector.connect():
                logger.error("Impossible de se connecter à MT5")
                return False
            
            # Créer l'exécuteur d'ordres
            self.executor = OrderExecutor(self.collector)
            
            # Charger le modèle
            logger.info("Chargement du modèle...")
            model_name = f"xgboost_model_{PRIMARY_TIMEFRAME}_latest"
            self.model.load(model_name)
            
            logger.info("Bot initialisé avec succès!")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation: {e}", exc_info=True)
            return False
    
    def get_current_market_data(self) -> pd.DataFrame:
        """Récupérer les données actuelles du marché"""
        # Récupérer les dernières 200 barres pour calculer les indicateurs
        df = self.collector.get_latest_bars(
            timeframe=PRIMARY_TIMEFRAME,
            num_bars=200
        )
        
        if df is None:
            raise ValueError("Impossible de récupérer les données")
        
        return df
    
    def generate_trading_signal(self) -> dict:
        """Générer un signal de trading"""
        try:
            # 1. Récupérer les données
            df = self.get_current_market_data()
            
            # 2. Créer les features
            df_features = self.feature_engineer.create_all_features(df)
            
            # 3. Prendre la dernière ligne (données actuelles)
            latest_data = df_features.iloc[-1]
            
            # 4. Préparer les features pour la prédiction
            feature_columns = self.feature_engineer.get_feature_names(df_features)
            features_dict = latest_data[feature_columns].to_dict()
            
            # 5. Faire la prédiction
            label, probabilities = self.model.predict_single(features_dict)
            
            # 6. Préparer les données de marché pour les filtres
            market_data = {
                'close': latest_data['close'],
                'RSI': latest_data.get('RSI', 50),
                'ADX': latest_data.get('ADX', 25),
                'ATR_pct': latest_data.get('ATR_pct', 1.0),
                'trend_medium': latest_data.get('trend_medium', 0),
                'SMA_50': latest_data.get('SMA_50', latest_data['close']),
            }
            
            # 7. Générer le signal
            signal, confidence = self.signal_generator.generate_signal(
                label,
                probabilities,
                market_data
            )
            
            return {
                'signal': signal,
                'confidence': confidence,
                'probabilities': probabilities,
                'market_data': market_data,
                'current_price': latest_data['close'],
                'timestamp': datetime.now()
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération du signal: {e}")
            return None
    
    def execute_trade(self, signal_data: dict) -> bool:
        """Exécuter un trade basé sur le signal"""
        try:
            signal = signal_data['signal']
            
            # Pas de trade pour HOLD
            if signal == "HOLD":
                return False
            
            # Obtenir les informations du compte
            account_info = self.executor.get_account_info()
            if not account_info:
                logger.error("Impossible d'obtenir les infos du compte")
                return False
            
            # Obtenir les positions ouvertes
            open_positions = self.executor.get_open_positions()
            
            # Valider le signal
            is_valid, reason = self.signal_validator.validate_signal(
                signal,
                signal_data['current_price'],
                account_info,
                open_positions
            )
            
            if not is_valid:
                logger.warning(f"Signal non valide: {reason}")
                return False
            
            # Obtenir les infos du symbole
            symbol_info = self.collector.get_symbol_info()
            
            # Calculer le stop loss
            sl_price = self.risk_manager.calculate_stop_loss(
                signal_data['current_price'],
                signal,
                atr=signal_data['market_data'].get('ATR_pct'),
                method="fixed_pips"
            )
            
            # Calculer le take profit
            tp_price = self.risk_manager.calculate_take_profit(
                signal_data['current_price'],
                sl_price,
                signal,
                method="risk_reward"
            )
            
            # Calculer la taille de position
            position_size = self.risk_manager.calculate_position_size(
                account_info['balance'],
                signal_data['current_price'],
                sl_price,
                symbol_info
            )
            
            # Valider le risque
            is_valid, reason = self.risk_manager.validate_trade_risk(
                signal_data['current_price'],
                sl_price,
                tp_price,
                position_size,
                account_info['balance']
            )
            
            if not is_valid:
                logger.warning(f"Risque non valide: {reason}")
                return False
            
            # Envoyer l'ordre
            logger.info(f"Envoi de l'ordre {signal}...")
            result = self.executor.send_order(
                action=signal,
                volume=position_size,
                stop_loss=sl_price,
                take_profit=tp_price,
                comment=f"AI Bot - Conf: {signal_data['confidence']:.2f}"
            )
            
            if result['success']:
                logger.info(f"✓ Trade exécuté: {signal} {position_size} lots")
                logger.info(f"  Prix: {result['price']:.2f}")
                logger.info(f"  SL: {sl_price:.2f}, TP: {tp_price:.2f}")
                logger.info(f"  Ticket: {result['ticket']}")
                return True
            else:
                logger.error(f"✗ Échec du trade: {result.get('error')}")
                return False
                
        except Exception as e:
            logger.error(f"Erreur lors de l'exécution du trade: {e}", exc_info=True)
            return False
    
    def manage_positions(self):
        """Gérer les positions ouvertes (trailing stop, etc.)"""
        try:
            positions = self.executor.get_open_positions()
            
            for position in positions:
                # Vérifier le trailing stop
                should_update, new_sl = self.risk_manager.should_update_trailing_stop(
                    position['type'],
                    position['open_price'],
                    position['current_price'],
                    position['sl']
                )
                
                if should_update and new_sl:
                    logger.info(f"Mise à jour du trailing stop pour {position['ticket']}")
                    self.executor.modify_position(
                        position['ticket'],
                        stop_loss=new_sl
                    )
                    
        except Exception as e:
            logger.error(f"Erreur lors de la gestion des positions: {e}")
    
    def run(self):
        """Boucle principale du bot"""
        self.is_running = True
        
        logger.info("="*60)
        logger.info("DÉMARRAGE DU BOT DE TRADING")
        logger.info("="*60)
        
        try:
            while self.is_running:
                # Vérifier si le marché est ouvert
                if not self.collector.is_market_open():
                    logger.info("Marché fermé, attente...")
                    time.sleep(300)  # Attendre 5 minutes
                    continue
                
                # Afficher le statut
                account_info = self.executor.get_account_info()
                if account_info:
                    logger.info(f"\n{'='*60}")
                    logger.info(f"Status: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    logger.info(f"Balance: ${account_info['balance']:.2f}")
                    logger.info(f"Equity: ${account_info['equity']:.2f}")
                    logger.info(f"Profit: ${account_info['profit']:.2f}")
                
                # Gérer les positions existantes
                self.manage_positions()
                
                # Générer un signal
                logger.info("Analyse du marché...")
                signal_data = self.generate_trading_signal()
                
                if signal_data:
                    logger.info(f"Signal: {signal_data['signal']} "
                              f"(confiance: {signal_data['confidence']:.3f})")
                    
                    # Exécuter le trade si nécessaire
                    if signal_data['signal'] != "HOLD":
                        self.execute_trade(signal_data)
                
                # Attendre avant la prochaine itération
                logger.info(f"Prochaine vérification dans {self.loop_interval}s...")
                time.sleep(self.loop_interval)
                
        except KeyboardInterrupt:
            logger.info("\nArrêt du bot par l'utilisateur...")
        except Exception as e:
            logger.error(f"Erreur dans la boucle principale: {e}", exc_info=True)
        finally:
            self.shutdown()
    
    def shutdown(self):
        """Arrêter proprement le bot"""
        logger.info("Arrêt du bot...")
        self.is_running = False
        
        if self.collector.connected:
            self.collector.disconnect()
        
        logger.info("Bot arrêté")


def main():
    """Fonction principale"""
    
    # Créer le bot
    bot = LiveTradingBot()
    
    # Initialiser
    if not bot.initialize():
        logger.error("Échec de l'initialisation")
        return False
    
    # Afficher un avertissement
    logger.warning("\n" + "!"*60)
    logger.warning("ATTENTION: Trading en temps réel activé!")
    logger.warning("Assurez-vous d'utiliser un compte DÉMO pour les tests.")
    logger.warning("!"*60 + "\n")
    
    # Demander confirmation
    print("\nVoulez-vous démarrer le bot de trading? (oui/non): ", end='')
    response = input().strip().lower()
    
    if response not in ['oui', 'yes', 'y']:
        logger.info("Démarrage annulé par l'utilisateur")
        return False
    
    # Démarrer le bot
    bot.run()
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

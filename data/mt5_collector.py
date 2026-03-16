"""
Module de collecte des données depuis MetaTrader 5
"""
import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime, timedelta
import time
from typing import Optional, Tuple
import logging

from config.mt5_config import MT5_CONFIG, CONNECTION_PARAMS, MT5_TIMEFRAMES
from config.config import SYMBOL

logger = logging.getLogger(__name__)


class MT5Collector:
    """Collecteur de données depuis MetaTrader 5"""
    
    def __init__(self):
        self.connected = False
        self.symbol = SYMBOL
        
    def connect(self) -> bool:
        """
        Établir la connexion avec MT5
        
        Returns:
            bool: True si la connexion est établie, False sinon
        """
        for attempt in range(CONNECTION_PARAMS["retries"]):
            try:
                # Initialiser MT5
                if not mt5.initialize(
                    path=MT5_CONFIG["path"] if MT5_CONFIG["path"] else None,
                    login=MT5_CONFIG["login"],
                    password=MT5_CONFIG["password"],
                    server=MT5_CONFIG["server"],
                    timeout=MT5_CONFIG["timeout"],
                    portable=MT5_CONFIG["portable"]
                ):
                    logger.error(f"Échec d'initialisation MT5: {mt5.last_error()}")
                    time.sleep(CONNECTION_PARAMS["retry_delay"])
                    continue
                
                # Vérifier la connexion
                account_info = mt5.account_info()
                if account_info is None:
                    logger.error("Impossible de récupérer les informations du compte")
                    mt5.shutdown()
                    time.sleep(CONNECTION_PARAMS["retry_delay"])
                    continue
                
                self.connected = True
                logger.info(f"Connexion MT5 établie - Compte: {account_info.login}")
                logger.info(f"Broker: {account_info.server}, Balance: {account_info.balance}")
                
                # Vérifier que le symbole est disponible
                if not self._check_symbol():
                    logger.error(f"Symbole {self.symbol} non disponible")
                    self.disconnect()
                    return False
                
                return True
                
            except Exception as e:
                logger.error(f"Erreur lors de la connexion MT5 (tentative {attempt + 1}): {e}")
                time.sleep(CONNECTION_PARAMS["retry_delay"])
        
        logger.error("Impossible d'établir la connexion avec MT5")
        return False
    
    def disconnect(self):
        """Fermer la connexion MT5"""
        if self.connected:
            mt5.shutdown()
            self.connected = False
            logger.info("Connexion MT5 fermée")
    
    def _check_symbol(self) -> bool:
        """
        Vérifier la disponibilité du symbole
        
        Returns:
            bool: True si le symbole est disponible
        """
        symbol_info = mt5.symbol_info(self.symbol)
        if symbol_info is None:
            return False
        
        # Activer le symbole s'il est disponible mais non sélectionné
        if not symbol_info.visible:
            if not mt5.symbol_select(self.symbol, True):
                return False
        
        logger.info(f"Symbole {self.symbol} vérifié - Spread: {symbol_info.spread}")
        return True
    
    def get_historical_data(
        self,
        timeframe: str = "H1",
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        num_bars: Optional[int] = None
    ) -> Optional[pd.DataFrame]:
        """
        Récupérer les données historiques
        
        Args:
            timeframe: Période temporelle (M1, M5, H1, etc.)
            start_date: Date de début
            end_date: Date de fin
            num_bars: Nombre de barres (alternatif à start_date/end_date)
            
        Returns:
            DataFrame avec colonnes: time, open, high, low, close, tick_volume, spread, real_volume
        """
        if not self.connected:
            logger.error("Non connecté à MT5")
            return None
        
        try:
            # Convertir le timeframe
            mt5_timeframe = MT5_TIMEFRAMES.get(timeframe)
            if mt5_timeframe is None:
                logger.error(f"Timeframe invalide: {timeframe}")
                return None
            
            # Récupérer les données
            if num_bars:
                # Récupérer un nombre spécifique de barres
                rates = mt5.copy_rates_from_pos(self.symbol, mt5_timeframe, 0, num_bars)
            else:
                # Récupérer entre deux dates
                if start_date is None:
                    start_date = datetime.now() - timedelta(days=365)
                if end_date is None:
                    end_date = datetime.now()
                
                rates = mt5.copy_rates_range(
                    self.symbol,
                    mt5_timeframe,
                    start_date,
                    end_date
                )
            
            if rates is None or len(rates) == 0:
                logger.error(f"Aucune donnée récupérée: {mt5.last_error()}")
                return None
            
            # Convertir en DataFrame
            df = pd.DataFrame(rates)
            df['time'] = pd.to_datetime(df['time'], unit='s')
            
            logger.info(f"Données récupérées: {len(df)} barres de {start_date} à {end_date}")
            logger.info(f"Période: {df['time'].min()} à {df['time'].max()}")
            
            return df
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des données: {e}")
            return None
    
    def get_current_price(self) -> Optional[Tuple[float, float]]:
        """
        Récupérer le prix actuel (bid, ask)
        
        Returns:
            Tuple (bid, ask) ou None
        """
        if not self.connected:
            logger.error("Non connecté à MT5")
            return None
        
        try:
            tick = mt5.symbol_info_tick(self.symbol)
            if tick is None:
                logger.error(f"Impossible de récupérer le prix: {mt5.last_error()}")
                return None
            
            return (tick.bid, tick.ask)
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du prix: {e}")
            return None
    
    def get_latest_bars(self, timeframe: str = "H1", num_bars: int = 100) -> Optional[pd.DataFrame]:
        """
        Récupérer les dernières barres pour le trading en temps réel
        
        Args:
            timeframe: Période temporelle
            num_bars: Nombre de barres à récupérer
            
        Returns:
            DataFrame avec les dernières barres
        """
        return self.get_historical_data(timeframe=timeframe, num_bars=num_bars)
    
    def get_symbol_info(self) -> Optional[dict]:
        """
        Récupérer les informations du symbole
        
        Returns:
            Dictionnaire avec les informations du symbole
        """
        if not self.connected:
            logger.error("Non connecté à MT5")
            return None
        
        try:
            symbol_info = mt5.symbol_info(self.symbol)
            if symbol_info is None:
                return None
            
            return {
                "name": symbol_info.name,
                "description": symbol_info.description,
                "point": symbol_info.point,
                "digits": symbol_info.digits,
                "spread": symbol_info.spread,
                "volume_min": symbol_info.volume_min,
                "volume_max": symbol_info.volume_max,
                "volume_step": symbol_info.volume_step,
                "trade_contract_size": symbol_info.trade_contract_size,
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des infos symbole: {e}")
            return None
    
    def is_market_open(self) -> bool:
        """
        Vérifier si le marché est ouvert
        
        Returns:
            bool: True si le marché est ouvert
        """
        if not self.connected:
            return False
        
        try:
            symbol_info = mt5.symbol_info(self.symbol)
            if symbol_info is None:
                return False
            
            # Vérifier les sessions de trading
            return symbol_info.trade_mode == mt5.SYMBOL_TRADE_MODE_FULL
            
        except Exception as e:
            logger.error(f"Erreur lors de la vérification du marché: {e}")
            return False


# Exemple d'utilisation
if __name__ == "__main__":
    # Configuration du logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Créer le collecteur
    collector = MT5Collector()
    
    # Se connecter
    if collector.connect():
        # Récupérer des données historiques
        df = collector.get_historical_data(
            timeframe="H1",
            start_date=datetime(2024, 1, 1),
            end_date=datetime.now()
        )
        
        if df is not None:
            print(f"\nDonnées récupérées: {len(df)} lignes")
            print(df.head())
            print(f"\nInfo symbole:")
            print(collector.get_symbol_info())
            print(f"\nPrix actuel: {collector.get_current_price()}")
        
        # Déconnexion
        collector.disconnect()

"""
Module de génération de signaux de trading
"""
import numpy as np
import pandas as pd
from typing import Tuple, Optional
import logging

from config.config import SIGNAL_CONFIG, LABELS

logger = logging.getLogger(__name__)


class SignalGenerator:
    """Générateur de signaux de trading basé sur les prédictions du modèle"""
    
    def __init__(self):
        self.config = SIGNAL_CONFIG
        
    def generate_signal(
        self,
        prediction: int,
        probabilities: np.ndarray,
        market_data: Optional[dict] = None
    ) -> Tuple[str, float]:
        """
        Générer un signal de trading
        
        Args:
            prediction: Label prédit (0: HOLD, 1: BUY, 2: SELL)
            probabilities: Probabilités pour chaque classe [P(HOLD), P(BUY), P(SELL)]
            market_data: Données de marché optionnelles pour filtres additionnels
            
        Returns:
            Tuple (signal, confidence) où signal est "BUY", "SELL" ou "HOLD"
        """
        # Récupérer le seuil de confiance
        confidence_threshold = self.config['confidence_threshold']
        
        # Probabilité de la classe prédite
        confidence = probabilities[prediction]
        
        # Vérifier si la confiance est suffisante
        if confidence < confidence_threshold:
            logger.debug(f"Confiance insuffisante: {confidence:.3f} < {confidence_threshold}")
            return "HOLD", confidence
        
        # Convertir la prédiction en signal
        signal = LABELS[prediction]
        
        # Appliquer les filtres additionnels si les données de marché sont fournies
        if market_data is not None:
            signal = self._apply_filters(signal, probabilities, market_data)
        
        # Vérifier les seuils spécifiques pour BUY et SELL
        if signal == "BUY":
            min_prob = self.config['min_probability_buy']
            if probabilities[1] < min_prob:
                logger.debug(f"Probabilité BUY insuffisante: {probabilities[1]:.3f} < {min_prob}")
                return "HOLD", confidence
        
        elif signal == "SELL":
            min_prob = self.config['min_probability_sell']
            if probabilities[2] < min_prob:
                logger.debug(f"Probabilité SELL insuffisante: {probabilities[2]:.3f} < {min_prob}")
                return "HOLD", confidence
        
        logger.info(f"Signal généré: {signal} (confiance: {confidence:.3f})")
        
        return signal, confidence
    
    def _apply_filters(
        self,
        signal: str,
        probabilities: np.ndarray,
        market_data: dict
    ) -> str:
        """
        Appliquer des filtres additionnels au signal
        
        Args:
            signal: Signal initial
            probabilities: Probabilités des classes
            market_data: Données de marché (RSI, ADX, ATR, trend, etc.)
            
        Returns:
            Signal filtré
        """
        # Filtre de tendance
        if self.config.get('use_trend_filter', False):
            signal = self._trend_filter(signal, market_data)
        
        # Filtre de volatilité
        if self.config.get('use_volatility_filter', False):
            signal = self._volatility_filter(signal, market_data)
        
        return signal
    
    def _trend_filter(self, signal: str, market_data: dict) -> str:
        """
        Filtrer le signal selon la tendance du marché
        
        Ne trader que dans le sens de la tendance:
        - Si tendance haussière: autoriser BUY, bloquer SELL
        - Si tendance baissière: autoriser SELL, bloquer BUY
        """
        # Vérifier si on a les données de tendance
        trend_indicators = ['trend_medium', 'SMA_50', 'EMA_26']
        if not any(ind in market_data for ind in trend_indicators):
            return signal  # Pas de filtre si pas de données
        
        # Déterminer la tendance
        is_uptrend = False
        is_downtrend = False
        
        if 'trend_medium' in market_data:
            is_uptrend = market_data['trend_medium'] > 0
            is_downtrend = market_data['trend_medium'] < 0
        
        elif 'SMA_50' in market_data and 'close' in market_data:
            is_uptrend = market_data['close'] > market_data['SMA_50']
            is_downtrend = market_data['close'] < market_data['SMA_50']
        
        # Appliquer le filtre
        if signal == "BUY" and is_downtrend:
            logger.debug("Signal BUY filtré: tendance baissière")
            return "HOLD"
        
        if signal == "SELL" and is_uptrend:
            logger.debug("Signal SELL filtré: tendance haussière")
            return "HOLD"
        
        return signal
    
    def _volatility_filter(self, signal: str, market_data: dict) -> str:
        """
        Filtrer le signal selon la volatilité
        
        Éviter de trader pendant les périodes de faible volatilité
        ou de volatilité extrême
        """
        # Vérifier si on a l'ATR
        if 'ATR' not in market_data or 'ATR_pct' not in market_data:
            return signal
        
        atr_pct = market_data['ATR_pct']
        
        # Définir les seuils (à ajuster selon le symbole)
        min_volatility = 0.5  # Volatilité minimale (%)
        max_volatility = 3.0  # Volatilité maximale (%)
        
        if atr_pct < min_volatility:
            logger.debug(f"Signal filtré: volatilité trop faible ({atr_pct:.2f}%)")
            return "HOLD"
        
        if atr_pct > max_volatility:
            logger.debug(f"Signal filtré: volatilité trop élevée ({atr_pct:.2f}%)")
            return "HOLD"
        
        return signal
    
    def analyze_signals(self, signals: pd.DataFrame) -> dict:
        """
        Analyser les signaux générés sur une période
        
        Args:
            signals: DataFrame avec colonnes ['signal', 'confidence']
            
        Returns:
            Dictionnaire avec les statistiques
        """
        stats = {
            'total': len(signals),
            'buy': (signals['signal'] == 'BUY').sum(),
            'sell': (signals['signal'] == 'SELL').sum(),
            'hold': (signals['signal'] == 'HOLD').sum(),
            'avg_confidence_buy': signals[signals['signal'] == 'BUY']['confidence'].mean(),
            'avg_confidence_sell': signals[signals['signal'] == 'SELL']['confidence'].mean(),
            'avg_confidence_all': signals['confidence'].mean(),
        }
        
        stats['buy_pct'] = (stats['buy'] / stats['total']) * 100
        stats['sell_pct'] = (stats['sell'] / stats['total']) * 100
        stats['hold_pct'] = (stats['hold'] / stats['total']) * 100
        
        return stats


class SignalValidator:
    """Validateur de signaux pour éviter les erreurs de trading"""
    
    @staticmethod
    def validate_signal(
        signal: str,
        current_price: float,
        account_info: dict,
        open_positions: list
    ) -> Tuple[bool, str]:
        """
        Valider un signal avant exécution
        
        Args:
            signal: Signal à valider
            current_price: Prix actuel
            account_info: Informations du compte
            open_positions: Liste des positions ouvertes
            
        Returns:
            Tuple (is_valid, reason)
        """
        # Vérifier que le signal est valide
        if signal not in ["BUY", "SELL", "HOLD"]:
            return False, f"Signal invalide: {signal}"
        
        # Pas de validation pour HOLD
        if signal == "HOLD":
            return True, "OK"
        
        # Vérifier le prix
        if current_price <= 0:
            return False, "Prix invalide"
        
        # Vérifier la balance du compte
        if account_info.get('balance', 0) <= 0:
            return False, "Balance insuffisante"
        
        # Vérifier le margin disponible
        if account_info.get('margin_free', 0) <= 0:
            return False, "Margin insuffisant"
        
        # Vérifier le nombre de positions ouvertes
        from config.config import RISK_CONFIG
        max_positions = RISK_CONFIG['max_open_positions']
        if len(open_positions) >= max_positions:
            return False, f"Nombre max de positions atteint ({max_positions})"
        
        # Vérifier qu'on n'a pas déjà une position dans la même direction
        for position in open_positions:
            if (signal == "BUY" and position['type'] == "BUY") or \
               (signal == "SELL" and position['type'] == "SELL"):
                return False, f"Position {signal} déjà ouverte"
        
        return True, "OK"


# Exemple d'utilisation
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Créer le générateur
    generator = SignalGenerator()
    
    # Simuler des prédictions
    predictions = [
        (1, np.array([0.1, 0.8, 0.1])),  # BUY avec forte confiance
        (2, np.array([0.1, 0.1, 0.75])),  # SELL avec bonne confiance
        (0, np.array([0.6, 0.3, 0.1])),   # HOLD
        (1, np.array([0.4, 0.55, 0.05])), # BUY avec faible confiance
    ]
    
    # Données de marché fictives
    market_data = {
        'close': 2050,
        'RSI': 55,
        'ADX': 25,
        'ATR_pct': 1.2,
        'trend_medium': 1,
        'SMA_50': 2040,
    }
    
    print("\nGénération de signaux:")
    print("-" * 60)
    
    for pred, proba in predictions:
        signal, confidence = generator.generate_signal(pred, proba, market_data)
        print(f"Prédiction: {LABELS[pred]}, Probas: {proba}, "
              f"→ Signal: {signal} (confiance: {confidence:.3f})")

"""
Module de gestion du risque (Risk Management)
"""
import numpy as np
from typing import Tuple, Optional
import logging

from config.config import RISK_CONFIG, SYMBOL

logger = logging.getLogger(__name__)


class RiskManager:
    """Gestionnaire de risque pour le système de trading"""
    
    def __init__(self):
        self.config = RISK_CONFIG
        self.daily_loss = 0.0
        self.daily_trades = 0
        
    def calculate_position_size(
        self,
        account_balance: float,
        entry_price: float,
        stop_loss_price: float,
        symbol_info: dict
    ) -> float:
        """
        Calculer la taille de la position basée sur le risque
        
        Args:
            account_balance: Balance du compte
            entry_price: Prix d'entrée
            stop_loss_price: Prix du stop loss
            symbol_info: Informations du symbole (volume_min, volume_max, etc.)
            
        Returns:
            Taille de la position (en lots)
        """
        # Montant maximum à risquer
        max_risk_amount = account_balance * self.config['max_risk_per_trade']
        
        # Calculer le risque par unité
        price_risk = abs(entry_price - stop_loss_price)
        
        if price_risk == 0:
            logger.warning("Risque de prix = 0, utilisation du volume minimum")
            return symbol_info.get('volume_min', 0.01)
        
        # Taille du contrat (pour l'or, 1 lot = 100 oz généralement)
        contract_size = symbol_info.get('trade_contract_size', 100)
        
        # Calculer la taille de position
        position_size = max_risk_amount / (price_risk * contract_size)
        
        # Arrondir au step du volume
        volume_step = symbol_info.get('volume_step', 0.01)
        position_size = round(position_size / volume_step) * volume_step
        
        # Limiter par les contraintes du broker
        volume_min = symbol_info.get('volume_min', 0.01)
        volume_max = symbol_info.get('volume_max', 100.0)
        
        position_size = max(volume_min, min(position_size, volume_max))
        
        logger.info(f"Position size calculée: {position_size} lots")
        logger.info(f"Risque: ${max_risk_amount:.2f} ({self.config['max_risk_per_trade']*100}%)")
        
        return position_size
    
    def calculate_stop_loss(
        self,
        entry_price: float,
        signal_type: str,
        atr: Optional[float] = None,
        method: str = "fixed_pips"
    ) -> float:
        """
        Calculer le prix du Stop Loss
        
        Args:
            entry_price: Prix d'entrée
            signal_type: "BUY" ou "SELL"
            atr: Average True Range (optionnel, pour méthode ATR)
            method: Méthode de calcul ("fixed_pips", "atr", "percentage")
            
        Returns:
            Prix du stop loss
        """
        if method == "fixed_pips":
            # Stop loss fixe en pips
            sl_pips = self.config['stop_loss_pips']
            pip_value = 0.01  # Pour XAUUSD, 1 pip = 0.01
            
            if signal_type == "BUY":
                sl_price = entry_price - (sl_pips * pip_value)
            else:  # SELL
                sl_price = entry_price + (sl_pips * pip_value)
        
        elif method == "atr" and atr is not None:
            # Stop loss basé sur l'ATR
            atr_multiplier = 2.0  # Facteur multiplicateur de l'ATR
            
            if signal_type == "BUY":
                sl_price = entry_price - (atr * atr_multiplier)
            else:  # SELL
                sl_price = entry_price + (atr * atr_multiplier)
        
        elif method == "percentage":
            # Stop loss en pourcentage
            sl_percentage = 0.01  # 1%
            
            if signal_type == "BUY":
                sl_price = entry_price * (1 - sl_percentage)
            else:  # SELL
                sl_price = entry_price * (1 + sl_percentage)
        
        else:
            logger.warning(f"Méthode de SL inconnue: {method}, utilisation de fixed_pips")
            return self.calculate_stop_loss(entry_price, signal_type, method="fixed_pips")
        
        logger.info(f"Stop Loss calculé: {sl_price:.2f} (méthode: {method})")
        
        return sl_price
    
    def calculate_take_profit(
        self,
        entry_price: float,
        stop_loss_price: float,
        signal_type: str,
        method: str = "risk_reward"
    ) -> float:
        """
        Calculer le prix du Take Profit
        
        Args:
            entry_price: Prix d'entrée
            stop_loss_price: Prix du stop loss
            signal_type: "BUY" ou "SELL"
            method: Méthode de calcul ("risk_reward", "fixed_pips")
            
        Returns:
            Prix du take profit
        """
        if method == "risk_reward":
            # Take profit basé sur le ratio risque/récompense
            risk = abs(entry_price - stop_loss_price)
            reward = risk * self.config['risk_reward_ratio']
            
            if signal_type == "BUY":
                tp_price = entry_price + reward
            else:  # SELL
                tp_price = entry_price - reward
        
        elif method == "fixed_pips":
            # Take profit fixe en pips
            tp_pips = self.config['take_profit_pips']
            pip_value = 0.01
            
            if signal_type == "BUY":
                tp_price = entry_price + (tp_pips * pip_value)
            else:  # SELL
                tp_price = entry_price - (tp_pips * pip_value)
        
        else:
            logger.warning(f"Méthode de TP inconnue: {method}, utilisation de risk_reward")
            return self.calculate_take_profit(
                entry_price, stop_loss_price, signal_type, method="risk_reward"
            )
        
        logger.info(f"Take Profit calculé: {tp_price:.2f} (méthode: {method})")
        
        return tp_price
    
    def should_update_trailing_stop(
        self,
        position_type: str,
        entry_price: float,
        current_price: float,
        current_sl: float
    ) -> Tuple[bool, Optional[float]]:
        """
        Vérifier si le trailing stop doit être mis à jour
        
        Args:
            position_type: "BUY" ou "SELL"
            entry_price: Prix d'entrée
            current_price: Prix actuel
            current_sl: Stop loss actuel
            
        Returns:
            Tuple (should_update, new_sl_price)
        """
        if not self.config.get('trailing_stop', False):
            return False, None
        
        trailing_pips = self.config['trailing_stop_pips']
        pip_value = 0.01
        trailing_distance = trailing_pips * pip_value
        
        if position_type == "BUY":
            # Pour une position BUY, le prix doit monter
            # Le SL suit le prix en restant à une distance fixe
            new_sl = current_price - trailing_distance
            
            # Mise à jour seulement si le nouveau SL est plus haut que l'actuel
            if new_sl > current_sl and new_sl > entry_price:
                logger.info(f"Trailing stop BUY: {current_sl:.2f} → {new_sl:.2f}")
                return True, new_sl
        
        else:  # SELL
            # Pour une position SELL, le prix doit descendre
            # Le SL suit le prix en restant à une distance fixe
            new_sl = current_price + trailing_distance
            
            # Mise à jour seulement si le nouveau SL est plus bas que l'actuel
            if new_sl < current_sl and new_sl < entry_price:
                logger.info(f"Trailing stop SELL: {current_sl:.2f} → {new_sl:.2f}")
                return True, new_sl
        
        return False, None
    
    def check_daily_limits(self, current_loss: float) -> Tuple[bool, str]:
        """
        Vérifier si les limites quotidiennes sont respectées
        
        Args:
            current_loss: Perte actuelle de la journée (négatif)
            
        Returns:
            Tuple (can_trade, reason)
        """
        max_daily_loss = self.config['max_daily_loss']
        
        # Calculer la perte en pourcentage
        # Note: current_loss devrait être négatif si c'est une perte
        loss_percentage = abs(current_loss)
        
        if loss_percentage >= max_daily_loss:
            reason = f"Limite de perte quotidienne atteinte: {loss_percentage:.2%} >= {max_daily_loss:.2%}"
            logger.warning(reason)
            return False, reason
        
        return True, "OK"
    
    def calculate_risk_reward_ratio(
        self,
        entry_price: float,
        stop_loss: float,
        take_profit: float
    ) -> float:
        """
        Calculer le ratio risque/récompense réel
        
        Args:
            entry_price: Prix d'entrée
            stop_loss: Prix du stop loss
            take_profit: Prix du take profit
            
        Returns:
            Ratio risque/récompense
        """
        risk = abs(entry_price - stop_loss)
        reward = abs(take_profit - entry_price)
        
        if risk == 0:
            return 0
        
        ratio = reward / risk
        
        return ratio
    
    def validate_trade_risk(
        self,
        entry_price: float,
        stop_loss: float,
        take_profit: float,
        position_size: float,
        account_balance: float
    ) -> Tuple[bool, str]:
        """
        Valider le risque d'un trade avant exécution
        
        Args:
            entry_price: Prix d'entrée
            stop_loss: Stop loss
            take_profit: Take profit
            position_size: Taille de position
            account_balance: Balance du compte
            
        Returns:
            Tuple (is_valid, reason)
        """
        # Vérifier que les prix sont valides
        if entry_price <= 0 or stop_loss <= 0 or take_profit <= 0:
            return False, "Prix invalides"
        
        # Vérifier le ratio risque/récompense
        rr_ratio = self.calculate_risk_reward_ratio(entry_price, stop_loss, take_profit)
        min_rr_ratio = self.config['risk_reward_ratio']
        
        if rr_ratio < min_rr_ratio:
            return False, f"Ratio R/R insuffisant: {rr_ratio:.2f} < {min_rr_ratio}"
        
        # Vérifier le risque total
        risk = abs(entry_price - stop_loss) * position_size * 100  # 100 = contract size
        risk_percentage = risk / account_balance
        max_risk = self.config['max_risk_per_trade']
        
        if risk_percentage > max_risk * 1.1:  # Marge de 10%
            return False, f"Risque trop élevé: {risk_percentage:.2%} > {max_risk:.2%}"
        
        return True, "OK"


# Exemple d'utilisation
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Créer le gestionnaire de risque
    rm = RiskManager()
    
    # Paramètres fictifs
    account_balance = 10000
    entry_price = 2050.50
    symbol_info = {
        'volume_min': 0.01,
        'volume_max': 100.0,
        'volume_step': 0.01,
        'trade_contract_size': 100,
    }
    
    print("\n" + "="*60)
    print("SIMULATION DE GESTION DU RISQUE")
    print("="*60)
    
    # Calculer le stop loss
    sl_price = rm.calculate_stop_loss(entry_price, "BUY")
    
    # Calculer le take profit
    tp_price = rm.calculate_take_profit(entry_price, sl_price, "BUY")
    
    # Calculer la taille de position
    position_size = rm.calculate_position_size(
        account_balance, entry_price, sl_price, symbol_info
    )
    
    # Calculer le ratio R/R
    rr_ratio = rm.calculate_risk_reward_ratio(entry_price, sl_price, tp_price)
    print(f"\nRatio Risque/Récompense: 1:{rr_ratio:.2f}")
    
    # Valider le trade
    is_valid, reason = rm.validate_trade_risk(
        entry_price, sl_price, tp_price, position_size, account_balance
    )
    print(f"\nValidation du trade: {is_valid} ({reason})")
    
    # Tester le trailing stop
    current_price = 2060.00  # Prix monté de 10$
    should_update, new_sl = rm.should_update_trailing_stop(
        "BUY", entry_price, current_price, sl_price
    )
    print(f"\nTrailing Stop: {should_update}")
    if should_update:
        print(f"Nouveau SL: {new_sl:.2f}")

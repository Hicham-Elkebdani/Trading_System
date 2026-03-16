"""
Module d'exécution des ordres via MetaTrader 5
"""
import MetaTrader5 as mt5
from datetime import datetime
from typing import Optional, Dict
import logging
import time

from config.mt5_config import MT5_CONFIG, ORDER_PARAMS, ORDER_TYPES
from config.config import SYMBOL

logger = logging.getLogger(__name__)


class OrderExecutor:
    """Exécuteur d'ordres pour le trading automatique"""
    
    def __init__(self, mt5_connector):
        """
        Args:
            mt5_connector: Instance de MT5Collector connectée
        """
        self.connector = mt5_connector
        self.symbol = SYMBOL
        self.magic_number = ORDER_PARAMS['magic_number']
        
    def send_order(
        self,
        action: str,
        volume: float,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None,
        comment: str = "",
        deviation: int = None
    ) -> Dict:
        """
        Envoyer un ordre au marché
        
        Args:
            action: "BUY" ou "SELL"
            volume: Taille de la position en lots
            stop_loss: Prix du stop loss (optionnel)
            take_profit: Prix du take profit (optionnel)
            comment: Commentaire de l'ordre
            deviation: Déviation maximale du prix en points
            
        Returns:
            Dictionnaire avec le résultat de l'ordre
        """
        if not self.connector.connected:
            logger.error("Non connecté à MT5")
            return {"success": False, "error": "Non connecté"}
        
        try:
            # Obtenir le prix actuel
            symbol_info = mt5.symbol_info_tick(self.symbol)
            if symbol_info is None:
                logger.error(f"Impossible d'obtenir le prix pour {self.symbol}")
                return {"success": False, "error": "Prix non disponible"}
            
            # Déterminer le type d'ordre et le prix
            if action == "BUY":
                order_type = ORDER_TYPES["BUY"]
                price = symbol_info.ask
            elif action == "SELL":
                order_type = ORDER_TYPES["SELL"]
                price = symbol_info.bid
            else:
                logger.error(f"Action invalide: {action}")
                return {"success": False, "error": "Action invalide"}
            
            # Préparer la requête d'ordre
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": self.symbol,
                "volume": volume,
                "type": order_type,
                "price": price,
                "deviation": deviation or ORDER_PARAMS['deviation'],
                "magic": self.magic_number,
                "comment": comment or ORDER_PARAMS['comment'],
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,  # Immediate or Cancel
            }
            
            # Ajouter SL et TP si fournis
            if stop_loss is not None:
                request["sl"] = stop_loss
            if take_profit is not None:
                request["tp"] = take_profit
            
            # Log de la requête
            logger.info(f"Envoi ordre {action}: {volume} lots @ {price:.2f}")
            if stop_loss:
                logger.info(f"Stop Loss: {stop_loss:.2f}")
            if take_profit:
                logger.info(f"Take Profit: {take_profit:.2f}")
            
            # Envoyer l'ordre
            result = mt5.order_send(request)
            
            # Vérifier le résultat
            if result is None:
                logger.error("order_send a retourné None")
                return {"success": False, "error": "Résultat None"}
            
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                logger.error(f"Échec de l'ordre: {result.retcode} - {result.comment}")
                return {
                    "success": False,
                    "error": result.comment,
                    "retcode": result.retcode
                }
            
            # Succès
            logger.info(f"Ordre exécuté avec succès!")
            logger.info(f"Ticket: {result.order}, Volume: {result.volume}, Prix: {result.price}")
            
            return {
                "success": True,
                "ticket": result.order,
                "volume": result.volume,
                "price": result.price,
                "action": action,
                "comment": result.comment,
                "request_id": result.request_id,
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi de l'ordre: {e}")
            return {"success": False, "error": str(e)}
    
    def modify_position(
        self,
        ticket: int,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None
    ) -> Dict:
        """
        Modifier une position existante (SL/TP)
        
        Args:
            ticket: Numéro du ticket de la position
            stop_loss: Nouveau stop loss (optionnel)
            take_profit: Nouveau take profit (optionnel)
            
        Returns:
            Dictionnaire avec le résultat
        """
        try:
            # Obtenir la position
            position = mt5.positions_get(ticket=ticket)
            
            if position is None or len(position) == 0:
                logger.error(f"Position {ticket} non trouvée")
                return {"success": False, "error": "Position non trouvée"}
            
            position = position[0]
            
            # Préparer la requête de modification
            request = {
                "action": mt5.TRADE_ACTION_SLTP,
                "symbol": self.symbol,
                "position": ticket,
            }
            
            # Ajouter les nouveaux SL/TP
            if stop_loss is not None:
                request["sl"] = stop_loss
            else:
                request["sl"] = position.sl
            
            if take_profit is not None:
                request["tp"] = take_profit
            else:
                request["tp"] = position.tp
            
            logger.info(f"Modification position {ticket}")
            logger.info(f"Nouveau SL: {request['sl']:.2f}, TP: {request['tp']:.2f}")
            
            # Envoyer la modification
            result = mt5.order_send(request)
            
            if result is None or result.retcode != mt5.TRADE_RETCODE_DONE:
                error_msg = result.comment if result else "Résultat None"
                logger.error(f"Échec de la modification: {error_msg}")
                return {"success": False, "error": error_msg}
            
            logger.info("Position modifiée avec succès")
            return {"success": True, "ticket": ticket}
            
        except Exception as e:
            logger.error(f"Erreur lors de la modification: {e}")
            return {"success": False, "error": str(e)}
    
    def close_position(self, ticket: int, volume: Optional[float] = None) -> Dict:
        """
        Fermer une position
        
        Args:
            ticket: Numéro du ticket de la position
            volume: Volume à fermer (None = fermeture complète)
            
        Returns:
            Dictionnaire avec le résultat
        """
        try:
            # Obtenir la position
            position = mt5.positions_get(ticket=ticket)
            
            if position is None or len(position) == 0:
                logger.error(f"Position {ticket} non trouvée")
                return {"success": False, "error": "Position non trouvée"}
            
            position = position[0]
            
            # Déterminer le type d'ordre de fermeture (inverse de la position)
            if position.type == mt5.ORDER_TYPE_BUY:
                close_type = mt5.ORDER_TYPE_SELL
                price = mt5.symbol_info_tick(self.symbol).bid
            else:
                close_type = mt5.ORDER_TYPE_BUY
                price = mt5.symbol_info_tick(self.symbol).ask
            
            # Volume à fermer
            close_volume = volume or position.volume
            
            # Préparer la requête
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": self.symbol,
                "volume": close_volume,
                "type": close_type,
                "position": ticket,
                "price": price,
                "deviation": ORDER_PARAMS['deviation'],
                "magic": self.magic_number,
                "comment": "Close by bot",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            
            logger.info(f"Fermeture position {ticket}: {close_volume} lots @ {price:.2f}")
            
            # Envoyer l'ordre de fermeture
            result = mt5.order_send(request)
            
            if result is None or result.retcode != mt5.TRADE_RETCODE_DONE:
                error_msg = result.comment if result else "Résultat None"
                logger.error(f"Échec de la fermeture: {error_msg}")
                return {"success": False, "error": error_msg}
            
            logger.info(f"Position {ticket} fermée avec succès")
            return {
                "success": True,
                "ticket": ticket,
                "close_price": result.price,
                "profit": position.profit
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la fermeture: {e}")
            return {"success": False, "error": str(e)}
    
    def get_open_positions(self) -> list:
        """
        Obtenir toutes les positions ouvertes
        
        Returns:
            Liste des positions ouvertes
        """
        try:
            positions = mt5.positions_get(symbol=self.symbol)
            
            if positions is None:
                return []
            
            positions_list = []
            for pos in positions:
                positions_list.append({
                    "ticket": pos.ticket,
                    "type": "BUY" if pos.type == mt5.ORDER_TYPE_BUY else "SELL",
                    "volume": pos.volume,
                    "open_price": pos.price_open,
                    "current_price": pos.price_current,
                    "sl": pos.sl,
                    "tp": pos.tp,
                    "profit": pos.profit,
                    "comment": pos.comment,
                    "magic": pos.magic,
                    "time": datetime.fromtimestamp(pos.time)
                })
            
            return positions_list
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des positions: {e}")
            return []
    
    def close_all_positions(self) -> Dict:
        """
        Fermer toutes les positions ouvertes
        
        Returns:
            Dictionnaire avec le résultat
        """
        positions = self.get_open_positions()
        
        if not positions:
            logger.info("Aucune position à fermer")
            return {"success": True, "closed": 0}
        
        closed_count = 0
        errors = []
        
        for position in positions:
            result = self.close_position(position["ticket"])
            if result["success"]:
                closed_count += 1
            else:
                errors.append(f"Ticket {position['ticket']}: {result['error']}")
            
            time.sleep(0.5)  # Petit délai entre les ordres
        
        logger.info(f"{closed_count}/{len(positions)} positions fermées")
        
        return {
            "success": len(errors) == 0,
            "closed": closed_count,
            "total": len(positions),
            "errors": errors
        }
    
    def get_account_info(self) -> Optional[Dict]:
        """
        Obtenir les informations du compte
        
        Returns:
            Dictionnaire avec les informations du compte
        """
        try:
            account = mt5.account_info()
            if account is None:
                return None
            
            return {
                "balance": account.balance,
                "equity": account.equity,
                "margin": account.margin,
                "margin_free": account.margin_free,
                "margin_level": account.margin_level,
                "profit": account.profit,
                "currency": account.currency,
                "leverage": account.leverage,
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des infos compte: {e}")
            return None


# Exemple d'utilisation
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    from data.mt5_collector import MT5Collector
    
    # Se connecter à MT5
    collector = MT5Collector()
    if collector.connect():
        # Créer l'exécuteur d'ordres
        executor = OrderExecutor(collector)
        
        # Obtenir les infos du compte
        account_info = executor.get_account_info()
        if account_info:
            print("\n" + "="*60)
            print("INFORMATIONS DU COMPTE")
            print("="*60)
            print(f"Balance: ${account_info['balance']:.2f}")
            print(f"Equity: ${account_info['equity']:.2f}")
            print(f"Margin libre: ${account_info['margin_free']:.2f}")
            print(f"Profit: ${account_info['profit']:.2f}")
        
        # Obtenir les positions ouvertes
        positions = executor.get_open_positions()
        print(f"\nPositions ouvertes: {len(positions)}")
        for pos in positions:
            print(f"  - {pos['type']} {pos['volume']} lots @ {pos['open_price']:.2f} "
                  f"(Profit: ${pos['profit']:.2f})")
        
        # ATTENTION: Décommenter pour tester l'envoi d'ordre (en mode démo uniquement!)
        # result = executor.send_order(
        #     action="BUY",
        #     volume=0.01,
        #     stop_loss=2000.00,
        #     take_profit=2100.00,
        #     comment="Test order"
        # )
        # print(f"\nRésultat: {result}")
        
        collector.disconnect()

"""
Configuration MetaTrader 5
"""
import os
from dotenv import load_dotenv

# Charger les variables d'environnement depuis .env
load_dotenv()

# Configuration MT5
MT5_CONFIG = {
    "login": int(os.getenv("MT5_LOGIN", "0")),
    "password": os.getenv("MT5_PASSWORD", ""),
    "server": os.getenv("MT5_SERVER", ""),
    "path": os.getenv("MT5_PATH", ""),  # Chemin vers terminal64.exe (optionnel)
    "timeout": 60000,  # Timeout en millisecondes
    "portable": False  # Mode portable
}

# Paramètres de connexion
CONNECTION_PARAMS = {
    "retries": 3,           # Nombre de tentatives de reconnexion
    "retry_delay": 5,       # Délai entre les tentatives (secondes)
    "check_interval": 60,   # Vérification de la connexion (secondes)
}

# Paramètres des ordres
ORDER_PARAMS = {
    "magic_number": 234000,      # Numéro magique pour identifier les ordres
    "deviation": 20,             # Déviation maximale du prix (points)
    "type_filling": "FOK",       # Fill or Kill (ou "IOC" pour Immediate or Cancel)
    "comment": "AI_Trading_Bot", # Commentaire des ordres
}

# Mapping des timeframes MT5
import MetaTrader5 as mt5

MT5_TIMEFRAMES = {
    "M1": mt5.TIMEFRAME_M1,
    "M5": mt5.TIMEFRAME_M5,
    "M15": mt5.TIMEFRAME_M15,
    "M30": mt5.TIMEFRAME_M30,
    "H1": mt5.TIMEFRAME_H1,
    "H4": mt5.TIMEFRAME_H4,
    "D1": mt5.TIMEFRAME_D1,
}

# Types d'ordres MT5
ORDER_TYPES = {
    "BUY": mt5.ORDER_TYPE_BUY,
    "SELL": mt5.ORDER_TYPE_SELL,
    "BUY_LIMIT": mt5.ORDER_TYPE_BUY_LIMIT,
    "SELL_LIMIT": mt5.ORDER_TYPE_SELL_LIMIT,
    "BUY_STOP": mt5.ORDER_TYPE_BUY_STOP,
    "SELL_STOP": mt5.ORDER_TYPE_SELL_STOP,
}

# Vérification de la configuration
def validate_mt5_config():
    """Valider la configuration MT5"""
    if not MT5_CONFIG["login"] or MT5_CONFIG["login"] == 0:
        raise ValueError("MT5_LOGIN non configuré dans .env")
    if not MT5_CONFIG["password"]:
        raise ValueError("MT5_PASSWORD non configuré dans .env")
    if not MT5_CONFIG["server"]:
        raise ValueError("MT5_SERVER non configuré dans .env")
    return True

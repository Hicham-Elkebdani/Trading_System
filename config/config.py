"""
Configuration globale du système de trading
"""
import os
from pathlib import Path

# Chemins du projet
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data_storage"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
MODELS_DIR = DATA_DIR / "models"
LOGS_DIR = BASE_DIR / "logs"

# Créer les dossiers s'ils n'existent pas
for directory in [RAW_DATA_DIR, PROCESSED_DATA_DIR, MODELS_DIR, LOGS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Configuration Trading
SYMBOL = "XAUUSD"  # Or contre Dollar US
TIMEFRAME_MAP = {
    "M1": 1,    # 1 minute
    "M5": 5,    # 5 minutes
    "M15": 15,  # 15 minutes
    "M30": 30,  # 30 minutes
    "H1": 60,   # 1 heure
    "H4": 240,  # 4 heures
    "D1": 1440  # 1 jour
}
PRIMARY_TIMEFRAME = "H1"  # Timeframe principal pour le trading

# Configuration des données
START_DATE = "2020-01-01"  # Date de début pour données historiques
TRAIN_TEST_SPLIT = 0.8     # 80% train, 20% test
VALIDATION_SPLIT = 0.2     # 20% du train pour validation

# Configuration des features (indicateurs techniques)
FEATURE_CONFIG = {
    "SMA_periods": [20, 50, 200],        # Simple Moving Average
    "EMA_periods": [12, 26, 50],         # Exponential Moving Average
    "RSI_period": 14,                     # Relative Strength Index
    "MACD_fast": 12,                      # MACD Fast period
    "MACD_slow": 26,                      # MACD Slow period
    "MACD_signal": 9,                     # MACD Signal period
    "BB_period": 20,                      # Bollinger Bands period
    "BB_std": 2,                          # Bollinger Bands std deviation
    "ATR_period": 14,                     # Average True Range
    "ADX_period": 14,                     # Average Directional Index
    "Stochastic_k": 14,                   # Stochastic %K period
    "Stochastic_d": 3,                    # Stochastic %D period
}

# Configuration du modèle XGBoost
XGBOOST_CONFIG = {
    "n_estimators": 200,
    "max_depth": 7,
    "learning_rate": 0.01,
    "subsample": 0.8,
    "colsample_bytree": 0.8,
    "objective": "multi:softmax",  # Classification (BUY/SELL/HOLD)
    "num_class": 3,
    "random_state": 42,
    "n_jobs": -1
}

# Configuration du modèle LSTM
LSTM_CONFIG = {
    "sequence_length": 60,  # Nombre de pas de temps
    "lstm_units": [128, 64, 32],  # Unités par couche
    "dropout": 0.2,
    "epochs": 100,
    "batch_size": 32,
    "learning_rate": 0.001
}

# Configuration de la gestion du risque
RISK_CONFIG = {
    "max_risk_per_trade": 0.02,      # 2% du capital par trade
    "max_daily_loss": 0.06,          # 6% de perte maximale par jour
    "risk_reward_ratio": 2.0,        # Ratio risque/récompense (1:2)
    "stop_loss_pips": 50,            # Stop Loss en pips
    "take_profit_pips": 100,         # Take Profit en pips
    "trailing_stop": True,           # Utiliser trailing stop
    "trailing_stop_pips": 30,        # Trailing stop en pips
    "max_open_positions": 3,         # Nombre max de positions ouvertes
}

# Configuration des signaux de trading
SIGNAL_CONFIG = {
    "confidence_threshold": 0.65,    # Seuil de confiance minimum
    "min_probability_buy": 0.65,     # Probabilité min pour BUY
    "min_probability_sell": 0.65,    # Probabilité min pour SELL
    "use_trend_filter": True,        # Filtrer selon la tendance
    "use_volatility_filter": True,   # Filtrer selon la volatilité
}

# Configuration du backtesting
BACKTEST_CONFIG = {
    "initial_capital": 10000,        # Capital initial en USD
    "commission": 0.0003,            # Commission par trade (0.03%)
    "slippage": 0.0001,              # Slippage (0.01%)
    "leverage": 100,                 # Effet de levier
}

# Configuration du logging
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": LOGS_DIR / "trading_system.log",
    "max_bytes": 10485760,  # 10MB
    "backup_count": 5
}

# Labels pour la classification
LABELS = {
    0: "HOLD",
    1: "BUY",
    2: "SELL"
}

# Configuration des notifications (optionnel)
NOTIFICATION_CONFIG = {
    "enable_email": False,
    "enable_telegram": False,
    "notify_on_trade": True,
    "notify_on_error": True,
}

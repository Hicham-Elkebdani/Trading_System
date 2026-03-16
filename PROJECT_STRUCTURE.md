# Structure du Projet Gold Trading System

```
gold_trading_system/
│
├── config/
│   ├── __init__.py
│   ├── config.py              # Configuration globale (broker, timeframes, etc.)
│   └── mt5_config.py          # Configuration MT5 spécifique
│
├── data/
│   ├── __init__.py
│   ├── mt5_collector.py       # Collecte données depuis MT5
│   ├── data_manager.py        # Gestion et sauvegarde des données
│   └── data_validator.py      # Validation des données
│
├── features/
│   ├── __init__.py
│   ├── technical_indicators.py # Calcul des indicateurs (RSI, MACD, etc.)
│   ├── feature_engineering.py  # Création des features
│   └── feature_selector.py     # Sélection des meilleures features
│
├── models/
│   ├── __init__.py
│   ├── xgboost_model.py       # Modèle XGBoost
│   ├── lstm_model.py          # Modèle LSTM (optionnel)
│   ├── model_trainer.py       # Entraînement des modèles
│   └── model_evaluator.py     # Évaluation et métriques
│
├── trading/
│   ├── __init__.py
│   ├── signal_generator.py    # Génération des signaux BUY/SELL/HOLD
│   ├── risk_manager.py        # Gestion du risque (SL, TP)
│   ├── order_executor.py      # Exécution des ordres MT5
│   └── portfolio_manager.py   # Gestion du portfolio
│
├── backtesting/
│   ├── __init__.py
│   ├── backtest_engine.py     # Moteur de backtesting
│   └── performance_analyzer.py # Analyse des performances
│
├── utils/
│   ├── __init__.py
│   ├── logger.py              # Système de logging
│   ├── helpers.py             # Fonctions utilitaires
│   └── notifications.py       # Notifications (email, telegram)
│
├── data_storage/              # Données sauvegardées
│   ├── raw/                   # Données brutes MT5
│   ├── processed/             # Données avec features
│   └── models/                # Modèles entraînés sauvegardés
│
├── logs/                      # Fichiers de logs
│
├── notebooks/                 # Jupyter notebooks pour exploration
│   ├── 01_data_exploration.ipynb
│   ├── 02_feature_analysis.ipynb
│   └── 03_model_testing.ipynb
│
├── scripts/                   # Scripts d'exécution
│   ├── 01_collect_data.py
│   ├── 02_train_model.py
│   ├── 03_backtest.py
│   └── 04_live_trading.py
│
├── tests/                     # Tests unitaires
│   ├── test_data.py
│   ├── test_features.py
│   └── test_models.py
│
├── requirements.txt           # Dépendances Python
├── README.md                  # Documentation principale
└── .env                       # Variables d'environnement (MT5 credentials)
```

## Flux de Travail

1. **Phase de Développement:**
   - Collecter données historiques → data/
   - Feature engineering → features/
   - Entraîner modèles → models/
   - Backtesting → backtesting/

2. **Phase de Production:**
   - Collecte temps réel → data/
   - Génération signaux → trading/
   - Exécution ordres → trading/
   - Monitoring → logs/

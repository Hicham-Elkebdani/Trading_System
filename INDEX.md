# 📁 INDEX DU PROJET - Gold Trading System

## 🎯 Bienvenue dans votre Système de Trading IA!

Ce projet contient un système complet de trading algorithmique pour l'or (XAUUSD) basé sur l'intelligence artificielle.

---

## 📖 Documentation Principale

### 🚀 Pour Commencer (LISEZ DANS CET ORDRE)

1. **QUICKSTART.md** ⭐
   - Démarrage rapide en 5 étapes
   - Guide le plus court pour commencer

2. **README.md**
   - Vue d'ensemble complète du projet
   - Architecture et fonctionnalités

3. **GUIDE_UTILISATION.md**
   - Guide détaillé étape par étape
   - Explication de chaque composant
   - Troubleshooting

4. **BEST_PRACTICES.md**
   - Bonnes pratiques à suivre
   - Erreurs à éviter
   - Optimisations avancées

5. **PROJECT_STRUCTURE.md**
   - Architecture détaillée du projet
   - Structure des dossiers

---

## 🗂️ Structure du Projet

```
gold_trading_system/
│
├── 📄 QUICKSTART.md              ⭐ COMMENCEZ ICI!
├── 📄 README.md                  Documentation principale
├── 📄 GUIDE_UTILISATION.md       Guide détaillé
├── 📄 BEST_PRACTICES.md          Bonnes pratiques
├── 📄 PROJECT_STRUCTURE.md       Architecture
├── 📄 requirements.txt           Dépendances Python
├── 📄 .env.example               Template de configuration
│
├── 📁 config/                    Configuration du système
│   ├── config.py                 Configuration générale
│   └── mt5_config.py             Configuration MT5
│
├── 📁 data/                      Gestion des données
│   ├── mt5_collector.py          Collecte depuis MT5
│   └── data_manager.py           Sauvegarde et chargement
│
├── 📁 features/                  Feature engineering
│   ├── technical_indicators.py   Indicateurs techniques
│   └── feature_engineering.py    Création des features
│
├── 📁 models/                    Modèles de Machine Learning
│   └── xgboost_model.py          Modèle XGBoost
│
├── 📁 trading/                   Système de trading
│   ├── signal_generator.py       Génération de signaux
│   ├── risk_manager.py           Gestion du risque
│   └── order_executor.py         Exécution des ordres
│
├── 📁 scripts/                   Scripts d'exécution
│   ├── 01_collect_data.py        Collecte des données
│   ├── 02_train_model.py         Entraînement du modèle
│   ├── 03_backtest.py            Backtesting
│   └── 04_live_trading.py        Trading en temps réel
│
├── 📁 backtesting/               Module de backtesting
├── 📁 utils/                     Utilitaires
├── 📁 tests/                     Tests unitaires
├── 📁 notebooks/                 Jupyter notebooks
│
├── 📁 data_storage/              Données et modèles (créé automatiquement)
│   ├── raw/                      Données brutes
│   ├── processed/                Données traitées
│   └── models/                   Modèles sauvegardés
│
└── 📁 logs/                      Fichiers de logs (créé automatiquement)
```

---

## 🚦 Workflow d'Utilisation

### Phase 1: Installation et Configuration

1. Installer Python 3.10+
2. Installer MetaTrader 5
3. Créer un compte DÉMO MT5
4. Configurer le fichier `.env`
5. Installer les dépendances: `pip install -r requirements.txt`

**📖 Voir: QUICKSTART.md - Étape 1**

---

### Phase 2: Collecte et Préparation des Données

```bash
python scripts/01_collect_data.py
```

**Ce script fait:**
- Se connecte à MT5
- Récupère l'historique XAUUSD
- Nettoie les données
- Sauvegarde dans `data_storage/raw/`

**📖 Voir: GUIDE_UTILISATION.md - Section 3**

---

### Phase 3: Entraînement du Modèle

```bash
python scripts/02_train_model.py
```

**Ce script fait:**
- Charge les données historiques
- Calcule les indicateurs techniques
- Crée les features et labels
- Entraîne XGBoost
- Évalue les performances
- Sauvegarde le modèle

**📖 Voir: GUIDE_UTILISATION.md - Section 4**

---

### Phase 4: Backtesting

```bash
python scripts/03_backtest.py
```

**Ce script fait:**
- Teste le modèle sur données passées
- Simule les trades
- Calcule les métriques de performance
- Génère un rapport

**📖 Voir: GUIDE_UTILISATION.md - Section 5**

---

### Phase 5: Trading en Temps Réel

```bash
python scripts/04_live_trading.py
```

**⚠️ ATTENTION: Compte DÉMO uniquement!**

**Ce script fait:**
- Analyse le marché en continu
- Génère des signaux BUY/SELL/HOLD
- Exécute les ordres automatiquement
- Gère les positions (SL/TP)

**📖 Voir: GUIDE_UTILISATION.md - Section 6**

---

## 🎓 Guide d'Apprentissage

### Pour les Débutants

1. **Jour 1-2**: Lire QUICKSTART.md et README.md
2. **Jour 3-5**: Installation et collecte de données
3. **Jour 6-7**: Entraînement du premier modèle
4. **Semaine 2**: Backtesting et analyse
5. **Semaine 3-4**: Tests sur compte démo
6. **Mois 2+**: Optimisation et amélioration

### Pour les Développeurs Expérimentés

1. **Jour 1**: Setup complet et premier run
2. **Jour 2-3**: Analyse du code et architecture
3. **Semaine 1**: Personnalisation et optimisation
4. **Semaine 2+**: Features avancées et production

---

## 📊 Modules Principaux

### 1. Configuration (`config/`)

- `config.py`: Paramètres généraux (symbole, timeframe, risque)
- `mt5_config.py`: Configuration MT5 spécifique

**Fichiers clés à éditer:**
- `.env`: Identifiants MT5
- `config.py`: RISK_CONFIG, FEATURE_CONFIG, etc.

---

### 2. Données (`data/`)

**Classes principales:**
- `MT5Collector`: Connexion et collecte MT5
- `DataManager`: Gestion et sauvegarde

**Méthodes importantes:**
- `connect()`: Connexion à MT5
- `get_historical_data()`: Récupérer l'historique
- `save_raw_data()`: Sauvegarder les données

---

### 3. Features (`features/`)

**Classes principales:**
- `TechnicalIndicators`: Calcul des indicateurs
- `FeatureEngineer`: Feature engineering complet

**Indicateurs disponibles:**
- RSI, MACD, SMA, EMA
- Bollinger Bands, ATR, ADX
- Stochastic, CCI, Williams %R
- Et plus de 50 features au total!

---

### 4. Modèles (`models/`)

**Classes principales:**
- `XGBoostModel`: Modèle de classification

**Méthodes importantes:**
- `train()`: Entraîner le modèle
- `predict()`: Faire une prédiction
- `evaluate()`: Évaluer les performances
- `save()`/`load()`: Sauvegarder/charger

---

### 5. Trading (`trading/`)

**Classes principales:**
- `SignalGenerator`: Génération de signaux
- `RiskManager`: Gestion du risque
- `OrderExecutor`: Exécution des ordres

**Fonctionnalités:**
- Calcul automatique du Stop Loss
- Calcul automatique du Take Profit
- Position sizing adaptatif
- Trailing stop
- Validation des signaux

---

## 🔧 Configuration Recommandée

### Pour Débuter (Conservateur)

```python
RISK_CONFIG = {
    "max_risk_per_trade": 0.01,      # 1%
    "max_daily_loss": 0.03,           # 3%
    "stop_loss_pips": 30,
    "take_profit_pips": 60,
    "max_open_positions": 1,
}

SIGNAL_CONFIG = {
    "confidence_threshold": 0.70,     # 70%
    "use_trend_filter": True,
    "use_volatility_filter": True,
}
```

### Pour Utilisateurs Avancés (Équilibré)

```python
RISK_CONFIG = {
    "max_risk_per_trade": 0.02,      # 2%
    "max_daily_loss": 0.05,           # 5%
    "risk_reward_ratio": 2.0,         # 1:2
    "trailing_stop": True,
    "max_open_positions": 2,
}

SIGNAL_CONFIG = {
    "confidence_threshold": 0.65,     # 65%
    "use_trend_filter": True,
    "use_volatility_filter": True,
}
```

---

## ⚠️ Checklist de Sécurité

Avant de lancer le système:

- [ ] ✅ Compte DÉMO MT5 configuré
- [ ] ✅ Fichier `.env` rempli correctement
- [ ] ✅ Dépendances installées: `pip install -r requirements.txt`
- [ ] ✅ Données collectées: `01_collect_data.py` exécuté
- [ ] ✅ Modèle entraîné: `02_train_model.py` exécuté
- [ ] ✅ Backtesting validé: Win rate > 50%
- [ ] ✅ Documentation lue: QUICKSTART.md, README.md
- [ ] ✅ Bonnes pratiques comprises: BEST_PRACTICES.md
- [ ] ✅ Paramètres de risque vérifiés
- [ ] ✅ Capital dédié défini (argent qu'on peut perdre)

---

## 📞 Aide et Support

### En cas de problème

1. **Consulter les logs:**
   - `logs/data_collection.log`
   - `logs/model_training.log`
   - `logs/live_trading.log`

2. **Vérifier la documentation:**
   - GUIDE_UTILISATION.md - Section 9 (Troubleshooting)
   - BEST_PRACTICES.md - Section 9 (Troubleshooting)

3. **Problèmes courants:**
   - Connexion MT5: Vérifier `.env` et que MT5 est ouvert
   - Pas de données: Vérifier le symbole et le serveur
   - Modèle peu performant: Plus de données ou ajuster les paramètres
   - Ordres rejetés: Vérifier le margin et les paramètres

---

## 🎯 Objectifs du Projet

### Objectifs Académiques (PFE)

- ✅ Comprendre le trading algorithmique
- ✅ Maîtriser le Machine Learning appliqué à la finance
- ✅ Intégrer une API de trading (MT5)
- ✅ Gérer un projet complet de A à Z
- ✅ Documenter professionnellement

### Objectifs Techniques

- ✅ Pipeline de données complet
- ✅ Feature engineering avancé
- ✅ Modèle ML performant (XGBoost)
- ✅ Gestion du risque robuste
- ✅ Système de trading automatisé

### Objectifs de Performance

- 🎯 Win Rate: > 55%
- 🎯 Profit Factor: > 1.5
- 🎯 Sharpe Ratio: > 1.0
- 🎯 Max Drawdown: < 15%
- 🎯 ROI annuel: > 20%

---

## 🌟 Fonctionnalités Clés

### ✅ Implémenté

- Collecte de données MT5
- Feature engineering (50+ indicateurs)
- Modèle XGBoost
- Gestion du risque avancée
- Exécution automatique des ordres
- Backtesting
- Logging complet
- Documentation extensive

### 🔄 Améliorations Possibles

- Modèle LSTM (Deep Learning)
- Multi-timeframe analysis
- Ensemble de modèles
- Optimisation des hyperparamètres (Grid Search)
- Dashboard de monitoring
- Notifications (Email, Telegram)
- Multi-symbole trading
- Sentiment analysis (news)

---

## 📚 Ressources Additionnelles

### Documentation Externe

- **MetaTrader 5**: https://www.metatrader5.com/en/terminal/help
- **XGBoost**: https://xgboost.readthedocs.io/
- **Scikit-learn**: https://scikit-learn.org/stable/
- **Pandas**: https://pandas.pydata.org/docs/

### Apprentissage

- **Trading**: BabyPips.com, Investopedia
- **Machine Learning**: Kaggle, Coursera
- **Python**: Real Python, Python.org

---

## 🎉 Félicitations!

Vous avez maintenant accès à un système de trading algorithmique professionnel et complet!

### Prochaines Actions

1. **Immédiat**: Lire QUICKSTART.md
2. **Aujourd'hui**: Installer et configurer
3. **Cette semaine**: Premier modèle et backtesting
4. **Ce mois**: Tests sur compte démo

---

## ⚖️ Avertissement Légal

Ce système est fourni à des fins éducatives dans le cadre d'un projet universitaire.

- Le trading comporte des risques de perte en capital
- Les performances passées ne garantissent pas les résultats futurs
- Utilisez à vos propres risques
- Consultez un conseiller financier professionnel
- Testez TOUJOURS sur compte démo d'abord

---

## 📝 Licence

Ce projet est développé dans le cadre d'un PFE (Projet de Fin d'Études).

---

## 👨‍💻 Contribution

Pour améliorer ce projet:
1. Testez et documentez vos modifications
2. Partagez vos résultats
3. Proposez des améliorations

---

**Bonne chance avec votre système de trading! 🚀📈**

*Développé avec passion pour l'apprentissage et l'innovation en finance algorithmique.*

---

**Dernière mise à jour**: 2024-01-27
**Version**: 1.0.0
**Statut**: Production Ready (Démo)

# Gold Trading System - Système de Trading Automatique IA

Système de trading automatique basé sur l'intelligence artificielle pour le marché de l'or (XAUUSD)
## 📋 Table des Matières

- [Vue d'ensemble](#vue-densemble)
- [Architecture](#architecture)
- [Installation](#installation)
- [Configuration](#configuration)
- [Utilisation](#utilisation)
- [Modules](#modules)
- [Workflow](#workflow)
- [Sécurité](#sécurité)
- [Résultats](#résultats)

## 🎯 Vue d'ensemble

Ce système utilise le Machine Learning (XGBoost) pour prédire les mouvements du prix de l'or et exécuter automatiquement des trades via MetaTrader 5.

### Fonctionnalités principales

- ✅ Collecte automatique des données depuis MT5
- ✅ Feature engineering avec indicateurs techniques (RSI, MACD, SMA, etc.)
- ✅ Modèle XGBoost pour la prédiction (BUY/SELL/HOLD)
- ✅ Gestion avancée du risque (Stop Loss, Take Profit, position sizing)
- ✅ Exécution automatique des ordres via MT5
- ✅ Backtesting sur données historiques
- ✅ Trading en temps réel
- ✅ Logging et monitoring complets

## 🏗️ Architecture

```
Données MT5 → Feature Engineering → Modèle ML → Signaux → Gestion Risque → Exécution
```

### Technologies utilisées

- **Python 3.10+**
- **MetaTrader 5** (source de données + exécution)
- **XGBoost** (Machine Learning)
- **Pandas** (manipulation de données)
- **Scikit-learn** (preprocessing, métriques)
- **TensorFlow/Keras** (optionnel, pour LSTM)

## 💻 Installation

### Prérequis

1. **Python 3.10 ou supérieur**
2. **MetaTrader 5 Desktop** installé et configuré
3. **Compte de trading** (DÉMO recommandé pour les tests)

### Étapes d'installation

```bash
# 1. Cloner le repository
git clone <url-du-repo>
cd gold_trading_system

# 2. Créer un environnement virtuel
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Créer le fichier .env
cp .env.example .env
# Éditer .env avec vos identifiants MT5
```

## ⚙️ Configuration

### 1. Configuration MT5

Éditez le fichier `.env`:

```env
MT5_LOGIN=12345678
MT5_PASSWORD=votre_mot_de_passe
MT5_SERVER=NomDuServeur-Demo
MT5_PATH=
```

### 2. Configuration du système

Les paramètres principaux sont dans `config/config.py`:

- **SYMBOL**: Symbole à trader (XAUUSD par défaut)
- **PRIMARY_TIMEFRAME**: Période temporelle (H1 par défaut)
- **RISK_CONFIG**: Paramètres de gestion du risque
- **FEATURE_CONFIG**: Configuration des indicateurs techniques

## 🚀 Utilisation

### Workflow complet

```bash
# 1. Collecter les données historiques
python scripts/01_collect_data.py

# 2. Entraîner le modèle
python scripts/02_train_model.py

# 3. Backtesting (optionnel)
python scripts/03_backtest.py

# 4. Trading en temps réel
python scripts/04_live_trading.py
```

### Détails de chaque étape

#### 1. Collecte des données

```bash
python scripts/01_collect_data.py
```

- Récupère les données OHLC depuis MT5
- Nettoie et valide les données
- Sauvegarde dans `data_storage/raw/`

#### 2. Entraînement du modèle

```bash
python scripts/02_train_model.py
```

- Charge les données historiques
- Calcule les indicateurs techniques
- Crée les labels (BUY/SELL/HOLD)
- Entraîne le modèle XGBoost
- Sauvegarde le modèle dans `data_storage/models/`

#### 3. Backtesting

```bash
python scripts/03_backtest.py
```

- Teste le modèle sur données historiques
- Génère des métriques de performance
- Affiche les résultats (win rate, profit, drawdown)

#### 4. Trading en temps réel

```bash
python scripts/04_live_trading.py
```

⚠️ **ATTENTION**: Ce script effectue de vrais trades!

- Analyse le marché en continu
- Génère des signaux de trading
- Exécute automatiquement les ordres
- Gère les positions (trailing stop)

## 📦 Modules

### data/
- `mt5_collector.py`: Connexion et collecte de données MT5
- `data_manager.py`: Gestion et sauvegarde des données

### features/
- `technical_indicators.py`: Calcul des indicateurs (RSI, MACD, etc.)
- `feature_engineering.py`: Création des features pour le ML

### models/
- `xgboost_model.py`: Modèle XGBoost pour la classification
- `lstm_model.py`: Modèle LSTM (optionnel)

### trading/
- `signal_generator.py`: Génération des signaux BUY/SELL/HOLD
- `risk_manager.py`: Gestion du risque (SL, TP, position sizing)
- `order_executor.py`: Exécution des ordres via MT5

### backtesting/
- `backtest_engine.py`: Moteur de backtesting
- `performance_analyzer.py`: Analyse des performances

## 📊 Workflow détaillé

### 1. Pipeline de données

```
MT5 → Données brutes → Nettoyage → Indicateurs techniques → Features → Labels
```

### 2. Pipeline ML

```
Features + Labels → Train/Test Split → Normalisation → Entraînement → Évaluation → Sauvegarde
```

### 3. Pipeline de trading

```
Données temps réel → Features → Prédiction → Signal → Validation → Risque → Exécution
```

## 🔒 Sécurité

### Règles de sécurité

1. **TOUJOURS** tester sur un compte démo d'abord
2. **NE JAMAIS** partager vos identifiants MT5
3. **VÉRIFIER** les paramètres de risque avant le live trading
4. **MONITORER** le système en continu
5. **LIMITER** le risque par trade (2% max recommandé)

### Gestion du risque

- **Stop Loss automatique** sur chaque position
- **Take Profit** basé sur le ratio risque/récompense
- **Position sizing** adaptatif selon le capital
- **Limite de perte quotidienne**
- **Nombre maximum de positions ouvertes**
- **Trailing stop** optionnel

## 📈 Résultats attendus

### Métriques du modèle

- **Accuracy**: Précision globale de la classification
- **Precision/Recall**: Pour chaque classe (BUY/SELL/HOLD)
- **F1-Score**: Équilibre entre précision et rappel
- **Matrice de confusion**: Distribution des prédictions

### Métriques de trading

- **Win Rate**: Pourcentage de trades gagnants
- **Profit Factor**: Ratio gains/pertes
- **Sharpe Ratio**: Ratio rendement/risque
- **Maximum Drawdown**: Perte maximale depuis un pic
- **Average Trade**: Gain/perte moyen par trade

## 🐛 Dépannage

### Problèmes courants

**1. Erreur de connexion MT5**
- Vérifier que MT5 est ouvert
- Vérifier les identifiants dans `.env`
- Vérifier le serveur (Démo vs Réel)

**2. Données non disponibles**
- Vérifier que le symbole XAUUSD est actif
- Vérifier la connexion internet
- Essayer un autre timeframe

**3. Erreur lors de l'entraînement**
- Vérifier qu'il y a assez de données (min 1000 barres)
- Vérifier les dépendances Python
- Consulter les logs dans `logs/`

**4. Ordres rejetés**
- Vérifier le solde du compte
- Vérifier le margin disponible
- Vérifier les heures de trading
- Vérifier la taille de position (min/max volume)

## 📚 Documentation

### Structure du projet

Voir `PROJECT_STRUCTURE.md` pour la structure détaillée.

### Configuration avancée

Tous les paramètres configurables sont dans:
- `config/config.py`: Configuration générale
- `config/mt5_config.py`: Configuration MT5

### Logs

Les logs sont sauvegardés dans `logs/`:
- `data_collection.log`: Collecte de données
- `model_training.log`: Entraînement du modèle
- `live_trading.log`: Trading en temps réel


## ⚠️ Avertissements

- Le trading comporte des risques de perte en capital
- Ce système est fourni à titre éducatif
- Les performances passées ne garantissent pas les résultats futurs
- Utilisez toujours un compte démo pour tester
- Consultez un conseiller financier avant le trading réel



**Note importante**: Ce système est un outil d'aide à la décision. La décision finale de trading revient toujours à l'utilisateur. Tradez de manière responsable.

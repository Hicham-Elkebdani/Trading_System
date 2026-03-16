# Guide d'Utilisation - Gold Trading System

Ce guide vous accompagne pas à pas dans l'utilisation du système de trading automatique.

## 📋 Table des Matières

1. [Installation initiale](#installation-initiale)
2. [Configuration](#configuration)
3. [Collecte des données](#collecte-des-données)
4. [Entraînement du modèle](#entraînement-du-modèle)
5. [Backtesting](#backtesting)
6. [Trading en temps réel](#trading-en-temps-réel)
7. [Monitoring et maintenance](#monitoring-et-maintenance)
8. [Optimisation](#optimisation)
9. [Troubleshooting](#troubleshooting)

---

## 1. Installation initiale

### Étape 1.1: Prérequis système

Avant de commencer, assurez-vous d'avoir:

- ✅ **Windows 10/11** (pour MT5)
- ✅ **Python 3.10+** installé
- ✅ **MetaTrader 5** installé
- ✅ **Git** (optionnel mais recommandé)
- ✅ **8 GB RAM** minimum
- ✅ **10 GB d'espace disque**

### Étape 1.2: Installation de Python

```bash
# Vérifier la version de Python
python --version

# Si Python n'est pas installé, téléchargez-le depuis:
# https://www.python.org/downloads/
```

### Étape 1.3: Installation de MetaTrader 5

1. Téléchargez MT5 depuis: https://www.metatrader5.com/
2. Installez et ouvrez MT5
3. Créez un compte **DÉMO** (très important pour les tests!)
4. Notez vos identifiants: Login, Password, Server

### Étape 1.4: Téléchargement du projet

```bash
# Option 1: Avec Git
git clone <url-du-repo>
cd gold_trading_system

# Option 2: Téléchargement ZIP
# Décompressez le fichier ZIP
# Ouvrez un terminal dans le dossier
```

### Étape 1.5: Environnement virtuel

```bash
# Créer l'environnement virtuel
python -m venv venv

# Activer l'environnement
# Windows:
venv\Scripts\activate

# Linux/Mac:
source venv/bin/activate

# Votre prompt devrait maintenant afficher (venv)
```

### Étape 1.6: Installation des dépendances

```bash
# Installer toutes les dépendances
pip install -r requirements.txt

# Vérifier l'installation
pip list | grep MetaTrader5
pip list | grep xgboost
```

---

## 2. Configuration

### Étape 2.1: Configuration MT5

```bash
# Copier le fichier d'exemple
cp .env.example .env

# Éditer le fichier .env (avec notepad, VS Code, etc.)
notepad .env
```

Remplissez avec vos identifiants MT5 DÉMO:

```env
MT5_LOGIN=12345678
MT5_PASSWORD=YourPassword123
MT5_SERVER=MetaQuotes-Demo
MT5_PATH=
```

### Étape 2.2: Vérification de la connexion MT5

```bash
# Tester la connexion
python -c "from data.mt5_collector import MT5Collector; c = MT5Collector(); print('Connexion:', c.connect())"
```

Résultat attendu:
```
Connexion MT5 établie - Compte: 12345678
Connexion: True
```

### Étape 2.3: Configuration des paramètres de trading

Éditez `config/config.py` pour ajuster:

- **SYMBOL**: "XAUUSD" (par défaut, or vs dollar)
- **PRIMARY_TIMEFRAME**: "H1" (1 heure, recommandé)
- **RISK_CONFIG**: Paramètres de risque

Exemple de configuration conservatrice:

```python
RISK_CONFIG = {
    "max_risk_per_trade": 0.01,      # 1% du capital par trade
    "max_daily_loss": 0.03,          # 3% de perte maximale par jour
    "stop_loss_pips": 30,            # Stop Loss de 30 pips
    "take_profit_pips": 60,          # Take Profit de 60 pips
    "max_open_positions": 2,         # Max 2 positions simultanées
}
```

---

## 3. Collecte des données

### Étape 3.1: Première collecte

```bash
python scripts/01_collect_data.py
```

**Ce que le script fait:**
1. Se connecte à MT5
2. Récupère les données historiques de XAUUSD depuis 2020
3. Nettoie les données (supprime doublons, valeurs manquantes)
4. Sauvegarde dans `data_storage/raw/`

**Sortie attendue:**
```
Connexion à MetaTrader 5...
Connexion MT5 établie - Compte: 12345678
Récupération des données depuis 2020-01-01...
Données récupérées: 35000 barres
Nettoyage des données...
Données sauvegardées: data_storage/raw/XAUUSD_H1_historical_20240127_123456.csv
COLLECTE TERMINÉE AVEC SUCCÈS
```

### Étape 3.2: Vérification des données

```python
import pandas as pd

# Charger les données
df = pd.read_csv('data_storage/raw/XAUUSD_H1_historical_<timestamp>.csv')

print(f"Nombre de lignes: {len(df)}")
print(f"Période: {df['time'].min()} à {df['time'].max()}")
print(f"\nAperçu des données:")
print(df.head())
```

---

## 4. Entraînement du modèle

### Étape 4.1: Lancer l'entraînement

```bash
python scripts/02_train_model.py
```

**Ce que le script fait:**
1. Charge les données historiques
2. Calcule 50+ indicateurs techniques (RSI, MACD, SMA, etc.)
3. Crée les labels (BUY/SELL/HOLD)
4. Entraîne le modèle XGBoost
5. Évalue les performances
6. Sauvegarde le modèle

**Durée estimée:** 5-15 minutes selon la quantité de données

**Sortie attendue:**
```
Création des features...
Features créées: 65 colonnes
Création des labels...
Distribution des labels:
0 (HOLD): 15000 (43%)
1 (BUY): 10000 (29%)
2 (SELL): 10000 (28%)

Entraînement du modèle XGBoost...
Train set: 28000 échantillons
Test set: 7000 échantillons

Évaluation du modèle...
Accuracy: 0.6234
Precision: 0.6102
Recall: 0.6234
F1-Score: 0.6145

Top features:
  RSI: 0.089
  MACD: 0.076
  ATR_pct: 0.065
  ...

Modèle sauvegardé: xgboost_model_H1_latest
```

### Étape 4.2: Analyse des résultats

Ouvrez `logs/model_training.log` pour voir les détails:

```bash
notepad logs\model_training.log
```

Points à vérifier:
- **Accuracy > 55%**: Performance acceptable
- **F1-Score équilibré**: Pas de biais vers une classe
- **Features importantes**: RSI, MACD, ATR doivent figurer dans le top 10

---

## 5. Backtesting

### Étape 5.1: Lancer le backtesting

```bash
python scripts/03_backtest.py
```

**Ce que le script fait:**
1. Charge le modèle entraîné
2. Simule des trades sur données historiques
3. Applique la gestion du risque
4. Calcule les performances

**Sortie attendue:**
```
RÉSULTATS DU BACKTESTING
========================
Période: 2024-01-01 à 2024-12-31
Capital initial: $10,000
Capital final: $12,345

Nombre de trades: 150
Trades gagnants: 85 (57%)
Trades perdants: 65 (43%)

Profit total: $2,345 (23.45%)
Perte totale: $1,234
Profit net: $1,111

Profit moyen: $27.58
Perte moyenne: $-18.98

Profit factor: 1.90
Sharpe ratio: 1.45
Max drawdown: -8.5%

Meilleur trade: +$250
Pire trade: -$95
```

### Étape 5.2: Analyse des résultats

**Métriques clés:**

- **Win Rate > 50%**: Bon
- **Profit Factor > 1.5**: Acceptable
- **Sharpe Ratio > 1.0**: Bon ratio risque/rendement
- **Max Drawdown < 15%**: Risque maîtrisé

**Si les résultats ne sont pas satisfaisants:**
- Ajustez les paramètres de risque dans `config/config.py`
- Essayez différents timeframes
- Collectez plus de données historiques
- Optimisez les hyperparamètres du modèle

---

## 6. Trading en temps réel

### ⚠️ AVERTISSEMENT IMPORTANT

**LISEZ ATTENTIVEMENT AVANT DE CONTINUER:**

1. ✅ **Utilisez UNIQUEMENT un compte DÉMO pour commencer**
2. ✅ **Vérifiez TOUS les paramètres de risque**
3. ✅ **Testez pendant au moins 1 mois en DÉMO**
4. ✅ **Surveillez le système en permanence**
5. ❌ **NE JAMAIS utiliser un compte réel sans tests approfondis**

### Étape 6.1: Préparation

1. **Vérifier MT5:**
   - MT5 est ouvert
   - Connecté au compte DÉMO
   - XAUUSD est visible dans les symboles

2. **Vérifier le modèle:**
   ```bash
   # Le fichier doit exister
   ls data_storage/models/xgboost_model_H1_latest.json
   ```

3. **Vérifier les paramètres de risque:**
   ```python
   # Ouvrir config/config.py et vérifier RISK_CONFIG
   notepad config\config.py
   ```

### Étape 6.2: Lancer le bot

```bash
python scripts/04_live_trading.py
```

**Le système vous demandera confirmation:**
```
ATTENTION: Trading en temps réel activé!
Assurez-vous d'utiliser un compte DÉMO pour les tests.

Voulez-vous démarrer le bot de trading? (oui/non):
```

Tapez `oui` pour continuer.

### Étape 6.3: Surveillance du bot

**Le bot affichera:**
```
DÉMARRAGE DU BOT DE TRADING
============================

Status: 2024-01-27 14:30:00
Balance: $10,000.00
Equity: $10,000.00
Profit: $0.00

Analyse du marché...
Signal: HOLD (confiance: 0.550)
Prochaine vérification dans 60s...

Status: 2024-01-27 14:31:00
Balance: $10,000.00
Equity: $10,000.00
Profit: $0.00

Analyse du marché...
Signal: BUY (confiance: 0.782)
Envoi de l'ordre BUY...
Position size calculée: 0.05 lots
Stop Loss calculé: 2045.30
Take Profit calculé: 2055.70
✓ Trade exécuté: BUY 0.05 lots
  Prix: 2050.50
  SL: 2045.30, TP: 2055.70
  Ticket: 123456789
```

### Étape 6.4: Arrêt du bot

Pour arrêter le bot proprement:
- Appuyez sur `Ctrl+C`
- Le bot fermera toutes les connexions
- Les positions resteront ouvertes (les fermer manuellement si nécessaire)

---

## 7. Monitoring et maintenance

### Étape 7.1: Consulter les logs

```bash
# Logs de trading en temps réel
notepad logs\live_trading.log

# Logs d'entraînement
notepad logs\model_training.log

# Logs de collecte
notepad logs\data_collection.log
```

### Étape 7.2: Surveillance des performances

**Vérifications quotidiennes:**

1. **Balance du compte:**
   ```python
   from data.mt5_collector import MT5Collector
   from trading.order_executor import OrderExecutor
   
   collector = MT5Collector()
   collector.connect()
   executor = OrderExecutor(collector)
   
   account = executor.get_account_info()
   print(f"Balance: ${account['balance']:.2f}")
   print(f"Profit: ${account['profit']:.2f}")
   
   collector.disconnect()
   ```

2. **Positions ouvertes:**
   ```python
   positions = executor.get_open_positions()
   for pos in positions:
       print(f"{pos['type']} {pos['volume']} lots @ {pos['open_price']:.2f}")
       print(f"  Profit: ${pos['profit']:.2f}")
   ```

3. **Logs d'erreurs:**
   ```bash
   # Rechercher les erreurs dans les logs
   grep ERROR logs\live_trading.log
   ```

### Étape 7.3: Maintenance hebdomadaire

**Chaque semaine:**

1. **Réentraîner le modèle:**
   ```bash
   python scripts/01_collect_data.py
   python scripts/02_train_model.py
   ```

2. **Analyser les performances:**
   - Calculer le win rate de la semaine
   - Vérifier le profit factor
   - Analyser les trades perdants

3. **Ajuster les paramètres:**
   - Si win rate < 45%, augmenter le seuil de confiance
   - Si trop peu de trades, diminuer les seuils
   - Ajuster le stop loss selon la volatilité

---

## 8. Optimisation

### Étape 8.1: Optimisation des hyperparamètres

Pour améliorer les performances du modèle:

```python
# Éditer config/config.py

XGBOOST_CONFIG = {
    "n_estimators": 300,      # Augmenter pour plus de précision
    "max_depth": 8,           # Augmenter prudemment
    "learning_rate": 0.008,   # Diminuer pour plus de stabilité
    # ...
}
```

### Étape 8.2: Optimisation des features

1. **Analyser l'importance des features:**
   - Regarder le fichier `model_training.log`
   - Identifier les features les plus importantes

2. **Ajouter de nouvelles features:**
   - Éditer `features/feature_engineering.py`
   - Ajouter des indicateurs personnalisés

3. **Supprimer les features inutiles:**
   - Features avec importance < 0.001
   - Features corrélées

### Étape 8.3: Optimisation du risque

```python
# config/config.py

# Configuration agressive (plus de risque, plus de profit potentiel)
RISK_CONFIG = {
    "max_risk_per_trade": 0.03,    # 3%
    "risk_reward_ratio": 2.5,      # 1:2.5
}

# Configuration conservatrice (moins de risque, plus stable)
RISK_CONFIG = {
    "max_risk_per_trade": 0.01,    # 1%
    "risk_reward_ratio": 3.0,      # 1:3
    "max_open_positions": 1,       # 1 seule position
}
```

---

## 9. Troubleshooting

### Problème 1: Erreur de connexion MT5

**Symptôme:**
```
Erreur: Échec d'initialisation MT5
```

**Solutions:**
1. Vérifier que MT5 est ouvert
2. Vérifier les identifiants dans `.env`
3. Vérifier que le serveur est correct (Démo vs Réel)
4. Redémarrer MT5
5. Vérifier la connexion internet

### Problème 2: Pas de données récupérées

**Symptôme:**
```
Aucune donnée récupérée: <error>
```

**Solutions:**
1. Vérifier que XAUUSD est actif dans MT5
2. Essayer un autre timeframe (M5, M15, H4)
3. Vérifier les dates (start_date trop ancien)
4. Vérifier le symbole (peut être GOLD ou XAUUSD selon le broker)

### Problème 3: Modèle peu performant

**Symptôme:**
```
Accuracy: 0.45 (inférieur à 50%)
```

**Solutions:**
1. Collecter plus de données (> 10,000 barres)
2. Ajuster le threshold des labels
3. Équilibrer les classes (SMOTE, undersampling)
4. Essayer un autre timeframe
5. Ajouter plus de features
6. Optimiser les hyperparamètres

### Problème 4: Ordres rejetés

**Symptôme:**
```
Échec de l'ordre: Invalid stops
```

**Solutions:**
1. Vérifier le stop loss (trop proche du prix)
2. Vérifier le margin disponible
3. Vérifier la taille de position (min/max volume)
4. Vérifier les horaires de trading
5. Contacter le broker (peut avoir des restrictions)

### Problème 5: Bot qui plante

**Symptôme:**
```
Exception: Connection lost
```

**Solutions:**
1. Vérifier la stabilité de la connexion internet
2. Vérifier que MT5 ne s'est pas déconnecté
3. Ajouter un système de reconnexion automatique
4. Vérifier les logs pour l'erreur exacte

---

## 📞 Support

Pour toute question ou problème:

1. Consultez d'abord ce guide
2. Vérifiez les logs dans `logs/`
3. Consultez le README.md
4. Ouvrez une issue sur GitHub
5. Contactez les développeurs

---

## ✅ Checklist de démarrage

Avant de lancer le bot en réel, vérifiez:

- [ ] Testé sur compte DÉMO pendant au moins 1 mois
- [ ] Win rate > 50% sur le backtest
- [ ] Profit factor > 1.5
- [ ] Max drawdown < 15%
- [ ] Paramètres de risque vérifiés et compris
- [ ] Système de monitoring en place
- [ ] Budget de trading défini (argent que vous pouvez perdre)
- [ ] Stratégie de sortie définie
- [ ] Comprendre tous les risques
- [ ] Conseiller financier consulté (recommandé)

---

**Bon trading! 🚀**

*N'oubliez pas: Le trading comporte des risques. Ne tradez que l'argent que vous pouvez vous permettre de perdre.*

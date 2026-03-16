# 🚀 Quick Start Guide - Gold Trading System

## Démarrage Rapide en 5 Étapes

### ⏱️ Temps estimé: 30 minutes

---

## Étape 1: Installation (5 min)

```bash
# 1. Créer l'environnement virtuel
python -m venv venv

# 2. Activer (Windows)
venv\Scripts\activate

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Configurer MT5
cp .env.example .env
notepad .env  # Remplir avec vos identifiants DÉMO MT5
```

---

## Étape 2: Collecte des Données (5 min)

```bash
python scripts/01_collect_data.py
```

**Résultat attendu:**
```
✓ Données récupérées: 35000 barres
✓ Données sauvegardées: data_storage/raw/XAUUSD_H1_historical_*.csv
```

---

## Étape 3: Entraînement du Modèle (10 min)

```bash
python scripts/02_train_model.py
```

**Résultat attendu:**
```
✓ Features créées: 65 colonnes
✓ Accuracy: 0.62
✓ Modèle sauvegardé: xgboost_model_H1_latest
```

---

## Étape 4: Backtesting (5 min)

```bash
python scripts/03_backtest.py
```

**Résultat attendu:**
```
✓ Win Rate: 57%
✓ Profit Factor: 1.9
✓ Sharpe Ratio: 1.45
```

---

## Étape 5: Trading Démo (en continu)

```bash
python scripts/04_live_trading.py
```

**⚠️ IMPORTANT:**
- Utilisez UNIQUEMENT un compte DÉMO
- Surveillez le système
- Lisez BEST_PRACTICES.md

---

## 📚 Documentation Complète

| Document | Description |
|----------|-------------|
| **README.md** | Vue d'ensemble du projet |
| **GUIDE_UTILISATION.md** | Guide détaillé étape par étape |
| **BEST_PRACTICES.md** | Bonnes pratiques et erreurs à éviter |
| **PROJECT_STRUCTURE.md** | Architecture du projet |

---

## 🆘 En cas de problème

1. Vérifier les logs dans `logs/`
2. Consulter le GUIDE_UTILISATION.md
3. Vérifier la connexion MT5
4. Vérifier le fichier .env

---

## ✅ Checklist Avant Production

- [ ] Tests sur compte DÉMO (1+ mois)
- [ ] Win rate > 50%
- [ ] Profit factor > 1.5
- [ ] Max drawdown < 15%
- [ ] Comprendre tous les risques
- [ ] Capital dédié disponible

---

## 📊 Fichiers Créés

### Configuration
- `config/config.py` - Configuration générale
- `config/mt5_config.py` - Configuration MT5
- `.env.example` - Template de configuration

### Modules de Données
- `data/mt5_collector.py` - Collecte depuis MT5
- `data/data_manager.py` - Gestion des données

### Features
- `features/technical_indicators.py` - Indicateurs techniques
- `features/feature_engineering.py` - Feature engineering

### Modèles
- `models/xgboost_model.py` - Modèle XGBoost

### Trading
- `trading/signal_generator.py` - Génération de signaux
- `trading/risk_manager.py` - Gestion du risque
- `trading/order_executor.py` - Exécution des ordres

### Scripts
- `scripts/01_collect_data.py` - Collecte des données
- `scripts/02_train_model.py` - Entraînement
- `scripts/03_backtest.py` - Backtesting
- `scripts/04_live_trading.py` - Trading en temps réel

---

## 🎯 Prochaines Étapes

### Court terme (cette semaine)
1. Collecter des données historiques
2. Entraîner le premier modèle
3. Faire le backtesting
4. Tester sur compte démo

### Moyen terme (ce mois)
1. Optimiser les hyperparamètres
2. Ajouter de nouvelles features
3. Tester différents timeframes
4. Analyser les performances

### Long terme (3-6 mois)
1. Développer le modèle LSTM
2. Implémenter le multi-timeframe
3. Ajouter d'autres symboles
4. Passer en production (si validé)

---

## 🎓 Ressources pour Apprendre

### Trading
- BabyPips.com - Éducation forex gratuite
- Investopedia - Concepts financiers
- TradingView - Analyse technique

### Machine Learning
- Scikit-learn docs - ML en Python
- XGBoost docs - Modèle gradient boosting
- Kaggle - Compétitions et tutoriels

### Python
- Real Python - Tutoriels Python
- Python docs - Documentation officielle
- Stack Overflow - Q&A

---

## ⚠️ Avertissement Final

```
┌─────────────────────────────────────────────────┐
│                                                 │
│  ⚠️  AVERTISSEMENT IMPORTANT                   │
│                                                 │
│  Le trading comporte des RISQUES de PERTE      │
│                                                 │
│  ✓ Utilisez un compte DÉMO pour les tests     │
│  ✓ Ne tradez que l'argent que vous pouvez     │
│    vous permettre de PERDRE                    │
│  ✓ Les performances passées ne garantissent   │
│    PAS les résultats futurs                    │
│  ✓ Consultez un conseiller financier          │
│                                                 │
│  Ce système est fourni à titre ÉDUCATIF        │
│                                                 │
└─────────────────────────────────────────────────┘
```

---

## 💡 Conseils pour Réussir

1. **Patience** - Ne vous précipitez pas en production
2. **Apprentissage** - Étudiez le marché et le système
3. **Discipline** - Respectez votre stratégie
4. **Gestion du risque** - TOUJOURS prioritaire
5. **Amélioration continue** - Analysez et optimisez

---

## 📞 Support

Pour des questions:
1. Lisez d'abord GUIDE_UTILISATION.md
2. Consultez BEST_PRACTICES.md
3. Vérifiez les logs
4. Ouvrez une issue GitHub

---

## 🎉 Félicitations!

Vous avez maintenant un système de trading algorithmique complet!

**Prochaine action:** Lancez `python scripts/01_collect_data.py`

---

**Bon trading et bonne chance! 🚀📈**

*Développé pour un projet académique (PFE) - Utilisez de manière responsable*

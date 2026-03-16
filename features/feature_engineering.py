"""
Module de feature engineering pour le système de trading
"""
import pandas as pd
import numpy as np
from typing import Optional
import logging

from features.technical_indicators import TechnicalIndicators
from config.config import FEATURE_CONFIG

logger = logging.getLogger(__name__)


class FeatureEngineer:
    """Création et transformation des features pour le modèle ML"""
    
    def __init__(self):
        self.ti = TechnicalIndicators()
        self.feature_config = FEATURE_CONFIG
        
    def create_all_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Créer toutes les features pour le modèle
        
        Args:
            df: DataFrame avec les données OHLC
            
        Returns:
            DataFrame avec toutes les features
        """
        logger.info("Création des features...")
        
        df = df.copy()
        
        # 1. Features de prix
        df = self._create_price_features(df)
        
        # 2. Moyennes mobiles
        df = self._create_moving_averages(df)
        
        # 3. Oscillateurs
        df = self._create_oscillators(df)
        
        # 4. Volatilité
        df = self._create_volatility_features(df)
        
        # 5. Volume
        df = self._create_volume_features(df)
        
        # 6. Features temporelles
        df = self._create_time_features(df)
        
        # 7. Features de tendance
        df = self._create_trend_features(df)
        
        # Supprimer les valeurs NaN au début
        initial_len = len(df)
        df = df.dropna()
        logger.info(f"Features créées: {len(df.columns)} colonnes")
        logger.info(f"Lignes perdues (NaN): {initial_len - len(df)}")
        
        return df
    
    def _create_price_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Créer les features basées sur les prix"""
        # Variations de prix
        df['price_change'] = df['close'].diff()
        df['price_change_pct'] = df['close'].pct_change() * 100
        
        # Range (high - low)
        df['price_range'] = df['high'] - df['low']
        df['price_range_pct'] = (df['price_range'] / df['close']) * 100
        
        # Body de la bougie
        df['candle_body'] = df['close'] - df['open']
        df['candle_body_pct'] = (df['candle_body'] / df['open']) * 100
        
        # Upper shadow et lower shadow
        df['upper_shadow'] = df['high'] - df[['open', 'close']].max(axis=1)
        df['lower_shadow'] = df[['open', 'close']].min(axis=1) - df['low']
        
        # Type de bougie (haussière = 1, baissière = -1)
        df['candle_type'] = np.where(df['close'] > df['open'], 1, -1)
        
        return df
    
    def _create_moving_averages(self, df: pd.DataFrame) -> pd.DataFrame:
        """Créer les moyennes mobiles"""
        # Simple Moving Averages
        for period in self.feature_config['SMA_periods']:
            col_name = f'SMA_{period}'
            df[col_name] = self.ti.calculate_sma(df, period)
            # Distance du prix à la SMA
            df[f'{col_name}_diff'] = df['close'] - df[col_name]
            df[f'{col_name}_diff_pct'] = ((df['close'] - df[col_name]) / df[col_name]) * 100
        
        # Exponential Moving Averages
        for period in self.feature_config['EMA_periods']:
            col_name = f'EMA_{period}'
            df[col_name] = self.ti.calculate_ema(df, period)
            df[f'{col_name}_diff'] = df['close'] - df[col_name]
            df[f'{col_name}_diff_pct'] = ((df['close'] - df[col_name]) / df[col_name]) * 100
        
        # Croisements de moyennes
        if len(self.feature_config['SMA_periods']) >= 2:
            df['SMA_cross_20_50'] = np.where(
                df['SMA_20'] > df['SMA_50'], 1, -1
            )
        
        if len(self.feature_config['EMA_periods']) >= 2:
            df['EMA_cross_12_26'] = np.where(
                df['EMA_12'] > df['EMA_26'], 1, -1
            )
        
        return df
    
    def _create_oscillators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Créer les oscillateurs"""
        # RSI
        rsi_period = self.feature_config['RSI_period']
        df['RSI'] = self.ti.calculate_rsi(df, rsi_period)
        df['RSI_oversold'] = np.where(df['RSI'] < 30, 1, 0)
        df['RSI_overbought'] = np.where(df['RSI'] > 70, 1, 0)
        
        # MACD
        macd, macd_signal, macd_hist = self.ti.calculate_macd(
            df,
            self.feature_config['MACD_fast'],
            self.feature_config['MACD_slow'],
            self.feature_config['MACD_signal']
        )
        df['MACD'] = macd
        df['MACD_signal'] = macd_signal
        df['MACD_hist'] = macd_hist
        df['MACD_cross'] = np.where(df['MACD'] > df['MACD_signal'], 1, -1)
        
        # Stochastic
        k, d = self.ti.calculate_stochastic(
            df,
            self.feature_config['Stochastic_k'],
            self.feature_config['Stochastic_d']
        )
        df['Stoch_K'] = k
        df['Stoch_D'] = d
        df['Stoch_oversold'] = np.where(df['Stoch_K'] < 20, 1, 0)
        df['Stoch_overbought'] = np.where(df['Stoch_K'] > 80, 1, 0)
        
        # CCI
        df['CCI'] = self.ti.calculate_cci(df, 20)
        
        # Williams %R
        df['Williams_R'] = self.ti.calculate_williams_r(df, 14)
        
        # Momentum
        df['Momentum'] = self.ti.calculate_momentum(df, 10)
        
        # ROC
        df['ROC'] = self.ti.calculate_roc(df, 12)
        
        return df
    
    def _create_volatility_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Créer les features de volatilité"""
        # ATR
        atr_period = self.feature_config['ATR_period']
        df['ATR'] = self.ti.calculate_atr(df, atr_period)
        df['ATR_pct'] = (df['ATR'] / df['close']) * 100
        
        # Bollinger Bands
        upper, middle, lower = self.ti.calculate_bollinger_bands(
            df,
            self.feature_config['BB_period'],
            self.feature_config['BB_std']
        )
        df['BB_upper'] = upper
        df['BB_middle'] = middle
        df['BB_lower'] = lower
        df['BB_width'] = ((upper - lower) / middle) * 100
        df['BB_position'] = ((df['close'] - lower) / (upper - lower)) * 100
        
        # ADX
        df['ADX'] = self.ti.calculate_adx(df, self.feature_config['ADX_period'])
        
        # Écart-type
        df['std_20'] = df['close'].rolling(window=20).std()
        df['std_50'] = df['close'].rolling(window=50).std()
        
        return df
    
    def _create_volume_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Créer les features de volume"""
        # Moyenne du volume
        df['volume_sma_20'] = df['tick_volume'].rolling(window=20).mean()
        df['volume_ratio'] = df['tick_volume'] / df['volume_sma_20']
        
        # OBV
        df['OBV'] = self.ti.calculate_obv(df)
        df['OBV_sma'] = df['OBV'].rolling(window=20).mean()
        
        # Volume trend
        df['volume_trend'] = df['tick_volume'].diff()
        
        return df
    
    def _create_time_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Créer les features temporelles"""
        if 'time' not in df.columns:
            return df
        
        df['hour'] = pd.to_datetime(df['time']).dt.hour
        df['day_of_week'] = pd.to_datetime(df['time']).dt.dayofweek
        df['day_of_month'] = pd.to_datetime(df['time']).dt.day
        df['month'] = pd.to_datetime(df['time']).dt.month
        
        # Sessions de trading (indicateurs binaires)
        # Session asiatique (00:00 - 09:00 UTC)
        df['asian_session'] = ((df['hour'] >= 0) & (df['hour'] < 9)).astype(int)
        # Session européenne (07:00 - 16:00 UTC)
        df['european_session'] = ((df['hour'] >= 7) & (df['hour'] < 16)).astype(int)
        # Session américaine (12:00 - 21:00 UTC)
        df['american_session'] = ((df['hour'] >= 12) & (df['hour'] < 21)).astype(int)
        
        return df
    
    def _create_trend_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Créer les features de tendance"""
        # Tendance court terme (5 périodes)
        df['trend_short'] = np.where(
            df['close'] > df['close'].shift(5), 1, -1
        )
        
        # Tendance moyen terme (20 périodes)
        df['trend_medium'] = np.where(
            df['close'] > df['close'].shift(20), 1, -1
        )
        
        # Tendance long terme (50 périodes)
        df['trend_long'] = np.where(
            df['close'] > df['close'].shift(50), 1, -1
        )
        
        # Pente de la tendance (régression linéaire sur 20 périodes)
        def calculate_slope(series):
            if len(series) < 2:
                return 0
            x = np.arange(len(series))
            y = series.values
            slope = np.polyfit(x, y, 1)[0]
            return slope
        
        df['trend_slope_20'] = df['close'].rolling(window=20).apply(
            calculate_slope, raw=False
        )
        
        return df
    
    def create_labels(
        self,
        df: pd.DataFrame,
        method: str = "future_return",
        threshold: float = 0.001
    ) -> pd.DataFrame:
        """
        Créer les labels pour le modèle (BUY/SELL/HOLD)
        
        Args:
            df: DataFrame avec les features
            method: Méthode de labélisation
            threshold: Seuil pour déterminer BUY/SELL
            
        Returns:
            DataFrame avec la colonne 'label'
        """
        df = df.copy()
        
        if method == "future_return":
            # Calculer le rendement futur (prochain prix)
            df['future_return'] = df['close'].shift(-1) / df['close'] - 1
            
            # Créer les labels
            df['label'] = 0  # HOLD par défaut
            df.loc[df['future_return'] > threshold, 'label'] = 1  # BUY
            df.loc[df['future_return'] < -threshold, 'label'] = 2  # SELL
            
        elif method == "future_trend":
            # Regarder la tendance sur les 5 prochaines périodes
            future_price = df['close'].shift(-5)
            df['future_change'] = (future_price - df['close']) / df['close']
            
            df['label'] = 0  # HOLD
            df.loc[df['future_change'] > threshold, 'label'] = 1  # BUY
            df.loc[df['future_change'] < -threshold, 'label'] = 2  # SELL
        
        # Supprimer les dernières lignes sans label
        df = df.dropna(subset=['label'])
        df['label'] = df['label'].astype(int)
        
        # Afficher la distribution des labels
        label_counts = df['label'].value_counts()
        logger.info(f"Distribution des labels:\n{label_counts}")
        logger.info(f"Proportions: {(label_counts / len(df) * 100).round(2).to_dict()}")
        
        return df
    
    def get_feature_names(self, df: pd.DataFrame) -> list:
        """
        Obtenir la liste des noms de features (sans time, label, etc.)
        
        Args:
            df: DataFrame avec les features
            
        Returns:
            Liste des noms de features
        """
        exclude_cols = ['time', 'label', 'future_return', 'future_change']
        ohlc_cols = ['open', 'high', 'low', 'close', 'tick_volume', 'spread', 'real_volume']
        
        feature_cols = [
            col for col in df.columns
            if col not in exclude_cols and col not in ohlc_cols
        ]
        
        return feature_cols


# Exemple d'utilisation
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Créer des données de test
    from data.mt5_collector import MT5Collector
    from datetime import datetime
    
    collector = MT5Collector()
    if collector.connect():
        df = collector.get_historical_data(
            timeframe="H1",
            start_date=datetime(2024, 1, 1),
            num_bars=5000
        )
        
        if df is not None:
            # Créer les features
            fe = FeatureEngineer()
            df_features = fe.create_all_features(df)
            
            # Créer les labels
            df_labeled = fe.create_labels(df_features)
            
            print(f"\nDataFrame final: {df_labeled.shape}")
            print(f"Features: {len(fe.get_feature_names(df_labeled))}")
            print(f"\nAperçu des données:")
            print(df_labeled[['time', 'close', 'RSI', 'MACD', 'label']].tail())
        
        collector.disconnect()

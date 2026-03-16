"""
Module de calcul des indicateurs techniques
"""
import pandas as pd
import numpy as np
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class TechnicalIndicators:
    """Calculateur d'indicateurs techniques pour l'analyse du marché"""
    
    @staticmethod
    def calculate_sma(df: pd.DataFrame, period: int, column: str = 'close') -> pd.Series:
        """
        Calculer la Simple Moving Average (SMA)
        
        Args:
            df: DataFrame avec les données
            period: Période de la moyenne
            column: Colonne à utiliser
            
        Returns:
            Series avec la SMA
        """
        return df[column].rolling(window=period).mean()
    
    @staticmethod
    def calculate_ema(df: pd.DataFrame, period: int, column: str = 'close') -> pd.Series:
        """
        Calculer l'Exponential Moving Average (EMA)
        
        Args:
            df: DataFrame avec les données
            period: Période de la moyenne
            column: Colonne à utiliser
            
        Returns:
            Series avec l'EMA
        """
        return df[column].ewm(span=period, adjust=False).mean()
    
    @staticmethod
    def calculate_rsi(df: pd.DataFrame, period: int = 14, column: str = 'close') -> pd.Series:
        """
        Calculer le Relative Strength Index (RSI)
        
        Args:
            df: DataFrame avec les données
            period: Période du RSI
            column: Colonne à utiliser
            
        Returns:
            Series avec le RSI
        """
        delta = df[column].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    @staticmethod
    def calculate_macd(
        df: pd.DataFrame,
        fast: int = 12,
        slow: int = 26,
        signal: int = 9,
        column: str = 'close'
    ) -> tuple:
        """
        Calculer le MACD (Moving Average Convergence Divergence)
        
        Args:
            df: DataFrame avec les données
            fast: Période rapide
            slow: Période lente
            signal: Période du signal
            column: Colonne à utiliser
            
        Returns:
            Tuple (macd, signal, histogram)
        """
        ema_fast = df[column].ewm(span=fast, adjust=False).mean()
        ema_slow = df[column].ewm(span=slow, adjust=False).mean()
        
        macd = ema_fast - ema_slow
        macd_signal = macd.ewm(span=signal, adjust=False).mean()
        macd_histogram = macd - macd_signal
        
        return macd, macd_signal, macd_histogram
    
    @staticmethod
    def calculate_bollinger_bands(
        df: pd.DataFrame,
        period: int = 20,
        std: float = 2.0,
        column: str = 'close'
    ) -> tuple:
        """
        Calculer les Bollinger Bands
        
        Args:
            df: DataFrame avec les données
            period: Période de la moyenne
            std: Nombre d'écarts-types
            column: Colonne à utiliser
            
        Returns:
            Tuple (upper_band, middle_band, lower_band)
        """
        middle_band = df[column].rolling(window=period).mean()
        std_dev = df[column].rolling(window=period).std()
        
        upper_band = middle_band + (std_dev * std)
        lower_band = middle_band - (std_dev * std)
        
        return upper_band, middle_band, lower_band
    
    @staticmethod
    def calculate_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
        """
        Calculer l'Average True Range (ATR)
        
        Args:
            df: DataFrame avec les données OHLC
            period: Période de l'ATR
            
        Returns:
            Series avec l'ATR
        """
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift())
        low_close = np.abs(df['low'] - df['close'].shift())
        
        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = true_range.rolling(window=period).mean()
        
        return atr
    
    @staticmethod
    def calculate_stochastic(
        df: pd.DataFrame,
        k_period: int = 14,
        d_period: int = 3
    ) -> tuple:
        """
        Calculer l'oscillateur Stochastique
        
        Args:
            df: DataFrame avec les données OHLC
            k_period: Période pour %K
            d_period: Période pour %D
            
        Returns:
            Tuple (%K, %D)
        """
        low_min = df['low'].rolling(window=k_period).min()
        high_max = df['high'].rolling(window=k_period).max()
        
        k = 100 * ((df['close'] - low_min) / (high_max - low_min))
        d = k.rolling(window=d_period).mean()
        
        return k, d
    
    @staticmethod
    def calculate_adx(df: pd.DataFrame, period: int = 14) -> pd.Series:
        """
        Calculer l'Average Directional Index (ADX)
        
        Args:
            df: DataFrame avec les données OHLC
            period: Période de l'ADX
            
        Returns:
            Series avec l'ADX
        """
        # Calculer +DM et -DM
        high_diff = df['high'].diff()
        low_diff = -df['low'].diff()
        
        plus_dm = high_diff.where((high_diff > low_diff) & (high_diff > 0), 0)
        minus_dm = low_diff.where((low_diff > high_diff) & (low_diff > 0), 0)
        
        # Calculer ATR
        atr = TechnicalIndicators.calculate_atr(df, period)
        
        # Calculer +DI et -DI
        plus_di = 100 * (plus_dm.rolling(window=period).mean() / atr)
        minus_di = 100 * (minus_dm.rolling(window=period).mean() / atr)
        
        # Calculer DX
        dx = 100 * np.abs(plus_di - minus_di) / (plus_di + minus_di)
        
        # Calculer ADX
        adx = dx.rolling(window=period).mean()
        
        return adx
    
    @staticmethod
    def calculate_obv(df: pd.DataFrame) -> pd.Series:
        """
        Calculer l'On-Balance Volume (OBV)
        
        Args:
            df: DataFrame avec les données (close, tick_volume)
            
        Returns:
            Series avec l'OBV
        """
        obv = (np.sign(df['close'].diff()) * df['tick_volume']).fillna(0).cumsum()
        return obv
    
    @staticmethod
    def calculate_cci(df: pd.DataFrame, period: int = 20) -> pd.Series:
        """
        Calculer le Commodity Channel Index (CCI)
        
        Args:
            df: DataFrame avec les données OHLC
            period: Période du CCI
            
        Returns:
            Series avec le CCI
        """
        typical_price = (df['high'] + df['low'] + df['close']) / 3
        sma = typical_price.rolling(window=period).mean()
        mad = typical_price.rolling(window=period).apply(
            lambda x: np.abs(x - x.mean()).mean()
        )
        
        cci = (typical_price - sma) / (0.015 * mad)
        
        return cci
    
    @staticmethod
    def calculate_williams_r(df: pd.DataFrame, period: int = 14) -> pd.Series:
        """
        Calculer le Williams %R
        
        Args:
            df: DataFrame avec les données OHLC
            period: Période du Williams %R
            
        Returns:
            Series avec le Williams %R
        """
        highest_high = df['high'].rolling(window=period).max()
        lowest_low = df['low'].rolling(window=period).min()
        
        williams_r = -100 * ((highest_high - df['close']) / (highest_high - lowest_low))
        
        return williams_r
    
    @staticmethod
    def calculate_momentum(df: pd.DataFrame, period: int = 10, column: str = 'close') -> pd.Series:
        """
        Calculer le Momentum
        
        Args:
            df: DataFrame avec les données
            period: Période du momentum
            column: Colonne à utiliser
            
        Returns:
            Series avec le momentum
        """
        return df[column].diff(period)
    
    @staticmethod
    def calculate_roc(df: pd.DataFrame, period: int = 12, column: str = 'close') -> pd.Series:
        """
        Calculer le Rate of Change (ROC)
        
        Args:
            df: DataFrame avec les données
            period: Période du ROC
            column: Colonne à utiliser
            
        Returns:
            Series avec le ROC
        """
        return ((df[column] - df[column].shift(period)) / df[column].shift(period)) * 100


# Exemple d'utilisation
if __name__ == "__main__":
    # Créer des données de test
    dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='H')
    np.random.seed(42)
    
    price = 2000
    prices = [price]
    for _ in range(len(dates) - 1):
        change = np.random.normal(0, 5)
        price += change
        prices.append(price)
    
    df = pd.DataFrame({
        'time': dates,
        'open': prices,
        'high': [p + np.random.uniform(0, 10) for p in prices],
        'low': [p - np.random.uniform(0, 10) for p in prices],
        'close': prices,
        'tick_volume': np.random.randint(100, 1000, len(dates)),
    })
    
    # Calculer les indicateurs
    ti = TechnicalIndicators()
    
    df['SMA_20'] = ti.calculate_sma(df, 20)
    df['EMA_12'] = ti.calculate_ema(df, 12)
    df['RSI_14'] = ti.calculate_rsi(df, 14)
    
    macd, macd_signal, macd_hist = ti.calculate_macd(df)
    df['MACD'] = macd
    df['MACD_Signal'] = macd_signal
    
    df['ATR_14'] = ti.calculate_atr(df, 14)
    
    print("\nIndicateurs calculés:")
    print(df[['time', 'close', 'SMA_20', 'RSI_14', 'MACD', 'ATR_14']].tail(10))

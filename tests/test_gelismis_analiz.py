import pytest
import pandas as pd
import numpy as np
import os
from datetime import datetime

from scripts.gelismis_analiz import (
    veri_kalitesi_kontrolu,
    format_veri_kalitesi,
    anomali_tespiti,
    format_anomali,
    mevsimsellik_temizle,
    format_mevsimsellik,
    coklu_degisken_analizi,
    format_coklu_analiz,
    dashboard_olustur,
    durgunluk_testi,
    frekans_donusumu
)

@pytest.fixture
def sample_df():
    """Returns a sample dataframe for testing purposes."""
    dates = pd.date_range(start='2023-01-01', periods=100, freq='D')
    np.random.seed(42)

    col_a = np.random.normal(100, 10, 100)
    col_b = col_a * 1.5 + np.random.normal(0, 5, 100)

    # Introduce outliers
    col_a[10] = 500
    col_a[20] = -300

    df = pd.DataFrame({
        'A': col_a,
        'B': col_b,
        'C': np.random.choice(['X', 'Y', 'Z'], 100)
    }, index=dates)

    # Introduce missing values
    df.loc[df.index[5], 'A'] = np.nan
    df.loc[df.index[15:18], 'B'] = np.nan

    # Add a duplicated row to make 101 rows total
    df = pd.concat([df, df.iloc[[-1]]])

    return df

@pytest.fixture
def sample_series():
    """Returns a sample series with trend and seasonality."""
    dates = pd.date_range(start='2020-01-01', periods=120, freq='MS')
    t = np.arange(120)
    trend = 0.5 * t
    seasonality = 10 * np.sin(2 * np.pi * t / 12)
    noise = np.random.normal(0, 2, 120)

    data = trend + seasonality + noise
    return pd.Series(data, index=dates, name='Value')

def test_veri_kalitesi_kontrolu(sample_df):
    """Test data quality checks against a sample dataframe."""
    rapor = veri_kalitesi_kontrolu(sample_df)

    # Check return structure
    assert isinstance(rapor, dict)
    assert all(k in rapor for k in ['genel', 'sutunlar', 'puan', 'uyarilar', 'zaman_serisi'])

    # Check calculations in general section
    assert rapor['genel']['satir_sayisi'] == 101
    assert rapor['genel']['sutun_sayisi'] == 3
    assert rapor['genel']['eksik_toplam'] == 4 # 1 in A + 3 in B
    assert rapor['genel']['duplicate_satir'] == 1

    # Check column specific section
    assert 'A' in rapor['sutunlar']
    assert rapor['sutunlar']['A']['eksik'] == 1
    assert rapor['sutunlar']['B']['eksik'] == 3

    # Check outlier detection within data quality check
    assert rapor['sutunlar']['A']['outlier_iqr'] > 0

    # Check score deduction
    assert rapor['puan'] < 100

def test_format_veri_kalitesi(sample_df):
    """Test formatting output for data quality report."""
    rapor = veri_kalitesi_kontrolu(sample_df)
    formatted = format_veri_kalitesi(rapor)

    assert isinstance(formatted, str)
    assert "VERİ KALİTESİ RAPORU" in formatted
    assert "Satır sayısı: 101" in formatted
    assert "Sütun sayısı: 3" in formatted

def test_anomali_tespiti_iqr(sample_df):
    """Test anomaly detection using the IQR method."""
    sonuclar = anomali_tespiti(sample_df, metot='iqr')

    assert isinstance(sonuclar, dict)

    # Check that A has the expected anomalies
    assert 'A' in sonuclar
    assert sonuclar['A']['metot'] == 'iqr'
    assert sonuclar['A']['anomali_sayisi'] >= 2 # Should detect the injected 500 and -300
    assert len(sonuclar['A']['anomali_indeksler']) == sonuclar['A']['anomali_sayisi']
    assert len(sonuclar['A']['anomali_degerler']) == sonuclar['A']['anomali_sayisi']
    assert 'sinirlar' in sonuclar['A']

    # Check that column C (non-numeric) is ignored
    assert 'C' not in sonuclar

def test_anomali_tespiti_zscore(sample_df):
    """Test anomaly detection using the Z-score method."""
    sonuclar = anomali_tespiti(sample_df, metot='zscore')

    assert 'A' in sonuclar
    assert sonuclar['A']['metot'] == 'zscore'
    assert sonuclar['A']['anomali_sayisi'] > 0

def test_format_anomali(sample_df):
    """Test formatting output for anomaly detection report."""
    sonuclar = anomali_tespiti(sample_df, metot='iqr')
    formatted = format_anomali(sonuclar)

    assert isinstance(formatted, str)
    assert "ANOMALİ TESPİT RAPORU" in formatted
    assert "Yöntem: IQR" in formatted
    assert "Anomali sayısı:" in formatted

def test_mevsimsellik_temizle_ma(sample_series):
    """Test seasonal decomposition using moving average method."""
    sonuc = mevsimsellik_temizle(sample_series, periyot=12, metot='ma')

    assert isinstance(sonuc, dict)
    assert 'hata' not in sonuc

    expected_keys = ['orijinal', 'trend', 'mevsimsel', 'artik', 'duzeltilmis', 'metot', 'periyot', 'mevsimsel_guc']
    assert all(k in sonuc for k in expected_keys)

    assert sonuc['metot'] == 'ma'
    assert sonuc['periyot'] == 12
    assert isinstance(sonuc['mevsimsel_guc'], float)

def test_mevsimsellik_temizle_stl(sample_series):
    """Test seasonal decomposition using STL method."""
    sonuc = mevsimsellik_temizle(sample_series, periyot=12, metot='stl')

    # STL requires statsmodels, which is available in our test env
    assert isinstance(sonuc, dict)
    assert 'hata' not in sonuc
    assert sonuc['metot'] == 'stl'
    assert 'orijinal' in sonuc
    assert 'trend' in sonuc

def test_format_mevsimsellik(sample_series):
    """Test formatting output for seasonality report."""
    sonuc = mevsimsellik_temizle(sample_series, periyot=12, metot='ma')
    formatted = format_mevsimsellik(sonuc)

    assert isinstance(formatted, str)
    assert "MEVSİMSELLİK TEMİZLEME RAPORU" in formatted
    assert "Yöntem: MA" in formatted
    assert "Mevsimsellik gücü:" in formatted

def test_coklu_degisken_analizi(sample_df):
    """Test multiple variable analysis including correlation, PCA, Granger, regression."""
    # Run analysis without specifying dependent variable to check core functions
    sonuclar = coklu_degisken_analizi(sample_df, analizler=['korelasyon', 'pca', 'granger'])

    assert isinstance(sonuclar, dict)
    assert 'hata' not in sonuclar

    # Check correlation
    assert 'korelasyon' in sonuclar
    assert 'pearson' in sonuclar['korelasyon']
    assert 'en_guclu' in sonuclar['korelasyon']

    # Check PCA
    assert 'pca' in sonuclar
    assert 'aciklanan_varyans' in sonuclar['pca']

    # Check Granger
    assert 'granger' in sonuclar

    # Run analysis with regression
    sonuclar_reg = coklu_degisken_analizi(
        sample_df,
        bagimli='B',
        bagimsizlar=['A'],
        analizler=['regresyon']
    )

    assert 'regresyon' in sonuclar_reg
    assert 'r2' in sonuclar_reg['regresyon']
    assert 'katsayilar' in sonuclar_reg['regresyon']

def test_format_coklu_analiz(sample_df):
    """Test formatting output for multiple variable analysis report."""
    sonuclar = coklu_degisken_analizi(sample_df, analizler=['korelasyon'])
    formatted = format_coklu_analiz(sonuclar)

    assert isinstance(formatted, str)
    assert "ÇOKLU DEĞİŞKEN ANALİZİ" in formatted
    assert "KORELASYON ANALİZİ" in formatted

def test_dashboard_olustur(sample_df, tmp_path):
    """Test the dashboard HTML generation."""
    # Create a temporary file path
    dashboard_file = tmp_path / "test_dashboard.html"

    # Generate dashboard
    dosya_adi = dashboard_olustur(
        sample_df,
        baslik="Test Dashboard",
        dosya_adi=str(dashboard_file),
        analizler=['ozet', 'korelasyon']
    )

    assert dosya_adi == str(dashboard_file)
    assert os.path.exists(dosya_adi)

    # Read the content and verify basic HTML structure
    with open(dosya_adi, 'r', encoding='utf-8') as f:
        content = f.read()

    assert "<!DOCTYPE html>" in content
    assert "<title>Test Dashboard</title>" in content
    assert "Test Dashboard" in content
    assert "Plotly.newPlot" in content # Plotly initialization should be present

    # Cleanup (handled automatically by pytest tmp_path, but explicitly testing os.remove here)
    if os.path.exists(dosya_adi):
        os.remove(dosya_adi)
    assert not os.path.exists(dosya_adi)

def test_durgunluk_testi():
    """Test stationarity test functions."""
    # Stationary series (white noise)
    np.random.seed(42)
    stationary = pd.Series(np.random.normal(0, 1, 200))

    # Non-stationary series (random walk)
    non_stationary = pd.Series(np.cumsum(np.random.normal(0, 1, 200)))

    # Test ADF on stationary series
    res_adf_stat = durgunluk_testi(stationary, test='adf')
    assert isinstance(res_adf_stat, dict)
    assert 'hata' not in res_adf_stat
    assert res_adf_stat['test'] == 'ADF'
    assert 'istatistik' in res_adf_stat
    assert 'p_value' in res_adf_stat
    assert bool(res_adf_stat['duragan']) is True

    # Test ADF on non-stationary series
    res_adf_non_stat = durgunluk_testi(non_stationary, test='adf')
    assert bool(res_adf_non_stat['duragan']) is False

    # Test KPSS on non-stationary series
    res_kpss = durgunluk_testi(non_stationary, test='kpss')
    assert 'hata' not in res_kpss
    assert res_kpss['test'] == 'KPSS'

def test_frekans_donusumu(sample_df):
    """Test frequency conversion for a DatetimeIndex dataframe."""
    # Convert daily to monthly start ('MS') using default method 'mean'
    # Drop non-numeric column C for mean aggregation
    df_numeric = sample_df.drop(columns=['C'])
    df_monthly = frekans_donusumu(df_numeric, hedef_frekans='MS')

    assert isinstance(df_monthly, pd.DataFrame)

    # Check frequency length (about 100 days should map to 4 months)
    assert len(df_monthly) == 4

    # Verify the index frequency attribute or values
    assert all(df_monthly.index.day == 1)

    # Test alternative aggregation method
    df_sum = frekans_donusumu(df_numeric, hedef_frekans='W', metot='sum')
    assert isinstance(df_sum, pd.DataFrame)
    assert len(df_sum) > 0

def test_frekans_donusumu_invalid():
    """Test frequency conversion with non-datetime index."""
    df_invalid = pd.DataFrame({'A': [1, 2, 3]})
    with pytest.raises(ValueError, match="tarih indexi olmalı"):
        frekans_donusumu(df_invalid, hedef_frekans='MS')

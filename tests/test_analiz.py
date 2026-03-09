import pytest
import pandas as pd
import numpy as np
from scripts.analiz import (
    korelasyon_analizi,
    ols_regresyon,
    arima_analizi,
    var_analizi,
    mevsimsellik_analizi,
    format_ols,
    format_arima,
    format_var,
    format_korelasyon,
)

@pytest.fixture
def df_korelasyon():
    np.random.seed(42)
    # A and B are perfectly correlated, C is somewhat random
    A = np.linspace(0, 10, 100)
    B = A * 2 + 5
    C = np.random.randn(100)
    return pd.DataFrame({'A': A, 'B': B, 'C': C})

@pytest.fixture
def df_ols():
    np.random.seed(42)
    A = np.linspace(0, 10, 100)
    C = np.random.randn(100)
    B = A * 2 + 5 + np.random.randn(100) * 0.1
    return pd.DataFrame({'A': A, 'B': B, 'C': C})

@pytest.fixture
def series_ts():
    np.random.seed(42)
    # Series with a trend and seasonality
    idx = pd.date_range('2020-01-01', periods=60, freq='ME')
    data = np.linspace(0, 10, 60) + np.sin(np.linspace(0, 4*np.pi, 60)) * 5 + np.random.randn(60) * 0.5
    return pd.Series(data, index=idx, name='Değer')

@pytest.fixture
def df_var():
    np.random.seed(42)
    idx = pd.date_range('2020-01-01', periods=60, freq='ME')
    x2 = np.random.randn(60)
    x1 = np.roll(x2, 1) + np.random.randn(60) * 0.1
    x1[0] = 0
    return pd.DataFrame({'x1': x1, 'x2': x2}, index=idx)

def test_korelasyon_analizi(df_korelasyon):
    sonuc = korelasyon_analizi(df_korelasyon)

    assert 'matris' in sonuc
    assert 'yorumlar' in sonuc

    matris = sonuc['matris']
    assert isinstance(matris, pd.DataFrame)
    assert matris.shape == (3, 3)

    # Check perfect correlation
    assert np.isclose(matris.loc['A', 'B'], 1.0)

    yorumlar = sonuc['yorumlar']
    assert len(yorumlar) == 3 # combinations of 3 items is 3

    # Find A <-> B correlation
    ab_yorum = next(y for y in yorumlar if (y['seri1'] == 'A' and y['seri2'] == 'B') or (y['seri1'] == 'B' and y['seri2'] == 'A'))
    assert ab_yorum['guc'] == 'cok guclu'
    assert ab_yorum['yon'] == 'pozitif'

def test_ols_regresyon(df_ols):
    y = df_ols['B']
    X = df_ols[['A', 'C']]

    sonuc = ols_regresyon(y, X)

    assert 'r_kare' in sonuc
    assert 'katsayilar' in sonuc
    assert 'p_degerleri' in sonuc

    # R-squared should be very high due to constructed dataset
    assert sonuc['r_kare'] > 0.95

    # Coefficient of A should be around 2
    assert np.isclose(sonuc['katsayilar']['A'], 2.0, atol=0.1)
    # Coefficient of C should be around 0
    assert np.isclose(sonuc['katsayilar']['C'], 0.0, atol=0.1)

    # p-value of A should be significant
    assert sonuc['p_degerleri']['A'] < 0.05
    # p-value of C should be insignificant
    assert sonuc['p_degerleri']['C'] > 0.05

def test_arima_analizi(series_ts):
    sonuc = arima_analizi(series_ts, tahmin_donemi=3, mevsimsel=False)

    assert 'tahmin' in sonuc
    assert 'aic' in sonuc
    assert 'model' in sonuc
    assert 'guven_araligi_alt' in sonuc
    assert 'guven_araligi_ust' in sonuc

    tahmin = sonuc['tahmin']
    assert len(tahmin) == 3

    # Check indices of forecast
    assert tahmin.index[0] == series_ts.index[-1] + pd.DateOffset(months=1)

def test_var_analizi(df_var):
    sonuc = var_analizi(df_var, ['x1', 'x2'], max_lag=2)

    assert 'optimal_lag' in sonuc
    assert 'granger' in sonuc
    assert 'model' in sonuc

    granger = sonuc['granger']

    # Since x1 is a shifted version of x2, x2 should granger-cause x1
    x2_causes_x1 = granger['x2 -> x1']
    assert x2_causes_x1['sonuc'] == "Nedensellik VAR"
    assert x2_causes_x1['p_value'] < 0.05

def test_mevsimsellik_analizi(series_ts):
    sonuc = mevsimsellik_analizi(series_ts, periyot=12)

    assert 'trend' in sonuc
    assert 'mevsimsel' in sonuc
    assert 'artik' in sonuc
    assert 'mevsimsel_guc' in sonuc
    assert 'trend_guc' in sonuc

    assert len(sonuc['trend']) == len(series_ts)
    assert len(sonuc['mevsimsel']) == len(series_ts)
    assert len(sonuc['artik']) == len(series_ts)

def test_format_korelasyon(df_korelasyon):
    sonuc = korelasyon_analizi(df_korelasyon)
    metin = format_korelasyon(sonuc)

    assert "Korelasyon Analizi" in metin
    assert "cok guclu pozitif" in metin

def test_format_ols(df_ols):
    y = df_ols['B']
    X = df_ols[['A', 'C']]
    sonuc = ols_regresyon(y, X)
    metin = format_ols(sonuc, bagimli="B")

    assert "OLS Regresyon Sonuclari" in metin
    assert "Bagimli Degisken: B" in metin
    assert "R2:" in metin
    assert "A:" in metin

def test_format_arima(series_ts):
    sonuc = arima_analizi(series_ts, tahmin_donemi=3, mevsimsel=False)
    metin = format_arima(sonuc, seri_adi="Test Seri")

    assert "ARIMA Model Sonuclari" in metin
    assert "Seri: Test Seri" in metin
    assert "AIC:" in metin
    assert "Tahminler:" in metin

def test_format_var(df_var):
    sonuc = var_analizi(df_var, ['x1', 'x2'], max_lag=2)
    metin = format_var(sonuc)

    assert "VAR Model Sonuclari" in metin
    assert "Optimal Gecikme:" in metin
    assert "Granger Nedensellik Testleri:" in metin

def test_format_hata():
    hata_sonuc = {'hata': 'Paket bulunamadi'}
    assert format_ols(hata_sonuc, 'y') == "Hata: Paket bulunamadi"
    assert format_arima(hata_sonuc, 'y') == "Hata: Paket bulunamadi"
    assert format_var(hata_sonuc) == "Hata: Paket bulunamadi"

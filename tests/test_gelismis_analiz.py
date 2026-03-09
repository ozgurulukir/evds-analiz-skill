import pytest
import pandas as pd
import numpy as np
from scripts.gelismis_analiz import veri_kalitesi_kontrolu

def test_veri_kalitesi_kontrolu_basic():
    """Test veri kalitesi on a clean, perfect dataframe"""
    df = pd.DataFrame({
        'A': [1, 2, 3, 4, 5],
        'B': ['a', 'b', 'c', 'd', 'e']
    })

    rapor = veri_kalitesi_kontrolu(df)

    assert rapor['genel']['satir_sayisi'] == 5
    assert rapor['genel']['sutun_sayisi'] == 2
    assert rapor['genel']['eksik_toplam'] == 0
    assert rapor['genel']['duplicate_satir'] == 0
    assert rapor['puan'] == 100
    assert rapor['degerlendirme'] == "✅ Mükemmel veri kalitesi"

def test_veri_kalitesi_kontrolu_missing_data():
    """Test missing data handling and scoring"""
    # 5 rows, 2 columns. Total cells: 10
    # Let's make 2 cells missing (20% missing)
    df = pd.DataFrame({
        'A': [1, np.nan, 3, 4, 5],
        'B': ['a', 'b', np.nan, 'd', 'e']
    })

    rapor = veri_kalitesi_kontrolu(df)

    assert rapor['genel']['eksik_toplam'] == 2
    assert rapor['genel']['eksik_oran'] == 20.0  # 2 / 10 * 100
    assert rapor['puan'] <= 80  # Because missing > 10% drops 20 points
    assert any("Yüksek eksik veri oranı" in u for u in rapor['uyarilar'])

def test_veri_kalitesi_kontrolu_medium_missing_data():
    """Test medium missing data handling and scoring"""
    # 10 rows, 2 columns. Total cells: 20
    # Let's make 2 cells missing (10% missing, which should trigger medium but >5%)
    # Let's use 10% exactly? The code checks > 10 and > 5. So 10% is > 5.
    # 2/20 = 10% -> greater than 5%.
    df = pd.DataFrame({
        'A': [1, np.nan, 3, 4, 5, 6, 7, 8, 9, 10],
        'B': ['a', 'b', np.nan, 'd', 'e', 'f', 'g', 'h', 'i', 'j']
    })

    rapor = veri_kalitesi_kontrolu(df)

    assert rapor['genel']['eksik_oran'] == 10.0
    # point reduction should be 10 for > 5%
    assert rapor['puan'] == 90
    assert any("Orta düzeyde eksik veri" in u for u in rapor['uyarilar'])


def test_veri_kalitesi_kontrolu_duplicates():
    """Test duplicate detection and scoring"""
    df = pd.DataFrame({
        'A': [1, 1, 3, 4, 5],
        'B': ['a', 'a', 'c', 'd', 'e']
    })

    rapor = veri_kalitesi_kontrolu(df)

    assert rapor['genel']['duplicate_satir'] == 1
    # duplicate drops 5 points
    assert rapor['puan'] == 95
    assert any("duplicate satır bulundu" in u for u in rapor['uyarilar'])


def test_veri_kalitesi_kontrolu_outliers():
    """Test outlier detection with IQR and Z-score"""
    # Need > 5% outlier to drop points for IQR.
    # 20 rows. 5% of 20 = 1. So > 1 outlier needed (at least 2).
    # To avoid duplicate deduction, make each inner value unique
    # e.g., 10, 11, 12... up to 27.
    # Q1 ~ 14, Q3 ~ 23, IQR ~ 9.
    # Limits ~ 14 - 13.5 = 0.5, 23 + 13.5 = 36.5
    # So 100 and -100 are outliers.
    data = list(range(10, 28)) + [100, -100]
    df = pd.DataFrame({'A': data})

    rapor = veri_kalitesi_kontrolu(df)

    col_info = rapor['sutunlar']['A']
    assert col_info['outlier_iqr'] == 2
    assert col_info['outlier_zscore'] > 0
    # 5 points dropped for outlier. Initial 100 -> 95. No duplicates.
    assert rapor['puan'] == 95
    assert any("outlier (IQR)" in u for u in rapor['uyarilar'])


def test_veri_kalitesi_kontrolu_skewness():
    """Test high skewness detection"""
    # Generate highly skewed data
    data = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1000, 2000, 3000, 4000]
    df = pd.DataFrame({'A': data})

    rapor = veri_kalitesi_kontrolu(df)

    assert 'A' in rapor['sutunlar']
    assert abs(rapor['sutunlar']['A']['carpiklik']) > 2
    assert any("Yüksek çarpıklık" in u for u in rapor['uyarilar'])


from unittest.mock import patch

def test_veri_kalitesi_kontrolu_time_series():
    """Test time series continuity checks without missing dates"""
    dates = pd.date_range(start="2024-01-01", end="2024-01-10", freq='D')
    df = pd.DataFrame({'A': range(len(dates))}, index=dates)

    rapor = veri_kalitesi_kontrolu(df)

    assert rapor['zaman_serisi']['tespit_edilen_frekans'] == 'D'
    assert rapor['zaman_serisi']['baslangic'] == '2024-01-01'
    assert rapor['zaman_serisi']['bitis'] == '2024-01-10'
    assert 'eksik_tarih_sayisi' in rapor['zaman_serisi']
    assert rapor['zaman_serisi']['eksik_tarih_sayisi'] == 0


@patch('pandas.infer_freq')
def test_veri_kalitesi_kontrolu_time_series_missing(mock_infer_freq):
    """Test time series gap detection by mocking infer_freq"""
    # Since pd.infer_freq fails on series with missing dates, we mock it
    # to return 'D' so the gap detection logic is executed.
    mock_infer_freq.return_value = 'D'

    dates = pd.date_range(start="2024-01-01", end="2024-01-10", freq='D')
    dates = dates.drop([pd.Timestamp("2024-01-05"), pd.Timestamp("2024-01-06")])
    df = pd.DataFrame({'A': range(len(dates))}, index=dates)

    rapor = veri_kalitesi_kontrolu(df)

    assert rapor['zaman_serisi']['tespit_edilen_frekans'] == 'D'
    assert rapor['zaman_serisi']['eksik_tarih_sayisi'] == 2
    # point reduction by min(10, len(eksik)) -> drops 2 points
    assert rapor['puan'] == 98
    assert any("eksik tarih var" in u for u in rapor['uyarilar'])


def test_veri_kalitesi_kontrolu_empty_df():
    """Test behavior with an empty dataframe"""
    df = pd.DataFrame(columns=['A', 'B'])

    rapor = veri_kalitesi_kontrolu(df)

    assert rapor['genel']['satir_sayisi'] == 0
    assert rapor['genel']['sutun_sayisi'] == 2
    assert rapor['genel']['eksik_toplam'] == 0
    assert rapor['genel']['eksik_oran'] == 0.0
    assert rapor['puan'] == 100

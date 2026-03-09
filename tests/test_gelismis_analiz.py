import pytest
import pandas as pd
import numpy as np
import sys
from unittest.mock import patch, MagicMock

from scripts.gelismis_analiz import anomali_tespiti


@pytest.fixture
def sample_data():
    """Returns a DataFrame with a known anomaly."""
    # Create 20 normal points around 10
    np.random.seed(42)
    data = np.random.normal(10, 1, 20).tolist()
    # Add a huge outlier in the middle so rolling catches it with 2 sigma
    data[10] = 1000.0
    # Add some NaN values to test dropna behavior
    data.extend([np.nan, np.nan])

    dates = pd.date_range(start='2023-01-01', periods=len(data))
    df = pd.DataFrame({'deger': data, 'kategori': ['A'] * len(data)}, index=dates)
    return df


def test_anomali_tespiti_iqr(sample_data):
    """Test IQR method for anomaly detection."""
    result = anomali_tespiti(sample_data, metot='iqr')

    assert 'deger' in result
    assert result['deger']['metot'] == 'iqr'
    assert result['deger']['anomali_sayisi'] >= 1
    # 1000.0 should be detected
    assert 1000.0 in result['deger']['anomali_degerler']
    # String column should be ignored
    assert 'kategori' not in result


def test_anomali_tespiti_zscore(sample_data):
    """Test Z-score method for anomaly detection."""
    result = anomali_tespiti(sample_data, metot='zscore', esik=2.0)

    assert 'deger' in result
    assert result['deger']['metot'] == 'zscore'
    assert result['deger']['anomali_sayisi'] >= 1
    assert 1000.0 in result['deger']['anomali_degerler']


def test_anomali_tespiti_mad(sample_data):
    """Test MAD method for anomaly detection."""
    result = anomali_tespiti(sample_data, metot='mad', esik=2.0)

    assert 'deger' in result
    assert result['deger']['metot'] == 'mad'
    assert result['deger']['anomali_sayisi'] >= 1
    assert 1000.0 in result['deger']['anomali_degerler']


def test_anomali_tespiti_rolling(sample_data):
    """Test rolling window method for anomaly detection."""
    # A tighter threshold might be needed for rolling as the outlier strongly
    # influences the local standard deviation. Alternatively, a larger window.
    result = anomali_tespiti(sample_data, metot='rolling', esik=1.0, pencere=5)

    assert 'deger' in result
    assert result['deger']['metot'] == 'rolling'
    assert result['deger']['anomali_sayisi'] >= 1
    assert 1000.0 in result['deger']['anomali_degerler']


def test_anomali_tespiti_isolation(sample_data):
    """Test Isolation Forest method."""
    result = anomali_tespiti(sample_data, metot='isolation')

    assert 'deger' in result
    assert result['deger']['metot'] == 'isolation'
    # Isolation forest uses random states, but with our blatant outlier it should find it
    assert result['deger']['anomali_sayisi'] >= 1


def test_anomali_tespiti_small_dataframe():
    """Test behavior with less than 10 valid data points."""
    df = pd.DataFrame({'deger': [1, 2, 3, 4, 5]})
    result = anomali_tespiti(df)

    assert 'deger' in result
    assert result['deger']['anomali_yok'] is True
    assert result['deger']['mesaj'] == 'Yetersiz veri'


def test_anomali_tespiti_unknown_method(sample_data):
    """Test behavior with an unknown method."""
    result = anomali_tespiti(sample_data, metot='unknown_magic')

    assert 'hata' in result
    assert 'Bilinmeyen metot' in result['hata']


def test_anomali_tespiti_missing_sklearn(sample_data):
    """Test behavior when sklearn is not installed."""
    with patch.dict(sys.modules, {'sklearn': None, 'sklearn.ensemble': None}):
        result = anomali_tespiti(sample_data, metot='isolation')
        assert 'hata' in result
        assert 'sklearn paketi yüklü değil' in result['hata']


def test_anomali_tespiti_details_format(sample_data):
    """Test the detailed format of the anomalies."""
    result = anomali_tespiti(sample_data, metot='iqr')

    details = result['deger'].get('detaylar', [])
    assert len(details) > 0

    first_detail = details[0]
    assert 'tarih' in first_detail
    assert 'deger' in first_detail
    assert 'z_score' in first_detail
    assert 'tip' in first_detail
    assert first_detail['tip'] == 'yüksek' # 1000.0 is > mean

import pytest
import pandas as pd
import numpy as np
import sys
from unittest.mock import patch

from scripts.gelismis_analiz import durgunluk_testi

@pytest.fixture
def stationary_series():
    """White noise series, should be stationary."""
    np.random.seed(42)
    return pd.Series(np.random.normal(0, 1, 1000))

@pytest.fixture
def non_stationary_series():
    """Random walk series, should be non-stationary."""
    np.random.seed(42)
    return pd.Series(np.cumsum(np.random.normal(0, 1, 1000)))


def test_durgunluk_testi_adf_stationary(stationary_series):
    result = durgunluk_testi(stationary_series, test='adf')
    assert result['test'] == 'ADF'
    assert result['duragan'] == True
    assert 'istatistik' in result
    assert 'p_value' in result


def test_durgunluk_testi_adf_non_stationary(non_stationary_series):
    result = durgunluk_testi(non_stationary_series, test='adf')
    assert result['test'] == 'ADF'
    assert result['duragan'] == False


def test_durgunluk_testi_kpss_stationary(stationary_series):
    result = durgunluk_testi(stationary_series, test='kpss')
    assert result['test'] == 'KPSS'
    assert result['duragan'] == True


def test_durgunluk_testi_kpss_non_stationary(non_stationary_series):
    result = durgunluk_testi(non_stationary_series, test='kpss')
    assert result['test'] == 'KPSS'
    assert result['duragan'] == False


def test_durgunluk_testi_pp_stationary(stationary_series):
    result = durgunluk_testi(stationary_series, test='pp')
    assert result['test'] == 'PP (ADF approx)'
    assert result['duragan'] == True


def test_durgunluk_testi_pp_non_stationary(non_stationary_series):
    result = durgunluk_testi(non_stationary_series, test='pp')
    assert result['test'] == 'PP (ADF approx)'
    assert result['duragan'] == False


def test_durgunluk_testi_missing_statsmodels(stationary_series):
    with patch.dict(sys.modules, {'statsmodels.tsa.stattools': None}):
        result = durgunluk_testi(stationary_series, test='adf')
        assert 'hata' in result
        assert 'statsmodels' in result['hata']


def test_durgunluk_testi_exception():
    # Passed a series that is too short for adfuller, triggering an exception
    short_series = pd.Series([1.0, 2.0])
    result = durgunluk_testi(short_series, test='adf')
    assert 'hata' in result
    assert isinstance(result['hata'], str)

import pytest
import pandas as pd
import numpy as np
from scripts.analiz import ols_regresyon

def test_ols_regresyon_basari():
    np.random.seed(42)
    X = pd.DataFrame({'a': np.random.rand(100), 'b': np.random.rand(100)})
    y = 2 + 3 * X['a'] + 4 * X['b'] + np.random.randn(100) * 0.1

    result = ols_regresyon(y, X)

    assert 'hata' not in result
    assert 'r_kare' in result
    assert result['r_kare'] > 0.9
    assert 'a' in result['katsayilar']
    assert 'b' in result['katsayilar']
    assert 'const' in result['katsayilar']

def test_ols_regresyon_yetersiz_veri():
    y = pd.Series([None, None, None, None], dtype=float)
    X = pd.DataFrame({'a': [1.0, None, 3.0, 4.0]})

    with pytest.raises(ValueError):
        ols_regresyon(y, X)

def test_ols_regresyon_missing_statsmodels():
    """Test that ols_regresyon returns an error message when statsmodels is not installed."""
    import sys
    from unittest.mock import MagicMock, patch

    with patch.dict(sys.modules, {'statsmodels': None, 'statsmodels.api': None}):
        # Reload the module to force the function to re-evaluate the try/except block.
        # However, since the import happens inside the function, patching sys.modules is enough.
        from scripts.analiz import ols_regresyon
        y = pd.Series([1, 2, 3])
        X = pd.DataFrame({'a': [1, 2, 3]})
        result = ols_regresyon(y, X)
        assert 'hata' in result
        assert 'statsmodels paketi yuklu degil' in result['hata']

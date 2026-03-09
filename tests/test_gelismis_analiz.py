import pytest
import pandas as pd
from scripts.gelismis_analiz import frekans_donusumu

def test_frekans_donusumu_missing_datetimeindex():
    """Test that frekans_donusumu raises ValueError when DataFrame doesn't have DatetimeIndex."""
    # Create a DataFrame with default RangeIndex
    df = pd.DataFrame({'deger': [10, 20, 30]})

    with pytest.raises(ValueError, match="DataFrame'in tarih indexi olmalı"):
        frekans_donusumu(df, hedef_frekans='MS', metot='mean')

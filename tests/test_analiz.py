import pytest
import pandas as pd
import numpy as np
from scripts.analiz import korelasyon_analizi

def test_korelasyon_analizi_basic():
    """Test korelasyon_analizi with a basic dataframe of known correlations."""

    # Create a simple dataset
    # A and B are perfectly positively correlated
    # A and C are perfectly negatively correlated
    # A and D are uncorrelated
    data = {
        'A': [1, 2, 3, 4, 5],
        'B': [2, 4, 6, 8, 10],
        'C': [5, 4, 3, 2, 1],
        'D': [1, 0, 1, 0, 1]
    }
    df = pd.DataFrame(data)

    result = korelasyon_analizi(df)

    # Check if correct keys are returned
    assert 'matris' in result
    assert 'yorumlar' in result

    # Check correlation matrix
    matris = result['matris']
    assert np.isclose(matris.loc['A', 'B'], 1.0)
    assert np.isclose(matris.loc['A', 'C'], -1.0)

    # Check yorumlar structure
    yorumlar = result['yorumlar']
    assert isinstance(yorumlar, list)

    # Check some comments
    ab_yorum = next(y for y in yorumlar if (y['seri1'] == 'A' and y['seri2'] == 'B') or (y['seri1'] == 'B' and y['seri2'] == 'A'))
    assert ab_yorum['r'] == 1.0
    assert ab_yorum['guc'] == 'cok guclu'
    assert ab_yorum['yon'] == 'pozitif'

    ac_yorum = next(y for y in yorumlar if (y['seri1'] == 'A' and y['seri2'] == 'C') or (y['seri1'] == 'C' and y['seri2'] == 'A'))
    assert ac_yorum['r'] == -1.0
    assert ac_yorum['guc'] == 'cok guclu'
    assert ac_yorum['yon'] == 'negatif'

def test_korelasyon_analizi_strength_categories():
    """Test the strength categories in korelasyon_analizi."""
    # Data to test all strength bands
    # 0.8 <= |r| <= 1.0: cok guclu
    # 0.6 <= |r| < 0.8: guclu
    # 0.4 <= |r| < 0.6: orta
    # 0.2 <= |r| < 0.4: zayif
    # |r| < 0.2: ihmal edilebilir

    # we can construct correlation directly but function takes dataframe.
    # it's easier to mock the corr matrix.
    df = pd.DataFrame({'X': [1,2,3], 'Y': [4,5,6], 'Z': [7,8,9]})

    with pytest.MonkeyPatch.context() as m:
        # Mock corr method of DataFrame
        mock_corr_matrix = pd.DataFrame(
            [[1.0, 0.9, 0.7, 0.5, 0.3, 0.1],
             [0.9, 1.0, 0.0, 0.0, 0.0, 0.0],
             [0.7, 0.0, 1.0, 0.0, 0.0, 0.0],
             [0.5, 0.0, 0.0, 1.0, 0.0, 0.0],
             [0.3, 0.0, 0.0, 0.0, 1.0, 0.0],
             [0.1, 0.0, 0.0, 0.0, 0.0, 1.0]],
            columns=['V1', 'V2', 'V3', 'V4', 'V5', 'V6'],
            index=['V1', 'V2', 'V3', 'V4', 'V5', 'V6']
        )

        # We don't want to mock pandas globally, just override the df's corr method
        # for this test instance.
        class MockDF:
            def corr(self, method):
                return mock_corr_matrix

        result = korelasyon_analizi(MockDF())
        yorumlar = result['yorumlar']

        # V1-V2: 0.9 -> cok guclu
        v1_v2 = next(y for y in yorumlar if y['seri1'] == 'V1' and y['seri2'] == 'V2')
        assert v1_v2['guc'] == 'cok guclu'

        # V1-V3: 0.7 -> guclu
        v1_v3 = next(y for y in yorumlar if y['seri1'] == 'V1' and y['seri2'] == 'V3')
        assert v1_v3['guc'] == 'guclu'

        # V1-V4: 0.5 -> orta
        v1_v4 = next(y for y in yorumlar if y['seri1'] == 'V1' and y['seri2'] == 'V4')
        assert v1_v4['guc'] == 'orta'

        # V1-V5: 0.3 -> zayif
        v1_v5 = next(y for y in yorumlar if y['seri1'] == 'V1' and y['seri2'] == 'V5')
        assert v1_v5['guc'] == 'zayif'

        # V1-V6: 0.1 -> ihmal edilebilir
        v1_v6 = next(y for y in yorumlar if y['seri1'] == 'V1' and y['seri2'] == 'V6')
        assert v1_v6['guc'] == 'ihmal edilebilir'

def test_korelasyon_analizi_empty_dataframe():
    """Test with an empty DataFrame or insufficient columns."""
    # Empty dataframe
    df = pd.DataFrame()
    result = korelasyon_analizi(df)
    assert result['matris'].empty
    assert result['yorumlar'] == []

    # Dataframe with 1 column
    df = pd.DataFrame({'A': [1, 2, 3]})
    result = korelasyon_analizi(df)
    assert len(result['matris'].columns) == 1
    assert result['yorumlar'] == []

def test_korelasyon_analizi_method_param():
    """Test passing different correlation methods."""
    df = pd.DataFrame({'A': [1, 2, 3, 4], 'B': [2, 4, 1, 8]})

    with pytest.MonkeyPatch.context() as m:
        class MockDF:
            def corr(self, method):
                self.called_method = method
                return pd.DataFrame({'A': [1.0, 0.5], 'B': [0.5, 1.0]}, index=['A', 'B'], columns=['A', 'B'])

        mock_df = MockDF()
        korelasyon_analizi(mock_df, metot='spearman')
        assert mock_df.called_method == 'spearman'

def test_korelasyon_analizi_nan_handling():
    """Test korelasyon_analizi with NaN values that result in NaN correlation."""
    # Creating a case where correlation calculation gives NaN
    df = pd.DataFrame({
        'A': [1, 1, 1, 1], # Constant column
        'B': [1, 2, 3, 4]
    })

    result = korelasyon_analizi(df)
    matris = result['matris']

    assert pd.isna(matris.loc['A', 'B'])

    yorumlar = result['yorumlar']
    ab_yorum = next(y for y in yorumlar if y['seri1'] == 'A' and y['seri2'] == 'B')

    # abs(NaN) will be NaN, so it falls through to 'ihmal edilebilir'
    assert np.isnan(ab_yorum['r'])
    assert ab_yorum['guc'] == 'ihmal edilebilir'

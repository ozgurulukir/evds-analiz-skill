import pytest
import pandas as pd
import numpy as np
from scripts.evds_client import EVDSClient, tanimlayici_istatistikler

@pytest.fixture
def client():
    # Instantiate client with dummy API key
    return EVDSClient(api_key="dummy_key")

def test_parse_tarih_aylik(client):
    # Test format: 2024-1, 2024-12
    df = pd.DataFrame({"Tarih": ["2024-1", "2024-12", "2023-05"]})
    result = client._parse_tarih(df, "Tarih")

    assert result.index.name == "Tarih"
    assert len(result) == 3
    assert result.index[0] == pd.Timestamp("2023-05-01")
    assert result.index[1] == pd.Timestamp("2024-01-01")
    assert result.index[2] == pd.Timestamp("2024-12-01")

def test_parse_tarih_gunluk(client):
    # Test format: 01-01-2024, 07-01-2024
    df = pd.DataFrame({"Tarih": ["01-01-2024", "07-01-2024"]})
    result = client._parse_tarih(df, "Tarih")

    assert result.index.name == "Tarih"
    assert len(result) == 2
    assert result.index[0] == pd.Timestamp("2024-01-01")
    assert result.index[1] == pd.Timestamp("2024-01-07")

def test_parse_tarih_ceyreklik(client):
    # Test format: 2024-Q1, 2024-Q4
    df = pd.DataFrame({"Tarih": ["2024-Q1", "2024-Q2", "2024-Q3", "2024-Q4"]})
    result = client._parse_tarih(df, "Tarih")

    assert result.index.name == "Tarih"
    assert len(result) == 4
    assert result.index[0] == pd.Timestamp("2024-01-01")
    assert result.index[1] == pd.Timestamp("2024-04-01")
    assert result.index[2] == pd.Timestamp("2024-07-01")
    assert result.index[3] == pd.Timestamp("2024-10-01")

def test_parse_tarih_yillik(client):
    # Test format: 2023, 2024
    df = pd.DataFrame({"Tarih": ["2023", "2024"]})
    result = client._parse_tarih(df, "Tarih")

    assert result.index.name == "Tarih"
    assert len(result) == 2
    assert result.index[0] == pd.Timestamp("2023-01-01")
    assert result.index[1] == pd.Timestamp("2024-01-01")

def test_parse_tarih_fallback(client):
    # Test fallback format e.g. 2024/01/01
    df = pd.DataFrame({"Tarih": ["01/05/2024", "15/05/2024"]})
    result = client._parse_tarih(df, "Tarih")

    assert result.index.name == "Tarih"
    assert len(result) == 2
    assert result.index[0] == pd.Timestamp("2024-05-01")
    assert result.index[1] == pd.Timestamp("2024-05-15")

def test_parse_tarih_empty_df(client):
    # Test empty dataframe
    df = pd.DataFrame({"Tarih": []})
    with pytest.raises(ValueError, match="Tarih sütunu boş."):
        client._parse_tarih(df, "Tarih")

def test_parse_tarih_invalid_format(client):
    # Test unresolvable format
    df = pd.DataFrame({"Tarih": ["invalid_date_1", "invalid_date_2"]})
    with pytest.raises(ValueError, match="Tarih formatı çözümlenemedi"):
        client._parse_tarih(df, "Tarih")

def test_parse_tarih_preserves_other_columns(client):
    # Ensure other columns are kept intact
    df = pd.DataFrame({
        "Tarih": ["2024-1", "2024-2"],
        "Değer": [10.5, 20.0]
    })
    result = client._parse_tarih(df, "Tarih")

    assert "Değer" in result.columns
    assert list(result["Değer"]) == [10.5, 20.0]
    assert result.index[0] == pd.Timestamp("2024-01-01")
    assert result.index[1] == pd.Timestamp("2024-02-01")


def test_tanimlayici_istatistikler_yetersiz_veri():
    dates = pd.date_range("2024-01-01", periods=10, freq="D")
    df = pd.DataFrame({"Değer": range(10)}, index=dates)

    result = tanimlayici_istatistikler(df)

    assert "Değer" in result
    stats = result["Değer"]
    assert stats["gozlem"] == 10
    assert stats["baslangic"] == "01.01.2024"
    assert stats["bitis"] == "10.01.2024"
    assert stats["min"] == 0
    assert stats["max"] == 9
    assert stats["ortalama"] == 4.5
    assert stats["son_deger"] == 9
    assert stats["trend"] == "Yetersiz veri"
    assert stats["eksik"] == 0

def test_tanimlayici_istatistikler_yukselis():
    dates = pd.date_range("2024-01-01", periods=12, freq="D")
    # First 6 mean: (10+10+10+10+10+10)/6 = 10
    # Last 6 mean: (12+12+12+12+12+12)/6 = 12
    # Change: (12-10)/10 * 100 = 20% (> 5%) -> Yükseliş
    values = [10] * 6 + [12] * 6
    df = pd.DataFrame({"Değer": values}, index=dates)

    result = tanimlayici_istatistikler(df)

    stats = result["Değer"]
    assert stats["gozlem"] == 12
    assert stats["trend"] == "↗ Yükseliş"

def test_tanimlayici_istatistikler_dusus():
    dates = pd.date_range("2024-01-01", periods=12, freq="D")
    # First 6 mean: (10+10+10+10+10+10)/6 = 10
    # Last 6 mean: (8+8+8+8+8+8)/6 = 8
    # Change: (8-10)/10 * 100 = -20% (< -5%) -> Düşüş
    values = [10] * 6 + [8] * 6
    df = pd.DataFrame({"Değer": values}, index=dates)

    result = tanimlayici_istatistikler(df)

    stats = result["Değer"]
    assert stats["trend"] == "↘ Düşüş"

def test_tanimlayici_istatistikler_yatay():
    dates = pd.date_range("2024-01-01", periods=12, freq="D")
    # First 6 mean: (100+100+100+100+100+100)/6 = 100
    # Last 6 mean: (102+102+102+102+102+102)/6 = 102
    # Change: (102-100)/100 * 100 = 2% (between -5% and 5%) -> Yatay
    values = [100] * 6 + [102] * 6
    df = pd.DataFrame({"Değer": values}, index=dates)

    result = tanimlayici_istatistikler(df)

    stats = result["Değer"]
    assert stats["trend"] == "→ Yatay"

def test_tanimlayici_istatistikler_ilk_6_sifir():
    dates = pd.date_range("2024-01-01", periods=12, freq="D")
    # First 6 mean: 0
    # Last 6 mean: 10
    # Should result in Yatay because ilk_6 == 0 condition
    values = [0] * 6 + [10] * 6
    df = pd.DataFrame({"Değer": values}, index=dates)

    result = tanimlayici_istatistikler(df)

    stats = result["Değer"]
    assert stats["trend"] == "→ Yatay"

def test_tanimlayici_istatistikler_eksik_veri():
    dates = pd.date_range("2024-01-01", periods=14, freq="D")
    values = [10] * 6 + [12] * 6 + [np.nan, np.nan]
    df = pd.DataFrame({"Değer": values}, index=dates)

    result = tanimlayici_istatistikler(df)

    stats = result["Değer"]
    assert stats["gozlem"] == 12  # non-nan
    assert stats["eksik"] == 2
    assert stats["trend"] == "↗ Yükseliş"  # Last 12 of the valid ones

def test_tanimlayici_istatistikler_empty_series():
    dates = pd.date_range("2024-01-01", periods=5, freq="D")
    df = pd.DataFrame({"Değer": [np.nan] * 5}, index=dates)

    result = tanimlayici_istatistikler(df)

    assert "Değer" not in result
    assert result == {}

import pytest
import pandas as pd
from scripts.evds_client import EVDSClient

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

def test_seri_ara_exact_match(client):
    result = client.seri_ara("kkm")
    assert result == {
        'TP.KKM.K1': 'DDKKM Toplam (Milyar USD)',
        'TP.KKM.K4': 'TL KKM Toplam (Milyar TL)',
    }

def test_seri_ara_case_insensitive(client):
    result = client.seri_ara("dolar")
    assert result == {'TP.DK.USD.A': 'USD/TRY'}

    result = client.seri_ara("DOLAR")
    assert result == {'TP.DK.USD.A': 'USD/TRY'}

    result2 = client.seri_ara("KkM")
    assert result2 == {
        'TP.KKM.K1': 'DDKKM Toplam (Milyar USD)',
        'TP.KKM.K4': 'TL KKM Toplam (Milyar TL)',
    }

def test_seri_ara_substring_match(client):
    # Test match when dictionary key is a substring of the input
    result = client.seri_ara("türkiye kkm verisi")
    assert result == {
        'TP.KKM.K1': 'DDKKM Toplam (Milyar USD)',
        'TP.KKM.K4': 'TL KKM Toplam (Milyar TL)',
    }

def test_seri_ara_no_match(client):
    result = client.seri_ara("büyüme")
    assert result == {}

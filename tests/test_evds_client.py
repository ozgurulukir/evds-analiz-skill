import pytest
import pandas as pd
import requests
from scripts.evds_client import EVDSClient, tanimlayici_istatistikler, istatistik_ozeti_formatla

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

def test_extract_records_list(client):
    data = [{"id": 1}, {"id": 2}]
    result = client._extract_records(data, "test_endpoint")
    assert result == data

def test_extract_records_dict_items(client):
    data = {"items": [{"id": 1}, {"id": 2}]}
    result = client._extract_records(data, "test_endpoint")
    assert result == [{"id": 1}, {"id": 2}]

def test_extract_records_dict_data(client):
    data = {"data": [{"id": 1}, {"id": 2}]}
    result = client._extract_records(data, "test_endpoint")
    assert result == [{"id": 1}, {"id": 2}]

def test_extract_records_invalid(client):
    data = {"invalid": [{"id": 1}]}
    with pytest.raises(ValueError, match="test_endpoint endpoint'i beklenen veri formatını döndürmedi."):
        client._extract_records(data, "test_endpoint")

def test_request_metadata_success(client, mocker):
    mock_get = mocker.patch.object(client, '_get_cached_json', return_value={"items": [{"kategori_id": 1}]})
    result = client._request_metadata("test_endpoint")
    assert result == {"items": [{"kategori_id": 1}]}
    mock_get.assert_called_once_with("https://evds3.tcmb.gov.tr/igmevdsms-dis/test_endpoint", timeout=30)

def test_request_metadata_http_error_403(client, mocker):
    response = requests.Response()
    response.status_code = 403
    error = requests.exceptions.HTTPError("403 Forbidden", response=response)
    mocker.patch.object(client, '_get_cached_json', side_effect=error)

    with pytest.raises(ValueError, match="API anahtarı geçersiz veya eksik. Lütfen kontrol edin."):
        client._request_metadata("test_endpoint")

def test_request_metadata_http_error_other(client, mocker):
    response = requests.Response()
    response.status_code = 500
    error = requests.exceptions.HTTPError("500 Internal Server Error", response=response)
    mocker.patch.object(client, '_get_cached_json', side_effect=error)

    with pytest.raises(requests.exceptions.HTTPError):
        client._request_metadata("test_endpoint")

def test_request_metadata_connection_error(client, mocker):
    error = requests.exceptions.ConnectionError("Connection timeout")
    mocker.patch.object(client, '_get_cached_json', side_effect=error)

    with pytest.raises(ConnectionError, match="Bağlantı hatası: Connection timeout"):
        client._request_metadata("test_endpoint")

def test_kategorileri_getir(client, mocker):
    mock_data = [{"CATEGORY_ID": 1, "NAME": "Kategori 1"}]
    # Mocking _request_metadata to return standard wrapper format that _extract_records expects
    mock_request = mocker.patch.object(client, '_request_metadata', return_value={"items": mock_data})

    # First call - hits endpoint
    df = client.kategorileri_getir()
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 1
    assert df.iloc[0]["CATEGORY_ID"] == 1
    mock_request.assert_called_once_with("categories/type=json")

    # Second call - returns cached property
    df2 = client.kategorileri_getir()
    assert df.equals(df2)
    assert mock_request.call_count == 1  # Still 1 call

def test_veri_gruplarini_getir_all(client, mocker):
    mock_data = [{"DATAGROUP_CODE": "CODE1"}]
    mock_request = mocker.patch.object(client, '_request_metadata', return_value={"items": mock_data})

    df = client.veri_gruplarini_getir()
    assert isinstance(df, pd.DataFrame)
    mock_request.assert_called_once_with("datagroups/mode=0&type=json")

def test_veri_gruplarini_getir_with_id(client, mocker):
    mock_data = [{"DATAGROUP_CODE": "CODE2"}]
    mock_request = mocker.patch.object(client, '_request_metadata', return_value={"items": mock_data})

    df = client.veri_gruplarini_getir(kategori_id=5)
    assert isinstance(df, pd.DataFrame)
    mock_request.assert_called_once_with("datagroups/mode=2&code=5&type=json")

def test_serileri_getir(client, mocker):
    mock_data = [{"SERIE_CODE": "S1"}]
    mock_request = mocker.patch.object(client, '_request_metadata', return_value={"items": mock_data})

    df = client.serileri_getir("GROUP1")
    assert isinstance(df, pd.DataFrame)
    mock_request.assert_called_once_with("serieList/type=json&code=GROUP1")

def test_veri_cek_success_single_series(client, mocker):
    mock_data = {
        "items": [
            {"Tarih": "01-01-2024", "TP_DK_USD_A": "29,5", "UNIXTIME": "123"},
            {"Tarih": "02-01-2024", "TP_DK_USD_A": "29,6", "YEARWEEK": "2024-1"}
        ]
    }
    mock_get = mocker.patch.object(client, '_get_cached_json', return_value=mock_data)

    df = client.veri_cek(
        seriler="TP.DK.USD.A",
        baslangic="01-01-2024",
        bitis="31-01-2024"
    )

    # Check parameters formatting
    expected_url = "https://evds3.tcmb.gov.tr/igmevdsms-dis/series=TP.DK.USD.A&startDate=01-01-2024&endDate=31-01-2024&type=json"
    mock_get.assert_called_once_with(expected_url, timeout=60)

    # Check that df parsed successfully and values converted
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    assert "TP_DK_USD_A" in df.columns
    assert df["TP_DK_USD_A"].iloc[0] == 29.5
    assert df["TP_DK_USD_A"].iloc[1] == 29.6

    # Check dropped columns
    assert "UNIXTIME" not in df.columns
    assert "YEARWEEK" not in df.columns
    assert df.index.name == "Tarih"

def test_veri_cek_multiple_series_and_options(client, mocker):
    mock_data = {
        "items": [
            {"Tarih": "2024-1", "S1": "10", "S2": "20"}
        ]
    }
    mock_get = mocker.patch.object(client, '_get_cached_json', return_value=mock_data)

    client.veri_cek(
        seriler=["S1", "S2"],
        baslangic="01-01-2024",
        bitis="31-12-2024",
        frekans="aylik",
        formul=["duzey", "yuzde_degisim"],
        aggregation=["ortalama", "toplam"]
    )

    expected_url = (
        "https://evds3.tcmb.gov.tr/igmevdsms-dis/series=S1-S2"
        "&startDate=01-01-2024&endDate=31-12-2024&type=json"
        "&frequency=5&formulas=0-1&aggregationTypes=avg-sum"
    )
    mock_get.assert_called_once_with(expected_url, timeout=60)

def test_veri_cek_http_error_403(client, mocker):
    response = requests.Response()
    response.status_code = 403
    error = requests.exceptions.HTTPError("403 Forbidden", response=response)
    mocker.patch.object(client, '_get_cached_json', side_effect=error)

    with pytest.raises(ValueError, match="API anahtarı geçersiz veya eksik"):
        client.veri_cek("S1", "01-01-2024", "31-01-2024")

def test_veri_cek_http_error_404(client, mocker):
    response = requests.Response()
    response.status_code = 404
    error = requests.exceptions.HTTPError("404 Not Found", response=response)
    mocker.patch.object(client, '_get_cached_json', side_effect=error)

    with pytest.raises(ValueError, match="Veri bulunamadı. URL formatını veya seri kodlarını kontrol edin."):
        client.veri_cek("S1", "01-01-2024", "31-01-2024")

def test_veri_cek_http_error_other(client, mocker):
    response = requests.Response()
    response.status_code = 500
    error = requests.exceptions.HTTPError("500 Error", response=response)
    mocker.patch.object(client, '_get_cached_json', side_effect=error)

    with pytest.raises(requests.exceptions.HTTPError):
        client.veri_cek("S1", "01-01-2024", "31-01-2024")

def test_veri_cek_connection_error(client, mocker):
    error = requests.exceptions.ConnectionError("Connection failed")
    mocker.patch.object(client, '_get_cached_json', side_effect=error)

    with pytest.raises(ConnectionError, match="Bağlantı hatası: Connection failed"):
        client.veri_cek("S1", "01-01-2024", "31-01-2024")

def test_veri_cek_empty_response(client, mocker):
    mocker.patch.object(client, '_get_cached_json', return_value={})

    with pytest.raises(ValueError, match="Veri bulunamadı. Tarih aralığını ve seri kodlarını kontrol edin."):
        client.veri_cek("S1", "01-01-2024", "31-01-2024")

def test_veri_cek_empty_items(client, mocker):
    mocker.patch.object(client, '_get_cached_json', return_value={"items": []})

    with pytest.raises(ValueError, match="Veri bulunamadı. Tarih aralığını ve seri kodlarını kontrol edin."):
        client.veri_cek("S1", "01-01-2024", "31-01-2024")


def test_seri_ara_match(client):
    result = client.seri_ara("enflasyon")
    assert "TP.FG.J0" in result
    assert result["TP.FG.J0"] == "TÜFE - Genel Endeks (2003=100)"

def test_seri_ara_partial_match(client):
    result = client.seri_ara("dolar")
    assert "TP.DK.USD.A" in result

def test_seri_ara_no_match(client):
    result = client.seri_ara("olmayan_seri")
    assert result == {}

def test_tanimlayici_istatistikler():
    dates = pd.date_range("2024-01-01", periods=15, freq="D")
    # 0 to 14, to create an upward trend
    data = {"Value": range(15), "Missing": [1] * 14 + [None]}
    df = pd.DataFrame(data, index=dates)

    stats = tanimlayici_istatistikler(df)

    assert "Value" in stats
    val_stats = stats["Value"]
    assert val_stats["gozlem"] == 15
    assert val_stats["min"] == 0
    assert val_stats["max"] == 14
    assert val_stats["son_deger"] == 14
    assert val_stats["trend"] == "↗ Yükseliş"
    assert val_stats["eksik"] == 0

    # Check handling of missing data
    assert "Missing" in stats
    assert stats["Missing"]["eksik"] == 1
    assert stats["Missing"]["gozlem"] == 14

def test_tanimlayici_istatistikler_downward_trend():
    dates = pd.date_range("2024-01-01", periods=15, freq="D")
    # 14 to 0, to create a downward trend
    data = {"Value": range(14, -1, -1)}
    df = pd.DataFrame(data, index=dates)

    stats = tanimlayici_istatistikler(df)
    assert stats["Value"]["trend"] == "↘ Düşüş"

def test_tanimlayici_istatistikler_flat_trend():
    dates = pd.date_range("2024-01-01", periods=15, freq="D")
    data = {"Value": [10] * 15}
    df = pd.DataFrame(data, index=dates)

    stats = tanimlayici_istatistikler(df)
    assert stats["Value"]["trend"] == "→ Yatay"

def test_tanimlayici_istatistikler_insufficient_data():
    dates = pd.date_range("2024-01-01", periods=5, freq="D")
    data = {"Value": range(5)}
    df = pd.DataFrame(data, index=dates)

    stats = tanimlayici_istatistikler(df)
    assert stats["Value"]["trend"] == "Yetersiz veri"

def test_istatistik_ozeti_formatla():
    mock_stats = {
        "Test Seri": {
            "baslangic": "01.01.2024",
            "bitis": "15.01.2024",
            "gozlem": 15,
            "ortalama": 7.0,
            "std": 4.47,
            "min": 0,
            "min_tarih": "01.01.2024",
            "max": 14,
            "max_tarih": "15.01.2024",
            "son_deger": 14,
            "trend": "↗ Yükseliş",
            "eksik": 1
        }
    }

    result = istatistik_ozeti_formatla(mock_stats)
    assert "Test Seri" in result
    assert "↗ Yükseliş" in result
    assert "⚠️ Eksik Veri: 1 gözlem" in result
    assert "01.01.2024 - 15.01.2024" in result

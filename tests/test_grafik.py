import os
import tempfile
import pandas as pd
import pytest
from scripts.grafik import cizgi_grafik

def test_cizgi_grafik():
    # Arrange
    # Create a dummy DataFrame with a DatetimeIndex
    dates = pd.date_range("2024-01-01", periods=5, freq="D")
    df = pd.DataFrame({
        "Seri_A": [10.5, 12.0, 11.5, 13.2, 14.1],
        "Seri_B": [5.0, 5.5, 5.2, 6.1, 6.5]
    }, index=dates)

    baslik = "Test Çizgi Grafik Başlığı"
    y_ekseni = "Değerler"

    # Use a temporary file to avoid cluttering the repository
    with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as tmp:
        dosya_adi = tmp.name

    try:
        # Act
        result_path = cizgi_grafik(
            df=df,
            baslik=baslik,
            y_ekseni=y_ekseni,
            dosya_adi=dosya_adi
        )

        # Assert
        assert result_path == dosya_adi
        assert os.path.exists(result_path)

        # Read the generated HTML file and check for expected content
        with open(result_path, "r", encoding="utf-8") as f:
            html_content = f.read()

        assert baslik in html_content
        # json.dumps escapes non-ascii characters by default unless ensure_ascii=False
        # Plotly layout includes titles which get json serialized
        import json
        assert json.dumps(y_ekseni).strip('"') in html_content
        assert "Seri_A" in html_content
        assert "Seri_B" in html_content
        assert "2024-01-01" in html_content
        assert "2024-01-05" in html_content

        # Check that Plotly is included
        assert "plotly" in html_content.lower()

    finally:
        # Cleanup
        if os.path.exists(dosya_adi):
            os.remove(dosya_adi)

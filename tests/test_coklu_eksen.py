import pytest
import os
import sys
import json
from unittest.mock import MagicMock, patch, mock_open

# We still need to mock pandas/numpy because they aren't in the environment
# and scripts.grafik imports them at the module level.
# To make it safer, we'll use a fixture or do it before importing.

@pytest.fixture(autouse=True)
def mock_dependencies():
    mock_pd = MagicMock()
    mock_np = MagicMock()
    with patch.dict(sys.modules, {'pandas': mock_pd, 'numpy': mock_np}):
        yield mock_pd, mock_np

def test_coklu_eksen_grafik_basic():
    """Test standard usage of coklu_eksen_grafik with mocked file IO."""
    from scripts.grafik import coklu_eksen_grafik

    mock_df = MagicMock()
    mock_df.columns = ['sol1', 'sag1']

    mock_seri = MagicMock()
    mock_seri.index.strftime.return_value.tolist.return_value = ['2024-01-01']
    mock_seri.values.tolist.return_value = [10.0]
    mock_df.__getitem__.return_value.dropna.return_value = mock_seri

    with patch('builtins.open', mock_open()) as mocked_file:
        returned_path = coklu_eksen_grafik(
            mock_df,
            sol_seriler=['sol1'],
            sag_seriler=['sag1'],
            baslik="Baslik",
            dosya_adi="test_coklu.html"
        )

        assert returned_path == "test_coklu.html"
        mocked_file.assert_called_once_with("test_coklu.html", 'w', encoding='utf-8')

        # Check written content
        handle = mocked_file()
        written_content = "".join(call.args[0] for call in handle.write.call_args_list)
        assert "Baslik" in written_content
        assert "yaxis2" in written_content
        assert "sol1" in written_content
        assert "sag1" in written_content

def test_coklu_eksen_grafik_missing_columns():
    """Test that missing columns are handled gracefully."""
    from scripts.grafik import coklu_eksen_grafik
    mock_df = MagicMock()
    mock_df.columns = ['sol1'] # sag1 is missing

    mock_seri = MagicMock()
    mock_seri.index.strftime.return_value.tolist.return_value = ['2024-01-01']
    mock_seri.values.tolist.return_value = [10.0]
    mock_df.__getitem__.return_value.dropna.return_value = mock_seri

    with patch('builtins.open', mock_open()) as mocked_file:
        coklu_eksen_grafik(
            mock_df,
            sol_seriler=['sol1'],
            sag_seriler=['sag1'],
            baslik="Missing Test"
        )

        handle = mocked_file()
        written_content = "".join(call.args[0] for call in handle.write.call_args_list)
        assert "sol1" in written_content
        assert "sag1" not in written_content

def test_coklu_eksen_grafik_layout():
    """Verify labels are correctly passed to layout."""
    from scripts.grafik import coklu_eksen_grafik
    mock_df = MagicMock()
    mock_df.columns = ['s1', 's2']
    mock_df.__getitem__.return_value.dropna.return_value.index.strftime.return_value.tolist.return_value = []
    mock_df.__getitem__.return_value.dropna.return_value.values.tolist.return_value = []

    with patch('builtins.open', mock_open()) as mocked_file:
        coklu_eksen_grafik(
            mock_df, ['s1'], ['s2'], "Title",
            sol_etiket="Sol Label",
            sag_etiket="Sag Label"
        )

        handle = mocked_file()
        written_content = "".join(call.args[0] for call in handle.write.call_args_list)
        assert "Sol Label" in written_content
        assert "Sag Label" in written_content

def test_coklu_eksen_grafik_palette_overflow():
    """Test that many series don't cause IndexError."""
    from scripts.grafik import coklu_eksen_grafik, PALETTE

    num_series = len(PALETTE) + 2
    sol_seriler = [f"sol{i}" for i in range(num_series)]
    sag_seriler = [f"sag{i}" for i in range(num_series)]

    mock_df = MagicMock()
    mock_df.columns = sol_seriler + sag_seriler

    mock_seri = MagicMock()
    mock_seri.index.strftime.return_value.tolist.return_value = []
    mock_seri.values.tolist.return_value = []
    mock_df.__getitem__.return_value.dropna.return_value = mock_seri

    with patch('builtins.open', mock_open()) as mocked_file:
        # This call should not raise IndexError after the fix
        returned_path = coklu_eksen_grafik(mock_df, sol_seriler, sag_seriler, "Overflow")
        assert returned_path == "grafik_coklu.html"

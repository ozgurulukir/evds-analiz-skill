import pytest
import os
import tempfile
import getpass
from unittest.mock import MagicMock, patch
from scripts.evds_client import EVDSClient

def test_cache_path_security():
    """Verify that the cache directory is user-specific and has restricted permissions."""
    with patch('requests_cache.CachedSession') as mock_session:
        client = EVDSClient(api_key="test_key")

        try:
            uid = os.getuid()
        except AttributeError:
            uid = getpass.getuser()

        expected_cache_dir = os.path.join(tempfile.gettempdir(), f'evds_cache_{uid}')
        expected_cache_path = os.path.join(expected_cache_dir, 'evds_cache')

        # Check if directory was created
        assert os.path.isdir(expected_cache_dir)

        # Check permissions on Unix
        if hasattr(os, 'getuid'):
            mode = os.stat(expected_cache_dir).st_mode
            assert (mode & 0o777) == 0o700

        # Check requests_cache call
        mock_session.assert_called_with(expected_cache_path, backend='sqlite', expire_after=3600)

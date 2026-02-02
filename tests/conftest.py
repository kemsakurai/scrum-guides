"""
Pytest configuration and shared fixtures for convert_pdf_to_md tests.
"""
import pytest
import json
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
from PIL import Image
import io


@pytest.fixture
def fixtures_dir():
    """Return the path to the fixtures directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def config_dir(fixtures_dir):
    """Return the path to the config fixtures directory."""
    return fixtures_dir / "configs"


@pytest.fixture
def pdfs_dir(fixtures_dir):
    """Return the path to the PDFs fixtures directory."""
    return fixtures_dir / "pdfs"


@pytest.fixture
def markdowns_dir(fixtures_dir):
    """Return the path to the markdowns fixtures directory."""
    return fixtures_dir / "markdowns"


@pytest.fixture
def images_dir(fixtures_dir):
    """Return the path to the images fixtures directory."""
    return fixtures_dir / "images"


@pytest.fixture
def sample_config():
    """Return a valid sample configuration dictionary."""
    return {
        "pdfs": [
            {
                "name": "Test PDF 2024",
                "url": "https://example.com/test.pdf",
                "output": "test-2024.md",
                "output_filename": "test-2024.pdf",
                "version": "2024"
            }
        ],
        "output_dir": "docs",
        "image_dir": "docs/images",
        "temp_dir": "temp"
    }


@pytest.fixture
def temp_test_dir(tmp_path):
    """Create and return a temporary test directory structure."""
    docs = tmp_path / "docs"
    images = tmp_path / "docs" / "images"
    temp = tmp_path / "temp"
    backups = tmp_path / "backups"
    
    docs.mkdir()
    images.mkdir()
    temp.mkdir()
    backups.mkdir()
    
    return {
        'base': tmp_path,
        'docs': docs,
        'images': images,
        'temp': temp,
        'backups': backups
    }


@pytest.fixture
def mock_marker_pdf():
    """Mock marker-pdf library components."""
    with patch('convert_pdf_to_md.PdfConverter') as mock_converter_class, \
         patch('convert_pdf_to_md.create_model_dict') as mock_create_model, \
         patch('convert_pdf_to_md.text_from_rendered') as mock_text_from_rendered:
        
        # Mock create_model_dict
        mock_create_model.return_value = {'model': 'mock_model'}
        
        # Mock PdfConverter instance
        mock_converter_instance = MagicMock()
        mock_converter_class.return_value = mock_converter_instance
        
        # Mock converter execution
        mock_rendered = MagicMock()
        mock_converter_instance.return_value = mock_rendered
        
        # Mock text_from_rendered output
        mock_markdown = "# Test Document\n\nThis is a test."
        mock_metadata = {'page_stats': {'pages': 1}}
        mock_images = {}
        
        mock_text_from_rendered.return_value = (mock_markdown, mock_metadata, mock_images)
        
        yield {
            'converter_class': mock_converter_class,
            'create_model': mock_create_model,
            'text_from_rendered': mock_text_from_rendered,
            'rendered': mock_rendered,
            'markdown': mock_markdown,
            'metadata': mock_metadata,
            'images': mock_images
        }


@pytest.fixture
def mock_marker_pdf_with_images():
    """Mock marker-pdf with image extraction."""
    with patch('convert_pdf_to_md.PdfConverter') as mock_converter_class, \
         patch('convert_pdf_to_md.create_model_dict') as mock_create_model, \
         patch('convert_pdf_to_md.text_from_rendered') as mock_text_from_rendered:
        
        mock_create_model.return_value = {'model': 'mock_model'}
        
        mock_converter_instance = MagicMock()
        mock_converter_class.return_value = mock_converter_instance
        
        mock_rendered = MagicMock()
        mock_converter_instance.return_value = mock_rendered
        
        # Create mock images
        mock_image = Image.new('RGB', (100, 100), color='blue')
        
        mock_markdown = "# Test\n\n![](image_0.png)\n\nSome text."
        mock_metadata = {'page_stats': {'pages': 2}}
        mock_images = {
            'image_0.png': mock_image,
            'image_1.png': b'\x89PNG\r\n\x1a\n...'  # Binary data
        }
        
        mock_text_from_rendered.return_value = (mock_markdown, mock_metadata, mock_images)
        
        yield {
            'converter_class': mock_converter_class,
            'create_model': mock_create_model,
            'text_from_rendered': mock_text_from_rendered,
            'rendered': mock_rendered,
            'markdown': mock_markdown,
            'metadata': mock_metadata,
            'images': mock_images
        }


@pytest.fixture
def mock_requests_success():
    """Mock successful requests.get()."""
    with patch('convert_pdf_to_md.requests.get') as mock_get:
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.headers = {'content-length': '1048576'}  # 1MB
        
        # Mock chunks (128KB x 8 = 1MB)
        chunk_size = 131072
        mock_response.iter_content = Mock(
            return_value=[b'x' * chunk_size for _ in range(8)]
        )
        
        mock_get.return_value = mock_response
        yield mock_get


@pytest.fixture
def mock_requests_timeout():
    """Mock requests.get() with timeout error."""
    with patch('convert_pdf_to_md.requests.get') as mock_get:
        import requests
        mock_get.side_effect = requests.exceptions.Timeout("Connection timeout")
        yield mock_get


@pytest.fixture
def mock_requests_404():
    """Mock requests.get() with 404 error."""
    with patch('convert_pdf_to_md.requests.get') as mock_get:
        import requests
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Not Found")
        mock_get.return_value = mock_response
        yield mock_get

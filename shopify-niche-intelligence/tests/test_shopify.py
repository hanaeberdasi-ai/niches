"""
Tests for Shopify verification and data extraction
"""
import pytest
from unittest.mock import Mock, patch

# Import after path is set up
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.normalization import normalize_domain, normalize_url, normalize_price
from utils.validators import is_valid_url, is_valid_domain, is_excluded_domain


class TestNormalization:
    """Tests for normalization utilities"""
    
    def test_normalize_domain_basic(self):
        """Test basic domain normalization"""
        assert normalize_domain("https://www.example.com") == "example.com"
        assert normalize_domain("http://example.com") == "example.com"
        assert normalize_domain("www.example.com") == "example.com"
        assert normalize_domain("example.com") == "example.com"
    
    def test_normalize_domain_with_path(self):
        """Test domain normalization with paths"""
        assert normalize_domain("https://example.com/page") == "example.com"
        assert normalize_domain("https://www.example.com/products/item") == "example.com"
    
    def test_normalize_domain_empty(self):
        """Test empty input"""
        assert normalize_domain("") == ""
        assert normalize_domain(None) == ""
    
    def test_normalize_url(self):
        """Test URL normalization"""
        assert normalize_url("example.com") == "https://example.com"
        assert normalize_url("http://example.com") == "https://example.com"
        assert normalize_url("https://www.example.com/") == "https://example.com"
    
    def test_normalize_price(self):
        """Test price normalization"""
        assert normalize_price("$29.99") == 29.99
        assert normalize_price("€ 15.50") == 15.50
        assert normalize_price("29.99 USD") == 29.99
        assert normalize_price("") is None
        assert normalize_price(None) is None


class TestValidators:
    """Tests for validation utilities"""
    
    def test_is_valid_url(self):
        """Test URL validation"""
        assert is_valid_url("https://example.com") is True
        assert is_valid_url("http://example.com") is True
        assert is_valid_url("example.com") is False
        assert is_valid_url("") is False
    
    def test_is_valid_domain(self):
        """Test domain validation"""
        assert is_valid_domain("example.com") is True
        assert is_valid_domain("sub.example.com") is True
        assert is_valid_domain("invalid") is False
        assert is_valid_domain("") is False
    
    def test_is_excluded_domain(self):
        """Test excluded domain detection"""
        assert is_excluded_domain("amazon.com") is True
        assert is_excluded_domain("ebay.com") is True
        assert is_excluded_domain("shopify-store.com") is False
        assert is_excluded_domain("mystore.com") is False


class TestShopifyVerification:
    """Tests for Shopify verification"""
    
    def test_shopify_indicators(self):
        """Test Shopify indicator detection"""
        from data_sources.shopify import ShopifyVerifier
        
        verifier = ShopifyVerifier()
        
        # Test with Shopify content
        shopify_content = """
        <html>
            <script src="https://cdn.shopify.com/s/files/1/0001/theme.js"></script>
            <div class="shopify-section">Content</div>
        </html>
        """
        
        indicators = verifier._check_shopify_indicators(shopify_content, {})
        assert indicators.get("is_shopify") is True
        
        # Test without Shopify content
        non_shopify_content = """
        <html>
            <div>Regular website</div>
        </html>
        """
        
        indicators = verifier._check_shopify_indicators(non_shopify_content, {})
        assert indicators.get("is_shopify") is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

"""
Base classes for data sources
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum


class DataSourceStatus(Enum):
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    RATE_LIMITED = "rate_limited"
    ERROR = "error"


@dataclass
class DataSourceResult:
    """Result from a data source query"""
    success: bool
    data: Any
    source: str
    is_estimated: bool = False
    error: Optional[str] = None
    
    @classmethod
    def success_result(cls, data: Any, source: str, is_estimated: bool = False):
        return cls(success=True, data=data, source=source, is_estimated=is_estimated)
    
    @classmethod
    def error_result(cls, error: str, source: str):
        return cls(success=False, data=None, source=source, error=error)


class BaseDataSource(ABC):
    """Base class for all data sources"""
    
    name: str = "Base Data Source"
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if this data source is available"""
        pass
    
    @abstractmethod
    def get_status(self) -> DataSourceStatus:
        """Get current status of this data source"""
        pass


class SearchDataSource(BaseDataSource):
    """Base class for search data sources"""
    
    @abstractmethod
    def search(self, query: str, **kwargs) -> DataSourceResult:
        """Perform a search query"""
        pass


class ShopifyDataSource(BaseDataSource):
    """Base class for Shopify-specific data sources"""
    
    @abstractmethod
    def verify_shopify(self, domain: str) -> bool:
        """Verify if a domain is a Shopify store"""
        pass
    
    @abstractmethod
    def get_store_info(self, domain: str) -> DataSourceResult:
        """Get information about a Shopify store"""
        pass
    
    @abstractmethod
    def get_products(self, domain: str, limit: int = 50) -> DataSourceResult:
        """Get products from a Shopify store"""
        pass


class TrendDataSource(BaseDataSource):
    """Base class for trend data sources"""
    
    @abstractmethod
    def get_trend(self, keyword: str, **kwargs) -> DataSourceResult:
        """Get trend data for a keyword"""
        pass

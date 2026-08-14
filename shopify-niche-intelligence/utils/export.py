"""
Export utilities for CSV, Excel, and JSON
"""
import json
import io
from datetime import datetime
from typing import List, Dict, Any
import pandas as pd


def prepare_export_data(data: List[Dict[str, Any]], export_type: str = "generic") -> pd.DataFrame:
    """Prepare data for export by flattening nested structures"""
    if not data:
        return pd.DataFrame()
    
    # Flatten nested dictionaries
    flattened = []
    for item in data:
        flat_item = {}
        for key, value in item.items():
            if isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    flat_item[f"{key}_{sub_key}"] = sub_value
            elif isinstance(value, list):
                flat_item[key] = ', '.join(str(v) for v in value)
            else:
                flat_item[key] = value
        flattened.append(flat_item)
    
    return pd.DataFrame(flattened)


def export_to_csv(data: List[Dict[str, Any]], filename_prefix: str = "export") -> tuple[bytes, str]:
    """Export data to CSV format"""
    df = prepare_export_data(data)
    
    buffer = io.StringIO()
    df.to_csv(buffer, index=False, encoding='utf-8')
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{filename_prefix}_{timestamp}.csv"
    
    return buffer.getvalue().encode('utf-8'), filename


def export_to_excel(data: List[Dict[str, Any]], filename_prefix: str = "export") -> tuple[bytes, str]:
    """Export data to Excel format"""
    df = prepare_export_data(data)
    
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Data')
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{filename_prefix}_{timestamp}.xlsx"
    
    return buffer.getvalue(), filename


def export_to_json(data: List[Dict[str, Any]], filename_prefix: str = "export") -> tuple[bytes, str]:
    """Export data to JSON format"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{filename_prefix}_{timestamp}.json"
    
    export_data = {
        "exported_at": datetime.now().isoformat(),
        "count": len(data),
        "data": data
    }
    
    json_str = json.dumps(export_data, indent=2, default=str)
    return json_str.encode('utf-8'), filename


def export_niches(niches: List[Dict[str, Any]]) -> Dict[str, tuple[bytes, str]]:
    """Export niches in all formats"""
    return {
        "csv": export_to_csv(niches, "niches"),
        "excel": export_to_excel(niches, "niches"),
        "json": export_to_json(niches, "niches")
    }


def export_products(products: List[Dict[str, Any]]) -> Dict[str, tuple[bytes, str]]:
    """Export products in all formats"""
    return {
        "csv": export_to_csv(products, "products"),
        "excel": export_to_excel(products, "products"),
        "json": export_to_json(products, "products")
    }


def export_stores(stores: List[Dict[str, Any]]) -> Dict[str, tuple[bytes, str]]:
    """Export stores in all formats"""
    return {
        "csv": export_to_csv(stores, "stores"),
        "excel": export_to_excel(stores, "stores"),
        "json": export_to_json(stores, "stores")
    }

"""
API Handler Module
Handles fetching real-time product information from external APIs.
"""

import requests
import json
import logging
from typing import Dict, List, Optional
from time import sleep

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ProductAPI:
    """
    Handles API interactions for product information.
    """
    
    # Mock API endpoint - In production, this would be a real API
    # Using JSONPlaceholder or a similar mock service for demonstration
    BASE_URL = "https://jsonplaceholder.typicode.com/posts"
    
    # Mock product database (simulating API responses)
    MOCK_PRODUCTS = {
        'P101': {
            'product_id': 'P101',
            'name': 'Laptop',
            'category': 'Electronics',
            'description': 'High-performance laptop for business and gaming',
            'stock_status': 'In Stock',
            'warranty_period': '12 months'
        },
        'P102': {
            'product_id': 'P102',
            'name': 'Mouse',
            'category': 'Accessories',
            'description': 'Ergonomic computer mouse',
            'stock_status': 'In Stock',
            'warranty_period': '6 months'
        },
        'P103': {
            'product_id': 'P103',
            'name': 'Keyboard',
            'category': 'Accessories',
            'description': 'Mechanical keyboard with RGB lighting',
            'stock_status': 'In Stock',
            'warranty_period': '12 months'
        },
        'P104': {
            'product_id': 'P104',
            'name': 'Monitor',
            'category': 'Electronics',
            'description': 'LED monitor with high resolution',
            'stock_status': 'In Stock',
            'warranty_period': '24 months'
        },
        'P105': {
            'product_id': 'P105',
            'name': 'Webcam',
            'category': 'Accessories',
            'description': 'HD webcam for video conferencing',
            'stock_status': 'In Stock',
            'warranty_period': '12 months'
        },
        'P106': {
            'product_id': 'P106',
            'name': 'Headphones',
            'category': 'Audio',
            'description': 'Wireless noise-cancelling headphones',
            'stock_status': 'In Stock',
            'warranty_period': '12 months'
        },
        'P107': {
            'product_id': 'P107',
            'name': 'USB Cable',
            'category': 'Accessories',
            'description': 'USB-C to USB-A cable',
            'stock_status': 'In Stock',
            'warranty_period': '3 months'
        },
        'P108': {
            'product_id': 'P108',
            'name': 'External Hard Drive',
            'category': 'Storage',
            'description': 'Portable external hard drive',
            'stock_status': 'In Stock',
            'warranty_period': '24 months'
        },
        'P109': {
            'product_id': 'P109',
            'name': 'Wireless Mouse',
            'category': 'Accessories',
            'description': 'Wireless optical mouse',
            'stock_status': 'In Stock',
            'warranty_period': '6 months'
        },
        'P110': {
            'product_id': 'P110',
            'name': 'Laptop Charger',
            'category': 'Accessories',
            'description': 'Universal laptop charger adapter',
            'stock_status': 'In Stock',
            'warranty_period': '6 months'
        }
    }
    
    def __init__(self, use_mock: bool = True):
        """
        Initialize API handler.
        
        Args:
            use_mock: If True, use mock data instead of real API calls
        """
        self.use_mock = use_mock
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'SalesAnalyticsSystem/1.0'
        })
    
    def fetch_product_info(self, product_id: str) -> Optional[Dict]:
        """
        Fetch product information from API.
        
        Args:
            product_id: Product ID to fetch information for
            
        Returns:
            Dictionary containing product information or None if not found
        """
        if self.use_mock:
            return self._fetch_mock_product(product_id)
        else:
            return self._fetch_api_product(product_id)
    
    def _fetch_mock_product(self, product_id: str) -> Optional[Dict]:
        """
        Fetch product from mock database.
        
        Args:
            product_id: Product ID
            
        Returns:
            Product information dictionary or None
        """
        # Simulate API delay
        sleep(0.1)
        
        product = self.MOCK_PRODUCTS.get(product_id)
        if product:
            logger.info(f"Fetched product info for {product_id}")
        else:
            logger.warning(f"Product {product_id} not found in mock database")
        
        return product
    
    def _fetch_api_product(self, product_id: str) -> Optional[Dict]:
        """
        Fetch product from real API endpoint.
        
        Args:
            product_id: Product ID
            
        Returns:
            Product information dictionary or None
        """
        try:
            # In a real scenario, this would be a product-specific endpoint
            # e.g., f"{BASE_URL}/products/{product_id}"
            response = self.session.get(
                f"{self.BASE_URL}/{product_id.replace('P', '')}",
                timeout=5
            )
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Successfully fetched product info for {product_id} from API")
            
            # Transform API response to our format
            return {
                'product_id': product_id,
                'name': data.get('title', 'Unknown'),
                'category': 'Unknown',
                'description': data.get('body', 'No description available'),
                'stock_status': 'Unknown',
                'warranty_period': 'Unknown'
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed for {product_id}: {e}")
            return None
    
    def fetch_multiple_products(self, product_ids: List[str]) -> Dict[str, Dict]:
        """
        Fetch information for multiple products.
        
        Args:
            product_ids: List of product IDs
            
        Returns:
            Dictionary mapping product_id to product information
        """
        results = {}
        unique_product_ids = list(set(product_ids))
        
        logger.info(f"Fetching information for {len(unique_product_ids)} unique products")
        
        for product_id in unique_product_ids:
            product_info = self.fetch_product_info(product_id)
            if product_info:
                results[product_id] = product_info
        
        logger.info(f"Successfully fetched {len(results)} products")
        return results
    
    def enrich_records_with_product_info(self, records: List[Dict]) -> List[Dict]:
        """
        Enrich sales records with product information from API.
        
        Args:
            records: List of sales records
            
        Returns:
            List of enriched sales records
        """
        # Get unique product IDs
        product_ids = [record.get('ProductID') for record in records if record.get('ProductID')]
        
        # Fetch product information
        product_info_map = self.fetch_multiple_products(product_ids)
        
        # Enrich records
        enriched_records = []
        for record in records:
            product_id = record.get('ProductID')
            if product_id in product_info_map:
                record['ProductInfo'] = product_info_map[product_id]
            else:
                record['ProductInfo'] = None
            enriched_records.append(record)
        
        return enriched_records


# ============================================================================
# PART 3: API INTEGRATION - DummyJSON API
# ============================================================================

def fetch_all_products():
    """
    Fetches all products from DummyJSON API

    Returns: list of product dictionaries

    Expected Output Format:
    [
        {
            'id': 1,
            'title': 'iPhone 9',
            'category': 'smartphones',
            'brand': 'Apple',
            'price': 549,
            'rating': 4.69
        },
        ...
    ]

    Requirements:
    - Fetch all available products (use limit=100)
    - Handle connection errors with try-except
    - Return empty list if API fails
    - Print status message (success/failure)
    """
    BASE_URL = "https://dummyjson.com/products"
    
    try:
        # Fetch all products with limit=100
        response = requests.get(f"{BASE_URL}?limit=100", timeout=10)
        response.raise_for_status()
        
        data = response.json()
        products = data.get('products', [])
        
        # Extract only required fields
        result = []
        for product in products:
            result.append({
                'id': product.get('id'),
                'title': product.get('title'),
                'category': product.get('category'),
                'brand': product.get('brand'),
                'price': product.get('price'),
                'rating': product.get('rating')
            })
        
        print(f"✓ Successfully fetched {len(result)} products from DummyJSON API")
        logger.info(f"Successfully fetched {len(result)} products from DummyJSON API")
        
        return result
        
    except requests.exceptions.RequestException as e:
        error_msg = f"Failed to fetch products from API: {e}"
        print(f"✗ {error_msg}")
        logger.error(error_msg)
        return []
    except Exception as e:
        error_msg = f"Unexpected error while fetching products: {e}"
        print(f"✗ {error_msg}")
        logger.error(error_msg)
        return []


def create_product_mapping(api_products):
    """
    Creates a mapping of product IDs to product info

    Parameters: api_products from fetch_all_products()

    Returns: dictionary mapping product IDs to info

    Expected Output Format:
    {
        1: {'title': 'iPhone 9', 'category': 'smartphones', 'brand': 'Apple', 'rating': 4.69},
        2: {'title': 'iPhone X', 'category': 'smartphones', 'brand': 'Apple', 'rating': 4.44},
        ...
    }
    """
    product_mapping = {}
    
    for product in api_products:
        product_id = product.get('id')
        if product_id is not None:
            product_mapping[product_id] = {
                'title': product.get('title'),
                'category': product.get('category'),
                'brand': product.get('brand'),
                'rating': product.get('rating')
            }
    
    logger.info(f"Created product mapping for {len(product_mapping)} products")
    return product_mapping


# ============================================================================
# TASK 3.2: ENRICH SALES DATA
# ============================================================================

def enrich_sales_data(transactions, product_mapping):
    """
    Enriches transaction data with API product information

    Parameters:
    - transactions: list of transaction dictionaries
    - product_mapping: dictionary from create_product_mapping()

    Returns: list of enriched transaction dictionaries

    Expected Output Format (each transaction):
    {
        'TransactionID': 'T001',
        'Date': '2024-12-01',
        'ProductID': 'P101',
        'ProductName': 'Laptop',
        'Quantity': 2,
        'UnitPrice': 45000.0,
        'CustomerID': 'C001',
        'Region': 'North',
        # NEW FIELDS ADDED FROM API:
        'API_Category': 'laptops',
        'API_Brand': 'Apple',
        'API_Rating': 4.7,
        'API_Match': True  # True if enrichment successful, False otherwise
    }

    Enrichment Logic:
    - Extract numeric ID from ProductID (P101 → 101, P5 → 5)
    - Map internal product IDs to API range (P101-P110 → 1-10)
    - If ID exists in product_mapping, add API fields
    - If ID doesn't exist, set API_Match to False and other fields to None
    - Handle all errors gracefully
    """
    # Mapping from internal product IDs to API product IDs
    # This maps P101-P110 to API products 1-10 for meaningful enrichment
    ID_MAPPING = {
        101: 1,   # Laptop products
        102: 2,   # Mouse/Accessories
        103: 3,   # Keyboard
        104: 4,   # Monitor
        105: 5,   # Webcam
        106: 6,   # Headphones
        107: 7,   # USB Cable/Accessories
        108: 8,   # External Storage
        109: 9,   # Wireless Mouse
        110: 10   # Laptop Charger/Accessories
    }
    
    enriched_transactions = []
    
    for transaction in transactions:
        # Create a copy to avoid modifying original
        enriched_transaction = transaction.copy()
        
        # Extract numeric ID from ProductID (P101 → 101, P5 → 5)
        product_id = transaction.get('ProductID', '')
        numeric_id = None
        
        try:
            if product_id and product_id.startswith('P'):
                # Remove 'P' prefix and convert to integer
                numeric_id_str = product_id[1:]  # Remove 'P'
                numeric_id = int(numeric_id_str)
                
                # Map internal ID to API ID range
                # If numeric_id is in our mapping, use the mapped value
                # Otherwise, use it directly (for IDs already in range 1-100)
                if numeric_id in ID_MAPPING:
                    api_id = ID_MAPPING[numeric_id]
                elif 1 <= numeric_id <= 100:
                    api_id = numeric_id
                else:
                    api_id = None
                
                numeric_id = api_id
                
        except (ValueError, AttributeError) as e:
            logger.debug(f"Could not extract numeric ID from ProductID '{product_id}': {e}")
            numeric_id = None
        
        # Try to match with product_mapping
        if numeric_id is not None and numeric_id in product_mapping:
            product_info = product_mapping[numeric_id]
            enriched_transaction['API_Category'] = product_info.get('category')
            enriched_transaction['API_Brand'] = product_info.get('brand')
            enriched_transaction['API_Rating'] = product_info.get('rating')
            enriched_transaction['API_Match'] = True
        else:
            # No match found
            enriched_transaction['API_Category'] = None
            enriched_transaction['API_Brand'] = None
            enriched_transaction['API_Rating'] = None
            enriched_transaction['API_Match'] = False
        
        enriched_transactions.append(enriched_transaction)
    
    logger.info(f"Enriched {len(enriched_transactions)} transactions")
    matched_count = sum(1 for t in enriched_transactions if t.get('API_Match', False))
    logger.info(f"Successfully matched {matched_count} transactions with API data")
    
    return enriched_transactions


def save_enriched_data(enriched_transactions, filename='data/enriched_sales_data.txt'):
    """
    Saves enriched transactions back to file

    Expected File Format:
    TransactionID|Date|ProductID|ProductName|Quantity|UnitPrice|CustomerID|Region|API_Category|API_Brand|API_Rating|API_Match
    T001|2024-12-01|P101|Laptop|2|45000.0|C001|North|laptops|Apple|4.7|True
    ...

    Requirements:
    - Create output file with all original + new fields
    - Use pipe delimiter
    - Handle None values appropriately
    """
    import os
    
    # Create data directory if it doesn't exist
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    # Define header with all fields
    header = [
        'TransactionID', 'Date', 'ProductID', 'ProductName',
        'Quantity', 'UnitPrice', 'CustomerID', 'Region',
        'API_Category', 'API_Brand', 'API_Rating', 'API_Match'
    ]
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            # Write header
            f.write('|'.join(header) + '\n')
            
            # Write transactions
            for transaction in enriched_transactions:
                row = []
                for field in header:
                    value = transaction.get(field, '')
                    
                    # Handle None values
                    if value is None:
                        value = ''
                    # Convert boolean to string
                    elif isinstance(value, bool):
                        value = str(value)
                    # Convert numeric types to string
                    elif isinstance(value, (int, float)):
                        value = str(value)
                    else:
                        value = str(value)
                    
                    row.append(value)
                
                f.write('|'.join(row) + '\n')
        
        print(f"✓ Successfully saved {len(enriched_transactions)} enriched transactions to {filename}")
        logger.info(f"Successfully saved {len(enriched_transactions)} enriched transactions to {filename}")
        
    except Exception as e:
        error_msg = f"Failed to save enriched data to file: {e}"
        print(f"✗ {error_msg}")
        logger.error(error_msg)
        raise

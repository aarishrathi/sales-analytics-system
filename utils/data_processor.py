"""
Data Processor Module
Handles data validation, cleaning, and analysis of sales data.
"""

import re
from typing import List, Dict, Tuple, Optional
from datetime import datetime
import logging
from collections import defaultdict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def validate_transaction_id(transaction_id: str) -> bool:
    """
    Validate transaction ID (must start with 'T').
    
    Args:
        transaction_id: Transaction ID string
        
    Returns:
        True if valid (starts with 'T'), False otherwise
    """
    if not transaction_id:
        return False
    return transaction_id.strip().startswith('T')


def validate_product_id(product_id: str) -> bool:
    """
    Validate product ID (must start with 'P').
    
    Args:
        product_id: Product ID string
        
    Returns:
        True if valid (starts with 'P'), False otherwise
    """
    if not product_id:
        return False
    return product_id.strip().startswith('P')


def validate_customer_id(customer_id: str) -> bool:
    """
    Validate customer ID (must start with 'C').
    
    Args:
        customer_id: Customer ID string
        
    Returns:
        True if valid (starts with 'C'), False otherwise
    """
    if not customer_id:
        return False
    return customer_id.strip().startswith('C')


def validate_date(date_str: str) -> bool:
    """
    Validate date format (YYYY-MM-DD).
    
    Args:
        date_str: Date string
        
    Returns:
        True if valid, False otherwise
    """
    if not date_str:
        return False
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False


def validate_and_filter(transactions, region=None, min_amount=None, max_amount=None):
    """
    Validates transactions and applies optional filters

    Parameters:
    - transactions: list of transaction dictionaries
    - region: filter by specific region (optional)
    - min_amount: minimum transaction amount (Quantity * UnitPrice) (optional)
    - max_amount: maximum transaction amount (optional)

    Returns: tuple (valid_transactions, invalid_count, filter_summary)

    Expected Output Format:
    (
        [list of valid filtered transactions],
        5,  # count of invalid transactions
        {
            'total_input': 100,
            'invalid': 5,
            'filtered_by_region': 20,
            'filtered_by_amount': 10,
            'final_count': 65
        }
    )

    Validation Rules:
    - Quantity must be > 0
    - UnitPrice must be > 0
    - All required fields must be present
    - TransactionID must start with 'T'
    - ProductID must start with 'P'
    - CustomerID must start with 'C'

    Filter Display:
    - Print available regions to user before filtering
    - Print transaction amount range (min/max) to user
    - Show count of records after each filter applied
    """
    total_input = len(transactions)
    valid_transactions = []
    invalid_count = 0
    
    # Step 1: Validate transactions
    for transaction in transactions:
        is_valid = True
        errors = []
        
        # Check required fields
        required_fields = ['TransactionID', 'Date', 'ProductID', 'ProductName', 
                          'Quantity', 'UnitPrice', 'CustomerID', 'Region']
        for field in required_fields:
            if field not in transaction or not transaction[field]:
                is_valid = False
                errors.append(f"Missing {field}")
        
        if not is_valid:
            invalid_count += 1
            continue
        
        # Validate TransactionID
        if not validate_transaction_id(transaction['TransactionID']):
            is_valid = False
            errors.append("TransactionID must start with 'T'")
        
        # Validate ProductID
        if not validate_product_id(transaction['ProductID']):
            is_valid = False
            errors.append("ProductID must start with 'P'")
        
        # Validate CustomerID
        if not validate_customer_id(transaction['CustomerID']):
            is_valid = False
            errors.append("CustomerID must start with 'C'")
        
        # Validate Quantity
        quantity = transaction.get('Quantity', 0)
        if not isinstance(quantity, (int, float)) or quantity <= 0:
            is_valid = False
            errors.append(f"Quantity must be > 0, got {quantity}")
        
        # Validate UnitPrice
        unit_price = transaction.get('UnitPrice', 0)
        if not isinstance(unit_price, (int, float)) or unit_price <= 0:
            is_valid = False
            errors.append(f"UnitPrice must be > 0, got {unit_price}")
        
        if is_valid:
            # Calculate transaction amount
            transaction['TotalAmount'] = quantity * unit_price
            valid_transactions.append(transaction)
        else:
            invalid_count += 1
            logger.debug(f"Invalid transaction {transaction.get('TransactionID', 'Unknown')}: {', '.join(errors)}")
    
    # Step 2: Display available regions and amount range
    if valid_transactions:
        # Get unique regions
        regions = sorted(set(t['Region'] for t in valid_transactions))
        print(f"\nAvailable regions: {', '.join(regions)}")
        
        # Calculate amount range
        amounts = [t['TotalAmount'] for t in valid_transactions]
        min_amount_available = min(amounts)
        max_amount_available = max(amounts)
        print(f"Transaction amount range: ₹{min_amount_available:,.2f} - ₹{max_amount_available:,.2f}")
        print(f"Total valid transactions before filtering: {len(valid_transactions)}")
    
    # Step 3: Apply filters
    filtered_by_region = 0
    filtered_by_amount = 0
    filtered_transactions = valid_transactions.copy()
    
    # Filter by region
    if region:
        before_count = len(filtered_transactions)
        filtered_transactions = [t for t in filtered_transactions if t['Region'] == region]
        filtered_by_region = before_count - len(filtered_transactions)
        print(f"\nFiltering by region '{region}':")
        print(f"  Records before filter: {before_count}")
        print(f"  Records after filter: {len(filtered_transactions)}")
        print(f"  Records filtered out: {filtered_by_region}")
    
    # Filter by min_amount
    if min_amount is not None:
        before_count = len(filtered_transactions)
        filtered_transactions = [t for t in filtered_transactions if t['TotalAmount'] >= min_amount]
        filtered_by_amount = before_count - len(filtered_transactions)
        print(f"\nFiltering by minimum amount ₹{min_amount:,.2f}:")
        print(f"  Records before filter: {before_count}")
        print(f"  Records after filter: {len(filtered_transactions)}")
        print(f"  Records filtered out: {filtered_by_amount}")
    
    # Filter by max_amount
    if max_amount is not None:
        before_count = len(filtered_transactions)
        filtered_transactions = [t for t in filtered_transactions if t['TotalAmount'] <= max_amount]
        filtered_by_amount = before_count - len(filtered_transactions)
        print(f"\nFiltering by maximum amount ₹{max_amount:,.2f}:")
        print(f"  Records before filter: {before_count}")
        print(f"  Records after filter: {len(filtered_transactions)}")
        print(f"  Records filtered out: {filtered_by_amount}")
    
    # Create filter summary
    filter_summary = {
        'total_input': total_input,
        'invalid': invalid_count,
        'filtered_by_region': filtered_by_region,
        'filtered_by_amount': filtered_by_amount,
        'final_count': len(filtered_transactions)
    }
    
    print(f"\nFinal summary:")
    print(f"  Total input transactions: {total_input}")
    print(f"  Invalid transactions: {invalid_count}")
    print(f"  Valid transactions after filtering: {len(filtered_transactions)}")
    
    return filtered_transactions, invalid_count, filter_summary


# Legacy functions for backward compatibility
def validate_record(record: Dict) -> Tuple[bool, List[str]]:
    """
    Validate a single sales record (legacy function).
    """
    errors = []
    
    # Validate TransactionID (must start with 'T')
    transaction_id = record.get('TransactionID', '').strip()
    if not validate_transaction_id(transaction_id):
        errors.append(f"Invalid TransactionID: {transaction_id} (must start with 'T')")
    
    # Validate ProductID
    if not validate_product_id(record.get('ProductID', '')):
        errors.append(f"Invalid ProductID: {record.get('ProductID')}")
    
    # Validate CustomerID (MANDATORY - cannot be empty)
    customer_id = record.get('CustomerID', '').strip()
    if not customer_id:
        errors.append("Missing CustomerID")
    elif not validate_customer_id(customer_id):
        errors.append(f"Invalid CustomerID format: {customer_id}")
    
    # Validate Date
    if not validate_date(record.get('Date', '')):
        errors.append(f"Invalid Date: {record.get('Date')}")
    
    # Validate Quantity (must be positive integer)
    quantity = record.get('Quantity', 0)
    if not isinstance(quantity, (int, float)) or quantity <= 0:
        errors.append(f"Invalid Quantity: {quantity} (must be positive)")
    
    # Validate UnitPrice (must be positive)
    unit_price = record.get('UnitPrice', 0)
    if not isinstance(unit_price, (int, float)) or unit_price <= 0:
        errors.append(f"Invalid UnitPrice: {unit_price} (must be positive)")
    
    # Validate Region (MANDATORY - cannot be empty)
    region = record.get('Region', '').strip()
    if not region:
        errors.append("Missing Region")
    
    is_valid = len(errors) == 0
    return is_valid, errors


def clean_and_validate_records(records: List[Dict]) -> Tuple[List[Dict], List[Dict], List[str]]:
    """
    Clean and validate sales records (legacy function).
    """
    valid_records = []
    invalid_records = []
    all_errors = []
    
    total_records = len(records)
    
    for record in records:
        is_valid, errors = validate_record(record)
        
        if is_valid:
            # Calculate total amount
            record['TotalAmount'] = record['Quantity'] * record['UnitPrice']
            valid_records.append(record)
        else:
            invalid_records.append(record)
            error_msg = f"Record {record.get('TransactionID', 'Unknown')}: {', '.join(errors)}"
            all_errors.append(error_msg)
            logger.debug(error_msg)
    
    # Print validation output as required
    print(f"Total records parsed: {total_records}")
    print(f"Invalid records removed: {len(invalid_records)}")
    print(f"Valid records after cleaning: {len(valid_records)}")
    
    logger.info(f"Validation complete: {len(valid_records)} valid, {len(invalid_records)} invalid records")
    return valid_records, invalid_records, all_errors


def calculate_sales_by_region(records: List[Dict]) -> Dict[str, float]:
    """
    Calculate total sales by region.
    
    Args:
        records: List of valid sales records
        
    Returns:
        Dictionary with region as key and total sales as value
    """
    sales_by_region = defaultdict(float)
    
    for record in records:
        region = record.get('Region', 'Unknown')
        sales_by_region[region] += record.get('TotalAmount', 0)
    
    return dict(sales_by_region)


def calculate_sales_by_product(records: List[Dict]) -> Dict[str, Dict]:
    """
    Calculate sales statistics by product.
    
    Args:
        records: List of valid sales records
        
    Returns:
        Dictionary with product ID as key and statistics as value
    """
    product_stats = defaultdict(lambda: {
        'name': '',
        'total_quantity': 0,
        'total_revenue': 0.0,
        'transaction_count': 0,
        'avg_price': 0.0
    })
    
    for record in records:
        product_id = record.get('ProductID', 'Unknown')
        product_stats[product_id]['name'] = record.get('ProductName', '')
        product_stats[product_id]['total_quantity'] += int(record.get('Quantity', 0))
        product_stats[product_id]['total_revenue'] += record.get('TotalAmount', 0)
        product_stats[product_id]['transaction_count'] += 1
    
    # Calculate average price
    for product_id in product_stats:
        stats = product_stats[product_id]
        if stats['total_quantity'] > 0:
            stats['avg_price'] = stats['total_revenue'] / stats['total_quantity']
    
    return dict(product_stats)


def calculate_sales_by_date(records: List[Dict]) -> Dict[str, float]:
    """
    Calculate total sales by date.
    
    Args:
        records: List of valid sales records
        
    Returns:
        Dictionary with date as key and total sales as value
    """
    sales_by_date = defaultdict(float)
    
    for record in records:
        date = record.get('Date', 'Unknown')
        sales_by_date[date] += record.get('TotalAmount', 0)
    
    return dict(sales_by_date)


def calculate_customer_statistics(records: List[Dict]) -> Dict[str, Dict]:
    """
    Calculate customer purchase statistics.
    
    Args:
        records: List of valid sales records
        
    Returns:
        Dictionary with customer ID as key and statistics as value
    """
    customer_stats = defaultdict(lambda: {
        'total_spent': 0.0,
        'transaction_count': 0,
        'unique_products': set(),
        'regions': set()
    })
    
    for record in records:
        customer_id = record.get('CustomerID', '')
        if not customer_id:
            continue
            
        customer_stats[customer_id]['total_spent'] += record.get('TotalAmount', 0)
        customer_stats[customer_id]['transaction_count'] += 1
        customer_stats[customer_id]['unique_products'].add(record.get('ProductID', ''))
        customer_stats[customer_id]['regions'].add(record.get('Region', ''))
    
    # Convert sets to counts for JSON serialization
    result = {}
    for customer_id, stats in customer_stats.items():
        result[customer_id] = {
            'total_spent': stats['total_spent'],
            'transaction_count': stats['transaction_count'],
            'unique_products_count': len(stats['unique_products']),
            'regions_count': len(stats['regions'])
        }
    
    return result


def get_top_customers(records: List[Dict], top_n: int = 10) -> List[Dict]:
    """
    Get top N customers by total spending.
    
    Args:
        records: List of valid sales records
        top_n: Number of top customers to return
        
    Returns:
        List of customer dictionaries sorted by total spending
    """
    customer_stats = calculate_customer_statistics(records)
    
    top_customers = sorted(
        customer_stats.items(),
        key=lambda x: x[1]['total_spent'],
        reverse=True
    )[:top_n]
    
    result = []
    for customer_id, stats in top_customers:
        result.append({
            'CustomerID': customer_id,
            **stats
        })
    
    return result


def get_top_products(records: List[Dict], top_n: int = 10) -> List[Dict]:
    """
    Get top N products by revenue.
    
    Args:
        records: List of valid sales records
        top_n: Number of top products to return
        
    Returns:
        List of product dictionaries sorted by revenue
    """
    product_stats = calculate_sales_by_product(records)
    
    top_products = sorted(
        product_stats.items(),
        key=lambda x: x[1]['total_revenue'],
        reverse=True
    )[:top_n]
    
    result = []
    for product_id, stats in top_products:
        result.append({
            'ProductID': product_id,
            **stats
        })
    
    return result


# ============================================================================
# PART 2: DATA PROCESSING (Lists, Dictionaries & Functions)
# ============================================================================

def calculate_total_revenue(transactions):
    """
    Calculates total revenue from all transactions

    Returns: float (total revenue)

    Expected Output: Single number representing sum of (Quantity * UnitPrice)
    Example: 1545000.50
    """
    total_revenue = 0.0
    
    for transaction in transactions:
        quantity = transaction.get('Quantity', 0)
        unit_price = transaction.get('UnitPrice', 0)
        total_revenue += quantity * unit_price
    
    return total_revenue


def region_wise_sales(transactions):
    """
    Analyzes sales by region

    Returns: dictionary with region statistics

    Expected Output Format:
    {
        'North': {
            'total_sales': 450000.0,
            'transaction_count': 15,
            'percentage': 29.13
        },
        'South': {...},
        ...
    }

    Requirements:
    - Calculate total sales per region
    - Count transactions per region
    - Calculate percentage of total sales
    - Sort by total_sales in descending order
    """
    # Calculate total revenue for percentage calculation
    total_revenue = calculate_total_revenue(transactions)
    
    # Aggregate by region
    region_stats = defaultdict(lambda: {
        'total_sales': 0.0,
        'transaction_count': 0
    })
    
    for transaction in transactions:
        region = transaction.get('Region', 'Unknown')
        quantity = transaction.get('Quantity', 0)
        unit_price = transaction.get('UnitPrice', 0)
        transaction_amount = quantity * unit_price
        
        region_stats[region]['total_sales'] += transaction_amount
        region_stats[region]['transaction_count'] += 1
    
    # Calculate percentages and convert to regular dict
    result = {}
    for region, stats in region_stats.items():
        percentage = (stats['total_sales'] / total_revenue * 100) if total_revenue > 0 else 0.0
        result[region] = {
            'total_sales': stats['total_sales'],
            'transaction_count': stats['transaction_count'],
            'percentage': round(percentage, 2)
        }
    
    # Sort by total_sales in descending order
    result = dict(sorted(result.items(), key=lambda x: x[1]['total_sales'], reverse=True))
    
    return result


def top_selling_products(transactions, n=5):
    """
    Finds top n products by total quantity sold

    Returns: list of tuples

    Expected Output Format:
    [
        ('Laptop', 45, 2250000.0),  # (ProductName, TotalQuantity, TotalRevenue)
        ('Mouse', 38, 19000.0),
        ...
    ]

    Requirements:
    - Aggregate by ProductName
    - Calculate total quantity sold
    - Calculate total revenue for each product
    - Sort by TotalQuantity descending
    - Return top n products
    """
    # Aggregate by ProductName
    product_stats = defaultdict(lambda: {
        'total_quantity': 0,
        'total_revenue': 0.0
    })
    
    for transaction in transactions:
        product_name = transaction.get('ProductName', 'Unknown')
        quantity = transaction.get('Quantity', 0)
        unit_price = transaction.get('UnitPrice', 0)
        transaction_amount = quantity * unit_price
        
        product_stats[product_name]['total_quantity'] += quantity
        product_stats[product_name]['total_revenue'] += transaction_amount
    
    # Convert to list of tuples and sort by total_quantity descending
    product_list = [
        (product_name, stats['total_quantity'], stats['total_revenue'])
        for product_name, stats in product_stats.items()
    ]
    
    # Sort by TotalQuantity (index 1) in descending order
    product_list.sort(key=lambda x: x[1], reverse=True)
    
    # Return top n products
    return product_list[:n]


def customer_analysis(transactions):
    """
    Analyzes customer purchase patterns

    Returns: dictionary of customer statistics

    Expected Output Format:
    {
        'C001': {
            'total_spent': 95000.0,
            'purchase_count': 3,
            'avg_order_value': 31666.67,
            'products_bought': ['Laptop', 'Mouse', 'Keyboard']
        },
        'C002': {...},
        ...
    }

    Requirements:
    - Calculate total amount spent per customer
    - Count number of purchases
    - Calculate average order value
    - List unique products bought
    - Sort by total_spent descending
    """
    # Aggregate by CustomerID
    customer_stats = defaultdict(lambda: {
        'total_spent': 0.0,
        'purchase_count': 0,
        'products_bought': set()
    })
    
    for transaction in transactions:
        customer_id = transaction.get('CustomerID', '')
        if not customer_id:
            continue
        
        quantity = transaction.get('Quantity', 0)
        unit_price = transaction.get('UnitPrice', 0)
        transaction_amount = quantity * unit_price
        product_name = transaction.get('ProductName', '')
        
        customer_stats[customer_id]['total_spent'] += transaction_amount
        customer_stats[customer_id]['purchase_count'] += 1
        customer_stats[customer_id]['products_bought'].add(product_name)
    
    # Calculate average order value and convert sets to lists
    result = {}
    for customer_id, stats in customer_stats.items():
        avg_order_value = (stats['total_spent'] / stats['purchase_count']) if stats['purchase_count'] > 0 else 0.0
        
        result[customer_id] = {
            'total_spent': stats['total_spent'],
            'purchase_count': stats['purchase_count'],
            'avg_order_value': round(avg_order_value, 2),
            'products_bought': sorted(list(stats['products_bought']))  # Convert set to sorted list
        }
    
    # Sort by total_spent in descending order
    result = dict(sorted(result.items(), key=lambda x: x[1]['total_spent'], reverse=True))
    
    return result


# ============================================================================
# TASK 2.2: DATE-BASED ANALYSIS
# ============================================================================

def daily_sales_trend(transactions):
    """
    Analyzes sales trends by date

    Returns: dictionary sorted by date

    Expected Output Format:
    {
        '2024-12-01': {
            'revenue': 125000.0,
            'transaction_count': 8,
            'unique_customers': 6
        },
        '2024-12-02': {...},
        ...
    }

    Requirements:
    - Group by date
    - Calculate daily revenue
    - Count daily transactions
    - Count unique customers per day
    - Sort chronologically
    """
    # Aggregate by date
    daily_stats = defaultdict(lambda: {
        'revenue': 0.0,
        'transaction_count': 0,
        'unique_customers': set()
    })
    
    for transaction in transactions:
        date = transaction.get('Date', '')
        if not date:
            continue
        
        quantity = transaction.get('Quantity', 0)
        unit_price = transaction.get('UnitPrice', 0)
        transaction_amount = quantity * unit_price
        customer_id = transaction.get('CustomerID', '')
        
        daily_stats[date]['revenue'] += transaction_amount
        daily_stats[date]['transaction_count'] += 1
        if customer_id:
            daily_stats[date]['unique_customers'].add(customer_id)
    
    # Convert sets to counts and create result dictionary
    result = {}
    for date, stats in daily_stats.items():
        result[date] = {
            'revenue': stats['revenue'],
            'transaction_count': stats['transaction_count'],
            'unique_customers': len(stats['unique_customers'])
        }
    
    # Sort chronologically by date
    result = dict(sorted(result.items()))
    
    return result


def find_peak_sales_day(transactions):
    """
    Identifies the date with highest revenue

    Returns: tuple (date, revenue, transaction_count)

    Expected Output Format:
    ('2024-12-15', 185000.0, 12)
    """
    daily_trend = daily_sales_trend(transactions)
    
    if not daily_trend:
        return (None, 0.0, 0)
    
    # Find the date with maximum revenue
    peak_date = max(daily_trend.items(), key=lambda x: x[1]['revenue'])
    
    date = peak_date[0]
    revenue = peak_date[1]['revenue']
    transaction_count = peak_date[1]['transaction_count']
    
    return (date, revenue, transaction_count)


# ============================================================================
# TASK 2.3: PRODUCT PERFORMANCE
# ============================================================================

def low_performing_products(transactions, threshold=10):
    """
    Identifies products with low sales

    Returns: list of tuples

    Expected Output Format:
    [
        ('Webcam', 4, 12000.0),  # (ProductName, TotalQuantity, TotalRevenue)
        ('Headphones', 7, 10500.0),
        ...
    ]

    Requirements:
    - Find products with total quantity < threshold
    - Include total quantity and revenue
    - Sort by TotalQuantity ascending
    """
    # Aggregate by ProductName
    product_stats = defaultdict(lambda: {
        'total_quantity': 0,
        'total_revenue': 0.0
    })
    
    for transaction in transactions:
        product_name = transaction.get('ProductName', 'Unknown')
        quantity = transaction.get('Quantity', 0)
        unit_price = transaction.get('UnitPrice', 0)
        transaction_amount = quantity * unit_price
        
        product_stats[product_name]['total_quantity'] += quantity
        product_stats[product_name]['total_revenue'] += transaction_amount
    
    # Filter products with total quantity < threshold
    low_performing = [
        (product_name, stats['total_quantity'], stats['total_revenue'])
        for product_name, stats in product_stats.items()
        if stats['total_quantity'] < threshold
    ]
    
    # Sort by TotalQuantity ascending
    low_performing.sort(key=lambda x: x[1])
    
    return low_performing

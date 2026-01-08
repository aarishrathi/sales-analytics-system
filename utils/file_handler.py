"""
File Handler Module
Handles reading and cleaning of sales data files with encoding issues and data quality problems.
"""

from typing import List, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def read_sales_data(filename):
    """
    Reads sales data from file handling encoding issues

    Returns: list of raw lines (strings)

    Expected Output Format:
    ['T001|2024-12-01|P101|Laptop|2|45000|C001|North', ...]

    Requirements:
    - Use 'with' statement
    - Handle different encodings (try 'utf-8', 'latin-1', 'cp1252')
    - Handle FileNotFoundError with appropriate error message
    - Skip the header row
    - Remove empty lines
    """
    encodings = ['utf-8', 'latin-1', 'cp1252']
    raw_lines = []
    
    for encoding in encodings:
        try:
            with open(filename, 'r', encoding=encoding, errors='replace') as f:
                lines = f.readlines()
                # Skip header row (first line)
                if lines:
                    data_lines = lines[1:]
                    # Remove empty lines and strip whitespace
                    raw_lines = [line.strip() for line in data_lines if line.strip()]
                    logger.info(f"Successfully read file using {encoding} encoding")
                    break
        except FileNotFoundError:
            error_msg = f"Error: File '{filename}' not found. Please check the file path."
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)
        except Exception as e:
            logger.warning(f"Failed to read with {encoding}: {e}")
            continue
    
    if not raw_lines:
        # If all encodings failed, try one more time with utf-8 and raise error
        try:
            with open(filename, 'r', encoding='utf-8', errors='replace') as f:
                lines = f.readlines()
                if lines:
                    data_lines = lines[1:]
                    raw_lines = [line.strip() for line in data_lines if line.strip()]
        except FileNotFoundError:
            error_msg = f"Error: File '{filename}' not found. Please check the file path."
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)
        except Exception as e:
            logger.error(f"Failed to read file: {e}")
            raise
    
    return raw_lines


def parse_transactions(raw_lines):
    """
    Parses raw lines into clean list of dictionaries

    Returns: list of dictionaries with keys:
    ['TransactionID', 'Date', 'ProductID', 'ProductName',
     'Quantity', 'UnitPrice', 'CustomerID', 'Region']

    Expected Output Format:
    [
        {
            'TransactionID': 'T001',
            'Date': '2024-12-01',
            'ProductID': 'P101',
            'ProductName': 'Laptop',
            'Quantity': 2,           # int type
            'UnitPrice': 45000.0,    # float type
            'CustomerID': 'C001',
            'Region': 'North'
        },
        ...
    ]

    Requirements:
    - Split by pipe delimiter '|'
    - Handle commas within ProductName (remove or replace)
    - Remove commas from numeric fields and convert to proper types
    - Convert Quantity to int
    - Convert UnitPrice to float
    - Skip rows with incorrect number of fields
    """
    expected_fields = ['TransactionID', 'Date', 'ProductID', 'ProductName',
                       'Quantity', 'UnitPrice', 'CustomerID', 'Region']
    expected_field_count = len(expected_fields)
    
    transactions = []
    skipped_count = 0
    
    for line in raw_lines:
        # Split by pipe delimiter
        parts = line.split('|')
        
        # Skip rows with incorrect number of fields
        if len(parts) != expected_field_count:
            skipped_count += 1
            logger.debug(f"Skipping row with incorrect field count: {len(parts)} (expected {expected_field_count})")
            continue
        
        try:
            transaction = {}
            
            # Parse each field
            transaction['TransactionID'] = parts[0].strip()
            transaction['Date'] = parts[1].strip()
            transaction['ProductID'] = parts[2].strip()
            
            # Handle commas in ProductName (remove commas)
            product_name = parts[3].strip()
            transaction['ProductName'] = product_name.replace(',', '')
            
            # Handle commas in Quantity (remove commas, convert to int)
            quantity_str = parts[4].strip().replace(',', '')
            try:
                transaction['Quantity'] = int(float(quantity_str))  # Convert via float first to handle decimals
            except ValueError:
                logger.warning(f"Invalid Quantity value: {parts[4]}")
                transaction['Quantity'] = 0
            
            # Handle commas in UnitPrice (remove commas, convert to float)
            unit_price_str = parts[5].strip().replace(',', '')
            try:
                transaction['UnitPrice'] = float(unit_price_str)
            except ValueError:
                logger.warning(f"Invalid UnitPrice value: {parts[5]}")
                transaction['UnitPrice'] = 0.0
            
            transaction['CustomerID'] = parts[6].strip()
            transaction['Region'] = parts[7].strip()
            
            transactions.append(transaction)
            
        except Exception as e:
            skipped_count += 1
            logger.warning(f"Error parsing line: {line[:50]}... Error: {e}")
            continue
    
    if skipped_count > 0:
        logger.info(f"Skipped {skipped_count} rows with parsing errors")
    
    logger.info(f"Successfully parsed {len(transactions)} transactions")
    return transactions


# Keep legacy functions for backward compatibility
def load_sales_data(file_path: str):
    """
    Legacy function for backward compatibility.
    Loads sales data and returns parsed transactions.
    """
    raw_lines = read_sales_data(file_path)
    transactions = parse_transactions(raw_lines)
    return transactions, []

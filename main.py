"""
Sales Analytics System - Main Entry Point
Orchestrates the entire sales data processing pipeline.
"""

import os
import json
from datetime import datetime
from typing import Dict, List
import logging

from utils.file_handler import load_sales_data
from utils.data_processor import (
    clean_and_validate_records,
    calculate_sales_by_region,
    calculate_sales_by_product,
    calculate_sales_by_date,
    get_top_customers,
    get_top_products,
    calculate_customer_statistics
)
from utils.api_handler import ProductAPI

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SalesAnalyticsSystem:
    """
    Main class for the Sales Analytics System.
    """
    
    def __init__(self, data_file: str = 'data/sales_data.txt', use_mock_api: bool = True):
        """
        Initialize the Sales Analytics System.
        
        Args:
            data_file: Path to the sales data file
            use_mock_api: Whether to use mock API (True) or real API (False)
        """
        self.data_file = data_file
        self.valid_records = []
        self.invalid_records = []
        self.product_api = ProductAPI(use_mock=use_mock_api)
        self.output_dir = 'output'
        
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
    
    def load_data(self):
        """Load and parse sales data from file."""
        logger.info(f"Loading sales data from {self.data_file}")
        
        try:
            records, errors = load_sales_data(self.data_file)
            logger.info(f"Loaded {len(records)} raw records")
            
            if errors:
                logger.warning(f"Encountered {len(errors)} errors during file parsing")
            
            # Validate and clean records
            self.valid_records, self.invalid_records, validation_errors = clean_and_validate_records(records)
            
            if validation_errors:
                logger.info(f"Validation found {len(validation_errors)} issues")
            
            logger.info(f"Processing complete: {len(self.valid_records)} valid, {len(self.invalid_records)} invalid records")
            
        except Exception as e:
            logger.error(f"Failed to load data: {e}")
            raise
    
    def enrich_with_product_info(self):
        """Enrich sales records with product information from API."""
        logger.info("Enriching records with product information from API")
        self.valid_records = self.product_api.enrich_records_with_product_info(self.valid_records)
        logger.info("Product information enrichment complete")
    
    def generate_reports(self):
        """Generate comprehensive analytics reports."""
        logger.info("Generating analytics reports...")
        
        reports = {}
        
        # 1. Overall Statistics
        total_revenue = sum(record.get('TotalAmount', 0) for record in self.valid_records)
        total_transactions = len(self.valid_records)
        total_quantity = sum(record.get('Quantity', 0) for record in self.valid_records)
        avg_transaction_value = total_revenue / total_transactions if total_transactions > 0 else 0
        
        reports['overall_statistics'] = {
            'total_revenue': round(total_revenue, 2),
            'total_transactions': total_transactions,
            'total_quantity_sold': total_quantity,
            'average_transaction_value': round(avg_transaction_value, 2),
            'invalid_records_count': len(self.invalid_records),
            'data_quality_score': round((len(self.valid_records) / (len(self.valid_records) + len(self.invalid_records)) * 100), 2) if (len(self.valid_records) + len(self.invalid_records)) > 0 else 0
        }
        
        # 2. Sales by Region
        reports['sales_by_region'] = {
            region: round(amount, 2)
            for region, amount in calculate_sales_by_region(self.valid_records).items()
        }
        
        # 3. Sales by Product
        product_stats = calculate_sales_by_product(self.valid_records)
        reports['sales_by_product'] = {
            pid: {
                'name': stats['name'],
                'total_revenue': round(stats['total_revenue'], 2),
                'total_quantity': stats['total_quantity'],
                'transaction_count': stats['transaction_count'],
                'average_price': round(stats['avg_price'], 2)
            }
            for pid, stats in product_stats.items()
        }
        
        # 4. Sales by Date
        reports['sales_by_date'] = {
            date: round(amount, 2)
            for date, amount in sorted(calculate_sales_by_date(self.valid_records).items())
        }
        
        # 5. Top Customers
        reports['top_customers'] = [
            {
                'CustomerID': customer['CustomerID'],
                'total_spent': round(customer['total_spent'], 2),
                'transaction_count': customer['transaction_count'],
                'unique_products_count': customer['unique_products_count']
            }
            for customer in get_top_customers(self.valid_records, top_n=10)
        ]
        
        # 6. Top Products
        reports['top_products'] = [
            {
                'ProductID': product['ProductID'],
                'name': product['name'],
                'total_revenue': round(product['total_revenue'], 2),
                'total_quantity': product['total_quantity']
            }
            for product in get_top_products(self.valid_records, top_n=10)
        ]
        
        # 7. Customer Statistics
        customer_stats = calculate_customer_statistics(self.valid_records)
        reports['customer_statistics'] = {
            cid: {
                'total_spent': round(stats['total_spent'], 2),
                'transaction_count': stats['transaction_count'],
                'unique_products_count': stats['unique_products_count'],
                'regions_count': stats['regions_count']
            }
            for cid, stats in customer_stats.items()
        }
        
        logger.info("Reports generated successfully")
        return reports
    
    def save_reports(self, reports: Dict):
        """Save reports to JSON and text files."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save JSON report
        json_file = os.path.join(self.output_dir, f'sales_report_{timestamp}.json')
        with open(json_file, 'w') as f:
            json.dump(reports, f, indent=2)
        logger.info(f"JSON report saved to {json_file}")
        
        # Save human-readable text report
        text_file = os.path.join(self.output_dir, f'sales_report_{timestamp}.txt')
        self._generate_text_report(reports, text_file)
        logger.info(f"Text report saved to {text_file}")
        
        return json_file, text_file
    
    def _generate_text_report(self, reports: Dict, output_file: str):
        """Generate a human-readable text report."""
        with open(output_file, 'w') as f:
            f.write("=" * 80 + "\n")
            f.write("SALES ANALYTICS REPORT\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 80 + "\n\n")
            
            # Overall Statistics
            f.write("OVERALL STATISTICS\n")
            f.write("-" * 80 + "\n")
            stats = reports['overall_statistics']
            f.write(f"Total Revenue: ₹{stats['total_revenue']:,.2f}\n")
            f.write(f"Total Transactions: {stats['total_transactions']}\n")
            f.write(f"Total Quantity Sold: {stats['total_quantity_sold']}\n")
            f.write(f"Average Transaction Value: ₹{stats['average_transaction_value']:,.2f}\n")
            f.write(f"Invalid Records: {stats['invalid_records_count']}\n")
            f.write(f"Data Quality Score: {stats['data_quality_score']}%\n\n")
            
            # Sales by Region
            f.write("SALES BY REGION\n")
            f.write("-" * 80 + "\n")
            for region, amount in sorted(reports['sales_by_region'].items(), key=lambda x: x[1], reverse=True):
                f.write(f"{region}: ₹{amount:,.2f}\n")
            f.write("\n")
            
            # Top Products
            f.write("TOP 10 PRODUCTS BY REVENUE\n")
            f.write("-" * 80 + "\n")
            for i, product in enumerate(reports['top_products'], 1):
                f.write(f"{i}. {product['ProductID']} - {product['name']}: "
                       f"₹{product['total_revenue']:,.2f} ({product['total_quantity']} units)\n")
            f.write("\n")
            
            # Top Customers
            f.write("TOP 10 CUSTOMERS BY SPENDING\n")
            f.write("-" * 80 + "\n")
            for i, customer in enumerate(reports['top_customers'], 1):
                f.write(f"{i}. {customer['CustomerID']}: "
                       f"₹{customer['total_spent']:,.2f} ({customer['transaction_count']} transactions, "
                       f"{customer['unique_products_count']} unique products)\n")
            f.write("\n")
            
            # Sales by Date (Top 10 days)
            f.write("TOP 10 DAYS BY SALES\n")
            f.write("-" * 80 + "\n")
            sorted_dates = sorted(reports['sales_by_date'].items(), key=lambda x: x[1], reverse=True)[:10]
            for date, amount in sorted_dates:
                f.write(f"{date}: ₹{amount:,.2f}\n")
            f.write("\n")
            
            # Sales by Product (Detailed)
            f.write("DETAILED PRODUCT PERFORMANCE\n")
            f.write("-" * 80 + "\n")
            for pid, stats in sorted(reports['sales_by_product'].items(), 
                                    key=lambda x: x[1]['total_revenue'], reverse=True):
                f.write(f"\n{pid} - {stats['name']}\n")
                f.write(f"  Revenue: ₹{stats['total_revenue']:,.2f}\n")
                f.write(f"  Quantity Sold: {stats['total_quantity']}\n")
                f.write(f"  Transactions: {stats['transaction_count']}\n")
                f.write(f"  Average Price: ₹{stats['average_price']:,.2f}\n")
            
            f.write("\n" + "=" * 80 + "\n")
            f.write("END OF REPORT\n")
            f.write("=" * 80 + "\n")
    
    def run(self):
        """Execute the complete analytics pipeline."""
        logger.info("Starting Sales Analytics System")
        
        try:
            # Step 1: Load data
            self.load_data()
            
            # Step 2: Enrich with product info
            self.enrich_with_product_info()
            
            # Step 3: Generate reports
            reports = self.generate_reports()
            
            # Step 4: Save reports
            json_file, text_file = self.save_reports(reports)
            
            logger.info("Sales Analytics System completed successfully")
            logger.info(f"Reports saved to: {json_file} and {text_file}")
            
            return reports
            
        except Exception as e:
            logger.error(f"System execution failed: {e}")
            raise


def main():
    """
    Main execution function

    Workflow:
    1. Print welcome message
    2. Read sales data file (handle encoding)
    3. Parse and clean transactions
    4. Display filter options to user
       - Show available regions
       - Show transaction amount range
       - Ask if user wants to filter (y/n)
    5. If yes, ask for filter criteria and apply
    6. Validate transactions
    7. Display validation summary
    8. Perform all data analyses (call all functions from Part 2)
    9. Fetch products from API
    10. Enrich sales data with API info
    11. Save enriched data to file
    12. Generate comprehensive report
    13. Print success message with file locations

    Error Handling:
    - Wrap entire process in try-except
    - Display user-friendly error messages
    - Don't let program crash on errors
    """
    import sys
    
    # Configuration
    DATA_FILE = 'data/sales_data.txt'
    ENRICHED_DATA_FILE = 'data/enriched_sales_data.txt'
    REPORT_FILE = 'output/sales_report.txt'
    
    try:
        # Print welcome message
        print("=" * 40)
        print("SALES ANALYTICS SYSTEM")
        print("=" * 40)
        print()
        
        # Step 1: Read sales data file
        print("[1/10] Reading sales data...")
        try:
            from utils.file_handler import read_sales_data, parse_transactions
            raw_lines = read_sales_data(DATA_FILE)
            print(f"✓ Successfully read {len(raw_lines)} transactions")
        except Exception as e:
            print(f"✗ Error reading sales data: {e}")
            return
        
        # Step 2: Parse and clean transactions
        print("\n[2/10] Parsing and cleaning data...")
        try:
            transactions = parse_transactions(raw_lines)
            print(f"✓ Parsed {len(transactions)} records")
        except Exception as e:
            print(f"✗ Error parsing data: {e}")
            return
        
        # Step 3: Display filter options
        print("\n[3/10] Filter Options Available:")
        try:
            from utils.data_processor import validate_and_filter
            
            # Get regions and amount range from transactions (before filtering)
            regions = sorted(set(t.get('Region', '') for t in transactions if t.get('Region')))
            amounts = []
            for t in transactions:
                qty = t.get('Quantity', 0)
                price = t.get('UnitPrice', 0)
                if qty > 0 and price > 0:
                    amounts.append(qty * price)
            
            if amounts:
                min_amount = min(amounts)
                max_amount = max(amounts)
                print(f"Regions: {', '.join(regions)}")
                print(f"Amount Range: ₹{min_amount:,.2f} - ₹{max_amount:,.2f}")
            else:
                print("Regions: N/A")
                print("Amount Range: N/A")
            
            # Ask user if they want to filter
            print("\nDo you want to filter data? (y/n): ", end='')
            filter_choice = input().strip().lower()
            
            filtered_transactions = transactions
            invalid_count = 0
            
            if filter_choice == 'y':
                # Get filter criteria
                print("\nEnter filter criteria (press Enter to skip):")
                
                print(f"Region ({', '.join(regions)}): ", end='')
                region_filter = input().strip()
                if not region_filter or region_filter not in regions:
                    region_filter = None
                
                print("Minimum amount: ", end='')
                min_amount_input = input().strip()
                try:
                    min_amount_filter = float(min_amount_input) if min_amount_input else None
                except ValueError:
                    min_amount_filter = None
                
                print("Maximum amount: ", end='')
                max_amount_input = input().strip()
                try:
                    max_amount_filter = float(max_amount_input) if max_amount_input else None
                except ValueError:
                    max_amount_filter = None
                
                # Apply filters (this will also validate)
                filtered_transactions, invalid_count, filter_summary = validate_and_filter(
                    transactions,
                    region=region_filter,
                    min_amount=min_amount_filter,
                    max_amount=max_amount_filter
                )
                print(f"✓ Filtered to {len(filtered_transactions)} transactions")
            else:
                # Still validate but don't filter (suppress filter output by calling validate_and_filter without filters)
                # We'll validate separately to avoid duplicate output
                filtered_transactions, invalid_count, filter_summary = validate_and_filter(transactions)
        except Exception as e:
            print(f"✗ Error in filtering: {e}")
            filtered_transactions = transactions
            invalid_count = 0
        
        # Step 4: Validate transactions (already done in filter, but show summary)
        print("\n[4/10] Validating transactions...")
        valid_count = len(filtered_transactions)
        print(f"✓ Valid: {valid_count} | Invalid: {invalid_count}")
        
        # Step 5: Perform all data analyses
        print("\n[5/10] Analyzing sales data...")
        try:
            from utils.data_processor import (
                calculate_total_revenue,
                region_wise_sales,
                top_selling_products,
                customer_analysis,
                daily_sales_trend,
                find_peak_sales_day,
                low_performing_products
            )
            
            # Run all analyses (even if not all results are displayed)
            total_revenue = calculate_total_revenue(filtered_transactions)
            region_stats = region_wise_sales(filtered_transactions)
            top_products = top_selling_products(filtered_transactions, n=5)
            customer_stats = customer_analysis(filtered_transactions)
            daily_trend = daily_sales_trend(filtered_transactions)
            peak_day = find_peak_sales_day(filtered_transactions)
            low_products = low_performing_products(filtered_transactions, threshold=10)
            
            print("✓ Analysis complete")
        except Exception as e:
            print(f"✗ Error in analysis: {e}")
            return
        
        # Step 6: Fetch products from API
        print("\n[6/10] Fetching product data from API...")
        try:
            from utils.api_handler import fetch_all_products, create_product_mapping
            api_products = fetch_all_products()
            product_mapping = create_product_mapping(api_products)
            print(f"✓ Fetched {len(product_mapping)} products")
        except Exception as e:
            print(f"✗ Error fetching API data: {e}")
            product_mapping = {}
        
        # Step 7: Enrich sales data
        print("\n[7/10] Enriching sales data...")
        try:
            from utils.api_handler import enrich_sales_data
            enriched_transactions = enrich_sales_data(filtered_transactions, product_mapping)
            matched_count = sum(1 for t in enriched_transactions if t.get('API_Match', False))
            success_rate = (matched_count / len(enriched_transactions) * 100) if enriched_transactions else 0
            print(f"✓ Enriched {matched_count}/{len(enriched_transactions)} transactions ({success_rate:.1f}%)")
        except Exception as e:
            print(f"✗ Error enriching data: {e}")
            enriched_transactions = filtered_transactions
        
        # Step 8: Save enriched data
        print("\n[8/10] Saving enriched data...")
        try:
            from utils.api_handler import save_enriched_data
            save_enriched_data(enriched_transactions, ENRICHED_DATA_FILE)
            print(f"✓ Saved to: {ENRICHED_DATA_FILE}")
        except Exception as e:
            print(f"✗ Error saving enriched data: {e}")
        
        # Step 9: Generate comprehensive report
        print("\n[9/10] Generating report...")
        try:
            from utils.report_generator import generate_sales_report
            generate_sales_report(filtered_transactions, enriched_transactions, REPORT_FILE)
            print(f"✓ Report saved to: {REPORT_FILE}")
        except Exception as e:
            print(f"✗ Error generating report: {e}")
        
        # Step 10: Print success message
        print("\n[10/10] Process Complete!")
        print("=" * 40)
        print("\nGenerated Files:")
        print(f"  - Enriched Data: {ENRICHED_DATA_FILE}")
        print(f"  - Sales Report: {REPORT_FILE}")
        print("\n" + "=" * 40)
        
    except KeyboardInterrupt:
        print("\n\n✗ Process interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        logger.error(f"Unexpected error in main: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()

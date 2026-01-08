"""
Report Generator Module
Handles generation of comprehensive sales analytics reports.
"""

from datetime import datetime
from typing import List, Dict
import logging
from utils.data_processor import (
    calculate_total_revenue,
    region_wise_sales,
    top_selling_products,
    customer_analysis,
    daily_sales_trend,
    find_peak_sales_day,
    low_performing_products
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def format_currency(amount):
    """Format amount as Indian currency with commas."""
    return f"₹{amount:,.2f}"


def format_number(num):
    """Format number with commas."""
    return f"{num:,}"


def generate_sales_report(transactions, enriched_transactions, output_file='output/sales_report.txt'):
    """
    Generates a comprehensive formatted text report

    Report Must Include (in this order):

    1. HEADER
       - Report title
       - Generation date and time
       - Total records processed

    2. OVERALL SUMMARY
       - Total Revenue (formatted with commas)
       - Total Transactions
       - Average Order Value
       - Date Range of data

    3. REGION-WISE PERFORMANCE
       - Table showing each region with:
         * Total Sales Amount
         * Percentage of Total
         * Transaction Count
       - Sorted by sales amount descending

    4. TOP 5 PRODUCTS
       - Table with columns: Rank, Product Name, Quantity Sold, Revenue

    5. TOP 5 CUSTOMERS
       - Table with columns: Rank, Customer ID, Total Spent, Order Count

    6. DAILY SALES TREND
       - Table showing: Date, Revenue, Transactions, Unique Customers

    7. PRODUCT PERFORMANCE ANALYSIS
       - Best selling day
       - Low performing products (if any)
       - Average transaction value per region

    8. API ENRICHMENT SUMMARY
       - Total products enriched
       - Success rate percentage
       - List of products that couldn't be enriched
    """
    import os
    
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # Calculate all analytics
    total_revenue = calculate_total_revenue(transactions)
    total_transactions = len(transactions)
    avg_order_value = total_revenue / total_transactions if total_transactions > 0 else 0
    
    # Get date range
    dates = [t.get('Date', '') for t in transactions if t.get('Date')]
    date_range = f"{min(dates)} to {max(dates)}" if dates else "N/A"
    
    # Region-wise sales
    region_stats = region_wise_sales(transactions)
    
    # Top products
    top_products = top_selling_products(transactions, n=5)
    
    # Top customers
    customer_stats = customer_analysis(transactions)
    top_customers_list = list(customer_stats.items())[:5]
    
    # Daily sales trend
    daily_trend = daily_sales_trend(transactions)
    
    # Peak sales day
    peak_day = find_peak_sales_day(transactions)
    
    # Low performing products
    low_products = low_performing_products(transactions, threshold=10)
    
    # Average transaction value per region
    avg_by_region = {}
    for region, stats in region_stats.items():
        if stats['transaction_count'] > 0:
            avg_by_region[region] = stats['total_sales'] / stats['transaction_count']
    
    # API enrichment summary
    total_enriched = len(enriched_transactions)
    matched_count = sum(1 for t in enriched_transactions if t.get('API_Match', False))
    success_rate = (matched_count / total_enriched * 100) if total_enriched > 0 else 0
    
    # Products that couldn't be enriched
    unmatched_products = set()
    for t in enriched_transactions:
        if not t.get('API_Match', False):
            unmatched_products.add(t.get('ProductID', 'Unknown'))
    
    # Generate report
    report_lines = []
    
    # 1. HEADER
    report_lines.append("=" * 60)
    report_lines.append(" " * 15 + "SALES ANALYTICS REPORT")
    report_lines.append(f"      Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append(f"      Records Processed: {format_number(total_transactions)}")
    report_lines.append("=" * 60)
    report_lines.append("")
    
    # 2. OVERALL SUMMARY
    report_lines.append("OVERALL SUMMARY")
    report_lines.append("-" * 60)
    report_lines.append(f"Total Revenue:        {format_currency(total_revenue)}")
    report_lines.append(f"Total Transactions:   {format_number(total_transactions)}")
    report_lines.append(f"Average Order Value:  {format_currency(avg_order_value)}")
    report_lines.append(f"Date Range:           {date_range}")
    report_lines.append("")
    
    # 3. REGION-WISE PERFORMANCE
    report_lines.append("REGION-WISE PERFORMANCE")
    report_lines.append("-" * 60)
    report_lines.append(f"{'Region':<12} {'Sales':<18} {'% of Total':<12} {'Transactions':<15}")
    report_lines.append("-" * 60)
    for region, stats in region_stats.items():
        sales_str = format_currency(stats['total_sales'])
        percentage_str = f"{stats['percentage']:.2f}%"
        report_lines.append(f"{region:<12} {sales_str:<18} {percentage_str:<12} {format_number(stats['transaction_count']):<15}")
    report_lines.append("")
    
    # 4. TOP 5 PRODUCTS
    report_lines.append("TOP 5 PRODUCTS")
    report_lines.append("-" * 60)
    report_lines.append(f"{'Rank':<6} {'Product Name':<25} {'Quantity Sold':<15} {'Revenue':<18}")
    report_lines.append("-" * 60)
    for i, (product_name, quantity, revenue) in enumerate(top_products, 1):
        report_lines.append(f"{i:<6} {product_name[:24]:<25} {format_number(quantity):<15} {format_currency(revenue):<18}")
    report_lines.append("")
    
    # 5. TOP 5 CUSTOMERS
    report_lines.append("TOP 5 CUSTOMERS")
    report_lines.append("-" * 60)
    report_lines.append(f"{'Rank':<6} {'Customer ID':<15} {'Total Spent':<18} {'Order Count':<15}")
    report_lines.append("-" * 60)
    for i, (customer_id, stats) in enumerate(top_customers_list, 1):
        report_lines.append(f"{i:<6} {customer_id:<15} {format_currency(stats['total_spent']):<18} {format_number(stats['purchase_count']):<15}")
    report_lines.append("")
    
    # 6. DAILY SALES TREND
    report_lines.append("DAILY SALES TREND")
    report_lines.append("-" * 60)
    report_lines.append(f"{'Date':<12} {'Revenue':<18} {'Transactions':<15} {'Unique Customers':<18}")
    report_lines.append("-" * 60)
    # Show first 10 days (or all if less than 10)
    daily_items = list(daily_trend.items())[:10]
    for date, stats in daily_items:
        report_lines.append(f"{date:<12} {format_currency(stats['revenue']):<18} {format_number(stats['transaction_count']):<15} {format_number(stats['unique_customers']):<18}")
    if len(daily_trend) > 10:
        report_lines.append(f"... ({len(daily_trend) - 10} more days)")
    report_lines.append("")
    
    # 7. PRODUCT PERFORMANCE ANALYSIS
    report_lines.append("PRODUCT PERFORMANCE ANALYSIS")
    report_lines.append("-" * 60)
    
    # Best selling day
    if peak_day[0]:
        report_lines.append(f"Best Selling Day: {peak_day[0]}")
        report_lines.append(f"  Revenue: {format_currency(peak_day[1])}")
        report_lines.append(f"  Transactions: {format_number(peak_day[2])}")
    else:
        report_lines.append("Best Selling Day: N/A")
    report_lines.append("")
    
    # Low performing products
    if low_products:
        report_lines.append("Low Performing Products (Quantity < 10):")
        report_lines.append(f"{'Product Name':<25} {'Quantity':<12} {'Revenue':<18}")
        report_lines.append("-" * 60)
        for product_name, quantity, revenue in low_products[:5]:  # Show top 5
            report_lines.append(f"{product_name[:24]:<25} {format_number(quantity):<12} {format_currency(revenue):<18}")
    else:
        report_lines.append("Low Performing Products: None")
    report_lines.append("")
    
    # Average transaction value per region
    report_lines.append("Average Transaction Value by Region:")
    report_lines.append(f"{'Region':<12} {'Avg Transaction Value':<25}")
    report_lines.append("-" * 60)
    for region, avg_value in sorted(avg_by_region.items(), key=lambda x: x[1], reverse=True):
        report_lines.append(f"{region:<12} {format_currency(avg_value):<25}")
    report_lines.append("")
    
    # 8. API ENRICHMENT SUMMARY
    report_lines.append("API ENRICHMENT SUMMARY")
    report_lines.append("-" * 60)
    report_lines.append(f"Total Products Enriched: {format_number(total_enriched)}")
    report_lines.append(f"Success Rate: {success_rate:.2f}%")
    report_lines.append(f"Successfully Matched: {format_number(matched_count)}")
    report_lines.append(f"Unmatched: {format_number(total_enriched - matched_count)}")
    
    if unmatched_products:
        report_lines.append("")
        report_lines.append("Products That Couldn't Be Enriched:")
        unmatched_list = sorted(list(unmatched_products))
        # Show first 10 or all if less than 10
        for product_id in unmatched_list[:10]:
            report_lines.append(f"  - {product_id}")
        if len(unmatched_list) > 10:
            report_lines.append(f"  ... ({len(unmatched_list) - 10} more)")
    else:
        report_lines.append("")
        report_lines.append("All products successfully enriched!")
    
    report_lines.append("")
    report_lines.append("=" * 60)
    report_lines.append("END OF REPORT")
    report_lines.append("=" * 60)
    
    # Write to file
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report_lines))
        
        print(f"✓ Successfully generated sales report: {output_file}")
        logger.info(f"Successfully generated sales report: {output_file}")
        
    except Exception as e:
        error_msg = f"Failed to generate report: {e}"
        print(f"✗ {error_msg}")
        logger.error(error_msg)
        raise

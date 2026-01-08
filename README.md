# Sales Analytics System

A comprehensive Python-based Sales Data Analytics System that processes sales transaction files, integrates with external APIs, performs data analysis, and generates detailed reports for business decision-making.

## 📋 Overview

This system is designed to handle real-world data quality challenges including:
- Non-UTF-8 encoding issues
- Data quality problems (missing fields, formatting issues, invalid data)
- Comma-separated values within fields
- Invalid records (zero quantities, negative prices, wrong ID formats)

## 🏗️ Project Structure

```
sales-analytics-system/
├── README.md                    # This file
├── main.py                      # Main entry point
├── requirements.txt             # Python dependencies
├── utils/
│   ├── __init__.py             # Package initializer
│   ├── file_handler.py         # File reading and data loading
│   ├── data_processor.py       # Data validation and analysis
│   ├── api_handler.py          # API integration for product info
│   └── report_generator.py     # Comprehensive report generation
├── data/
│   └── sales_data.txt          # Sales transaction data file
└── output/                     # Generated reports directory
```

## ✨ Features

1. **Data Loading & Cleaning**
   - Automatic encoding detection and handling
   - Robust parsing of pipe-delimited files
   - Handling of data quality issues

2. **Data Validation**
   - Transaction ID validation (T### format)
   - Product ID validation (P### format)
   - Customer ID validation (C### format)
   - Date format validation
   - Business rule validation (positive quantities, positive prices)

3. **API Integration**
   - Fetch product information from external APIs
   - Mock API support for testing
   - Batch product information retrieval
   - Record enrichment with product details

4. **Analytics & Reporting**
   - Overall sales statistics
   - Sales by region analysis
   - Sales by product analysis
   - Sales by date trends
   - Top customers identification
   - Top products identification
   - Customer behavior analysis

5. **Report Generation**
   - JSON reports for programmatic access
   - Human-readable text reports
   - Comprehensive analytics summaries

## 🚀 Installation

### Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

### Setup Steps

1. **Clone the repository** (or download the project files)
   ```bash
   git clone <repository-url>
   cd sales-analytics-system
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   
   # On macOS/Linux:
   source venv/bin/activate
   
   # On Windows:
   venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## 📖 Usage

### Basic Usage

Run the main script to process the sales data and generate reports:

```bash
python main.py
```

This will:
1. Load and parse the sales data file
2. Validate and clean the records
3. Fetch product information from the API
4. Perform comprehensive analytics
5. Generate reports in the `output/` directory

### Programmatic Usage

You can also use the system programmatically:

```python
from main import SalesAnalyticsSystem

# Initialize the system
system = SalesAnalyticsSystem(
    data_file='data/sales_data.txt',
    use_mock_api=True  # Set to False for real API calls
)

# Run the complete pipeline
reports = system.run()

# Access specific analytics
print(f"Total Revenue: ₹{reports['overall_statistics']['total_revenue']}")
print(f"Top Product: {reports['top_products'][0]['name']}")
```

### Configuration Options

You can modify the following in `main.py`:

- **DATA_FILE**: Path to the sales data file (default: `'data/sales_data.txt'`)
- **USE_MOCK_API**: Whether to use mock API data (default: `True`)
  - Set to `False` to make real API calls (requires internet connection)

## 📊 Data Format

The system expects sales data in the following format:

```
TransactionID|Date|ProductID|ProductName|Quantity|UnitPrice|CustomerID|Region
T001|2024-12-01|P101|Laptop|2|45000|C001|North
T002|2024-12-01|P102|Mouse,Wireless|5|500|C002|South
```

**Field Descriptions:**
- `TransactionID`: Unique transaction identifier (format: T###)
- `Date`: Transaction date (format: YYYY-MM-DD)
- `ProductID`: Product identifier (format: P###)
- `ProductName`: Product name (may contain commas)
- `Quantity`: Number of items (positive integer)
- `UnitPrice`: Price per unit (positive number, may contain commas)
- `CustomerID`: Customer identifier (format: C###, optional)
- `Region`: Sales region (North, South, East, West)

## 🔍 Data Quality Handling

The system handles various data quality issues:

1. **Encoding Issues**: Automatically detects and handles non-UTF-8 encodings
2. **Formatting Issues**: Removes commas from numeric values
3. **Missing Fields**: Handles records with missing or extra fields
4. **Invalid Data**:
   - Rejects records with zero or negative quantities
   - Rejects records with negative prices
   - Rejects records with invalid ID formats
   - Rejects records with invalid dates

## 📈 Generated Reports

Reports are saved in the `output/` directory with timestamps:

- `sales_report_YYYYMMDD_HHMMSS.json`: Machine-readable JSON format
- `sales_report_YYYYMMDD_HHMMSS.txt`: Human-readable text format

**Report Contents:**
- Overall statistics (revenue, transactions, data quality score)
- Sales by region breakdown
- Sales by product detailed analysis
- Sales by date trends
- Top 10 customers by spending
- Top 10 products by revenue
- Customer behavior statistics

## 🧪 Testing

To verify the system works correctly:

1. Ensure all dependencies are installed
2. Verify `data/sales_data.txt` exists
3. Run the system:
   ```bash
   python main.py
   ```
4. Check the `output/` directory for generated reports

## 🛠️ Dependencies

- **requests**: HTTP library for API integration
- **chardet**: Character encoding detection

See `requirements.txt` for specific versions.

## 📝 Notes

- The system uses mock API data by default for reliability and testing
- Real API integration requires internet connectivity and a valid API endpoint
- The output directory is created automatically if it doesn't exist
- Invalid records are logged but excluded from analytics

## 🤝 Contributing

This is an assignment project. For improvements or bug fixes:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is created for educational purposes as part of a Python programming assignment.

## 👤 Author

Created as part of BITSoM Python Programming Assignment 4.

---

**Note**: This system is designed to handle real-world data quality challenges commonly encountered in business analytics scenarios.

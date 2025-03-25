# main.py
from db import test_connection
from data_utils import load_symbols, load_data, filter_zones
from datetime import date

if __name__ == "__main__":
    # Test database connection
    if test_connection():
        # Load symbols
        symbols = load_symbols()
        print("Symbols loaded:", symbols)

        # Load and filter data for the first symbol (if available)
        if symbols:
            symbol = symbols[0]
            start_date = date(2021, 1, 1)  # Example start date
            end_date = date(2023, 12, 31)  # Example end date
            data = load_data(symbol, start_date, end_date)
            print(f"Data for {symbol} from {start_date} to {end_date} (first 5 rows):\n", data.head())

            # Test filter_zones with 30 minutes for each zone
            filtered_data = filter_zones(data, first_minutes_asia=30, first_minutes_london=30, first_minutes_ny=30)
            print(f"Filtered data for {symbol} (first 5 rows within 30 minutes of market zones):\n", filtered_data.head())
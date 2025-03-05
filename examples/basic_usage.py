from eodhd_options import EODHDOptions
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

def main():
    # Get API key from environment variable
    api_key = os.getenv("EODHD_API_KEY")
    if api_key:
        # Save the API key for future use
        EODHDOptions.save_api_key(api_key)
    
    try:
        # Create client (will use stored key if available)
        client = EODHDOptions()
    except ValueError:
        if not api_key:
            raise ValueError(
                "Please set EODHD_API_KEY environment variable "
                "or save an API key using EODHDOptions.save_api_key()"
            )
        client = EODHDOptions(api_key=api_key)

    # Get AAPL options expiring from today onwards (up to 10,000 results due to API limits)
    today = datetime.now().date()
    
    print("Fetching AAPL options expiring from today onwards...")
    print(f"Start date: {today}")
    print("Note: Due to API limitations, only the first 10,000 results can be fetched.")
    
    options = client.get_options(
        ticker="AAPL",
        from_date=today,
        sort="exp_date"  # Sort by expiration date
    )
    
    print(f"\nFetched {len(options):,} options")
    if len(options) > 0:
        print("\nFirst few options:")
        print(options.head())
        
        # Save to CSV for analysis
        filename = "aapl_options.csv"
        options.to_csv(filename, index=False)
        print(f"\nSaved all results to {filename}")
    else:
        print("\nNo options found matching the criteria.")

if __name__ == "__main__":
    main() 
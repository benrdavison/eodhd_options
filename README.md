# EODHD Options API Wrapper

A Python wrapper for the EODHD Options API that provides a simple interface to fetch options data. This package allows you to easily retrieve options data by underlying ticker, expiration range, moneyness range, and put/call type.

## Installation

```bash
pip install eodhd_options
```

## API Key Management

There are several ways to use your EODHD API key with this package:

1. Store the API key for future use:
```python
from eodhd_options import EODHDOptions

# Save your API key (only need to do this once)
EODHDOptions.save_api_key("your_api_key")

# Then create client without providing key
client = EODHDOptions()  # Uses stored key
```

2. Provide the API key when creating the client:
```python
client = EODHDOptions(api_key="your_api_key")
```

3. Use environment variable:
```bash
export EODHD_API_KEY="your_api_key"
```
```python
client = EODHDOptions()  # Will use environment variable
```

The API key is stored securely in your system's user-specific configuration directory:
- Windows: `%APPDATA%\eodhd_options\config.json`
- Unix/Linux: `~/.config/eodhd_options/config.json`

## Usage

```python
from eodhd_options import EODHDOptions

# Initialize the client with your API key
client = EODHDOptions(api_key="your_api_key")

# Fetch options data for a specific ticker
options = client.get_options(
    ticker="AAPL",
    from_date="2024-03-01",
    to_date="2024-06-30",
    min_strike=300,
    max_strike=400,
    option_type="call"  # or "put" or None for both
)
```

## Features

- Fetch options data by ticker symbol
- Filter by expiration date range
- Filter by strike price range
- Filter by option type (calls, puts, or both)
- Data returned as Pandas DataFrames for easy analysis
- Secure API key storage in system configuration
- Automatic pagination handling (up to 10,000 results per query)

## Dependencies

- Python >= 3.7
- requests >= 2.25.0
- pandas >= 1.2.0
- python-dateutil >= 2.8.0

## Planned Features

The following endpoints are planned for future implementation:

### Historical Options Data
Fetch historical end-of-day data for specific option contracts:
```python
# Planned implementation
historical_data = client.get_historical_options_data(
    contracts=["AAPL240621C00180000"],  # List of option contract symbols
    from_date="2024-01-01",
    to_date="2024-03-01"
)
```

### Available Option Tickers
Get a list of all tickers that have options data available:
```python
# Planned implementation
available_tickers = client.get_options_tickers()
# Returns list of symbols like ["AAPL", "MSFT", "GOOGL", ...]
```

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. 

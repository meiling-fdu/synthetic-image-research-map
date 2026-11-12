"""Register exact versioned B5 transaction inputs, with independent live guards."""
pytest_plugins = (
    'tests.b5_02_historical_fixtures',
    'tests.b5_03_historical_fixtures',
    'tests.b5_04_historical_fixtures',
)

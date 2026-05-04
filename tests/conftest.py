from __future__ import annotations

import pandas as pd
import pytest


@pytest.fixture
def synth_sessions() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "date": pd.to_datetime(["2024-01-01", "2024-01-01", "2024-01-02", "2024-01-02"]),
            "user_type": ["New_User", "Returning_User", "New_User", "Returning_User"],
            "category": ["electronics", "electronics", "fashion", "fashion"],
            "brand": ["BrandA", "BrandB", "BrandA", "BrandB"],
            "Sessions": [100, 80, 120, 90],
            "Views": [200, 160, 240, 180],
        }
    )


@pytest.fixture
def synth_cart() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "date": pd.to_datetime(["2024-01-01", "2024-01-01", "2024-01-02", "2024-01-02"]),
            "user_type": ["New_User", "Returning_User", "New_User", "Returning_User"],
            "category": ["electronics", "electronics", "fashion", "fashion"],
            "brand": ["BrandA", "BrandB", "BrandA", "BrandB"],
            "Cart": [50, 40, 60, 45],
            "Potential_Buyers": [25, 20, 30, 22],
            "Products_in_Cart": [70, 55, 85, 60],
            "Potential_Sales": [500.0, 400.0, 600.0, 450.0],
        }
    )


@pytest.fixture
def synth_orders() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "date": pd.to_datetime(["2024-01-01", "2024-01-01", "2024-01-02", "2024-01-02"]),
            "user_type": ["New_User", "Returning_User", "New_User", "Returning_User"],
            "category": ["electronics", "electronics", "fashion", "fashion"],
            "brand": ["BrandA", "BrandB", "BrandA", "BrandB"],
            "Orders": [10, 15, 12, 17],
            "Buyers": [8, 12, 10, 14],
            "Products_Sold": [12, 18, 14, 20],
            "Sales": [200.0, 350.0, 240.0, 400.0],
        }
    )


@pytest.fixture
def synth_customer_orders() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "customer_id": ["c1", "c1", "c2", "c2", "c3", "c4", "c4", "c4"],
            "order_id": ["o1", "o2", "o3", "o4", "o5", "o6", "o7", "o8"],
            "date": pd.to_datetime([
                "2024-01-01", "2024-02-01", "2024-01-15",
                "2024-03-01", "2024-02-10",
                "2024-01-20", "2024-01-25", "2024-02-15",
            ]),
            "revenue": [50.0, 30.0, 100.0, 60.0, 200.0, 25.0, 35.0, 45.0],
        }
    )

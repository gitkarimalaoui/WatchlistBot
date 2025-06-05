# -*- coding: utf-8 -*-
import sqlite3
import pandas as pd

# Path to the local SQLite database
DB_PATH = r"C:\Users\KARIM\Desktop\python\projet AI\BOTV7\BOTV7\data\entreprise.db"

def get_portfolio_modules():
    """
    Returns the list of IA/CRM modules, with their categories.
    """
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(
        "SELECT category, module_name FROM portfolio_modules",
        conn
    )
    conn.close()
    return df

def get_use_cases():
    """
    Returns the use cases by region and sector.
    """
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(
        "SELECT region, sector FROM use_cases",
        conn
    )
    conn.close()
    return df

def get_revenue_sources():
    """
    Returns the breakdown of revenue sources and amounts.
    """
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(
        "SELECT source, amount FROM revenue_sources",
        conn
    )
    conn.close()
    return df

def get_kpi_targets():
    """
    Returns the KPI targets and their values.
    """
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(
        "SELECT kpi, value FROM kpi_targets",
        conn
    )
    conn.close()
    return df

if __name__ == "__main__":
    # Quick CLI test
    print(get_portfolio_modules())
    print(get_use_cases())
    print(get_revenue_sources())
    print(get_kpi_targets())

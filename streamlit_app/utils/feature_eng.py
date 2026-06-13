def update_rolling_features(historical_sales):
    """
    Given a list of historical sales (chronological order),
    computes the next day's rolling features.
    """
    if not historical_sales:
        return {"RollingMean_7": 0, "RollingMean_14": 0, "RollingMean_30": 0, "RollingStd_7": 0}
        
    def mean(vals):
        return sum(vals)/len(vals) if vals else 0
        
    def std(vals):
        m = mean(vals)
        return (sum((v - m)**2 for v in vals) / len(vals)) ** 0.5 if vals else 0

    last_7 = historical_sales[-7:] if len(historical_sales) >= 7 else historical_sales
    last_14 = historical_sales[-14:] if len(historical_sales) >= 14 else historical_sales
    last_30 = historical_sales[-30:] if len(historical_sales) >= 30 else historical_sales
    
    return {
        "RollingMean_7": mean(last_7),
        "RollingMean_14": mean(last_14),
        "RollingMean_30": mean(last_30),
        "RollingStd_7": std(last_7)
    }

def update_lag_features(historical_sales):
    """
    Given a list of historical sales, computes lag features for the next day.
    """
    def get_lag(n):
        return historical_sales[-n] if len(historical_sales) >= n else 0
        
    return {
        "Sales_Lag_1": get_lag(1),
        "Sales_Lag_7": get_lag(7),
        "Sales_Lag_14": get_lag(14),
        "Sales_Lag_30": get_lag(30)
    }

def generate_next_day_features(base_row, historical_sales):
    """
    Updates the base feature row with new recursive lag and rolling values.
    """
    next_row = base_row.copy()
    
    # Update lags
    lags = update_lag_features(historical_sales)
    next_row.update(lags)
    
    # Update rolling metrics
    rolling = update_rolling_features(historical_sales)
    next_row.update(rolling)
    
    return next_row

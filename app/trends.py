import pandas as pd
from ruptures import Pelt


def get_trend_data(ingredient=None):
    # todo: replace with real ES aggregation later
    dates = pd.date_range(end=pd.Timestamp.today(), periods=12, freq='M')
    counts = pd.Series([i + (ingredient is not None)*5 for i in range(12)], index=dates)
    algo = Pelt(model='rbf').fit(counts.values)
    change_points = algo.predict(pen=10)
    return {
        'dates': dates.strftime('%Y-%m').tolist(),
        'counts': counts.tolist(),
        'change_points': change_points
    }
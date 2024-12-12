import pandas as pd

def process_data(data):
    df = pd.DataFrame(data)
    # Example transformation: convert date strings to datetime
    df['date'] = pd.to_datetime(df['date'])
    # More complex transformations can be added here
    return df.to_json(orient='records')

import pandas as pd

def process_gsc_data(result, request):
    rows = result.get('rows', [])
    if not rows:
        return None

    df = pd.DataFrame(rows)
    keys = df['keys'].apply(pd.Series)
    
    dimension_names = request['dimensions']
    for i, dim in enumerate(dimension_names):
        keys = keys.rename(columns={i: dim.lower()})
    
    df_display = pd.concat([keys, df.drop('keys', axis=1)], axis=1)
    
    # Rename '2' to 'Date' if it exists
    if '2' in df_display.columns:
        df_display = df_display.rename(columns={'2': 'Date'})
    
    # Special handling for daily data
    if 'Date' in df_display.columns:
        df_display['Date'] = pd.to_datetime(df_display['Date']).dt.date
    
    cols = df_display.columns.tolist()
    for col in ['Query', 'Page']:
        if col in cols:
            cols.remove(col)
            cols.insert(0, col)
    df_display = df_display[cols]

    # Convert CTR to percentage and round to 2 decimal places
    df_display['CTR'] = (df_display['ctr'] * 100).round(2)
    
    # Round average position to 2 decimal places
    df_display['Average Position'] = df_display['position'].round(2)
    
    # Drop the original columns
    df_display = df_display.drop(['ctr', 'position'], axis=1)
    
    # Reorder columns to put CTR and Average Position at the end
    cols = [col for col in df_display.columns if col not in ['CTR', 'Average Position']]
    cols += ['CTR', 'Average Position']
    df_display = df_display[cols]

    return df_display

def group_gsc_data(df_display):
    if 'page' in df_display.columns and 'query' in df_display.columns and 'clicks' in df_display.columns:
        df_display = df_display.sort_values('clicks', ascending=False)
        
        df_grouped = df_display.groupby('page').agg({
            'query': lambda x: ', '.join(x.head(10)),
            'clicks': 'sum',
            'impressions': 'sum',
            'CTR': lambda x: f"{x.astype(float).mean():.2f}%",
            'Average Position': 'mean'
        }).reset_index()
        
        # Sort df_grouped by clicks in descending order
        df_grouped = df_grouped.sort_values('clicks', ascending=False)

        df_grouped = df_grouped.rename(columns={'query': 'top 10 queries'})
        return df_grouped
    return None

import streamlit as st
import requests
import datetime
import pandas as pd
import altair as alt

# Constants
API_ENDPOINT = "https://api.stakingrewards.com/public/query"

# GraphQL Queries
VALIDATOR_BY_ADDRESS_QUERY = """
    query FetchValidatorByAddress($address: String!) {
        validators(where: {addresses: [$address]}, limit: 20) {
            id
            address
            rewardOptions(limit: 1) {
              inputAssets(limit: 1) {
                name
                symbol
              }
            }
            isActive
            isPrivate
            isDynamic
            isOpensource
            activeSince
            metricsUpdatedAt
            status {
                label
            }
            metrics(limit: 20) {
                label
                metricKey
                tooltip
                unit
                precision
                defaultValue
                variation
                changePercentages
                changeAbsolutes
                rewardOptionKeys
                createdAt
            }
        }
    }
"""

HISTORICAL_VALIDATOR_METRICS_QUERY = """
    query HistoricalValidatorMetrics($validatorID: String!, $timeStart: Date, $timeEnd: Date) {
        delegatedTokens: metrics(where: {validator: {id: $validatorID}, metricKeys: ["delegated_tokens"], createdAt_gt: $timeStart, createdAt_lt: $timeEnd}, limit: 30, order: {createdAt: asc}) {
            defaultValue
            createdAt
        }
        rewardRate: metrics(where: {validator: {id: $validatorID}, metricKeys: ["reward_rate"], createdAt_gt: $timeStart, createdAt_lt: $timeEnd}, limit: 30, order: {createdAt: asc}) {
            defaultValue
            createdAt
        }
        selfStakedTokens: metrics(where: {validator: {id: $validatorID}, metricKeys: ["self_staked_tokens"], createdAt_gt: $timeStart, createdAt_lt: $timeEnd}, limit: 30, order: {createdAt: asc}) {
            defaultValue
            createdAt
        }
        stakedTokens: metrics(where: {validator: {id: $validatorID}, metricKeys: ["staked_tokens"], createdAt_gt: $timeStart, createdAt_lt: $timeEnd}, limit: 30, order: {createdAt: asc}) {
            defaultValue
            createdAt
        }
        stakingShare: metrics(where: {validator: {id: $validatorID}, metricKeys: ["staking_share"], createdAt_gt: $timeStart, createdAt_lt: $timeEnd}, limit: 30, order: {createdAt: asc}) {
            defaultValue
            createdAt
        }
        stakingWallets: metrics(where: {validator: {id: $validatorID}, metricKeys: ["staking_wallets"], createdAt_gt: $timeStart, createdAt_lt: $timeEnd}, limit: 30, order: {createdAt: asc}) {
            defaultValue
            createdAt
        }
    }
"""


def main():
    st.title("Validator Performance Analyzer")

    st.write("""
             This tool provides insights into the performance metrics of a given validator.
             By simply entering the validator address, you can view current performance metrics and historical data. Whether you're an individual staker, a validator, or just curious about the metrics, this app offers a comprehensive snapshot of validator performance over time.
             """)
    

    # Request API key from user
    API_KEY = st.text_input("Enter your API key:", type="password")
    
    # Request validator address from user
    validator_address = st.text_input("Enter validator address:")

    # Date inputs
    today = datetime.date.today()
    start_date = st.date_input('Start date', today - datetime.timedelta(days=30))
    end_date = st.date_input('End date', today)

    if API_KEY and validator_address:
        headers = {
            "Content-Type": "application/json",
            "x-api-key": API_KEY
        }

        if st.button("Fetch Validator Data"):
            process_and_display_data(headers, validator_address, start_date, end_date)

    st.divider()
    st.markdown('Created by [**@0xfabs**](https://twitter.com/0xfabs)')



def process_and_display_data(headers, validator_address, start_date, end_date):
    # Fetch current validator data
    validator_data = fetch_validator_by_address(headers, validator_address)
    if validator_data:
        validator = validator_data[0]  # Get the first validator
        st.divider()
        # Fetch historical validator data
        historical_data = fetch_validator_historical_data(headers, validator['id'], start_date.isoformat(), end_date.isoformat())
        if historical_data:
            display_current_validator_data(validator, historical_data)
            st.divider()
            # Add a subheading for historical data
            st.subheader("Historical Data")
            display_historical_data(historical_data)
        else:
            st.write("No historical data available for the given period.")




def display_current_validator_data(validator, historical_data):
    asset_name = validator['rewardOptions'][0]['inputAssets'][0]['name']
    asset_symbol = validator['rewardOptions'][0]['inputAssets'][0]['symbol']
    st.subheader(f"Validator Address: {validator.get('address', 'N/A')} ")  # Display the asset
    st.subheader(f"{asset_name} (${asset_symbol})")
    
    metrics_data = {metric['label']: metric['defaultValue'] for metric in validator['metrics']}
    
    # Extract the most recent historical data points
    most_recent_data = {
        "Delegated Tokens": historical_data.get("Delegated Tokens") and round(list(historical_data.get("Delegated Tokens", {}).values())[-1], 2) or None,
        "Reward Rate": historical_data.get("Reward Rate") and round(list(historical_data.get("Reward Rate", {}).values())[-1], 2) or None,
        "Staked Tokens": historical_data.get("Staked Tokens") and round(list(historical_data.get("Staked Tokens", {}).values())[-1], 2) or None,
        "Staking Share": historical_data.get("Staking Share") and round(list(historical_data.get("Staking Share", {}).values())[-1], 2) or None
    }

    # Split the items into two equal halves (or almost equal if odd number of items)
    items = list(metrics_data.items())
    first_half = items[:len(items)//2]
    second_half = items[len(items)//2:]
    
    # Create columns to display the data
    col1, col2 = st.columns(2)
    
    for label, value in first_half:
        value = round(value, 2)
        delta = None
        if label in most_recent_data and most_recent_data[label] is not None:
            delta = round(value - most_recent_data[label], 2)
        col1.metric(label=label, value=value, delta=delta)
        
    for label, value in second_half:
        value = round(value, 2)
        delta = None
        if label in most_recent_data and most_recent_data[label] is not None:
            delta = round(value - most_recent_data[label], 2)
        col2.metric(label=label, value=value, delta=delta)



def display_historical_data(historical_data):
    organized_data = {}

    human_readable_names = {
        'delegatedTokens': 'Delegated Tokens',
        'rewardRate': 'Reward Rate',
        'selfStakedTokens': 'Self Staked Tokens',
        'stakedTokens': 'Staked Tokens',
        'stakingShare': 'Staking Share',
        'stakingWallets': 'Staking Wallets',
    }

    for metric_name, metric_data in historical_data.items():
        if isinstance(metric_data, list):
            readable_name = human_readable_names.get(metric_name, metric_name)
            organized_data[readable_name] = {
                entry['createdAt']: entry['defaultValue'] for entry in metric_data
            }

    st.json(organized_data)

def fetch_validator_by_address(headers, address):
    payload = {
        "query": VALIDATOR_BY_ADDRESS_QUERY,
        "variables": {"address": address}
    }
    response = requests.post(API_ENDPOINT, json=payload, headers=headers)
    return handle_response(response, "validators")

def fetch_validator_historical_data(headers, validatorID, timeStart, timeEnd):
    payload = {
        "query": HISTORICAL_VALIDATOR_METRICS_QUERY,
        "variables": {"validatorID": validatorID, "timeStart": timeStart, "timeEnd": timeEnd}
    }
    response = requests.post(API_ENDPOINT, json=payload, headers=headers)
    return handle_response(response)

def handle_response(response, key=None):
    if response.status_code == 200:
        json_data = response.json()
        if 'errors' in json_data:
            st.error(f"GraphQL Error: {json_data['errors'][0]['message']}")
            return {}
        return json_data["data"].get(key, {}) if key else json_data['data']
    else:
        st.error(f"Failed to fetch data. HTTP Status: {response.status_code}")
        return {}
    
def display_historical_data(historical_data):
    # Organize data by metric type
    organized_data = {}
    # Mapping from GraphQL metric names to human-readable names
    human_readable_names = {
        'delegatedTokens': 'Delegated Tokens',
        'rewardRate': 'Reward Rate',
        'selfStakedTokens': 'Self Staked Tokens',
        'stakedTokens': 'Staked Tokens',
        'stakingShare': 'Staking Share',
        'stakingWallets': 'Staking Wallets',
        # Add more as necessary
    }

    for metric_name, metric_data in historical_data.items():
        if isinstance(metric_data, list):  # Ensure metric_data is a list
            readable_name = human_readable_names.get(metric_name, metric_name)
            organized_data[readable_name] = {
                entry['createdAt']: entry['defaultValue'] for entry in metric_data
            }

    # Plot the data
    plot_historical_data(organized_data)


def plot_historical_data(data):
    metrics = list(data.keys())
    
    for i in range(0, len(metrics), 2):  # Step by 2 to process two metrics at a time
        cols = st.columns(2)
        
        for j in range(2):
            if i + j < len(metrics):
                metric_name = metrics[i + j]
                metric_data = data[metric_name]

                # Convert the data into a DataFrame
                df = pd.DataFrame(list(metric_data.items()), columns=['Date', metric_name])
                df['Date'] = pd.to_datetime(df['Date'])

                # Check if data is available
                if not df[metric_name].isna().all():  # Check if all values are NaN
                    # Calculate y_min and y_max for padding
                    y_min = df[metric_name].min()
                    y_max = df[metric_name].max()

                    # Add some padding to the limits to ensure some space above and below the actual data
                    padding = (y_max - y_min) * 0.1 
                    y_min -= padding
                    y_max += padding

                    # Create an Altair chart
                    chart = alt.Chart(df).mark_line(point=True).encode(
                        x='Date:T',
                        y=alt.Y(metric_name, scale=alt.Scale(domain=(y_min, y_max))),
                        tooltip=['Date:T', metric_name]
                    ).properties(
                        width=300,  # Adjust the width to fit side by side
                        height=300,
                        title=metric_name
                    ).interactive()

                    # Display chart in one of the columns
                    cols[j].altair_chart(chart, use_container_width=True)
                else:
                    cols[j].write(f"No data available for {metric_name}")




if __name__ == "__main__":
    main()


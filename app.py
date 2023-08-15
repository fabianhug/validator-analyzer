import streamlit as st
import requests
import datetime

# Constants
API_ENDPOINT = "https://api.stakingrewards.com/public/query"

# GraphQL Queries
VALIDATOR_BY_ADDRESS_QUERY = """
    query FetchValidatorByAddress($address: String!) {
        validators(where: {addresses: [$address]}, limit: 20) {
            id
            address
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



def process_and_display_data(headers, validator_address, start_date, end_date):
    # Fetch current validator data
    validator_data = fetch_validator_by_address(headers, validator_address)
    if validator_data:
        validator = validator_data[0]  # Get the first validator
        st.subheader(f"Validator ID: {validator['id']} | Address: {validator.get('address', 'N/A')}")
        metrics_data = {metric['label']: metric['defaultValue'] for metric in validator['metrics']}
        st.json(metrics_data)

        # Fetch historical validator data
        historical_data = fetch_validator_historical_data(headers, validator['id'], start_date.isoformat(), end_date.isoformat())
        if historical_data:
            display_historical_data(historical_data)
        else:
            st.write("No historical data available for the given period.")


def display_current_validator_data(validator):
    st.subheader(f"Validator ID: {validator['id']} | Address: {validator.get('address', 'N/A')}")
    metrics_data = {metric['label']: metric['defaultValue'] for metric in validator['metrics']}
    st.json(metrics_data)

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
    st.text(payload)
    response = requests.post(API_ENDPOINT, json=payload, headers=headers)
    st.text(response.json())
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
    organized_data = {}

    human_readable_names = {
        'delegatedTokens': 'Delegated Tokens',
        'rewardRate': 'Reward Rate',
        'selfStakedTokens': 'Self Staked Tokens',
        'stakedTokens': 'Staked Tokens',
        'stakingShare': 'Staking Share',
        'stakingWallets': 'Staking Wallets',
    }

    has_data = False  # Use a flag to check if there's any data

    for metric_name, metric_data in historical_data.items():
        if isinstance(metric_data, list) and metric_data:
            has_data = True
            readable_name = human_readable_names.get(metric_name, metric_name)
            organized_data[readable_name] = {
                entry['createdAt']: entry['defaultValue'] for entry in metric_data
            }

    if has_data:
        st.json(organized_data)
    else:
        st.write("No historical data available for the given period.")


if __name__ == "__main__":
    main()


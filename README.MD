# Validator Performance Analyzer

**Validator Performance Analyzer** is a tool designed to provide insights into the performance metrics of validators in the blockchain ecosystem. By entering a validator address, users can view both current performance metrics and historical data.

## Setup and Installation

### Prerequisites

- Python 3.x
- pip (Python package installer)

### Steps

1. **Clone the Repository:**

    ```bash
    git clone https://github.com/fabianhug/validator-analyzer
    cd validator-analyzer
    ```

2. **Install Dependencies:**
    Using the provided `requirements.txt` file, install the necessary Python packages.

    ```bash
    pip install -r requirements.txt
    ```

3. **Set Up API Key:**
    Ensure you have your API key for accessing the data. You will be prompted to input this key when running the app.

4. **Run the App:**

    ```bash
    streamlit run [YOUR APP FILE NAME HERE, e.g., app.py]
    ```

5. **Access the App:**
    Once the app is running, you'll be provided with a local URL in your terminal (usually `http://localhost:8501/`). Open this link in your web browser to access the app.

## Usage

1. Enter your API key when prompted.
2. Provide the validator address you wish to analyze.
3. Select the date range for which you want historical data.
4. Click the `Fetch Validator Data` button to view the performance metrics and historical data.

## Feedback and Contributions

For feedback, issues, or contributions, please open an issue on the repository or contact the creator.

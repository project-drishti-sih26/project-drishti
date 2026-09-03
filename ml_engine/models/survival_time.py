"""
FILE: ml_engine/models/survival_time.py
ROLE: Role 2 — ML/AI Engineer
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📌 WHAT IS THIS FILE?
    This is the WHEN Engine — the time window predictor. It uses Survival Analysis
    to answer: "How many minutes after receiving the stolen funds will the mule
    runner attempt to withdraw cash from an ATM?"

    Output example: "Cashout expected between 14:32 and 14:48 (in 23 to 39 minutes)"

📌 WHY SURVIVAL ANALYSIS AND NOT LINEAR REGRESSION?
    Standard regression would predict a single point in time (e.g., "32 minutes").
    That's overconfident and brittle. In reality, we have UNCERTAINTY — the mule
    could withdraw in 20 mins if they're nearby, or 45 mins if they have to travel.

    Survival Analysis is the statistically correct approach because:
    1. It models the TIME-TO-EVENT (time until withdrawal) as a DISTRIBUTION, not a point.
    2. It naturally handles RIGHT-CENSORED data: transactions where we lost track
       of the mule before withdrawal happened (we know "at least X minutes passed").
    3. Kaplan-Meier gives a probability curve: P(withdrawal before time T) = 0.85.
       We can then extract the 25th and 75th percentile as the prediction window.

📌 WHAT TO IMPLEMENT HERE:

    DATA PREPARATION FUNCTION:
    def prepare_survival_data(historical_tx_path: str = "simulation/data/historical_transactions.csv") -> pd.DataFrame:
        """
        Loads and processes the historical transaction CSV to create the
        training dataset for the Survival Analysis model.

        The historical_transactions.csv (from Role 5) should contain columns:
        - tx_id: transaction ID
        - mule_account_id: which mule account
        - amount: transaction amount
        - transfer_timestamp: when money was transferred to mule
        - withdrawal_timestamp: when mule withdrew cash (NaN if not withdrawn yet)

        Steps:
        1. Load the CSV with pandas.
        2. Compute time_to_withdrawal:
           df['duration'] = (df['withdrawal_timestamp'] - df['transfer_timestamp']).dt.total_seconds() / 60
        3. Compute the 'event' column (did withdrawal happen?):
           df['event_occurred'] = df['withdrawal_timestamp'].notna().astype(int)
           (1 = withdrawal happened, 0 = censored / not yet withdrawn)
        4. Return cleaned DataFrame with at minimum: ['duration', 'event_occurred', 'amount']
        """

    MODEL TRAINING FUNCTION:
    def train_survival_model(df: pd.DataFrame):
        """
        Fits a Kaplan-Meier survival estimator on the training data.

        Steps:
        1. Separate durations and event flags:
           T = df['duration']    # Time in minutes until withdrawal
           E = df['event_occurred']  # 1 = withdrew, 0 = censored

        2. Fit KaplanMeierFitter:
           from lifelines import KaplanMeierFitter
           kmf = KaplanMeierFitter()
           kmf.fit(T, event_observed=E, label="Mule Withdrawal Time")

        3. Save the fitted model to weights/:
           import pickle
           with open("ml_engine/weights/survival_model.pkl", "wb") as f:
               pickle.dump(kmf, f)

        4. Return the fitted kmf object.
        """

    MODEL LOADING (run once at module level):
    _survival_model = None
    def _load_model():
        """Lazy-loads the saved survival model from disk."""
        import pickle
        with open("ml_engine/weights/survival_model.pkl", "rb") as f:
            return pickle.load(f)

    MAIN PREDICTION FUNCTION (called by inference_pipeline.py):
    def predict_time_window(
        transaction_timestamp: str,
        mule_account_id: str,
        confidence_percentiles: tuple = (0.25, 0.75)
    ) -> dict:
        """
        Predicts the withdrawal time window using the trained KM model.

        STEPS:
        1. Load the survival model (if not already loaded).

        2. Use the model's survival function to find the time at which
           the cumulative withdrawal probability crosses the percentile thresholds:
           
           From the KM fitted model:
           timeline = kmf.survival_function_.index  # array of time values in minutes
           survival_probs = kmf.survival_function_['Mule Withdrawal Time'].values

           Find T_25 (time when 25% of mules have already withdrawn):
           → This is the EARLIEST likely withdrawal time.
           Find T_75 (time when 75% of mules have already withdrawn):
           → This is the LATEST likely withdrawal time.

        3. Compute actual timestamps:
           tx_dt = datetime.fromisoformat(transaction_timestamp)
           window_start = tx_dt + timedelta(minutes=T_25)
           window_end = tx_dt + timedelta(minutes=T_75)
           minutes_from_now = int(T_25)  # Urgency indicator for the frontend countdown

        4. Return:
           {
               "start": window_start.isoformat(),
               "end": window_end.isoformat(),
               "minutes_from_now": minutes_from_now,
               "confidence": 0.75 - 0.25  # = 0.50, the width of the percentile range
           }

        FALLBACK (if model not trained yet):
        If the weights file doesn't exist, return a hardcoded estimate:
        { "start": now+25min, "end": now+45min, "minutes_from_now": 25, "confidence": 0.6 }
        Log a warning: "WARNING: Using hardcoded fallback time window. Train survival model."
        """

📌 HOW IT CONNECTS TO OTHER FILES:
    - Called BY: ml_engine/pipelines/inference_pipeline.py (STEP 4).
    - Training data: simulation/data/historical_transactions.csv (Role 5).
    - Saves model to: ml_engine/weights/survival_model.pkl.
    - Training: Run once via a notebook in ml_engine/notebooks/ before demo.

📌 LIBRARIES TO USE:
    - lifelines (pip install lifelines) — `KaplanMeierFitter`
    - pandas (for data loading)
    - pickle (for saving/loading model)
    - datetime (standard library)
    - numpy (for finding percentile crossings in survival function)
"""

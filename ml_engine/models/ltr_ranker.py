"""
FILE: ml_engine/models/ltr_ranker.py
ROLE: Role 2 — ML/AI Engineer
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📌 WHAT IS THIS FILE?
    This is the WHERE Engine Phase 2: Learning-to-Rank (LTR) using LightGBM's
    LambdaMART algorithm. After spatial_filter.py produces ~100-200 candidate
    ATMs, this model ranks them by probability that the mule will choose each one.

    The output is a sorted list — Rank #1 is the ATM the mule is MOST likely
    heading to right now. Police should be dispatched to Rank #1 immediately.

📌 WHY LIGHTGBM LAMBDAMART AND NOT SIMPLE SORTING?
    The fallback heuristic sorts by (fraud_history, distance). But that ignores
    many subtle patterns in the data:
    - Mules often return to the SAME ATM they used before (network affinity).
    - Mules avoid ATMs near police stations (not captured by fraud count alone).
    - Mules prefer ATMs in crowded areas with camera blind spots.
    - Time of day affects ATM preference (night → remote ATMs).

    LambdaMART is the industry-standard algorithm for ranking (also used by Bing,
    Airbnb, LinkedIn for recommendations). It learns complex feature interactions
    from historical data to produce a relevance ranking score. It directly optimizes
    NDCG (Normalized Discounted Cumulative Gain) — a ranking quality metric.

📌 FEATURE ENGINEERING — What features to build for each candidate ATM:

    For each (mule, candidate_ATM) pair, build a feature vector:
    [
        "travel_time_mins",           # Minutes from mule location to ATM (from distance matrix)
        "distance_km",                # Road distance in km
        "historical_fraud_count",     # How many fraud withdrawals at this ATM historically
        "h3_fraud_density",           # Average fraud count of ATMs in same H3 hex cell
        "mule_atm_affinity",          # Has THIS specific mule used THIS ATM before? (0 or 1)
        "mule_network_affinity",      # Has ANY mule in this network used this ATM? (count)
        "time_of_day_sin",            # sin(2π × hour/24) — cyclical encoding of hour
        "time_of_day_cos",            # cos(2π × hour/24)
        "is_weekend",                 # 1 if Saturday/Sunday, 0 otherwise
        "bank_match_score",           # Does mule prefer same bank as this ATM? (0 or 1)
        "atm_type_encoded",           # ATM=0, Branch=1, BC=2
        "h3_ring_distance",           # How many H3 rings away from mule (0=same hex)
    ]

📌 WHAT TO IMPLEMENT HERE:

    TRAINING DATA PREPARATION:
    def prepare_ltr_training_data(
        historical_tx_path: str,
        atm_data_path: str,
        distance_matrix_path: str
    ) -> tuple[pd.DataFrame, list[int], list[int]]:
        """
        Builds the LambdaMART training dataset from historical transaction data.

        LambdaMART requires data in a specific format:
        - X: feature matrix (rows = candidate ATMs, columns = features above)
        - y: relevance labels (0-3 scale: 3=definitely withdrew here, 0=never)
        - groups: list of query sizes (how many candidates per mule event)
               e.g., [150, 143, 178, ...] — one number per fraud event in history

        Steps:
        1. Load historical_transactions.csv and atms_master.csv.
        2. For each historical fraud event where withdrawal_atm_id is known:
           a. The "query" = all ATMs that were candidates for this mule event.
           b. The ATM where the mule ACTUALLY withdrew = relevance label 3.
           c. All other ATMs in the candidate set = relevance label 0.
           d. Build feature vectors for each candidate ATM.
        3. Return (X_df, y_labels, groups_list) for LightGBM training.
        """

    MODEL TRAINING:
    def train_ltr_model(X, y, groups, save_path: str = "ml_engine/weights/ltr_model.txt"):
        """
        Trains the LightGBM LambdaMART model.

        import lightgbm as lgb

        train_data = lgb.Dataset(X, label=y, group=groups)

        params = {
            "objective": "lambdarank",    # LambdaMART
            "metric": "ndcg",             # Normalized Discounted Cumulative Gain
            "ndcg_eval_at": [1, 3, 5],   # Evaluate NDCG@1, @3, @5
            "num_leaves": 63,
            "learning_rate": 0.05,
            "n_estimators": 200,
            "feature_fraction": 0.8,
        }

        model = lgb.train(params, train_data, num_boost_round=200)
        model.save_model(save_path)
        return model
        """

    MODEL LOADING (lazy, at module level):
    _ltr_model = None
    def _load_ltr_model(model_path: str = "ml_engine/weights/ltr_model.txt"):
        import lightgbm as lgb
        return lgb.Booster(model_file=model_path)

    MAIN RANKING FUNCTION (called by inference_pipeline.py):
    def rank_atm_candidates(
        candidate_atms: list[dict],
        mule_account_id: str,
        transaction_timestamp: str
    ) -> list[dict]:
        """
        Builds features for each candidate, runs LambdaMART prediction,
        and returns the candidates sorted by predicted relevance score.

        Steps:
        1. Load model if not already loaded.
        2. For each candidate, build the feature vector using the fields
           listed under FEATURE ENGINEERING above.
        3. Stack into a numpy array or pandas DataFrame X.
        4. Predict: scores = model.predict(X)
           Each score is the LambdaMART relevance score for that candidate.
        5. Attach scores: candidates[i]['score'] = scores[i]
        6. Sort by score descending.
        7. Return sorted candidates list.
        8. Also return the feature matrix (X) so explainability.py can
           compute SHAP values on it.
        """

📌 HOW IT CONNECTS TO OTHER FILES:
    - Called BY: ml_engine/pipelines/inference_pipeline.py (STEP 3, if mule has history).
    - Input: candidate_atms list from spatial_filter.py.
    - Output: sorted candidates + feature matrix (for SHAP in explainability.py).
    - Training: Done once via a notebook in ml_engine/notebooks/ using Role 5's CSV data.
    - Model weights saved to: ml_engine/weights/ltr_model.txt.

📌 LIBRARIES TO USE:
    - lightgbm (pip install lightgbm)
    - pandas
    - numpy
    - datetime (for feature engineering)
"""

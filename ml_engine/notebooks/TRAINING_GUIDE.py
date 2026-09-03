"""
FILE: ml_engine/notebooks/01_training_pipeline.ipynb (use this as a Python script outline)
ROLE: Role 2 — ML/AI Engineer
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📌 WHAT IS THIS FILE?
    This is the master training notebook/script for all ML models in the system.
    Run this ONCE (before the hackathon demo) to train both the Survival Analysis
    (WHEN) model and the LightGBM LambdaMART (WHERE) model, and save their weights
    to the ml_engine/weights/ directory.

📌 WHAT TO IMPLEMENT HERE (as a Jupyter notebook or Python script):

    SECTION 1 — DATA LOADING:
        - Load simulation/data/historical_transactions.csv
        - Load simulation/data/atms_master.csv
        - Load simulation/data/distance_matrix.json
        - Print shape and sample rows to verify data quality.
        - Check for null values and handle them.

    SECTION 2 — SURVIVAL ANALYSIS TRAINING (WHEN Model):
        from ml_engine.models.survival_time import prepare_survival_data, train_survival_model
        df = prepare_survival_data("simulation/data/historical_transactions.csv")
        kmf = train_survival_model(df)
        # Plot the Kaplan-Meier survival curve to visualize:
        # kmf.plot_survival_function()  → shows P(not withdrawn yet) vs time
        # This plot is GREAT to include in your SIH presentation slides!

    SECTION 3 — LAMBDAMART TRAINING (WHERE Model):
        from ml_engine.models.ltr_ranker import prepare_ltr_training_data, train_ltr_model
        X, y, groups = prepare_ltr_training_data(
            "simulation/data/historical_transactions.csv",
            "simulation/data/atms_master.csv",
            "simulation/data/distance_matrix.json"
        )
        print(f"Training on {len(y)} candidate-event pairs across {len(groups)} fraud events")
        model = train_ltr_model(X, y, groups)
        # Print feature importances to verify the model learned correctly:
        import lightgbm as lgb
        lgb.plot_importance(model, max_num_features=10)

    SECTION 4 — VALIDATION (Very Important for SIH Presentation):
        - Take 20% of historical events as a test set (holdout).
        - For each test event, run the full inference pipeline on it.
        - Compare: which rank did the actual withdrawal ATM get in our prediction?
        - Compute: Hit Rate @ 1 (was correct ATM our Rank #1?)
                   Hit Rate @ 3 (was correct ATM in our Top-3?)
                   Hit Rate @ 5 (was correct ATM in our Top-5?)
        - A good result to aim for: Hit Rate @1 > 40%, Hit Rate @5 > 80%.
        - SHOW THIS GRAPH IN THE PRESENTATION. Judges love quantified accuracy.

    SECTION 5 — VERIFY FULL PIPELINE END-TO-END:
        from ml_engine.pipelines.inference_pipeline import predict_fraud_cashout
        test_input = {
            "mule_account_id": "ACC_MULE_0042",
            "last_latitude": 28.6315,
            "last_longitude": 77.2167,
            "transaction_amount": 75000.0,
            "transaction_timestamp": "2026-09-03T14:00:00",
            "case_id": "TEST-CASE-001",
            "victim_account_id": "ACC_VICTIM_0001",
        }
        result = predict_fraud_cashout(test_input)
        import json
        print(json.dumps(result, indent=2))
        # Verify the output matches the PredictionAlert schema.
"""

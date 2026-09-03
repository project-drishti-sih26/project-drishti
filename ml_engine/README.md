# 🧠 Role 2: ML/AI Engineer (Predictive Brain)

## 📌 Ownership
* **Owner:** ML/AI Engineer (Role 2)
* **Stack:** Python 3.11+, LightGBM (LambdaMART), lifelines (Survival Analysis), SHAP, H3-py, osmnx, scikit-learn.

---

## 📂 Folder Structure
```
ml_engine/
├── models/
│   ├── ltr_ranker.py          # LightGBM LambdaMART Learning-to-Rank model (WHERE)
│   ├── survival_time.py       # lifelines Kaplan-Meier / Cox PH model (WHEN)
│   └── fallback_heuristic.py  # Cold-start formula: (Fraud_History * 0.7) + (1/Distance * 0.3)
├── pipelines/
│   ├── spatial_filter.py      # H3 spatial hex pruning & distance matrix lookup
│   ├── explainability.py      # SHAP values -> Human readable strings for police
│   └── inference_pipeline.py  # Master entrypoint: predict_where_and_when()
├── weights/                   # Exported model weights (.txt, .pkl, .joblib)
├── notebooks/                 # Jupyter exploratory analysis & training notebooks
├── requirements.txt           # ML engine dependencies
└── README.md                  # This guide
```

---

## 🎯 Deliverables & Key Tasks
1. **WHERE Model (`models/ltr_ranker.py`):**
   - Candidate filtering: Use H3 spatial indexing to filter national ATMs down to ~200 reachable candidates.
   - Ranking: LightGBM LambdaMART scoring candidates based on travel distance, ATM historical fraud density, and mule affinity.
2. **WHEN Model (`models/survival_time.py`):**
   - Predicts the withdrawal time window (e.g., "in 25-45 minutes") using Survival Analysis.
3. **Cold-Start Fallback Heuristic (`models/fallback_heuristic.py`):**
   - For unknown mules with no history:
     $$\text{Score} = (\text{Fraud\_History} \times 0.7) + \left(\frac{1}{\text{Distance}} \times 0.3\right)$$
4. **SHAP AI Explainability (`pipelines/explainability.py`):**
   - Translate model outputs into natural language for police dispatch:
     *"Ranked #1: 6-minute road travel time + historically used by this mule network."*
5. **Unified Inference Hook (`pipelines/inference_pipeline.py`):**
   - Provide a clean callable function for Role 1 (Backend Engineer):
     `predict_fraud_cashout(transaction_data) -> PredictionPayload`

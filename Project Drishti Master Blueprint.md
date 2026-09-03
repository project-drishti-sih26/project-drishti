# **👁️ Project Drishti: Predictive Analytics for Cybercrime**

**SIH Problem Statement:** SIH26184 (Indian Cybercrime Coordination Centre \- I4C)

**Domain:** Machine Learning, Spatial-Temporal Forecasting, Fintech Security

## **1\. Executive Summary**

### **The Problem (Reactive Policing)**

Currently, law enforcement relies on reactive tracing for cybercrimes. When a victim reports a cyber fraud (e.g., OTP scam), scammers rapidly route the funds through a network of "mule" bank accounts and withdraw the cash from a distant ATM. Police are only alerted *after* the cash has disappeared.

### **The Solution (Proactive Forecasting)**

**Project Drishti** is a proactive AI intelligence radar. It monitors live transaction graphs and, the moment stolen funds hit a known mule network, predicts the scammers' next move before it happens.

It answers two exact questions during an active fraud:

1. **WHERE:** Predicts the Top-5 specific physical ATMs/locations the mule will use (Ranked).  
2. **WHEN:** Forecasts the exact time window (e.g., "in 25-45 minutes") the withdrawal will occur.  
   *Result: Giving police a 20-minute head start to intercept the criminal.*

## **2\. Master System Architecture**

### **Tech Stack**

* **Frontend (Command Center):** React.js, Tailwind CSS (Dark Mode), Mapbox GL JS (for spatial H3 hex grids & heatmaps), Recharts (for velocity graphs).  
* **Backend (Core Logic):** Python, FastAPI (Async), WebSockets (for live streaming), JWT Auth & RBAC (Role-Based Access Control for security).  
* **Database:** PostgreSQL with PostGIS (for spatial queries).  
* **Machine Learning Engine:** LightGBM (LambdaMART for ranking), lifelines (for Survival Time Analysis), shap (for AI explainability), h3-py & osmnx (for spatial road networks).  
* **Data Simulation:** Faker, pandas, networkx (to generate synthetic fraud networks for the demo).

## **3\. The Machine Learning Engine**

The system uses a 4-step Retrieval \+ Learning-to-Rank (LTR) pipeline, moving away from flawed binary classification.

### **Step 1: Activation Trigger**

The model sits idle until a rapid, suspicious transfer lands in a known high-risk mule account (Incoming\_Amount \> Threshold).

### **Step 2: WHEN Engine (Time Forecasting)**

* **Model:** Survival Analysis (Kaplan-Meier / Cox Proportional Hazards).  
* **Output:** Probability of withdrawal within a time frame (e.g., 14:30 \- 15:00).

### **Step 3: WHERE Engine (Two-Stage Spatial Prediction)**

* **Phase 1 (Candidate Retrieval):** Uses H3 spatial indexing and a **Pre-computed Distance Matrix** to filter 100,000 national ATMs down to \~200 locations physically reachable by road within the predicted time window.  
* **Phase 2 (Learning-to-Rank):** LightGBM (LambdaMART) scores the candidates based on:  
  * distance\_to\_last\_known\_node (Road travel time)  
  * atm\_historical\_fraud\_count (Fraud density)  
  * mule\_atm\_affinity (Historical preference of this mule)  
* **Cold-Start Fallback Heuristic:** If a mule is 100% new, the system bypasses the ML block and uses: Score \= (Fraud\_History × 0.7) \+ (1/Distance × 0.3) to ensure a prediction is always made.

### **Step 4: AI Explainability (SHAP)**

No black boxes. SHAP values convert model scores into human-readable strings for police (e.g., *"Ranked \#1: 6-minute road travel time \+ historically used by this mule network."*).

## **4\. Database Schema (SQLAlchemy Reference)**

\# 1\. Accounts Table  
class Account(Base):  
    \_\_tablename\_\_ \= 'accounts'  
    account\_id \= Column(String, primary\_key=True)  
    account\_type \= Column(Enum("Standard", "Mule"))  
    risk\_score \= Column(Float, default=0.0)

\# 2\. Transactions Table (Graph Edges)  
class Transaction(Base):  
    \_\_tablename\_\_ \= 'transactions'  
    tx\_id \= Column(String, primary\_key=True)  
    sender\_id \= Column(String, ForeignKey('accounts.account\_id'))  
    receiver\_id \= Column(String, ForeignKey('accounts.account\_id'))  
    amount \= Column(Float, nullable=False)  
    timestamp \= Column(DateTime, default=datetime.utcnow)  
    case\_id \= Column(String, nullable=True)

\# 3\. Physical Locations (ATMs/BCs)  
class PhysicalLocation(Base):  
    \_\_tablename\_\_ \= 'physical\_locations'  
    location\_id \= Column(String, primary\_key=True)  
    location\_type \= Column(Enum("ATM", "Branch", "BC"))  
    latitude \= Column(Float)  
    longitude \= Column(Float)  
    historical\_fraud\_count \= Column(Integer, default=0)

\# 4\. Cases Table  
class Case(Base):  
    \_\_tablename\_\_ \= 'cases'  
    case\_id \= Column(String, primary\_key=True)  
    victim\_account\_id \= Column(String, ForeignKey('accounts.account\_id'))  
    compromised\_amount \= Column(Float)  
    status \= Column(String, default="ACTIVE")  

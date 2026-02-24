# 🚀 Agentic Feedback System: Capstone 2026
**Powered by Gemini 2.5 Flash-Lite & Streamlit**

An automated, multi-agent pipeline designed to process customer feedback at scale. This system utilizes AI agents to classify sentiment, extract key features, and validate data quality using the latest Google Generative AI models.

## 🌟 Key Features
* **Multi-Agent Orchestration:** Specialized agents for Classification, Extraction, and QA.
* **Gemini 2.5 Flash-Lite Integration:** Optimized for high-speed, cost-effective inference.
* **Intelligent CSV Processing:** Smart column mapping and auto-ID generation for seamless mobile/desktop uploads.
* **Secure Secrets Management:** Fully integrated with Streamlit Cloud Secrets for API key safety.
* **Robust Error Handling:** System detects pipeline freezes and outputs a "stuck" status instead of crashing.

## 🏗️ Architecture
The system follows a modular architecture where the `LLMClient` interfaces with the Google Gemini v1 API, and the `Orchestrator` manages the flow of data between agents.



## 🛠️ Tech Stack
* **LLM:** Google Gemini 2.5 Flash-Lite (v1 API)
* **Frontend:** Streamlit
* **Data Handling:** Pandas
* **Language:** Python 3.11

## 🚀 Getting Started

### 1. Prerequisites
* Python 3.11
* Google AI Studio API Key

### 2. Local Setup
1.  **Clone the repository:**

    git clone [https://github.com/ChavanSneh/CapStone_project.git](https://github.com/ChavanSneh/CapStone_project.git)
    cd CapStone_project
    
2.  **Install dependencies:**

    pip install -r requirements.txt
    
3.  **Configure Secrets:**
    Create a `.streamlit/secrets.toml` file (do not commit this!):
    toml
    GEMINI_API_KEY = "your_actual_key_here"
    
4.  **Run the app:**
    
    streamlit run streamlit_app.py
    

## ☁️ Deployment
This project is optimized for **Streamlit Cloud**. 
1.  Ensure `GEMINI_API_KEY` is added to the **App Settings > Secrets**.
2.  The system is configured to ignore local `venv` folders to ensure a clean build on Linux servers.

## 📝 CSV Format
The system is flexible. You can upload a CSV with a column named `user_feedback` or simply `feedback`. The system will automatically generate `feedback_id` if missing.


**Developed by:** Chavan Sneh  
**Version:** 1.2.0 (2026 Stable)
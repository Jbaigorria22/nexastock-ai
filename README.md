# NexaStock AI 🤖📦
**Serverless Supply Chain Copilot & Inventory Control Tower**

NexaStock AI is an event-driven, AI-powered control tower designed to solve a critical business problem: **supply chain disruptions and stockouts**. 

By leveraging real-time data and Generative AI, this system identifies critical inventory risks and prescribes actionable purchase plans, acting as an automated warehouse manager.

## 🏗️ Cloud Architecture (AWS)
This project is built using a **100% Serverless Cloud-Native** architecture, entirely provisioned using **Infrastructure as Code (Terraform)** and automated via **GitHub Actions (CI/CD)**.

* **Frontend:** Streamlit (Python) for an enterprise-grade UI.
* **Backend API:** FastAPI running on **AWS Lambda** (via Mangum adapter).
* **API Gateway:** Exposes the Lambda function securely to the web.
* **Database:** **Amazon DynamoDB** (NoSQL) for high-performance, low-latency inventory reads.
* **Security:** **AWS SSM Parameter Store** manages encrypted secrets (OpenAI API Keys) accessed in runtime via IAM Roles (Least Privilege Principle).
* **AI Engine:** OpenAI `gpt-4o-mini` integration for predictive analysis and natural language queries.

## ✨ Key Features
1. **Real-time Visibility:** Live tracking of inventory value, critical items, and high-risk products.
2. **AI Copilot:** Natural language interface to ask complex supply chain questions (e.g., *"What is my exposure if supplier X delays shipping?"*).
3. **Automated Purchase Plans:** AI-prescribed restocking quantities and estimated costs based on dynamic thresholds.
4. **CI/CD Pipeline:** Fully automated deployment to AWS via GitHub Actions using Dockerized Lambda builds for Linux environments.

## 🚀 Infrastructure Deployment
The AWS infrastructure is defined in the `/infrastructure` directory. To deploy it:
```bash
cd infrastructure
terraform init
terraform plan
terraform apply
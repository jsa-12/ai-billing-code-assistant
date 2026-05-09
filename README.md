# AI Billing Code Assistant

## Overview

AI Billing Code Assistant is a Streamlit-based healthcare workflow application that helps providers review synthetic patient visit information and retrieve relevant ICD-10 billing codes from a real billing dataset.

The system simulates a clinical billing review workflow where providers can:
- Log in to the platform
- Review patient visit summaries
- Generate ICD-10 billing code suggestions
- Perform human review before final selection

---

## Problem

Manual billing code lookup can be time-consuming and inconsistent. Providers and billing staff often search through large ICD-10 datasets manually to identify the correct billing codes for patient visits.

This project aims to simplify the workflow by automatically retrieving relevant ICD-10 billing codes based on patient visit information.

---

## Solution

The application uses:
- Streamlit frontend
- Real ICD-10 billing dataset
- Keyword matching workflow
- Human review interface

The system suggests billing codes based on patient symptoms, diagnoses, and visit notes.

---

## Features

- Provider login workflow
- Patient dashboard
- Clinical billing review interface
- ICD-10 billing code suggestions
- Human-in-the-loop workflow
- Responsive healthcare UI

---

## Dataset

The project uses a real ICD-10 billing code dataset:

`Data/Billing_codes.csv`

The dataset contains:
- ICD-10 codes
- Code descriptions
- Real medical billing terminology

---

## Evaluation

The project was evaluated using several synthetic patient visit examples.

### Baseline

Manual ICD-10 code lookup using keyword search.

### Billing Assistant Workflow

Automated ICD-10 billing code suggestions from patient visit information.

| Test Case | Manual Workflow | Billing Assistant |
|---|---|---|
| Chest pain | Required manual dataset search | Suggested relevant ICD-10 codes instantly |
| Diabetes follow-up | Multiple code options caused confusion | Returned narrowed billing suggestions |
| Migraine visit | Time-consuming lookup process | Faster billing code retrieval |

### Findings

The assistant reduced the time needed to search for billing codes and simplified the billing review process. The system worked best when visit descriptions were clear and specific.

---

## Tech Stack

- Python
- Streamlit
- Pandas
- ICD-10 Dataset

---

## How To Run

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Future Improvements

- Expand the ICD-10 billing dataset with additional clinical conditions and procedures
- Improve billing code retrieval using semantic search and better ranking methods
- Support CPT procedure codes in addition to ICD-10 diagnosis codes
- Improve clinical note understanding using more advanced natural language processing
- Add secure authentication and role-based access control for providers
- Deploy the application as a cloud-hosted healthcare workflow platform
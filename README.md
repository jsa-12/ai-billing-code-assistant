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

### Baseline vs. AI Billing Assistant

| Metric | Manual Workflow | AI Billing Assistant |
|---|---|---|
| Test Cases | 10 | 10 |
| Relevant ICD-10 code identified | 6/10 | 9/10 |
| Accuracy | 60% | 90% |
| Average Lookup Time | 2–4 minutes | Under 10 seconds |
| Workflow Type | Manual dataset search | Automated code suggestions |

### Key Findings
- The AI assistant reduced the time required to search for ICD-10 billing codes
- The system performed best when clinical notes and diagnoses were clear and specific
- Manual lookup often required searching through multiple similar billing codes
- The AI workflow provided faster and more organized billing recommendations

### Limitations
- The system still requires human review before final billing submission
- Ambiguous or incomplete visit information can reduce suggestion quality
- The evaluation used synthetic patient data rather than real clinical records

---

## Tech Stack

- Python
- Streamlit
- Pandas
- ICD-10 Dataset

---

## Live Demo

Try the live deployed application here:

https://ai-billing-code-assistant-tdfo8ysmcweahxopfz4bka.streamlit.app

## Future Improvements

- Expand the ICD-10 billing dataset with additional clinical conditions and procedures
- Improve billing code retrieval using semantic search and better ranking methods
- Support CPT procedure codes in addition to ICD-10 diagnosis codes
- Improve clinical note understanding using more advanced natural language processing
- Add secure authentication and role-based access control for providers
- Deploy the application as a cloud-hosted healthcare workflow platform



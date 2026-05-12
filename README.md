# AI Billing Code Assistant

## Context, User, and Problem

AI Billing Code Assistant is a Streamlit-based healthcare workflow application designed to help providers and billing staff review synthetic patient visit information and retrieve relevant ICD-10 billing code suggestions.

The idea for the project came from a friend who previously worked at a clinic and explained how providers and billing staff sometimes spend significant time manually searching through ICD-10 billing datasets to identify the correct billing codes for patient visits. Manual billing workflows can be time-consuming, repetitive, and inconsistent, especially when multiple similar billing codes exist for the same condition.

This project aims to simplify the billing review workflow by automatically generating billing code suggestions based on patient visit information such as diagnosis, procedure, symptoms, and clinical notes.

ICD-10 billing codes are standardized medical classification codes used by healthcare providers and insurance companies for diagnoses and billing purposes. For example, the ICD-10 code “J06.9” represents an acute upper respiratory infection.

The application was developed using Codex-assisted prompt engineering to iteratively design and improve the workflow and healthcare interface.

---

## Solution and Design

The system simulates a healthcare billing review workflow where providers can:

- Log into the platform
- Review patient visit summaries
- Review clinical notes and diagnoses
- Generate ICD-10 billing code suggestions
- Perform human review before final billing submission

The application uses:

- Streamlit frontend
- Real ICD-10 billing dataset
- Keyword-matching workflow
- Synthetic patient visit records
- Human-in-the-loop billing review workflow

The project also includes:

- Provider login workflow
- Patient dashboard
- Clinical billing review interface
- Billing code recommendation workflow
- Responsive healthcare-style UI for desktop and mobile devices

The dataset used in the project contains:

- ICD-10 billing codes
- Billing code descriptions
- Medical terminology and classifications

Dataset location:

```bash
Data/Billing_codes.csv
```

---

## Evaluation and Results

The project was evaluated using 10 synthetic patient visit test cases.

### Baseline Workflow

The baseline comparison used manual ICD-10 dataset lookup through keyword searching and manual review.

### Baseline vs. AI Billing Assistant

| Metric | Manual Workflow | AI Billing Assistant |
|---|---|---|
| Test Cases | 10 | 10 |
| Relevant ICD-10 code identified | 6/10 | 9/10 |
| Accuracy | 60% | 90% |
| Average Lookup Time | 2–4 minutes | <10 seconds |
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
- Some billing suggestions may still return broader or partially related ICD-10 codes

---

## Artifact Snapshot

### Live Demo Video

YouTube Demo Link: https://www.youtube.com/watch?v=HGGHULJR0Fw

### Example Workflow

1. Provider reviews patient information
2. User selects visit reason, diagnosis, and procedure
3. System generates top ICD-10 billing code suggestions
4. Provider performs final review before billing submission

---

## Tech Stack

- Python
- Streamlit
- Pandas
- ICD-10 Billing Dataset
- GitHub
- Codex-assisted prompt engineering

---

## Setup and Usage Instructions

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the application:

```bash
streamlit run app.py
```

Open the generated Streamlit local URL in your browser to access the application.

---

## Live Demo Application

Streamlit Deployment:

https://ai-billing-code-assistant-tdfo8ysmcweahxopfz4bka.streamlit.app

---

## Future Improvements

- Expand the ICD-10 billing dataset with additional conditions and procedures
- Improve billing retrieval using semantic search and ranking methods
- Add CPT procedure code support
- Improve clinical note understanding using advanced NLP workflows
- Add secure authentication and role-based access control
- Deploy the system as a larger healthcare workflow platform
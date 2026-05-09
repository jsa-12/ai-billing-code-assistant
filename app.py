import base64
import copy
import os
import re

import pandas as pd
import streamlit as st

SHARED_PASSWORD = "demojhu@12"
BILLING_CODES_PATH = "Data/Billing_codes.csv"
TOKEN_PATTERN = re.compile(r"[a-z0-9]+")
STOPWORDS = {
    "and",
    "the",
    "with",
    "for",
    "from",
    "that",
    "this",
    "have",
    "has",
    "had",
    "into",
    "today",
    "patient",
    "reports",
    "report",
    "visit",
    "review",
    "follow",
    "followup",
    "follow-up",
    "about",
    "after",
    "before",
    "during",
    "mild",
    "office",
    "focus",
    "focused",
    "clinic",
    "completed",
    "evaluation",
    "examination",
    "exam",
    "outpatient",
    "established",
    "counseling",
    "counsel",
    "encounter",
    "routine",
    "adult",
    "general",
    "disease",
    "medication",
    "regimen",
    "therapy",
    "management",
}
TOKEN_EXPANSIONS = {
    "gastroesophageal": {"gastro", "esophageal", "reflux"},
    "heartburn": {"reflux"},
    "hypertension": {"pressure"},
    "uri": {"upper", "respiratory", "infection"},
    "back": {"lumbar"},
    "pharyngitis": {"throat"},
}

PATIENT_DIRECTORY = [
    {"name": "Fahda Alajmi", "gender": "Female"},
    {"name": "Rawan Alghebiwi", "gender": "Female"},
    {"name": "Rohan Allen", "gender": "Male"},
    {"name": "Jawad Alobaidan", "gender": "Male"},
    {"name": "Koniska Bandyopadhyay", "gender": "Female"},
    {"name": "Bill Bwana", "gender": "Male"},
    {"name": "Khadidiatou Dia", "gender": "Female"},
    {"name": "Yuying Ding", "gender": "Female"},
    {"name": "Zihang Ding", "gender": "Male"},
    {"name": "Chengcheng Du", "gender": "Female"},
    {"name": "Tianjin Duan", "gender": "Male"},
    {"name": "Mingyu Gao", "gender": "Male"},
    {"name": "Bingning Guo", "gender": "Female"},
    {"name": "Haojia Hu", "gender": "Male"},
    {"name": "Haitong Huang", "gender": "Male"},
    {"name": "Ruoxuan Huang", "gender": "Female"},
    {"name": "Xiaoxi Jiang", "gender": "Female"},
    {"name": "Tuosheng Jiao", "gender": "Male"},
    {"name": "Harang Ju", "gender": "Male"},
    {"name": "Qi Kan", "gender": "Male"},
    {"name": "Chengyao Li", "gender": "Female"},
    {"name": "Lyra Li", "gender": "Female"},
    {"name": "Shuzheng Lin", "gender": "Female"},
    {"name": "Wilson Liu", "gender": "Male"},
    {"name": "Lixing Lu", "gender": "Male"},
    {"name": "Yiyun Ma", "gender": "Female"},
    {"name": "Calis Nguyen", "gender": "Male"},
    {"name": "Tieyuan Qian", "gender": "Male"},
    {"name": "Bocheng Shi", "gender": "Male"},
    {"name": "Sophia Tamakloe", "gender": "Female"},
    {"name": "Zhonghuan Tang", "gender": "Male"},
    {"name": "Emanuel Telles Chaves", "gender": "Male"},
    {"name": "Yiyang Tong", "gender": "Female"},
    {"name": "Tito Vivas Buitrago", "gender": "Male"},
    {"name": "Mingyu Wang", "gender": "Male"},
    {"name": "Ruiming Wang", "gender": "Male"},
    {"name": "Xiaojia Wang", "gender": "Female"},
    {"name": "Yijing Wang", "gender": "Female"},
    {"name": "Yuzhou Wang", "gender": "Male"},
    {"name": "Zihan Wang", "gender": "Male"},
    {"name": "Ziyu Wang", "gender": "Female"},
    {"name": "Yixin Wei", "gender": "Female"},
    {"name": "Haoyu Xie", "gender": "Male"},
    {"name": "Xin Yuan", "gender": "Female"},
    {"name": "Hanrui Zhang", "gender": "Female"},
    {"name": "Shangjun Zhang", "gender": "Female"},
    {"name": "Yuhui Zhang", "gender": "Female"},
    {"name": "Rui Zhao", "gender": "Male"},
    {"name": "Shiyi Zhao", "gender": "Female"},
    {"name": "Xingyuan Zheng", "gender": "Male"},
    {"name": "Minying Zhou", "gender": "Female"},
    {"name": "Yuan Zhou", "gender": "Male"},
]

INSURANCE_OPTIONS = [
    "Active PPO",
    "Commercial HMO",
    "Student Health Plan",
    "Medicaid Managed Care",
    "Employer-Sponsored Plan",
    "Marketplace Bronze Plan",
]

CASE_BLUEPRINTS = [
    {
        "primary_condition": "Hypertension",
        "visit_type": "Chronic care follow-up",
        "reason_options": [
            "Blood pressure follow-up",
            "Medication refill and blood pressure review",
            "Hypertension check after elevated home readings",
            "Routine follow-up for blood pressure management",
        ],
        "diagnosis_options": [
            "Essential hypertension",
            "Primary hypertension",
            "Hypertension, stable on treatment",
            "Essential hypertension with ongoing medication management",
        ],
        "procedure_options": [
            "Established patient follow-up with medication management",
            "Office follow-up for blood pressure management",
            "Chronic care visit with cardiovascular review",
            "Established patient evaluation for hypertension follow-up",
        ],
        "background_options": [
            "essential hypertension treated with a daily antihypertensive",
            "chronic hypertension monitored with home readings",
            "elevated blood pressure requiring medication follow-up",
            "hypertension managed with lifestyle changes and medication",
        ],
        "note_options": [
            "Patient presents for blood pressure follow-up and medication review. Home blood pressure readings have remained above target this week, and medication management was reviewed during follow-up.",
            "Patient is here for hypertension follow-up after elevated blood pressure readings at home. Cardiovascular review was stable, and medication management was discussed in clinic.",
            "Patient returns for blood pressure management with no acute symptoms. Hypertension follow-up and medication adherence were reviewed during today's visit.",
            "Patient presents for follow-up of hypertension with mildly elevated blood pressure today. Home monitoring, medication management, and follow-up planning were completed in clinic.",
        ],
        "vital_options": [
            {"blood_pressure": "138/86 mmHg", "heart_rate": "78 bpm", "temperature": "98.4 F", "oxygen_saturation": "98%"},
            {"blood_pressure": "142/88 mmHg", "heart_rate": "80 bpm", "temperature": "98.5 F", "oxygen_saturation": "98%"},
            {"blood_pressure": "134/82 mmHg", "heart_rate": "76 bpm", "temperature": "98.2 F", "oxygen_saturation": "99%"},
            {"blood_pressure": "146/90 mmHg", "heart_rate": "82 bpm", "temperature": "98.6 F", "oxygen_saturation": "98%"},
        ],
    },
    {
        "primary_condition": "Type 2 Diabetes",
        "visit_type": "Medication management visit",
        "reason_options": [
            "Diabetes follow-up and medication review",
            "Blood sugar follow-up visit",
            "Routine follow-up for type 2 diabetes",
            "Diabetes medication management",
        ],
        "diagnosis_options": [
            "Type 2 diabetes mellitus",
            "Type 2 diabetes mellitus without complications",
            "Type 2 diabetes, controlled on medication",
            "Type 2 diabetes mellitus with hyperglycemia history",
        ],
        "procedure_options": [
            "Established patient follow-up with diabetes counseling",
            "Medication management visit for diabetes",
            "Chronic care follow-up with glucose review",
            "Office follow-up for diabetes treatment plan review",
        ],
        "background_options": [
            "type 2 diabetes managed with oral medication",
            "type 2 diabetes with home glucose monitoring",
            "chronic diabetes requiring routine medication review",
            "type 2 diabetes followed in outpatient primary care",
        ],
        "note_options": [
            "Patient presents for diabetes follow-up and medication review. Home glucose logs were reviewed, and dietary counseling was reinforced during the visit.",
            "Patient is here for blood sugar follow-up with no acute complaints. Diabetes medication management and interval glucose trends were discussed in clinic.",
            "Patient returns for type 2 diabetes follow-up. Home glucose readings have been mildly elevated after meals, and treatment plan review was completed.",
            "Patient presents for diabetes management and follow-up of recent lab trends. Medication adherence and glucose monitoring were reviewed today.",
        ],
        "vital_options": [
            {"blood_pressure": "126/80 mmHg", "heart_rate": "74 bpm", "temperature": "98.2 F", "oxygen_saturation": "99%"},
            {"blood_pressure": "130/82 mmHg", "heart_rate": "76 bpm", "temperature": "98.3 F", "oxygen_saturation": "98%"},
            {"blood_pressure": "128/78 mmHg", "heart_rate": "72 bpm", "temperature": "98.1 F", "oxygen_saturation": "99%"},
            {"blood_pressure": "132/84 mmHg", "heart_rate": "78 bpm", "temperature": "98.4 F", "oxygen_saturation": "98%"},
        ],
    },
    {
        "primary_condition": "Hyperlipidemia",
        "visit_type": "Medication management visit",
        "reason_options": [
            "Cholesterol medication follow-up",
            "Routine lipid management visit",
            "Hyperlipidemia follow-up after recent labs",
            "Medication review for elevated cholesterol",
        ],
        "diagnosis_options": [
            "Hyperlipidemia",
            "Mixed hyperlipidemia",
            "Elevated cholesterol",
            "Hyperlipidemia, ongoing treatment",
        ],
        "procedure_options": [
            "Established patient lipid management follow-up",
            "Medication review with lifestyle counseling",
            "Office follow-up for cholesterol management",
            "Chronic care visit with lab review",
        ],
        "background_options": [
            "hyperlipidemia treated with statin therapy",
            "elevated cholesterol monitored with periodic lab work",
            "mixed hyperlipidemia managed through medication and diet",
            "hyperlipidemia requiring preventive follow-up",
        ],
        "note_options": [
            "Patient presents for hyperlipidemia follow-up and review of recent cholesterol labs. Medication tolerance and diet changes were discussed in clinic.",
            "Patient is here for elevated cholesterol follow-up with no acute symptoms. Lipid management and medication adherence were reviewed today.",
            "Patient returns for chronic hyperlipidemia management after recent outpatient labs. Preventive counseling and medication review were completed.",
            "Patient presents for cholesterol medication follow-up. Lifestyle measures, lab trends, and treatment planning were reviewed during the visit.",
        ],
        "vital_options": [
            {"blood_pressure": "124/76 mmHg", "heart_rate": "72 bpm", "temperature": "98.0 F", "oxygen_saturation": "99%"},
            {"blood_pressure": "128/80 mmHg", "heart_rate": "74 bpm", "temperature": "98.1 F", "oxygen_saturation": "99%"},
            {"blood_pressure": "122/78 mmHg", "heart_rate": "70 bpm", "temperature": "98.2 F", "oxygen_saturation": "98%"},
            {"blood_pressure": "126/79 mmHg", "heart_rate": "76 bpm", "temperature": "98.3 F", "oxygen_saturation": "99%"},
        ],
    },
    {
        "primary_condition": "GERD",
        "visit_type": "Established outpatient visit",
        "reason_options": [
            "Heartburn and reflux follow-up",
            "GERD symptom review",
            "Reflux symptoms after meals",
            "Follow-up for chronic heartburn",
        ],
        "diagnosis_options": [
            "Gastroesophageal reflux disease",
            "GERD",
            "Reflux esophagitis symptoms",
            "Gastroesophageal reflux disease without esophagitis",
        ],
        "procedure_options": [
            "Established patient reflux evaluation and counseling",
            "Office follow-up with medication review for GERD",
            "Symptom-focused outpatient evaluation for reflux",
            "Medication management and dietary counseling visit",
        ],
        "background_options": [
            "gastroesophageal reflux disease with meal-related symptoms",
            "chronic heartburn improved by dietary changes",
            "GERD treated with acid-suppressing medication",
            "reflux symptoms followed in primary care",
        ],
        "note_options": [
            "Patient reports reflux and heartburn after evening meals with intermittent abdominal discomfort. GERD symptoms, diet triggers, and medication use were reviewed in clinic.",
            "Patient presents for follow-up of chronic heartburn and reflux. Symptoms are worse after spicy foods, and GERD counseling was reinforced during the visit.",
            "Patient is here for GERD symptom review with ongoing reflux several times per week. Medication response and upper abdominal discomfort were discussed today.",
            "Patient returns for outpatient follow-up of heartburn and reflux symptoms. Abdominal discomfort has improved slightly, and the GERD treatment plan was updated.",
        ],
        "vital_options": [
            {"blood_pressure": "122/78 mmHg", "heart_rate": "74 bpm", "temperature": "98.3 F", "oxygen_saturation": "99%"},
            {"blood_pressure": "118/74 mmHg", "heart_rate": "76 bpm", "temperature": "98.1 F", "oxygen_saturation": "99%"},
            {"blood_pressure": "124/80 mmHg", "heart_rate": "72 bpm", "temperature": "98.4 F", "oxygen_saturation": "98%"},
            {"blood_pressure": "120/76 mmHg", "heart_rate": "78 bpm", "temperature": "98.2 F", "oxygen_saturation": "99%"},
        ],
    },
    {
        "primary_condition": "Low Back Pain",
        "visit_type": "Established outpatient visit",
        "reason_options": [
            "Low back pain after prolonged sitting",
            "Follow-up for chronic low back discomfort",
            "Back pain flare after desk work",
            "Musculoskeletal follow-up for lumbar pain",
        ],
        "diagnosis_options": [
            "Low back pain",
            "Lumbar strain symptoms",
            "Mechanical low back pain",
            "Chronic low back pain without sciatica",
        ],
        "procedure_options": [
            "Office follow-up with musculoskeletal exam",
            "Established patient musculoskeletal evaluation",
            "Outpatient lumbar pain assessment",
            "Problem-focused visit for back pain management",
        ],
        "background_options": [
            "intermittent low back pain related to posture",
            "chronic low back discomfort associated with prolonged sitting",
            "mechanical lumbar pain without neurologic symptoms",
            "recurrent low back pain managed conservatively",
        ],
        "note_options": [
            "Patient reports back pain after prolonged sitting and computer work. No trauma or red flag symptoms were reported, and a musculoskeletal exam was completed in clinic.",
            "Patient presents for low back pain follow-up after a recent flare with desk work. No trauma was reported, and the musculoskeletal exam remained reassuring.",
            "Patient returns for lumbar pain after extended sitting during study and work sessions. No trauma or neurologic changes were noted, and supportive management was reviewed.",
            "Patient reports persistent low back discomfort worse with prolonged sitting. Focused musculoskeletal exam was completed, and no trauma history was identified.",
        ],
        "vital_options": [
            {"blood_pressure": "118/76 mmHg", "heart_rate": "72 bpm", "temperature": "98.2 F", "oxygen_saturation": "99%"},
            {"blood_pressure": "116/72 mmHg", "heart_rate": "70 bpm", "temperature": "98.0 F", "oxygen_saturation": "99%"},
            {"blood_pressure": "120/78 mmHg", "heart_rate": "74 bpm", "temperature": "98.1 F", "oxygen_saturation": "99%"},
            {"blood_pressure": "122/80 mmHg", "heart_rate": "76 bpm", "temperature": "98.3 F", "oxygen_saturation": "98%"},
        ],
    },
    {
        "primary_condition": "Sore Throat/URI",
        "visit_type": "Acute sick visit",
        "reason_options": [
            "Sore throat and congestion",
            "Upper respiratory symptoms with cough",
            "Acute sore throat and fever",
            "Respiratory symptoms for three days",
        ],
        "diagnosis_options": [
            "Acute pharyngitis / upper respiratory infection",
            "Upper respiratory infection",
            "Sore throat with viral URI symptoms",
            "Acute nasopharyngitis",
        ],
        "procedure_options": [
            "Office sick visit with rapid strep evaluation",
            "Focused respiratory office evaluation",
            "Acute outpatient visit with throat exam",
            "Problem-focused sick visit for URI symptoms",
        ],
        "background_options": [
            "no major chronic conditions and a recent upper respiratory illness",
            "an acute sore throat with congestion and cough",
            "new respiratory symptoms after a recent sick contact",
            "mild viral upper respiratory symptoms",
        ],
        "note_options": [
            "Patient reports sore throat, congestion, and mild cough for 3 days with subjective fever. Focused respiratory exam completed and supportive URI care discussed.",
            "Patient presents with sore throat and nasal congestion after recent sick contact. Cough has been mild, and respiratory symptoms were reviewed during the visit.",
            "Patient reports cough, sore throat, and low-grade fever for several days. Focused throat and respiratory exam was completed in clinic.",
            "Patient returns for evaluation of respiratory symptoms including sore throat, congestion, and dry cough. URI counseling and testing discussion were completed today.",
        ],
        "vital_options": [
            {"blood_pressure": "116/72 mmHg", "heart_rate": "92 bpm", "temperature": "99.1 F", "oxygen_saturation": "98%"},
            {"blood_pressure": "118/74 mmHg", "heart_rate": "88 bpm", "temperature": "99.3 F", "oxygen_saturation": "98%"},
            {"blood_pressure": "120/76 mmHg", "heart_rate": "94 bpm", "temperature": "99.5 F", "oxygen_saturation": "97%"},
            {"blood_pressure": "114/70 mmHg", "heart_rate": "90 bpm", "temperature": "99.0 F", "oxygen_saturation": "98%"},
        ],
    },
    {
        "primary_condition": "Allergic Rhinitis",
        "visit_type": "Established outpatient visit",
        "reason_options": [
            "Seasonal allergy follow-up",
            "Sneezing and nasal congestion",
            "Itchy eyes and allergic symptoms",
            "Allergy medication review",
        ],
        "diagnosis_options": [
            "Seasonal allergic rhinitis",
            "Allergic rhinitis",
            "Environmental allergies with rhinitis",
            "Seasonal allergies",
        ],
        "procedure_options": [
            "Outpatient allergy follow-up with medication review",
            "Established patient evaluation for allergic rhinitis",
            "Office visit for seasonal allergy management",
            "Symptom-focused follow-up for environmental allergies",
        ],
        "background_options": [
            "seasonal allergic rhinitis triggered by pollen exposure",
            "environmental allergies with intermittent nasal symptoms",
            "allergic rhinitis controlled with antihistamine use",
            "recurrent seasonal allergies during peak pollen months",
        ],
        "note_options": [
            "Patient reports sneezing, congestion, and itchy eyes during the past week. Seasonal allergies and medication response were reviewed in clinic.",
            "Patient presents for allergic rhinitis follow-up with ongoing nasal congestion and watery eyes. Symptom control and trigger avoidance were discussed today.",
            "Patient returns for seasonal allergy symptoms including sneezing and congestion. Allergic rhinitis treatment plan and medication timing were reviewed.",
            "Patient is here for allergy medication review after recurrent nasal congestion and itchy eyes. Environmental triggers and outpatient follow-up were discussed.",
        ],
        "vital_options": [
            {"blood_pressure": "112/70 mmHg", "heart_rate": "72 bpm", "temperature": "98.1 F", "oxygen_saturation": "99%"},
            {"blood_pressure": "114/72 mmHg", "heart_rate": "74 bpm", "temperature": "98.0 F", "oxygen_saturation": "99%"},
            {"blood_pressure": "116/74 mmHg", "heart_rate": "76 bpm", "temperature": "98.2 F", "oxygen_saturation": "98%"},
            {"blood_pressure": "118/72 mmHg", "heart_rate": "70 bpm", "temperature": "98.3 F", "oxygen_saturation": "99%"},
        ],
    },
    {
        "primary_condition": "Migraine",
        "visit_type": "Medication management visit",
        "reason_options": [
            "Migraine follow-up",
            "Headache medication review",
            "Intermittent migraine symptoms",
            "Follow-up for recurrent headaches",
        ],
        "diagnosis_options": [
            "Migraine without aura",
            "Migraine headaches",
            "Recurrent migraine",
            "Migraine, stable with outpatient management",
        ],
        "procedure_options": [
            "Office follow-up with headache medication review",
            "Established patient visit for migraine management",
            "Neurologic symptom follow-up",
            "Outpatient visit for recurrent headache evaluation",
        ],
        "background_options": [
            "a history of migraine headaches treated with as-needed medication",
            "recurrent migraine symptoms without recent emergency visits",
            "intermittent migraines followed in primary care",
            "migraine headaches associated with stress and poor sleep",
        ],
        "note_options": [
            "Patient presents for migraine follow-up with intermittent headaches over the past month. Medication response and common triggers were reviewed during the visit.",
            "Patient is here for recurrent migraine management. Headache frequency has improved, and outpatient medication review was completed today.",
            "Patient reports several migraine episodes since the last visit without neurologic red flags. Trigger avoidance and symptom management were discussed.",
            "Patient returns for headache medication review after recent migraine symptoms. Follow-up planning and supportive counseling were completed in clinic.",
        ],
        "vital_options": [
            {"blood_pressure": "118/74 mmHg", "heart_rate": "72 bpm", "temperature": "98.1 F", "oxygen_saturation": "99%"},
            {"blood_pressure": "122/76 mmHg", "heart_rate": "74 bpm", "temperature": "98.2 F", "oxygen_saturation": "99%"},
            {"blood_pressure": "116/70 mmHg", "heart_rate": "70 bpm", "temperature": "98.0 F", "oxygen_saturation": "99%"},
            {"blood_pressure": "120/78 mmHg", "heart_rate": "76 bpm", "temperature": "98.3 F", "oxygen_saturation": "98%"},
        ],
    },
    {
        "primary_condition": "Dermatitis/Eczema",
        "visit_type": "Established outpatient visit",
        "reason_options": [
            "Rash follow-up visit",
            "Eczema flare on arms",
            "Itchy skin and redness",
            "Dermatitis medication review",
        ],
        "diagnosis_options": [
            "Atopic dermatitis",
            "Eczema flare",
            "Dermatitis",
            "Atopic eczema",
        ],
        "procedure_options": [
            "Office follow-up with focused skin exam",
            "Established patient dermatology symptom review",
            "Outpatient evaluation for dermatitis flare",
            "Problem-focused skin visit with treatment counseling",
        ],
        "background_options": [
            "eczema with occasional flares during dry weather",
            "atopic dermatitis treated with topical medication",
            "sensitive skin with intermittent dermatitis symptoms",
            "recurrent eczema managed in outpatient primary care",
        ],
        "note_options": [
            "Patient reports itchy rash with mild redness on the forearms. Focused skin exam was completed, and dermatitis treatment options were reviewed.",
            "Patient presents for eczema follow-up after increased dry, itchy patches. Topical medication use and skin care routine were discussed in clinic.",
            "Patient returns with dermatitis flare and ongoing skin irritation. Focused skin exam showed mild redness without drainage or systemic symptoms.",
            "Patient is here for skin medication review after recurrent eczema symptoms. Dry patches and itch control were addressed during the visit.",
        ],
        "vital_options": [
            {"blood_pressure": "114/72 mmHg", "heart_rate": "72 bpm", "temperature": "98.1 F", "oxygen_saturation": "99%"},
            {"blood_pressure": "118/74 mmHg", "heart_rate": "74 bpm", "temperature": "98.2 F", "oxygen_saturation": "99%"},
            {"blood_pressure": "116/70 mmHg", "heart_rate": "70 bpm", "temperature": "98.0 F", "oxygen_saturation": "99%"},
            {"blood_pressure": "120/76 mmHg", "heart_rate": "73 bpm", "temperature": "98.3 F", "oxygen_saturation": "98%"},
        ],
    },
    {
        "primary_condition": "Preventive Visit",
        "visit_type": "Preventive wellness visit",
        "reason_options": [
            "Annual preventive wellness visit",
            "Routine physical exam",
            "Preventive care and screening review",
            "Annual health maintenance visit",
        ],
        "diagnosis_options": [
            "Routine general medical examination",
            "Preventive adult health visit",
            "Wellness examination",
            "General adult preventive visit",
        ],
        "procedure_options": [
            "Preventive medicine visit with counseling",
            "Annual wellness evaluation",
            "Established patient preventive exam",
            "Routine physical with screening review",
        ],
        "background_options": [
            "no major chronic conditions and is presenting for routine preventive care",
            "generally good health and is due for annual wellness review",
            "routine health maintenance needs with no acute complaints",
            "no active medical concerns and is here for preventive screening",
        ],
        "note_options": [
            "Patient presents for preventive care and annual wellness review. Screening history, lifestyle habits, and routine health maintenance were discussed.",
            "Patient is here for routine physical examination with no acute complaints. Preventive counseling and screening recommendations were completed today.",
            "Patient returns for annual preventive visit. General health maintenance, vaccines, and age-appropriate screening plans were reviewed in clinic.",
            "Patient presents for wellness follow-up and routine health screening. No acute concerns were identified during today's preventive visit.",
        ],
        "vital_options": [
            {"blood_pressure": "112/70 mmHg", "heart_rate": "68 bpm", "temperature": "98.1 F", "oxygen_saturation": "99%"},
            {"blood_pressure": "118/72 mmHg", "heart_rate": "70 bpm", "temperature": "98.2 F", "oxygen_saturation": "99%"},
            {"blood_pressure": "116/74 mmHg", "heart_rate": "72 bpm", "temperature": "98.0 F", "oxygen_saturation": "99%"},
            {"blood_pressure": "120/76 mmHg", "heart_rate": "74 bpm", "temperature": "98.3 F", "oxygen_saturation": "98%"},
        ],
    },
    {
        "primary_condition": "Asthma Follow-up",
        "visit_type": "Chronic care follow-up",
        "reason_options": [
            "Asthma medication follow-up",
            "Mild wheezing and inhaler review",
            "Routine asthma control visit",
            "Follow-up for intermittent asthma symptoms",
        ],
        "diagnosis_options": [
            "Mild intermittent asthma",
            "Asthma follow-up",
            "Mild persistent asthma",
            "Reactive airway disease / asthma",
        ],
        "procedure_options": [
            "Established patient respiratory follow-up",
            "Office visit with inhaler technique review",
            "Chronic care visit for asthma management",
            "Outpatient follow-up for asthma symptom control",
        ],
        "background_options": [
            "mild intermittent asthma treated with rescue inhaler use",
            "asthma symptoms that increase with exercise or seasonal triggers",
            "reactive airway symptoms followed in primary care",
            "outpatient asthma management with inhaler therapy",
        ],
        "note_options": [
            "Patient presents for asthma follow-up and inhaler review. Breathing has been stable overall, with mild wheezing only during exercise.",
            "Patient is here for routine asthma management after intermittent shortness of breath. Inhaler use and trigger control were reviewed during the visit.",
            "Patient returns for asthma symptom follow-up with no recent urgent care visits. Respiratory review and medication plan were discussed today.",
            "Patient presents for inhaler medication review and asthma follow-up. Symptoms have remained mild, and outpatient respiratory follow-up was completed.",
        ],
        "vital_options": [
            {"blood_pressure": "118/76 mmHg", "heart_rate": "78 bpm", "temperature": "98.3 F", "oxygen_saturation": "97%"},
            {"blood_pressure": "116/74 mmHg", "heart_rate": "80 bpm", "temperature": "98.2 F", "oxygen_saturation": "98%"},
            {"blood_pressure": "120/78 mmHg", "heart_rate": "76 bpm", "temperature": "98.1 F", "oxygen_saturation": "97%"},
            {"blood_pressure": "114/72 mmHg", "heart_rate": "79 bpm", "temperature": "98.4 F", "oxygen_saturation": "98%"},
        ],
    },
    {
        "primary_condition": "Anxiety Follow-up",
        "visit_type": "Medication management visit",
        "reason_options": [
            "Anxiety medication follow-up",
            "Follow-up for stress and sleep concerns",
            "Mood and anxiety check-in",
            "Medication management for generalized anxiety",
        ],
        "diagnosis_options": [
            "Generalized anxiety disorder",
            "Anxiety disorder",
            "Generalized anxiety with sleep disturbance",
            "Anxiety symptoms, outpatient follow-up",
        ],
        "procedure_options": [
            "Medication management visit with counseling review",
            "Established patient mental health follow-up",
            "Office follow-up for anxiety symptom management",
            "Outpatient visit for anxiety medication review",
        ],
        "background_options": [
            "generalized anxiety managed with conservative treatment",
            "anxiety symptoms associated with stress and poor sleep",
            "outpatient anxiety follow-up with stable medication use",
            "ongoing anxiety symptoms monitored in primary care",
        ],
        "note_options": [
            "Patient presents for anxiety follow-up and medication review. Stress levels have improved slightly, and sleep habits were discussed during the visit.",
            "Patient is here for generalized anxiety follow-up with no acute safety concerns. Medication response and coping strategies were reviewed in clinic.",
            "Patient returns for outpatient anxiety management after several stressful weeks. Symptom check-in and medication follow-up were completed today.",
            "Patient presents for mood and anxiety follow-up. Sleep patterns, current stressors, and medication management were discussed during the visit.",
        ],
        "vital_options": [
            {"blood_pressure": "122/78 mmHg", "heart_rate": "84 bpm", "temperature": "98.2 F", "oxygen_saturation": "99%"},
            {"blood_pressure": "118/76 mmHg", "heart_rate": "82 bpm", "temperature": "98.1 F", "oxygen_saturation": "99%"},
            {"blood_pressure": "124/80 mmHg", "heart_rate": "86 bpm", "temperature": "98.3 F", "oxygen_saturation": "98%"},
            {"blood_pressure": "120/78 mmHg", "heart_rate": "80 bpm", "temperature": "98.0 F", "oxygen_saturation": "99%"},
        ],
    },
    {
        "primary_condition": "Knee Pain",
        "visit_type": "Established outpatient visit",
        "reason_options": [
            "Knee pain after exercise",
            "Follow-up for anterior knee discomfort",
            "Joint pain with stairs and walking",
            "Musculoskeletal knee evaluation",
        ],
        "diagnosis_options": [
            "Knee pain",
            "Patellofemoral pain syndrome",
            "Right knee pain",
            "Mechanical knee pain",
        ],
        "procedure_options": [
            "Office visit with focused knee exam",
            "Established patient musculoskeletal evaluation",
            "Problem-focused visit for joint pain",
            "Outpatient follow-up for knee pain management",
        ],
        "background_options": [
            "intermittent knee pain with activity",
            "mechanical knee discomfort worsened by stairs",
            "joint pain after increased exercise",
            "recurrent knee symptoms managed conservatively",
        ],
        "note_options": [
            "Patient reports knee pain after increased exercise and discomfort with stairs. No major trauma was reported, and a focused musculoskeletal exam was completed.",
            "Patient presents for follow-up of anterior knee pain that worsens with prolonged walking. Joint exam was completed and no acute injury was identified.",
            "Patient is here for knee pain review after activity-related flare. No swelling or trauma was reported, and supportive management was discussed.",
            "Patient returns for outpatient knee pain evaluation with discomfort during stairs and exercise. Musculoskeletal exam remained reassuring today.",
        ],
        "vital_options": [
            {"blood_pressure": "118/74 mmHg", "heart_rate": "72 bpm", "temperature": "98.1 F", "oxygen_saturation": "99%"},
            {"blood_pressure": "120/76 mmHg", "heart_rate": "74 bpm", "temperature": "98.2 F", "oxygen_saturation": "99%"},
            {"blood_pressure": "116/72 mmHg", "heart_rate": "70 bpm", "temperature": "98.0 F", "oxygen_saturation": "99%"},
            {"blood_pressure": "122/78 mmHg", "heart_rate": "76 bpm", "temperature": "98.3 F", "oxygen_saturation": "98%"},
        ],
    },
]


def build_synthetic_patient_cases(directory):
    patient_cases = []
    for index, patient_data in enumerate(directory):
        blueprint = CASE_BLUEPRINTS[index % len(CASE_BLUEPRINTS)]
        variant = (index // len(CASE_BLUEPRINTS)) % len(blueprint["note_options"])
        age = 22 + ((index * 3) % 17)
        reason = blueprint["reason_options"][variant]
        diagnosis = blueprint["diagnosis_options"][variant]
        procedure = blueprint["procedure_options"][variant]
        background = blueprint["background_options"][variant]
        note = blueprint["note_options"][variant]
        vitals = blueprint["vital_options"][variant]
        patient_cases.append(
            {
                "name": patient_data["name"],
                "patient_id": f"PT-{20001 + index}",
                "age": age,
                "gender": patient_data["gender"],
                "primary_condition": blueprint["primary_condition"],
                "visit_type": blueprint["visit_type"],
                "insurance": INSURANCE_OPTIONS[index % len(INSURANCE_OPTIONS)],
                "patient_bio": (
                    f"{patient_data['name']} is a {age}-year-old {patient_data['gender']} patient with "
                    f"{background}. The patient is visiting today for {reason.lower()}."
                ),
                "vitals": vitals,
                "clinical_note": note,
                "default_visit_reason": reason,
                "default_diagnosis": diagnosis,
                "default_procedure": procedure,
                "status": "Not Complete",
            }
        )
    return patient_cases


PATIENTS = build_synthetic_patient_cases(PATIENT_DIRECTORY)


def validate_patient_cases(patient_cases):
    issues = []
    required_fields = [
        "name",
        "patient_id",
        "age",
        "gender",
        "primary_condition",
        "visit_type",
        "patient_bio",
        "vitals",
        "clinical_note",
        "default_visit_reason",
        "default_diagnosis",
        "default_procedure",
        "status",
    ]

    condition_rules = {
        "Hypertension": ["blood pressure", "hypertension", "medication management", "follow-up"],
        "Sore Throat/URI": ["sore throat", "congestion", "cough", "fever", "strep", "respiratory"],
        "GERD": ["reflux", "heartburn", "abdominal discomfort", "gerd"],
        "Low Back Pain": ["back pain", "sitting", "musculoskeletal exam", "no trauma"],
        "Type 2 Diabetes": ["diabetes", "glucose", "blood sugar", "medication review"],
        "Hyperlipidemia": ["cholesterol", "lipid", "statin", "labs"],
        "Allergic Rhinitis": ["allerg", "congestion", "itchy eyes", "sneezing"],
        "Migraine": ["migraine", "headache", "trigger", "medication"],
        "Dermatitis/Eczema": ["rash", "eczema", "dermatitis", "skin"],
        "Preventive Visit": ["preventive", "wellness", "screening", "health maintenance"],
        "Asthma Follow-up": ["asthma", "inhaler", "wheezing", "respiratory"],
        "Anxiety Follow-up": ["anxiety", "stress", "sleep", "medication"],
        "Knee Pain": ["knee pain", "stairs", "joint", "musculoskeletal"],
    }

    for patient in patient_cases:
        missing_fields = [field for field in required_fields if field not in patient]
        if missing_fields:
            issues.append(f"{patient.get('name', 'Unknown patient')} is missing fields: {', '.join(missing_fields)}.")
            continue

        note_text = patient["clinical_note"].lower()
        primary_condition = patient["primary_condition"]
        if primary_condition in condition_rules:
            keywords = condition_rules[primary_condition]
            if not any(keyword in note_text for keyword in keywords):
                issues.append(
                    f"{patient['name']} has primary condition '{primary_condition}' but the clinical note does not match it."
                )

    return issues

def get_patient_initials(name):
    parts = name.split()
    return "".join(part[0] for part in parts[:2]).upper()


def get_image_data_uri(image_path):
    extension = os.path.splitext(image_path)[1].lower()
    mime_type = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
    }.get(extension, "application/octet-stream")
    with open(image_path, "rb") as image_file:
        encoded = base64.b64encode(image_file.read()).decode("utf-8")
    return f"data:{mime_type};base64,{encoded}"


def tokenize_text(text):
    base_tokens = [
        token
        for token in TOKEN_PATTERN.findall(str(text).lower())
        if len(token) > 2 and token not in STOPWORDS
    ]
    expanded_tokens = set(base_tokens)
    for token in base_tokens:
        expanded_tokens.update(TOKEN_EXPANSIONS.get(token, set()))
    return sorted(expanded_tokens)


@st.cache_data(show_spinner=False)
def load_billing_codes():
    df = pd.read_csv(
        BILLING_CODES_PATH,
        header=None,
        names=[
            "category_code",
            "subcategory",
            "icd10_code",
            "short_description",
            "long_description",
            "category_description",
        ],
        dtype=str,
    ).fillna("")
    df["description"] = df["long_description"].where(
        df["long_description"].str.strip() != "",
        df["short_description"],
    )
    df["search_text"] = (
        df["icd10_code"].str.lower()
        + " "
        + df["description"].str.lower()
        + " "
        + df["short_description"].str.lower()
        + " "
        + df["category_description"].str.lower()
    ).str.replace(r"\s+", " ", regex=True).str.strip()
    df["search_terms"] = df["search_text"].apply(lambda text: frozenset(tokenize_text(text)))
    return df


def analyze_billing_inputs(visit_reason, diagnosis, procedure, clinical_notes):
    weighted_sources = [
        ("visit reason", visit_reason, 3),
        ("diagnosis", diagnosis, 5),
        ("procedure", procedure, 2),
        ("clinical notes", clinical_notes, 2),
    ]

    term_weights = {}
    term_sources = {}
    for source_name, text, weight in weighted_sources:
        for term in tokenize_text(text):
            term_weights[term] = term_weights.get(term, 0) + weight
            term_sources.setdefault(term, set()).add(source_name)

    return {
        "term_weights": term_weights,
        "term_sources": term_sources,
        "diagnosis_text": str(diagnosis).lower().strip(),
        "source_tokens": {
            "visit reason": set(tokenize_text(visit_reason)),
            "diagnosis": set(tokenize_text(diagnosis)),
            "procedure": set(tokenize_text(procedure)),
            "clinical notes": set(tokenize_text(clinical_notes)),
        },
        "query_text": " ".join(
            value.strip().lower()
            for value in [visit_reason, diagnosis, procedure, clinical_notes]
            if str(value).strip()
        ),
    }


def build_patient_records(patient_cases):
    records = []
    for patient in patient_cases:
        record = copy.deepcopy(patient)
        record["id"] = patient["patient_id"]
        record["condition"] = patient["primary_condition"]
        record["avatar"] = get_patient_initials(patient["name"])
        records.append(record)
    return records


def find_patient_record(patient_value):
    if isinstance(patient_value, dict):
        patient_id = patient_value.get("id")
        for patient in st.session_state["patient_records"]:
            if patient["id"] == patient_id:
                return patient
        return patient_value

    for patient in st.session_state["patient_records"]:
        if patient["name"] == patient_value or patient["id"] == patient_value:
            return patient
    return None


def update_patient_status(patient_id, status):
    for patient in st.session_state["patient_records"]:
        if patient["id"] == patient_id:
            patient["status"] = status
            break


def generate_billing_code_suggestions(visit_reason, diagnosis, procedure, clinical_notes):
    billing_codes = load_billing_codes()
    analysis = analyze_billing_inputs(visit_reason, diagnosis, procedure, clinical_notes)
    term_weights = analysis["term_weights"]
    diagnosis_text = analysis["diagnosis_text"]
    query_text = analysis["query_text"]
    source_tokens = analysis["source_tokens"]

    if not term_weights:
        raise ValueError("Enter more clinical detail to search the billing code dataset.")

    context_terms = {
        "preventive", "wellness", "screening", "follow", "followup", "follow-up",
        "history", "medication", "review", "exam", "encounter",
    }
    query_context_tokens = context_terms & set(tokenize_text(query_text))
    complication_terms = {"complication", "device", "implant", "postoperative", "postop", "surgery", "surgical"}
    query_complication_tokens = complication_terms & set(tokenize_text(query_text))

    def get_family_key(row):
        family_text = row.category_description or row.description or row.short_description
        family_tokens = [
            token for token in tokenize_text(family_text)
            if token not in {"unspecified", "without", "with", "other"}
        ]
        family_label = " ".join(family_tokens[:3]) if family_tokens else str(row.icd10_code)[:3].lower()
        code_stem = re.sub(r"[^a-z0-9]", "", str(row.icd10_code).lower())[:3]
        return code_stem, family_label

    def is_distinct_candidate(candidate, chosen_rows):
        candidate_stem, candidate_family = get_family_key(candidate)
        candidate_terms = set(tokenize_text(candidate.description))

        for chosen in chosen_rows:
            chosen_stem, chosen_family = get_family_key(chosen)
            chosen_terms = set(tokenize_text(chosen.description))

            overlap_ratio = 0.0
            if candidate_terms and chosen_terms:
                overlap_ratio = len(candidate_terms & chosen_terms) / max(len(candidate_terms), len(chosen_terms))

            if candidate_stem == chosen_stem and candidate_family == chosen_family:
                return False
            if candidate_family == chosen_family and overlap_ratio >= 0.6:
                return False

        return True

    scored_rows = []
    for row in billing_codes.itertuples(index=False):
        diagnosis_matches = source_tokens["diagnosis"] & row.search_terms
        reason_matches = source_tokens["visit reason"] & row.search_terms
        procedure_matches = source_tokens["procedure"] & row.search_terms
        note_matches = source_tokens["clinical notes"] & row.search_terms
        context_matches = context_terms & row.search_terms
        clinical_match_count = len(diagnosis_matches | reason_matches | note_matches)
        complication_matches = complication_terms & row.search_terms

        if str(row.icd10_code).upper().startswith("Z") and not (query_context_tokens and context_matches):
            continue
        if clinical_match_count == 0 and not (query_context_tokens and context_matches):
            continue
        if complication_matches and not query_complication_tokens:
            continue

        score = (
            len(diagnosis_matches) * 7
            + len(reason_matches) * 4
            + len(procedure_matches) * 3
            + len(note_matches) * 2
        )

        if diagnosis_text and diagnosis_text in row.search_text:
            score += 10

        if row.category_description and row.category_description.lower() in query_text:
            score += 4

        if context_matches and any(term in query_text for term in context_terms):
            score += 3

        matched_terms = list(diagnosis_matches | reason_matches | procedure_matches | note_matches)

        if diagnosis_matches:
            bucket = "primary"
        elif str(row.icd10_code).upper().startswith("Z") or context_matches:
            bucket = "context"
        else:
            bucket = "supporting"

        if score > 0:
            scored_rows.append((score, len(diagnosis_matches), len(matched_terms), bucket, row, matched_terms))

    if not scored_rows:
        raise ValueError("No relevant billing codes were found in the local dataset for these inputs.")

    scored_rows.sort(
        key=lambda item: (
            item[0],
            item[1],
            item[2],
            len(item[4].description),
        ),
        reverse=True,
    )

    suggestions = []
    seen_codes = set()
    chosen_rows = []
    primary_code_prefix = None

    def append_suggestion(row, matched_terms):
        top_terms = matched_terms[:3]
        source_labels = sorted(
            {source for term in top_terms for source in analysis["term_sources"].get(term, set())}
        )

        if top_terms and source_labels:
            explanation = (
                f"Selected because it matches {', '.join(top_terms)} from "
                f"{', '.join(source_labels)}."
            )
        elif top_terms:
            explanation = f"Selected because it matches {', '.join(top_terms)} in the patient details."
        else:
            explanation = "Selected because its description closely matches the patient details."

        suggestions.append(
            {
                "code": row.icd10_code,
                "description": row.description,
                "explanation": explanation,
            }
        )

    for preferred_bucket in ["primary", "supporting", "context"]:
        for _, diagnosis_match_count, _, bucket, row, matched_terms in scored_rows:
            if bucket != preferred_bucket or row.icd10_code in seen_codes:
                continue
            code_prefix = str(row.icd10_code).upper()[:1]
            if preferred_bucket != "primary" and primary_code_prefix:
                if code_prefix not in {primary_code_prefix, "R", "Z"}:
                    continue
            if preferred_bucket != "primary" and len(matched_terms) < 2:
                if not (diagnosis_text and diagnosis_text in row.search_text) and diagnosis_match_count == 0:
                    continue
            if not is_distinct_candidate(row, chosen_rows):
                continue

            seen_codes.add(row.icd10_code)
            chosen_rows.append(row)
            if preferred_bucket == "primary" and not primary_code_prefix:
                primary_code_prefix = code_prefix
            append_suggestion(row, matched_terms)
            break

    if len(suggestions) < 3:
        for _, diagnosis_match_count, _, _, row, matched_terms in scored_rows:
            if row.icd10_code in seen_codes:
                continue
            code_prefix = str(row.icd10_code).upper()[:1]
            if primary_code_prefix and code_prefix not in {primary_code_prefix, "R", "Z"}:
                continue
            if len(matched_terms) < 2:
                if not (diagnosis_text and diagnosis_text in row.search_text) and diagnosis_match_count == 0:
                    continue
            if not is_distinct_candidate(row, chosen_rows):
                continue

            seen_codes.add(row.icd10_code)
            chosen_rows.append(row)
            append_suggestion(row, matched_terms)

            if len(suggestions) == 3:
                break

    return suggestions


def get_patient_profile(patient):
    return patient


def build_result_card_data(suggestion):
    return {
        "code": suggestion["code"],
        "description": suggestion["description"],
        "reason": suggestion["explanation"],
    }


def get_vital_indicator(label, value):
    if label == "Blood Pressure":
        systolic = int(value.split("/")[0])
        return "normal" if systolic < 120 else "borderline"
    if label == "Heart Rate":
        rate = int(value.split()[0])
        return "normal" if 60 <= rate <= 100 else "borderline"
    if label == "Temperature":
        temp = float(value.split()[0])
        return "normal" if temp < 99.5 else "borderline"
    if label == "Oxygen Saturation":
        oxygen = int(value.replace("%", ""))
        return "normal" if oxygen >= 97 else "borderline"
    return "normal"


def unique_preserve(values):
    seen = set()
    ordered = []
    for value in values:
        cleaned = str(value).strip()
        if not cleaned or cleaned in seen:
            continue
        seen.add(cleaned)
        ordered.append(cleaned)
    return ordered


def get_patient_field_suggestions(patient_records, current_patient, field_name, limit=8):
    current_value = current_patient[field_name]
    same_condition_values = [
        patient[field_name]
        for patient in patient_records
        if patient["patient_id"] != current_patient["patient_id"]
        and patient["primary_condition"] == current_patient["primary_condition"]
    ]
    all_values = [
        patient[field_name]
        for patient in patient_records
        if patient["patient_id"] != current_patient["patient_id"]
    ]
    return unique_preserve([current_value] + same_condition_values + all_values)[:limit]


def render_guided_field(label, icon, current_patient, field_name, choice_key, custom_key):
    suggestions = get_patient_field_suggestions(st.session_state["patient_records"], current_patient, field_name)
    options = suggestions + ["Custom entry..."]
    selected_option = st.selectbox(f"{icon} {label}", options, key=choice_key)

    if selected_option == "Custom entry...":
        return st.text_input(
            f"Custom {label}",
            key=custom_key,
            placeholder=current_patient[field_name],
        )

    return selected_option


def render_dashboard_sidebar(current_page):
    nav_items = [
        ("🏠", "Dashboard"),
        ("👥", "Patients"),
        ("💳", "Billing Assistant"),
        ("⚙️", "Settings"),
    ]
    sidebar_logo_uri = get_image_data_uri("project-logo.png")

    with st.sidebar:
        st.markdown(
            f"""
            <div class="sidebar-brand">
                <img src="{sidebar_logo_uri}" alt="Ai10 logo" class="sidebar-brand-logo">
                <div class="sidebar-brand-title">Ai10 Clinical Workspace</div>
                <div class="sidebar-brand-subtitle">Clinical billing review platform</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        for icon, label in nav_items:
            button_type = "primary" if label == current_page else "secondary"
            if st.button(
                f"{icon}  {label}",
                key=f"nav_{label}",
                use_container_width=True,
                type=button_type,
            ):
                st.session_state["page"] = label
                st.rerun()


def render_dashboard_home():
    render_dashboard_sidebar("Dashboard")
    doctor_image_uri = get_image_data_uri("doctor-image1.png")

    total_patients = len(st.session_state["patient_records"])
    total_reviews = len(st.session_state["generated_reviews"])
    pending_reviews = len(
        [patient for patient in st.session_state["patient_records"] if patient["status"] == "Not Complete"]
    )

    st.markdown(
        f"""
        <div class="welcome-banner">
            <div class="welcome-media">
                <img src="{doctor_image_uri}" alt="Doctor" class="welcome-image">
            </div>
            <div class="welcome-copy">
                <div class="welcome-kicker">Provider Command Center</div>
                <div class="welcome-name">Welcome, Dr. {st.session_state['doctor_name']}</div>
                <div class="welcome-subtitle">{pending_reviews} active patient charts awaiting review.</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    stats_cols = st.columns(3, gap="large")
    stat_cards = [
        ("👥", "Total Patients", str(total_patients), "patient-stat"),
        ("📋", "Total Billing Reviews", str(total_reviews), "review-stat"),
        ("⏳", "Pending Reviews", str(pending_reviews), "pending-stat"),
    ]

    for column, (icon, label, value, css_class) in zip(stats_cols, stat_cards):
        with column:
            st.markdown(
                f"""
                <div class="dashboard-stat-card {css_class}">
                    <div class="dashboard-stat-icon">{icon}</div>
                    <div class="dashboard-stat-label">{label}</div>
                    <div class="dashboard-stat-value">{value}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_settings_page():
    render_dashboard_sidebar("Settings")

    st.markdown(
        """
        <div class="header-card page-header-card">
            <div class="header-icon">⚙️</div>
            <div>
                <div class="app-title">Settings</div>
                <div class="header-subtitle">Current demo environment configuration.</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    setting_cols = st.columns(3, gap="large")
    settings = [
        ("Demo Mode", "On"),
        ("Data Type", "Synthetic"),
        ("Human Review Required", "Yes"),
    ]

    for column, (label, value) in zip(setting_cols, settings):
        with column:
            st.markdown(
                f"""
                <div class="ehr-card settings-card">
                    <div class="card-label">{label}</div>
                    <div class="settings-value">{value}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_billing_assistant_gate():
    render_dashboard_sidebar("Billing Assistant")

    st.markdown(
        """
        <div class="header-card page-header-card">
            <div class="header-icon">💳</div>
            <div>
                <div class="app-title">Billing Code Assistant</div>
                <div class="header-subtitle">Select a patient before opening the billing workspace.</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.warning("Please select a patient first.")
    if st.button("Go to Patients", use_container_width=False, type="primary"):
        st.session_state["page"] = "Patients"
        st.rerun()


def render_login_screen():
    left, right = st.columns([1.05, 0.95], gap="large")
    logo_uri = get_image_data_uri("project-logo.png")

    with left:
        st.markdown(
            f"""
            <div class="auth-visual-panel auth-fade-in">
                <div class="auth-blob auth-blob-one"></div>
                <div class="auth-blob auth-blob-two"></div>
                <div class="auth-panel-content">
                    <div class="auth-logo-wrap">
                        <img src="{logo_uri}" alt="Ai10 logo" class="auth-logo-large">
                    </div>
                    <div class="auth-panel-title">Clinical Billing Review Platform</div>
                    <div class="auth-panel-subtitle">
                        Review patient charts, retrieve ICD-10 references, and complete billing workflows.
                    </div>
                    <div class="feature-chip-row">
                        <span class="feature-chip">Patient Charts</span>
                        <span class="feature-chip">ICD-10 Dataset</span>
                        <span class="feature-chip">Human Review</span>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with right:
        st.markdown(
            """
            <div class="entry-card login-card glass-card auth-fade-in auth-form-card">
                <div class="login-eyebrow">Secure Provider Access</div>
                <div class="entry-title">Sign in to continue</div>
                <div class="entry-subtitle">Access the provider workspace and continue clinical billing review.</div>
            """,
            unsafe_allow_html=True,
        )

        with st.form("login_form", clear_on_submit=False):
            full_name = st.text_input("Full Name", key="login_full_name", placeholder="Enter your full name")
            password = st.text_input(
                "Password",
                type="password",
                key="login_password",
                placeholder="Enter shared password",
            )
            login_clicked = st.form_submit_button("Login", use_container_width=True, type="primary")
        st.markdown("</div>", unsafe_allow_html=True)

        if login_clicked:
            if password != SHARED_PASSWORD:
                st.error("Incorrect password. Please try again.")
            elif not full_name.strip():
                st.error("Please enter your full name.")
            else:
                st.session_state["logged_in"] = True
                st.session_state["doctor_name"] = full_name.strip()
                st.session_state["welcome_seen"] = False
                st.session_state["selected_patient"] = ""
                st.session_state["page"] = "Dashboard"
                st.rerun()


def render_welcome_screen():
    doctor_image_uri = get_image_data_uri("doctor-image1.png")
    logo_uri = get_image_data_uri("project-logo.png")

    st.markdown(
        f"""
        <div class="welcome-hero glass-card auth-fade-in">
            <div class="auth-blob auth-blob-one"></div>
            <div class="auth-blob auth-blob-two"></div>
            <div class="welcome-hero-copy">
                <div class="welcome-hero-top">
                    <img src="{logo_uri}" alt="Ai10 logo" class="welcome-hero-logo">
                    <div class="login-eyebrow">Workspace Ready</div>
                </div>
                <div class="entry-title">Welcome back, Dr. {st.session_state['doctor_name']}</div>
                <div class="entry-subtitle">Your provider workspace is ready.</div>
                <div class="feature-chip-row status-chip-row">
                    <span class="feature-chip feature-chip-light">52 Patients</span>
                    <span class="feature-chip feature-chip-light">ICD-10 Dataset Ready</span>
                    <span class="feature-chip feature-chip-light">Human Review Required</span>
                </div>
                <div class="loading-line">
                    <span class="loading-dot"></span>
                    <span>Loading provider workspace...</span>
                </div>
            </div>
            <div class="welcome-hero-media">
                <img src="{doctor_image_uri}" alt="Provider" class="welcome-hero-image">
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("Continue", use_container_width=True, type="primary"):
        st.session_state["welcome_seen"] = True
        st.session_state["page"] = "Dashboard"
        st.rerun()


def render_patient_selection():
    render_dashboard_sidebar("Patients")

    st.markdown(
        """
        <div class="header-card page-header-card">
            <div class="header-icon">🏥</div>
            <div>
                <div class="app-title">Patient Directory</div>
                <div class="header-subtitle">Select a patient to review and generate billing codes.</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="warning-note">Synthetic demo data only. Codes require human review.</div>',
        unsafe_allow_html=True,
    )

    filter_cols = st.columns(3, gap="small")
    filters = ["All", "Not Complete", "Complete"]
    for column, filter_name in zip(filter_cols, filters):
        with column:
            button_type = "primary" if st.session_state["patient_filter"] == filter_name else "secondary"
            if st.button(
                filter_name,
                key=f"filter_{filter_name}",
                use_container_width=True,
                type=button_type,
            ):
                st.session_state["patient_filter"] = filter_name
                st.rerun()

    if st.session_state["patient_filter"] == "All":
        filtered_patients = st.session_state["patient_records"]
    else:
        filtered_patients = [
            patient
            for patient in st.session_state["patient_records"]
            if patient["status"] == st.session_state["patient_filter"]
        ]

    if not filtered_patients:
        st.info("No patients match the selected filter.")
        return

    for row_start in range(0, len(filtered_patients), 4):
        row_patients = filtered_patients[row_start : row_start + 4]
        row_columns = st.columns(4, gap="large")

        for column, patient in zip(row_columns, row_patients):
            with column:
                status_class = patient["status"].lower().replace(" ", "-")
                st.markdown(
                    f"""
                    <div class="directory-card">
                        <div class="directory-card-top">
                            <div class="directory-avatar">{patient["avatar"]}</div>
                            <div class="directory-status status-{status_class}">{patient["status"]}</div>
                        </div>
                        <div class="directory-name">{patient["name"]}</div>
                        <div class="directory-id">{patient["patient_id"]}</div>
                        <div class="directory-condition">{patient["primary_condition"]}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if st.button(
                    "Open Chart",
                    key=f"open_chart_{patient['id']}",
                    use_container_width=True,
                    type="primary",
                ):
                    st.session_state["selected_patient"] = patient["id"]
                    st.session_state["page"] = "Billing Assistant"
                    st.rerun()


def render_main_app():
    selected_patient = find_patient_record(st.session_state["selected_patient"])
    if not selected_patient:
        st.session_state["selected_patient"] = ""
        st.session_state["page"] = "Patients"
        st.rerun()

    patient_name = selected_patient["name"]
    profile = get_patient_profile(selected_patient)
    status_class = selected_patient["status"].lower().replace(" ", "-")
    saved_suggestions = st.session_state["generated_reviews"].get(selected_patient["id"], [])

    render_dashboard_sidebar("Billing Assistant")

    if st.button("← Back to Patient Directory", use_container_width=False):
        st.session_state["selected_patient"] = ""
        st.session_state["visit_reason"] = ""
        st.session_state["diagnosis"] = ""
        st.session_state["procedure"] = ""
        st.session_state["page"] = "Patients"
        st.rerun()

    st.markdown(
        f"""
        <div class="welcome-banner compact-welcome">
            <div class="welcome-kicker">Active Chart</div>
            <div class="welcome-name">Active Patient Chart</div>
            <div class="welcome-subtitle">Review patient information, vitals, and complete billing code recommendations.</div>
            <div class="welcome-context">Currently viewing: {patient_name}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="ehr-shell">
            <div class="patient-header-card">
                <div class="patient-header-main">
                    <div class="patient-avatar">🧑‍⚕️</div>
                    <div class="patient-header-copy">
                        <div class="patient-header-name">{patient_name}</div>
                        <div class="patient-header-subtitle">Synthetic outpatient chart</div>
                        <div class="patient-header-tags">
                            <span class="status-badge status-{status_class}">{selected_patient["status"]}</span>
                            <span class="visit-type-tag">{profile["visit_type"]}</span>
                        </div>
                    </div>
                </div>
                <div class="patient-header-grid">
                    <div class="header-metric"><span>Age</span><strong>{profile["age"]}</strong></div>
                    <div class="header-metric"><span>Gender</span><strong>{profile["gender"]}</strong></div>
                    <div class="header-metric"><span>Patient ID</span><strong>{profile["patient_id"]}</strong></div>
                    <div class="header-metric"><span>Insurance</span><strong>{profile["insurance"]}</strong></div>
                    <div class="header-metric"><span>Primary Condition</span><strong>{profile["primary_condition"]}</strong></div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    left_col, right_col = st.columns([1.05, 1], gap="large")

    with left_col:
        st.markdown('<div class="section-title">👤 Patient Overview</div>', unsafe_allow_html=True)
        st.markdown(
            f"""
            <div class="ehr-card overview-card">
                <div class="card-label">Patient Bio</div>
                <div class="notes-line">{profile["patient_bio"]}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown('<div class="section-title">❤️ Vitals</div>', unsafe_allow_html=True)
        vitals_cols = st.columns(4, gap="small")
        vital_items = [
            ("Blood Pressure", profile["vitals"]["blood_pressure"]),
            ("Heart Rate", profile["vitals"]["heart_rate"]),
            ("Temperature", profile["vitals"]["temperature"]),
            ("Oxygen Saturation", profile["vitals"]["oxygen_saturation"]),
        ]
        for column, (label, value) in zip(vitals_cols, vital_items):
            indicator = get_vital_indicator(label, value)
            with column:
                st.markdown(
                    f"""
                    <div class="vital-card vital-{indicator}">
                        <div class="vital-label">{label}</div>
                        <div class="vital-value">{value}</div>
                        <div class="vital-indicator">
                            <span class="indicator-dot indicator-{indicator}"></span>
                            <span>{indicator.title()}</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        st.markdown('<div class="section-title">📝 Visit Notes</div>', unsafe_allow_html=True)
        st.markdown(
            f"""
            <div class="ehr-card notes-accent-card">
                <div class="card-label">Clinical Note</div>
                <div class="notes-line">{profile["clinical_note"]}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with right_col:
        st.markdown(
            """
            <div class="ehr-card billing-card accent-billing ai-billing-shell">
                <div class="ai-billing-header">
                    <div class="ai-billing-icon">🤖</div>
                    <div>
                        <div class="ai-billing-title">AI Billing Code Assistant 🤖</div>
                        <div class="ai-billing-subtitle">Enter visit details to generate billing code suggestions</div>
                    </div>
                </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button("Use Patient Defaults", key=f"use_defaults_{selected_patient['id']}", use_container_width=True):
            st.session_state[f"visit_reason_choice_{selected_patient['id']}"] = profile["default_visit_reason"]
            st.session_state[f"diagnosis_choice_{selected_patient['id']}"] = profile["default_diagnosis"]
            st.session_state[f"procedure_choice_{selected_patient['id']}"] = profile["default_procedure"]
            st.rerun()

        visit_reason = render_guided_field(
            "Visit Reason",
            "🩺",
            profile,
            "default_visit_reason",
            f"visit_reason_choice_{selected_patient['id']}",
            f"visit_reason_custom_{selected_patient['id']}",
        )
        st.markdown('<div class="field-gap"></div>', unsafe_allow_html=True)
        diagnosis = render_guided_field(
            "Diagnosis",
            "🧾",
            profile,
            "default_diagnosis",
            f"diagnosis_choice_{selected_patient['id']}",
            f"diagnosis_custom_{selected_patient['id']}",
        )
        st.markdown('<div class="field-gap"></div>', unsafe_allow_html=True)
        procedure = render_guided_field(
            "Procedure",
            "⚙️",
            profile,
            "default_procedure",
            f"procedure_choice_{selected_patient['id']}",
            f"procedure_custom_{selected_patient['id']}",
        )

        st.markdown('<div class="spacer-sm"></div>', unsafe_allow_html=True)
        generate_clicked = st.button(
            "⚡ Generate Billing Code Suggestions",
            use_container_width=True,
            type="primary",
        )
        st.markdown("</div>", unsafe_allow_html=True)

        if generate_clicked:
            if not visit_reason.strip() or not diagnosis.strip() or not procedure.strip():
                st.warning("Please fill in all fields before generating suggestions.")
            else:
                try:
                    with st.spinner("Analyzing patient data and generating codes..."):
                        suggestions = generate_billing_code_suggestions(
                            visit_reason,
                            diagnosis,
                            procedure,
                            profile["clinical_note"],
                        )

                    st.session_state["generated_reviews"][selected_patient["id"]] = copy.deepcopy(suggestions)
                    update_patient_status(selected_patient["id"], "Complete")
                    selected_patient = find_patient_record(selected_patient["id"])
                    saved_suggestions = st.session_state["generated_reviews"][selected_patient["id"]]
                    st.success(f"Billing review completed for {selected_patient['name']}.")
                except Exception as error:
                    st.error(f"Unable to generate suggestions: {error}")

        if saved_suggestions:
            st.markdown(
                '<div class="results-heading">Top 3 Suggested Billing Codes</div>',
                unsafe_allow_html=True,
            )
            for suggestion in saved_suggestions:
                result = build_result_card_data(suggestion)
                st.markdown(
                    f"""
                    <div class="result-card">
                        <div class="result-top-row">
                            <div class="result-code">{result["code"]}</div>
                        </div>
                        <div class="result-description">{result["description"]}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    st.markdown(
        '<div class="footer-note">Synthetic demo data only. Codes require human review.</div>',
        unsafe_allow_html=True,
    )


st.set_page_config(
    page_title="AI Billing Code Assistant",
    page_icon="🩺",
    layout="wide",
)

st.markdown(
    """
    <style>
    @keyframes fadeUp {
        from {
            opacity: 0;
            transform: translateY(18px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    @keyframes softFloat {
        0% {
            transform: translateY(0);
        }
        50% {
            transform: translateY(-4px);
        }
        100% {
            transform: translateY(0);
        }
    }
    @keyframes pulseGlow {
        0% {
            box-shadow: 0 0 0 0 rgba(67, 130, 204, 0.22);
            opacity: 0.8;
        }
        70% {
            box-shadow: 0 0 0 10px rgba(67, 130, 204, 0);
            opacity: 1;
        }
        100% {
            box-shadow: 0 0 0 0 rgba(67, 130, 204, 0);
            opacity: 0.8;
        }
    }
    .stApp {
        background:
            radial-gradient(circle at top right, rgba(139, 202, 224, 0.26) 0%, transparent 26%),
            radial-gradient(circle at top left, rgba(208, 235, 247, 0.58) 0%, transparent 32%),
            radial-gradient(circle at bottom left, rgba(175, 217, 199, 0.18) 0%, transparent 26%),
            linear-gradient(180deg, #f5fbff 0%, #eef5fb 52%, #edf3f8 100%);
        color: #1f2d3d;
    }
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #18324a 0%, #10283d 100%);
        border-right: 1px solid rgba(205, 223, 238, 0.12);
    }
    section[data-testid="stSidebar"] > div {
        background: transparent;
    }
    div[data-testid="stSidebarUserContent"] {
        padding-top: 1.2rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }
    .sidebar-brand {
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
        margin-bottom: 1.5rem;
        padding-bottom: 1rem;
        border-bottom: 1px solid rgba(205, 223, 238, 0.14);
    }
    .sidebar-brand-logo {
        width: 90px;
        height: auto;
        display: block;
        margin-bottom: 0.7rem;
    }
    .sidebar-brand-title {
        color: #f4f8fb;
        font-size: 1rem;
        font-weight: 700;
    }
    .sidebar-brand-subtitle {
        color: #9eb4c7;
        font-size: 0.84rem;
        margin-top: 0.15rem;
    }
    .entry-card {
        background: rgba(255, 255, 255, 0.74);
        border: 1px solid rgba(219, 230, 241, 0.85);
        border-radius: 28px;
        box-shadow: 0 24px 54px rgba(27, 62, 96, 0.11);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        padding: 38px 40px;
        text-align: center;
        margin-bottom: 1rem;
    }
    .glass-card {
        position: relative;
        overflow: hidden;
    }
    .glass-card::before {
        content: "";
        position: absolute;
        inset: 0;
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.24) 0%, rgba(255, 255, 255, 0.06) 100%);
        pointer-events: none;
    }
    .auth-fade-in {
        animation: fadeUp 0.72s ease both;
    }
    .login-card {
        margin-top: 3.4rem;
    }
    .login-logo-wrap {
        display: flex;
        justify-content: center;
        margin-bottom: 1.2rem;
    }
    .login-logo {
        width: 150px;
        height: auto;
        display: block;
    }
    .login-eyebrow {
        color: #5f7fa0;
        font-size: 0.76rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        margin-bottom: 0.8rem;
        position: relative;
        z-index: 1;
    }
    .welcome-card {
        margin-top: 5.2rem;
        max-width: 640px;
        margin-left: auto;
        margin-right: auto;
    }
    .auth-visual-panel {
        min-height: 620px;
        border-radius: 30px;
        position: relative;
        overflow: hidden;
        background:
            radial-gradient(circle at top left, rgba(127, 193, 219, 0.28) 0%, transparent 28%),
            linear-gradient(160deg, rgba(16, 46, 72, 0.95) 0%, rgba(24, 73, 112, 0.92) 46%, rgba(36, 112, 146, 0.86) 100%);
        border: 1px solid rgba(180, 215, 233, 0.22);
        box-shadow: 0 30px 60px rgba(19, 47, 74, 0.18);
        padding: 42px;
    }
    .auth-panel-content {
        position: relative;
        z-index: 1;
        display: flex;
        flex-direction: column;
        justify-content: center;
        height: 100%;
        max-width: 460px;
    }
    .auth-logo-wrap {
        margin-bottom: 1.6rem;
    }
    .auth-logo-large {
        width: 150px;
        height: auto;
        display: block;
    }
    .auth-panel-title {
        color: #f8fcff;
        font-size: 2.35rem;
        font-weight: 800;
        line-height: 1.1;
        letter-spacing: -0.03em;
        margin-bottom: 1rem;
    }
    .auth-panel-subtitle {
        color: rgba(230, 241, 248, 0.88);
        font-size: 1.04rem;
        line-height: 1.7;
        max-width: 420px;
        margin-bottom: 1.5rem;
    }
    .feature-chip-row {
        display: flex;
        flex-wrap: wrap;
        gap: 0.7rem;
    }
    .feature-chip {
        display: inline-flex;
        align-items: center;
        padding: 0.52rem 0.95rem;
        border-radius: 999px;
        background: rgba(255, 255, 255, 0.12);
        border: 1px solid rgba(203, 225, 237, 0.16);
        color: #f3fbff;
        font-size: 0.88rem;
        font-weight: 700;
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
    }
    .feature-chip-light {
        background: rgba(255, 255, 255, 0.72);
        border-color: rgba(206, 224, 238, 0.86);
        color: #29506d;
    }
    .auth-form-card {
        max-width: 560px;
        margin-left: auto;
        margin-right: auto;
        padding: 44px 42px;
        box-shadow: 0 28px 60px rgba(29, 68, 102, 0.12);
    }
    .auth-blob {
        position: absolute;
        border-radius: 999px;
        filter: blur(2px);
        pointer-events: none;
    }
    .auth-blob-one {
        width: 230px;
        height: 230px;
        top: -70px;
        right: -60px;
        background: radial-gradient(circle, rgba(141, 223, 229, 0.24) 0%, rgba(141, 223, 229, 0) 70%);
    }
    .auth-blob-two {
        width: 190px;
        height: 190px;
        bottom: -50px;
        left: -40px;
        background: radial-gradient(circle, rgba(157, 191, 255, 0.18) 0%, rgba(157, 191, 255, 0) 72%);
    }
    .entry-icon {
        font-size: 2.4rem;
        margin-bottom: 0.7rem;
    }
    .entry-title {
        font-size: 2.3rem;
        font-weight: 800;
        color: #17364c;
        line-height: 1.14;
        letter-spacing: -0.03em;
        margin-bottom: 0.55rem;
        position: relative;
        z-index: 1;
    }
    .entry-subtitle {
        color: #698196;
        font-size: 1.02rem;
        line-height: 1.65;
        max-width: 460px;
        margin: 0 auto;
        position: relative;
        z-index: 1;
    }
    .welcome-logo-orbit {
        display: flex;
        justify-content: center;
        margin-bottom: 1.2rem;
        position: relative;
        z-index: 1;
        animation: softFloat 4.6s ease-in-out infinite;
    }
    .welcome-logo {
        width: 114px;
        height: auto;
        display: block;
        filter: drop-shadow(0 10px 24px rgba(64, 112, 164, 0.10));
    }
    .loading-line {
        margin-top: 1.15rem;
        display: inline-flex;
        align-items: center;
        gap: 0.65rem;
        color: #5e7a94;
        font-size: 0.95rem;
        font-weight: 600;
        position: relative;
        z-index: 1;
    }
    .loading-dot {
        width: 10px;
        height: 10px;
        border-radius: 999px;
        background: linear-gradient(180deg, #57a1db 0%, #2d78b7 100%);
        animation: pulseGlow 1.8s ease-in-out infinite;
    }
    .welcome-hero {
        margin-top: 3.2rem;
        padding: 34px 36px;
        border-radius: 30px;
        display: flex;
        align-items: stretch;
        gap: 28px;
        position: relative;
        overflow: hidden;
    }
    .welcome-hero-copy,
    .welcome-hero-media {
        position: relative;
        z-index: 1;
    }
    .welcome-hero-copy {
        flex: 1;
        display: flex;
        flex-direction: column;
        justify-content: center;
        min-width: 0;
    }
    .welcome-hero-top {
        display: flex;
        align-items: center;
        gap: 14px;
        margin-bottom: 1rem;
    }
    .welcome-hero-logo {
        width: 84px;
        height: auto;
        display: block;
    }
    .status-chip-row {
        margin-top: 1.15rem;
        margin-bottom: 1rem;
    }
    .welcome-hero-media {
        width: min(34vw, 300px);
        min-width: 220px;
        display: flex;
        align-items: stretch;
    }
    .welcome-hero-image {
        width: 100%;
        height: 100%;
        object-fit: cover;
        border-radius: 22px;
        display: block;
        box-shadow: 0 18px 38px rgba(30, 78, 112, 0.14);
    }
    .welcome-banner {
        background: linear-gradient(135deg, #eef6ff 0%, #f8fbff 55%, #ffffff 100%);
        border: 1px solid #d6e4f3;
        border-radius: 18px;
        box-shadow: 0 10px 24px rgba(55, 96, 138, 0.08);
        padding: 0;
        margin-top: 1.1rem;
        margin-bottom: 1rem;
        position: relative;
        overflow: hidden;
        display: flex;
        align-items: stretch;
        gap: 20px;
        min-height: 172px;
    }
    .welcome-banner::after {
        content: "";
        position: absolute;
        inset: 0;
        background: radial-gradient(circle at top right, rgba(108, 164, 214, 0.12) 0%, transparent 32%);
        pointer-events: none;
    }
    .welcome-media,
    .welcome-copy {
        position: relative;
        z-index: 1;
    }
    .welcome-media {
        flex-shrink: 0;
        display: flex;
        align-self: stretch;
    }
    .welcome-image {
        width: 164px;
        height: 100%;
        object-fit: cover;
        border-radius: 12px 0 0 12px;
        display: block;
        border: none;
        outline: none;
        box-shadow: none;
        background: transparent;
        padding: 0;
    }
    .welcome-copy {
        min-width: 0;
        display: flex;
        flex-direction: column;
        justify-content: center;
        padding: 18px 22px 18px 0;
    }
    .compact-welcome {
        display: block;
        padding: 16px 18px;
        margin-top: 0.25rem;
        margin-bottom: 0.8rem;
    }
    .welcome-kicker {
        color: #5d7995;
        font-size: 0.76rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 0.45rem;
        position: relative;
        z-index: 1;
    }
    .welcome-name {
        color: #1d364d;
        font-size: 1.4rem;
        font-weight: 800;
        line-height: 1.15;
        margin-bottom: 0.28rem;
        position: relative;
        z-index: 1;
    }
    .welcome-subtitle {
        color: #698096;
        font-size: 0.95rem;
        line-height: 1.5;
        position: relative;
        z-index: 1;
    }
    .welcome-context {
        color: #36566f;
        font-size: 0.92rem;
        font-weight: 700;
        margin-top: 0.55rem;
        position: relative;
        z-index: 1;
    }
    @media (max-width: 900px) {
        .welcome-banner {
            flex-direction: column;
            align-items: flex-start;
            min-height: auto;
            padding: 18px 22px;
        }
        .welcome-media {
            align-self: auto;
        }
        .welcome-image {
            width: 100%;
            max-width: 180px;
            height: auto;
            border-radius: 12px;
        }
        .welcome-copy {
            padding: 0;
        }
    }
    .header-card,
    .ehr-card,
    .dashboard-stat-card,
    .directory-card,
    .patient-header-card,
    .vital-card,
    .result-card {
        background: #ffffff;
        border: 1px solid #d9e3ec;
        border-radius: 18px;
        box-shadow: 0 10px 22px rgba(15, 23, 42, 0.05);
    }
    .header-card,
    .ehr-card,
    .patient-header-card {
        padding: 20px 22px;
        margin-bottom: 1rem;
    }
    .header-card {
        display: flex;
        align-items: center;
        gap: 14px;
    }
    .page-header-card {
        margin-bottom: 1.2rem;
    }
    .header-icon {
        width: 52px;
        height: 52px;
        border-radius: 14px;
        background: #eaf3fb;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
        flex-shrink: 0;
    }
    .app-title {
        font-size: 1.9rem;
        font-weight: 800;
        color: #1d364d;
        line-height: 1.1;
    }
    .header-subtitle {
        color: #6a7b8d;
        font-size: 0.97rem;
        margin-top: 0.28rem;
    }
    .warning-note {
        text-align: center;
        color: #8a5a3b;
        font-size: 0.92rem;
        margin-bottom: 1rem;
        background: #fff3ee;
        border: 1px solid #f1d4c9;
        border-radius: 12px;
        padding: 0.7rem 0.9rem;
    }
    .dashboard-stat-card {
        padding: 18px 20px;
        margin-bottom: 1rem;
        animation: fadeUp 0.62s ease both;
    }
    .dashboard-stat-icon {
        width: 38px;
        height: 38px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 12px;
        background: rgba(234, 243, 251, 0.92);
        color: #345c7b;
        font-size: 1rem;
        margin-bottom: 0.75rem;
    }
    .patient-stat {
        background: linear-gradient(180deg, #f6fbff 0%, #ffffff 100%);
    }
    .review-stat {
        background: linear-gradient(180deg, #f4fbf8 0%, #ffffff 100%);
    }
    .pending-stat {
        background: linear-gradient(180deg, #fff8f2 0%, #ffffff 100%);
    }
    .dashboard-stat-label,
    .card-label,
    .vital-label {
        color: #6a7b8d;
        font-size: 0.84rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.45rem;
    }
    .dashboard-stat-value {
        color: #1f3347;
        font-size: 1.8rem;
        font-weight: 800;
    }
    .settings-value {
        color: #1d364d;
        font-size: 1.2rem;
        font-weight: 800;
        margin-top: 0.3rem;
    }
    .section-title {
        font-size: 1.18rem;
        font-weight: 800;
        color: #24445d;
        margin-top: 0.55rem;
        margin-bottom: 0.85rem;
    }
    .directory-card {
        background: linear-gradient(180deg, #fbfdff 0%, #ffffff 100%);
        padding: 18px;
        margin-bottom: 0.75rem;
        min-height: 210px;
        transition: transform 0.18s ease, box-shadow 0.18s ease, border-color 0.18s ease;
    }
    .directory-card:hover {
        transform: translateY(-2px);
        border-color: #8fb4d4;
        box-shadow: 0 18px 30px rgba(59, 101, 138, 0.12);
    }
    .directory-card-top {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 10px;
        margin-bottom: 1rem;
    }
    .directory-avatar,
    .patient-avatar {
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 800;
    }
    .directory-avatar {
        width: 48px;
        height: 48px;
        border-radius: 999px;
        background: linear-gradient(135deg, #d9ebf8 0%, #edf6fd 100%);
        color: #274c69;
        border: 1px solid #cfe0ee;
    }
    .directory-status,
    .status-badge,
    .visit-type-tag {
        display: inline-flex;
        align-items: center;
        border-radius: 999px;
        padding: 0.32rem 0.8rem;
        font-size: 0.82rem;
        font-weight: 700;
    }
    .status-not-complete {
        background: #fff0ee;
        color: #b34f43;
        border: 1px solid #f1d3cf;
    }
    .status-complete {
        background: #eaf7ef;
        color: #2f7d57;
        border: 1px solid #cfe8db;
    }
    .visit-type-tag {
        background: #edf4ff;
        color: #325e94;
        border: 1px solid #d6e4f8;
    }
    .directory-name,
    .patient-header-name {
        color: #173f53;
        font-weight: 800;
        line-height: 1.2;
    }
    .directory-name {
        font-size: 1.15rem;
        margin-bottom: 0.28rem;
    }
    .directory-id,
    .patient-caption {
        color: #7890a0;
        font-size: 0.84rem;
        margin-bottom: 0.7rem;
    }
    .directory-condition,
    .notes-line,
    .result-text {
        color: #435466;
        line-height: 1.6;
    }
    .patient-header-card {
        background: linear-gradient(180deg, #ffffff 0%, #f8fbfe 100%);
    }
    .patient-header-main {
        display: flex;
        align-items: center;
        gap: 14px;
        margin-bottom: 1rem;
    }
    .patient-avatar {
        width: 60px;
        height: 60px;
        border-radius: 18px;
        background: linear-gradient(135deg, #d7effa 0%, #ebf7fb 100%);
        font-size: 1.8rem;
        flex-shrink: 0;
    }
    .patient-header-subtitle {
        color: #6b7c8c;
        font-size: 0.96rem;
        margin-top: 0.25rem;
    }
    .patient-header-copy {
        flex: 1;
    }
    .patient-header-tags {
        display: flex;
        gap: 0.5rem;
        flex-wrap: wrap;
        margin-top: 0.8rem;
    }
    .patient-header-grid {
        display: grid;
        grid-template-columns: repeat(5, minmax(0, 1fr));
        gap: 12px;
    }
    .header-metric {
        background: #f7fafc;
        border: 1px solid #e2eaf1;
        border-radius: 14px;
        padding: 12px 14px;
    }
    .header-metric span {
        display: block;
        font-size: 0.78rem;
        color: #708090;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.3rem;
    }
    .header-metric strong {
        font-size: 1rem;
        color: #1f3347;
    }
    .overview-card {
        background: linear-gradient(180deg, #f6fbff 0%, #ffffff 100%);
    }
    .notes-accent-card {
        background: linear-gradient(180deg, #fffdf4 0%, #ffffff 100%);
    }
    .vital-card {
        padding: 14px 16px;
        min-height: 92px;
        background: linear-gradient(180deg, #f3fbf8 0%, #ffffff 100%);
    }
    .vital-value {
        color: #1f3347;
        font-size: 1.15rem;
        font-weight: 800;
    }
    .vital-indicator {
        display: flex;
        align-items: center;
        gap: 6px;
        margin-top: 0.6rem;
        font-size: 0.82rem;
        font-weight: 700;
        color: #617384;
    }
    .indicator-dot {
        width: 10px;
        height: 10px;
        border-radius: 999px;
        display: inline-block;
    }
    .indicator-normal {
        background: #4fa972;
    }
    .indicator-borderline {
        background: #d0a645;
    }
    .vital-borderline {
        background: linear-gradient(180deg, #fffaf0 0%, #ffffff 100%);
        border-color: #ead9ab;
    }
    .ai-billing-shell {
        background: linear-gradient(180deg, #f4f5ff 0%, #ffffff 100%);
        border-color: #d7daf4;
    }
    .ai-billing-header {
        display: flex;
        align-items: center;
        gap: 14px;
        margin-bottom: 1.15rem;
        padding-bottom: 0.95rem;
        border-bottom: 1px solid #e2e6f5;
    }
    .ai-billing-icon {
        width: 54px;
        height: 54px;
        border-radius: 16px;
        background: linear-gradient(135deg, #dfe5ff 0%, #eef2ff 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
        flex-shrink: 0;
    }
    .ai-billing-title {
        font-size: 1.2rem;
        font-weight: 800;
        color: #2b3f69;
    }
    .ai-billing-subtitle {
        color: #6d7795;
        font-size: 0.93rem;
        margin-top: 0.3rem;
    }
    .field-gap {
        height: 0.45rem;
    }
    .smart-hint {
        margin-top: 0.8rem;
        padding: 0.78rem 0.9rem;
        border-radius: 12px;
        background: #f0f4ff;
        border: 1px solid #d9e3fb;
        color: #58709a;
        font-size: 0.9rem;
        font-weight: 600;
    }
    .guided-input-note {
        margin-bottom: 0.85rem;
        color: #607b96;
        font-size: 0.9rem;
        line-height: 1.5;
    }
    .results-heading {
        font-size: 1.28rem;
        font-weight: 800;
        color: #1d364d;
        margin-top: 1.2rem;
        margin-bottom: 1rem;
    }
    .result-card {
        padding: 18px 20px;
        margin-bottom: 0.85rem;
        background: linear-gradient(180deg, #fbfdff 0%, #ffffff 100%);
        border-left: 4px solid #6ea8d8;
        animation: fadeUp 0.55s ease both;
    }
    .result-top-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 10px;
        margin-bottom: 0.45rem;
    }
    .result-code {
        font-size: 1.15rem;
        font-weight: 800;
        color: #18354a;
    }
    .confidence-badge {
        background: #edf5fb;
        color: #28597a;
        border: 1px solid #d5e4f1;
        border-radius: 999px;
        padding: 0.22rem 0.7rem;
        font-size: 0.8rem;
        font-weight: 700;
    }
    .result-description {
        color: #5e7082;
        font-size: 0.96rem;
        margin-bottom: 0.8rem;
    }
    .result-section-label {
        color: #6f8192;
        font-size: 0.78rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.35rem;
    }
    .spacer-sm {
        height: 0.5rem;
    }
    .footer-note {
        text-align: center;
        color: #7a8897;
        font-size: 0.94rem;
        margin-top: 2rem;
        margin-bottom: 1.5rem;
    }
    div[data-testid="stTextInput"] label p {
        font-size: 0.92rem;
        font-weight: 600;
        color: #4b5d6b;
    }
    div[data-testid="stTextInput"] input {
        border-radius: 14px !important;
        border: 1px solid #d2daea !important;
        background: #fbfcff !important;
    }
    div.stButton {
        margin-bottom: 0.65rem;
    }
    div.stButton > button {
        border-radius: 14px;
        height: 3rem;
        font-weight: 700;
        border: 1px solid rgba(160, 191, 220, 0.9);
        background: linear-gradient(180deg, rgba(248, 251, 255, 0.98) 0%, rgba(233, 242, 251, 0.98) 100%);
        color: #234e70;
        box-shadow: 0 8px 18px rgba(69, 116, 155, 0.10);
        transition: all 0.22s ease;
    }
    div.stButton > button:hover {
        border-color: #8fb4d4;
        color: #1c425f;
        transform: translateY(-2px);
        box-shadow: 0 14px 24px rgba(69, 116, 155, 0.14);
    }
    button[kind="primary"] {
        background: linear-gradient(135deg, #4b8fd2 0%, #2f6ca8 55%, #245784 100%) !important;
        border: 1px solid #2e6a9e !important;
        color: #ffffff !important;
        box-shadow: 0 14px 28px rgba(53, 118, 179, 0.28) !important;
    }
    button[kind="primary"]:hover {
        background: linear-gradient(135deg, #3d84ca 0%, #295f95 55%, #214d75 100%) !important;
        color: #ffffff !important;
        box-shadow: 0 18px 34px rgba(53, 118, 179, 0.34) !important;
    }
    section[data-testid="stSidebar"] div.stButton > button {
        justify-content: flex-start;
        padding-left: 1rem;
        background: rgba(255, 255, 255, 0.06);
        color: #dce8f3;
        box-shadow: none;
        border-color: rgba(167, 191, 214, 0.18);
    }
    section[data-testid="stSidebar"] div.stButton > button:hover {
        background: rgba(255, 255, 255, 0.1);
        border-color: rgba(167, 191, 214, 0.3);
        color: #ffffff;
        transform: none;
        box-shadow: none;
    }
    section[data-testid="stSidebar"] button[kind="primary"] {
        background: linear-gradient(180deg, rgba(76, 128, 177, 0.95) 0%, rgba(55, 100, 147, 0.95) 100%) !important;
        border: 1px solid rgba(146, 186, 221, 0.22) !important;
        color: #ffffff !important;
        box-shadow: inset 0 0 0 1px rgba(192, 219, 241, 0.08) !important;
    }
    button[title*="star" i],
    button[aria-label*="star" i],
    button[title*="edit" i],
    button[aria-label*="edit" i],
    a[title*="github" i],
    a[aria-label*="github" i],
    button[title*="github" i],
    button[aria-label*="github" i],
    #MainMenu,
    button[aria-label*="menu" i][kind="header"],
    button[title*="more" i],
    button[aria-label*="more" i] {
        display: none !important;
        visibility: hidden !important;
    }
    [data-testid="stToolbar"] a:not(:first-child),
    [data-testid="stToolbar"] button:not(:first-child) {
        display: none !important;
        visibility: hidden !important;
    }
    .page-header-card,
    .dashboard-info-card,
    .patient-header-card,
    .directory-card,
    .billing-card,
    .overview-card,
    .notes-accent-card {
        animation: fadeUp 0.62s ease both;
    }
    @media (max-width: 900px) {
        .entry-card {
            padding: 30px 24px;
            border-radius: 24px;
        }
        .entry-title {
            font-size: 1.95rem;
        }
        .auth-visual-panel {
            min-height: auto;
            padding: 34px 26px;
        }
        .auth-form-card,
        .login-card,
        .welcome-card {
            max-width: 100%;
            padding: 32px 26px;
        }
        .welcome-hero {
            flex-direction: column;
            padding: 28px 24px;
        }
        .welcome-hero-media {
            width: 100%;
            min-width: 0;
        }
        .welcome-hero-image {
            max-height: 260px;
        }
        .welcome-hero-top {
            flex-direction: column;
            align-items: flex-start;
            gap: 10px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

patient_case_issues = validate_patient_cases(PATIENTS)
if patient_case_issues:
    raise ValueError("Invalid demo patient cases:\n" + "\n".join(patient_case_issues))

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "doctor_name" not in st.session_state:
    st.session_state["doctor_name"] = ""
if "welcome_seen" not in st.session_state:
    st.session_state["welcome_seen"] = False
if "page" not in st.session_state:
    st.session_state["page"] = "Dashboard"
if "selected_patient" not in st.session_state:
    st.session_state["selected_patient"] = ""
if "patient_filter" not in st.session_state:
    st.session_state["patient_filter"] = "All"
if "billing_reviews" not in st.session_state:
    st.session_state["billing_reviews"] = 0
if "generated_reviews" not in st.session_state:
    st.session_state["generated_reviews"] = {}
valid_patient_ids = {patient["patient_id"] for patient in PATIENTS}
if "generated_reviews" in st.session_state:
    st.session_state["generated_reviews"] = {
        patient_id: reviews
        for patient_id, reviews in st.session_state["generated_reviews"].items()
        if patient_id in valid_patient_ids
    }
if (
    "patient_records" not in st.session_state
    or len(st.session_state["patient_records"]) != len(PATIENTS)
    or any("primary_condition" not in patient for patient in st.session_state["patient_records"])
):
    st.session_state["patient_records"] = copy.deepcopy(build_patient_records(PATIENTS))
if "visit_reason" not in st.session_state:
    st.session_state["visit_reason"] = ""
if "diagnosis" not in st.session_state:
    st.session_state["diagnosis"] = ""
if "procedure" not in st.session_state:
    st.session_state["procedure"] = ""
if st.session_state["selected_patient"] and not find_patient_record(st.session_state["selected_patient"]):
    st.session_state["selected_patient"] = ""

st.session_state["billing_reviews"] = len(st.session_state["generated_reviews"])

if not st.session_state["logged_in"]:
    render_login_screen()
elif not st.session_state["welcome_seen"]:
    render_welcome_screen()
else:
    current_page = st.session_state["page"]
    if current_page == "Dashboard":
        render_dashboard_home()
    elif current_page == "Patients":
        render_patient_selection()
    elif current_page == "Billing Assistant":
        if st.session_state["selected_patient"]:
            render_main_app()
        else:
            render_billing_assistant_gate()
    elif current_page == "Settings":
        render_settings_page()
    else:
        render_dashboard_home()

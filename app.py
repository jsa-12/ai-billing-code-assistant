import base64
import copy
import os
import re

import pandas as pd
import streamlit as st

SHARED_PASSWORD = "demo123"
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
    "management",
}

PATIENTS = [
    {
        "name": "Fahda Alajmi",
        "patient_id": "PT-20001",
        "age": 26,
        "gender": "Female",
        "primary_condition": "Hypertension",
        "visit_type": "Chronic care follow-up",
        "insurance": "Active PPO",
        "patient_bio": "Fahda Alajmi is a 26-year-old Female patient with essential hypertension managed with medication. She is visiting today for blood pressure follow-up and medication review.",
        "vitals": {
            "blood_pressure": "138/86 mmHg",
            "heart_rate": "78 bpm",
            "temperature": "98.4 F",
            "oxygen_saturation": "98%",
        },
        "clinical_note": "Patient presents for hypertension follow-up and blood pressure review. Home blood pressure readings have been mildly elevated this week. Medication management and cardiovascular follow-up completed in clinic.",
        "default_visit_reason": "Blood pressure follow-up",
        "default_diagnosis": "Essential hypertension",
        "default_procedure": "Established patient follow-up with medication management",
        "status": "Not Complete",
    },
    {
        "name": "Rawan Alghebiwi",
        "patient_id": "PT-20002",
        "age": 24,
        "gender": "Female",
        "primary_condition": "Sore Throat/URI",
        "visit_type": "Acute sick visit",
        "insurance": "Commercial HMO",
        "patient_bio": "Rawan Alghebiwi is a 24-year-old Female patient with no major chronic conditions. She is visiting today for sore throat and upper respiratory symptoms.",
        "vitals": {
            "blood_pressure": "116/72 mmHg",
            "heart_rate": "92 bpm",
            "temperature": "99.1 F",
            "oxygen_saturation": "98%",
        },
        "clinical_note": "Patient reports sore throat, congestion, and mild cough for 3 days. Low-grade fever noted yesterday. Focused respiratory exam completed and rapid strep testing discussed.",
        "default_visit_reason": "Sore throat and congestion",
        "default_diagnosis": "Acute pharyngitis / upper respiratory infection",
        "default_procedure": "Office sick visit with rapid strep evaluation",
        "status": "Not Complete",
    },
    {
        "name": "Rohan Allen",
        "patient_id": "PT-20003",
        "age": 29,
        "gender": "Male",
        "primary_condition": "GERD",
        "visit_type": "Medication management visit",
        "insurance": "Employer-Sponsored Plan",
        "patient_bio": "Rohan Allen is a 29-year-old Male patient with gastroesophageal reflux disease. He is visiting today for persistent reflux symptoms after meals.",
        "vitals": {
            "blood_pressure": "122/78 mmHg",
            "heart_rate": "74 bpm",
            "temperature": "98.3 F",
            "oxygen_saturation": "99%",
        },
        "clinical_note": "Patient reports reflux, heartburn, and mild upper abdominal discomfort after meals. Symptoms improve partially with over-the-counter medication. GERD counseling and medication review completed.",
        "default_visit_reason": "Heartburn and reflux follow-up",
        "default_diagnosis": "Gastroesophageal reflux disease",
        "default_procedure": "Established patient evaluation with reflux medication review",
        "status": "Not Complete",
    },
    {
        "name": "Jawad Alobaidan",
        "patient_id": "PT-20004",
        "age": 27,
        "gender": "Male",
        "primary_condition": "Low Back Pain",
        "visit_type": "Established outpatient visit",
        "insurance": "Marketplace Bronze Plan",
        "patient_bio": "Jawad Alobaidan is a 27-year-old Male patient with intermittent low back pain. He is visiting today after increased discomfort related to prolonged sitting.",
        "vitals": {
            "blood_pressure": "118/76 mmHg",
            "heart_rate": "72 bpm",
            "temperature": "98.2 F",
            "oxygen_saturation": "99%",
        },
        "clinical_note": "Patient reports low back pain after long periods of sitting. No trauma, weakness, or bowel or bladder symptoms. Focused musculoskeletal exam completed and conservative follow-up discussed.",
        "default_visit_reason": "Low back pain after prolonged sitting",
        "default_diagnosis": "Low back pain",
        "default_procedure": "Established patient musculoskeletal evaluation",
        "status": "Not Complete",
    },
    {
        "name": "Koniska Bandyopadhyay",
        "patient_id": "PT-20005",
        "age": 25,
        "gender": "Female",
        "primary_condition": "Hypertension",
        "visit_type": "Chronic care follow-up",
        "insurance": "Medicaid Managed Care",
        "patient_bio": "Koniska Bandyopadhyay is a 25-year-old Female patient with recently diagnosed hypertension. She is visiting today for follow-up on blood pressure control.",
        "vitals": {
            "blood_pressure": "142/88 mmHg",
            "heart_rate": "80 bpm",
            "temperature": "98.5 F",
            "oxygen_saturation": "98%",
        },
        "clinical_note": "Patient is here for hypertension follow-up. Blood pressure remains above goal despite current therapy. Medication management and treatment follow-up reviewed during the visit.",
        "default_visit_reason": "Hypertension medication follow-up",
        "default_diagnosis": "Essential hypertension",
        "default_procedure": "Office follow-up for blood pressure management",
        "status": "Not Complete",
    },
    {
        "name": "Bill Bwana",
        "patient_id": "PT-20006",
        "age": 31,
        "gender": "Male",
        "primary_condition": "Sore Throat/URI",
        "visit_type": "Acute sick visit",
        "insurance": "Active PPO",
        "patient_bio": "Bill Bwana is a 31-year-old Male patient with no chronic cardiopulmonary disease. He is visiting today for sore throat, cough, and respiratory symptoms.",
        "vitals": {
            "blood_pressure": "120/74 mmHg",
            "heart_rate": "90 bpm",
            "temperature": "99.0 F",
            "oxygen_saturation": "97%",
        },
        "clinical_note": "Patient reports sore throat, cough, and nasal congestion for 2 days. No chest pain or shortness of breath. Focused respiratory exam completed and URI care plan reviewed.",
        "default_visit_reason": "Cough, congestion, and sore throat",
        "default_diagnosis": "Upper respiratory infection",
        "default_procedure": "Office sick visit with focused respiratory evaluation",
        "status": "Not Complete",
    },
    {
        "name": "Khadidiatou Dia",
        "patient_id": "PT-20007",
        "age": 28,
        "gender": "Female",
        "primary_condition": "GERD",
        "visit_type": "Medication management visit",
        "insurance": "Commercial HMO",
        "patient_bio": "Khadidiatou Dia is a 28-year-old Female patient with GERD symptoms triggered by late meals. She is visiting today for reflux follow-up.",
        "vitals": {
            "blood_pressure": "114/70 mmHg",
            "heart_rate": "76 bpm",
            "temperature": "98.1 F",
            "oxygen_saturation": "99%",
        },
        "clinical_note": "Patient reports worsening heartburn and reflux in the evening with occasional abdominal discomfort. GERD symptoms and medication adherence were reviewed in clinic.",
        "default_visit_reason": "Reflux and heartburn follow-up",
        "default_diagnosis": "Gastroesophageal reflux disease",
        "default_procedure": "Established patient reflux evaluation and counseling",
        "status": "Not Complete",
    },
    {
        "name": "Yuying Ding",
        "patient_id": "PT-20008",
        "age": 23,
        "gender": "Female",
        "primary_condition": "Low Back Pain",
        "visit_type": "Established outpatient visit",
        "insurance": "Student Health Plan",
        "patient_bio": "Yuying Ding is a 23-year-old Female patient with recurrent low back pain related to posture and prolonged studying. She is visiting today for symptom review.",
        "vitals": {
            "blood_pressure": "112/68 mmHg",
            "heart_rate": "70 bpm",
            "temperature": "98.0 F",
            "oxygen_saturation": "99%",
        },
        "clinical_note": "Patient reports back pain after prolonged sitting and computer work. No trauma or neurologic deficits reported. Musculoskeletal exam completed and supportive care discussed.",
        "default_visit_reason": "Low back pain with prolonged sitting",
        "default_diagnosis": "Low back pain",
        "default_procedure": "Office follow-up with musculoskeletal exam",
        "status": "Not Complete",
    },
    {
        "name": "Zihang Ding",
        "patient_id": "PT-20009",
        "age": 30,
        "gender": "Male",
        "primary_condition": "Hypertension",
        "visit_type": "Medication management visit",
        "insurance": "Employer-Sponsored Plan",
        "patient_bio": "Zihang Ding is a 30-year-old Male patient with hypertension on daily medication. He is visiting today for blood pressure and treatment follow-up.",
        "vitals": {
            "blood_pressure": "136/84 mmHg",
            "heart_rate": "77 bpm",
            "temperature": "98.4 F",
            "oxygen_saturation": "98%",
        },
        "clinical_note": "Patient presents for blood pressure follow-up and hypertension medication management. Home readings are variable but improving. Cardiovascular follow-up completed during the visit.",
        "default_visit_reason": "Blood pressure check and medication review",
        "default_diagnosis": "Essential hypertension",
        "default_procedure": "Established patient follow-up for hypertension management",
        "status": "Not Complete",
    },
    {
        "name": "Chengcheng Du",
        "patient_id": "PT-20010",
        "age": 24,
        "gender": "Female",
        "primary_condition": "Sore Throat/URI",
        "visit_type": "Acute sick visit",
        "insurance": "Marketplace Bronze Plan",
        "patient_bio": "Chengcheng Du is a 24-year-old Female patient with an acute sore throat and congestion. She is visiting today for upper respiratory evaluation.",
        "vitals": {
            "blood_pressure": "118/71 mmHg",
            "heart_rate": "88 bpm",
            "temperature": "99.3 F",
            "oxygen_saturation": "98%",
        },
        "clinical_note": "Patient reports sore throat, nasal congestion, and dry cough for 4 days with intermittent fever. Respiratory symptoms reviewed and focused exam completed in clinic.",
        "default_visit_reason": "Sore throat with congestion and cough",
        "default_diagnosis": "Acute upper respiratory infection",
        "default_procedure": "Focused respiratory office evaluation",
        "status": "Not Complete",
    },
]


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
    return [
        token
        for token in TOKEN_PATTERN.findall(str(text).lower())
        if len(token) > 2 and token not in STOPWORDS
    ]


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

    if not term_weights:
        raise ValueError("Enter more clinical detail to search the billing code dataset.")

    scored_rows = []
    for row in billing_codes.itertuples(index=False):
        score = 0
        matched_terms = []

        for term, weight in term_weights.items():
            if term in row.search_terms:
                score += weight * 3
                matched_terms.append(term)

        if diagnosis_text and diagnosis_text in row.search_text:
            score += 8

        if row.category_description and row.category_description.lower() in query_text:
            score += 4

        if score > 0:
            scored_rows.append((score, len(matched_terms), row, matched_terms))

    if not scored_rows:
        raise ValueError("No relevant billing codes were found in the local dataset for these inputs.")

    scored_rows.sort(
        key=lambda item: (
            item[0],
            item[1],
            len(item[2].description),
        ),
        reverse=True,
    )

    suggestions = []
    seen_codes = set()
    for _, _, row, matched_terms in scored_rows:
        if row.icd10_code in seen_codes:
            continue

        seen_codes.add(row.icd10_code)
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
        st.markdown('<div class="section-title">💳 Billing Code Assistant</div>', unsafe_allow_html=True)
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

        visit_reason = st.text_input(
            "🩺 Visit Reason",
            key="visit_reason",
            placeholder=profile["default_visit_reason"],
        )
        st.markdown('<div class="field-gap"></div>', unsafe_allow_html=True)
        diagnosis = st.text_input(
            "🧾 Diagnosis",
            key="diagnosis",
            placeholder=profile["default_diagnosis"],
        )
        st.markdown('<div class="field-gap"></div>', unsafe_allow_html=True)
        procedure = st.text_input(
            "⚙️ Procedure",
            key="procedure",
            placeholder=profile["default_procedure"],
        )
        st.markdown(
            '<div class="smart-hint">💡 Tip: Be specific with diagnosis to improve code accuracy</div>',
            unsafe_allow_html=True,
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

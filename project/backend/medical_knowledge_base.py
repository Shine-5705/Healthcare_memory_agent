"""
Medical Knowledge Base using Qdrant Vector Database
Searchable database of chronic conditions, treatments, symptoms, and care guidelines
"""
import os
import uuid
from typing import List, Dict, Optional, Tuple
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
from sentence_transformers import SentenceTransformer
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MedicalKnowledgeBase:
    """Manages medical knowledge base using Qdrant vector database"""
    
    # Comprehensive medical knowledge for 20+ chronic conditions
    MEDICAL_CONDITIONS = {
        "diabetes_type2": {
            "name": "Type 2 Diabetes",
            "category": "Metabolic Disorder",
            "description": "A chronic condition affecting how the body processes blood sugar (glucose). The body either resists insulin or doesn't produce enough insulin.",
            "symptoms": [
                "Increased thirst and frequent urination",
                "Increased hunger",
                "Unintended weight loss",
                "Fatigue and weakness",
                "Blurred vision",
                "Slow-healing sores or frequent infections",
                "Tingling or numbness in hands or feet",
                "Dark patches on skin (acanthosis nigricans)"
            ],
            "risk_factors": [
                "Being overweight or obese",
                "Family history of diabetes",
                "Age over 45",
                "Physical inactivity",
                "High blood pressure",
                "High cholesterol levels"
            ],
            "treatments": [
                "Blood sugar monitoring - Regular glucose testing",
                "Metformin - First-line medication to control blood sugar",
                "Insulin therapy - When oral medications are insufficient",
                "GLP-1 receptor agonists - Injectable medications",
                "SGLT2 inhibitors - Kidney-based glucose management",
                "Dietary modifications - Low glycemic index diet",
                "Regular exercise - 150 minutes per week",
                "Weight management - 5-10% weight loss can improve control"
            ],
            "care_guidelines": [
                "Monitor blood sugar levels as recommended by doctor",
                "Take medications as prescribed",
                "Follow diabetic diet plan with portion control",
                "Exercise regularly with doctor approval",
                "Schedule regular eye exams (annually)",
                "Check feet daily for injuries or infections",
                "Maintain healthy weight",
                "Monitor blood pressure and cholesterol",
                "Get annual flu vaccination",
                "Regular dental check-ups"
            ],
            "complications": [
                "Heart disease and stroke",
                "Kidney disease (nephropathy)",
                "Eye damage (retinopathy)",
                "Nerve damage (neuropathy)",
                "Foot problems and infections"
            ]
        },
        "hypertension": {
            "name": "Hypertension (High Blood Pressure)",
            "category": "Cardiovascular",
            "description": "A condition where blood pressure remains consistently elevated above 130/80 mmHg, increasing risk of heart disease and stroke.",
            "symptoms": [
                "Often no symptoms (silent killer)",
                "Severe headaches",
                "Nosebleeds",
                "Fatigue or confusion",
                "Vision problems",
                "Chest pain",
                "Irregular heartbeat",
                "Blood in urine"
            ],
            "risk_factors": [
                "Family history",
                "Age (risk increases with age)",
                "Obesity",
                "High sodium diet",
                "Lack of physical activity",
                "Excessive alcohol consumption",
                "Chronic stress",
                "Smoking"
            ],
            "treatments": [
                "ACE inhibitors - Lisinopril, enalapril",
                "ARBs (Angiotensin II receptor blockers) - Losartan, valsartan",
                "Calcium channel blockers - Amlodipine",
                "Diuretics - Hydrochlorothiazide (water pills)",
                "Beta-blockers - Metoprolol, atenolol",
                "DASH diet - Low sodium, high potassium",
                "Regular aerobic exercise",
                "Stress management techniques"
            ],
            "care_guidelines": [
                "Monitor blood pressure regularly at home",
                "Take medications at same time daily",
                "Limit sodium intake to 1500-2000mg per day",
                "Maintain healthy weight (BMI 18.5-24.9)",
                "Exercise 150 minutes weekly",
                "Limit alcohol (1 drink for women, 2 for men daily)",
                "Quit smoking",
                "Manage stress through meditation or yoga",
                "Get adequate sleep (7-8 hours)",
                "Regular follow-up with healthcare provider"
            ],
            "complications": [
                "Heart attack or heart failure",
                "Stroke or transient ischemic attack",
                "Kidney disease or failure",
                "Vision loss",
                "Sexual dysfunction"
            ]
        },
        "copd": {
            "name": "COPD (Chronic Obstructive Pulmonary Disease)",
            "category": "Respiratory",
            "description": "A progressive lung disease causing breathing difficulties due to damaged airways and emphysema, primarily caused by smoking.",
            "symptoms": [
                "Chronic cough with mucus (smoker's cough)",
                "Shortness of breath, especially during activities",
                "Wheezing",
                "Chest tightness",
                "Frequent respiratory infections",
                "Lack of energy and fatigue",
                "Unintended weight loss (in later stages)",
                "Swelling in ankles, feet, or legs"
            ],
            "risk_factors": [
                "Smoking (primary cause)",
                "Long-term exposure to air pollutants",
                "Occupational dust and chemicals",
                "Alpha-1 antitrypsin deficiency",
                "Indoor air pollution",
                "History of respiratory infections in childhood"
            ],
            "treatments": [
                "Bronchodilators - Albuterol, tiotropium (inhalers)",
                "Inhaled corticosteroids - Fluticasone",
                "Combination inhalers - Symbicort, Advair",
                "Oral steroids - For exacerbations",
                "Antibiotics - For bacterial infections",
                "Oxygen therapy - For severe cases",
                "Pulmonary rehabilitation program",
                "Smoking cessation - Most critical intervention",
                "Vaccinations - Flu and pneumonia shots"
            ],
            "care_guidelines": [
                "Quit smoking immediately (most important)",
                "Use inhalers correctly and consistently",
                "Practice breathing exercises and pursed-lip breathing",
                "Stay active with appropriate exercise",
                "Avoid lung irritants (smoke, pollution, chemicals)",
                "Get flu shot annually and pneumonia vaccine",
                "Maintain healthy weight",
                "Use oxygen as prescribed",
                "Join pulmonary rehabilitation program",
                "Monitor symptoms and seek early treatment for exacerbations"
            ],
            "complications": [
                "Respiratory infections",
                "Heart problems",
                "Lung cancer",
                "Pulmonary hypertension",
                "Depression and anxiety"
            ]
        },
        "asthma": {
            "name": "Asthma",
            "category": "Respiratory",
            "description": "A chronic condition causing inflammation and narrowing of airways, leading to breathing difficulties and attacks triggered by various factors.",
            "symptoms": [
                "Shortness of breath",
                "Chest tightness or pain",
                "Wheezing when exhaling",
                "Coughing, especially at night or early morning",
                "Difficulty sleeping due to breathing problems",
                "Whistling sound when breathing",
                "Worsening symptoms with exercise or cold air"
            ],
            "risk_factors": [
                "Family history of asthma or allergies",
                "Childhood respiratory infections",
                "Allergies (allergic asthma)",
                "Exposure to tobacco smoke",
                "Occupational exposures",
                "Obesity",
                "Air pollution exposure"
            ],
            "treatments": [
                "Quick-relief inhalers - Albuterol (rescue inhaler)",
                "Long-term control - Inhaled corticosteroids",
                "Leukotriene modifiers - Montelukast (Singulair)",
                "Long-acting beta agonists - Salmeterol",
                "Combination inhalers - Advair, Symbicort",
                "Biologics - For severe asthma (Xolair, Dupixent)",
                "Allergy medications or immunotherapy",
                "Bronchial thermoplasty - For severe cases"
            ],
            "care_guidelines": [
                "Use preventer inhaler daily as prescribed",
                "Keep rescue inhaler accessible always",
                "Identify and avoid asthma triggers",
                "Use peak flow meter to monitor lung function",
                "Develop asthma action plan with doctor",
                "Take allergy medications if applicable",
                "Get annual flu vaccination",
                "Exercise regularly with proper warm-up",
                "Maintain allergen-free home environment",
                "Regular follow-ups with pulmonologist"
            ],
            "complications": [
                "Severe asthma attacks requiring emergency care",
                "Permanent airway remodeling",
                "Side effects from long-term medication use",
                "Reduced quality of life",
                "Sleep disturbances"
            ]
        },
        "arthritis_rheumatoid": {
            "name": "Rheumatoid Arthritis",
            "category": "Autoimmune/Musculoskeletal",
            "description": "An autoimmune disorder causing chronic inflammation of joints, potentially leading to joint damage and disability if untreated.",
            "symptoms": [
                "Joint pain, tenderness, and swelling",
                "Morning stiffness lasting 30+ minutes",
                "Symmetrical joint involvement (both sides)",
                "Fatigue and weakness",
                "Low-grade fever",
                "Loss of appetite",
                "Firm lumps under skin (rheumatoid nodules)",
                "Reduced range of motion"
            ],
            "risk_factors": [
                "Female gender (more common in women)",
                "Age 40-60 (peak onset)",
                "Family history of RA",
                "Smoking",
                "Obesity",
                "Environmental exposures"
            ],
            "treatments": [
                "DMARDs - Methotrexate (gold standard)",
                "Biologics - TNF inhibitors (Humira, Enbrel)",
                "JAK inhibitors - Xeljanz, Rinvoq",
                "NSAIDs - Ibuprofen, naproxen for pain",
                "Corticosteroids - Prednisone for flares",
                "Physical therapy and occupational therapy",
                "Exercise programs - Low-impact activities",
                "Heat and cold therapy"
            ],
            "care_guidelines": [
                "Take DMARDs consistently as prescribed",
                "Regular monitoring of disease activity",
                "Balance rest and activity",
                "Protect joints during daily activities",
                "Maintain healthy weight to reduce joint stress",
                "Exercise regularly (swimming, walking, cycling)",
                "Use assistive devices when needed",
                "Apply heat or cold to affected joints",
                "Get adequate sleep",
                "Regular blood tests to monitor medication effects"
            ],
            "complications": [
                "Joint deformity and disability",
                "Osteoporosis",
                "Heart disease",
                "Lung problems",
                "Increased infection risk"
            ]
        },
        "osteoarthritis": {
            "name": "Osteoarthritis",
            "category": "Musculoskeletal",
            "description": "Degenerative joint disease causing cartilage breakdown, leading to pain and stiffness, commonly affecting knees, hips, hands, and spine.",
            "symptoms": [
                "Joint pain during or after movement",
                "Joint stiffness after inactivity",
                "Tenderness when pressing on joint",
                "Loss of flexibility",
                "Grating sensation during movement",
                "Bone spurs around affected joint",
                "Swelling from inflammation"
            ],
            "risk_factors": [
                "Age (over 50)",
                "Obesity",
                "Joint injuries or repetitive stress",
                "Genetics",
                "Bone deformities",
                "Certain metabolic diseases"
            ],
            "treatments": [
                "Acetaminophen - For mild to moderate pain",
                "NSAIDs - Ibuprofen, naproxen",
                "Topical NSAIDs - Diclofenac gel",
                "Corticosteroid injections",
                "Hyaluronic acid injections",
                "Physical therapy",
                "Weight management",
                "Joint replacement surgery - For severe cases"
            ],
            "care_guidelines": [
                "Maintain healthy weight",
                "Stay active with low-impact exercises",
                "Strengthen muscles around joints",
                "Use heat and cold therapy",
                "Protect joints with braces or supports",
                "Use assistive devices (canes, walkers)",
                "Pace activities and take breaks",
                "Practice good posture",
                "Consider occupational therapy for daily tasks"
            ],
            "complications": [
                "Chronic pain and disability",
                "Reduced mobility",
                "Sleep disturbances",
                "Depression from chronic pain",
                "Need for joint replacement"
            ]
        },
        "depression": {
            "name": "Major Depressive Disorder",
            "category": "Mental Health",
            "description": "A mood disorder causing persistent feelings of sadness, loss of interest, and various physical and emotional problems affecting daily functioning.",
            "symptoms": [
                "Persistent sad, anxious, or empty mood",
                "Loss of interest in activities once enjoyed",
                "Changes in appetite and weight",
                "Sleep disturbances (insomnia or oversleeping)",
                "Fatigue and decreased energy",
                "Feelings of worthlessness or guilt",
                "Difficulty concentrating or making decisions",
                "Thoughts of death or suicide",
                "Physical aches without clear cause"
            ],
            "risk_factors": [
                "Family history of depression",
                "Major life changes or trauma",
                "Chronic stress",
                "Certain medications",
                "Chronic illness",
                "Substance abuse",
                "Low self-esteem"
            ],
            "treatments": [
                "SSRIs - Fluoxetine (Prozac), sertraline (Zoloft)",
                "SNRIs - Venlafaxine (Effexor), duloxetine (Cymbalta)",
                "Cognitive behavioral therapy (CBT)",
                "Interpersonal therapy",
                "Psychotherapy (talk therapy)",
                "Electroconvulsive therapy (ECT) - For severe cases",
                "Exercise therapy",
                "Light therapy - For seasonal depression",
                "Mindfulness and meditation"
            ],
            "care_guidelines": [
                "Take antidepressants consistently as prescribed",
                "Attend therapy sessions regularly",
                "Maintain regular sleep schedule",
                "Exercise regularly (30 minutes daily)",
                "Eat balanced, nutritious meals",
                "Avoid alcohol and recreational drugs",
                "Stay connected with supportive people",
                "Set realistic goals and priorities",
                "Practice stress-reduction techniques",
                "Seek immediate help for suicidal thoughts"
            ],
            "complications": [
                "Increased suicide risk",
                "Substance abuse",
                "Relationship problems",
                "Work or school difficulties",
                "Physical health problems"
            ]
        },
        "anxiety_disorder": {
            "name": "Generalized Anxiety Disorder",
            "category": "Mental Health",
            "description": "A mental health condition characterized by excessive, persistent worry and anxiety about various aspects of life, interfering with daily activities.",
            "symptoms": [
                "Excessive worry about everyday situations",
                "Restlessness or feeling on edge",
                "Easily fatigued",
                "Difficulty concentrating",
                "Irritability",
                "Muscle tension",
                "Sleep disturbances",
                "Panic attacks (in some cases)",
                "Physical symptoms: rapid heartbeat, sweating, trembling"
            ],
            "risk_factors": [
                "Family history of anxiety",
                "Childhood adversity or trauma",
                "Chronic medical conditions",
                "Substance abuse",
                "Personality factors (shyness, nervousness)",
                "Stressful life events",
                "Female gender"
            ],
            "treatments": [
                "SSRIs - Escitalopram (Lexapro), paroxetine (Paxil)",
                "SNRIs - Venlafaxine (Effexor)",
                "Benzodiazepines - Short-term use only",
                "Buspirone - Anti-anxiety medication",
                "Cognitive behavioral therapy (CBT)",
                "Exposure therapy",
                "Relaxation techniques",
                "Mindfulness-based stress reduction",
                "Regular exercise"
            ],
            "care_guidelines": [
                "Practice relaxation and deep breathing exercises",
                "Maintain regular sleep schedule",
                "Exercise regularly",
                "Limit caffeine and alcohol",
                "Attend therapy sessions consistently",
                "Take medications as prescribed",
                "Challenge negative thoughts",
                "Practice mindfulness meditation",
                "Build support network",
                "Keep stress diary to identify triggers"
            ],
            "complications": [
                "Depression",
                "Substance abuse",
                "Digestive problems",
                "Headaches and chronic pain",
                "Social isolation"
            ]
        },
        "heart_failure": {
            "name": "Congestive Heart Failure",
            "category": "Cardiovascular",
            "description": "A chronic condition where the heart cannot pump blood efficiently to meet the body's needs, causing fluid buildup in lungs and other tissues.",
            "symptoms": [
                "Shortness of breath with activity or lying down",
                "Fatigue and weakness",
                "Swelling in legs, ankles, and feet",
                "Rapid or irregular heartbeat",
                "Persistent cough with white or pink phlegm",
                "Increased need to urinate at night",
                "Abdominal swelling",
                "Sudden weight gain from fluid retention",
                "Lack of appetite"
            ],
            "risk_factors": [
                "Coronary artery disease",
                "Previous heart attack",
                "High blood pressure",
                "Diabetes",
                "Obesity",
                "Smoking",
                "Alcohol abuse",
                "Sleep apnea"
            ],
            "treatments": [
                "ACE inhibitors - Lisinopril, enalapril",
                "Beta-blockers - Carvedilol, metoprolol",
                "Diuretics - Furosemide (Lasix)",
                "Aldosterone antagonists - Spironolactone",
                "ARNIs - Entresto (sacubitril/valsartan)",
                "Digoxin - For heart rhythm",
                "Low-sodium diet",
                "Fluid restriction",
                "Cardiac rehabilitation",
                "Implantable devices (pacemaker, ICD)"
            ],
            "care_guidelines": [
                "Monitor weight daily (report gain of 2-3 lbs)",
                "Limit sodium to 2000mg or less per day",
                "Restrict fluid intake as recommended",
                "Take medications exactly as prescribed",
                "Stay physically active as tolerated",
                "Avoid smoking and excessive alcohol",
                "Elevate legs to reduce swelling",
                "Get adequate rest",
                "Monitor blood pressure regularly",
                "Report worsening symptoms immediately"
            ],
            "complications": [
                "Kidney damage or failure",
                "Liver damage",
                "Heart valve problems",
                "Heart rhythm problems",
                "Sudden cardiac death"
            ]
        },
        "chronic_kidney_disease": {
            "name": "Chronic Kidney Disease",
            "category": "Renal",
            "description": "Progressive loss of kidney function over time, affecting the kidneys' ability to filter waste and excess fluids from blood.",
            "symptoms": [
                "Often no symptoms in early stages",
                "Fatigue and weakness",
                "Swelling in feet and ankles",
                "Shortness of breath",
                "Nausea and vomiting",
                "Loss of appetite",
                "Changes in urination (more or less)",
                "Sleep problems",
                "Muscle cramps",
                "Decreased mental sharpness"
            ],
            "risk_factors": [
                "Diabetes",
                "High blood pressure",
                "Heart disease",
                "Family history of kidney disease",
                "Age over 60",
                "Obesity",
                "Smoking",
                "Prolonged use of NSAIDs"
            ],
            "treatments": [
                "Blood pressure medications - ACE inhibitors, ARBs",
                "Diabetes management",
                "Cholesterol-lowering medications - Statins",
                "Phosphate binders",
                "Erythropoietin - For anemia",
                "Low-protein, low-sodium diet",
                "Dialysis - For advanced stages",
                "Kidney transplant - For end-stage disease"
            ],
            "care_guidelines": [
                "Control blood pressure and blood sugar",
                "Follow renal diet (low protein, sodium, potassium)",
                "Take medications as prescribed",
                "Stay hydrated appropriately",
                "Avoid NSAIDs and certain medications",
                "Monitor kidney function regularly",
                "Maintain healthy weight",
                "Exercise regularly as tolerated",
                "Avoid smoking",
                "Limit alcohol consumption"
            ],
            "complications": [
                "End-stage renal disease",
                "Cardiovascular disease",
                "Anemia",
                "Bone disease",
                "Electrolyte imbalances"
            ]
        },
        "stroke": {
            "name": "Stroke (Cerebrovascular Accident)",
            "category": "Neurological",
            "description": "A medical emergency where blood flow to part of the brain is interrupted, causing brain cell death and potential disability.",
            "symptoms": [
                "Sudden numbness or weakness (face, arm, leg)",
                "Confusion or trouble speaking",
                "Trouble seeing in one or both eyes",
                "Difficulty walking or loss of balance",
                "Severe headache with no cause",
                "FAST: Face drooping, Arm weakness, Speech difficulty, Time to call 911"
            ],
            "risk_factors": [
                "High blood pressure",
                "Smoking",
                "Diabetes",
                "High cholesterol",
                "Atrial fibrillation",
                "Obesity",
                "Family history",
                "Age over 55"
            ],
            "treatments": [
                "Emergency: tPA (clot-busting drug) if ischemic stroke",
                "Antiplatelet drugs - Aspirin, clopidogrel",
                "Anticoagulants - Warfarin, newer DOACs",
                "Blood pressure medications",
                "Statins for cholesterol",
                "Physical therapy for rehabilitation",
                "Occupational therapy",
                "Speech therapy",
                "Carotid endarterectomy (if indicated)"
            ],
            "care_guidelines": [
                "Take prevention medications consistently",
                "Control blood pressure strictly",
                "Manage diabetes effectively",
                "Attend rehabilitation sessions",
                "Practice exercises at home",
                "Modify home for safety",
                "Quit smoking immediately",
                "Limit alcohol",
                "Eat heart-healthy diet",
                "Know warning signs of another stroke"
            ],
            "complications": [
                "Paralysis or loss of muscle movement",
                "Difficulty speaking or swallowing",
                "Memory loss or cognitive problems",
                "Emotional problems and depression",
                "Chronic pain",
                "Risk of another stroke"
            ]
        },
        "parkinsons_disease": {
            "name": "Parkinson's Disease",
            "category": "Neurological",
            "description": "A progressive nervous system disorder affecting movement, causing tremors, stiffness, and difficulty with balance and coordination.",
            "symptoms": [
                "Tremor in hands, arms, legs, or jaw",
                "Stiffness of limbs and trunk",
                "Slowness of movement (bradykinesia)",
                "Impaired balance and coordination",
                "Shuffling walk",
                "Reduced facial expressions",
                "Soft or slurred speech",
                "Writing changes (smaller handwriting)",
                "Sleep disturbances",
                "Depression and anxiety"
            ],
            "risk_factors": [
                "Age (onset typically after 60)",
                "Male gender",
                "Genetics (family history)",
                "Environmental toxin exposure",
                "Head trauma"
            ],
            "treatments": [
                "Levodopa/carbidopa - Most effective medication",
                "Dopamine agonists - Pramipexole, ropinirole",
                "MAO-B inhibitors - Selegiline, rasagiline",
                "COMT inhibitors - Entacapone",
                "Anticholinergics - For tremor",
                "Physical therapy",
                "Occupational therapy",
                "Speech therapy",
                "Deep brain stimulation - For advanced cases"
            ],
            "care_guidelines": [
                "Take medications on strict schedule",
                "Stay physically active with regular exercise",
                "Work with physical therapist",
                "Practice balance and gait training",
                "Maintain good posture",
                "Perform speech exercises",
                "Eat balanced diet with adequate fiber",
                "Stay socially engaged",
                "Join support groups",
                "Modify home for safety (remove fall hazards)"
            ],
            "complications": [
                "Cognitive problems and dementia",
                "Depression and emotional changes",
                "Swallowing problems",
                "Sleep disorders",
                "Falls and injuries"
            ]
        },
        "alzheimers_disease": {
            "name": "Alzheimer's Disease",
            "category": "Neurological",
            "description": "A progressive brain disorder causing memory loss, confusion, and changes in behavior, eventually affecting daily functioning.",
            "symptoms": [
                "Memory loss affecting daily activities",
                "Difficulty planning or solving problems",
                "Confusion with time or place",
                "Trouble understanding visual images",
                "Problems with words in speaking or writing",
                "Misplacing things",
                "Poor or decreased judgment",
                "Withdrawal from social activities",
                "Changes in mood and personality",
                "Difficulty completing familiar tasks"
            ],
            "risk_factors": [
                "Age (over 65)",
                "Family history and genetics",
                "Down syndrome",
                "Head trauma",
                "Cardiovascular disease",
                "Obesity",
                "Diabetes",
                "Smoking",
                "Low education level"
            ],
            "treatments": [
                "Cholinesterase inhibitors - Donepezil (Aricept), rivastigmine",
                "Memantine (Namenda) - For moderate to severe",
                "Aducanumab (Aduhelm) - New amyloid-targeting therapy",
                "Cognitive stimulation therapy",
                "Reality orientation therapy",
                "Reminiscence therapy",
                "Treatment of behavioral symptoms",
                "Support for caregivers"
            ],
            "care_guidelines": [
                "Establish daily routines",
                "Keep environment simple and familiar",
                "Use memory aids (calendars, lists, labels)",
                "Encourage physical activity",
                "Provide mental stimulation",
                "Ensure safety at home (locks, alarms)",
                "Maintain social connections",
                "Manage other health conditions",
                "Plan for future care needs",
                "Support and educate caregivers"
            ],
            "complications": [
                "Complete inability to care for self",
                "Increased vulnerability to infections",
                "Difficulty swallowing (aspiration risk)",
                "Falls and injuries",
                "Caregiver burnout"
            ]
        },
        "hypothyroidism": {
            "name": "Hypothyroidism",
            "category": "Endocrine",
            "description": "A condition where the thyroid gland doesn't produce enough thyroid hormones, slowing body metabolism.",
            "symptoms": [
                "Fatigue and weakness",
                "Weight gain",
                "Cold intolerance",
                "Dry skin and hair",
                "Hair loss",
                "Constipation",
                "Depression",
                "Memory problems",
                "Slow heart rate",
                "Muscle aches and stiffness",
                "Heavy or irregular menstrual periods"
            ],
            "risk_factors": [
                "Female gender",
                "Age over 60",
                "Family history",
                "Autoimmune disease (Hashimoto's)",
                "Previous thyroid surgery or radioactive iodine",
                "Pregnancy (postpartum thyroiditis)",
                "Certain medications (lithium)"
            ],
            "treatments": [
                "Levothyroxine (Synthroid) - Thyroid hormone replacement",
                "Take medication on empty stomach",
                "Regular monitoring of TSH levels",
                "Adjustment of dose as needed",
                "Lifelong treatment usually required"
            ],
            "care_guidelines": [
                "Take thyroid medication consistently every morning",
                "Take on empty stomach (30-60 min before food)",
                "Avoid taking with calcium, iron supplements",
                "Regular blood tests to monitor TSH",
                "Maintain healthy diet and exercise",
                "Report symptoms of over/under medication",
                "Inform doctor of other medications",
                "Regular follow-ups every 6-12 months"
            ],
            "complications": [
                "Heart problems",
                "Mental health issues",
                "Peripheral neuropathy",
                "Infertility",
                "Myxedema (severe, life-threatening)"
            ]
        },
        "gerd": {
            "name": "GERD (Gastroesophageal Reflux Disease)",
            "category": "Gastrointestinal",
            "description": "A chronic digestive disease where stomach acid flows back into the esophagus, causing irritation and discomfort.",
            "symptoms": [
                "Heartburn (burning sensation in chest)",
                "Regurgitation of food or sour liquid",
                "Difficulty swallowing",
                "Chest pain",
                "Chronic cough",
                "Hoarseness or sore throat",
                "Feeling of lump in throat",
                "Disrupted sleep",
                "Worsening asthma symptoms"
            ],
            "risk_factors": [
                "Obesity",
                "Hiatal hernia",
                "Pregnancy",
                "Smoking",
                "Dry mouth",
                "Asthma",
                "Delayed stomach emptying",
                "Connective tissue disorders"
            ],
            "treatments": [
                "PPIs - Omeprazole (Prilosec), esomeprazole (Nexium)",
                "H2 blockers - Famotidine (Pepcid), ranitidine",
                "Antacids - For quick relief",
                "Lifestyle modifications",
                "Weight loss if overweight",
                "Elevate head of bed",
                "Avoid trigger foods",
                "Fundoplication surgery - For severe cases"
            ],
            "care_guidelines": [
                "Eat smaller, more frequent meals",
                "Avoid foods that trigger symptoms (spicy, fatty, acidic)",
                "Don't lie down within 3 hours of eating",
                "Elevate head of bed 6-8 inches",
                "Maintain healthy weight",
                "Quit smoking",
                "Limit alcohol and caffeine",
                "Avoid tight-fitting clothing",
                "Take medications as prescribed",
                "Chew food thoroughly"
            ],
            "complications": [
                "Esophagitis",
                "Esophageal stricture",
                "Barrett's esophagus",
                "Esophageal cancer (rare)",
                "Respiratory problems"
            ]
        },
        "ibs": {
            "name": "IBS (Irritable Bowel Syndrome)",
            "category": "Gastrointestinal",
            "description": "A common disorder affecting the large intestine, causing cramping, abdominal pain, bloating, gas, diarrhea, and constipation.",
            "symptoms": [
                "Abdominal pain and cramping",
                "Bloating and gas",
                "Diarrhea, constipation, or alternating both",
                "Mucus in stool",
                "Feeling of incomplete bowel movement",
                "Urgency to have bowel movement",
                "Symptoms worsen with stress or certain foods"
            ],
            "risk_factors": [
                "Young age (under 50)",
                "Female gender",
                "Family history",
                "Mental health issues (anxiety, depression)",
                "History of physical or sexual abuse",
                "Severe infection or gastroenteritis"
            ],
            "treatments": [
                "Fiber supplements - Psyllium (Metamucil)",
                "Anti-diarrheal - Loperamide (Imodium)",
                "Antispasmodics - Dicyclomine, hyoscyamine",
                "Antidepressants - For pain and motility",
                "Alosetron - For severe IBS-D (women only)",
                "Lubiprostone - For IBS-C",
                "Probiotics",
                "Low FODMAP diet",
                "Cognitive behavioral therapy",
                "Stress management"
            ],
            "care_guidelines": [
                "Keep food diary to identify triggers",
                "Follow low FODMAP diet if recommended",
                "Eat regular meals at consistent times",
                "Stay hydrated",
                "Exercise regularly",
                "Manage stress through relaxation techniques",
                "Get adequate sleep",
                "Limit caffeine and alcohol",
                "Avoid gas-producing foods",
                "Consider probiotics"
            ],
            "complications": [
                "Poor quality of life",
                "Depression and anxiety",
                "Hemorrhoids (from diarrhea or constipation)",
                "Malnutrition (if avoiding many foods)"
            ]
        },
        "fibromyalgia": {
            "name": "Fibromyalgia",
            "category": "Musculoskeletal/Chronic Pain",
            "description": "A disorder characterized by widespread musculoskeletal pain accompanied by fatigue, sleep, memory, and mood issues.",
            "symptoms": [
                "Widespread pain lasting 3+ months",
                "Fatigue despite adequate sleep",
                "Cognitive difficulties (fibro fog)",
                "Headaches and migraines",
                "Depression and anxiety",
                "Sleep disturbances",
                "Tender points on body",
                "Numbness or tingling in extremities",
                "Sensitivity to temperature, light, sound",
                "Digestive problems"
            ],
            "risk_factors": [
                "Female gender",
                "Family history",
                "Rheumatic disease (RA, lupus)",
                "Physical or emotional trauma",
                "Infections",
                "Age (middle-aged)"
            ],
            "treatments": [
                "Duloxetine (Cymbalta) - SNRI approved for fibromyalgia",
                "Pregabalin (Lyrica) - Anti-seizure medication",
                "Gabapentin (Neurontin)",
                "Amitriptyline - Low-dose antidepressant",
                "Pain relievers - Acetaminophen, NSAIDs (limited benefit)",
                "Physical therapy",
                "Cognitive behavioral therapy",
                "Stress reduction techniques",
                "Aerobic exercise",
                "Occupational therapy"
            ],
            "care_guidelines": [
                "Maintain regular sleep schedule",
                "Practice good sleep hygiene",
                "Exercise regularly (start slow, build gradually)",
                "Practice stress management (yoga, meditation)",
                "Pace activities to avoid overexertion",
                "Apply heat or cold to painful areas",
                "Get massage therapy",
                "Maintain healthy lifestyle",
                "Join support groups",
                "Keep pain diary"
            ],
            "complications": [
                "Reduced quality of life",
                "Depression and anxiety",
                "Hospitalization rates higher than general population",
                "Work disability in some cases"
            ]
        },
        "lupus": {
            "name": "Systemic Lupus Erythematosus (SLE)",
            "category": "Autoimmune",
            "description": "An autoimmune disease where the immune system attacks its own tissues, affecting multiple organs including skin, joints, kidneys, and brain.",
            "symptoms": [
                "Butterfly-shaped facial rash",
                "Photosensitivity (sun sensitivity)",
                "Joint pain and swelling",
                "Fatigue and fever",
                "Skin lesions",
                "Fingers turn white or blue in cold (Raynaud's)",
                "Shortness of breath",
                "Chest pain",
                "Dry eyes",
                "Headaches and confusion",
                "Memory loss"
            ],
            "risk_factors": [
                "Female gender (9:1 ratio)",
                "Age 15-45 (child-bearing years)",
                "Race (more common in African Americans, Hispanics, Asians)",
                "Family history",
                "Certain medications (drug-induced lupus)"
            ],
            "treatments": [
                "NSAIDs - For pain and inflammation",
                "Antimalarial drugs - Hydroxychloroquine (Plaquenil)",
                "Corticosteroids - Prednisone",
                "Immunosuppressants - Azathioprine, methotrexate",
                "Biologics - Belimumab (Benlysta)",
                "Cyclophosphamide - For severe lupus",
                "Sun protection",
                "Lifestyle modifications"
            ],
            "care_guidelines": [
                "Take medications consistently",
                "Protect skin from sun (SPF 30+, protective clothing)",
                "Get adequate rest",
                "Exercise regularly but don't overdo",
                "Eat balanced, anti-inflammatory diet",
                "Don't smoke",
                "Manage stress",
                "Regular monitoring with rheumatologist",
                "Report new symptoms promptly",
                "Get regular vaccinations (avoid live vaccines during immunosuppression)"
            ],
            "complications": [
                "Kidney failure",
                "Heart disease",
                "Stroke",
                "Blood clotting problems",
                "Pregnancy complications",
                "Increased infection risk",
                "Bone death (avascular necrosis)"
            ]
        },
        "psoriasis": {
            "name": "Psoriasis",
            "category": "Autoimmune/Dermatological",
            "description": "A chronic autoimmune skin condition causing rapid buildup of skin cells, resulting in scaling on the skin's surface.",
            "symptoms": [
                "Red patches covered with thick silvery scales",
                "Dry, cracked skin that may bleed",
                "Itching, burning, or soreness",
                "Thickened or ridged nails",
                "Swollen and stiff joints (psoriatic arthritis)",
                "Small scaling spots (in children)",
                "Cycles of flares and remission"
            ],
            "risk_factors": [
                "Family history",
                "Smoking",
                "Obesity",
                "Stress",
                "Infections (strep throat)",
                "Certain medications (lithium, beta-blockers)",
                "Alcohol consumption"
            ],
            "treatments": [
                "Topical corticosteroids",
                "Vitamin D analogues - Calcipotriene",
                "Topical retinoids - Tazarotene",
                "Salicylic acid",
                "Moisturizers and emollients",
                "Phototherapy (UV light treatment)",
                "Methotrexate - Systemic treatment",
                "Cyclosporine - Immunosuppressant",
                "Biologics - TNF inhibitors, IL-17/IL-23 inhibitors",
                "Oral retinoids - Acitretin"
            ],
            "care_guidelines": [
                "Apply moisturizers regularly",
                "Take short, warm baths with oatmeal",
                "Apply topicals as prescribed",
                "Expose skin to small amounts of sunlight",
                "Avoid triggers (stress, infections, skin injuries)",
                "Don't pick or scratch plaques",
                "Limit alcohol consumption",
                "Quit smoking",
                "Maintain healthy weight",
                "Manage stress through relaxation techniques"
            ],
            "complications": [
                "Psoriatic arthritis",
                "Eye conditions",
                "Obesity",
                "Type 2 diabetes",
                "Cardiovascular disease",
                "Depression and low self-esteem"
            ]
        },
        "migraine": {
            "name": "Migraine",
            "category": "Neurological",
            "description": "A neurological condition causing intense, debilitating headaches often accompanied by nausea, vomiting, and sensitivity to light and sound.",
            "symptoms": [
                "Intense throbbing or pulsing headache",
                "Usually one-sided head pain",
                "Nausea and vomiting",
                "Sensitivity to light and sound",
                "Visual disturbances (aura) - flashing lights, zigzag lines",
                "Dizziness",
                "Fatigue",
                "Mood changes",
                "Difficulty concentrating",
                "Duration: 4-72 hours if untreated"
            ],
            "risk_factors": [
                "Family history",
                "Female gender",
                "Age (teens to 50s)",
                "Hormonal changes",
                "Stress",
                "Sleep disturbances",
                "Certain foods and drinks",
                "Weather changes"
            ],
            "treatments": [
                "Acute treatment - Triptans (sumatriptan, rizatriptan)",
                "NSAIDs - Ibuprofen, naproxen",
                "Anti-nausea medications",
                "Preventive medications - Beta-blockers, antidepressants",
                "CGRP inhibitors - Aimovig, Emgality (preventive)",
                "Botox injections - For chronic migraine",
                "Nerve stimulation devices",
                "Lifestyle modifications",
                "Cognitive behavioral therapy"
            ],
            "care_guidelines": [
                "Keep migraine diary to identify triggers",
                "Maintain regular sleep schedule",
                "Eat regular meals (don't skip)",
                "Stay hydrated",
                "Exercise regularly",
                "Manage stress effectively",
                "Avoid known triggers (certain foods, drinks)",
                "Limit caffeine",
                "Take preventive medication as prescribed",
                "Use acute medication early in attack"
            ],
            "complications": [
                "Chronic migraine (15+ days per month)",
                "Medication overuse headache",
                "Migrainous infarction (stroke)",
                "Depression and anxiety",
                "Reduced quality of life"
            ]
        },
        "sleep_apnea": {
            "name": "Obstructive Sleep Apnea",
            "category": "Respiratory/Sleep Disorder",
            "description": "A sleep disorder where breathing repeatedly stops and starts due to throat muscle relaxation blocking the airway during sleep.",
            "symptoms": [
                "Loud snoring",
                "Gasping for air during sleep",
                "Morning headaches",
                "Excessive daytime sleepiness",
                "Difficulty concentrating",
                "Irritability and mood changes",
                "Dry mouth or sore throat upon waking",
                "Night sweats",
                "Decreased libido",
                "Witnessed breathing pauses during sleep"
            ],
            "risk_factors": [
                "Obesity",
                "Large neck circumference",
                "Male gender",
                "Older age",
                "Family history",
                "Nasal congestion",
                "Smoking",
                "Alcohol or sedative use"
            ],
            "treatments": [
                "CPAP (Continuous Positive Airway Pressure) - Gold standard",
                "BiPAP - For those who can't tolerate CPAP",
                "Oral appliances - Mandibular advancement device",
                "Weight loss - Can significantly improve symptoms",
                "Positional therapy - Avoid sleeping on back",
                "Surgery - Uvulopalatopharyngoplasty (UPPP)",
                "Inspire therapy - Hypoglossal nerve stimulation",
                "Avoid alcohol and sedatives"
            ],
            "care_guidelines": [
                "Use CPAP every night for full sleep duration",
                "Maintain and clean CPAP equipment regularly",
                "Lose weight if overweight",
                "Sleep on side instead of back",
                "Avoid alcohol and sedatives before bed",
                "Treat nasal congestion",
                "Maintain regular sleep schedule",
                "Avoid smoking",
                "Follow up regularly with sleep specialist",
                "Report mask fitting issues promptly"
            ],
            "complications": [
                "Cardiovascular disease",
                "High blood pressure",
                "Type 2 diabetes",
                "Metabolic syndrome",
                "Liver problems",
                "Increased surgical complications",
                "Daytime fatigue and accidents"
            ]
        }
    }
    
    def __init__(self, collection_name: str = "medical_knowledge"):
        """Initialize the Medical Knowledge Base"""
        self.collection_name = collection_name
        
        # Initialize Qdrant client
        qdrant_url = os.getenv("QDRANT_URL", None)
        qdrant_api_key = os.getenv("QDRANT_API_KEY", None)
        
        if qdrant_url:
            logger.info(f"🔗 Connecting to Qdrant server at {qdrant_url}")
            self.client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)
        else:
            logger.info("💾 Using Qdrant in-memory mode for medical knowledge")
            self.client = QdrantClient(":memory:")
        
        # Initialize embedding model
        logger.info("🤖 Loading sentence transformer model for medical knowledge...")
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.embedding_dimension = 384
        
        # Create collection and populate
        self._setup_collection()
        self._populate_knowledge_base()
        logger.info("✅ Medical Knowledge Base initialized with {} conditions".format(
            len(self.MEDICAL_CONDITIONS)))
    
    def _setup_collection(self):
        """Create Qdrant collection if it doesn't exist"""
        try:
            collections = self.client.get_collections().collections
            collection_names = [col.name for col in collections]
            
            if self.collection_name not in collection_names:
                logger.info(f"📦 Creating medical knowledge collection: {self.collection_name}")
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.embedding_dimension,
                        distance=Distance.COSINE
                    )
                )
                logger.info("✅ Medical knowledge collection created successfully")
            else:
                logger.info(f"✅ Medical knowledge collection '{self.collection_name}' already exists")
                
        except Exception as e:
            logger.error(f"❌ Error setting up medical knowledge collection: {e}")
            raise
    
    def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding vector for text"""
        try:
            embedding = self.embedding_model.encode(text, convert_to_numpy=True)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"❌ Error generating embedding: {e}")
            raise
    
    def _create_searchable_content(self, condition_key: str, condition_data: Dict) -> str:
        """Create comprehensive searchable content from condition data"""
        parts = [
            f"Medical condition: {condition_data['name']}",
            f"Category: {condition_data['category']}",
            f"Description: {condition_data['description']}",
            f"Common symptoms include: {', '.join(condition_data['symptoms'][:5])}",
            f"Risk factors: {', '.join(condition_data['risk_factors'][:3])}",
            f"Treatments: {', '.join(condition_data['treatments'][:5])}",
            f"Care guidelines: {', '.join(condition_data['care_guidelines'][:3])}"
        ]
        return " ".join(parts)
    
    def _populate_knowledge_base(self):
        """Populate knowledge base with medical conditions"""
        try:
            # Check if already populated
            collection_info = self.client.get_collection(self.collection_name)
            if collection_info.points_count > 0:
                logger.info(f"📚 Knowledge base already populated with {collection_info.points_count} entries")
                return
            
            logger.info("📝 Populating medical knowledge base...")
            points = []
            
            for condition_key, condition_data in self.MEDICAL_CONDITIONS.items():
                # Create searchable content
                searchable_content = self._create_searchable_content(condition_key, condition_data)
                
                # Generate embedding
                embedding = self._generate_embedding(searchable_content)
                
                # Create point
                point = PointStruct(
                    id=str(uuid.uuid4()),
                    vector=embedding,
                    payload={
                        "condition_key": condition_key,
                        "name": condition_data["name"],
                        "category": condition_data["category"],
                        "description": condition_data["description"],
                        "symptoms": condition_data["symptoms"],
                        "risk_factors": condition_data["risk_factors"],
                        "treatments": condition_data["treatments"],
                        "care_guidelines": condition_data["care_guidelines"],
                        "complications": condition_data["complications"],
                        "searchable_content": searchable_content
                    }
                )
                points.append(point)
            
            # Batch insert
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            
            logger.info(f"✅ Successfully populated knowledge base with {len(points)} conditions")
            
        except Exception as e:
            logger.error(f"❌ Error populating knowledge base: {e}")
            raise
    
    def search_medical_knowledge(
        self,
        query: str,
        limit: int = 3
    ) -> List[Dict]:
        """
        Search medical knowledge base using semantic search
        
        Args:
            query: User's health question or search query
            limit: Number of top matches to return (default: 3)
            
        Returns:
            List of relevant medical conditions with confidence scores
        """
        try:
            # Generate embedding for query
            query_embedding = self._generate_embedding(query)
            
            # Search knowledge base
            search_results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=limit
            )
            
            # Store raw results for evidence tracking
            self._last_search_results = search_results.points
            
            # Format results
            results = []
            for result in search_results.points:
                results.append({
                    "condition_key": result.payload.get("condition_key"),
                    "name": result.payload.get("name"),
                    "category": result.payload.get("category"),
                    "description": result.payload.get("description"),
                    "symptoms": result.payload.get("symptoms", []),
                    "risk_factors": result.payload.get("risk_factors", []),
                    "treatments": result.payload.get("treatments", []),
                    "care_guidelines": result.payload.get("care_guidelines", []),
                    "complications": result.payload.get("complications", []),
                    "confidence_score": round(result.score, 3),
                    "relevance": "high" if result.score > 0.7 else "medium" if result.score > 0.5 else "low"
                })
            
            logger.info(f"✅ Found {len(results)} relevant conditions for query: '{query[:50]}...'")
            return results
            
        except Exception as e:
            logger.error(f"❌ Error searching medical knowledge: {e}")
            return []
    
    def get_condition_details(self, condition_key: str) -> Optional[Dict]:
        """Get detailed information about a specific condition"""
        return self.MEDICAL_CONDITIONS.get(condition_key)
    
    def list_all_conditions(self) -> List[Dict]:
        """Get list of all available conditions"""
        return [
            {
                "key": key,
                "name": data["name"],
                "category": data["category"],
                "description": data["description"]
            }
            for key, data in self.MEDICAL_CONDITIONS.items()
        ]
    
    def search_by_category(self, category: str) -> List[Dict]:
        """Get all conditions in a specific category"""
        return [
            {
                "key": key,
                "name": data["name"],
                "category": data["category"],
                "description": data["description"]
            }
            for key, data in self.MEDICAL_CONDITIONS.items()
            if data["category"].lower() == category.lower()
        ]


# Singleton instance
_medical_kb = None

def get_medical_knowledge_base() -> MedicalKnowledgeBase:
    """Get or create the singleton MedicalKnowledgeBase instance"""
    global _medical_kb
    if _medical_kb is None:
        _medical_kb = MedicalKnowledgeBase()
    return _medical_kb

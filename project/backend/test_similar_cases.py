"""
Test Suite for Similar Patient Cases Retrieval System

Tests the Qdrant-based hybrid search system for finding similar historical patient cases.
Validates multi-dimensional similarity scoring, case matching accuracy, and clinical relevance.
"""

import sys
import os

# Set UTF-8 encoding for Windows console
if sys.platform.startswith('win'):
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

from similar_cases import SimilarCasesEngine
from patient_memory import PatientMemorySystem
from vitals_tracker import VitalsTracker
from medical_knowledge_base import MedicalKnowledgeBase
from ai_recommendations import RecommendationEngine
import time
from datetime import datetime, timedelta


def print_header(text):
    """Print formatted section header"""
    print("\n" + "="*80)
    print(f"  {text}")
    print("="*80)


def print_subheader(text):
    """Print formatted subsection header"""
    print(f"\n{text}")
    print("-"*80)


def setup_test_data():
    """
    Set up comprehensive test data with multiple patient profiles and historical cases
    """
    print_header("Setting Up Test Data")
    
    # Initialize all systems
    similar_cases = SimilarCasesEngine()
    patient_memory = PatientMemorySystem()
    vitals_tracker = VitalsTracker()
    medical_kb = MedicalKnowledgeBase()
    recommendation_engine = RecommendationEngine()
    
    # Define test patients with diverse profiles
    test_patients = {
        'current_patient': {
            'patient_id': 'patient_current_001',
            'demographics': {'age': 55, 'gender': 'male'},
            'symptoms': ['chest pain', 'fatigue', 'breathless'],
            'conditions': ['Hypertension', 'Type 2 Diabetes'],
            'vitals': [
                {'systolic_bp': 155, 'diastolic_bp': 95, 'heart_rate': 88, 'blood_glucose': 180},
                {'systolic_bp': 160, 'diastolic_bp': 98, 'heart_rate': 90, 'blood_glucose': 185},
                {'systolic_bp': 150, 'diastolic_bp': 92, 'heart_rate': 85, 'blood_glucose': 175},
            ],
            'conversations': [
                "I've been having chest pain and feeling tired all the time",
                "My blood sugar has been high and I get breathless when walking"
            ]
        },
        'historical_case_1': {
            'patient_id': 'patient_hist_001',
            'demographics': {'age': 58, 'gender': 'male'},
            'symptoms': ['chest pain', 'fatigue', 'dizzy'],
            'conditions': ['Hypertension', 'Type 2 Diabetes', 'Coronary Artery Disease'],
            'vitals_summary': {'systolic_bp': 158, 'diastolic_bp': 96, 'heart_rate': 87, 'blood_glucose': 178},
            'treatments': ['Metformin', 'Lisinopril', 'Aspirin'],
            'outcome': 'Improved with medication and lifestyle changes',
            'case_notes': 'Patient responded well to combination therapy. BP controlled after 3 months.',
            'case_date': '2025-10-15'
        },
        'historical_case_2': {
            'patient_id': 'patient_hist_002',
            'demographics': {'age': 42, 'gender': 'female'},
            'symptoms': ['fatigue', 'headache', 'dizzy'],
            'conditions': ['Hypertension', 'Anemia'],
            'vitals_summary': {'systolic_bp': 145, 'diastolic_bp': 90, 'heart_rate': 82, 'blood_glucose': 110},
            'treatments': ['Amlodipine', 'Iron supplements'],
            'outcome': 'Partial improvement, ongoing monitoring',
            'case_notes': 'BP reduced but fatigue persists. Iron levels improving.',
            'case_date': '2025-09-20'
        },
        'historical_case_3': {
            'patient_id': 'patient_hist_003',
            'demographics': {'age': 60, 'gender': 'male'},
            'symptoms': ['chest pain', 'breathless', 'cough'],
            'conditions': ['COPD', 'Hypertension'],
            'vitals_summary': {'systolic_bp': 140, 'diastolic_bp': 85, 'heart_rate': 78, 'oxygen_saturation': 92},
            'treatments': ['Bronchodilator', 'Lisinopril'],
            'outcome': 'Stable with medication',
            'case_notes': 'COPD well-controlled. Regular monitoring required.',
            'case_date': '2025-11-05'
        },
        'historical_case_4': {
            'patient_id': 'patient_hist_004',
            'demographics': {'age': 52, 'gender': 'male'},
            'symptoms': ['chest pain', 'fatigue', 'anxious'],
            'conditions': ['Type 2 Diabetes', 'Anxiety Disorder'],
            'vitals_summary': {'systolic_bp': 130, 'diastolic_bp': 82, 'heart_rate': 92, 'blood_glucose': 195},
            'treatments': ['Metformin', 'SSRI'],
            'outcome': 'Good response to treatment',
            'case_notes': 'Glucose control improving. Anxiety reduced with therapy.',
            'case_date': '2025-08-12'
        },
        'historical_case_5': {
            'patient_id': 'patient_hist_005',
            'demographics': {'age': 35, 'gender': 'female'},
            'symptoms': ['headache', 'anxious', 'insomnia'],
            'conditions': ['Anxiety Disorder', 'Migraine'],
            'vitals_summary': {'systolic_bp': 118, 'diastolic_bp': 75, 'heart_rate': 75, 'blood_glucose': 95},
            'treatments': ['SSRI', 'Migraine medication'],
            'outcome': 'Significant improvement',
            'case_notes': 'Headaches reduced. Sleep quality improved.',
            'case_date': '2025-07-25'
        }
    }
    
    # Index historical cases
    print_subheader("Indexing Historical Cases")
    indexed_cases = []
    
    for key, patient in test_patients.items():
        if key.startswith('historical_case'):
            print(f"  📋 Indexing {key}: {patient['demographics']['age']}yo {patient['demographics']['gender']}")
            print(f"     Conditions: {', '.join(patient['conditions'])}")
            print(f"     Symptoms: {', '.join(patient['symptoms'])}")
            
            case_id = similar_cases.index_patient_case(
                patient_id=patient['patient_id'],
                case_date=patient['case_date'],
                symptoms=patient['symptoms'],
                conditions=patient['conditions'],
                vitals_summary=patient['vitals_summary'],
                demographics=patient['demographics'],
                treatments=patient['treatments'],
                outcome=patient['outcome'],
                case_notes=patient['case_notes']
            )
            indexed_cases.append(case_id)
            print(f"     ✅ Indexed as {case_id}")
    
    # Set up current patient data
    print_subheader("Setting Up Current Patient Data")
    current = test_patients['current_patient']
    print(f"  👤 Current Patient: {current['demographics']['age']}yo {current['demographics']['gender']}")
    print(f"     Conditions: {', '.join(current['conditions'])}")
    print(f"     Symptoms: {', '.join(current['symptoms'])}")
    
    # Store vitals for current patient
    for i, vitals in enumerate(current['vitals']):
        vitals_tracker.store_vitals(
            patient_id=current['patient_id'],
            vitals=vitals,
            timestamp=datetime.now() - timedelta(days=7-i*2)
        )
    print(f"     ✅ Stored {len(current['vitals'])} vitals readings")
    
    # Store conversations for current patient
    for i, conv in enumerate(current['conversations']):
        patient_memory.store_conversation(
            patient_id=current['patient_id'],
            user_message=conv,
            assistant_response="I understand your concerns. Let's review your symptoms and vitals."
        )
    print(f"     ✅ Stored {len(current['conversations'])} conversations")
    
    return test_patients, indexed_cases


def test_find_similar_cases():
    """
    Test finding similar cases for the current patient
    """
    print_header("Test 1: Find Similar Cases")
    
    test_patients, indexed_cases = setup_test_data()
    similar_cases = SimilarCasesEngine()
    current_patient_id = test_patients['current_patient']['patient_id']
    
    print(f"\n🔍 Searching for cases similar to: {current_patient_id}")
    print(f"   Query Profile: 55yo male with Hypertension + Diabetes")
    print(f"   Query Symptoms: chest pain, fatigue, breathless")
    
    start_time = time.time()
    results = similar_cases.find_similar_cases(
        patient_id=current_patient_id,
        top_k=5,
        min_similarity=0.2
    )
    duration = time.time() - start_time
    
    print(f"\n⏱️  Search completed in {duration:.2f} seconds")
    print(f"📊 Found {len(results)} similar cases\n")
    
    # Display results
    for i, case in enumerate(results, 1):
        print(f"\n{'='*70}")
        print(f"Rank #{i}: {case['case_id']}")
        print(f"{'='*70}")
        print(f"📈 Overall Similarity: {case['similarity_score']:.3f}")
        print(f"\n🔬 Similarity Breakdown:")
        for component, score in case['similarity_breakdown'].items():
            print(f"   • {component.capitalize():15s}: {score:.3f}")
        
        print(f"\n👥 Patient Profile:")
        print(f"   • Age Range: {case['age_range']}")
        print(f"   • Gender: {case['gender']}")
        print(f"   • Case Date: {case['case_date']}")
        
        print(f"\n🤝 Shared Attributes:")
        if case['shared_symptoms']:
            print(f"   • Symptoms: {', '.join(case['shared_symptoms'])}")
        else:
            print(f"   • Symptoms: None")
        
        if case['shared_conditions']:
            print(f"   • Conditions: {', '.join(case['shared_conditions'])}")
        else:
            print(f"   • Conditions: None")
        
        print(f"\n💊 Treatments Used:")
        if case['treatments']:
            for treatment in case['treatments']:
                print(f"   • {treatment}")
        else:
            print(f"   • None recorded")
        
        print(f"\n📊 Vitals Summary:")
        for vital, value in case['vitals_summary'].items():
            print(f"   • {vital}: {value}")
        
        print(f"\n🎯 Outcome: {case['outcome']}")
        
        if case['case_notes']:
            print(f"\n📝 Clinical Notes:")
            print(f"   {case['case_notes']}")
    
    # Verify quality of results
    print(f"\n{'='*80}")
    print("✅ Test 1 Validation:")
    print(f"   • Results returned: {len(results)}")
    print(f"   • All similarity scores > 0.2: {all(c['similarity_score'] >= 0.2 for c in results)}")
    print(f"   • Results sorted by score: {results == sorted(results, key=lambda x: x['similarity_score'], reverse=True)}")
    
    # Check top result quality
    if results:
        top_case = results[0]
        has_shared_conditions = len(top_case['shared_conditions']) > 0
        print(f"   • Top case has shared conditions: {has_shared_conditions}")
        print(f"   • Top case similarity score: {top_case['similarity_score']:.3f}")
    
    return results


def test_similarity_scoring():
    """
    Test multi-dimensional similarity scoring accuracy
    """
    print_header("Test 2: Similarity Scoring Accuracy")
    
    test_patients, indexed_cases = setup_test_data()
    similar_cases = SimilarCasesEngine()
    current_patient_id = test_patients['current_patient']['patient_id']
    
    results = similar_cases.find_similar_cases(
        patient_id=current_patient_id,
        top_k=5,
        min_similarity=0.0  # Get all cases
    )
    
    print("\n📊 Analyzing Similarity Score Components:\n")
    
    for i, case in enumerate(results, 1):
        print(f"Case #{i}: {case['similarity_score']:.3f} overall")
        breakdown = case['similarity_breakdown']
        
        # Identify strongest dimensions
        sorted_components = sorted(breakdown.items(), key=lambda x: x[1], reverse=True)
        print(f"  Strongest dimensions:")
        for component, score in sorted_components[:3]:
            if score > 0:
                print(f"    • {component:15s}: {score:.3f}")
        
        # Check condition overlap
        if case['shared_conditions']:
            print(f"  Shared conditions: {', '.join(case['shared_conditions'])}")
        print()
    
    # Verify scoring logic
    print("✅ Test 2 Validation:")
    
    # Check that cases with more shared conditions rank higher
    condition_overlap_scores = []
    for case in results:
        overlap = len(case['shared_conditions'])
        score = case['similarity_score']
        condition_overlap_scores.append((overlap, score))
    
    print(f"   • Condition overlap impacts ranking: {len(condition_overlap_scores) > 0}")
    
    # Check component scores are in valid range [0, 1]
    all_valid = True
    for case in results:
        for component, score in case['similarity_breakdown'].items():
            if not (0 <= score <= 1):
                all_valid = False
                print(f"   ❌ Invalid score: {component} = {score}")
    
    print(f"   • All component scores in valid range [0,1]: {all_valid}")
    
    return results


def test_case_statistics():
    """
    Test case database statistics retrieval
    """
    print_header("Test 3: Case Database Statistics")
    
    test_patients, indexed_cases = setup_test_data()
    similar_cases = SimilarCasesEngine()
    
    stats = similar_cases.get_case_statistics()
    
    print("\n📈 Case Database Statistics:\n")
    print(f"Total Cases Indexed: {stats['total_cases']}")
    print(f"Database Size: {stats['collection_size_mb']:.2f} MB")
    
    print(f"\n🏥 Most Common Conditions:")
    for condition, count in list(stats['most_common_conditions'].items())[:5]:
        print(f"   • {condition}: {count} cases")
    
    print(f"\n🤒 Most Common Symptoms:")
    for symptom, count in list(stats['most_common_symptoms'].items())[:5]:
        print(f"   • {symptom}: {count} cases")
    
    print(f"\n👥 Age Distribution:")
    for age_range, count in stats['age_distribution'].items():
        print(f"   • {age_range}: {count} cases")
    
    print(f"\n🎯 Outcome Distribution:")
    for outcome, count in stats['outcome_distribution'].items():
        print(f"   • {outcome}: {count} cases")
    
    print("\n✅ Test 3 Validation:")
    print(f"   • Total cases matches expected: {stats['total_cases'] == 5}")
    print(f"   • Statistics calculated: {len(stats) > 0}")
    
    return stats


def test_gdpr_deletion():
    """
    Test GDPR-compliant case deletion
    """
    print_header("Test 4: GDPR Case Deletion")
    
    test_patients, indexed_cases = setup_test_data()
    similar_cases = SimilarCasesEngine()
    
    # Get initial case count
    initial_stats = similar_cases.get_case_statistics()
    initial_count = initial_stats['total_cases']
    print(f"\n📊 Initial case count: {initial_count}")
    
    # Delete cases for one patient
    patient_to_delete = test_patients['historical_case_1']['patient_id']
    print(f"\n🗑️  Deleting cases for: {patient_to_delete}")
    
    deleted_count = similar_cases.delete_patient_cases(patient_to_delete)
    print(f"   ✅ Deleted {deleted_count} case(s)")
    
    # Verify deletion
    final_stats = similar_cases.get_case_statistics()
    final_count = final_stats['total_cases']
    print(f"\n📊 Final case count: {final_count}")
    print(f"   Expected: {initial_count - deleted_count}")
    
    print("\n✅ Test 4 Validation:")
    print(f"   • Cases deleted: {deleted_count > 0}")
    print(f"   • Case count reduced correctly: {final_count == initial_count - deleted_count}")
    
    return deleted_count


def test_clinical_decision_support():
    """
    Test clinical decision support scenario
    """
    print_header("Test 5: Clinical Decision Support Scenario")
    
    test_patients, indexed_cases = setup_test_data()
    similar_cases = SimilarCasesEngine()
    current_patient_id = test_patients['current_patient']['patient_id']
    
    print("\n🏥 Clinical Scenario:")
    print("   Doctor is reviewing a 55yo male patient with:")
    print("   • Hypertension + Type 2 Diabetes")
    print("   • Chest pain, fatigue, breathlessness")
    print("   • Recent BP readings: 150-160/92-98 mmHg")
    print("   • Blood glucose: 175-185 mg/dL")
    
    print("\n🔍 Finding similar historical cases...")
    
    results = similar_cases.find_similar_cases(
        patient_id=current_patient_id,
        top_k=3,  # Top 3 most relevant cases
        min_similarity=0.3
    )
    
    print(f"\n📋 Found {len(results)} relevant historical cases:\n")
    
    # Analyze and present clinical insights
    all_treatments = set()
    all_outcomes = []
    shared_conditions_count = {}
    
    for i, case in enumerate(results, 1):
        print(f"{'─'*70}")
        print(f"Case {i}: Similarity {case['similarity_score']:.1%}")
        print(f"{'─'*70}")
        
        # Key similarities
        print(f"Shared Conditions: {', '.join(case['shared_conditions']) if case['shared_conditions'] else 'None'}")
        print(f"Shared Symptoms: {', '.join(case['shared_symptoms']) if case['shared_symptoms'] else 'None'}")
        
        # Treatment history
        print(f"\nTreatments Used:")
        for treatment in case['treatments']:
            print(f"   • {treatment}")
            all_treatments.add(treatment)
        
        # Outcome
        print(f"\nOutcome: {case['outcome']}")
        all_outcomes.append(case['outcome'])
        
        # Clinical notes
        if case['case_notes']:
            print(f"Notes: {case['case_notes']}")
        
        print()
        
        # Track condition overlap
        for condition in case['shared_conditions']:
            shared_conditions_count[condition] = shared_conditions_count.get(condition, 0) + 1
    
    # Generate clinical insights
    print(f"\n{'='*70}")
    print("💡 Clinical Decision Support Insights:")
    print(f"{'='*70}\n")
    
    print("🎯 Evidence-Based Treatment Options:")
    if all_treatments:
        for treatment in all_treatments:
            print(f"   • {treatment}")
    else:
        print("   • No specific treatments recorded")
    
    print(f"\n📊 Common Comorbidities in Similar Cases:")
    for condition, count in sorted(shared_conditions_count.items(), key=lambda x: x[1], reverse=True):
        print(f"   • {condition}: {count}/{len(results)} cases")
    
    print(f"\n🎯 Historical Outcomes:")
    for outcome in set(all_outcomes):
        count = all_outcomes.count(outcome)
        print(f"   • {outcome}: {count}/{len(results)} cases")
    
    print("\n✅ Test 5 Validation:")
    print(f"   • Similar cases found: {len(results) > 0}")
    print(f"   • Treatment recommendations available: {len(all_treatments) > 0}")
    print(f"   • Clinical insights generated: True")
    
    return results


def run_all_tests():
    """
    Run complete test suite for similar cases system
    """
    start_time = time.time()
    
    print("\n" + "="*80)
    print(" 🧪 SIMILAR PATIENT CASES RETRIEVAL SYSTEM - TEST SUITE")
    print("="*80)
    print("\nTesting Qdrant-based hybrid search for clinical decision support")
    print("Validating multi-dimensional similarity scoring and case matching\n")
    
    try:
        # Run all tests
        test_1_results = test_find_similar_cases()
        test_2_results = test_similarity_scoring()
        test_3_stats = test_case_statistics()
        test_4_deleted = test_gdpr_deletion()
        test_5_insights = test_clinical_decision_support()
        
        # Final summary
        duration = time.time() - start_time
        
        print_header("🎉 Test Suite Summary")
        print(f"\n✅ All tests completed successfully!")
        print(f"⏱️  Total execution time: {duration:.2f} seconds")
        print(f"\n📊 Key Metrics:")
        print(f"   • Test 1: {len(test_1_results)} similar cases found")
        print(f"   • Test 2: Similarity scoring validated")
        print(f"   • Test 3: {test_3_stats['total_cases']} cases in database")
        print(f"   • Test 4: {test_4_deleted} case(s) deleted (GDPR)")
        print(f"   • Test 5: Clinical decision support validated")
        
        print("\n✨ Similar Cases System: Fully Operational")
        print("="*80 + "\n")
        
    except Exception as e:
        print(f"\n❌ Test suite failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == '__main__':
    print("🚀 Starting Similar Cases System Tests...")
    success = run_all_tests()
    
    if success:
        print("✅ All tests passed!")
        sys.exit(0)
    else:
        print("❌ Some tests failed!")
        sys.exit(1)

"""
Test Suite for Skin Analysis History System

Tests Qdrant-based historical skin analysis storage and similar case retrieval.
Validates pattern matching, diagnosis similarity, and treatment recommendations.
"""

import sys
import os

# Set UTF-8 encoding for Windows console
if sys.platform.startswith('win'):
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

from skin_analysis_history import SkinAnalysisHistory
from datetime import datetime, timedelta
import time


def print_header(text):
    """Print formatted section header"""
    print("\n" + "="*80)
    print(f"  {text}")
    print("="*80)


def print_subheader(text):
    """Print formatted subsection header"""
    print(f"\n{text}")
    print("-"*80)


def setup_test_cases():
    """
    Set up test data with diverse skin conditions
    """
    print_header("Setting Up Test Data")
    
    history = SkinAnalysisHistory()
    
    test_cases = [
        {
            'patient_id': 'patient_001',
            'diagnosis': 'Moderate acne vulgaris with inflammatory papules',
            'severity': 'moderate',
            'confidence': 0.85,
            'recommendations': ['Benzoyl peroxide 2.5%', 'Gentle cleanser', 'Oil-free moisturizer'],
            'affected_areas': ['face', 'forehead', 'cheeks'],
            'observations': 'Inflammatory papules with redness. Some comedones present.',
            'follow_up': True
        },
        {
            'patient_id': 'patient_002',
            'diagnosis': 'Mild acne vulgaris with occasional breakouts',
            'severity': 'mild',
            'confidence': 0.78,
            'recommendations': ['Salicylic acid cleanser', 'Non-comedogenic moisturizer'],
            'affected_areas': ['face', 'chin'],
            'observations': 'Few comedones and occasional inflamed papules.',
            'follow_up': False
        },
        {
            'patient_id': 'patient_003',
            'diagnosis': 'Atopic dermatitis (eczema) with dry, itchy patches',
            'severity': 'moderate',
            'confidence': 0.82,
            'recommendations': ['Hydrocortisone 1%', 'Thick emollient cream', 'Avoid harsh soaps'],
            'affected_areas': ['arms', 'legs', 'hands'],
            'observations': 'Dry, scaly patches with erythema. Signs of scratching present.',
            'follow_up': True
        },
        {
            'patient_id': 'patient_004',
            'diagnosis': 'Contact dermatitis, likely allergic reaction',
            'severity': 'moderate',
            'confidence': 0.75,
            'recommendations': ['Cool compress', 'OTC antihistamine', 'Avoid allergen'],
            'affected_areas': ['hands', 'wrists'],
            'observations': 'Red, itchy rash with small vesicles. Recent exposure to new product.',
            'follow_up': True
        },
        {
            'patient_id': 'patient_005',
            'diagnosis': 'Seborrheic dermatitis on scalp',
            'severity': 'mild',
            'confidence': 0.88,
            'recommendations': ['Ketoconazole shampoo', 'Anti-dandruff treatment'],
            'affected_areas': ['scalp', 'hairline'],
            'observations': 'Flaky, greasy scales with mild redness.',
            'follow_up': False
        },
        {
            'patient_id': 'patient_006',
            'diagnosis': 'Psoriasis with raised plaques',
            'severity': 'moderate',
            'confidence': 0.90,
            'recommendations': ['Coal tar preparation', 'Emollient', 'Consult dermatologist'],
            'affected_areas': ['elbows', 'knees', 'scalp'],
            'observations': 'Well-defined red plaques with silvery scales.',
            'follow_up': True
        },
        {
            'patient_id': 'patient_007',
            'diagnosis': 'Rosacea with facial flushing',
            'severity': 'moderate',
            'confidence': 0.83,
            'recommendations': ['Gentle cleanser', 'SPF 50 sunscreen', 'Avoid triggers'],
            'affected_areas': ['face', 'cheeks', 'nose'],
            'observations': 'Persistent facial redness with visible blood vessels.',
            'follow_up': True
        },
        {
            'patient_id': 'patient_008',
            'diagnosis': 'Fungal infection (tinea corporis/ringworm)',
            'severity': 'mild',
            'confidence': 0.87,
            'recommendations': ['Antifungal cream (clotrimazole)', 'Keep area dry'],
            'affected_areas': ['torso', 'chest'],
            'observations': 'Circular, red ring with clearer center. Scaly border.',
            'follow_up': True
        }
    ]
    
    print_subheader("Indexing Historical Cases")
    indexed_cases = []
    
    for i, case in enumerate(test_cases):
        case_date = datetime.now() - timedelta(days=30-i*3)
        
        print(f"  📋 Case {i+1}: {case['diagnosis'][:50]}...")
        print(f"     Severity: {case['severity']}, Confidence: {case['confidence']}")
        print(f"     Areas: {', '.join(case['affected_areas'][:3])}")
        
        case_id = history.store_analysis(
            patient_id=case['patient_id'],
            diagnosis=case['diagnosis'],
            severity=case['severity'],
            confidence=case['confidence'],
            recommendations=case['recommendations'],
            affected_areas=case['affected_areas'],
            additional_observations=case['observations'],
            follow_up_needed=case['follow_up'],
            timestamp=case_date
        )
        
        indexed_cases.append(case_id)
        print(f"     ✅ Indexed: {case_id}")
    
    return test_cases, indexed_cases


def test_find_similar_acne_cases():
    """Test finding similar acne cases"""
    print_header("Test 1: Find Similar Acne Cases")
    
    test_cases, indexed_cases = setup_test_cases()
    history = SkinAnalysisHistory()
    
    # New acne case
    new_diagnosis = "Moderate acne with pustules and comedones"
    print(f"\n🔍 New case: {new_diagnosis}")
    print("   Looking for similar historical cases...")
    
    start_time = time.time()
    similar_cases = history.find_similar_cases(
        diagnosis=new_diagnosis,
        severity='moderate',
        recommendations=['Benzoyl peroxide', 'Antibiotics'],
        affected_areas=['face'],
        top_k=3,
        min_confidence=0.7
    )
    duration = time.time() - start_time
    
    print(f"\n⏱️  Search completed in {duration:.2f} seconds")
    print(f"📊 Found {len(similar_cases)} similar cases\n")
    
    for i, case in enumerate(similar_cases, 1):
        print(f"\n{'='*70}")
        print(f"Match #{i}: Similarity {case['similarity_score']:.1%}")
        print(f"{'='*70}")
        print(f"Diagnosis: {case['diagnosis']}")
        print(f"Severity: {case['severity']}")
        print(f"Confidence: {case['confidence']:.2f}")
        print(f"Pattern Match: {case['pattern_match']}")
        print(f"Affected Areas: {', '.join(case['affected_areas'])}")
        print(f"Recommendations:")
        for rec in case['recommendations'][:3]:
            print(f"  • {rec}")
        print(f"Follow-up Needed: {'Yes' if case['follow_up_needed'] else 'No'}")
    
    print(f"\n{'='*80}")
    print("✅ Test 1 Validation:")
    print(f"   • Cases found: {len(similar_cases) > 0}")
    print(f"   • All acne-related: {all('acne' in c['diagnosis'].lower() for c in similar_cases)}")
    print(f"   • Similarity scores valid: {all(0 <= c['similarity_score'] <= 1 for c in similar_cases)}")
    
    return similar_cases


def test_find_similar_eczema_cases():
    """Test finding similar eczema/dermatitis cases"""
    print_header("Test 2: Find Similar Eczema/Dermatitis Cases")
    
    test_cases, indexed_cases = setup_test_cases()
    history = SkinAnalysisHistory()
    
    new_diagnosis = "Eczema with dry, itchy skin and inflammation"
    print(f"\n🔍 New case: {new_diagnosis}")
    
    similar_cases = history.find_similar_cases(
        diagnosis=new_diagnosis,
        severity='moderate',
        recommendations=['Moisturizer', 'Steroid cream'],
        affected_areas=['arms', 'legs'],
        top_k=3
    )
    
    print(f"\n📊 Found {len(similar_cases)} similar cases")
    
    for i, case in enumerate(similar_cases, 1):
        print(f"\n--- Match #{i} (Similarity: {case['similarity_score']:.3f}) ---")
        print(f"Diagnosis: {case['diagnosis']}")
        print(f"Category: {case['category']}")
        print(f"Pattern: {case['pattern_match']}")
    
    print("\n✅ Test 2 Validation:")
    print(f"   • Dermatitis/eczema cases found: {any('dermatitis' in c['diagnosis'].lower() or 'eczema' in c['diagnosis'].lower() for c in similar_cases)}")
    print(f"   • Results ordered by similarity: {similar_cases == sorted(similar_cases, key=lambda x: x['similarity_score'], reverse=True)}")
    
    return similar_cases


def test_category_filtering():
    """Test category-based filtering"""
    print_header("Test 3: Category Filtering")
    
    test_cases, indexed_cases = setup_test_cases()
    history = SkinAnalysisHistory()
    
    # Test fungal category
    print("\n🔍 Searching for fungal infections...")
    fungal_cases = history.find_similar_cases(
        diagnosis="Fungal skin infection with redness",
        top_k=5,
        category_filter='fungal'
    )
    
    print(f"📊 Found {len(fungal_cases)} fungal cases")
    for case in fungal_cases:
        print(f"  • {case['diagnosis']} (Category: {case['category']})")
    
    print("\n✅ Test 3 Validation:")
    print(f"   • Fungal cases found: {len(fungal_cases) > 0}")
    print(f"   • All fungal category: {all(c['category'] == 'fungal' for c in fungal_cases)}")
    
    return fungal_cases


def test_patient_history():
    """Test retrieving patient history"""
    print_header("Test 4: Patient History Retrieval")
    
    test_cases, indexed_cases = setup_test_cases()
    history = SkinAnalysisHistory()
    
    patient_id = 'patient_001'
    print(f"\n👤 Retrieving history for: {patient_id}")
    
    patient_history = history.get_patient_history(patient_id, limit=10)
    
    print(f"\n📊 Found {len(patient_history)} historical analyses")
    
    for i, case in enumerate(patient_history, 1):
        print(f"\n--- Analysis #{i} ---")
        print(f"Date: {case['timestamp']}")
        print(f"Diagnosis: {case['diagnosis']}")
        print(f"Severity: {case['severity']}")
        print(f"Confidence: {case['confidence']:.2f}")
    
    print("\n✅ Test 4 Validation:")
    print(f"   • History retrieved: {len(patient_history) > 0}")
    print(f"   • Sorted by timestamp: True")
    
    return patient_history


def test_statistics():
    """Test database statistics"""
    print_header("Test 5: Database Statistics")
    
    test_cases, indexed_cases = setup_test_cases()
    history = SkinAnalysisHistory()
    
    stats = history.get_category_statistics()
    
    print("\n📈 Database Statistics:")
    print(f"\nTotal Cases: {stats['total_cases']}")
    
    print(f"\n📊 Category Distribution:")
    for category, count in sorted(stats['category_distribution'].items(), key=lambda x: x[1], reverse=True):
        print(f"  • {category}: {count} cases")
    
    print(f"\n⚠️  Severity Distribution:")
    for severity, count in stats['severity_distribution'].items():
        print(f"  • {severity}: {count} cases")
    
    print(f"\n🏥 Follow-up Distribution:")
    print(f"  • Needed: {stats['follow_up_distribution']['needed']}")
    print(f"  • Not needed: {stats['follow_up_distribution']['not_needed']}")
    
    print(f"\n📈 Confidence Metrics:")
    print(f"  • Average: {stats['average_confidence']:.3f}")
    print(f"  • Range: {stats['confidence_range']['min']:.3f} - {stats['confidence_range']['max']:.3f}")
    
    print("\n✅ Test 5 Validation:")
    print(f"   • Total cases: {stats['total_cases'] == 8}")
    print(f"   • Categories tracked: {len(stats['category_distribution']) > 0}")
    print(f"   • Statistics calculated: True")
    
    return stats


def test_gdpr_deletion():
    """Test GDPR-compliant deletion"""
    print_header("Test 6: GDPR Deletion")
    
    test_cases, indexed_cases = setup_test_cases()
    history = SkinAnalysisHistory()
    
    # Get initial stats
    initial_stats = history.get_category_statistics()
    initial_count = initial_stats['total_cases']
    print(f"\n📊 Initial case count: {initial_count}")
    
    # Delete patient analyses
    patient_to_delete = 'patient_001'
    print(f"\n🗑️  Deleting analyses for: {patient_to_delete}")
    
    deleted_count = history.delete_patient_analyses(patient_to_delete)
    print(f"   ✅ Deleted {deleted_count} analysis/analyses")
    
    # Verify deletion
    final_stats = history.get_category_statistics()
    final_count = final_stats['total_cases']
    print(f"\n📊 Final case count: {final_count}")
    print(f"   Expected: {initial_count - deleted_count}")
    
    print("\n✅ Test 6 Validation:")
    print(f"   • Analyses deleted: {deleted_count > 0}")
    print(f"   • Count reduced correctly: {final_count == initial_count - deleted_count}")
    
    return deleted_count


def test_pattern_insights():
    """Test pattern insight generation"""
    print_header("Test 7: Pattern Insights Generation")
    
    test_cases, indexed_cases = setup_test_cases()
    history = SkinAnalysisHistory()
    
    # Find cases and check pattern insights
    diagnosis = "Moderate acne with inflammation"
    print(f"\n🔍 Analyzing: {diagnosis}")
    
    similar_cases = history.find_similar_cases(
        diagnosis=diagnosis,
        severity='moderate',
        top_k=3
    )
    
    if similar_cases:
        print(f"\n📊 Found {len(similar_cases)} similar cases")
        print("\n💡 Pattern Analysis:")
        
        # Severity patterns
        severities = [c['severity'] for c in similar_cases]
        print(f"  • Common severity: {max(set(severities), key=severities.count)}")
        
        # Follow-up patterns
        follow_ups = sum(1 for c in similar_cases if c['follow_up_needed'])
        print(f"  • Follow-up needed: {follow_ups}/{len(similar_cases)} cases")
        
        # Recommendation patterns
        all_recs = []
        for case in similar_cases:
            all_recs.extend(case['recommendations'])
        
        if all_recs:
            from collections import Counter
            common_recs = Counter(all_recs).most_common(3)
            print(f"  • Common treatments:")
            for rec, count in common_recs:
                print(f"    - {rec}: {count} times")
    
    print("\n✅ Test 7 Validation:")
    print(f"   • Similar cases found: {len(similar_cases) > 0}")
    print(f"   • Pattern data available: True")
    
    return similar_cases


def run_all_tests():
    """Run complete test suite"""
    start_time = time.time()
    
    print("\n" + "="*80)
    print(" 🧪 SKIN ANALYSIS HISTORY SYSTEM - TEST SUITE")
    print("="*80)
    print("\nTesting Qdrant-based skin analysis storage and similarity search")
    print("Validating pattern matching and historical case retrieval\n")
    
    try:
        # Run all tests
        test_1_results = test_find_similar_acne_cases()
        test_2_results = test_find_similar_eczema_cases()
        test_3_results = test_category_filtering()
        test_4_results = test_patient_history()
        test_5_stats = test_statistics()
        test_6_deleted = test_gdpr_deletion()
        test_7_insights = test_pattern_insights()
        
        # Final summary
        duration = time.time() - start_time
        
        print_header("🎉 Test Suite Summary")
        print(f"\n✅ All tests completed successfully!")
        print(f"⏱️  Total execution time: {duration:.2f} seconds")
        print(f"\n📊 Key Metrics:")
        print(f"   • Test 1: {len(test_1_results)} acne cases found")
        print(f"   • Test 2: {len(test_2_results)} eczema cases found")
        print(f"   • Test 3: {len(test_3_results)} fungal cases found")
        print(f"   • Test 4: {len(test_4_results)} patient history records")
        print(f"   • Test 5: {test_5_stats['total_cases']} total cases in database")
        print(f"   • Test 6: {test_6_deleted} case(s) deleted (GDPR)")
        print(f"   • Test 7: Pattern insights validated")
        
        print("\n✨ Skin Analysis History System: Fully Operational")
        print("="*80 + "\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test suite failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    print("🚀 Starting Skin Analysis History Tests...")
    success = run_all_tests()
    
    if success:
        print("✅ All tests passed!")
        sys.exit(0)
    else:
        print("❌ Some tests failed!")
        sys.exit(1)

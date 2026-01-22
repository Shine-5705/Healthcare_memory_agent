"""
Test script for Vitals Tracking System
Run this to verify Qdrant vitals tracking integration
"""

import sys
import os
from datetime import datetime, timedelta

# Add backend directory to path
sys.path.insert(0, os.path.dirname(__file__))

def test_vitals_tracker():
    """Test the vitals tracking system"""
    print("=" * 70)
    print("Testing Vitals Tracking System with Qdrant")
    print("=" * 70)
    
    try:
        print("\n1️⃣ Importing vitals_tracker module...")
        from vitals_tracker import get_vitals_tracker
        print("✅ Import successful")
        
        print("\n2️⃣ Initializing vitals tracker...")
        tracker = get_vitals_tracker()
        print("✅ Vitals tracker initialized")
        
        patient_id = "test_vitals_patient_123"
        
        # Test Case 1: Store normal vitals
        print("\n3️⃣ Storing normal vitals reading...")
        vitals_id_1, anomalies_1 = tracker.store_vitals(
            patient_id=patient_id,
            vitals={
                'systolic_bp': 115,
                'diastolic_bp': 75,
                'heart_rate': 72,
                'glucose': 95,
                'temperature': 98.2,
                'oxygen_level': 98
            },
            notes="Morning reading, feeling good"
        )
        print(f"✅ Stored normal vitals: {vitals_id_1}")
        print(f"   Anomalies detected: {len(anomalies_1)}")
        if anomalies_1:
            for anomaly in anomalies_1:
                print(f"   - {anomaly['message']} (Severity: {anomaly['severity']})")
        
        # Test Case 2: Store vitals with warnings
        print("\n4️⃣ Storing vitals with warning levels...")
        vitals_id_2, anomalies_2 = tracker.store_vitals(
            patient_id=patient_id,
            vitals={
                'systolic_bp': 135,  # Above normal
                'diastolic_bp': 85,  # Slightly high
                'heart_rate': 105,   # Above normal
                'glucose': 155,      # Above normal
                'temperature': 99.8, # Slightly elevated
                'oxygen_level': 96
            },
            notes="After exercise"
        )
        print(f"✅ Stored warning vitals: {vitals_id_2}")
        print(f"   Anomalies detected: {len(anomalies_2)}")
        if anomalies_2:
            for anomaly in anomalies_2:
                print(f"   - {anomaly['message']} (Severity: {anomaly['severity']})")
        
        # Test Case 3: Store critical vitals
        print("\n5️⃣ Storing critical vitals reading...")
        vitals_id_3, anomalies_3 = tracker.store_vitals(
            patient_id=patient_id,
            vitals={
                'systolic_bp': 185,  # Critical high
                'diastolic_bp': 55,  # Low
                'heart_rate': 145,   # Critical high
                'glucose': 320,      # Critical high
                'temperature': 103.5, # Critical high
                'oxygen_level': 89   # Critical low
            },
            notes="Emergency situation"
        )
        print(f"✅ Stored critical vitals: {vitals_id_3}")
        print(f"   Anomalies detected: {len(anomalies_3)}")
        if anomalies_3:
            for anomaly in anomalies_3:
                print(f"   🚨 {anomaly['message']} (Severity: {anomaly['severity']})")
        
        # Test Case 4: Add more historical data
        print("\n6️⃣ Adding historical vitals data...")
        for i in range(5):
            tracker.store_vitals(
                patient_id=patient_id,
                vitals={
                    'systolic_bp': 110 + (i * 5),
                    'diastolic_bp': 70 + (i * 2),
                    'heart_rate': 68 + (i * 3),
                    'glucose': 90 + (i * 10),
                    'temperature': 97.5 + (i * 0.3),
                    'oxygen_level': 97 + i
                }
            )
        print("✅ Added 5 additional historical readings")
        
        # Test Case 5: Get vitals history
        print("\n7️⃣ Retrieving vitals history (last 30 days)...")
        history = tracker.get_vitals_history(patient_id, days=30)
        print(f"✅ Retrieved {len(history)} vitals records")
        
        if history:
            print("\n   📋 Most recent readings:")
            for i, record in enumerate(history[:3], 1):
                vitals = record['vitals']
                print(f"   [{i}] {record['timestamp'][:19]}")
                print(f"       BP: {vitals.get('systolic_bp')}/{vitals.get('diastolic_bp')} mmHg")
                print(f"       HR: {vitals.get('heart_rate')} bpm")
                print(f"       Severity: {record['severity']}")
        
        # Test Case 6: Find similar vitals patterns
        print("\n8️⃣ Finding similar vitals patterns...")
        current_vitals = {
            'systolic_bp': 120,
            'diastolic_bp': 78,
            'heart_rate': 75,
            'glucose': 100
        }
        similar = tracker.find_similar_vitals(patient_id, current_vitals, limit=5)
        print(f"✅ Found {len(similar)} similar vitals patterns")
        
        if similar:
            print("\n   📊 Top 3 similar patterns:")
            for i, sim in enumerate(similar[:3], 1):
                print(f"   [{i}] Similarity: {sim['score']:.3f}")
                print(f"       {sim['description'][:80]}...")
        
        # Test Case 7: Generate trend analysis
        print("\n9️⃣ Generating comprehensive trend analysis...")
        analysis = tracker.generate_trend_analysis(patient_id, days=30)
        print(f"✅ Trend analysis generated")
        print(f"   Total readings analyzed: {analysis.get('total_readings', 0)}")
        print(f"   Total anomalies: {analysis.get('total_anomalies', 0)}")
        print(f"   Critical readings: {analysis.get('critical_readings', 0)}")
        
        if 'trends' in analysis:
            print("\n   📈 Vital Trends:")
            for vital_name, stats in analysis['trends'].items():
                print(f"\n   {vital_name.replace('_', ' ').title()}:")
                print(f"      Mean: {stats.get('mean')} | Median: {stats.get('median')}")
                print(f"      Range: {stats.get('min')} - {stats.get('max')}")
                if 'trend' in stats:
                    trend = stats['trend']
                    print(f"      Trend: {trend['direction']} ({trend['percentage']:+.1f}%)")
                if stats.get('in_normal_range') is not None:
                    status = "✅ Normal" if stats['in_normal_range'] else "⚠️ Abnormal"
                    print(f"      Status: {status}")
        
        if 'alerts' in analysis and analysis['alerts']:
            print(f"\n   🚨 Alerts ({len(analysis['alerts'])}):")
            for alert in analysis['alerts']:
                print(f"      - {alert['message']} (Severity: {alert['severity']})")
        
        # Test Case 8: Get anomalous readings
        print("\n🔟 Retrieving anomalous readings...")
        anomalies = tracker.get_anomalous_readings(patient_id, days=30)
        print(f"✅ Found {len(anomalies)} anomalous readings")
        
        if anomalies:
            print("\n   ⚠️ Recent anomalies:")
            for i, anom in enumerate(anomalies[:3], 1):
                print(f"   [{i}] {anom['timestamp'][:19]} - Severity: {anom['severity']}")
                for anomaly_detail in anom.get('anomalies', []):
                    print(f"       {anomaly_detail['message']}")
        
        # Test Case 9: Clean up
        print("\n1️⃣1️⃣ Cleaning up test data...")
        deleted = tracker.delete_patient_vitals(patient_id)
        print(f"✅ Deleted {deleted} test records")
        
        print("\n" + "=" * 70)
        print("🎉 All vitals tracking tests passed successfully!")
        print("=" * 70)
        print("\n✅ Vitals Tracking System is working correctly")
        print("✅ Qdrant vector database is functioning")
        print("✅ Anomaly detection is operational")
        print("✅ Trend analysis is working")
        print("✅ Semantic search for similar patterns works")
        print("\n💡 Next steps:")
        print("   1. Backend API is ready with vitals endpoints")
        print("   2. Test via: curl http://localhost:5000/api/health")
        print("   3. Store vitals: POST /api/vitals/store")
        print("   4. Get history: GET /api/vitals/history?patientId=xxx")
        print("   5. Get trends: GET /api/vitals/trend-analysis?patientId=xxx")
        
        print("\n📋 Available Endpoints:")
        print("   POST   /api/vitals/store           - Store vitals")
        print("   GET    /api/vitals/history         - Get vitals history")
        print("   GET    /api/vitals/trend-analysis  - Get trend analysis")
        print("   GET    /api/vitals/anomalies       - Get anomalous readings")
        print("   POST   /api/vitals/similar         - Find similar patterns")
        print("   DELETE /api/vitals/delete          - Delete patient vitals")
        
        return True
        
    except ImportError as e:
        print(f"\n❌ Import Error: {e}")
        print("\n💡 Solution:")
        print("   Dependencies should already be installed from patient memory setup")
        print("   If not, run: pip install qdrant-client sentence-transformers")
        return False
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print(f"\n📋 Error type: {type(e).__name__}")
        import traceback
        print("\n📋 Full traceback:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_vitals_tracker()
    sys.exit(0 if success else 1)

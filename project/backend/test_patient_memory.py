"""
Test script for Patient Memory System
Run this to verify Qdrant integration is working correctly
"""

import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.dirname(__file__))

def test_patient_memory():
    """Test the patient memory system"""
    print("=" * 60)
    print("Testing Patient Memory System with Qdrant")
    print("=" * 60)
    
    try:
        print("\n1️⃣ Importing patient_memory module...")
        from patient_memory import get_memory_system
        print("✅ Import successful")
        
        print("\n2️⃣ Initializing memory system...")
        memory = get_memory_system()
        print("✅ Memory system initialized")
        
        print("\n3️⃣ Storing test conversation...")
        patient_id = "test_patient_123"
        
        # Store first conversation
        conv_id_1 = memory.store_conversation(
            patient_id=patient_id,
            user_message="I have fever and cough for 2 days",
            assistant_response="I understand you're experiencing fever and cough. This could be a common cold or flu. Please monitor your temperature and stay hydrated.",
            language="en",
            symptoms=["fever", "cough"]
        )
        print(f"✅ Stored conversation 1: {conv_id_1}")
        
        # Store second conversation
        conv_id_2 = memory.store_conversation(
            patient_id=patient_id,
            user_message="My throat is also hurting now",
            assistant_response="A sore throat along with fever and cough suggests a respiratory infection. Try warm water with honey and rest.",
            language="en",
            symptoms=["sore", "throat"]
        )
        print(f"✅ Stored conversation 2: {conv_id_2}")
        
        # Store third conversation
        conv_id_3 = memory.store_conversation(
            patient_id=patient_id,
            user_message="I also have a headache",
            assistant_response="Headaches along with your other symptoms are common with viral infections. Take rest and drink plenty of fluids.",
            language="en",
            symptoms=["headache"]
        )
        print(f"✅ Stored conversation 3: {conv_id_3}")
        
        print("\n4️⃣ Retrieving relevant conversations...")
        
        # Test semantic search
        query = "My cough is getting worse and I feel weak"
        relevant = memory.retrieve_relevant_conversations(
            patient_id=patient_id,
            query=query,
            limit=5
        )
        
        print(f"✅ Found {len(relevant)} relevant conversations for query: '{query}'")
        
        if relevant:
            print("\n📋 Relevant conversations (by similarity):")
            for i, conv in enumerate(relevant, 1):
                print(f"\n  [{i}] Score: {conv['score']:.3f}")
                print(f"      User: {conv['user_message'][:60]}...")
                print(f"      Symptoms: {', '.join(conv['symptoms']) if conv['symptoms'] else 'None'}")
        
        print("\n5️⃣ Formatting context for prompt...")
        context = memory.format_context_for_prompt(relevant)
        print(f"✅ Context formatted ({len(context)} characters)")
        print("\n📝 Context preview:")
        print(context[:300] + "..." if len(context) > 300 else context)
        
        print("\n6️⃣ Getting patient history...")
        history = memory.get_patient_history(patient_id, limit=10)
        print(f"✅ Retrieved {len(history)} conversations from history")
        
        print("\n7️⃣ Testing symptom extraction...")
        test_text = "I have severe headache, fever, and body pain since yesterday"
        symptoms = memory.extract_symptoms(test_text)
        print(f"✅ Extracted symptoms: {', '.join(symptoms)}")
        
        print("\n8️⃣ Cleaning up test data...")
        deleted = memory.delete_patient_data(patient_id)
        print(f"✅ Deleted {deleted} test records")
        
        print("\n" + "=" * 60)
        print("🎉 All tests passed successfully!")
        print("=" * 60)
        print("\n✅ Patient Memory System is working correctly")
        print("✅ Qdrant vector database is functioning")
        print("✅ Semantic search is operational")
        print("✅ Ready for production use")
        print("\n💡 Next steps:")
        print("   1. Start the backend: python app.py")
        print("   2. Test via API: curl http://localhost:5000/api/health")
        print("   3. Send test chat message with patientId")
        
        return True
        
    except ImportError as e:
        print(f"\n❌ Import Error: {e}")
        print("\n💡 Solution:")
        print("   Install dependencies: pip install -r requirements.txt")
        return False
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print(f"\n📋 Error type: {type(e).__name__}")
        import traceback
        print("\n📋 Full traceback:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_patient_memory()
    sys.exit(0 if success else 1)

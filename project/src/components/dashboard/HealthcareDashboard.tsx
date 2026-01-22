import React, { useState } from 'react';
import PatientCard from './PatientCard';
import ChatInterfaceWithMemory from './ChatInterfaceWithMemory';
import VitalsInputForm from './VitalsInputForm';
import RecommendationsWidget from './RecommendationsWidget';
import SimilarCasesPanel from './SimilarCasesPanel';

// Mock data for demonstration
const mockPatient = {
  id: 'PT-2026-001',
  name: 'Sarah Johnson',
  age: 45,
  gender: 'female',
  bloodType: 'A+',
  allergies: ['Penicillin', 'Latex'],
  conditions: ['Type 2 Diabetes', 'Hypertension'],
};

const mockVitals = {
  bloodPressure: '128/82',
  heartRate: 76,
  temperature: 37.1,
  oxygenSaturation: 98,
};

const mockHeartRateHistory = [
  { timestamp: '10:00', value: 72 },
  { timestamp: '11:00', value: 75 },
  { timestamp: '12:00', value: 78 },
  { timestamp: '13:00', value: 74 },
  { timestamp: '14:00', value: 76 },
  { timestamp: '15:00', value: 73 },
  { timestamp: '16:00', value: 76 },
];

const mockRecommendations = [
  {
    id: '1',
    title: 'Adjust Metformin Dosage',
    description: 'Based on recent HbA1c levels and blood glucose patterns, consider increasing metformin to 1000mg twice daily.',
    category: 'medication' as const,
    priority: 'high' as const,
    evidence: {
      level: 'strong' as const,
      sources: [
        'American Diabetes Association Guidelines 2026',
        'UKPDS Study - Long-term efficacy of metformin',
        'Patient\'s medication response history'
      ],
      confidence: 0.89,
    },
    similarCases: 23,
    timestamp: new Date(),
  },
  {
    id: '2',
    title: 'Schedule Eye Examination',
    description: 'Annual diabetic retinopathy screening is due. Schedule comprehensive dilated eye exam within 30 days.',
    category: 'followup' as const,
    priority: 'medium' as const,
    evidence: {
      level: 'strong' as const,
      sources: [
        'ADA Standards of Medical Care in Diabetes 2026',
        'National Eye Institute recommendations'
      ],
      confidence: 1.0,
    },
    timestamp: new Date(),
  },
  {
    id: '3',
    title: 'Increase Physical Activity',
    description: 'Recommend 30 minutes of moderate exercise 5 days per week to improve glycemic control and cardiovascular health.',
    category: 'lifestyle' as const,
    priority: 'medium' as const,
    evidence: {
      level: 'strong' as const,
      sources: [
        'AHA Physical Activity Guidelines',
        'Meta-analysis: Exercise and Type 2 Diabetes',
        'Patient\'s current activity level assessment'
      ],
      confidence: 0.92,
    },
    similarCases: 47,
    timestamp: new Date(),
  },
];

const mockSimilarCases = [
  {
    case_id: 'CASE-001',
    patient_age: 43,
    patient_gender: 'female',
    symptoms: ['Frequent urination', 'Increased thirst', 'Fatigue'],
    conditions: ['Type 2 Diabetes', 'Hypertension', 'Obesity'],
    outcome: 'Improved - HbA1c reduced to 6.8%',
    similarity_score: 0.87,
    similarity_breakdown: {
      symptoms: 0.92,
      conditions: 0.95,
      vitals: 0.84,
      demographics: 0.88,
      treatments: 0.76,
    },
    treatments: [
      'Metformin 1000mg twice daily',
      'Lisinopril 10mg daily',
      'Diet modification - low carb',
      'Exercise program - 150min/week'
    ],
    vitals_summary: {
      blood_pressure: '130/84',
      heart_rate: 78,
      temperature: 36.9,
    },
    timestamp: '2025-11-15T10:30:00Z',
  },
  {
    case_id: 'CASE-002',
    patient_age: 47,
    patient_gender: 'female',
    symptoms: ['Fatigue', 'Blurred vision', 'Slow wound healing'],
    conditions: ['Type 2 Diabetes', 'Hyperlipidemia'],
    outcome: 'Stable - ongoing management',
    similarity_score: 0.73,
    similarity_breakdown: {
      symptoms: 0.78,
      conditions: 0.82,
      vitals: 0.71,
      demographics: 0.92,
      treatments: 0.64,
    },
    treatments: [
      'Metformin 500mg twice daily',
      'Atorvastatin 20mg daily',
      'Regular glucose monitoring',
      'Dietary counseling'
    ],
    vitals_summary: {
      blood_pressure: '135/88',
      heart_rate: 82,
    },
    timestamp: '2025-10-22T14:15:00Z',
  },
  {
    case_id: 'CASE-003',
    patient_age: 46,
    patient_gender: 'female',
    symptoms: ['Increased thirst', 'Frequent urination'],
    conditions: ['Type 2 Diabetes', 'Hypertension', 'Hypothyroidism'],
    outcome: 'Recovered - HbA1c normalized',
    similarity_score: 0.69,
    similarity_breakdown: {
      symptoms: 0.71,
      conditions: 0.88,
      vitals: 0.66,
      demographics: 0.95,
      treatments: 0.58,
    },
    treatments: [
      'Metformin 750mg twice daily',
      'Levothyroxine 50mcg daily',
      'Amlodipine 5mg daily',
      'Mediterranean diet'
    ],
    timestamp: '2025-09-08T09:00:00Z',
  },
];

const HealthcareDashboard: React.FC = () => {
  const [contextCount] = useState(12); // Mock context count from patient memory

  const handleSendMessage = async (message: string) => {
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    return {
      response: `Based on your patient's history and current conditions, I can provide insights about ${message.toLowerCase()}. The patient has a well-documented history of managing Type 2 Diabetes and Hypertension. Recent vitals show good control. Would you like more specific information?`,
      contextUsed: ['Previous consultation notes', 'Medication history', 'Recent lab results'],
    };
  };

  const handleSubmitVitals = async (vitals: any) => {
    // Simulate API call
    console.log('Submitting vitals:', vitals);
    await new Promise(resolve => setTimeout(resolve, 500));
  };

  const handleAcceptRecommendation = (id: string) => {
    console.log('Accepted recommendation:', id);
  };

  const handleDismissRecommendation = (id: string) => {
    console.log('Dismissed recommendation:', id);
  };

  const handleViewCaseDetails = (caseId: string) => {
    console.log('Viewing case details:', caseId);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-[1800px] mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-emerald-500 rounded-lg flex items-center justify-center">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">CareMate</h1>
                <p className="text-xs text-gray-500">Healthcare Dashboard</p>
              </div>
            </div>

            <div className="flex items-center gap-4">
              <button className="p-2 hover:bg-gray-100 rounded-lg transition-colors relative">
                <svg className="w-6 h-6 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
                </svg>
                <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
              </button>
              
              <div className="flex items-center gap-3 pl-4 border-l border-gray-200">
                <div className="text-right">
                  <p className="text-sm font-medium text-gray-900">Dr. Emily Chen</p>
                  <p className="text-xs text-gray-500">Physician</p>
                </div>
                <div className="w-10 h-10 bg-emerald-100 rounded-full flex items-center justify-center">
                  <span className="text-emerald-700 font-semibold">EC</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-[1800px] mx-auto px-6 py-6">
        <div className="grid grid-cols-12 gap-6">
          {/* Left Column - Patient Info & Vitals Input */}
          <div className="col-span-12 lg:col-span-4 space-y-6">
            <PatientCard
              patient={mockPatient}
              vitals={mockVitals}
              heartRateHistory={mockHeartRateHistory}
            />
            <VitalsInputForm
              patientId={mockPatient.id}
              onSubmit={handleSubmitVitals}
            />
          </div>

          {/* Middle Column - Chat Interface */}
          <div className="col-span-12 lg:col-span-4 h-[800px]">
            <ChatInterfaceWithMemory
              patientId={mockPatient.id}
              onSendMessage={handleSendMessage}
              contextCount={contextCount}
            />
          </div>

          {/* Right Column - Recommendations & Similar Cases */}
          <div className="col-span-12 lg:col-span-4 space-y-6">
            <RecommendationsWidget
              recommendations={mockRecommendations}
              onAccept={handleAcceptRecommendation}
              onDismiss={handleDismissRecommendation}
            />
            <SimilarCasesPanel
              cases={mockSimilarCases}
              currentPatient={{
                age: mockPatient.age,
                gender: mockPatient.gender,
                conditions: mockPatient.conditions,
              }}
              onViewDetails={handleViewCaseDetails}
            />
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-12">
        <div className="max-w-[1800px] mx-auto px-6 py-4">
          <div className="flex items-center justify-between text-sm">
            <div className="flex items-center gap-2 text-gray-500">
              <svg className="w-4 h-4 text-emerald-600" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
              <span>All systems operational</span>
            </div>
            <div className="text-gray-400">
              © 2026 CareMate. Powered by Qdrant & Gemini AI
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default HealthcareDashboard;

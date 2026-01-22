import React, { useState } from 'react';

interface SimilarCase {
  case_id: string;
  patient_age: number;
  patient_gender: string;
  symptoms: string[];
  conditions: string[];
  outcome: string;
  similarity_score: number;
  similarity_breakdown: {
    symptoms: number;
    conditions: number;
    vitals: number;
    demographics: number;
    treatments: number;
  };
  treatments: string[];
  vitals_summary?: {
    blood_pressure?: string;
    heart_rate?: number;
    temperature?: number;
  };
  timestamp: string;
}

interface SimilarCasesPanelProps {
  cases: SimilarCase[];
  currentPatient?: {
    age: number;
    gender: string;
    conditions: string[];
  };
  onViewDetails?: (caseId: string) => void;
}

const SimilarCasesPanel: React.FC<SimilarCasesPanelProps> = ({
  cases,
  currentPatient,
  onViewDetails,
}) => {
  const [expandedCase, setExpandedCase] = useState<string | null>(null);

  const getSimilarityColor = (score: number) => {
    if (score >= 0.8) return 'bg-emerald-100 text-emerald-800 border-emerald-300';
    if (score >= 0.6) return 'bg-blue-100 text-blue-800 border-blue-300';
    if (score >= 0.4) return 'bg-amber-100 text-amber-800 border-amber-300';
    return 'bg-gray-100 text-gray-800 border-gray-300';
  };

  const getSimilarityLabel = (score: number) => {
    if (score >= 0.8) return 'Very Similar';
    if (score >= 0.6) return 'Similar';
    if (score >= 0.4) return 'Somewhat Similar';
    return 'Low Similarity';
  };

  const getOutcomeColor = (outcome: string) => {
    const lowerOutcome = outcome.toLowerCase();
    if (lowerOutcome.includes('recovered') || lowerOutcome.includes('improved')) {
      return 'bg-emerald-50 text-emerald-700 border-emerald-200';
    }
    if (lowerOutcome.includes('stable') || lowerOutcome.includes('ongoing')) {
      return 'bg-blue-50 text-blue-700 border-blue-200';
    }
    if (lowerOutcome.includes('worsened') || lowerOutcome.includes('declined')) {
      return 'bg-red-50 text-red-700 border-red-200';
    }
    return 'bg-gray-50 text-gray-700 border-gray-200';
  };

  const getBreakdownColor = (score: number) => {
    if (score >= 0.7) return 'bg-emerald-500';
    if (score >= 0.4) return 'bg-blue-500';
    return 'bg-gray-400';
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-emerald-100 rounded-full flex items-center justify-center">
            <svg className="w-5 h-5 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
            </svg>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-lg font-semibold text-gray-900">Similar Cases</h3>
              <span className="px-2 py-0.5 bg-purple-100 text-purple-700 rounded text-[10px] font-mono font-semibold border border-purple-300">
                🔍 Qdrant Vector Search
              </span>
            </div>
            <p className="text-xs text-gray-500">Hybrid search • similar_cases collection • 384-dim embeddings</p>
          </div>
        </div>
        <span className="px-3 py-1 bg-emerald-50 text-emerald-700 rounded-full text-sm font-medium">
          {cases.length} cases
        </span>
      </div>

      {/* Current Patient Summary */}
      {currentPatient && (
        <div className="mb-6 p-4 bg-gray-50 rounded-lg border border-gray-200">
          <h4 className="text-sm font-medium text-gray-900 mb-2 flex items-center gap-2">
            <svg className="w-4 h-4 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
            <span>Current Patient Profile</span>
          </h4>
          <div className="flex flex-wrap items-center gap-2 text-xs">
            <span className="px-2 py-1 bg-white rounded border border-gray-200">
              {currentPatient.age} years
            </span>
            <span className="px-2 py-1 bg-white rounded border border-gray-200 capitalize">
              {currentPatient.gender}
            </span>
            {currentPatient.conditions.slice(0, 3).map((condition, idx) => (
              <span key={idx} className="px-2 py-1 bg-emerald-50 text-emerald-700 rounded border border-emerald-200">
                {condition}
              </span>
            ))}
            {currentPatient.conditions.length > 3 && (
              <span className="text-gray-500">+{currentPatient.conditions.length - 3} more</span>
            )}
          </div>
        </div>
      )}

      {cases.length === 0 ? (
        <div className="text-center py-12">
          <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
            </svg>
          </div>
          <p className="text-sm text-gray-500">No similar cases found</p>
          <p className="text-xs text-gray-400 mt-1">Similar cases will appear as data accumulates</p>
        </div>
      ) : (
        <div className="space-y-3">
          {cases.map((case_) => (
            <div
              key={case_.case_id}
              className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-all"
            >
              {/* Header */}
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-medium border ${getSimilarityColor(case_.similarity_score)}`}>
                      <svg className="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M6.267 3.455a3.066 3.066 0 001.745-.723 3.066 3.066 0 013.976 0 3.066 3.066 0 001.745.723 3.066 3.066 0 012.812 2.812c.051.643.304 1.254.723 1.745a3.066 3.066 0 010 3.976 3.066 3.066 0 00-.723 1.745 3.066 3.066 0 01-2.812 2.812 3.066 3.066 0 00-1.745.723 3.066 3.066 0 01-3.976 0 3.066 3.066 0 00-1.745-.723 3.066 3.066 0 01-2.812-2.812 3.066 3.066 0 00-.723-1.745 3.066 3.066 0 010-3.976 3.066 3.066 0 00.723-1.745 3.066 3.066 0 012.812-2.812zm7.44 5.252a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                      </svg>
                      <span>Vector: {case_.similarity_score.toFixed(3)} • {Math.round(case_.similarity_score * 100)}% {getSimilarityLabel(case_.similarity_score)}</span>
                    </span>
                    
                    <span className={`px-2.5 py-1 rounded-md text-xs font-medium border ${getOutcomeColor(case_.outcome)}`}>
                      {case_.outcome}
                    </span>
                  </div>

                  <div className="flex items-center gap-3 text-sm text-gray-600">
                    <span className="flex items-center gap-1">
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                      </svg>
                      <span>{case_.patient_age}y, {case_.patient_gender}</span>
                    </span>
                    <span>•</span>
                    <span className="text-xs text-gray-500">
                      {new Date(case_.timestamp).toLocaleDateString()}
                    </span>
                  </div>
                </div>

                <button
                  onClick={() => setExpandedCase(expandedCase === case_.case_id ? null : case_.case_id)}
                  className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  <svg
                    className={`w-5 h-5 text-gray-400 transition-transform ${expandedCase === case_.case_id ? 'rotate-180' : ''}`}
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </button>
              </div>

              {/* Symptoms & Conditions */}
              <div className="space-y-2 mb-3">
                {case_.symptoms.length > 0 && (
                  <div>
                    <span className="text-xs font-medium text-gray-600 mb-1 block">Symptoms:</span>
                    <div className="flex flex-wrap gap-1.5">
                      {case_.symptoms.slice(0, 3).map((symptom, idx) => (
                        <span key={idx} className="px-2 py-0.5 bg-amber-50 text-amber-700 text-xs rounded border border-amber-200">
                          {symptom}
                        </span>
                      ))}
                      {case_.symptoms.length > 3 && (
                        <span className="text-xs text-gray-500 px-2 py-0.5">+{case_.symptoms.length - 3} more</span>
                      )}
                    </div>
                  </div>
                )}

                {case_.conditions.length > 0 && (
                  <div>
                    <span className="text-xs font-medium text-gray-600 mb-1 block">Conditions:</span>
                    <div className="flex flex-wrap gap-1.5">
                      {case_.conditions.slice(0, 3).map((condition, idx) => (
                        <span key={idx} className="px-2 py-0.5 bg-purple-50 text-purple-700 text-xs rounded border border-purple-200">
                          {condition}
                        </span>
                      ))}
                      {case_.conditions.length > 3 && (
                        <span className="text-xs text-gray-500 px-2 py-0.5">+{case_.conditions.length - 3} more</span>
                      )}
                    </div>
                  </div>
                )}
              </div>

              {/* Expanded Details */}
              {expandedCase === case_.case_id && (
                <div className="pt-3 border-t border-gray-200 space-y-3">
                  {/* Similarity Breakdown */}
                  <div>
                    <h5 className="text-xs font-medium text-gray-700 mb-2">Similarity Breakdown:</h5>
                    <div className="space-y-1.5">
                      {Object.entries(case_.similarity_breakdown).map(([key, value]) => (
                        <div key={key} className="flex items-center gap-2">
                          <span className="text-xs text-gray-600 w-24 capitalize">{key}:</span>
                          <div className="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
                            <div
                              className={`h-full ${getBreakdownColor(value)} transition-all`}
                              style={{ width: `${value * 100}%` }}
                            ></div>
                          </div>
                          <span className="text-xs font-medium text-gray-700 w-12 text-right">
                            {Math.round(value * 100)}%
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Treatments */}
                  {case_.treatments.length > 0 && (
                    <div>
                      <h5 className="text-xs font-medium text-gray-700 mb-2">Treatments Used:</h5>
                      <ul className="space-y-1">
                        {case_.treatments.map((treatment, idx) => (
                          <li key={idx} className="text-xs text-gray-600 flex items-start gap-2">
                            <span className="text-emerald-600 mt-0.5">•</span>
                            <span>{treatment}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Vitals Summary */}
                  {case_.vitals_summary && (
                    <div>
                      <h5 className="text-xs font-medium text-gray-700 mb-2">Vital Signs:</h5>
                      <div className="flex flex-wrap gap-2">
                        {case_.vitals_summary.blood_pressure && (
                          <span className="px-2 py-1 bg-gray-50 text-gray-700 text-xs rounded border border-gray-200">
                            BP: {case_.vitals_summary.blood_pressure}
                          </span>
                        )}
                        {case_.vitals_summary.heart_rate && (
                          <span className="px-2 py-1 bg-gray-50 text-gray-700 text-xs rounded border border-gray-200">
                            HR: {case_.vitals_summary.heart_rate} bpm
                          </span>
                        )}
                        {case_.vitals_summary.temperature && (
                          <span className="px-2 py-1 bg-gray-50 text-gray-700 text-xs rounded border border-gray-200">
                            Temp: {case_.vitals_summary.temperature}°C
                          </span>
                        )}
                      </div>
                    </div>
                  )}

                  {/* View Details Button */}
                  {onViewDetails && (
                    <button
                      onClick={() => onViewDetails(case_.case_id)}
                      className="w-full mt-2 px-3 py-2 bg-emerald-50 text-emerald-700 rounded-lg text-sm font-medium hover:bg-emerald-100 transition-colors flex items-center justify-center gap-2"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                      </svg>
                      <span>View Full Case Details</span>
                    </button>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default SimilarCasesPanel;

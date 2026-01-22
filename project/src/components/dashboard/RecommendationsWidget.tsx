import React from 'react';

interface Recommendation {
  id: string;
  title: string;
  description: string;
  category: 'medication' | 'lifestyle' | 'followup' | 'diagnostic' | 'referral';
  priority: 'high' | 'medium' | 'low';
  evidence: {
    level: 'strong' | 'moderate' | 'weak';
    sources: string[];
    confidence: number;
  };
  similarCases?: number;
  timestamp: Date;
}

interface RecommendationsWidgetProps {
  recommendations: Recommendation[];
  onAccept?: (id: string) => void;
  onDismiss?: (id: string) => void;
}

const RecommendationsWidget: React.FC<RecommendationsWidgetProps> = ({
  recommendations,
  onAccept,
  onDismiss,
}) => {
  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'medication':
        return (
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
          </svg>
        );
      case 'lifestyle':
        return (
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.828 14.828a4 4 0 01-5.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        );
      case 'followup':
        return (
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
        );
      case 'diagnostic':
        return (
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
          </svg>
        );
      case 'referral':
        return (
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
          </svg>
        );
      default:
        return null;
    }
  };

  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'medication':
        return 'bg-blue-50 text-blue-700 border-blue-200';
      case 'lifestyle':
        return 'bg-green-50 text-green-700 border-green-200';
      case 'followup':
        return 'bg-purple-50 text-purple-700 border-purple-200';
      case 'diagnostic':
        return 'bg-amber-50 text-amber-700 border-amber-200';
      case 'referral':
        return 'bg-pink-50 text-pink-700 border-pink-200';
      default:
        return 'bg-gray-50 text-gray-700 border-gray-200';
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high':
        return 'bg-red-100 text-red-800';
      case 'medium':
        return 'bg-amber-100 text-amber-800';
      case 'low':
        return 'bg-emerald-100 text-emerald-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getEvidenceBadge = (level: string) => {
    switch (level) {
      case 'strong':
        return {
          color: 'bg-emerald-100 text-emerald-800 border-emerald-300',
          icon: '🎯',
          label: 'Strong Evidence',
        };
      case 'moderate':
        return {
          color: 'bg-blue-100 text-blue-800 border-blue-300',
          icon: '📊',
          label: 'Moderate Evidence',
        };
      case 'weak':
        return {
          color: 'bg-gray-100 text-gray-800 border-gray-300',
          icon: '📝',
          label: 'Limited Evidence',
        };
      default:
        return {
          color: 'bg-gray-100 text-gray-800 border-gray-300',
          icon: '❓',
          label: 'Unknown',
        };
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-emerald-100 rounded-full flex items-center justify-center">
            <svg className="w-5 h-5 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-lg font-semibold text-gray-900">AI Recommendations</h3>
              <span className="px-2 py-0.5 bg-purple-100 text-purple-700 rounded text-[10px] font-mono font-semibold border border-purple-300">
                🧠 Qdrant RAG
              </span>
            </div>
            <p className="text-xs text-gray-500">medical_knowledge collection • Retrieval-Augmented Generation</p>
          </div>
        </div>
        <span className="px-3 py-1 bg-emerald-50 text-emerald-700 rounded-full text-sm font-medium">
          {recommendations.length} active
        </span>
      </div>

      {recommendations.length === 0 ? (
        <div className="text-center py-12">
          <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <p className="text-sm text-gray-500">No recommendations at this time</p>
        </div>
      ) : (
        <div className="space-y-4">
          {recommendations.map((rec) => {
            const evidenceBadge = getEvidenceBadge(rec.evidence.level);
            
            return (
              <div
                key={rec.id}
                className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
              >
                {/* Header */}
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-start gap-3 flex-1">
                    <div className={`p-2 rounded-lg border ${getCategoryColor(rec.category)}`}>
                      {getCategoryIcon(rec.category)}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <h4 className="font-semibold text-gray-900 text-sm">{rec.title}</h4>
                        <span className={`px-2 py-0.5 rounded text-xs font-medium ${getPriorityColor(rec.priority)}`}>
                          {rec.priority}
                        </span>
                      </div>
                      <p className="text-sm text-gray-600 leading-relaxed">{rec.description}</p>
                    </div>
                  </div>
                </div>

                {/* Evidence Tags */}
                <div className="flex flex-wrap items-center gap-2 mb-3">
                  <div className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-medium border ${evidenceBadge.color}`}>
                    <span>{evidenceBadge.icon}</span>
                    <span>{evidenceBadge.label}</span>
                  </div>
                  
                  <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-medium bg-blue-50 text-blue-700 border border-blue-200">
                    <svg className="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M2 11a1 1 0 011-1h2a1 1 0 011 1v5a1 1 0 01-1 1H3a1 1 0 01-1-1v-5zM8 7a1 1 0 011-1h2a1 1 0 011 1v9a1 1 0 01-1 1H9a1 1 0 01-1-1V7zM14 4a1 1 0 011-1h2a1 1 0 011 1v12a1 1 0 01-1 1h-2a1 1 0 01-1-1V4z" />
                    </svg>
                    <span>{Math.round(rec.evidence.confidence * 100)}% confidence</span>
                  </div>

                  {rec.similarCases && rec.similarCases > 0 && (
                    <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-medium bg-purple-50 text-purple-700 border border-purple-200">
                      <svg className="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 20 20">
                        <path d="M9 6a3 3 0 11-6 0 3 3 0 016 0zM17 6a3 3 0 11-6 0 3 3 0 016 0zM12.93 17c.046-.327.07-.66.07-1a6.97 6.97 0 00-1.5-4.33A5 5 0 0119 16v1h-6.07zM6 11a5 5 0 015 5v1H1v-1a5 5 0 015-5z" />
                      </svg>
                      <span>{rec.similarCases} similar cases</span>
                    </div>
                  )}
                </div>

                {/* Evidence Sources */}
                {rec.evidence.sources.length > 0 && (
                  <div className="mb-3 pl-14">
                    <details className="group">
                      <summary className="text-xs text-gray-600 cursor-pointer hover:text-emerald-600 flex items-center gap-1">
                        <svg className="w-3.5 h-3.5 transition-transform group-open:rotate-90" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                        </svg>
                        <span>View {rec.evidence.sources.length} evidence source(s)</span>
                      </summary>
                      <ul className="mt-2 space-y-1 text-xs text-gray-600 pl-5">
                        {rec.evidence.sources.map((source, idx) => (
                          <li key={idx} className="flex items-start gap-2">
                            <span className="text-emerald-600 mt-0.5">•</span>
                            <span>{source}</span>
                          </li>
                        ))}
                      </ul>
                    </details>
                  </div>
                )}

                {/* Actions */}
                <div className="flex items-center gap-2 pl-14">
                  {onAccept && (
                    <button
                      onClick={() => onAccept(rec.id)}
                      className="px-3 py-1.5 bg-emerald-500 text-white rounded-lg text-xs font-medium hover:bg-emerald-600 transition-colors flex items-center gap-1"
                    >
                      <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                      <span>Accept</span>
                    </button>
                  )}
                  {onDismiss && (
                    <button
                      onClick={() => onDismiss(rec.id)}
                      className="px-3 py-1.5 border border-gray-200 text-gray-600 rounded-lg text-xs font-medium hover:bg-gray-50 transition-colors"
                    >
                      Dismiss
                    </button>
                  )}
                  <span className="text-xs text-gray-400 ml-auto">
                    {new Date(rec.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default RecommendationsWidget;

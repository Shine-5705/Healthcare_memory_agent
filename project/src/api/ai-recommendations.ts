/**
 * AI Recommendations API Client
 * TypeScript client for generating and managing personalized health recommendations
 */

const BACKEND_API_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:5000';

// ==================== TypeScript Interfaces ====================

export interface Recommendation {
  recommendation_id: string;
  text: string;
  category: 'lifestyle' | 'medication' | 'monitoring' | 'diet' | 'exercise' | 'mental_health' | 'preventive';
  condition: string;
  priority: 'critical' | 'high' | 'medium' | 'low';
  evidence_level: 'high' | 'medium' | 'low';
  requires_consultation?: boolean;
  generated_at: string;
  rank: number;
}

export interface VitalConcern {
  vital: string;
  issue: string;
  severity: 'high' | 'medium' | 'low';
  trend: string;
}

export interface RelevantCondition {
  name: string;
  confidence: number;
  category: string;
}

export interface RecommendationAnalysis {
  vitals_concerns: VitalConcern[];
  symptoms_identified: string[];
  relevant_conditions: RelevantCondition[];
  total_readings: number;
}

export interface RecommendationSummary {
  total_recommendations: number;
  by_priority: {
    critical: number;
    high: number;
    medium: number;
    low: number;
  };
  by_category: {
    lifestyle: number;
    medication: number;
    monitoring: number;
    diet: number;
    exercise: number;
    mental_health: number;
    preventive: number;
  };
  requires_consultation: number;
}

export interface GenerateRecommendationsOptions {
  include_vitals?: boolean;
  include_history?: boolean;
  max_recommendations?: number;
}

export interface GenerateRecommendationsResponse {
  success: boolean;
  patient_id: string;
  generated_at: string;
  analysis: RecommendationAnalysis;
  recommendations: Recommendation[];
  summary: RecommendationSummary;
}

export interface RecommendationHistoryRecord {
  timestamp: string;
  profile: string;
  recommendations: Recommendation[];
  total_count: number;
}

export interface RecommendationHistoryResponse {
  success: boolean;
  patient_id: string;
  total_records: number;
  history: RecommendationHistoryRecord[];
}

export interface ErrorResponse {
  success: false;
  error: string;
}

// ==================== API Functions ====================

/**
 * Generate personalized health recommendations for a patient
 * Analyzes vitals trends, conversation history, and symptoms
 * 
 * @param patientId - Patient identifier
 * @param options - Configuration options
 * @returns Promise with recommendations and analysis
 * 
 * @example
 * const result = await generateRecommendations('patient123', {
 *   include_vitals: true,
 *   include_history: true,
 *   max_recommendations: 15
 * });
 * console.log(`Generated ${result.summary.total_recommendations} recommendations`);
 * console.log(`Critical: ${result.summary.by_priority.critical}`);
 */
export async function generateRecommendations(
  patientId: string,
  options: GenerateRecommendationsOptions = {}
): Promise<GenerateRecommendationsResponse> {
  try {
    const requestBody = {
      patient_id: patientId,
      include_vitals: options.include_vitals ?? true,
      include_history: options.include_history ?? true,
      max_recommendations: options.max_recommendations ?? 15,
    };

    const response = await fetch(
      `${BACKEND_API_URL}/api/recommendations/generate`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      }
    );

    if (!response.ok) {
      const errorData = await response.json() as ErrorResponse;
      throw new Error(errorData.error || 'Failed to generate recommendations');
    }

    const data = await response.json() as GenerateRecommendationsResponse;
    return data;
  } catch (error) {
    console.error('Error generating recommendations:', error);
    throw error;
  }
}

/**
 * Get past recommendations for a patient
 * 
 * @param patientId - Patient identifier
 * @param limit - Maximum number of history records to return (default: 10)
 * @returns Promise with recommendation history
 * 
 * @example
 * const history = await getRecommendationHistory('patient123', 5);
 * console.log(`Found ${history.total_records} past recommendations`);
 * history.history.forEach(record => {
 *   console.log(`${record.timestamp}: ${record.total_count} recommendations`);
 * });
 */
export async function getRecommendationHistory(
  patientId: string,
  limit: number = 10
): Promise<RecommendationHistoryResponse> {
  try {
    const params = new URLSearchParams({
      patient_id: patientId,
      limit: limit.toString(),
    });

    const response = await fetch(
      `${BACKEND_API_URL}/api/recommendations/history?${params}`,
      {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      }
    );

    if (!response.ok) {
      const errorData = await response.json() as ErrorResponse;
      throw new Error(errorData.error || 'Failed to get recommendation history');
    }

    const data = await response.json() as RecommendationHistoryResponse;
    return data;
  } catch (error) {
    console.error('Error getting recommendation history:', error);
    throw error;
  }
}

/**
 * Delete all recommendations for a patient (GDPR compliance)
 * 
 * @param patientId - Patient identifier
 * @returns Promise with deletion result
 * 
 * @example
 * const result = await deletePatientRecommendations('patient123');
 * console.log(`Deleted ${result.deleted_count} recommendations`);
 */
export async function deletePatientRecommendations(
  patientId: string
): Promise<{ success: boolean; message: string; deleted_count: number }> {
  try {
    const response = await fetch(
      `${BACKEND_API_URL}/api/recommendations/delete`,
      {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ patient_id: patientId }),
      }
    );

    if (!response.ok) {
      const errorData = await response.json() as ErrorResponse;
      throw new Error(errorData.error || 'Failed to delete recommendations');
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error deleting recommendations:', error);
    throw error;
  }
}

// ==================== Utility Functions ====================

/**
 * Get priority badge color for UI display
 * 
 * @param priority - Priority level
 * @returns Tailwind CSS color classes
 * 
 * @example
 * const color = getPriorityBadgeColor('critical');
 * // Returns: "bg-red-100 text-red-800 border-red-200"
 */
export function getPriorityBadgeColor(
  priority: 'critical' | 'high' | 'medium' | 'low'
): string {
  switch (priority) {
    case 'critical':
      return 'bg-red-100 text-red-800 border-red-200';
    case 'high':
      return 'bg-orange-100 text-orange-800 border-orange-200';
    case 'medium':
      return 'bg-yellow-100 text-yellow-800 border-yellow-200';
    case 'low':
      return 'bg-blue-100 text-blue-800 border-blue-200';
    default:
      return 'bg-gray-100 text-gray-800 border-gray-200';
  }
}

/**
 * Get priority icon for UI display
 * 
 * @param priority - Priority level
 * @returns Emoji icon
 */
export function getPriorityIcon(
  priority: 'critical' | 'high' | 'medium' | 'low'
): string {
  switch (priority) {
    case 'critical':
      return '🚨';
    case 'high':
      return '⚠️';
    case 'medium':
      return '📌';
    case 'low':
      return '💡';
    default:
      return '📋';
  }
}

/**
 * Get category badge color for UI display
 * 
 * @param category - Recommendation category
 * @returns Tailwind CSS color classes
 */
export function getCategoryBadgeColor(
  category: Recommendation['category']
): string {
  switch (category) {
    case 'medication':
      return 'bg-purple-100 text-purple-800 border-purple-200';
    case 'monitoring':
      return 'bg-blue-100 text-blue-800 border-blue-200';
    case 'diet':
      return 'bg-green-100 text-green-800 border-green-200';
    case 'exercise':
      return 'bg-indigo-100 text-indigo-800 border-indigo-200';
    case 'mental_health':
      return 'bg-pink-100 text-pink-800 border-pink-200';
    case 'preventive':
      return 'bg-teal-100 text-teal-800 border-teal-200';
    case 'lifestyle':
    default:
      return 'bg-gray-100 text-gray-800 border-gray-200';
  }
}

/**
 * Get category icon for UI display
 * 
 * @param category - Recommendation category
 * @returns Emoji icon
 */
export function getCategoryIcon(category: Recommendation['category']): string {
  switch (category) {
    case 'medication':
      return '💊';
    case 'monitoring':
      return '📊';
    case 'diet':
      return '🥗';
    case 'exercise':
      return '🏃';
    case 'mental_health':
      return '🧠';
    case 'preventive':
      return '🛡️';
    case 'lifestyle':
    default:
      return '🌟';
  }
}

/**
 * Get severity badge color for vital concerns
 * 
 * @param severity - Severity level
 * @returns Tailwind CSS color classes
 */
export function getSeverityBadgeColor(
  severity: 'high' | 'medium' | 'low'
): string {
  switch (severity) {
    case 'high':
      return 'bg-red-100 text-red-800 border-red-200';
    case 'medium':
      return 'bg-yellow-100 text-yellow-800 border-yellow-200';
    case 'low':
      return 'bg-green-100 text-green-800 border-green-200';
    default:
      return 'bg-gray-100 text-gray-800 border-gray-200';
  }
}

/**
 * Format category name for display
 * 
 * @param category - Category key
 * @returns Formatted category name
 * 
 * @example
 * formatCategoryName('mental_health'); // "Mental Health"
 */
export function formatCategoryName(category: string): string {
  return category
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
}

/**
 * Filter recommendations by priority
 * 
 * @param recommendations - Array of recommendations
 * @param priorities - Priority levels to include
 * @returns Filtered recommendations
 */
export function filterByPriority(
  recommendations: Recommendation[],
  priorities: Array<'critical' | 'high' | 'medium' | 'low'>
): Recommendation[] {
  return recommendations.filter(rec => priorities.includes(rec.priority));
}

/**
 * Filter recommendations by category
 * 
 * @param recommendations - Array of recommendations
 * @param categories - Categories to include
 * @returns Filtered recommendations
 */
export function filterByCategory(
  recommendations: Recommendation[],
  categories: Recommendation['category'][]
): Recommendation[] {
  return recommendations.filter(rec => categories.includes(rec.category));
}

/**
 * Get recommendations requiring medical consultation
 * 
 * @param recommendations - Array of recommendations
 * @returns Recommendations that require consultation
 */
export function getConsultationRequired(
  recommendations: Recommendation[]
): Recommendation[] {
  return recommendations.filter(rec => rec.requires_consultation);
}

/**
 * Group recommendations by category
 * 
 * @param recommendations - Array of recommendations
 * @returns Object with categories as keys
 */
export function groupByCategory(
  recommendations: Recommendation[]
): Record<string, Recommendation[]> {
  return recommendations.reduce((groups, rec) => {
    const category = rec.category;
    if (!groups[category]) {
      groups[category] = [];
    }
    groups[category].push(rec);
    return groups;
  }, {} as Record<string, Recommendation[]>);
}

/**
 * Get top N recommendations by priority
 * 
 * @param recommendations - Array of recommendations
 * @param count - Number of top recommendations to return
 * @returns Top N recommendations
 */
export function getTopRecommendations(
  recommendations: Recommendation[],
  count: number = 5
): Recommendation[] {
  return recommendations
    .sort((a, b) => a.rank - b.rank)
    .slice(0, count);
}

/**
 * Check if AI recommendations are available
 * 
 * @returns Promise resolving to true if available, false otherwise
 */
export async function isRecommendationsAvailable(): Promise<boolean> {
  try {
    const response = await fetch(`${BACKEND_API_URL}/api/health`);
    const data = await response.json();
    return data.apis?.ai_recommendations === '✅ Available';
  } catch {
    return false;
  }
}

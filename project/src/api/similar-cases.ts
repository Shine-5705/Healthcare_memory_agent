/**
 * Similar Patient Cases API Client
 * TypeScript client for retrieving similar historical cases for clinical decision support
 */

const BACKEND_API_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:5000';

// ==================== TypeScript Interfaces ====================

export interface VitalsSummary {
  systolic_bp?: number;
  diastolic_bp?: number;
  heart_rate?: number;
  blood_glucose?: number;
  oxygen_saturation?: number;
  temperature?: number;
  respiratory_rate?: number;
  weight?: number;
  [key: string]: number | undefined;
}

export interface SimilarityBreakdown {
  symptoms: number;
  conditions: number;
  vitals: number;
  demographics: number;
  treatments: number;
  vector: number;
}

export interface SimilarCase {
  case_id: string;
  similarity_score: number;
  similarity_breakdown: SimilarityBreakdown;
  shared_symptoms: string[];
  shared_conditions: string[];
  case_date: string;
  age_range: 'pediatric' | 'young_adult' | 'adult' | 'middle_age' | 'senior' | 'unknown';
  gender: string;
  outcome: string;
  treatments: string[];
  vitals_summary: VitalsSummary;
  case_notes: string;
  anonymized_patient_id: string;
}

export interface FindSimilarCasesOptions {
  top_k?: number;
  min_similarity?: number;
  include_demographics?: boolean;
}

export interface FindSimilarCasesResponse {
  success: boolean;
  patient_id: string;
  total_cases_found: number;
  similar_cases: SimilarCase[];
  search_params: {
    top_k: number;
    min_similarity: number;
  };
}

export interface IndexCaseRequest {
  patient_id: string;
  case_date: string;
  symptoms: string[];
  conditions: string[];
  vitals_summary: VitalsSummary;
  demographics: {
    age: number;
    gender: string;
  };
  treatments?: string[];
  outcome?: string;
  case_notes?: string;
}

export interface IndexCaseResponse {
  success: boolean;
  case_id: string;
  message: string;
}

export interface CaseStatistics {
  total_cases: number;
  most_common_conditions: Record<string, number>;
  most_common_symptoms: Record<string, number>;
  age_distribution: Record<string, number>;
  outcome_distribution: Record<string, number>;
  collection_size_mb: number;
}

export interface CaseStatisticsResponse {
  success: boolean;
  statistics: CaseStatistics;
}

export interface ErrorResponse {
  success: false;
  error: string;
}

// ==================== API Functions ====================

/**
 * Find similar historical patient cases for clinical decision support
 * 
 * @param patientId - Patient identifier
 * @param options - Search configuration options
 * @returns Promise with similar cases
 * 
 * @example
 * const result = await findSimilarCases('patient123', {
 *   top_k: 5,
 *   min_similarity: 0.3,
 *   include_demographics: true
 * });
 * console.log(`Found ${result.total_cases_found} similar cases`);
 * result.similar_cases.forEach(case => {
 *   console.log(`${case.case_id}: ${case.similarity_score} similarity`);
 *   console.log(`Shared conditions: ${case.shared_conditions.join(', ')}`);
 *   console.log(`Outcome: ${case.outcome}`);
 * });
 */
export async function findSimilarCases(
  patientId: string,
  options: FindSimilarCasesOptions = {}
): Promise<FindSimilarCasesResponse> {
  try {
    const requestBody = {
      patient_id: patientId,
      top_k: options.top_k ?? 5,
      min_similarity: options.min_similarity ?? 0.3,
    };

    const response = await fetch(
      `${BACKEND_API_URL}/api/similar-cases/find`,
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
      throw new Error(errorData.error || 'Failed to find similar cases');
    }

    const data = await response.json() as FindSimilarCasesResponse;
    return data;
  } catch (error) {
    console.error('Error finding similar cases:', error);
    throw error;
  }
}

/**
 * Index a patient case for future similarity searches
 * 
 * @param caseData - Case information to index
 * @returns Promise with case ID
 * 
 * @example
 * const result = await indexPatientCase({
 *   patient_id: 'patient123',
 *   case_date: '2025-12-15',
 *   symptoms: ['chest pain', 'fatigue'],
 *   conditions: ['Hypertension', 'Type 2 Diabetes'],
 *   vitals_summary: { systolic_bp: 155, blood_glucose: 180 },
 *   demographics: { age: 55, gender: 'male' },
 *   treatments: ['Metformin', 'Lisinopril'],
 *   outcome: 'Improved with medication',
 *   case_notes: 'Patient responded well to treatment'
 * });
 * console.log(`Indexed case: ${result.case_id}`);
 */
export async function indexPatientCase(
  caseData: IndexCaseRequest
): Promise<IndexCaseResponse> {
  try {
    const response = await fetch(
      `${BACKEND_API_URL}/api/similar-cases/index`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(caseData),
      }
    );

    if (!response.ok) {
      const errorData = await response.json() as ErrorResponse;
      throw new Error(errorData.error || 'Failed to index case');
    }

    const data = await response.json() as IndexCaseResponse;
    return data;
  } catch (error) {
    console.error('Error indexing case:', error);
    throw error;
  }
}

/**
 * Get statistics about the case database
 * 
 * @returns Promise with database statistics
 * 
 * @example
 * const result = await getCaseStatistics();
 * console.log(`Total cases: ${result.statistics.total_cases}`);
 * console.log('Most common conditions:', result.statistics.most_common_conditions);
 */
export async function getCaseStatistics(): Promise<CaseStatisticsResponse> {
  try {
    const response = await fetch(
      `${BACKEND_API_URL}/api/similar-cases/statistics`,
      {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      }
    );

    if (!response.ok) {
      const errorData = await response.json() as ErrorResponse;
      throw new Error(errorData.error || 'Failed to get case statistics');
    }

    const data = await response.json() as CaseStatisticsResponse;
    return data;
  } catch (error) {
    console.error('Error getting case statistics:', error);
    throw error;
  }
}

/**
 * Delete all cases for a patient (GDPR compliance)
 * 
 * @param patientId - Patient identifier
 * @returns Promise with deletion result
 * 
 * @example
 * const result = await deletePatientCases('patient123');
 * console.log(`Deleted ${result.deleted_count} cases`);
 */
export async function deletePatientCases(
  patientId: string
): Promise<{ success: boolean; message: string; deleted_count: number }> {
  try {
    const response = await fetch(
      `${BACKEND_API_URL}/api/similar-cases/delete`,
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
      throw new Error(errorData.error || 'Failed to delete cases');
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error deleting cases:', error);
    throw error;
  }
}

// ==================== Utility Functions ====================

/**
 * Get similarity score badge color for UI display
 * 
 * @param score - Similarity score (0-1)
 * @returns Tailwind CSS color classes
 */
export function getSimilarityBadgeColor(score: number): string {
  if (score >= 0.8) {
    return 'bg-green-100 text-green-800 border-green-200';
  } else if (score >= 0.6) {
    return 'bg-blue-100 text-blue-800 border-blue-200';
  } else if (score >= 0.4) {
    return 'bg-yellow-100 text-yellow-800 border-yellow-200';
  } else {
    return 'bg-gray-100 text-gray-800 border-gray-200';
  }
}

/**
 * Get similarity score label for display
 * 
 * @param score - Similarity score (0-1)
 * @returns Human-readable label
 */
export function getSimilarityLabel(score: number): string {
  if (score >= 0.8) {
    return 'Very High';
  } else if (score >= 0.6) {
    return 'High';
  } else if (score >= 0.4) {
    return 'Moderate';
  } else if (score >= 0.2) {
    return 'Low';
  } else {
    return 'Very Low';
  }
}

/**
 * Get age range badge color for UI display
 * 
 * @param ageRange - Age range category
 * @returns Tailwind CSS color classes
 */
export function getAgeRangeBadgeColor(
  ageRange: SimilarCase['age_range']
): string {
  switch (ageRange) {
    case 'pediatric':
      return 'bg-pink-100 text-pink-800 border-pink-200';
    case 'young_adult':
      return 'bg-blue-100 text-blue-800 border-blue-200';
    case 'adult':
      return 'bg-indigo-100 text-indigo-800 border-indigo-200';
    case 'middle_age':
      return 'bg-purple-100 text-purple-800 border-purple-200';
    case 'senior':
      return 'bg-gray-100 text-gray-800 border-gray-200';
    default:
      return 'bg-gray-100 text-gray-600 border-gray-200';
  }
}

/**
 * Format age range for display
 * 
 * @param ageRange - Age range category
 * @returns Human-readable age range
 */
export function formatAgeRange(ageRange: SimilarCase['age_range']): string {
  switch (ageRange) {
    case 'pediatric':
      return '< 18 years';
    case 'young_adult':
      return '18-34 years';
    case 'adult':
      return '35-49 years';
    case 'middle_age':
      return '50-64 years';
    case 'senior':
      return '65+ years';
    default:
      return 'Unknown';
  }
}

/**
 * Get outcome badge color for UI display
 * 
 * @param outcome - Treatment outcome text
 * @returns Tailwind CSS color classes
 */
export function getOutcomeBadgeColor(outcome: string): string {
  const outcomeLower = outcome.toLowerCase();
  
  if (outcomeLower.includes('improv') || outcomeLower.includes('good') || outcomeLower.includes('success')) {
    return 'bg-green-100 text-green-800 border-green-200';
  } else if (outcomeLower.includes('partial') || outcomeLower.includes('stable')) {
    return 'bg-yellow-100 text-yellow-800 border-yellow-200';
  } else if (outcomeLower.includes('no change') || outcomeLower.includes('ongoing')) {
    return 'bg-blue-100 text-blue-800 border-blue-200';
  } else if (outcomeLower.includes('worsen') || outcomeLower.includes('decline')) {
    return 'bg-red-100 text-red-800 border-red-200';
  } else {
    return 'bg-gray-100 text-gray-800 border-gray-200';
  }
}

/**
 * Format vitals summary for display
 * 
 * @param vitals - Vitals summary object
 * @returns Formatted vitals string
 */
export function formatVitals(vitals: VitalsSummary): string {
  const vitalsList = [];
  
  if (vitals.systolic_bp && vitals.diastolic_bp) {
    vitalsList.push(`BP: ${vitals.systolic_bp}/${vitals.diastolic_bp} mmHg`);
  }
  if (vitals.heart_rate) {
    vitalsList.push(`HR: ${vitals.heart_rate} bpm`);
  }
  if (vitals.blood_glucose) {
    vitalsList.push(`Glucose: ${vitals.blood_glucose} mg/dL`);
  }
  if (vitals.oxygen_saturation) {
    vitalsList.push(`O2: ${vitals.oxygen_saturation}%`);
  }
  if (vitals.temperature) {
    vitalsList.push(`Temp: ${vitals.temperature}°F`);
  }
  
  return vitalsList.join(', ');
}

/**
 * Sort cases by similarity score (descending)
 * 
 * @param cases - Array of similar cases
 * @returns Sorted array
 */
export function sortBySimilarity(cases: SimilarCase[]): SimilarCase[] {
  return [...cases].sort((a, b) => b.similarity_score - a.similarity_score);
}

/**
 * Filter cases by minimum similarity score
 * 
 * @param cases - Array of similar cases
 * @param minScore - Minimum similarity score
 * @returns Filtered array
 */
export function filterByMinSimilarity(
  cases: SimilarCase[],
  minScore: number
): SimilarCase[] {
  return cases.filter(case_ => case_.similarity_score >= minScore);
}

/**
 * Filter cases by shared conditions
 * 
 * @param cases - Array of similar cases
 * @param conditions - Required conditions
 * @returns Filtered array
 */
export function filterBySharedConditions(
  cases: SimilarCase[],
  conditions: string[]
): SimilarCase[] {
  return cases.filter(case_ => 
    conditions.some(condition => 
      case_.shared_conditions.includes(condition)
    )
  );
}

/**
 * Group cases by outcome
 * 
 * @param cases - Array of similar cases
 * @returns Object with outcomes as keys
 */
export function groupByOutcome(
  cases: SimilarCase[]
): Record<string, SimilarCase[]> {
  return cases.reduce((groups, case_) => {
    const outcome = case_.outcome || 'unknown';
    if (!groups[outcome]) {
      groups[outcome] = [];
    }
    groups[outcome].push(case_);
    return groups;
  }, {} as Record<string, SimilarCase[]>);
}

/**
 * Get cases with successful outcomes
 * 
 * @param cases - Array of similar cases
 * @returns Cases with positive outcomes
 */
export function getSuccessfulCases(cases: SimilarCase[]): SimilarCase[] {
  return cases.filter(case_ => {
    const outcome = case_.outcome.toLowerCase();
    return outcome.includes('improv') || 
           outcome.includes('good') || 
           outcome.includes('success') ||
           outcome.includes('recover');
  });
}

/**
 * Extract all unique treatments from cases
 * 
 * @param cases - Array of similar cases
 * @returns Array of unique treatments
 */
export function extractUniqueTreatments(cases: SimilarCase[]): string[] {
  const treatments = new Set<string>();
  cases.forEach(case_ => {
    case_.treatments.forEach(treatment => treatments.add(treatment));
  });
  return Array.from(treatments).sort();
}

/**
 * Calculate average similarity by component
 * 
 * @param cases - Array of similar cases
 * @returns Average scores for each similarity component
 */
export function calculateAverageSimilarity(
  cases: SimilarCase[]
): SimilarityBreakdown {
  if (cases.length === 0) {
    return {
      symptoms: 0,
      conditions: 0,
      vitals: 0,
      demographics: 0,
      treatments: 0,
      vector: 0,
    };
  }

  const totals: SimilarityBreakdown = {
    symptoms: 0,
    conditions: 0,
    vitals: 0,
    demographics: 0,
    treatments: 0,
    vector: 0,
  };

  cases.forEach(case_ => {
    Object.keys(totals).forEach(key => {
      totals[key as keyof SimilarityBreakdown] += 
        case_.similarity_breakdown[key as keyof SimilarityBreakdown];
    });
  });

  Object.keys(totals).forEach(key => {
    totals[key as keyof SimilarityBreakdown] /= cases.length;
  });

  return totals;
}

/**
 * Check if similar cases are available
 * 
 * @returns Promise resolving to true if available, false otherwise
 */
export async function isSimilarCasesAvailable(): Promise<boolean> {
  try {
    const response = await fetch(`${BACKEND_API_URL}/api/health`);
    const data = await response.json();
    return data.apis?.similar_cases === '✅ Available';
  } catch {
    return false;
  }
}

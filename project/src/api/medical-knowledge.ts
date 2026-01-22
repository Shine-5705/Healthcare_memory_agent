/**
 * Medical Knowledge Base API Client
 * TypeScript client for accessing medical condition information
 */

const BACKEND_API_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:5000';

// ==================== TypeScript Interfaces ====================

export interface MedicalCondition {
  condition_key: string;
  name: string;
  category: string;
  description: string;
  symptoms: string[];
  risk_factors: string[];
  treatments: string[];
  care_guidelines: string[];
  complications: string[];
}

export interface SearchResult extends MedicalCondition {
  confidence_score: number;
  relevance: 'high' | 'medium' | 'low';
}

export interface ConditionSummary {
  key: string;
  name: string;
  category: string;
  description: string;
}

export interface SearchResponse {
  success: boolean;
  query: string;
  results_count: number;
  results: SearchResult[];
}

export interface ConditionsListResponse {
  success: boolean;
  total_conditions: number;
  conditions: ConditionSummary[];
}

export interface ConditionDetailsResponse {
  success: boolean;
  condition: MedicalCondition;
}

export interface CategoryResponse {
  success: boolean;
  category: string;
  total_conditions: number;
  conditions: ConditionSummary[];
}

export interface ErrorResponse {
  success: false;
  error: string;
}

// ==================== API Functions ====================

/**
 * Search medical knowledge base using semantic search
 * Returns top matching conditions with confidence scores
 * 
 * @param query - User's health question or search query
 * @param limit - Number of top matches to return (default: 3)
 * @returns Promise with search results
 * 
 * @example
 * const results = await searchMedicalKnowledge('how to manage high blood sugar', 3);
 * console.log(results.results[0].name); // "Type 2 Diabetes"
 * console.log(results.results[0].confidence_score); // 0.545
 */
export async function searchMedicalKnowledge(
  query: string,
  limit: number = 3
): Promise<SearchResponse> {
  try {
    const params = new URLSearchParams({
      query,
      limit: limit.toString()
    });

    const response = await fetch(
      `${BACKEND_API_URL}/api/knowledge/search?${params}`,
      {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      }
    );

    if (!response.ok) {
      const errorData = await response.json() as ErrorResponse;
      throw new Error(errorData.error || 'Failed to search medical knowledge');
    }

    const data = await response.json() as SearchResponse;
    return data;
  } catch (error) {
    console.error('Error searching medical knowledge:', error);
    throw error;
  }
}

/**
 * Get list of all available medical conditions in knowledge base
 * 
 * @returns Promise with list of all conditions
 * 
 * @example
 * const { conditions } = await getAllConditions();
 * console.log(conditions.length); // 21
 * console.log(conditions[0].name); // "Type 2 Diabetes"
 */
export async function getAllConditions(): Promise<ConditionsListResponse> {
  try {
    const response = await fetch(
      `${BACKEND_API_URL}/api/knowledge/conditions`,
      {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      }
    );

    if (!response.ok) {
      const errorData = await response.json() as ErrorResponse;
      throw new Error(errorData.error || 'Failed to get conditions list');
    }

    const data = await response.json() as ConditionsListResponse;
    return data;
  } catch (error) {
    console.error('Error getting conditions list:', error);
    throw error;
  }
}

/**
 * Get detailed information about a specific medical condition
 * 
 * @param conditionKey - The condition key (e.g., 'diabetes_type2', 'hypertension')
 * @returns Promise with detailed condition information
 * 
 * @example
 * const { condition } = await getConditionDetails('diabetes_type2');
 * console.log(condition.name); // "Type 2 Diabetes"
 * console.log(condition.treatments.length); // 8
 * console.log(condition.symptoms); // Array of symptoms
 */
export async function getConditionDetails(
  conditionKey: string
): Promise<ConditionDetailsResponse> {
  try {
    const response = await fetch(
      `${BACKEND_API_URL}/api/knowledge/condition/${encodeURIComponent(conditionKey)}`,
      {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      }
    );

    if (!response.ok) {
      const errorData = await response.json() as ErrorResponse;
      throw new Error(errorData.error || 'Failed to get condition details');
    }

    const data = await response.json() as ConditionDetailsResponse;
    return data;
  } catch (error) {
    console.error('Error getting condition details:', error);
    throw error;
  }
}

/**
 * Search medical conditions by category
 * 
 * @param category - The category name (e.g., 'Cardiovascular', 'Mental Health', 'Respiratory')
 * @returns Promise with conditions in the specified category
 * 
 * @example
 * const { conditions } = await searchByCategory('Mental Health');
 * console.log(conditions.length); // 2
 * console.log(conditions[0].name); // "Major Depressive Disorder"
 */
export async function searchByCategory(
  category: string
): Promise<CategoryResponse> {
  try {
    const response = await fetch(
      `${BACKEND_API_URL}/api/knowledge/category/${encodeURIComponent(category)}`,
      {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      }
    );

    if (!response.ok) {
      const errorData = await response.json() as ErrorResponse;
      throw new Error(errorData.error || 'Failed to search by category');
    }

    const data = await response.json() as CategoryResponse;
    return data;
  } catch (error) {
    console.error('Error searching by category:', error);
    throw error;
  }
}

// ==================== Utility Functions ====================

/**
 * Get condition categories available in knowledge base
 * Extracts unique categories from all conditions
 * 
 * @returns Promise with list of unique categories
 */
export async function getAvailableCategories(): Promise<string[]> {
  try {
    const { conditions } = await getAllConditions();
    const categories = [...new Set(conditions.map(c => c.category))];
    return categories.sort();
  } catch (error) {
    console.error('Error getting categories:', error);
    throw error;
  }
}

/**
 * Format confidence score for display
 * 
 * @param score - Confidence score (0-1)
 * @returns Formatted percentage string
 * 
 * @example
 * formatConfidenceScore(0.703); // "70%"
 */
export function formatConfidenceScore(score: number): string {
  return `${Math.round(score * 100)}%`;
}

/**
 * Get relevance badge color based on confidence score
 * 
 * @param relevance - Relevance level ('high', 'medium', 'low')
 * @returns Tailwind CSS color class
 * 
 * @example
 * getRelevanceBadgeColor('high'); // "bg-green-100 text-green-800"
 */
export function getRelevanceBadgeColor(
  relevance: 'high' | 'medium' | 'low'
): string {
  switch (relevance) {
    case 'high':
      return 'bg-green-100 text-green-800 border-green-200';
    case 'medium':
      return 'bg-yellow-100 text-yellow-800 border-yellow-200';
    case 'low':
      return 'bg-gray-100 text-gray-800 border-gray-200';
    default:
      return 'bg-gray-100 text-gray-800 border-gray-200';
  }
}

/**
 * Get category icon emoji
 * 
 * @param category - Category name
 * @returns Emoji representing the category
 */
export function getCategoryIcon(category: string): string {
  const icons: Record<string, string> = {
    'Metabolic Disorder': '🩸',
    'Cardiovascular': '❤️',
    'Respiratory': '🫁',
    'Autoimmune/Musculoskeletal': '🦴',
    'Musculoskeletal': '🦴',
    'Mental Health': '🧠',
    'Renal': '🫘',
    'Neurological': '🧠',
    'Endocrine': '🦠',
    'Gastrointestinal': '🫃',
    'Musculoskeletal/Chronic Pain': '💊',
    'Autoimmune': '🛡️',
    'Autoimmune/Dermatological': '🩹',
    'Respiratory/Sleep Disorder': '😴',
  };
  
  return icons[category] || '📋';
}

/**
 * Check if medical knowledge base is available
 * 
 * @returns Promise resolving to true if available, false otherwise
 */
export async function isMedicalKnowledgeAvailable(): Promise<boolean> {
  try {
    const response = await fetch(`${BACKEND_API_URL}/api/health`);
    const data = await response.json();
    return data.apis?.medical_knowledge === '✅ Available';
  } catch {
    return false;
  }
}

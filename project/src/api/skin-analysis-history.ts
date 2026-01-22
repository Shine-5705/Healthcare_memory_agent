/**
 * Skin Analysis History API Client
 * 
 * TypeScript client for interacting with the Qdrant-powered skin analysis history system.
 * Provides functions for finding similar skin cases, retrieving patient history,
 * and accessing statistics on historical analyses.
 */

const API_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:5000';

// ============================================================================
// Type Definitions
// ============================================================================

/**
 * Represents a single skin analysis case from history
 */
export interface SkinAnalysisCase {
  case_id: string;
  patient_id_hash: string;
  diagnosis: string;
  severity: 'mild' | 'moderate' | 'severe';
  confidence: number;
  recommendations: string[];
  affected_areas: string[];
  category: string;
  observations?: string;
  follow_up_needed: boolean;
  timestamp: string;
  similarity_score?: number;
  pattern_match?: string;
}

/**
 * Statistics about skin analysis cases by category
 */
export interface CategoryStatistics {
  total_cases: number;
  category_distribution: Record<string, number>;
  severity_distribution: Record<string, number>;
  follow_up_distribution: {
    needed: number;
    not_needed: number;
  };
  average_confidence: number;
  confidence_range: {
    min: number;
    max: number;
  };
}

/**
 * Patient's historical skin analyses
 */
export interface PatientSkinHistory {
  patient_id: string;
  total_analyses: number;
  analyses: SkinAnalysisCase[];
}

/**
 * Options for finding similar skin cases
 */
export interface FindSimilarCasesOptions {
  diagnosis: string;
  severity?: 'mild' | 'moderate' | 'severe';
  recommendations?: string[];
  affected_areas?: string[];
  top_k?: number;
  min_confidence?: number;
  category_filter?: string;
}

/**
 * Pattern insights from similar cases
 */
export interface PatternInsights {
  severity_patterns: string[];
  common_treatments: string[];
  follow_up_frequency: string;
  high_similarity_cases: number;
}

// ============================================================================
// Core API Functions
// ============================================================================

/**
 * Find similar skin analysis cases based on diagnosis and symptoms
 */
export async function findSimilarSkinCases(
  options: FindSimilarCasesOptions
): Promise<SkinAnalysisCase[]> {
  try {
    const response = await fetch(`${API_URL}/api/skin-analysis/similar-cases`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(options),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data.similar_cases || [];
  } catch (error) {
    console.error('Error finding similar skin cases:', error);
    throw error;
  }
}

/**
 * Get patient's historical skin analyses
 */
export async function getPatientSkinHistory(
  patientId: string,
  limit: number = 10
): Promise<PatientSkinHistory> {
  try {
    const response = await fetch(
      `${API_URL}/api/skin-analysis/patient-history?patient_id=${encodeURIComponent(patientId)}&limit=${limit}`,
      {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      }
    );

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return {
      patient_id: patientId,
      total_analyses: data.total_analyses || 0,
      analyses: data.analyses || [],
    };
  } catch (error) {
    console.error('Error getting patient skin history:', error);
    throw error;
  }
}

/**
 * Get statistics about skin analysis cases
 */
export async function getSkinAnalysisStatistics(): Promise<CategoryStatistics> {
  try {
    const response = await fetch(`${API_URL}/api/skin-analysis/statistics`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data.statistics;
  } catch (error) {
    console.error('Error getting skin analysis statistics:', error);
    throw error;
  }
}

/**
 * Delete all skin analyses for a patient (GDPR compliance)
 */
export async function deletePatientSkinAnalyses(
  patientId: string
): Promise<number> {
  try {
    const response = await fetch(
      `${API_URL}/api/skin-analysis/delete?patient_id=${encodeURIComponent(patientId)}`,
      {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
        },
      }
    );

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data.deleted_count || 0;
  } catch (error) {
    console.error('Error deleting patient skin analyses:', error);
    throw error;
  }
}

// ============================================================================
// Utility Functions
// ============================================================================

/**
 * Get color for severity level
 */
export function getSeverityColor(severity: string): string {
  const colors: Record<string, string> = {
    mild: 'text-green-600 bg-green-50',
    moderate: 'text-yellow-600 bg-yellow-50',
    severe: 'text-red-600 bg-red-50',
  };
  return colors[severity.toLowerCase()] || 'text-gray-600 bg-gray-50';
}

/**
 * Get emoji icon for severity
 */
export function getSeverityIcon(severity: string): string {
  const icons: Record<string, string> = {
    mild: '🟢',
    moderate: '🟡',
    severe: '🔴',
  };
  return icons[severity.toLowerCase()] || '⚪';
}

/**
 * Get color for category
 */
export function getCategoryColor(category: string): string {
  const colors: Record<string, string> = {
    acne: 'text-purple-600 bg-purple-50',
    eczema: 'text-blue-600 bg-blue-50',
    psoriasis: 'text-indigo-600 bg-indigo-50',
    rosacea: 'text-pink-600 bg-pink-50',
    fungal: 'text-orange-600 bg-orange-50',
    bacterial: 'text-red-600 bg-red-50',
    viral: 'text-rose-600 bg-rose-50',
    allergic: 'text-yellow-600 bg-yellow-50',
    pigmentation: 'text-amber-600 bg-amber-50',
    aging: 'text-slate-600 bg-slate-50',
    sun_damage: 'text-amber-700 bg-amber-100',
    other: 'text-gray-600 bg-gray-50',
  };
  return colors[category.toLowerCase()] || colors.other;
}

/**
 * Get display name for category
 */
export function getCategoryDisplayName(category: string): string {
  const names: Record<string, string> = {
    acne: 'Acne',
    eczema: 'Eczema/Dermatitis',
    psoriasis: 'Psoriasis',
    rosacea: 'Rosacea',
    fungal: 'Fungal Infection',
    bacterial: 'Bacterial Infection',
    viral: 'Viral Infection',
    allergic: 'Allergic Reaction',
    pigmentation: 'Pigmentation',
    aging: 'Aging',
    sun_damage: 'Sun Damage',
    other: 'Other',
  };
  return names[category.toLowerCase()] || 'Other';
}

/**
 * Get color for confidence level
 */
export function getConfidenceColor(confidence: number): string {
  if (confidence >= 0.8) return 'text-green-600 bg-green-50';
  if (confidence >= 0.6) return 'text-yellow-600 bg-yellow-50';
  return 'text-red-600 bg-red-50';
}

/**
 * Get confidence label
 */
export function getConfidenceLabel(confidence: number): string {
  if (confidence >= 0.8) return 'High';
  if (confidence >= 0.6) return 'Medium';
  return 'Low';
}

/**
 * Get color for similarity score
 */
export function getSimilarityColor(score: number): string {
  if (score >= 0.8) return 'text-green-600 bg-green-50 border-green-200';
  if (score >= 0.6) return 'text-blue-600 bg-blue-50 border-blue-200';
  if (score >= 0.4) return 'text-yellow-600 bg-yellow-50 border-yellow-200';
  return 'text-gray-600 bg-gray-50 border-gray-200';
}

/**
 * Get similarity badge text
 */
export function getSimilarityBadge(score: number): string {
  if (score >= 0.8) return 'Very Similar';
  if (score >= 0.6) return 'Similar';
  if (score >= 0.4) return 'Somewhat Similar';
  return 'Low Similarity';
}

/**
 * Get follow-up badge color
 */
export function getFollowUpColor(needed: boolean): string {
  return needed 
    ? 'text-red-600 bg-red-50 border-red-200'
    : 'text-green-600 bg-green-50 border-green-200';
}

/**
 * Format timestamp for display
 */
export function formatTimestamp(timestamp: string): string {
  const date = new Date(timestamp);
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

/**
 * Format date only
 */
export function formatDateOnly(timestamp: string): string {
  const date = new Date(timestamp);
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
}

/**
 * Get time ago string
 */
export function getTimeAgo(timestamp: string): string {
  const date = new Date(timestamp);
  const now = new Date();
  const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000);

  if (diffInSeconds < 60) return 'Just now';
  if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`;
  if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`;
  if (diffInSeconds < 604800) return `${Math.floor(diffInSeconds / 86400)}d ago`;
  if (diffInSeconds < 2592000) return `${Math.floor(diffInSeconds / 604800)}w ago`;
  return formatDateOnly(timestamp);
}

/**
 * Format affected areas for display
 */
export function formatAffectedAreas(areas: string[]): string {
  if (!areas || areas.length === 0) return 'Not specified';
  if (areas.length <= 3) return areas.join(', ');
  return `${areas.slice(0, 3).join(', ')} +${areas.length - 3} more`;
}

/**
 * Get area icon
 */
export function getAreaIcon(area: string): string {
  const icons: Record<string, string> = {
    face: '👤',
    hands: '✋',
    arms: '💪',
    legs: '🦵',
    torso: '🫁',
    scalp: '🧠',
    feet: '🦶',
    neck: '🦒',
    back: '🔙',
  };
  return icons[area.toLowerCase()] || '📍';
}

/**
 * Sort cases by similarity score (descending)
 */
export function sortBySimilarity(cases: SkinAnalysisCase[]): SkinAnalysisCase[] {
  return [...cases].sort((a, b) => 
    (b.similarity_score || 0) - (a.similarity_score || 0)
  );
}

/**
 * Sort cases by timestamp (newest first)
 */
export function sortByTimestamp(cases: SkinAnalysisCase[]): SkinAnalysisCase[] {
  return [...cases].sort((a, b) => 
    new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
  );
}

/**
 * Filter cases by minimum similarity
 */
export function filterByMinSimilarity(
  cases: SkinAnalysisCase[],
  minSimilarity: number
): SkinAnalysisCase[] {
  return cases.filter(c => (c.similarity_score || 0) >= minSimilarity);
}

/**
 * Filter cases by category
 */
export function filterByCategory(
  cases: SkinAnalysisCase[],
  category: string
): SkinAnalysisCase[] {
  return cases.filter(c => 
    c.category.toLowerCase() === category.toLowerCase()
  );
}

/**
 * Filter cases by severity
 */
export function filterBySeverity(
  cases: SkinAnalysisCase[],
  severity: string
): SkinAnalysisCase[] {
  return cases.filter(c => 
    c.severity.toLowerCase() === severity.toLowerCase()
  );
}

/**
 * Filter cases requiring follow-up
 */
export function filterByFollowUp(
  cases: SkinAnalysisCase[],
  needsFollowUp: boolean
): SkinAnalysisCase[] {
  return cases.filter(c => c.follow_up_needed === needsFollowUp);
}

/**
 * Group cases by category
 */
export function groupByCategory(
  cases: SkinAnalysisCase[]
): Record<string, SkinAnalysisCase[]> {
  return cases.reduce((groups, case_) => {
    const category = case_.category;
    if (!groups[category]) {
      groups[category] = [];
    }
    groups[category].push(case_);
    return groups;
  }, {} as Record<string, SkinAnalysisCase[]>);
}

/**
 * Group cases by severity
 */
export function groupBySeverity(
  cases: SkinAnalysisCase[]
): Record<string, SkinAnalysisCase[]> {
  return cases.reduce((groups, case_) => {
    const severity = case_.severity;
    if (!groups[severity]) {
      groups[severity] = [];
    }
    groups[severity].push(case_);
    return groups;
  }, {} as Record<string, SkinAnalysisCase[]>);
}

/**
 * Extract unique recommendations from cases
 */
export function extractUniqueRecommendations(
  cases: SkinAnalysisCase[]
): string[] {
  const allRecommendations = cases.flatMap(c => c.recommendations);
  return Array.from(new Set(allRecommendations));
}

/**
 * Get most common recommendations
 */
export function getMostCommonRecommendations(
  cases: SkinAnalysisCase[],
  limit: number = 5
): Array<{ recommendation: string; count: number }> {
  const allRecommendations = cases.flatMap(c => c.recommendations);
  const counts = allRecommendations.reduce((acc, rec) => {
    acc[rec] = (acc[rec] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  return Object.entries(counts)
    .map(([recommendation, count]) => ({ recommendation, count }))
    .sort((a, b) => b.count - a.count)
    .slice(0, limit);
}

/**
 * Calculate average confidence from cases
 */
export function calculateAverageConfidence(cases: SkinAnalysisCase[]): number {
  if (cases.length === 0) return 0;
  const sum = cases.reduce((acc, c) => acc + c.confidence, 0);
  return sum / cases.length;
}

/**
 * Calculate average similarity from cases
 */
export function calculateAverageSimilarity(cases: SkinAnalysisCase[]): number {
  if (cases.length === 0) return 0;
  const casesWithScore = cases.filter(c => c.similarity_score !== undefined);
  if (casesWithScore.length === 0) return 0;
  const sum = casesWithScore.reduce((acc, c) => acc + (c.similarity_score || 0), 0);
  return sum / casesWithScore.length;
}

/**
 * Get severity distribution from statistics
 */
export function getSeverityDistribution(
  stats: CategoryStatistics
): Array<{ severity: string; count: number; percentage: number }> {
  const total = stats.total_cases;
  return Object.entries(stats.severity_distribution).map(([severity, count]) => ({
    severity,
    count,
    percentage: total > 0 ? (count / total) * 100 : 0,
  }));
}

/**
 * Get category distribution from statistics
 */
export function getCategoryDistribution(
  stats: CategoryStatistics
): Array<{ category: string; count: number; percentage: number }> {
  const total = stats.total_cases;
  return Object.entries(stats.category_distribution)
    .map(([category, count]) => ({
      category,
      count,
      percentage: total > 0 ? (count / total) * 100 : 0,
    }))
    .sort((a, b) => b.count - a.count);
}

/**
 * Generate pattern insights from similar cases
 */
export function generatePatternInsights(
  cases: SkinAnalysisCase[]
): PatternInsights {
  if (cases.length === 0) {
    return {
      severity_patterns: [],
      common_treatments: [],
      follow_up_frequency: 'No data',
      high_similarity_cases: 0,
    };
  }

  // Severity patterns
  const severityCounts = cases.reduce((acc, c) => {
    acc[c.severity] = (acc[c.severity] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);
  
  const severity_patterns = Object.entries(severityCounts)
    .sort((a, b) => b[1] - a[1])
    .map(([severity, count]) => 
      `${severity}: ${count}/${cases.length} cases (${Math.round((count / cases.length) * 100)}%)`
    );

  // Common treatments
  const recommendationCounts = getMostCommonRecommendations(cases, 5);
  const common_treatments = recommendationCounts.map(r => 
    `${r.recommendation} (${r.count} cases)`
  );

  // Follow-up frequency
  const followUpCount = cases.filter(c => c.follow_up_needed).length;
  const followUpPercentage = Math.round((followUpCount / cases.length) * 100);
  const follow_up_frequency = `${followUpCount}/${cases.length} cases (${followUpPercentage}%) require follow-up`;

  // High similarity cases
  const high_similarity_cases = cases.filter(c => 
    (c.similarity_score || 0) >= 0.8
  ).length;

  return {
    severity_patterns,
    common_treatments,
    follow_up_frequency,
    high_similarity_cases,
  };
}

/**
 * Check if patient needs follow-up based on history
 */
export function needsFollowUp(history: PatientSkinHistory): boolean {
  if (history.analyses.length === 0) return false;
  
  // Check most recent analysis
  const recent = history.analyses[0];
  return recent.follow_up_needed;
}

/**
 * Get trend from patient history (improving, worsening, stable)
 */
export function getPatientTrend(history: PatientSkinHistory): string {
  if (history.analyses.length < 2) return 'insufficient_data';
  
  const sorted = sortByTimestamp(history.analyses);
  const recent = sorted[0];
  const previous = sorted[1];
  
  const severityOrder = { mild: 1, moderate: 2, severe: 3 };
  const recentScore = severityOrder[recent.severity];
  const previousScore = severityOrder[previous.severity];
  
  if (recentScore < previousScore) return 'improving';
  if (recentScore > previousScore) return 'worsening';
  return 'stable';
}

/**
 * Get trend icon
 */
export function getTrendIcon(trend: string): string {
  const icons: Record<string, string> = {
    improving: '📈 Improving',
    worsening: '📉 Worsening',
    stable: '➡️ Stable',
    insufficient_data: '❓ Insufficient Data',
  };
  return icons[trend] || icons.insufficient_data;
}

/**
 * Get trend color
 */
export function getTrendColor(trend: string): string {
  const colors: Record<string, string> = {
    improving: 'text-green-600 bg-green-50',
    worsening: 'text-red-600 bg-red-50',
    stable: 'text-blue-600 bg-blue-50',
    insufficient_data: 'text-gray-600 bg-gray-50',
  };
  return colors[trend] || colors.insufficient_data;
}

export default {
  // Core API
  findSimilarSkinCases,
  getPatientSkinHistory,
  getSkinAnalysisStatistics,
  deletePatientSkinAnalyses,
  
  // Display utilities
  getSeverityColor,
  getSeverityIcon,
  getCategoryColor,
  getCategoryDisplayName,
  getConfidenceColor,
  getConfidenceLabel,
  getSimilarityColor,
  getSimilarityBadge,
  getFollowUpColor,
  
  // Formatting
  formatTimestamp,
  formatDateOnly,
  getTimeAgo,
  formatAffectedAreas,
  getAreaIcon,
  
  // Filtering & sorting
  sortBySimilarity,
  sortByTimestamp,
  filterByMinSimilarity,
  filterByCategory,
  filterBySeverity,
  filterByFollowUp,
  
  // Grouping
  groupByCategory,
  groupBySeverity,
  
  // Analysis
  extractUniqueRecommendations,
  getMostCommonRecommendations,
  calculateAverageConfidence,
  calculateAverageSimilarity,
  getSeverityDistribution,
  getCategoryDistribution,
  generatePatternInsights,
  needsFollowUp,
  getPatientTrend,
  getTrendIcon,
  getTrendColor,
};

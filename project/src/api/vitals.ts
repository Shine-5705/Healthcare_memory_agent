// Vitals API integration
const BACKEND_API_URL = 'http://localhost:5000';

export interface VitalsData {
  systolic_bp?: number;
  diastolic_bp?: number;
  heart_rate?: number;
  glucose?: number;
  temperature?: number;
  oxygen_level?: number;
  notes?: string;
}

export interface VitalsRecord {
  id: string;
  timestamp: string;
  vitals: VitalsData;
  description: string;
  anomalies: Anomaly[];
  severity: 'normal' | 'warning' | 'critical';
}

export interface Anomaly {
  vital: string;
  value: number;
  severity: 'warning' | 'critical';
  message: string;
  normal_range: string;
}

export interface TrendAnalysis {
  patient_id: string;
  days_analyzed: number;
  total_readings: number;
  total_anomalies: number;
  critical_readings: number;
  trends: {
    [key: string]: {
      count: number;
      mean: number;
      median: number;
      min: number;
      max: number;
      latest: number;
      std_dev?: number;
      trend?: {
        direction: string;
        percentage: number;
      };
      normal_range?: string;
      in_normal_range?: boolean;
    };
  };
  alerts: Array<{
    type: string;
    vital: string;
    message: string;
    severity: string;
  }>;
  latest_reading?: VitalsRecord;
  analysis_timestamp: string;
}

export interface StoreVitalsRequest {
  patientId: string;
  vitals: VitalsData;
  notes?: string;
}

export interface StoreVitalsResponse {
  vitalsId: string;
  anomalies: Anomaly[];
  hasAnomalies: boolean;
  success: boolean;
  message: string;
}

/**
 * Store patient vitals
 */
export const storeVitals = async (
  request: StoreVitalsRequest
): Promise<StoreVitalsResponse> => {
  try {
    const response = await fetch(`${BACKEND_API_URL}/api/vitals/store`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error storing vitals:', error);
    throw error;
  }
};

/**
 * Get vitals history for a patient
 */
export const getVitalsHistory = async (
  patientId: string,
  days: number = 30,
  limit: number = 100
): Promise<{ history: VitalsRecord[]; count: number; days: number; success: boolean }> => {
  try {
    const response = await fetch(
      `${BACKEND_API_URL}/api/vitals/history?patientId=${patientId}&days=${days}&limit=${limit}`,
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

    return await response.json();
  } catch (error) {
    console.error('Error fetching vitals history:', error);
    throw error;
  }
};

/**
 * Get trend analysis for patient vitals
 */
export const getTrendAnalysis = async (
  patientId: string,
  days: number = 30
): Promise<{ analysis: TrendAnalysis; success: boolean }> => {
  try {
    const response = await fetch(
      `${BACKEND_API_URL}/api/vitals/trend-analysis?patientId=${patientId}&days=${days}`,
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

    return await response.json();
  } catch (error) {
    console.error('Error fetching trend analysis:', error);
    throw error;
  }
};

/**
 * Get anomalous vitals readings
 */
export const getAnomalousReadings = async (
  patientId: string,
  days: number = 30
): Promise<{ anomalies: VitalsRecord[]; count: number; success: boolean }> => {
  try {
    const response = await fetch(
      `${BACKEND_API_URL}/api/vitals/anomalies?patientId=${patientId}&days=${days}`,
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

    return await response.json();
  } catch (error) {
    console.error('Error fetching anomalous readings:', error);
    throw error;
  }
};

/**
 * Find similar vitals patterns
 */
export const findSimilarVitals = async (
  patientId: string,
  currentVitals: VitalsData,
  limit: number = 10
): Promise<{ similar: VitalsRecord[]; count: number; success: boolean }> => {
  try {
    const response = await fetch(`${BACKEND_API_URL}/api/vitals/similar`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        patientId,
        vitals: currentVitals,
        limit,
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error finding similar vitals:', error);
    throw error;
  }
};

/**
 * Delete all vitals for a patient
 */
export const deletePatientVitals = async (
  patientId: string
): Promise<{ deletedCount: number; success: boolean; message: string }> => {
  try {
    const response = await fetch(`${BACKEND_API_URL}/api/vitals/delete`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ patientId }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error deleting patient vitals:', error);
    throw error;
  }
};

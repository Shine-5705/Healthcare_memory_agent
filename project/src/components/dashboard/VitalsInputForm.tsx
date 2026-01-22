import React, { useState } from 'react';

interface VitalAlert {
  vital: string;
  message: string;
  severity: 'normal' | 'warning' | 'critical';
}

interface VitalsData {
  bloodPressureSystolic: string;
  bloodPressureDiastolic: string;
  heartRate: string;
  temperature: string;
  oxygenSaturation: string;
  respiratoryRate: string;
  weight: string;
  height: string;
}

interface VitalsInputFormProps {
  onSubmit: (vitals: VitalsData) => Promise<void>;
  patientId: string;
}

const VitalsInputForm: React.FC<VitalsInputFormProps> = ({ onSubmit, patientId }) => {
  const [vitals, setVitals] = useState<VitalsData>({
    bloodPressureSystolic: '',
    bloodPressureDiastolic: '',
    heartRate: '',
    temperature: '',
    oxygenSaturation: '',
    respiratoryRate: '',
    weight: '',
    height: '',
  });

  const [alerts, setAlerts] = useState<VitalAlert[]>([]);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const checkVitalAlerts = (name: keyof VitalsData, value: string) => {
    const numValue = parseFloat(value);
    if (isNaN(numValue)) return;

    const newAlerts: VitalAlert[] = [];

    switch (name) {
      case 'bloodPressureSystolic':
        if (numValue > 140) {
          newAlerts.push({
            vital: 'Blood Pressure',
            message: 'Systolic pressure is high. Consider immediate evaluation.',
            severity: 'critical',
          });
        } else if (numValue > 130) {
          newAlerts.push({
            vital: 'Blood Pressure',
            message: 'Systolic pressure is elevated. Monitor closely.',
            severity: 'warning',
          });
        }
        break;

      case 'heartRate':
        if (numValue < 60) {
          newAlerts.push({
            vital: 'Heart Rate',
            message: 'Heart rate is low (bradycardia). Assess patient.',
            severity: 'warning',
          });
        } else if (numValue > 100) {
          newAlerts.push({
            vital: 'Heart Rate',
            message: 'Heart rate is high (tachycardia). Monitor patient.',
            severity: 'warning',
          });
        } else if (numValue > 120) {
          newAlerts.push({
            vital: 'Heart Rate',
            message: 'Heart rate is very high. Immediate attention needed.',
            severity: 'critical',
          });
        }
        break;

      case 'temperature':
        if (numValue < 36) {
          newAlerts.push({
            vital: 'Temperature',
            message: 'Temperature is low (hypothermia risk).',
            severity: 'warning',
          });
        } else if (numValue > 37.5 && numValue <= 38.5) {
          newAlerts.push({
            vital: 'Temperature',
            message: 'Mild fever detected. Monitor symptoms.',
            severity: 'warning',
          });
        } else if (numValue > 38.5) {
          newAlerts.push({
            vital: 'Temperature',
            message: 'High fever. Medical attention recommended.',
            severity: 'critical',
          });
        }
        break;

      case 'oxygenSaturation':
        if (numValue < 90) {
          newAlerts.push({
            vital: 'Oxygen Saturation',
            message: 'Critically low oxygen levels. Immediate intervention needed.',
            severity: 'critical',
          });
        } else if (numValue < 95) {
          newAlerts.push({
            vital: 'Oxygen Saturation',
            message: 'Oxygen saturation is low. Monitor closely.',
            severity: 'warning',
          });
        }
        break;

      case 'respiratoryRate':
        if (numValue < 12) {
          newAlerts.push({
            vital: 'Respiratory Rate',
            message: 'Breathing rate is low. Assess patient.',
            severity: 'warning',
          });
        } else if (numValue > 20) {
          newAlerts.push({
            vital: 'Respiratory Rate',
            message: 'Breathing rate is elevated. Monitor closely.',
            severity: 'warning',
          });
        }
        break;
    }

    setAlerts(prev => {
      const filtered = prev.filter(a => a.vital !== name);
      return [...filtered, ...newAlerts];
    });
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setVitals(prev => ({ ...prev, [name]: value }));
    checkVitalAlerts(name as keyof VitalsData, value);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);

    try {
      await onSubmit(vitals);
      // Reset form
      setVitals({
        bloodPressureSystolic: '',
        bloodPressureDiastolic: '',
        heartRate: '',
        temperature: '',
        oxygenSaturation: '',
        respiratoryRate: '',
        weight: '',
        height: '',
      });
      setAlerts([]);
    } catch (error) {
      console.error('Error submitting vitals:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical':
        return 'bg-red-50 border-red-200 text-red-800';
      case 'warning':
        return 'bg-amber-50 border-amber-200 text-amber-800';
      default:
        return 'bg-emerald-50 border-emerald-200 text-emerald-800';
    }
  };

  const getSeverityIcon = (severity: string) => {
    if (severity === 'critical') {
      return (
        <svg className="w-5 h-5 text-red-600" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
        </svg>
      );
    }
    return (
      <svg className="w-5 h-5 text-amber-600" fill="currentColor" viewBox="0 0 20 20">
        <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
      </svg>
    );
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-gray-900">Record Vital Signs</h3>
        <div className="flex items-center gap-2 text-xs text-gray-500">
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
          </svg>
          <span>Patient #{patientId}</span>
        </div>
      </div>

      {/* Alerts */}
      {alerts.length > 0 && (
        <div className="mb-6 space-y-2">
          {alerts.map((alert, index) => (
            <div
              key={index}
              className={`flex items-start gap-3 p-3 rounded-lg border ${getSeverityColor(alert.severity)}`}
            >
              {getSeverityIcon(alert.severity)}
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium">{alert.vital}</p>
                <p className="text-xs mt-0.5">{alert.message}</p>
              </div>
            </div>
          ))}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Blood Pressure */}
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1.5">
              Systolic BP
            </label>
            <div className="relative">
              <input
                type="number"
                name="bloodPressureSystolic"
                value={vitals.bloodPressureSystolic}
                onChange={handleChange}
                placeholder="120"
                className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent text-sm"
              />
              <span className="absolute right-3 top-2 text-xs text-gray-400">mmHg</span>
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1.5">
              Diastolic BP
            </label>
            <div className="relative">
              <input
                type="number"
                name="bloodPressureDiastolic"
                value={vitals.bloodPressureDiastolic}
                onChange={handleChange}
                placeholder="80"
                className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent text-sm"
              />
              <span className="absolute right-3 top-2 text-xs text-gray-400">mmHg</span>
            </div>
          </div>
        </div>

        {/* Heart Rate and Temperature */}
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1.5">
              Heart Rate
            </label>
            <div className="relative">
              <input
                type="number"
                name="heartRate"
                value={vitals.heartRate}
                onChange={handleChange}
                placeholder="72"
                className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent text-sm"
              />
              <span className="absolute right-3 top-2 text-xs text-gray-400">bpm</span>
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1.5">
              Temperature
            </label>
            <div className="relative">
              <input
                type="number"
                step="0.1"
                name="temperature"
                value={vitals.temperature}
                onChange={handleChange}
                placeholder="37.0"
                className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent text-sm"
              />
              <span className="absolute right-3 top-2 text-xs text-gray-400">°C</span>
            </div>
          </div>
        </div>

        {/* O2 Saturation and Respiratory Rate */}
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1.5">
              O₂ Saturation
            </label>
            <div className="relative">
              <input
                type="number"
                name="oxygenSaturation"
                value={vitals.oxygenSaturation}
                onChange={handleChange}
                placeholder="98"
                className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent text-sm"
              />
              <span className="absolute right-3 top-2 text-xs text-gray-400">%</span>
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1.5">
              Respiratory Rate
            </label>
            <div className="relative">
              <input
                type="number"
                name="respiratoryRate"
                value={vitals.respiratoryRate}
                onChange={handleChange}
                placeholder="16"
                className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent text-sm"
              />
              <span className="absolute right-3 top-2 text-xs text-gray-400">breaths/min</span>
            </div>
          </div>
        </div>

        {/* Weight and Height */}
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1.5">
              Weight
            </label>
            <div className="relative">
              <input
                type="number"
                step="0.1"
                name="weight"
                value={vitals.weight}
                onChange={handleChange}
                placeholder="70.0"
                className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent text-sm"
              />
              <span className="absolute right-3 top-2 text-xs text-gray-400">kg</span>
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1.5">
              Height
            </label>
            <div className="relative">
              <input
                type="number"
                step="0.1"
                name="height"
                value={vitals.height}
                onChange={handleChange}
                placeholder="170.0"
                className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent text-sm"
              />
              <span className="absolute right-3 top-2 text-xs text-gray-400">cm</span>
            </div>
          </div>
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={isSubmitting}
          className="w-full py-2.5 bg-emerald-500 text-white rounded-lg font-medium hover:bg-emerald-600 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2"
        >
          {isSubmitting ? (
            <>
              <svg className="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <span>Recording...</span>
            </>
          ) : (
            <>
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              <span>Record Vitals</span>
            </>
          )}
        </button>
      </form>
    </div>
  );
};

export default VitalsInputForm;

import React from 'react';
import { LineChart, Line, XAxis, YAxis, ResponsiveContainer, Tooltip } from 'recharts';

interface VitalReading {
  timestamp: string;
  value: number;
}

interface PatientCardProps {
  patient: {
    id: string;
    name: string;
    age: number;
    gender: string;
    avatar?: string;
    bloodType?: string;
    allergies?: string[];
  };
  vitals: {
    bloodPressure: string;
    heartRate: number;
    temperature: number;
    oxygenSaturation: number;
  };
  heartRateHistory?: VitalReading[];
}

const PatientCard: React.FC<PatientCardProps> = ({ patient, vitals, heartRateHistory = [] }) => {
  const getAvatarInitials = (name: string) => {
    return name
      .split(' ')
      .map(n => n[0])
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  const getVitalStatus = (vital: string, value: number | string) => {
    // Simple status check - can be enhanced with real thresholds
    if (vital === 'heartRate') {
      const hr = value as number;
      if (hr < 60 || hr > 100) return 'text-amber-600';
      return 'text-emerald-600';
    }
    if (vital === 'oxygenSaturation') {
      const o2 = value as number;
      if (o2 < 95) return 'text-red-600';
      return 'text-emerald-600';
    }
    if (vital === 'temperature') {
      const temp = value as number;
      if (temp < 36 || temp > 37.5) return 'text-amber-600';
      return 'text-emerald-600';
    }
    return 'text-gray-700';
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
      {/* Header with Avatar */}
      <div className="flex items-start gap-4 mb-6">
        <div className="relative">
          {patient.avatar ? (
            <img
              src={patient.avatar}
              alt={patient.name}
              className="w-16 h-16 rounded-full object-cover border-2 border-emerald-500"
            />
          ) : (
            <div className="w-16 h-16 rounded-full bg-emerald-100 border-2 border-emerald-500 flex items-center justify-center">
              <span className="text-emerald-700 font-semibold text-xl">
                {getAvatarInitials(patient.name)}
              </span>
            </div>
          )}
          <div className="absolute -bottom-1 -right-1 w-5 h-5 bg-emerald-500 rounded-full border-2 border-white"></div>
        </div>

        <div className="flex-1">
          <h3 className="text-xl font-semibold text-gray-900">{patient.name}</h3>
          <div className="flex items-center gap-3 mt-1 text-sm text-gray-600">
            <span className="flex items-center gap-1">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              {patient.age} years
            </span>
            <span>•</span>
            <span className="capitalize">{patient.gender}</span>
            {patient.bloodType && (
              <>
                <span>•</span>
                <span className="font-medium text-red-600">{patient.bloodType}</span>
              </>
            )}
          </div>
          {patient.allergies && patient.allergies.length > 0 && (
            <div className="mt-2 flex items-center gap-1 text-xs">
              <svg className="w-3.5 h-3.5 text-amber-600" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
              <span className="text-amber-700">Allergies: {patient.allergies.join(', ')}</span>
            </div>
          )}
        </div>
      </div>

      {/* Current Vitals Grid */}
      <div className="grid grid-cols-2 gap-3 mb-6">
        <div className="bg-gray-50 rounded-lg p-3 border border-gray-100">
          <div className="flex items-center justify-between mb-1">
            <span className="text-xs text-gray-600 font-medium">Blood Pressure</span>
            <svg className="w-4 h-4 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
            </svg>
          </div>
          <div className="text-lg font-semibold text-gray-900">{vitals.bloodPressure}</div>
          <div className="text-xs text-gray-500 mt-0.5">mmHg</div>
        </div>

        <div className="bg-gray-50 rounded-lg p-3 border border-gray-100">
          <div className="flex items-center justify-between mb-1">
            <span className="text-xs text-gray-600 font-medium">Heart Rate</span>
            <svg className="w-4 h-4 text-emerald-600" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M3.172 5.172a4 4 0 015.656 0L10 6.343l1.172-1.171a4 4 0 115.656 5.656L10 17.657l-6.828-6.829a4 4 0 010-5.656z" clipRule="evenodd" />
            </svg>
          </div>
          <div className={`text-lg font-semibold ${getVitalStatus('heartRate', vitals.heartRate)}`}>
            {vitals.heartRate}
          </div>
          <div className="text-xs text-gray-500 mt-0.5">bpm</div>
        </div>

        <div className="bg-gray-50 rounded-lg p-3 border border-gray-100">
          <div className="flex items-center justify-between mb-1">
            <span className="text-xs text-gray-600 font-medium">Temperature</span>
            <svg className="w-4 h-4 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
          </div>
          <div className={`text-lg font-semibold ${getVitalStatus('temperature', vitals.temperature)}`}>
            {vitals.temperature}°C
          </div>
          <div className="text-xs text-gray-500 mt-0.5">Celsius</div>
        </div>

        <div className="bg-gray-50 rounded-lg p-3 border border-gray-100">
          <div className="flex items-center justify-between mb-1">
            <span className="text-xs text-gray-600 font-medium">O₂ Saturation</span>
            <svg className="w-4 h-4 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          </div>
          <div className={`text-lg font-semibold ${getVitalStatus('oxygenSaturation', vitals.oxygenSaturation)}`}>
            {vitals.oxygenSaturation}%
          </div>
          <div className="text-xs text-gray-500 mt-0.5">SpO₂</div>
        </div>
      </div>

      {/* Heart Rate Chart */}
      {heartRateHistory.length > 0 && (
        <div className="border-t border-gray-100 pt-4">
          <div className="flex items-center justify-between mb-3">
            <h4 className="text-sm font-medium text-gray-700">Heart Rate Trend</h4>
            <span className="text-xs text-gray-500">Last 7 readings</span>
          </div>
          <div className="h-24">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={heartRateHistory}>
                <XAxis 
                  dataKey="timestamp" 
                  hide 
                />
                <YAxis 
                  hide 
                  domain={[50, 120]}
                />
                <Tooltip 
                  contentStyle={{ 
                    background: 'white', 
                    border: '1px solid #e5e7eb',
                    borderRadius: '8px',
                    fontSize: '12px'
                  }}
                  labelStyle={{ color: '#6b7280' }}
                />
                <Line 
                  type="monotone" 
                  dataKey="value" 
                  stroke="#10B981" 
                  strokeWidth={2}
                  dot={{ fill: '#10B981', r: 3 }}
                  activeDot={{ r: 5 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}
    </div>
  );
};

export default PatientCard;

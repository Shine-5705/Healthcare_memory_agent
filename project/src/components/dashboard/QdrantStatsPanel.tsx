import React from 'react';

interface QdrantStatsProps {
  className?: string;
}

const QdrantStatsPanel: React.FC<QdrantStatsProps> = ({ className = '' }) => {
  const collections = [
    { name: 'patient_memory', dims: 384, icon: '💬', color: 'bg-blue-50 border-blue-200 text-blue-700', count: '~2,000' },
    { name: 'skin_analysis_history', dims: 512, icon: '📸', color: 'bg-purple-50 border-purple-200 text-purple-700', count: '~3,000', multimodal: true },
    { name: 'audio_health_history', dims: 768, icon: '🎵', color: 'bg-pink-50 border-pink-200 text-pink-700', count: '~1,500', multimodal: true },
    { name: 'similar_cases', dims: 384, icon: '🔍', color: 'bg-emerald-50 border-emerald-200 text-emerald-700', count: '~1,200' },
    { name: 'medical_knowledge', dims: 384, icon: '🧠', color: 'bg-amber-50 border-amber-200 text-amber-700', count: '~1,200' },
    { name: 'vitals_tracking', dims: 384, icon: '💓', color: 'bg-red-50 border-red-200 text-red-700', count: '~382' },
  ];

  const totalVectors = collections.reduce((sum, col) => 
    sum + parseInt(col.count.replace('~', '').replace(',', '')), 0
  );

  return (
    <div className={`bg-gradient-to-br from-purple-50 to-blue-50 rounded-xl border-2 border-purple-200 p-6 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 bg-purple-600 rounded-xl flex items-center justify-center shadow-lg">
            <svg className="w-7 h-7 text-white" fill="currentColor" viewBox="0 0 24 24">
              <path d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z"/>
            </svg>
          </div>
          <div>
            <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2">
              Qdrant Vector Database
              <span className="px-2 py-0.5 bg-green-100 text-green-700 rounded text-xs font-semibold border border-green-300">
                v1.7.0
              </span>
            </h2>
            <p className="text-sm text-gray-600 font-medium">
              {totalVectors.toLocaleString()}+ vectors • 6 collections • Multimodal embeddings
            </p>
          </div>
        </div>
      </div>

      {/* Collections Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 mb-4">
        {collections.map((col) => (
          <div
            key={col.name}
            className={`relative border-2 rounded-lg p-3 transition-all hover:shadow-md ${col.color}`}
          >
            {col.multimodal && (
              <div className="absolute top-2 right-2">
                <span className="px-1.5 py-0.5 bg-white bg-opacity-80 border border-current rounded text-[9px] font-bold">
                  MULTIMODAL
                </span>
              </div>
            )}
            
            <div className="flex items-start gap-2">
              <span className="text-2xl">{col.icon}</span>
              <div className="flex-1 min-w-0">
                <p className="font-mono text-xs font-bold truncate mb-0.5">
                  {col.name}
                </p>
                <div className="flex items-center gap-2 text-[10px] font-semibold">
                  <span className="px-1.5 py-0.5 bg-white bg-opacity-60 rounded border border-current">
                    {col.dims}D
                  </span>
                  <span className="px-1.5 py-0.5 bg-white bg-opacity-60 rounded border border-current">
                    {col.count} vectors
                  </span>
                </div>
                {col.multimodal && (
                  <p className="text-[9px] mt-1 opacity-80 font-semibold">
                    Named vectors: image + text
                  </p>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Key Features */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mt-4">
        <div className="bg-white bg-opacity-60 border-2 border-purple-300 rounded-lg p-3">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-lg">🎯</span>
            <h4 className="text-xs font-bold text-gray-900">Named Vectors</h4>
          </div>
          <p className="text-[10px] text-gray-700 font-medium leading-relaxed">
            Multiple embeddings per point (512-dim CLIP + 384-dim text)
          </p>
        </div>

        <div className="bg-white bg-opacity-60 border-2 border-purple-300 rounded-lg p-3">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-lg">🔄</span>
            <h4 className="text-xs font-bold text-gray-900">Cross-Modal Search</h4>
          </div>
          <p className="text-[10px] text-gray-700 font-medium leading-relaxed">
            Text queries → Image results via CLIP shared space
          </p>
        </div>

        <div className="bg-white bg-opacity-60 border-2 border-purple-300 rounded-lg p-3">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-lg">🔍</span>
            <h4 className="text-xs font-bold text-gray-900">Hybrid Search</h4>
          </div>
          <p className="text-[10px] text-gray-700 font-medium leading-relaxed">
            Vector similarity + metadata filters + HNSW indexing
          </p>
        </div>
      </div>

      {/* Pro Tip */}
      <div className="mt-4 bg-gradient-to-r from-yellow-50 to-amber-50 border-2 border-amber-300 rounded-lg p-3">
        <div className="flex items-start gap-2">
          <span className="text-xl">💡</span>
          <div className="flex-1">
            <p className="text-xs font-bold text-amber-900 mb-1">
              Open Browser Console to See Qdrant in Action!
            </p>
            <p className="text-[10px] text-amber-800 font-medium leading-relaxed">
              Press <kbd className="px-1.5 py-0.5 bg-white rounded border border-amber-400 font-mono">F12</kbd> to view:
              • Point IDs • Similarity scores • Collection names • Evidence logs
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default QdrantStatsPanel;

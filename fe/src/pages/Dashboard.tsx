import React from 'react';
import { useModels, usePredictions } from '../hooks';
import { formatDate } from '../utils/dateUtils';

const Dashboard: React.FC = () => {
  const { data: models, isLoading: modelsLoading } = useModels();
  const { data: predictions, isLoading: predictionsLoading } = usePredictions();

  return (
    <div style={{ padding: '20px' }}>
      <h1>ML Prediction Dashboard</h1>
      
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginTop: '20px' }}>
        <div style={{ border: '1px solid #ddd', padding: '20px', borderRadius: '8px' }}>
          <h2>Models Overview</h2>
          {modelsLoading ? (
            <p>Loading models...</p>
          ) : (
            <div>
              <p><strong>Total Models:</strong> {models?.length || 0}</p>
              <p><strong>Trained:</strong> {models?.filter(m => m.status === 'TRAINED').length || 0}</p>
              <p><strong>Training:</strong> {models?.filter(m => m.status === 'TRAINING').length || 0}</p>
              <p><strong>Failed:</strong> {models?.filter(m => m.status === 'FAILED').length || 0}</p>
            </div>
          )}
        </div>

        <div style={{ border: '1px solid #ddd', padding: '20px', borderRadius: '8px' }}>
          <h2>Predictions Overview</h2>
          {predictionsLoading ? (
            <p>Loading predictions...</p>
          ) : (
            <div>
              <p><strong>Total Predictions:</strong> {predictions?.length || 0}</p>
              <p><strong>Completed:</strong> {predictions?.filter(p => p.status === 'COMPLETED').length || 0}</p>
              <p><strong>Processing:</strong> {predictions?.filter(p => p.status === 'PROCESSING').length || 0}</p>
              <p><strong>Failed:</strong> {predictions?.filter(p => p.status === 'FAILED').length || 0}</p>
            </div>
          )}
        </div>
      </div>

      <div style={{ marginTop: '20px' }}>
        <h2>Recent Activity</h2>
        <div style={{ border: '1px solid #ddd', padding: '20px', borderRadius: '8px' }}>
          <h3>Latest Models</h3>
          {models?.slice(0, 3).map(model => (
            <div key={model.modelId} style={{ margin: '10px 0', padding: '10px', background: '#f5f5f5', borderRadius: '4px' }}>
              <strong>{model.modelName}</strong> - {model.status} (Created: {formatDate(model.createdAt)})
            </div>
          ))}
          
          <h3>Latest Predictions</h3>
          {predictions?.slice(0, 3).map(prediction => (
            <div key={prediction.predictId} style={{ margin: '10px 0', padding: '10px', background: '#f5f5f5', borderRadius: '4px' }}>
              <strong>Prediction {prediction.predictId.slice(0, 8)}...</strong> - {prediction.status} (Created: {formatDate(prediction.createdAt)})
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
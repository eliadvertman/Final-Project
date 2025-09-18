import React from 'react';
import { useModels, useModelStatus } from '../hooks';
import type { TrainingSummary } from '../types';
import { formatDateTime } from '../utils/dateUtils';

const ModelStatusBadge: React.FC<{ status: string }> = ({ status }) => {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'TRAINED': return '#28a745';
      case 'TRAINING': return '#ffc107';
      case 'PENDING': return '#6c757d';
      case 'FAILED': return '#dc3545';
      case 'DEPLOYED': return '#007bff';
      default: return '#6c757d';
    }
  };

  return (
    <span style={{
      background: getStatusColor(status),
      color: 'white',
      padding: '4px 8px',
      borderRadius: '4px',
      fontSize: '12px',
      fontWeight: 'bold'
    }}>
      {status}
    </span>
  );
};

const ModelRow: React.FC<{ model: TrainingSummary }> = ({ model }) => {
  const { data: status } = useModelStatus(model.trainingId, model.status === 'TRAINING');

  const displayStatus = status?.status || model.status;
  const progress = status?.progress;

  return (
    <tr style={{ borderBottom: '1px solid #ddd' }}>
      <td style={{ padding: '12px' }}>{model.trainingName}</td>
      <td style={{ padding: '12px' }}>
        <ModelStatusBadge status={displayStatus} />
        {progress !== undefined && displayStatus === 'TRAINING' && (
          <div style={{ marginTop: '4px' }}>
            <div style={{
              background: '#e0e0e0',
              borderRadius: '4px',
              height: '4px',
              width: '100px',
              overflow: 'hidden'
            }}>
              <div style={{
                background: '#007bff',
                height: '100%',
                width: `${progress}%`,
                transition: 'width 0.3s ease'
              }} />
            </div>
            <small>{progress.toFixed(1)}%</small>
          </div>
        )}
      </td>
      <td style={{ padding: '12px' }}>{formatDateTime(model.createdAt)}</td>
      <td style={{ padding: '12px' }}>
        <code style={{ fontSize: '11px', color: '#666' }}>
          {model.trainingId.slice(0, 8)}...
        </code>
      </td>
      <td style={{ padding: '12px' }}>
        {status?.errorMessage && (
          <span style={{ color: '#dc3545', fontSize: '12px' }}>
            {status.errorMessage}
          </span>
        )}
      </td>
    </tr>
  );
};

const Models: React.FC = () => {
  const { data: models, isLoading, error } = useModels();

  if (isLoading) {
    return (
      <div style={{ padding: '20px' }}>
        <h1>Models</h1>
        <p>Loading models...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ padding: '20px' }}>
        <h1>Models</h1>
        <div style={{
          padding: '12px',
          background: '#f8d7da',
          color: '#721c24',
          border: '1px solid #f5c6cb',
          borderRadius: '4px'
        }}>
          Error loading models: {error.message}
        </div>
      </div>
    );
  }

  return (
    <div style={{ padding: '20px' }}>
      <h1>Models</h1>
      <p style={{ color: '#666', marginBottom: '20px' }}>
        View all training sessions and their models. To start new training, use the Training Management page.
      </p>
      
      {!models || models.length === 0 ? (
        <div style={{ 
          padding: '40px', 
          textAlign: 'center', 
          border: '1px solid #ddd', 
          borderRadius: '8px',
          marginTop: '20px'
        }}>
          <p>No training sessions found. Start by training your first model in the Training Management page!</p>
        </div>
      ) : (
        <div style={{ marginTop: '20px' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', border: '1px solid #ddd' }}>
            <thead style={{ background: '#f8f9fa' }}>
              <tr>
                <th style={{ padding: '12px', textAlign: 'left', borderBottom: '2px solid #ddd' }}>
                  Training Name
                </th>
                <th style={{ padding: '12px', textAlign: 'left', borderBottom: '2px solid #ddd' }}>
                  Status
                </th>
                <th style={{ padding: '12px', textAlign: 'left', borderBottom: '2px solid #ddd' }}>
                  Created At
                </th>
                <th style={{ padding: '12px', textAlign: 'left', borderBottom: '2px solid #ddd' }}>
                  Training ID
                </th>
                <th style={{ padding: '12px', textAlign: 'left', borderBottom: '2px solid #ddd' }}>
                  Error
                </th>
              </tr>
            </thead>
            <tbody>
              {models.map(model => (
                <ModelRow key={model.trainingId} model={model} />
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default Models;
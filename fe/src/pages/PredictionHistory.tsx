import React from 'react';
import { usePredictions, usePredictionStatus } from '../hooks';
import type { PredictionSummary } from '../types';
import { formatDateTime } from '../utils/dateUtils';

const PredictionStatusBadge: React.FC<{ status: string }> = ({ status }) => {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'COMPLETED': return '#28a745';
      case 'PROCESSING': return '#ffc107';
      case 'PENDING': return '#6c757d';
      case 'FAILED': return '#dc3545';
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

const PredictionRow: React.FC<{ prediction: PredictionSummary }> = ({ prediction }) => {
  const { data: status } = usePredictionStatus(prediction.predictId, prediction.status === 'PROCESSING');

  const displayStatus = status?.status || prediction.status;

  return (
    <tr style={{ borderBottom: '1px solid #ddd' }}>
      <td style={{ padding: '12px' }}>
        <code style={{ fontSize: '11px' }}>
          {prediction.predictId.slice(0, 8)}...
        </code>
      </td>
      <td style={{ padding: '12px' }}>
        <code style={{ fontSize: '11px' }}>
          {prediction.modelId.slice(0, 8)}...
        </code>
      </td>
      <td style={{ padding: '12px' }}>
        <PredictionStatusBadge status={displayStatus} />
      </td>
      <td style={{ padding: '12px' }}>{formatDateTime(prediction.createdAt)}</td>
      <td style={{ padding: '12px' }}>
        {status?.startTime && (
          <small style={{ color: '#666' }}>
            Started: {formatDateTime(status.startTime)}
          </small>
        )}
        {status?.endTime && (
          <small style={{ color: '#666', display: 'block' }}>
            Ended: {formatDateTime(status.endTime)}
          </small>
        )}
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

const PredictionHistory: React.FC = () => {
  const { data: predictions, isLoading, error } = usePredictions();

  if (isLoading) {
    return (
      <div style={{ padding: '20px' }}>
        <h1>Prediction History</h1>
        <p>Loading predictions...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ padding: '20px' }}>
        <h1>Prediction History</h1>
        <div style={{ 
          padding: '12px', 
          background: '#f8d7da', 
          color: '#721c24', 
          border: '1px solid #f5c6cb', 
          borderRadius: '4px' 
        }}>
          Error loading predictions: {error.message}
        </div>
      </div>
    );
  }

  return (
    <div style={{ padding: '20px' }}>
      <h1>Prediction History</h1>
      
      {!predictions || predictions.length === 0 ? (
        <div style={{ 
          padding: '40px', 
          textAlign: 'center', 
          border: '1px solid #ddd', 
          borderRadius: '8px',
          marginTop: '20px'
        }}>
          <p>No predictions found. Make your first prediction to see results here!</p>
        </div>
      ) : (
        <div style={{ marginTop: '20px' }}>
          <div style={{ marginBottom: '16px' }}>
            <p>Total predictions: <strong>{predictions.length}</strong></p>
          </div>
          
          <table style={{ width: '100%', borderCollapse: 'collapse', border: '1px solid #ddd' }}>
            <thead style={{ background: '#f8f9fa' }}>
              <tr>
                <th style={{ padding: '12px', textAlign: 'left', borderBottom: '2px solid #ddd' }}>
                  Prediction ID
                </th>
                <th style={{ padding: '12px', textAlign: 'left', borderBottom: '2px solid #ddd' }}>
                  Model ID
                </th>
                <th style={{ padding: '12px', textAlign: 'left', borderBottom: '2px solid #ddd' }}>
                  Status
                </th>
                <th style={{ padding: '12px', textAlign: 'left', borderBottom: '2px solid #ddd' }}>
                  Created At
                </th>
                <th style={{ padding: '12px', textAlign: 'left', borderBottom: '2px solid #ddd' }}>
                  Timing
                </th>
                <th style={{ padding: '12px', textAlign: 'left', borderBottom: '2px solid #ddd' }}>
                  Error
                </th>
              </tr>
            </thead>
            <tbody>
              {predictions.map(prediction => (
                <PredictionRow key={prediction.predictId} prediction={prediction} />
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default PredictionHistory;
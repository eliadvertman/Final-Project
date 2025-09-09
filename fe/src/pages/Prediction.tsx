import React, { useState, useEffect } from 'react';
import { useModels, useMakePrediction } from '../hooks';
import type { PredictionRequest } from '../types';

interface NotificationState {
  type: 'success' | 'error' | 'warning' | null;
  message: string;
  details?: string;
}

const Prediction: React.FC = () => {
  const [selectedModelId, setSelectedModelId] = useState<string>('');
  const [inputPath, setInputPath] = useState<string>('');
  const [notification, setNotification] = useState<NotificationState>({
    type: null,
    message: '',
  });
  
  const { data: models, isLoading: modelsLoading } = useModels();
  const makePredictionMutation = useMakePrediction();

  // Filter only trained models for predictions
  const trainedModels = models?.filter(model => model.status === 'TRAINED') || [];

  // Auto-dismiss success notifications after 7 seconds (longer for prediction results)
  useEffect(() => {
    if (notification.type === 'success') {
      const timer = setTimeout(() => {
        setNotification({ type: null, message: '' });
      }, 7000);
      return () => clearTimeout(timer);
    }
  }, [notification]);

  const handleFormChange = () => {
    // Clear notifications when user interacts with form
    if (notification.type) {
      setNotification({ type: null, message: '' });
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validation
    if (!selectedModelId) {
      setNotification({
        type: 'error',
        message: 'Please select a model',
        details: 'You must choose a trained model from the dropdown before making a prediction.'
      });
      return;
    }

    if (!inputPath.trim()) {
      setNotification({
        type: 'error',
        message: 'Please provide an input path',
        details: 'You must specify a file path for the prediction input.'
      });
      return;
    }

    const request: PredictionRequest = {
      modelId: selectedModelId,
      inputPath: inputPath.trim()
    };

    try {
      const result = await makePredictionMutation.mutateAsync(request);
      setNotification({
        type: 'success',
        message: 'Prediction completed successfully!',
        details: `Prediction ID: ${result.predictId}. Results are displayed below.`
      });
    } catch (error: any) {
      const errorMessage = error?.response?.data?.message || error?.message || 'Prediction failed';
      setNotification({
        type: 'error',
        message: 'Prediction failed',
        details: errorMessage
      });
    }
  };

  const dismissNotification = () => {
    setNotification({ type: null, message: '' });
  };

  return (
    <div style={{ padding: '20px' }}>
      <h1>Make Prediction</h1>
      
      {/* Notification Component */}
      {notification.type && (
        <div style={{
          maxWidth: '600px',
          marginTop: '20px',
          padding: '16px',
          borderRadius: '8px',
          border: `1px solid ${
            notification.type === 'success' ? '#c3e6cb' : 
            notification.type === 'error' ? '#f5c6cb' : '#ffeaa7'
          }`,
          backgroundColor: 
            notification.type === 'success' ? '#d4edda' : 
            notification.type === 'error' ? '#f8d7da' : '#fff3cd',
          color: 
            notification.type === 'success' ? '#155724' : 
            notification.type === 'error' ? '#721c24' : '#856404',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'flex-start',
          animation: 'fadeIn 0.3s ease-in'
        }}>
          <div style={{ flex: 1 }}>
            <div style={{ fontWeight: 'bold', marginBottom: '4px' }}>
              {notification.type === 'success' ? '✅ ' : notification.type === 'error' ? '❌ ' : '⚠️ '}
              {notification.message}
            </div>
            {notification.details && (
              <div style={{ fontSize: '14px', opacity: 0.9 }}>
                {notification.details}
              </div>
            )}
          </div>
          <button
            type="button"
            onClick={dismissNotification}
            style={{
              background: 'none',
              border: 'none',
              fontSize: '18px',
              cursor: 'pointer',
              padding: '0 0 0 12px',
              color: 'inherit',
              opacity: 0.7
            }}
            aria-label="Dismiss notification"
          >
            ×
          </button>
        </div>
      )}
      
      {modelsLoading ? (
        <p>Loading models...</p>
      ) : trainedModels.length === 0 ? (
        <div style={{ 
          padding: '20px', 
          background: '#fff3cd', 
          color: '#856404', 
          border: '1px solid #ffeaa7', 
          borderRadius: '4px',
          marginTop: '20px'
        }}>
          No trained models available. Please train a model first before making predictions.
        </div>
      ) : (
        <form onSubmit={handleSubmit} style={{ maxWidth: '600px', marginTop: '20px' }}>
          <div style={{ marginBottom: '16px' }}>
            <label style={{ display: 'block', marginBottom: '4px', fontWeight: 'bold' }}>
              Select Model *
            </label>
            <select
              value={selectedModelId}
              onChange={(e) => {
                setSelectedModelId(e.target.value);
                handleFormChange();
              }}
              required
              style={{
                width: '100%',
                padding: '8px',
                border: '1px solid #ddd',
                borderRadius: '4px',
                fontSize: '14px'
              }}
            >
              <option value="">Choose a trained model...</option>
              {trainedModels.map(model => (
                <option key={model.modelId} value={model.modelId}>
                  {model.modelName} (ID: {model.modelId.slice(0, 8)}...)
                </option>
              ))}
            </select>
          </div>

          <div style={{ marginBottom: '16px' }}>
            <label style={{ display: 'block', marginBottom: '4px', fontWeight: 'bold' }}>
              Input File Path *
            </label>
            <input
              type="text"
              value={inputPath}
              onChange={(e) => {
                setInputPath(e.target.value);
                handleFormChange();
              }}
              required
              style={{
                width: '100%',
                padding: '8px',
                border: '1px solid #ddd',
                borderRadius: '4px',
                fontSize: '14px'
              }}
              placeholder="Enter file path for prediction (e.g., /path/to/input/file.jpg)"
            />
            <small style={{ color: '#666' }}>
              Enter the path to the input file for prediction. Example: /work/images/sample.jpg
            </small>
          </div>

          <button
            type="submit"
            disabled={makePredictionMutation.isPending}
            style={{
              background: makePredictionMutation.isPending ? '#ccc' : '#28a745',
              color: 'white',
              padding: '12px 24px',
              border: 'none',
              borderRadius: '4px',
              fontSize: '16px',
              cursor: makePredictionMutation.isPending ? 'not-allowed' : 'pointer',
            }}
          >
            {makePredictionMutation.isPending ? 'Making Prediction...' : 'Make Prediction'}
          </button>


          {makePredictionMutation.data && (
            <div style={{ 
              marginTop: '16px', 
              padding: '12px', 
              background: '#d4edda', 
              color: '#155724', 
              border: '1px solid #c3e6cb', 
              borderRadius: '4px' 
            }}>
              <h3>Prediction Result</h3>
              <p><strong>Prediction ID:</strong> {makePredictionMutation.data.predictId}</p>
              <p><strong>Timestamp:</strong> {new Date(makePredictionMutation.data.timestamp).toLocaleString()}</p>
              <div style={{ marginTop: '8px' }}>
                <strong>Result:</strong>
                <pre style={{ 
                  background: '#f8f9fa', 
                  padding: '8px', 
                  borderRadius: '4px', 
                  marginTop: '4px',
                  overflow: 'auto'
                }}>
                  {JSON.stringify(makePredictionMutation.data.prediction, null, 2)}
                </pre>
              </div>
            </div>
          )}
        </form>
      )}
    </div>
  );
};

export default Prediction;
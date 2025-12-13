import React, { useState, useEffect } from 'react';
import { useTrainedModels, useRunEvaluation } from '../hooks';
import type { EvaluationRequest, ConfigurationType } from '../types';

interface NotificationState {
  type: 'success' | 'error' | 'warning' | null;
  message: string;
  details?: string;
}

const CONFIGURATION_OPTIONS: ConfigurationType[] = ['2d', '3d_fullres', '3d_lowres', '3d_cascade_lowres'];

const Evaluation: React.FC = () => {
  const [selectedModelName, setSelectedModelName] = useState<string>('');
  const [evaluationPath, setEvaluationPath] = useState<string>('');
  const [selectedConfigurations, setSelectedConfigurations] = useState<ConfigurationType[]>([]);
  const [notification, setNotification] = useState<NotificationState>({
    type: null,
    message: '',
  });
  
  const { data: models, isLoading: modelsLoading } = useTrainedModels();
  const runEvaluationMutation = useRunEvaluation();

  // Filter only trained models for evaluation
  const trainedModels = models?.filter(model => model.status === 'TRAINED') || [];

  // Auto-dismiss success notifications after 7 seconds
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

  const handleConfigurationToggle = (config: ConfigurationType) => {
    setSelectedConfigurations(prev => {
      if (prev.includes(config)) {
        return prev.filter(c => c !== config);
      } else {
        return [...prev, config];
      }
    });
    handleFormChange();
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validation
    if (!selectedModelName) {
      setNotification({
        type: 'error',
        message: 'Please select a model',
        details: 'You must choose a trained model from the dropdown before running evaluation.'
      });
      return;
    }

    if (!evaluationPath.trim()) {
      setNotification({
        type: 'error',
        message: 'Please provide an evaluation path',
        details: 'You must specify a path to the evaluation/validation dataset.'
      });
      return;
    }

    if (selectedConfigurations.length === 0) {
      setNotification({
        type: 'error',
        message: 'Please select at least one configuration',
        details: 'You must select at least one configuration to evaluate.'
      });
      return;
    }

    const request: EvaluationRequest = {
      modelName: selectedModelName,
      evaluationPath: evaluationPath.trim(),
      configurations: selectedConfigurations
    };

    try {
      const result = await runEvaluationMutation.mutateAsync(request);
      setNotification({
        type: 'success',
        message: 'Evaluation started successfully!',
        details: `Evaluation ID: ${result.evaluationId}. The evaluation job has been submitted.`
      });
    } catch (error: any) {
      const errorMessage = error?.response?.data?.message || error?.message || 'Evaluation failed';
      setNotification({
        type: 'error',
        message: 'Evaluation failed',
        details: errorMessage
      });
    }
  };

  const dismissNotification = () => {
    setNotification({ type: null, message: '' });
  };

  return (
    <div style={{ padding: '20px' }}>
      <h1>Evaluate Model</h1>
      
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
          No trained models available. Please train a model first before running evaluations.
        </div>
      ) : (
        <form onSubmit={handleSubmit} style={{ maxWidth: '600px', marginTop: '20px' }}>
          <div style={{ marginBottom: '16px' }}>
            <label style={{ display: 'block', marginBottom: '4px', fontWeight: 'bold' }}>
              Select Model *
            </label>
            <select
              value={selectedModelName}
              onChange={(e) => {
                setSelectedModelName(e.target.value);
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
                <option key={model.modelId} value={model.modelName}>
                  {model.modelName} (ID: {model.modelId.slice(0, 8)}...)
                </option>
              ))}
            </select>
          </div>

          <div style={{ marginBottom: '16px' }}>
            <label style={{ display: 'block', marginBottom: '4px', fontWeight: 'bold' }}>
              Evaluation Dataset Path *
            </label>
            <input
              type="text"
              value={evaluationPath}
              onChange={(e) => {
                setEvaluationPath(e.target.value);
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
              placeholder="Enter path to evaluation/validation dataset"
            />
            <small style={{ color: '#666' }}>
              Enter the path to the evaluation dataset. Example: /work/datasets/validation
            </small>
          </div>

          <div style={{ marginBottom: '16px' }}>
            <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>
              Configurations to Evaluate *
            </label>
            <div style={{ 
              display: 'flex', 
              flexWrap: 'wrap', 
              gap: '12px',
              padding: '12px',
              border: '1px solid #ddd',
              borderRadius: '4px',
              background: '#f8f9fa'
            }}>
              {CONFIGURATION_OPTIONS.map(config => (
                <label 
                  key={config} 
                  style={{ 
                    display: 'flex', 
                    alignItems: 'center', 
                    cursor: 'pointer',
                    padding: '8px 12px',
                    borderRadius: '4px',
                    background: selectedConfigurations.includes(config) ? '#007bff' : 'white',
                    color: selectedConfigurations.includes(config) ? 'white' : '#333',
                    border: `1px solid ${selectedConfigurations.includes(config) ? '#007bff' : '#ddd'}`,
                    transition: 'all 0.2s ease'
                  }}
                >
                  <input
                    type="checkbox"
                    checked={selectedConfigurations.includes(config)}
                    onChange={() => handleConfigurationToggle(config)}
                    style={{ marginRight: '8px', cursor: 'pointer' }}
                  />
                  {config}
                </label>
              ))}
            </div>
            <small style={{ color: '#666', display: 'block', marginTop: '4px' }}>
              Select one or more configurations to evaluate. Each configuration will be evaluated against the dataset.
            </small>
          </div>

          <button
            type="submit"
            disabled={runEvaluationMutation.isPending}
            style={{
              background: runEvaluationMutation.isPending ? '#ccc' : '#17a2b8',
              color: 'white',
              padding: '12px 24px',
              border: 'none',
              borderRadius: '4px',
              fontSize: '16px',
              cursor: runEvaluationMutation.isPending ? 'not-allowed' : 'pointer',
            }}
          >
            {runEvaluationMutation.isPending ? 'Starting Evaluation...' : 'Run Evaluation'}
          </button>

          {runEvaluationMutation.data && (
            <div style={{ 
              marginTop: '16px', 
              padding: '12px', 
              background: '#d1ecf1', 
              color: '#0c5460', 
              border: '1px solid #bee5eb', 
              borderRadius: '4px' 
            }}>
              <h3>Evaluation Submitted</h3>
              <p><strong>Evaluation ID:</strong> {runEvaluationMutation.data.evaluationId}</p>
              <p><strong>Batch Job ID:</strong> {runEvaluationMutation.data.batchJobId}</p>
              <p style={{ marginTop: '8px', fontSize: '14px' }}>
                The evaluation job has been submitted. You can monitor its progress in the system.
              </p>
            </div>
          )}
        </form>
      )}
    </div>
  );
};

export default Evaluation;

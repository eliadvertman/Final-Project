import React, { useState, useEffect } from 'react';
import { useTrainModel } from '../hooks';
import type { TrainingConfig } from '../types';

interface NotificationState {
  type: 'success' | 'error' | 'warning' | null;
  message: string;
  details?: string;
}

const ModelTraining: React.FC = () => {
  const [formData, setFormData] = useState<TrainingConfig>({
    modelName: '',
    imagesPath: '',
    labelsPath: '',
    foldIndex: undefined,
    taskNumber: undefined,
  });

  const [notification, setNotification] = useState<NotificationState>({
    type: null,
    message: '',
  });

  const trainModelMutation = useTrainModel();

  // Auto-dismiss success notifications after 5 seconds
  useEffect(() => {
    if (notification.type === 'success') {
      const timer = setTimeout(() => {
        setNotification({ type: null, message: '' });
      }, 5000);
      return () => clearTimeout(timer);
    }
  }, [notification]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, type } = e.target;
    let processedValue: string | number | undefined = value;

    // Handle number inputs
    if (type === 'number') {
      if (value === '') {
        processedValue = undefined;
      } else {
        processedValue = parseInt(value, 10);
      }
    }

    setFormData(prev => ({
      ...prev,
      [name]: processedValue
    }));
    // Clear any existing notifications when user starts typing
    if (notification.type) {
      setNotification({ type: null, message: '' });
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Client-side validation
    if (!formData.modelName.trim()) {
      setNotification({
        type: 'error',
        message: 'Model name is required',
        details: 'Please enter a unique name for your model before starting training.'
      });
      return;
    }

    try {
      const result = await trainModelMutation.mutateAsync(formData);
      setNotification({
        type: 'success',
        message: 'Training started successfully!',
        details: `Model ID: ${result.modelId}. You can monitor progress in the Model Management page.`
      });
      
      // Reset form on success
      setFormData({
        modelName: '',
        imagesPath: '',
        labelsPath: '',
        foldIndex: undefined,
        taskNumber: undefined,
      });
    } catch (error: any) {
      const errorMessage = error?.response?.data?.message || error?.message || 'Failed to start training';
      setNotification({
        type: 'error',
        message: 'Failed to start training',
        details: errorMessage
      });
    }
  };

  const dismissNotification = () => {
    setNotification({ type: null, message: '' });
  };

  return (
    <div style={{ padding: '20px' }}>
      <h1>Train New Model</h1>
      
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
      
      <form onSubmit={handleSubmit} style={{ maxWidth: '600px', marginTop: '20px' }}>
        <div style={{ marginBottom: '16px' }}>
          <label style={{ display: 'block', marginBottom: '4px', fontWeight: 'bold' }}>
            Model Name *
          </label>
          <input
            type="text"
            name="modelName"
            value={formData.modelName}
            onChange={handleInputChange}
            required
            style={{
              width: '100%',
              padding: '8px',
              border: '1px solid #ddd',
              borderRadius: '4px',
              fontSize: '14px'
            }}
            placeholder="Enter a unique name for your model"
          />
        </div>

        <div style={{ marginBottom: '16px' }}>
          <label style={{ display: 'block', marginBottom: '4px', fontWeight: 'bold' }}>
            Images Path
          </label>
          <input
            type="text"
            name="imagesPath"
            value={formData.imagesPath}
            onChange={handleInputChange}
            style={{
              width: '100%',
              padding: '8px',
              border: '1px solid #ddd',
              borderRadius: '4px',
              fontSize: '14px'
            }}
            placeholder="/path/to/images"
          />
        </div>

        <div style={{ marginBottom: '16px' }}>
          <label style={{ display: 'block', marginBottom: '4px', fontWeight: 'bold' }}>
            Labels Path
          </label>
          <input
            type="text"
            name="labelsPath"
            value={formData.labelsPath}
            onChange={handleInputChange}
            style={{
              width: '100%',
              padding: '8px',
              border: '1px solid #ddd',
              borderRadius: '4px',
              fontSize: '14px'
            }}
            placeholder="/path/to/labels"
          />
        </div>

        <div style={{ marginBottom: '16px' }}>
          <label style={{ display: 'block', marginBottom: '4px', fontWeight: 'bold' }}>
            Fold Index
          </label>
          <input
            type="number"
            name="foldIndex"
            value={formData.foldIndex || ''}
            onChange={handleInputChange}
            style={{
              width: '100%',
              padding: '8px',
              border: '1px solid #ddd',
              borderRadius: '4px',
              fontSize: '14px'
            }}
            placeholder="Enter fold index for cross-validation"
            min="0"
          />
        </div>

        <div style={{ marginBottom: '16px' }}>
          <label style={{ display: 'block', marginBottom: '4px', fontWeight: 'bold' }}>
            Task Number
          </label>
          <input
            type="number"
            name="taskNumber"
            value={formData.taskNumber || ''}
            onChange={handleInputChange}
            style={{
              width: '100%',
              padding: '8px',
              border: '1px solid #ddd',
              borderRadius: '4px',
              fontSize: '14px'
            }}
            placeholder="Enter task number for SLURM job identification"
            min="0"
          />
        </div>

        <button
          type="submit"
          disabled={trainModelMutation.isPending}
          style={{
            background: trainModelMutation.isPending ? '#ccc' : '#007bff',
            color: 'white',
            padding: '12px 24px',
            border: 'none',
            borderRadius: '4px',
            fontSize: '16px',
            cursor: trainModelMutation.isPending ? 'not-allowed' : 'pointer',
          }}
        >
          {trainModelMutation.isPending ? 'Starting Training...' : 'Start Training'}
        </button>
      </form>
    </div>
  );
};

export default ModelTraining;
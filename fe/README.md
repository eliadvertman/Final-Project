# ML Prediction Platform - Frontend

A modern React-based web interface for machine learning model training and prediction management.

## Features

### 🎯 Model Training
- **Interactive Training Form**: Submit new models with folder paths for images, labels, and datasets
- **Real-time Progress Monitoring**: Live updates on training status with progress indicators
- **Training History**: View all trained models with status tracking

### 🤖 Model Management
- **Model Dashboard**: Comprehensive overview of all models
- **Status Tracking**: Real-time monitoring of model states (PENDING, TRAINING, TRAINED, FAILED, DEPLOYED)
- **Progress Visualization**: Visual progress bars for training models
- **Error Reporting**: Detailed error messages for failed training

### 🔮 Prediction Engine
- **Smart Model Selection**: Dropdown of available trained models
- **JSON Input Interface**: Flexible input data entry with syntax validation
- **Real-time Results**: Instant prediction results with formatted output
- **Input Validation**: Built-in JSON validation and error handling

### 📊 Dashboard & Analytics
- **Overview Statistics**: Quick stats on models and predictions
- **Recent Activity**: Latest models and predictions at a glance
- **Status Distribution**: Visual breakdown of model and prediction states

### 📋 Prediction History
- **Comprehensive History**: All prediction requests with detailed status
- **Status Monitoring**: Real-time updates for processing predictions
- **Timing Information**: Start/end times and duration tracking
- **Error Diagnostics**: Detailed error reporting for failed predictions

## Technology Stack

- **React 19** with TypeScript for type safety
- **Vite** for fast development and building
- **React Query (TanStack Query)** for efficient API state management
- **React Router** for client-side routing
- **Axios** for HTTP requests
- **Modern CSS** with responsive design

## Getting Started

### Prerequisites
- Node.js 16+ and npm
- Running ML Prediction API server (backend)

### Installation

1. **Clone and install dependencies:**
   ```bash
   cd fe
   npm install
   ```

2. **Start development server:**
   ```bash
   npm run dev
   ```

3. **Build for production:**
   ```bash
   npm run build
   ```

4. **Preview production build:**
   ```bash
   npm run preview
   ```

### Development Commands
- `npm run dev` - Start development server on http://localhost:5173
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

## API Configuration

The frontend communicates with the ML Prediction API at `http://localhost:8080/api/v1`. 

Update the API base URL in `src/services/api.ts` if your backend runs on a different port:

```typescript
const API_BASE_URL = 'http://localhost:8080/api/v1';
```

## Architecture

### Project Structure
```
src/
├── components/          # Reusable UI components
│   ├── Navigation.tsx   # Main navigation bar
│   └── Layout.tsx       # Page layout wrapper
├── pages/              # Main application pages
│   ├── Dashboard.tsx    # Overview dashboard
│   ├── ModelTraining.tsx # Model training interface
│   ├── ModelManagement.tsx # Model management
│   ├── Prediction.tsx   # Make predictions
│   └── PredictionHistory.tsx # View prediction history
├── hooks/              # Custom React hooks
│   ├── useModels.ts     # Model-related queries
│   └── usePredictions.ts # Prediction-related queries
├── services/           # API service layer
│   └── api.ts          # HTTP client and API methods
├── types/              # TypeScript type definitions
│   └── api.ts          # API response types
└── utils/              # Utility functions
```

### Key Features

1. **Real-time Updates**: Automatic polling for status updates using React Query
2. **Type Safety**: Full TypeScript coverage with API response types
3. **Error Handling**: Comprehensive error boundaries and user feedback
4. **Responsive Design**: Works on desktop and mobile devices
5. **Performance Optimized**: Efficient re-renders and caching with React Query

## API Integration

The frontend integrates with the following API endpoints:

### Model Management
- `POST /api/v1/model/train` - Start model training
- `GET /api/v1/model/{modelId}/status` - Get training status
- `GET /api/v1/model/list` - List all models

### Predictions
- `POST /api/v1/predict/predict` - Make predictions
- `GET /api/v1/predict/{predictId}/status` - Get prediction status  
- `GET /api/v1/predict/list` - List all predictions

## Real-time Features

- **Auto-refresh**: Models and predictions refresh every 5 seconds
- **Status polling**: Active training/prediction status updates every 2 seconds
- **Progress tracking**: Real-time progress bars for training models
- **Error monitoring**: Instant error reporting and recovery

## Usage Guide

### 1. Training a Model
1. Navigate to "Train Model" page
2. Enter a unique model name
3. Provide folder paths for images, labels, and dataset
4. Click "Start Training"
5. Monitor progress in "Model Management"

### 2. Making Predictions
1. Navigate to "Make Prediction" page
2. Select a trained model from the dropdown
3. Enter input data in JSON format
4. Click "Make Prediction"
5. View results immediately or check "Prediction History"

### 3. Monitoring
- Use the Dashboard for overview statistics
- Check Model Management for training progress
- View Prediction History for detailed logs

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes following TypeScript and React best practices
4. Test thoroughly with the backend API
5. Submit a pull request

## Troubleshooting

### Common Issues

1. **API Connection Errors**: Ensure the backend server is running on port 8080
2. **Build Errors**: Run `npm install` to ensure all dependencies are installed
3. **TypeScript Errors**: Check that all types are properly imported

### Development Tips

1. Use browser DevTools Network tab to debug API calls
2. Check React Query DevTools for cache and query state
3. Monitor console for error logs and warnings

## License

This project is part of the ML Prediction Platform suite.

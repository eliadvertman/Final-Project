# Frontend Architecture Documentation

This document provides comprehensive documentation for the React/TypeScript frontend application of the ML Prediction Platform.

## Table of Contents
- [Architecture Overview](#architecture-overview)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Component Architecture](#component-architecture)
- [API Integration](#api-integration)
- [State Management](#state-management)
- [Development Workflow](#development-workflow)
- [Build and Deployment](#build-and-deployment)

## Architecture Overview

The frontend is a modern **Single Page Application (SPA)** built with React and TypeScript, providing a responsive web interface for the ML Prediction Platform. It follows a **component-based architecture** with clear separation of concerns:

- **UI Components**: Reusable presentation components
- **Pages**: Route-level components representing different application views
- **Hooks**: Custom React hooks for business logic and API interactions
- **Services**: API integration layer with type-safe HTTP client
- **Types**: TypeScript interfaces for type safety and API contracts

### Key Design Principles
- **Type Safety**: Full TypeScript implementation with strict type checking
- **Component Reusability**: Modular components with clear interfaces
- **State Management**: React Query for server state + local component state
- **API Integration**: Centralized HTTP client with error handling and logging
- **Responsive Design**: Adaptive UI with modern styling patterns

## Technology Stack

### Core Technologies
- **React 19.1.1**: Modern React with hooks and functional components
- **TypeScript 5.8.3**: Static type checking and enhanced developer experience
- **Vite 7.1.2**: Fast build tool and development server
- **React Router DOM 7.8.2**: Client-side routing and navigation

### State Management & API
- **@tanstack/react-query 5.87.1**: Server state management, caching, and synchronization
- **Axios 1.11.0**: HTTP client for API communication with interceptors

### Development Tools
- **ESLint 9.33.0**: Code linting with TypeScript and React rules
- **@vitejs/plugin-react 5.0.0**: Vite plugin for React support
- **TypeScript ESLint**: Enhanced TypeScript linting rules

### Build & Configuration
- **Project Type**: ES Module (`"type": "module"`)
- **Build Pipeline**: TypeScript compilation + Vite bundling
- **Dev Server**: Vite development server with HMR (Hot Module Replacement)

## Project Structure

```
fe/
├── src/
│   ├── components/           # Reusable UI components
│   │   ├── Layout.tsx       # Main application layout wrapper
│   │   ├── Navigation.tsx   # Navigation header component
│   │   └── index.ts         # Component exports
│   ├── hooks/               # Custom React hooks
│   │   ├── useModels.ts     # Model-related data fetching
│   │   ├── usePredictions.ts # Prediction-related data fetching
│   │   ├── useTraining.ts   # Training-related mutations
│   │   └── index.ts         # Hook exports
│   ├── pages/               # Route-level page components
│   │   ├── Dashboard.tsx    # Main dashboard view
│   │   ├── ModelTraining.tsx # Model training form
│   │   ├── Models.tsx       # Model management view
│   │   ├── Prediction.tsx   # Prediction creation form
│   │   ├── PredictionHistory.tsx # Prediction history view
│   │   └── index.ts         # Page exports
│   ├── services/            # API integration layer
│   │   ├── api.ts          # HTTP client and API methods
│   │   └── index.ts        # Service exports
│   ├── types/               # TypeScript type definitions
│   │   ├── api.ts          # API contract types
│   │   └── index.ts        # Type exports
│   ├── utils/               # Utility functions
│   │   └── dateUtils.ts    # Date formatting utilities
│   ├── App.tsx             # Root application component
│   ├── main.tsx            # Application entry point
│   └── vite-env.d.ts       # Vite type declarations
├── dist/                    # Build output directory
├── node_modules/           # Dependencies
├── package.json            # Project configuration
├── tsconfig.json          # TypeScript configuration
├── vite.config.ts         # Vite build configuration
└── eslint.config.js       # ESLint configuration
```

## Component Architecture

### Layout Structure
The application uses a **hierarchical layout pattern**:

```
App (Router + QueryClient Provider)
└── Layout (Navigation + Main Content Area)
    └── Routes (Page Components)
        ├── Dashboard
        ├── ModelTraining
        ├── Models
        ├── Prediction
        └── PredictionHistory
```

### Core Components

#### Layout.tsx
```typescript
interface LayoutProps {
  children: React.ReactNode;
}
```
- **Purpose**: Main application shell with navigation
- **Features**: Responsive design, consistent styling
- **Structure**: Header navigation + main content area

#### Navigation.tsx
```typescript
const navItems = [
  { path: '/', label: 'Dashboard', icon: '📊' },
  { path: '/train', label: 'Train Model', icon: '🎯' },
  { path: '/models', label: 'Models', icon: '🤖' },
  { path: '/predict', label: 'Make Prediction', icon: '🔮' },
  { path: '/history', label: 'Prediction History', icon: '📋' },
];
```
- **Purpose**: Application navigation with active state management
- **Features**: Icon-based navigation, hover effects, responsive design
- **Routing**: React Router integration with `useLocation` hook

### Page Components

#### Dashboard.tsx
- **Purpose**: Overview dashboard with statistics and recent activity
- **Data Sources**: Models list + Predictions list via React Query
- **Features**: Real-time statistics, recent items display

#### ModelTraining.tsx
- **Purpose**: Model training configuration and submission
- **Form Management**: Controlled form with validation
- **Features**: Client-side validation, error handling, success notifications
- **API Integration**: Training mutation with loading states

#### Models.tsx / Prediction.tsx / PredictionHistory.tsx
- **Purpose**: Specialized views for different ML operations
- **Pattern**: List/detail views with real-time updates
- **State Management**: React Query for server state synchronization

## API Integration

### HTTP Client Configuration
```typescript
const apiClient = axios.create({
  baseURL: 'http://localhost:8080/api/v1',
  headers: { 'Content-Type': 'application/json' },
  timeout: 30000, // 30 seconds
});
```

### API Service Architecture
The API layer is organized into **domain-specific modules**:

```typescript
export const api = {
  models: modelApi,      // Model management endpoints
  training: trainingApi, // Training operations
  predictions: predictionApi, // Prediction/inference operations
};
```

### API Endpoints Mapping

#### Model API (`/model/*`)
```typescript
modelApi = {
  getModelStatus: (modelId: string) => GET `/model/${modelId}/status`,
  listModels: (limit, offset) => GET `/model/list?limit=${limit}&offset=${offset}`,
}
```

#### Training API (`/training/*`)
```typescript
trainingApi = {
  trainModel: (config: TrainingConfig) => POST `/training/train`,
  getTrainingStatus: (trainingId: string) => GET `/training/${trainingId}/status`,
  listTrainings: (limit, offset) => GET `/training/list?limit=${limit}&offset=${offset}`,
}
```

#### Prediction API (`/inference/*`)
```typescript
predictionApi = {
  makePrediction: (request: PredictionRequest) => POST `/inference/predict`,
  getPredictionStatus: (predictId: string) => GET `/inference/${predictId}/status`,
  listPredictions: (limit, offset) => GET `/inference/list?limit=${limit}&offset=${offset}`,
}
```

### Request/Response Interceptors
```typescript
// Request logging
apiClient.interceptors.request.use((config) => {
  console.log(`🚀 API Request: ${config.method?.toUpperCase()} ${config.url}`);
  return config;
});

// Response logging and error handling
apiClient.interceptors.response.use(
  (response) => {
    console.log(`✅ API Response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error(`❌ API Error: ${error.response?.status}`, error.response?.data);
    return Promise.reject(error);
  }
);
```

## State Management

### React Query Configuration
```typescript
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      refetchOnWindowFocus: false,
    },
  },
});
```

### Query Key Patterns
```typescript
const QUERY_KEYS = {
  MODELS: ['models'],
  TRAININGS: ['trainings'],
  PREDICTIONS: ['predictions'],
  MODEL_STATUS: (id: string) => ['models', id, 'status'],
  TRAINING_STATUS: (id: string) => ['trainings', id, 'status'],
  PREDICTION_STATUS: (id: string) => ['predictions', id, 'status'],
} as const;
```

### Custom Hooks Architecture

#### Data Fetching Hooks
```typescript
// Models and Training Sessions
export const useModels = () => useQuery({
  queryKey: QUERY_KEYS.TRAININGS,
  queryFn: () => api.training.listTrainings(),
  refetchInterval: 5000, // Real-time updates
});

// Trained Models for Predictions
export const useTrainedModels = () => useQuery({
  queryKey: QUERY_KEYS.MODELS,
  queryFn: () => api.models.listModels(),
  refetchInterval: 5000,
});

// Status Monitoring with Conditional Fetching
export const useModelStatus = (trainingId: string, enabled = true) => useQuery({
  queryKey: QUERY_KEYS.TRAINING_STATUS(trainingId),
  queryFn: () => api.training.getTrainingStatus(trainingId),
  refetchInterval: 2000, // Frequent updates for status
  enabled: enabled && !!trainingId,
});
```

#### Mutation Hooks
```typescript
export const useTrainModel = () => {
  return useMutation({
    mutationFn: (config: TrainingConfig) => api.training.trainModel(config),
    onSuccess: () => {
      // Invalidate related queries to trigger refetch
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.TRAININGS });
    },
  });
};
```

### State Management Patterns

1. **Server State**: Managed by React Query with automatic caching and synchronization
2. **Component State**: Local state with `useState` for forms and UI interactions
3. **URL State**: Route parameters and query strings via React Router
4. **Global State**: Minimal - primarily handled through React Query cache

## Type Safety

### API Contract Types
```typescript
// Training Configuration
export interface TrainingConfig {
  modelName: string;
  imagesPath?: string;
  labelsPath?: string;
  foldIndex?: number;
}

// Status Enums with Union Types
export interface ModelStatus {
  modelId: string;
  status: 'PENDING' | 'TRAINING' | 'TRAINED' | 'FAILED' | 'DEPLOYED';
  progress: number;
  startTime?: string;
  endTime?: string;
  errorMessage?: string;
}

// Prediction Workflow Types
export interface PredictionRequest {
  modelId: string;
  inputPath: string;
  foldIndex: number;
}
```

### Type-Safe API Integration
```typescript
// Generic HTTP response typing
const response: AxiosResponse<ModelStatus> = await apiClient.get(`/model/${modelId}/status`);
return response.data; // Fully typed ModelStatus object
```

## Development Workflow

### Available Scripts
```json
{
  "dev": "vite",                    // Start development server
  "build": "tsc -b && vite build", // Type check + build
  "lint": "eslint .",               // Run linting
  "preview": "vite preview"         // Preview build
}
```

### Development Server
- **Port**: Default Vite port (typically 5173)
- **Hot Reload**: Automatic component updates on file changes
- **API Proxy**: Configure in `vite.config.ts` if needed

### Code Quality Tools
- **TypeScript**: Strict type checking with `tsc -b`
- **ESLint**: React and TypeScript specific rules
- **React Rules**: Hook dependencies, JSX patterns
- **Import Rules**: Module resolution and organization

## Build and Deployment

### Build Process
1. **Type Checking**: `tsc -b` validates all TypeScript code
2. **Bundling**: Vite bundles and optimizes for production
3. **Output**: Static files in `dist/` directory
4. **Assets**: Code splitting, tree shaking, and minification

### Build Configuration
```typescript
// vite.config.ts
export default defineConfig({
  plugins: [react()],
  // Additional production optimizations can be added here
});
```

### Deployment Options
- **Static Hosting**: Deploy `dist/` folder to any static host
- **CDN Integration**: All assets are bundled and optimized
- **Environment Configuration**: API endpoints can be configured per environment

### Production Considerations
- **API Base URL**: Update `API_BASE_URL` in `api.ts` for production
- **Error Boundaries**: Add React error boundaries for production error handling
- **Performance Monitoring**: Consider adding performance monitoring tools
- **Bundle Analysis**: Use `vite-bundle-analyzer` to optimize bundle size

## Frontend-Backend Integration

### API Endpoint Alignment
The frontend is designed to work seamlessly with the Python Flask backend:

| Frontend Service | Backend Endpoint | Purpose |
|-----------------|------------------|---------|
| `modelApi.listModels()` | `GET /api/v1/model/list` | List trained models |
| `trainingApi.trainModel()` | `POST /api/v1/training/train` | Start training job |
| `predictionApi.makePrediction()` | `POST /api/v1/inference/predict` | Submit prediction |
| Status endpoints | `GET /api/v1/{resource}/{id}/status` | Real-time status updates |

### Real-time Updates
- **Polling Strategy**: React Query automatically refetches data every 2-5 seconds
- **Status Monitoring**: Frequent updates for job status tracking
- **Error Recovery**: Automatic retry on network failures

### Development Setup
1. **Backend**: Start Flask server on `localhost:8080`
2. **Frontend**: Start Vite dev server on `localhost:5173`
3. **CORS**: Backend configured to accept frontend requests
4. **API Testing**: Both services can be tested independently

## Future Enhancements

### Potential Improvements
- **WebSocket Integration**: Real-time updates instead of polling
- **Progressive Web App (PWA)**: Offline capability and app-like experience
- **Component Library**: Shared design system with Storybook
- **Performance Optimization**: Code splitting, lazy loading, virtual scrolling
- **Testing**: Unit tests with React Testing Library, E2E tests with Cypress
- **Accessibility**: WCAG compliance and screen reader support
- **Internationalization**: Multi-language support with i18n libraries

### Architecture Evolution
- **State Management**: Consider Zustand or Redux Toolkit for complex state
- **Styling**: Migrate to styled-components or Tailwind CSS
- **Form Management**: Integrate React Hook Form for complex forms
- **Error Handling**: Global error boundary and user-friendly error pages
- **Authentication**: JWT token management and protected routes
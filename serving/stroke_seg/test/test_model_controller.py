import pytest
import json
import uuid
from datetime import datetime

from stroke_seg.dao.models import TrainingRecord
from stroke_seg.app import app

@pytest.fixture
def client():
    """Create test client."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def sample_model(clean_db):
    """Create a sample model for testing."""
    model = ModelRecord(
        name="TestModel",
        images_path="/test/images",
        labels_path="/test/labels",
        dataset_path="/test/dataset",
        status="TRAINED",
        progress=100.0,
        start_time=datetime.now(),
        end_time=datetime.now()
    )
    model.save()
    yield model

class TestModelTraining:
    """Test cases for model training endpoint."""
    
    def test_train_model_success(self, client, clean_db):
        """Test successful model training initiation."""
        payload = {
            "modelName": "TestModel",
            "imagesPath": "/test/images",
            "labelsPath": "/test/labels",
            "datasetPath": "/test/dataset"
        }
        
        response = client.post('/api/v1/training/train', 
                             data=json.dumps(payload),
                             content_type='application/json')
        
        assert response.status_code == 202
        data = json.loads(response.data)
        assert data['message'] == "Model training started."
        assert 'modelId' in data
        assert uuid.UUID(data['modelId'])
        
        # Verify model was created in database
        model = ModelRecord.get(ModelRecord.model_id == data['modelId'])
        assert model.name == "TestModel"
        assert model.status == "PENDING"
        assert model.progress == 0.0
    
    def test_train_model_without_model_name(self, client, clean_db):
        """Test training model without model name uses default."""
        payload = {
            "imagesPath": "/test/images",
            "labelsPath": "/test/labels"
        }
        
        response = client.post('/api/v1/training/train', 
                             data=json.dumps(payload),
                             content_type='application/json')
        
        assert response.status_code == 202
        data = json.loads(response.data)
        assert data['message'] == "Model training started."
        assert 'modelId' in data
        
        # Verify model was created with default name
        model = ModelRecord.get(ModelRecord.model_id == data['modelId'])
        assert model.name == "Unnamed Model"
    
    def test_train_model_invalid_json(self, client, clean_db):
        """Test training model with invalid JSON."""
        response = client.post('/api/v1/training/train', 
                             data="invalid json",
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['message'] == "Invalid JSON payload"
    
    def test_train_model_empty_payload(self, client, clean_db):
        """Test training model with empty payload."""
        response = client.post('/api/v1/training/train', 
                             data=json.dumps({}),
                             content_type='application/json')
        
        assert response.status_code == 202
        data = json.loads(response.data)
        assert data['message'] == "Model training started."
        assert 'modelId' in data
        
        # Verify model was created with default name
        model = ModelRecord.get(ModelRecord.model_id == data['modelId'])
        assert model.name == "Unnamed Model"
    
    def test_train_model_with_optional_fields(self, client, clean_db):
        """Test training model with only required fields."""
        payload = {
            "modelName": "MinimalModel"
        }
        
        response = client.post('/api/v1/training/train', 
                             data=json.dumps(payload),
                             content_type='application/json')
        
        assert response.status_code == 202
        data = json.loads(response.data)
        assert 'modelId' in data
        
        # Verify model was created with null optional fields
        model = ModelRecord.get(ModelRecord.model_id == data['modelId'])
        assert model.name == "MinimalModel"
        assert model.images_path is None
        assert model.labels_path is None
        assert model.dataset_path is None

class TestModelStatus:
    """Test cases for model status endpoint."""
    
    def test_get_model_status_success(self, client, sample_model):
        """Test getting model status successfully."""
        response = client.get(f'/api/v1/model/{sample_model.model_id}/status')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['modelId'] == str(sample_model.model_id)
        assert data['status'] == sample_model.status
        assert data['progress'] == sample_model.progress
        assert 'startTime' in data
        assert 'endTime' in data
    
    def test_get_model_status_not_found(self, client, clean_db):
        """Test getting status of non-existent model."""
        fake_uuid = str(uuid.uuid4())
        response = client.get(f'/api/v1/model/{fake_uuid}/status')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['code'] == 404
        assert "not found" in data['message']
    
    def test_get_model_status_invalid_uuid(self, client, clean_db):
        """Test getting status with invalid UUID."""
        response = client.get('/api/v1/model/invalid-uuid/status')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['code'] == 400
        assert data['message'] == "Invalid model ID format"
    
    def test_get_model_status_with_error_message(self, client, clean_db):
        """Test getting status of model with error message."""
        model = ModelRecord(
            name="FailedModel",
            status="FAILED",
            progress=50.0,
            start_time=datetime.now(),
            error_message="Training failed due to insufficient data"
        )
        model.save()
        
        response = client.get(f'/api/v1/model/{model.model_id}/status')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == "FAILED"
        assert data['errorMessage'] == "Training failed due to insufficient data"
    
    def test_get_model_status_pending(self, client, clean_db):
        """Test getting status of pending model."""
        model = ModelRecord(
            name="PendingModel",
            status="PENDING",
            progress=0.0,
            start_time=datetime.now()
        )
        model.save()
        
        response = client.get(f'/api/v1/model/{model.model_id}/status')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == "PENDING"
        assert data['progress'] == 0.0
        assert 'startTime' in data
        assert 'endTime' not in data  # No end time for pending model

class TestModelList:
    """Test cases for model listing endpoint."""
    
    def test_list_models_success(self, client, sample_model):
        """Test listing models successfully."""
        response = client.get('/api/v1/model/list')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
        assert len(data) >= 1
        
        # Find our test model
        model_found = False
        for model in data:
            if model['modelId'] == str(sample_model.model_id):
                model_found = True
                assert model['modelName'] == sample_model.name
                assert model['status'] == sample_model.status
                assert 'createdAt' in model
                assert model['createdAt'].endswith('Z')  # ISO format with Z
                break
        assert model_found, "Test model not found in response"
    
    def test_list_models_empty(self, client, clean_db):
        """Test listing models when database is empty."""
        response = client.get('/api/v1/model/list')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
        assert len(data) == 0
    
    def test_list_models_pagination_limit(self, client, clean_db):
        """Test listing models with limit parameter."""
        # Create multiple models
        for i in range(5):
            model = ModelRecord(
                name=f"Model{i}",
                status="TRAINED",
                progress=100.0
            )
            model.save()
        
        response = client.get('/api/v1/model/list?limit=2')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
        assert len(data) == 2
    
    def test_list_models_pagination_offset(self, client, clean_db):
        """Test listing models with offset parameter."""
        # Create multiple models
        models = []
        for i in range(3):
            model = ModelRecord(
                name=f"Model{i}",
                status="TRAINED",
                progress=100.0
            )
            model.save()
            models.append(model)
        
        # Get first page
        response1 = client.get('/api/v1/model/list?limit=2&offset=0')
        assert response1.status_code == 200
        data1 = json.loads(response1.data)
        assert len(data1) == 2
        
        # Get second page
        response2 = client.get('/api/v1/model/list?limit=2&offset=2')
        assert response2.status_code == 200
        data2 = json.loads(response2.data)
        assert len(data2) == 1
        
        # Verify no overlap between pages
        page1_ids = {model['modelId'] for model in data1}
        page2_ids = {model['modelId'] for model in data2}
        assert page1_ids.isdisjoint(page2_ids)
    
    def test_list_models_invalid_pagination_params(self, client, clean_db):
        """Test listing models with invalid pagination parameters."""
        # Test with negative limit
        response = client.get('/api/v1/model/list?limit=-1')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['message'] == "Limit must be non-negative"
        
        # Test with negative offset
        response = client.get('/api/v1/model/list?offset=-1')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['message'] == "Offset must be non-negative"
    
    def test_list_models_multiple_statuses(self, client, clean_db):
        """Test listing models with different statuses."""
        statuses = ["PENDING", "TRAINING", "TRAINED", "FAILED", "DEPLOYED"]
        
        for status in statuses:
            model = ModelRecord(
                name=f"Model_{status}",
                status=status,
                progress=100.0 if status in ["TRAINED", "DEPLOYED"] else 0.0
            )
            model.save()
        
        response = client.get('/api/v1/model/list')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) == 5
        
        # Verify all statuses are present
        response_statuses = {model['status'] for model in data}
        assert response_statuses == set(statuses)
    
    def test_list_models_ordering(self, client, clean_db):
        """Test that models are ordered by creation date (newest first)."""
        # Create models with slight delay to ensure different timestamps
        import time
        
        first_model = ModelRecord(
            name="FirstModel",
            status="TRAINED",
            progress=100.0
        )
        first_model.save()
        
        time.sleep(0.01)  # Small delay
        
        second_model = ModelRecord(
            name="SecondModel", 
            status="TRAINED",
            progress=100.0
        )
        second_model.save()
        
        response = client.get('/api/v1/model/list')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) >= 2
        
        # Find our models in the response
        first_model_pos = None
        second_model_pos = None
        
        for i, model in enumerate(data):
            if model['modelId'] == str(first_model.model_id):
                first_model_pos = i
            elif model['modelId'] == str(second_model.model_id):
                second_model_pos = i
        
        assert first_model_pos is not None
        assert second_model_pos is not None
        assert second_model_pos < first_model_pos, "Models should be ordered by creation date (newest first)"
import pytest
import json
import uuid
from datetime import datetime

from main.dao.models import ModelRecord, InferenceRecord
from main.app import app

@pytest.fixture
def client():
    """Create test client."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def trained_model(clean_db):
    """Create a trained model for testing predictions."""
    model = ModelRecord(
        name="TrainedModel",
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

@pytest.fixture
def deployed_model(clean_db):
    """Create a deployed model for testing predictions."""
    model = ModelRecord(
        name="DeployedModel",
        images_path="/test/images",
        labels_path="/test/labels",
        dataset_path="/test/dataset", 
        status="DEPLOYED",
        progress=100.0,
        start_time=datetime.now(),
        end_time=datetime.now()
    )
    model.save()
    yield model

@pytest.fixture
def pending_model(clean_db):
    """Create a pending model for testing."""
    model = ModelRecord(
        name="PendingModel",
        status="PENDING",
        progress=0.0,
        start_time=datetime.now()
    )
    model.save()
    yield model

@pytest.fixture
def sample_inference(trained_model):
    """Create a sample inference record for testing."""
    inference = InferenceRecord(
        model_id=trained_model,
        input_data={"feature1": 10.5, "feature2": "test"},
        prediction={"result": "positive", "confidence": 0.95},
        status="COMPLETED",
        start_time=datetime.now(),
        end_time=datetime.now()
    )
    inference.save()
    yield inference

class TestMakePrediction:
    """Test cases for making predictions."""
    
    def test_make_prediction_success_trained_model(self, client, trained_model):
        """Test making a prediction with a trained model."""
        payload = {
            "modelId": str(trained_model.model_id),
            "inputData": {
                "feature1": 10.5,
                "feature2": "Value A",
                "feature3": True
            }
        }
        
        response = client.post('/api/v1/predict/predict', 
                             data=json.dumps(payload),
                             content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'predictId' in data
        assert uuid.UUID(data['predictId'])
        assert data['modelId'] == str(trained_model.model_id)
        assert 'prediction' in data
        assert 'timestamp' in data
        assert data['timestamp'].endswith('Z')
        
        # Verify inference was created in database
        inference = InferenceRecord.get(InferenceRecord.predict_id == data['predictId'])
        assert inference.model_id.model_id == trained_model.model_id
        assert inference.status == "COMPLETED"
        assert inference.input_data == payload['inputData']
        assert inference.prediction is not None
    
    def test_make_prediction_success_deployed_model(self, client, deployed_model):
        """Test making a prediction with a deployed model."""
        payload = {
            "modelId": str(deployed_model.model_id),
            "inputData": {
                "feature1": 20.0,
                "feature2": "Value B"
            }
        }
        
        response = client.post('/api/v1/predict/predict', 
                             data=json.dumps(payload),
                             content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'predictId' in data
        assert data['modelId'] == str(deployed_model.model_id)
    
    def test_make_prediction_model_not_found(self, client, clean_db):
        """Test making prediction with non-existent model."""
        fake_uuid = str(uuid.uuid4())
        payload = {
            "modelId": fake_uuid,
            "inputData": {"feature1": 10.5}
        }
        
        response = client.post('/api/v1/predict/predict', 
                             data=json.dumps(payload),
                             content_type='application/json')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['code'] == 404
        assert "not found" in data['message']
    
    def test_make_prediction_model_not_ready(self, client, pending_model):
        """Test making prediction with model not ready."""
        payload = {
            "modelId": str(pending_model.model_id),
            "inputData": {"feature1": 10.5}
        }
        
        response = client.post('/api/v1/predict/predict', 
                             data=json.dumps(payload),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['code'] == 400
        assert "not ready for predictions" in data['message']
    
    def test_make_prediction_missing_model_id(self, client, clean_db):
        """Test making prediction with missing model ID."""
        payload = {
            "inputData": {"feature1": 10.5}
        }
        
        response = client.post('/api/v1/predict/predict', 
                             data=json.dumps(payload),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['message'] == "Invalid model ID format"
    
    def test_make_prediction_missing_input_data(self, client, trained_model):
        """Test making prediction with missing input data uses empty dict."""
        payload = {
            "modelId": str(trained_model.model_id)
        }
        
        response = client.post('/api/v1/predict/predict', 
                             data=json.dumps(payload),
                             content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'predictId' in data
        
        # Verify inference was created with empty input data
        inference = InferenceRecord.get(InferenceRecord.predict_id == data['predictId'])
        assert inference.input_data == {}
    
    def test_make_prediction_invalid_json(self, client, clean_db):
        """Test making prediction with invalid JSON."""
        response = client.post('/api/v1/predict/predict', 
                             data="invalid json",
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['message'] == "Invalid JSON payload"
    
    def test_make_prediction_invalid_model_id_format(self, client, clean_db):
        """Test making prediction with invalid model ID format."""
        payload = {
            "modelId": "invalid-uuid",
            "inputData": {"feature1": 10.5}
        }
        
        response = client.post('/api/v1/predict/predict', 
                             data=json.dumps(payload),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['message'] == "Invalid model ID format"
    
    def test_make_prediction_complex_input_data(self, client, trained_model):
        """Test making prediction with complex input data."""
        payload = {
            "modelId": str(trained_model.model_id),
            "inputData": {
                "numerical_features": [1.0, 2.5, 3.7],
                "categorical_features": ["A", "B", "C"],
                "nested_object": {
                    "sub_feature1": "value1",
                    "sub_feature2": 42
                },
                "boolean_feature": True
            }
        }
        
        response = client.post('/api/v1/predict/predict', 
                             data=json.dumps(payload),
                             content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'predictId' in data
        
        # Verify complex input data was stored correctly
        inference = InferenceRecord.get(InferenceRecord.predict_id == data['predictId'])
        assert inference.input_data == payload['inputData']

class TestPredictionStatus:
    """Test cases for prediction status endpoint."""
    
    def test_get_prediction_status_success(self, client, sample_inference):
        """Test getting prediction status successfully."""
        response = client.get(f'/api/v1/predict/{sample_inference.predict_id}/status')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['predictId'] == str(sample_inference.predict_id)
        assert data['status'] == sample_inference.status
        assert data['modelId'] == str(sample_inference.model_id.model_id)
        assert 'startTime' in data
        assert 'endTime' in data
        assert data['startTime'].endswith('Z')
        assert data['endTime'].endswith('Z')
    
    def test_get_prediction_status_not_found(self, client, clean_db):
        """Test getting status of non-existent prediction."""
        fake_uuid = str(uuid.uuid4())
        response = client.get(f'/api/v1/predict/{fake_uuid}/status')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['code'] == 404
        assert "not found" in data['message']
    
    def test_get_prediction_status_invalid_uuid(self, client, clean_db):
        """Test getting prediction status with invalid UUID."""
        response = client.get('/api/v1/predict/invalid-uuid/status')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['code'] == 400
        assert data['message'] == "Invalid prediction ID format"
    
    def test_get_prediction_status_with_error(self, client, trained_model):
        """Test getting status of prediction with error."""
        inference = InferenceRecord(
            model_id=trained_model,
            input_data={"feature1": "invalid"},
            status="FAILED",
            start_time=datetime.now(),
            end_time=datetime.now(),
            error_message="Invalid input data format"
        )
        inference.save()
        
        response = client.get(f'/api/v1/predict/{inference.predict_id}/status')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == "FAILED"
        assert data['errorMessage'] == "Invalid input data format"
    
    def test_get_prediction_status_pending(self, client, trained_model):
        """Test getting status of pending prediction."""
        inference = InferenceRecord(
            model_id=trained_model,
            input_data={"feature1": 10.5},
            status="PENDING",
            start_time=datetime.now()
        )
        inference.save()
        
        response = client.get(f'/api/v1/predict/{inference.predict_id}/status')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == "PENDING"
        assert 'startTime' in data
        assert 'endTime' not in data  # No end time for pending prediction
        assert 'errorMessage' not in data

class TestPredictionList:
    """Test cases for prediction listing endpoint."""
    
    def test_list_predictions_success(self, client, sample_inference):
        """Test listing predictions successfully."""
        response = client.get('/api/v1/predict/list')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
        assert len(data) >= 1
        
        # Find our test prediction
        prediction_found = False
        for prediction in data:
            if prediction['predictId'] == str(sample_inference.predict_id):
                prediction_found = True
                assert prediction['modelId'] == str(sample_inference.model_id.model_id)
                assert prediction['status'] == sample_inference.status
                assert 'createdAt' in prediction
                assert prediction['createdAt'].endswith('Z')
                break
        assert prediction_found, "Test prediction not found in response"
    
    def test_list_predictions_empty(self, client, clean_db):
        """Test listing predictions when database is empty."""
        response = client.get('/api/v1/predict/list')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
        assert len(data) == 0
    
    def test_list_predictions_pagination_limit(self, client, trained_model):
        """Test listing predictions with limit parameter."""
        # Create multiple predictions
        for i in range(5):
            inference = InferenceRecord(
                model_id=trained_model,
                input_data={"feature1": i},
                prediction={"result": f"result_{i}"},
                status="COMPLETED"
            )
            inference.save()
        
        response = client.get('/api/v1/predict/list?limit=2')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
        assert len(data) == 2
    
    def test_list_predictions_pagination_offset(self, client, trained_model):
        """Test listing predictions with offset parameter."""
        # Create multiple predictions
        predictions = []
        for i in range(3):
            inference = InferenceRecord(
                model_id=trained_model,
                input_data={"feature1": i},
                prediction={"result": f"result_{i}"},
                status="COMPLETED"
            )
            inference.save()
            predictions.append(inference)
        
        # Get first page
        response1 = client.get('/api/v1/predict/list?limit=2&offset=0')
        assert response1.status_code == 200
        data1 = json.loads(response1.data)
        assert len(data1) == 2
        
        # Get second page
        response2 = client.get('/api/v1/predict/list?limit=2&offset=2')
        assert response2.status_code == 200
        data2 = json.loads(response2.data)
        assert len(data2) == 1
        
        # Verify no overlap between pages
        page1_ids = {pred['predictId'] for pred in data1}
        page2_ids = {pred['predictId'] for pred in data2}
        assert page1_ids.isdisjoint(page2_ids)
    
    def test_list_predictions_multiple_statuses(self, client, trained_model):
        """Test listing predictions with different statuses."""
        statuses = ["PENDING", "PROCESSING", "COMPLETED", "FAILED"]
        
        for status in statuses:
            inference = InferenceRecord(
                model_id=trained_model,
                input_data={"feature1": f"input_{status}"},
                prediction={"result": f"result_{status}"} if status == "COMPLETED" else None,
                status=status,
                error_message=f"Error for {status}" if status == "FAILED" else None
            )
            inference.save()
        
        response = client.get('/api/v1/predict/list')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) == 4
        
        # Verify all statuses are present
        response_statuses = {pred['status'] for pred in data}
        assert response_statuses == set(statuses)
    
    def test_list_predictions_ordering(self, client, trained_model):
        """Test that predictions are ordered by creation date (newest first)."""
        import time
        
        # Create first prediction
        first_inference = InferenceRecord(
            model_id=trained_model,
            input_data={"feature1": "first"},
            prediction={"result": "first"},
            status="COMPLETED"
        )
        first_inference.save()
        
        time.sleep(0.01)  # Small delay
        
        # Create second prediction
        second_inference = InferenceRecord(
            model_id=trained_model,
            input_data={"feature1": "second"},
            prediction={"result": "second"},
            status="COMPLETED"
        )
        second_inference.save()
        
        response = client.get('/api/v1/predict/list')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) >= 2
        
        # Find our predictions in the response
        first_pred_pos = None
        second_pred_pos = None
        
        for i, pred in enumerate(data):
            if pred['predictId'] == str(first_inference.predict_id):
                first_pred_pos = i
            elif pred['predictId'] == str(second_inference.predict_id):
                second_pred_pos = i
        
        assert first_pred_pos is not None
        assert second_pred_pos is not None
        assert second_pred_pos < first_pred_pos, "Predictions should be ordered by creation date (newest first)"
    
    def test_list_predictions_multiple_models(self, client, clean_db):
        """Test listing predictions from multiple models."""
        # Create two different models
        model1 = ModelRecord(
            name="Model1",
            status="TRAINED",
            progress=100.0
        )
        model1.save()
        
        model2 = ModelRecord(
            name="Model2", 
            status="TRAINED",
            progress=100.0
        )
        model2.save()
        
        # Create predictions for both models
        inference1 = InferenceRecord(
            model_id=model1,
            input_data={"feature1": "model1_input"},
            prediction={"result": "model1_result"},
            status="COMPLETED"
        )
        inference1.save()
        
        inference2 = InferenceRecord(
            model_id=model2,
            input_data={"feature1": "model2_input"},
            prediction={"result": "model2_result"},
            status="COMPLETED"
        )
        inference2.save()
        
        response = client.get('/api/v1/predict/list')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) == 2
        
        # Verify both models are represented
        model_ids = {pred['modelId'] for pred in data}
        expected_model_ids = {str(model1.model_id), str(model2.model_id)}
        assert model_ids == expected_model_ids
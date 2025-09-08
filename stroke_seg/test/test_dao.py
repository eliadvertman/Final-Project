import uuid
from datetime import datetime

from stroke_seg.dao.inference_dao import InferenceDAO
from stroke_seg.dao.model_dao import ModelDAO
from stroke_seg.dao.models import ModelRecord, InferenceRecord


class TestDatabaseIntegration:
    """Integration tests for basic CRUD operations across the database."""

    def test_model_dao_crud_integration(self, clean_db):
        """Test basic CRUD operations for ModelDAO."""
        dao = ModelDAO()

        # CREATE
        model_record = ModelRecord(
            name="test_model",
            status="TRAINING",
            progress=50.0,
            start_time=datetime.now()
        )
        model = dao.create(model_record)
        assert model.model_id is not None

        # READ
        retrieved_by_uuid = dao.get_by_model_id(uuid.UUID(model.model_id))
        assert retrieved_by_uuid.name == "test_model"

        # UPDATE
        updated = dao.update(uuid.UUID(model.model_id), status="TRAINED")
        assert updated.status == "TRAINED"

        # DELETE
        assert dao.delete(uuid.UUID(model.model_id)) is True
        assert dao.get_by_model_id(uuid.UUID(model.model_id)) is None

    def test_inference_dao_crud_integration(self, clean_db):
        """Test basic CRUD operations for InferenceDAO."""
        model_dao = ModelDAO()
        inference_dao = InferenceDAO()

        # Create a model first
        model_record = ModelRecord(
            name="test_model", 
            status="TRAINED",
            progress=100.0
        )
        model = model_dao.create(model_record)

        # CREATE
        inference_record = InferenceRecord(
            model_id=model,
            input_data={"feature1": 10.5},
            prediction={"result": "test"},
            status="COMPLETED",
            start_time=datetime.now(),
            end_time=datetime.now()
        )
        inference = inference_dao.create(inference_record)
        assert inference.predict_id is not None

        # READ
        retrieved_by_uuid = inference_dao.get_by_predict_id(uuid.UUID(inference.predict_id))
        assert retrieved_by_uuid.status == "COMPLETED"
        assert retrieved_by_uuid.model_id.model_id == model.model_id

        # UPDATE
        updated = inference_dao.update(uuid.UUID(inference.predict_id), status="FAILED")
        assert updated.status == "FAILED"

        # DELETE
        assert inference_dao.delete(uuid.UUID(inference.predict_id)) is True
        assert inference_dao.get_by_predict_id(uuid.UUID(inference.predict_id)) is None

    def test_model_inference_relationship(self, clean_db):
        """Test basic relationship between models and inferences."""
        model_dao = ModelDAO()
        inference_dao = InferenceDAO()

        # Create model
        model_record = ModelRecord(
            name="ml_model",
            status="DEPLOYED",
            progress=100.0
        )
        model = model_dao.create(model_record)

        # Create inference for the model
        inference_record = InferenceRecord(
            model_id=model,
            input_data={"feature1": 15.0},
            prediction={"result": "positive"},
            status="COMPLETED"
        )
        inference = inference_dao.create(inference_record)

        # Test relationship queries
        model_inferences = inference_dao.get_by_model_id(uuid.UUID(model.model_id))
        assert len(model_inferences) == 1
        assert model_inferences[0].predict_id == inference.predict_id
        
        # Test list all functionality
        all_models = model_dao.list_all()
        assert len(all_models) == 1
        assert all_models[0].name == "ml_model"
        
        all_inferences = inference_dao.list_all()
        assert len(all_inferences) == 1
        assert all_inferences[0].model_id.name == "ml_model"
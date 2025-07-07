import pytest
from main.dao.model_dao import ModelDAO
from main.dao.inference_dao import InferenceDAO

class TestDatabaseIntegration:
    """Integration tests for basic CRUD operations across the database."""

    def test_model_dao_crud_integration(self, clean_db):
        """Test basic CRUD operations for ModelDAO."""
        dao = ModelDAO()

        # CREATE
        model = dao.create(name="test_model", status="TRAINING")
        assert model.id is not None

        # READ
        retrieved = dao.get_by_id(model.id)
        assert retrieved.name == "test_model"

        # UPDATE
        updated = dao.update(model.id, status="SERVING")
        assert updated.status == "SERVING"

        # DELETE
        assert dao.delete(model.id) is True
        assert dao.get_by_id(model.id) is None

    def test_inference_dao_crud_integration(self, clean_db):
        """Test basic CRUD operations for InferenceDAO."""
        model_dao = ModelDAO()
        inference_dao = InferenceDAO()

        # Create a model first
        model = model_dao.create(name="test_model", status="SERVING")

        # CREATE
        inference = inference_dao.create(status="RUNNING", model_id=model.id)
        assert inference.id is not None

        # READ
        retrieved = inference_dao.get_by_id(inference.id)
        assert retrieved.status == "RUNNING"
        assert retrieved.model_id.id == model.id

        # UPDATE
        updated = inference_dao.update(inference.id, status="COMPLETED")
        assert updated.status == "COMPLETED"

        # DELETE
        assert inference_dao.delete(inference.id) is True
        assert inference_dao.get_by_id(inference.id) is None

    def test_model_inference_relationship(self, clean_db):
        """Test basic relationship between models and inferences."""
        model_dao = ModelDAO()
        inference_dao = InferenceDAO()

        # Create model
        model = model_dao.create(name="ml_model", status="SERVING")

        # Create inference for the model
        inference = inference_dao.create(status="COMPLETED", model_id=model.id)

        # Test relationship queries
        model_inferences = inference_dao.get_by_model_id(model.id)
        assert len(model_inferences) == 1
        assert model_inferences[0].id == inference.id
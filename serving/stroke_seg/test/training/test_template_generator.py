"""Tests for TemplateGenerator class."""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from stroke_seg.exceptions import ModelCreationException
from stroke_seg.bl.training import TemplateGenerator, TrainingTemplateVariables


class TestTemplateGenerator:
    """Test cases for TemplateGenerator class."""
    
    def test_current_template_interpolation(self):
        """Test that the actual sbatch template is interpolated correctly with expected variables."""
        # Create test variables matching the current template requirements
        expected_timestamp = 1757589116
        model_name = 'test_stroke_model'
        expected_fold_index = 1
        expected_task_num = 130

        test_variables = TrainingTemplateVariables(
            model_name=model_name,
            fold_index = expected_fold_index,
            task_number= expected_task_num,
            timestamp=expected_timestamp
        )
        
        # Initialize template generator (will load actual template)
        generator = TemplateGenerator()
        
        # Generate sbatch content
        result = generator.generate_training_sbatch_content(test_variables)
        
        # Define expected sbatch content with interpolated values
        with open('C:\\Users\\Eliad\\Documents\\Final Project\\Final Project\\project\\Final-Project\\serving\\stroke_seg\\test\\resources\\expected_sbatch_train', 'r', encoding='utf-8') as file:
            expected_sbatch_content = file.read()
        
        # Compare actual with expected content
        assert result == expected_sbatch_content, f"Generated content does not match expected.\nExpected:\n{expected_sbatch_content}\n\nActual:\n{result}"
        
        # Verify specific interpolations worked
        assert f"{model_name}-{expected_timestamp}" in result

    
    def test_template_loading_success(self):
        """Test successful template loading."""
        generator = TemplateGenerator()
        
        # Template should be loaded during initialization
        assert generator.template_content is not None
        assert len(generator.template_content) > 0
        assert "#!/bin/bash" in generator.template_content
    
    def test_template_loading_file_not_found(self):
        """Test template loading with non-existent file."""
        non_existent_path = "/non/existent/path/template"
        
        with pytest.raises(FileNotFoundError):
            TemplateGenerator(template_path=non_existent_path)
    
    def test_interpolate_template_with_valid_variables(self):
        """Test template interpolation with valid variables."""
        # Create a simple test template
        test_template_content = "Job: {model_name}, Fold: {fold_index}, Task: {task_number}, Timestamp: {timestamp}"
        
        with patch.object(TemplateGenerator, '_load_template', return_value=test_template_content):
            generator = TemplateGenerator()
            
            variables = TrainingTemplateVariables(
                model_name="test_model",
                fold_index=2,
                task_number=150,
                timestamp=1234567890
            )
            
            result = generator.interpolate_template(variables)
            
            assert result == "Job: test_model, Fold: 2, Task: 150, Timestamp: 1234567890"
    
    def test_interpolate_template_missing_variables(self):
        """Test template interpolation with missing variables in template."""
        # Template requires variables that aren't in the dataclass
        test_template_content = "Job: {model_name}, Fold: {fold_index}, Task: {task_number}, Timestamp: {timestamp}, Extra: {missing_var}"
        
        with patch.object(TemplateGenerator, '_load_template', return_value=test_template_content):
            generator = TemplateGenerator()
            
            variables = TrainingTemplateVariables(
                model_name="test_model",
                fold_index=3,
                task_number=200,
                timestamp=1234567890
            )
            
            with pytest.raises(ModelCreationException) as exc_info:
                generator.interpolate_template(variables)
            
            assert "Missing template variables: ['missing_var']" in str(exc_info.value)
    
    def test_generate_sbatch_content(self):
        """Test complete sbatch content generation workflow."""
        test_template_content = "#!/bin/bash\n#SBATCH --job-name={model_name}-{timestamp}\nsingularity run --env fold_index={fold_index} --env task_number={task_number}\necho 'Training {model_name}'"
        
        with patch.object(TemplateGenerator, '_load_template', return_value=test_template_content):
            generator = TemplateGenerator()
            
            variables = TrainingTemplateVariables(
                model_name="neural_net",
                fold_index=4,
                task_number=250,
                timestamp=9876543210
            )
            
            result = generator.generate_training_sbatch_content(variables)
            
            expected = "#!/bin/bash\n#SBATCH --job-name=neural_net-9876543210\nsingularity run --env fold_index=4 --env task_number=250\necho 'Training neural_net'"
            assert result == expected
    
    def test_custom_template_path(self):
        """Test TemplateGenerator with custom template path."""
        # Create a temporary template file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sbatch', delete=False) as temp_file:
            temp_file.write("Custom template: {model_name}")
            temp_path = temp_file.name
        
        try:
            generator = TemplateGenerator(template_path=temp_path)
            
            variables = TrainingTemplateVariables(
                model_name="custom_model",
                fold_index=5,
                task_number=300,
                timestamp=1111111111
            )
            
            result = generator.interpolate_template(variables)
            assert result == "Custom template: custom_model"
            
        finally:
            # Clean up temporary file
            os.unlink(temp_path)
    
    def test_template_validation_empty_strings(self):
        """Test that SbatchTemplateVariables validates against empty strings and invalid integers."""
        with pytest.raises(ValueError) as exc_info:
            TrainingTemplateVariables(model_name="", fold_index=1, task_number=100, timestamp=1234567890)
        
        assert "model_name must be a non-empty string" in str(exc_info.value)
        
        # Test fold_index validation (0 is considered falsy and should fail)
        with pytest.raises(ValueError) as exc_info:
            TrainingTemplateVariables(model_name="valid_name", fold_index=0, task_number=100, timestamp=1234567890)
        
        assert "fold_index must be a non-empty string" in str(exc_info.value)
        
        # Test task_number validation (0 is considered falsy and should fail)
        with pytest.raises(ValueError) as exc_info:
            TrainingTemplateVariables(model_name="valid_name", fold_index=1, task_number=0, timestamp=1234567890)
        
        assert "task_number must be a non-empty string" in str(exc_info.value)
    
    def test_template_variables_to_dict(self):
        """Test SbatchTemplateVariables to_dict method."""
        variables = TrainingTemplateVariables(
            model_name="test_model",
            fold_index=6,
            task_number=400,
            timestamp=1234567890
        )
        
        result = variables.to_dict()
        
        expected = {
            'model_name': 'test_model',
            'timestamp': 1234567890,
            'fold_index': 6,
            'task_number': 400
        }
        
        assert result == expected
    
    def test_default_template_path_resolution(self):
        """Test that default template path is resolved correctly."""
        generator = TemplateGenerator()
        
        expected_path = Path(__file__).parent.parent / "templates" / "sbatch_train_template"
        
        # Check that the template loaded successfully (meaning path was correct)
        assert generator.template_content is not None
        assert len(generator.template_content) > 0
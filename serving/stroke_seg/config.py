import os
from pathlib import Path

models_base_path = '/home/veeliad/work/BrainSegmentation/models'

# Template paths configuration
_template_dir = Path(__file__).parent / "templates"
training_template_path = str(_template_dir / "sbatch_train_template")
inference_template_path = str(_template_dir / "sbatch_inference_template")

def validate_template_files():
    """
    Validate that all required template files exist.

    Raises:
        FileNotFoundError: If any template file is missing
    """
    templates = {
        "Training template": training_template_path,
        "Inference template": inference_template_path
    }

    missing_templates = []
    for name, path in templates.items():
        if not os.path.isfile(path):
            missing_templates.append(f"{name}: {path}")

    if missing_templates:
        raise FileNotFoundError(f"Missing template files:\n" + "\n".join(missing_templates))
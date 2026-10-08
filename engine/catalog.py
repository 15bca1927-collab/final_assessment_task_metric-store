import os
import yaml
from typing import Dict, Any, List

class MetricCatalog:
    def __init__(self, semantic_dir: str = "models/semantic"):
        self.semantic_dir = semantic_dir
        self.models: Dict[str, Dict[str, Any]] = {}
        self.metrics_index: Dict[str, str] = {}  # metric_name -> model_name
        self._load_catalog()

    def _load_catalog(self):
        for fname in os.listdir(self.semantic_dir):
            if fname.endswith(".yml") or fname.endswith(".yaml"):
                fpath = os.path.join(self.semantic_dir, fname)
                with open(fpath, "r") as f:
                    content = yaml.safe_load(f)
                    model_data = content.get("model")
                    if model_data:
                        model_name = model_data["name"]
                        self.models[model_name] = model_data
                        for metric in model_data.get("metrics", []):
                            self.metrics_index[metric["name"]] = model_name

    def get_model_for_metric(self, metric_name: str) -> Dict[str, Any]:
        model_name = self.metrics_index.get(metric_name)
        if not model_name:
            raise ValueError(f"Metric '{metric_name}' not defined in semantic catalog.")
        return self.models[model_name]

    def list_available_metrics(self) -> List[Dict[str, str]]:
        result = []
        for model in self.models.values():
            for m in model.get("metrics", []):
                result.append({
                    "name": m["name"],
                    "model": model["name"],
                    "description": m.get("description", ""),
                    "format": m.get("format", "number")
                })
        return result

# SPDX-License-Identifier: Apache-2.0
from copy import deepcopy
from pathlib import Path

import yaml


SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
DEFAULT_CONFIG_PATH = PROJECT_ROOT / "config.yaml"

_CONFIG_PATH_KEYS = {
    "sasb_metrics",
    "sasb_database",
    "sasb_index",
    "ocr_output",
    "chandra_ocr_output",
    "esg_reports_pdf",
    "results_output",
    "marked_results_output",
    "train_labels",
}


def resolve_path(path_value, base_dir=PROJECT_ROOT):
    path = Path(path_value)
    if path.is_absolute():
        return path
    return (base_dir / path).resolve()


def load_config(config_path=DEFAULT_CONFIG_PATH):
    config_path = Path(config_path)
    with config_path.open("r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    config = deepcopy(config)
    paths = config.get("paths", {})
    for key in _CONFIG_PATH_KEYS:
        value = paths.get(key)
        if isinstance(value, str):
            paths[key] = str(resolve_path(value, PROJECT_ROOT))
    config["paths"] = paths
    return config

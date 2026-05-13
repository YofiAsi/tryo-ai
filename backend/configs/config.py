"""
CV Processing System Configuration Module

This module provides configuration management for the CV processing system,
allowing easy switching between test and production environments.
"""

import os
import json
from enum import Enum
from typing import Dict, Any, List, Optional
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Environment(Enum):
    TEST = "test"
    PRODUCTION = "production"

class Config:
    """Configuration manager for the CV processing system."""
    
    # Default configurations
    DEFAULT_CONFIG = {
        "test": {
            "api": {
                "provider": "openai",
                "max_rpm": 10,
                "batch_size": 2,
                "max_workers": 5
            },
            "storage": {
                "document_db": {
                    "connection_string": "mongodb://localhost:27017/",
                    "db_name": "cv_database_test",
                    "collection_name": "processed_cvs_test"
                },
                "vector_db": {
                    "index_name": "cv-embeddings-test",
                    "environment": "us-west1-gcp"
                }
            },
            "job_repository": {
                "db_name": "cv_database_test",
                "collection_name": "job_positions_test"
            },
            "sample_data": {
                "cv_dir": "samples/cvs",
                "job_dir": "samples/jobs"
            }
        },
        "production": {
            "api": {
                "provider": "openai",
                "max_rpm": 50,
                "batch_size": 3,
                "max_workers": 20
            },
            "storage": {
                "document_db": {
                    "connection_string": None,  # Will be loaded from env
                    "db_name": "cv_database",
                    "collection_name": "processed_cvs"
                },
                "vector_db": {
                    "index_name": "cv-embeddings",
                    "environment": "us-west1-gcp"
                }
            },
            "job_repository": {
                "db_name": "cv_database",
                "collection_name": "job_positions"
            }
        }
    }
    
    def __init__(self, env: Environment = None):
        """Initialize configuration with specified environment."""
        self.config_file = Path(os.environ.get('CONFIG_PATH', 'config.json'))
        self.env = env or Environment(os.environ.get('CV_ENVIRONMENT', 'test'))
        self.config = self._load_config()
        logger.info(f"Initialized configuration for {self.env.value} environment")
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or use defaults."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    logger.info(f"Loaded configuration from {self.config_file}")
                    return config
            except Exception as e:
                logger.warning(f"Failed to load config from {self.config_file}: {e}")
                logger.info("Using default configuration")
                return self.DEFAULT_CONFIG
        else:
            logger.info(f"Config file {self.config_file} not found. Using default configuration")
            return self.DEFAULT_CONFIG
    
    def save_config(self) -> None:
        """Save current configuration to file."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=4)
            logger.info(f"Saved configuration to {self.config_file}")
        except Exception as e:
            logger.error(f"Failed to save config to {self.config_file}: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value for current environment."""
        env_config = self.config.get(self.env.value, {})
        
        # Handle nested keys
        if '.' in key:
            parts = key.split('.')
            value = env_config
            for part in parts:
                if isinstance(value, dict):
                    value = value.get(part, None)
                else:
                    return default
            return value if value is not None else default
        
        return env_config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value for current environment."""
        if self.env.value not in self.config:
            self.config[self.env.value] = {}
        
        # Handle nested keys
        if '.' in key:
            parts = key.split('.')
            config_dict = self.config[self.env.value]
            for part in parts[:-1]:
                if part not in config_dict or not isinstance(config_dict[part], dict):
                    config_dict[part] = {}
                config_dict = config_dict[part]
            config_dict[parts[-1]] = value
        else:
            self.config[self.env.value][key] = value
    
    def switch_environment(self, env: Environment) -> None:
        """Switch to a different environment."""
        self.env = env
        logger.info(f"Switched to {self.env.value} environment")
    
    def get_api_config(self) -> Dict[str, Any]:
        """Get API configuration for current environment."""
        return self.get('api', {})
    
    def get_storage_config(self) -> Dict[str, Any]:
        """Get storage configuration for current environment."""
        return self.get('storage', {})
    
    def get_job_repository_config(self) -> Dict[str, Any]:
        """Get job repository configuration for current environment."""
        return self.get('job_repository', {})
    
    def get_sample_data_paths(self) -> Dict[str, str]:
        """Get sample data paths for testing."""
        return self.get('sample_data', {})

# Global configuration instance
config = Config()

def get_config() -> Config:
    """Get the global configuration instance."""
    return config

def set_environment(env: str) -> None:
    """Set the current environment."""
    config.switch_environment(Environment(env)) 
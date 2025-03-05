import os
import json
from pathlib import Path
from typing import Optional

class Config:
    """Configuration manager for EODHD Options API."""
    
    def __init__(self):
        """Initialize the configuration manager."""
        self.config_dir = self._get_config_dir()
        self.config_file = self.config_dir / 'config.json'
        self._ensure_config_dir()
    
    def _get_config_dir(self) -> Path:
        """Get the configuration directory path."""
        # Use platform-specific config directory
        if os.name == 'nt':  # Windows
            base_dir = os.getenv('APPDATA')
            if not base_dir:
                base_dir = os.path.expanduser('~')
            return Path(base_dir) / 'eodhd_options'
        else:  # Unix-like
            return Path(os.path.expanduser('~')) / '.config' / 'eodhd_options'
    
    def _ensure_config_dir(self):
        """Ensure the configuration directory exists."""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Set appropriate permissions on Unix-like systems
        if os.name != 'nt':
            os.chmod(self.config_dir, 0o700)
    
    def save_api_key(self, api_key: str):
        """
        Save the API key to the configuration file.
        
        Args:
            api_key (str): The API key to save
        """
        config = self._read_config()
        config['api_key'] = api_key
        
        # Write with restricted permissions
        with open(self.config_file, 'w') as f:
            json.dump(config, f)
        
        # Set appropriate permissions on Unix-like systems
        if os.name != 'nt':
            os.chmod(self.config_file, 0o600)
    
    def get_api_key(self) -> Optional[str]:
        """
        Get the stored API key.
        
        Returns:
            Optional[str]: The stored API key, or None if not found
        """
        config = self._read_config()
        return config.get('api_key')
    
    def _read_config(self) -> dict:
        """Read the configuration file."""
        if not self.config_file.exists():
            return {}
        
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {} 
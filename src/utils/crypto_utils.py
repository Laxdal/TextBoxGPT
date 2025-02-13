from cryptography.fernet import Fernet
from typing import Dict, Any, Optional
import json
import os
import sys

class ConfigDecryptor:
    """A utility class for decrypting configuration files.
    
    This class provides methods to decrypt JSON configuration files
    using Fernet symmetric encryption with external key file support.
    """
    
    def __init__(self, key_file: str = "gpt.key", config_file: str = "gpt_config.bin") -> None:
        """Initialize the ConfigDecryptor.
        
        Args:
            key_file: Path to the encryption key file. Defaults to "gpt.key".
            config_file: Path to the encrypted configuration file. Defaults to "gpt_config.bin".
        """
        self.key_file = self._get_executable_dir(key_file)
        self.config_file = self._get_executable_dir(config_file)
    
    def _get_executable_dir(self, filename: str) -> str:
        """Get path in the same directory as the executable.
        
        Args:
            filename: The name of the file.
            
        Returns:
            str: The absolute path to the file in the executable's directory.
        """
        if getattr(sys, 'frozen', False):
            # Running in PyInstaller bundle
            base_path = os.path.dirname(sys.executable)
        else:
            # Running in normal Python environment
            base_path = os.path.abspath(os.path.dirname(__file__))
            # Go up two levels to reach the project root
            base_path = os.path.dirname(os.path.dirname(base_path))
            
        return os.path.join(base_path, filename)
    
    def _load_key(self) -> Optional[bytes]:
        """Load the encryption key from file.
        
        Returns:
            Optional[bytes]: The encryption key if found, None otherwise.
        """
        try:
            with open(self.key_file, 'rb') as f:
                return f.read()
        except FileNotFoundError:
            return None
    
    def decrypt_config(self) -> Optional[Dict[str, Any]]:
        """Decrypt configuration from file.
        
        Returns:
            Optional[Dict[str, Any]]: Decrypted configuration data if successful, None if key not found.
        """
        key = self._load_key()
        if key is None:
            print("No encryption key found. Please place the correct 'gpt.key' file in the program directory.")
            return None
            
        try:
            fernet = Fernet(key)
            
            with open(self.config_file, 'rb') as f:
                encrypted_data = f.read()
                
            # Decrypt the data
            decrypted_data = fernet.decrypt(encrypted_data)
            
            # Parse JSON and return
            return json.loads(decrypted_data)
        except FileNotFoundError:
            print("Configuration file not found. Please ensure 'gpt_config.bin' exists.")
            return None
        except Exception as e:
            print(f"Error decrypting configuration: {e}")
            print("The key file might be incorrect. Please ensure you have the correct key file.")
            return None 
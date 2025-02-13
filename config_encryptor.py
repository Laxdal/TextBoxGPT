from cryptography.fernet import Fernet
import json
import os
import sys
from typing import Dict, Any

class ConfigEncryptor:
    """A standalone utility for encrypting configuration files."""
    
    def __init__(self) -> None:
        """Initialize the ConfigEncryptor."""
        self.key_file = "gpt.key"
        self.config_file = "gpt_config.bin"
    
    def generate_key(self) -> bytes:
        """Generate a new encryption key.
        
        Returns:
            bytes: The generated encryption key.
        """
        return Fernet.generate_key()
    
    def encrypt_config(self, config_data: Dict[str, Any], key: bytes) -> bytes:
        """Encrypt configuration data.
        
        Args:
            config_data: Dictionary containing configuration data.
            key: Encryption key.
            
        Returns:
            bytes: Encrypted configuration data.
        """
        fernet = Fernet(key)
        json_data = json.dumps(config_data).encode()
        return fernet.encrypt(json_data)

def main() -> None:
    """Main function to run the encryption process."""
    try:
        # Check if api.json exists in the current directory
        if not os.path.exists("api.json"):
            print("Error: api.json not found in the current directory")
            print("\nPlease create an api.json file with the following format:")
            print('''{
    "api_key": "your-api-key-here",
    "api_url": "your-api-url-here",
    "model_name": "your-model-name"
}''')
            sys.exit(1)
        
        # Read the configuration
        with open("api.json", 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        
        # Validate required fields
        if not all(key in config_data for key in ['api_key', 'api_url']):
            print("Error: Configuration must contain 'api_key' and 'api_url'")
            sys.exit(1)
        
        # Create encryptor and generate key
        encryptor = ConfigEncryptor()
        key = encryptor.generate_key()
        
        # Encrypt the configuration
        encrypted_data = encryptor.encrypt_config(config_data, key)
        
        # Save the key
        with open(encryptor.key_file, 'wb') as f:
            f.write(key)
        
        # Save the encrypted configuration
        with open(encryptor.config_file, 'wb') as f:
            f.write(encrypted_data)
        
        print("\nConfiguration encrypted successfully!")
        print(f"Key file saved as: {encryptor.key_file}")
        print(f"Encrypted configuration saved as: {encryptor.config_file}")
        print("\nTo use these files:")
        print("1. Copy both files to the same directory as TextBoxGPT.exe")
        print("2. Run TextBoxGPT.exe to use the configuration")
        print("\nTo update configuration:")
        print("1. Create a new api.json with the new settings")
        print("2. Run this program again to generate new key and config files")
        
    except json.JSONDecodeError:
        print("Error: api.json is not a valid JSON file")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 
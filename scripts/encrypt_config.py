import sys
import os
import json
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.utils.crypto_utils import CryptoManager

def encrypt_config_file(input_file: str = "api.json") -> None:
    """Encrypt the configuration file.
    
    Args:
        input_file: Path to the input JSON configuration file.
    """
    try:
        # Read the original config
        with open(input_file, 'r') as f:
            config_data = json.load(f)
        
        # Validate required fields
        if not all(key in config_data for key in ['api_key', 'api_url']):
            print("Error: Configuration must contain 'api_key' and 'api_url'")
            sys.exit(1)
        
        # Create crypto manager and encrypt
        crypto_manager = CryptoManager()
        crypto_manager.encrypt_config(config_data)
        
        print("Configuration encrypted successfully!")
        print("The encryption key has been saved as 'vretta.key'")
        print("The encrypted configuration has been saved as 'vretta_config.bin'")
        print("\nTo use different API credentials:")
        print("1. Delete the existing 'vretta.key' file")
        print("2. Create a new api.json with the new credentials")
        print("3. Run this script again to generate a new key and encrypted config")
        
    except FileNotFoundError:
        print(f"Error: {input_file} not found")
        print("\nPlease create an api.json file with the following format:")
        print('''{
    "api_key": "your-api-key-here",
    "api_url": "your-api-url-here",
    "model_name": "gpt-4o"
}''')
        sys.exit(1)
    except Exception as e:
        print(f"Error encrypting configuration: {e}")
        sys.exit(1)

if __name__ == "__main__":
    encrypt_config_file() 
# TextBoxGPT

A Windows application that integrates with ChatGPT API to provide quick text generation and typing automation.

## Features

- Secure API key and configuration management with encryption
- Clipboard monitoring for automatic prompt processing
- Automated text typing with case preservation
- Global hotkeys for quick access
- Detailed logging system

## Requirements

- Windows 10/11
- Python 3.8+
- Required DLL: buke_km64.dll (not included)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Laxdal/TextBoxGPT.git
cd TextBoxGPT
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create configuration file:
Create a file named `api.json` with your API credentials:
```json
{
    "api_key": "your-api-key-here",
    "api_url": "your-api-url-here",
    "model_name": "your-model-name"
}
```

4. Encrypt configuration:
```bash
python config_encryptor.py
```

## Usage

1. Run the program:
```bash
python product.py
```

2. Available hotkeys:
- `Ctrl+D`: Send clipboard content to ChatGPT
- `Ctrl+T`: Type text from output.txt
- `Alt+Q`: Exit program
- Prefix clipboard text with "GPT" for automatic processing

## Building

To create standalone executables:

1. Build main program:
```bash
pyinstaller textbox_gpt.spec
```

2. Build configuration encryptor:
```bash
pyinstaller config_encryptor.spec
```

## Security

- API credentials are stored in encrypted format
- Encryption key is stored separately from encrypted configuration
- Configuration can be easily updated using the encryptor tool

## License

[MIT License](LICENSE)

## Note

The `buke_km64.dll` file is required for keyboard simulation but is not included in this repository. Please obtain it separately. 
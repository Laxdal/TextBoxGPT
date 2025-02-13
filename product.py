from openai import OpenAI
import win32clipboard
import win32con
import keyboard
import time
from ctypes import *
import threading
from typing import Optional
from src.utils.crypto_utils import ConfigDecryptor
import sys
import logging
from datetime import datetime

# Add custom logging levels
USER = 25  # Between INFO and WARNING
GPT = 26
SYSTEM = 27

# Add custom level names
logging.addLevelName(USER, 'USER')
logging.addLevelName(GPT, 'GPT')
logging.addLevelName(SYSTEM, 'SYSTEM')

# Add custom logging methods
def user_log(self, message, *args, **kwargs):
    self.log(USER, message, *args, **kwargs)

def gpt_log(self, message, *args, **kwargs):
    self.log(GPT, message, *args, **kwargs)

def system_log(self, message, *args, **kwargs):
    self.log(SYSTEM, message, *args, **kwargs)

# Add methods to Logger class
logging.Logger.user = user_log
logging.Logger.gpt = gpt_log
logging.Logger.system = system_log

# Create a global logger
logger = logging.getLogger('TextBoxGPT')

def setup_logging() -> None:
    """Setup logging configuration.
    
    Creates a log file with the current date as the filename and configures
    logging to write both to the file and console.
    """
    # Create log filename with current date
    log_filename = f"{datetime.now().strftime('%Y-%m-%d')}.log"
    
    # Configure logging format
    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
    
    # File handler
    file_handler = logging.FileHandler(log_filename, encoding='utf-8')
    file_handler.setFormatter(formatter)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # Configure logger
    logger.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    logger.system("=== TextBoxGPT Started ===")

def load_config() -> Optional[dict]:
    """Load and decrypt configuration from encrypted file.
    
    Returns:
        Optional[dict]: Decrypted configuration data if successful, None otherwise.
    """
    decryptor = ConfigDecryptor()
    config = decryptor.decrypt_config()
    
    if config is None:
        logger.error("Failed to load configuration. Please ensure the correct key file is present.")
        sys.exit(1)
        
    return config

# Setup logging first
setup_logging()

# Load configuration
config = load_config()

# OpenAI API Configuration
API_KEY = config.get("api_key")
API_URL = config.get("api_url")
MODEL_NAME = config.get("model_name", "gpt-4o")

if not all([API_KEY, API_URL]):
    logger.error("Missing required configuration. Please ensure api_key and api_url are set.")
    sys.exit(1)

# Display configuration information
logger.system("=== Configuration Information ===")
logger.system(f"API URL: {API_URL}")
logger.system(f"Model: {MODEL_NAME}")
logger.system("===============================")

# Load the DLL
try:
    buke_km = CDLL('buke_km64.dll', winmode=0)
    logger.system("DLL loaded successfully")
except Exception as e:
    logger.error(f"Failed to load DLL: {e}")
    print(f"Error: Could not load buke_km64.dll: {e}")
    sys.exit(1)

# Initialize the DLL
def initialize_dll() -> bool:
    """Initialize the keyboard DLL.
    
    Returns:
        bool: True if initialization successful, False otherwise.
    """
    try:
        res = buke_km.Init(0, 0)
        if res == False:
            logger.error("DLL initialization returned False")
            print("Error: Failed to initialize keyboard DLL. Please ensure you have the correct permissions.")
            return False
            
        logger.system("DLL initialized successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error during DLL initialization: {e}")
        print(f"Error: Failed to initialize DLL: {e}")
        return False

# 获取剪切板文本的函数
def get_clipboard_text() -> str:
    """Get text from clipboard.
    
    Returns:
        str: Text from clipboard, empty string if error occurs.
    """
    try:
        # 打开剪切板
        win32clipboard.OpenClipboard(0)

        # 尝试获取文本
        try:
            text = win32clipboard.GetClipboardData(win32con.CF_UNICODETEXT)
        except:
            text = ""

        # 关闭剪切板
        win32clipboard.CloseClipboard()

        return text.strip() if text else ""
    except Exception as e:
        logger.error(f"Error getting clipboard content: {e}")
        return ""

def type_text_from_file() -> bool:
    """Type text from output.txt file using the keyboard DLL.
    
    Returns:
        bool: True if typing successful, False otherwise.
    """
    try:
        # Read text from output.txt
        with open('output.txt', 'r', encoding='utf-8') as file:
            text_to_type = file.read().strip()

        # Replace newlines with three spaces
        text_to_type = text_to_type.replace('\n', '   ')

        if not text_to_type:
            logger.warning("No text to type")
            return False

        # Wait a moment to switch to the target input area
        logger.system("Preparing to type. Switch to target input area...")
        time.sleep(1)

        # Type text character by character to handle case
        for char in text_to_type:
            if char.isupper():
                # VK code for Shift key is 16
                buke_km.KeyboardDown(16)  # Press Shift
                buke_km.InputString(char.lower())
                buke_km.KeyboardUp(16)  # Release Shift
            else:
                buke_km.InputString(char)

        logger.system("Typing complete")
        return True

    except FileNotFoundError:
        logger.error("output.txt not found")
        return False
    except Exception as e:
        logger.error(f"Error reading or typing file: {e}")
        return False

def send_prompt_to_chatgpt(prompt: str) -> bool:
    """Send prompt to ChatGPT and save response to file.
    
    Args:
        prompt: The prompt to send to ChatGPT.
        
    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        # Log the full prompt
        logger.user(prompt)
        
        client = OpenAI(
            api_key=API_KEY,
            base_url=API_URL
        )

        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        )

        # Get the response content
        response_text = response.choices[0].message.content.strip()

        # Log the full response
        logger.gpt(response_text)
        logger.system("-" * 50)  # Add a separator line between conversations

        # Write to output.txt
        with open('output.txt', 'w', encoding='utf-8') as file:
            file.write(response_text)

        logger.info("Response saved to output.txt")
        return True

    except Exception as e:
        logger.error(f"Error in ChatGPT interaction: {e}")
        return False

def send_clipboard_prompt() -> None:
    """Send clipboard content to ChatGPT and type the response."""
    # 使用新的剪切板获取方法
    prompt = get_clipboard_text()

    if not prompt:
        logger.warning("Clipboard is empty")
        return

    # Send prompt to ChatGPT and save to file
    if send_prompt_to_chatgpt(prompt):
        # Type out the response
        type_text_from_file()

def exit_program() -> None:
    """Exit the program."""
    logger.system("Exiting script")
    exit()

def monitor_clipboard() -> None:
    """Monitor clipboard for text starting with 'GPT' and process it."""
    logger.system("Clipboard monitoring started")
    last_clipboard_content = ""
    while True:
        try:
            current_clipboard_content = get_clipboard_text()

            # 检查剪切板内容是否变化且以"GPT"开头
            if current_clipboard_content != last_clipboard_content and current_clipboard_content.startswith("GPT"):
                logger.info("GPT-prefixed content detected in clipboard")
                # 去掉"GPT"前缀
                prompt = current_clipboard_content[3:].strip()

                # 发送prompt到ChatGPT
                if send_prompt_to_chatgpt(prompt):
                    # 打字输出响应
                    type_text_from_file()

                last_clipboard_content = current_clipboard_content

            time.sleep(0.5)  # 每0.5秒检查一次剪切板
        except Exception as e:
            logger.error(f"Clipboard monitoring error: {e}")
            time.sleep(1)

def main() -> None:
    """Main function to run the program."""
    # Initialize DLL
    if not initialize_dll():
        return

    # 启动剪切板监控线程
    clipboard_thread = threading.Thread(target=monitor_clipboard, daemon=True)
    clipboard_thread.start()

    # Register global hotkey for Ctrl+D to send clipboard content
    keyboard.add_hotkey('ctrl+d', send_clipboard_prompt)
    logger.system("Registered hotkey: Ctrl+D for sending clipboard content")

    # Register global hotkey for Ctrl+T to type text from file
    keyboard.add_hotkey('ctrl+t', type_text_from_file)
    logger.system("Registered hotkey: Ctrl+T for typing text from file")

    # Register global hotkey for Alt+Q to exit the program
    keyboard.add_hotkey('alt+q', exit_program)
    logger.system("Registered hotkey: Alt+Q for exiting")

    print("Script is running:")
    print("- Press Ctrl+D to send clipboard content to ChatGPT")
    print("- Press Ctrl+T to type text from output.txt")
    print("- Press Alt+Q to exit")
    print("- Prefix clipboard text with 'GPT' for automatic processing")
    print("- Ctrl+C is now free for copying")

    try:
        # Keep the script running
        keyboard.wait()
    except Exception as e:
        logger.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()


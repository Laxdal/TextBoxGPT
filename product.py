from openai import OpenAI
import win32clipboard
import win32con
import keyboard
import time
from ctypes import *
import threading

# OpenAI API Configuration
API_KEY = "sk-65794a68624763694f694a49557a49314e694a392e65794a755957316c496a6f69544746345a474673587a51354d7a6c664e446b7a4f534973496d6c68644349364d54637a4e6a51334e6a41314d6977695a586877496a6f784e7a4d334e6a67314e6a557966512e4b7869325a56563836343543757934636f626e393961727163625356456a6b7a656e35366b415347525359"
API_URL = "https://api.4chat.me/v1/"
MODEL_NAME = "claude-3.5-sonnet-20241022"

# Load the DLL
buke_km = CDLL('buke_km64.dll', winmode=0)

# 获取剪切板文本的函数
def get_clipboard_text():
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
        print(f"获取剪切板内容时出错: {e}")
        return ""

# Initialize the DLL
def initialize_dll():
    res = buke_km.Init(0, 0)
    if res == False:
        print("Failed to initialize DLL")
        return False
    return True

def type_text_from_file():
    try:
        # Read text from example.txt
        with open('example.txt', 'r', encoding='utf-8') as file:
            text_to_type = file.read().strip()

        if not text_to_type:
            print("No text to type")
            return False

        # Wait a moment to switch to the target input area
        print("Preparing to type. Switch to target input area...")
        time.sleep(1)

        # Type out the text
        buke_km.InputString(text_to_type.encode('utf-8'))

        print("Typing complete")
        return True

    except FileNotFoundError:
        print("example.txt not found")
        return False
    except Exception as e:
        print(f"Error reading or typing file: {e}")
        return False

def send_prompt_to_chatgpt(prompt):
    try:
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

        # Print to console
        print("ChatGPT: ", response_text)

        # Write to example.txt
        with open('example.txt', 'w', encoding='utf-8') as file:
            file.write(response_text)

        print("Response saved to example.txt")

        return True

    except Exception as e:
        print(f"Error in ChatGPT interaction: {e}")
        return False

def send_clipboard_prompt():
    # 使用新的剪切板获取方法
    prompt = get_clipboard_text()

    if not prompt:
        print("Clipboard is empty.")
        return

    # Send prompt to ChatGPT and save to file
    if send_prompt_to_chatgpt(prompt):
        # Type out the response
        type_text_from_file()

def exit_program():
    print("\nExiting script.")
    exit()

def monitor_clipboard():
    last_clipboard_content = ""
    while True:
        try:
            current_clipboard_content = get_clipboard_text()

            # 检查剪切板内容是否变化且以"GPT"开头
            if current_clipboard_content != last_clipboard_content and current_clipboard_content.startswith("GPT"):
                # 去掉"GPT"前缀
                prompt = current_clipboard_content[3:].strip()

                # 发送prompt到ChatGPT
                if send_prompt_to_chatgpt(prompt):
                    # 打字输出响应
                    type_text_from_file()

                last_clipboard_content = current_clipboard_content

            time.sleep(0.5)  # 每0.5秒检查一次剪切板
        except Exception as e:
            print(f"Clipboard monitoring error: {e}")
            time.sleep(1)

def main():
    # Initialize DLL
    if not initialize_dll():
        return

    # 启动剪切板监控线程
    clipboard_thread = threading.Thread(target=monitor_clipboard, daemon=True)
    clipboard_thread.start()

    # Register global hotkey for Ctrl+D to send clipboard content
    keyboard.add_hotkey('ctrl+d', send_clipboard_prompt)

    # Register global hotkey for Ctrl+T to type text from file
    keyboard.add_hotkey('ctrl+t', type_text_from_file)

    # Register global hotkey for Alt+Q to exit the program
    keyboard.add_hotkey('alt+q', exit_program)

    print("Script is running:")
    print("- Press Ctrl+D to send clipboard content to ChatGPT")
    print("- Press Ctrl+T to type text from example.txt")
    print("- Press Alt+Q to exit")
    print("- Prefix clipboard text with 'GPT' for automatic processing")
    print("- Ctrl+C is now free for copying")

    try:
        # Keep the script running
        keyboard.wait()
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()


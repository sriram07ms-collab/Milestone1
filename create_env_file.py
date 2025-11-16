"""Create .env file for API key configuration"""
import os

env_content = """# Gemini AI Configuration
# Get your API key from: https://makersuite.google.com/app/apikey
GEMINI_API_KEY=your_api_key_here

# Gemini Model (default: gemini-2.0-flash-exp)
GEMINI_MODEL=gemini-2.0-flash-exp

# Database Configuration
DATABASE_URL=sqlite:///./icici_funds.db

# Logging Level (INFO, DEBUG, WARNING, ERROR)
LOG_LEVEL=INFO
"""

def create_env_file():
    """Create .env file if it doesn't exist"""
    env_path = ".env"
    
    if os.path.exists(env_path):
        print(f"[OK] .env file already exists at: {os.path.abspath(env_path)}")
        print("\nCurrent contents:")
        print("-" * 60)
        with open(env_path, 'r') as f:
            print(f.read())
        print("-" * 60)
        print("\nTo update your API key, edit the .env file and replace 'your_api_key_here' with your actual API key.")
    else:
        with open(env_path, 'w') as f:
            f.write(env_content)
        print(f"[OK] .env file created successfully at: {os.path.abspath(env_path)}")
        print("\nFile contents:")
        print("-" * 60)
        print(env_content)
        print("-" * 60)
        print("\nNEXT STEPS:")
        print("1. Open the .env file")
        print("2. Replace 'your_api_key_here' with your actual Gemini API key")
        print("3. Get your API key from: https://makersuite.google.com/app/apikey")
        print("4. Save the file")

if __name__ == "__main__":
    create_env_file()


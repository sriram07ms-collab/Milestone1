# How to Add Your Gemini API Key

## Step 1: Get Your API Key

1. Visit: https://makersuite.google.com/app/apikey
2. Sign in with your Google account
3. Click "Create API Key" or "Get API Key"
4. Copy your API key

## Step 2: Add to .env File

1. Open the `.env` file in the project root directory
2. Find the line: `GEMINI_API_KEY=your_api_key_here`
3. Replace `your_api_key_here` with your actual API key
4. Save the file

### Example:
```env
GEMINI_API_KEY=AIzaSyAbCdEfGhIjKlMnOpQrStUvWxYz1234567
```

## Step 3: Verify

After adding your API key, test the system:

```bash
python quick_test.py
```

Or start the server:

```bash
python run_server.py
```

## Important Notes

- ⚠️ **Never commit the `.env` file to version control** (it's already in `.gitignore`)
- ✅ The `.env` file is in the project root directory
- ✅ The system will automatically load the API key when you run the application
- ✅ If the API key is missing, the LLM features won't work, but the RAG system will still function

## Troubleshooting

### API Key Not Working?
- Make sure there are no extra spaces around the `=` sign
- Make sure the API key is on a single line
- Verify the API key is valid at https://makersuite.google.com/app/apikey

### File Not Found?
- Make sure the `.env` file is in the project root (same directory as `run_server.py`)
- Check that the file is named exactly `.env` (not `.env.txt`)


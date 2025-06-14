# HelpBot - AI Error Assistant

A clean, simple AI error assistant that integrates with Confluence to provide specific error documentation and resolution steps.

## Features

- 🔍 **Simple Error Analysis**: Just paste your error and get 3 clear sections: Issue, Explanation, Resolution
- 🔗 **Confluence Integration**: Connects directly to your Confluence space for documentation
- 🧪 **Built-in Testing**: Test your Confluence connection with one click
- 🎨 **Modern UI**: Clean, responsive interface with real-time status updates
- ⚡ **Fast & Lightweight**: Minimal dependencies, focused functionality

## Quick Start

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Confluence

Copy the example config and update with your details:

```bash
cp config.env.example config.env
```

Edit `config.env` with your Confluence details:

```env
CONFLUENCE_URL=https://your-domain.atlassian.net/wiki
CONFLUENCE_USERNAME=your-email@domain.com
CONFLUENCE_API_TOKEN=your-api-token
CONFLUENCE_SPACE_KEY=DOCS
```

### 3. Run the Application

```bash
python app.py
```

The application will be available at `http://localhost:8000`

## Configuration

### Environment Variables

- `CONFLUENCE_URL`: Your Confluence base URL
- `CONFLUENCE_USERNAME`: Your Confluence username/email
- `CONFLUENCE_API_TOKEN`: Your Confluence API token
- `CONFLUENCE_SPACE_KEY`: The space key containing your error documentation

### Getting Confluence API Token

1. Go to https://id.atlassian.com/manage-profile/security/api-tokens
2. Click "Create API token"
3. Give it a name and copy the token
4. Use your email as username and the token as password

## Usage

1. **Test Connection**: Click "Test Connection" to verify your Confluence setup
2. **Enter Error**: Paste your error message or describe the issue
3. **Get Results**: View the 3-part response:
   - **Your Issue**: What you submitted
   - **Explanation**: What the error means
   - **Resolution Steps**: How to fix it

## Project Structure

```
backend/
├── app.py                 # Main FastAPI application
├── requirements.txt       # Python dependencies
├── config.env.example    # Configuration template
├── helpbot/              # Core modules
│   ├── __init__.py
│   ├── confluence_client.py  # Confluence API client
│   └── html_extractor.py     # HTML content parser
├── templates/
│   └── index.html        # Web interface
└── scripts/
    └── index_confluence.py  # Indexing utility
```

## API Endpoints

- `GET /` - Web interface
- `GET /test-connection` - Test Confluence connection
- `POST /query` - Analyze error (JSON: `{"query": "error description"}`)
- `GET /health` - Health check

## Troubleshooting

### Connection Issues

1. Verify your Confluence URL format: `https://domain.atlassian.net/wiki`
2. Check your API token is valid and not expired
3. Ensure your user has access to the specified space
4. Test with the "Test Connection" button

### No Results Found

1. Check if your space contains error documentation
2. Try different search terms
3. Verify the space key is correct
4. Use the indexing script to check content structure

### Performance

- The system caches search results for better performance
- Large Confluence spaces may take longer to search
- Consider creating a dedicated error documentation space

## Development

### Adding New Features

The system is modular:

- `confluence_client.py`: Handles all Confluence API interactions
- `html_extractor.py`: Parses and extracts error information
- `app.py`: Main application logic and API endpoints

### Testing

```bash
# Test connection
curl http://localhost:8000/test-connection

# Test query
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "database connection error"}'
```

## License

MIT License - feel free to use and modify as needed.
# Help-Bot

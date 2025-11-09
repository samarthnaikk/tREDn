# tREDn - Reddit Topic Research and Data Navigator

**tREDn** is a web-based application that searches Reddit based on user prompts/topics, fetches relevant posts and their comments, saves the data in JSON format, and provides CSV export functionality. The application retrieves Reddit content specifically matching your search queries. Built with Flask for easy web access and data analysis.

## Features

- Web-based interface for searching Reddit content using custom prompts/topics
- Real-time data fetching from Reddit's public API based on user queries
- JSON data storage for search results
- CSV export functionality for data analysis
- File management system for saved searches
- Clean, responsive web interface
- No API keys required - uses Reddit's public endpoints

## Installation

### Prerequisites

- Python 3.7 or higher
- Internet connection

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/samarthnaikk/tREDn.git
   cd tREDn
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python app.py
   ```

4. Open your browser and navigate to `http://localhost:5001`

## Usage

### Web Interface

1. **Search Reddit**: Enter your search prompt/topic and configure parameters
2. **View Results**: Browse Reddit posts and comments matching your prompt in an organized format
3. **Save Data**: Results are automatically saved as JSON files
4. **Export CSV**: Download search results as CSV for analysis
5. **Manage Files**: Load previous searches and manage saved files

### Search Parameters

- **Query**: Enter any topic, question, or prompt to search Reddit content
- **Number of Posts**: How many posts to fetch (5-25)
- **Sort Method**: Top, Hot, or New
- **Time Period**: Day, Week, Month, Year, or All Time

## File Structure

```
tREDn/
├── app.py              # Main Flask application
├── utils.py            # Utility functions for Reddit data processing
├── requirements.txt    # Python dependencies
├── README.md          # Project documentation
└── data/              # Saved search results (auto-created)
```

## API Endpoints

- `GET /` - Main web interface
- `POST /search` - Perform Reddit search
- `GET /files` - List saved search files
- `GET /load/<filename>` - Load specific search results
- `GET /export/<filename>` - Export search results as CSV

## Data Format

### JSON Storage
Search results are stored in JSON format with the following structure:
```json
{
  "search_query": "topic name",
  "search_timestamp": "2025-01-01T00:00:00",
  "posts": [
    {
      "title": "Post title",
      "author": "username",
      "subreddit": "subreddit_name",
      "score": 100,
      "upvotes": 120,
      "comment_count": 50,
      "post_date": "2025-01-01 12:00:00",
      "external_url": "https://example.com",
      "reddit_permalink": "https://reddit.com/r/...",
      "text_content": "Post content",
      "top_comments": [...]
    }
  ],
  "statistics": {
    "total_posts": 10,
    "total_upvotes": 1000,
    "total_comments": 500,
    "average_score": 100.5
  }
}
```

### CSV Export
CSV exports include the following columns:
- title
- author
- subreddit
- score
- upvotes
- comment_count
- post_date
- external_url
- reddit_permalink

## Technical Details

### Rate Limiting
The application includes automatic rate limiting with 1.2-second delays between requests to respect Reddit's servers.

### Error Handling
Robust error handling for network issues, malformed responses, and invalid requests.

### Data Processing
- Automatic filtering of deleted/removed content
- Top comments sorting by score
- Timestamp conversion to readable format
- Safe filename generation for saved searches

## Troubleshooting

### Common Issues

**No results found**
- Verify internet connection
- Try broader search terms
- Adjust time period filter

**Rate limiting errors**
- Wait a few minutes between large searches
- The app automatically handles rate limiting

**Import errors**
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Verify Python version 3.7+

## Development

### Running in Development Mode
```bash
python app.py
```
The Flask app runs in debug mode by default for development.

### Code Structure
- `app.py`: Main Flask application with web interface and API endpoints
- `utils.py`: Core Reddit data processing utilities and CSV conversion

### Adding Features
The modular structure allows easy extension:
- Add new API endpoints in `app.py`
- Extend data processing in `utils.py`
- Modify the HTML template in `app.py` for UI changes

## License

This project is licensed under the MIT License.

## Author

Created by samarthnaikk

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review error messages for specific guidance
3. Ensure all dependencies are properly installed
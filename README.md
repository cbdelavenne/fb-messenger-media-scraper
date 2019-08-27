# fb-messenger-image-scraper
Helper script to scrape your Facebook Messenger account for images shared in your conversations quickly and efficiently.

### Configuration

Carefully configure the `config/.env` file to download images from the specific conversation you want.

#### Key-value pairs

- `email`: Your FB account email used for authentication.
- `password`: Your FB account password used for authentication.
- `user_url`: The URL to your friend's FB page.
- `threads`: Number of threads to look through (from most recent). If the conversation you're looking for is very old, you'll have to increase this number. Otherwise, you'll want to set this to a low value for speed.
- `messages`: Number of messages to search through for images once the thread with your friend has been found. Again, if the media you want to download is hundreds of messages go, you'll want to increase this value proportionally.
- `download_path`: Local target path for the images to be downloaded to.

### Execution

1. Install Python 3.x
2. Open `cmd` (Windows) or `terminal` (Unix)
3. Install pip prerequisites: `pip install -r requirements.txt`
4. Modify `config/.env` to your needs
5. Execute `python ./fbm-scraper.py`

# fb-messenger-image-scraper
Helper script to scrape your Facebook Messenger account for images shared in your conversations quickly and efficiently.

### Configuration

Carefully create and configure a `config.ini` file to your needs under the same directory as this script.
Use `config.ini.example` as a reference guide.

#### Key-value pairs

- `[Credentials][email]`: Your FB account email used for authentication.
- `[Credentials][password]`: Your FB account password used for authentication.
- `[Friend][url]`: The URL to your friend's FB page.
- `[Threads][search_limit]`: Number of threads to look through (from most recent). If the conversation you're looking for is very old, you'll have to increase this number. Otherwise, you'll want to set this to a low value for speed.
- `[Threads][before_date]`: (**Note:** Optional. If not used, leave value after `=` blank) Specify a date (in format Y-m-d, i.e. 2019-08-15) from which point to retrieve threads. 
- `[Messages][search_limit]`: Number of messages to search through for images once the thread with your friend has been found. Again, if the media you want to download is hundreds of messages go, you'll want to increase this value proportionally.
- `[Messages][before_date]`: (**Note:** Optional. If not used, leave value after `=` blank) Specify a date (in format Y-m-d, i.e. 2019-08-15) from which point to retrieve messages. For instance, for a given thread, the script will only download images sent in last `[Messages][search_limit]` starting from the date specified here.
- `[Media][sender_only]`: Simple `true` or `false` value. If `true`, only images from your target Friend will be downloaded. 
- `[Download][path]`: Local target path for the images to be downloaded to.

### Execution

1. Install Python 3.x
2. Open `cmd` (Windows) or `terminal` (Unix)
3. Install pip prerequisites: `pip install -r requirements.txt`
4. Create and configure `config.ini`
5. Execute `python ./fbm-scraper.py`

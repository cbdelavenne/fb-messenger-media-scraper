import os
import requests
import time
import uuid
import configparser
import datetime

from fbchat import Client, ImageAttachment
from fbchat import FBchatException
from pathlib import Path

politeness_index = 0.5  # ;)
epoch = datetime.datetime(1970, 1, 1)


def download_file_from_url(url, target_path):
    """
    Download image from a given URL to a specified target path.

    :param url: URL of file to download
    :param target_path: Local target path to save the file
    :type url: str
    :type target_path: str
    """
    if url is not None:
        r = requests.get(url)
        with open(target_path, 'wb') as f:
            print('\tDownloading image to {path}'.format(path=target_path))
            f.write(r.content)


def convert_date_to_unix_ms(date, as_int=True):
    """
    Convert a given date string to epoch (int in milliseconds)

    :param date: Date string (preferred format %Y-%m-%d)
    :param as_int: Return unix timestamp as an integer value, instead of a float
    :type date: str
    :type as_int: int
    :return: int
    """
    try:
        dt = datetime.datetime.strptime(date, '%Y-%m-%d')
        res = ((dt - epoch).total_seconds() * 1000)  # convert to milliseconds

        return int(res) if as_int else res
    except ValueError:
        return None


if __name__ == '__main__':
    config_path = Path('.') / 'config.ini'
    if os.path.exists(config_path) is False:
        raise Exception("Please create config.ini under this script's current directory")

    # Load config file
    config = configparser.ConfigParser()
    config.read(config_path)

    download_path = config.get('Download', 'path')
    if os.path.exists(download_path) is False:
        raise Exception("The path specified in download_path does not exist ({path}). Please specify a valid path in "
                        "config.ini".format(path=download_path))

    # Initialize FB Client
    fb_email = config.get('Credentials', 'email')
    fb_pw = config.get('Credentials', 'password')
    fb_client = Client(fb_email, fb_pw)

    # Search for latest threads
    thread_search_limit = int(config.get('Threads', 'search_limit'))
    thread_search_before = convert_date_to_unix_ms(config.get('Threads', 'before_date'))

    if thread_search_before is not None:
        threads = fb_client.fetchThreadList(limit=thread_search_limit, before=thread_search_before)
    else:
        threads = fb_client.fetchThreadList(limit=thread_search_limit)

    # Find correct thread for given user URL
    my_thread = None
    friend_url = config.get('Friend', 'url')
    for thread in threads:
        if thread.url == friend_url:
            my_thread = thread
            break

    # Get Messages for my_thread
    if my_thread is not None:
        message_search_limit = int(config.get('Messages', 'search_limit'))
        message_search_before = convert_date_to_unix_ms(config.get('Messages', 'before_date'))

        if message_search_before is not None:
            messages = fb_client.fetchThreadMessages(my_thread.uid, limit=message_search_limit,
                                                     before=message_search_before)
        else:
            messages = fb_client.fetchThreadMessages(my_thread.uid, limit=message_search_limit)

        # Extract Image attachments' full-sized image signed URLs (along with their original file extension)
        full_images = []

        sender_id = None
        if config.getboolean('Media', 'sender_only'):
            sender_id = my_thread.uid

        for message in messages:
            if len(message.attachments) > 0:
                if (sender_id is None) or (sender_id == message.author):
                    for attachment in message.attachments:
                        if isinstance(attachment, ImageAttachment):
                            try:
                                full_images.append({
                                    'extension': attachment.original_extension,
                                    'full_url': fb_client.fetchImageUrl(attachment.uid)
                                })
                            except FBchatException:
                                pass  # ignore errors

        # Download Full Images
        if len(full_images) > 0:
            images_count = len(full_images)

            print('Attempting to download {count} images...................\n'.format(count=images_count))

            for full_image in full_images:
                friend_name = str.lower(my_thread.name).replace(' ', '_')
                file_uid = str(uuid.uuid4())
                file_ext = full_image['extension']
                img_url = full_image['full_url']

                image_path = ''.join([download_path, '\\', 'fb-image-', friend_name, '-', file_uid, '.', file_ext])

                download_file_from_url(img_url, image_path)

                # Sleep half a second between file downloads to avoid getting flagged as a bot
                time.sleep(politeness_index)
        else:
            print('No images to download in the last {count} messages'.format(count=message_search_limit))
    else:
        print('Thread not found for URL provided')

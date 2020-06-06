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


def convert_date_to_epoch(date, as_int=True):
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
        res = ((dt - epoch).total_seconds() * 1000.0)  # convert to milliseconds

        return int(res) if as_int else res
    except ValueError:
        return None


def convert_epoch_to_datetime(timestamp, dt_format='%Y-%m-%d_%H.%M.%S'):
    """
    Convert epoch (unix time in ms) to a datetime string

    :param timestamp: Unix time in ms
    :param dt_format: Format of datetime string
    :type timestamp: str
    :type dt_format: str
    :return:
    """
    s = int(timestamp) / 1000.0
    dt_str = datetime.datetime.fromtimestamp(s).strftime(dt_format)
    return dt_str


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
    thread_search_before = convert_date_to_epoch(config.get('Threads', 'before_date'))

    if thread_search_before is not None:
        threads = fb_client.fetchThreadList(limit=thread_search_limit, before=thread_search_before)
    else:
        threads = fb_client.fetchThreadList(limit=thread_search_limit)

    # Find correct thread for given user URL
    my_thread = None
    friend_url = config.get('Friend', 'url')
    for thread in threads:
        try:
             if thread.url == friend_url:
                my_thread = thread
                break
        except AttributeError:
             pass

    # Get Messages for my_thread
    if my_thread is not None:
        thread_message_count = my_thread.message_count
        thread_message_name = my_thread.name

        print('Found {count} messages in thread with {friend_name}'.format(count=thread_message_count,
                                                                           friend_name=thread_message_name))

        message_before_date = config.get('Messages', 'before_date')
        message_search_limit = int(config.get('Messages', 'search_limit'))
        message_search_before = convert_date_to_epoch(message_before_date)

        if message_search_limit > thread_message_count:
            message_search_limit = thread_message_count
            print('\tWarning: Message search limit was greater than the total number of messages in thread.\n')

        if message_search_before is not None:
            messages = fb_client.fetchThreadMessages(my_thread.uid, limit=message_search_limit,
                                                     before=message_search_before)
            print('Searching for images in the {message_limit} messages sent before {before_date}...'.format(
                message_limit=message_search_limit, before_date=message_before_date))
        else:
            messages = fb_client.fetchThreadMessages(my_thread.uid, limit=message_search_limit)
            print('Searching for images in the last {message_limit} messages...'.format(
                message_limit=message_search_limit))

        sender_id = None
        if config.getboolean('Media', 'sender_only'):
            sender_id = my_thread.uid
            print('\tNote: Only images sent by {friend_name} will be downloaded (as specified by sender_only in your '
                  'config.ini)'.format(friend_name=thread_message_name))

        # Extract Image attachments' full-sized image signed URLs (along with their original file extension)
        total_count = 0
        skip_count = 0
        full_images = []
        last_message_date = None
        print('\n')

        extension_blacklist = str.split(config.get('Media', 'ext_blacklist'), ',')

        for message in messages:
            message_datetime = convert_epoch_to_datetime(message.timestamp)

            if len(message.attachments) > 0:
                if (sender_id is None) or (sender_id == message.author):
                    for attachment in message.attachments:
                        if isinstance(attachment, ImageAttachment):
                            try:
                                attachment_ext = str.lower(attachment.original_extension)

                                if attachment_ext not in extension_blacklist:
                                    full_images.append({
                                        'extension': attachment_ext,
                                        'timestamp': message_datetime,
                                        'full_url': fb_client.fetchImageUrl(attachment.uid)
                                    })
                                    print('+', sep=' ', end='', flush=True)
                                else:
                                    skip_count += 1
                                    print('-', sep=' ', end='', flush=True)

                                total_count += 1
                            except FBchatException:
                                pass  # ignore errors

            last_message_date = message_datetime

        # Download Full Images
        if len(full_images) > 0:
            images_count = len(full_images)
            print('\n\nFound a total of {total_count} images. Skipped {skip_count} images that had a blacklisted '
                  'extension'.format(total_count=total_count, skip_count=skip_count))
            print('Attempting to download {count} images...................\n'.format(count=images_count))

            for full_image in full_images:
                friend_name = str.lower(my_thread.name).replace(' ', '_')
                file_uid = str(uuid.uuid4())
                file_ext = full_image['extension']
                file_timestamp = full_image['timestamp']
                img_url = full_image['full_url']

                image_path = ''.join([download_path, '\\', 'fb-image-', file_uid, '-', friend_name, '-',
                                      file_timestamp, '.', file_ext])

                download_file_from_url(img_url, image_path)

                # Sleep half a second between file downloads to avoid getting flagged as a bot
                time.sleep(politeness_index)
        else:
            print('No images to download in the last {count} messages'.format(count=message_search_limit))

        # Reminder of last message found
        print('\nLast message scanned for image attachments was dated: {last_message_date}'.format(
            last_message_date=last_message_date))
    else:
        print('Thread not found for URL provided')

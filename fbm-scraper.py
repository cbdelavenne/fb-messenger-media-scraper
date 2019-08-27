import os
from pathlib import Path
import uuid
import requests
from dotenv import load_dotenv
from fbchat import Client, ImageAttachment
from fbchat import FBchatException

import time


def download_file_from_url(url, target_path):
    """
    Download image from a given URL to a specified target path.

    :param url: URL of file to download
    :param target_path: Local target path to save the file
    """
    if url is not None:
        r = requests.get(url)
        with open(target_path, 'wb') as f:
            print('\tDownloading image to {path}'.format(path=target_path))
            f.write(r.content)


if __name__ == '__main__':
    env_path = Path('.') / 'config/.env'
    load_dotenv(dotenv_path=env_path)

    download_path = os.getenv('download_path')

    if os.path.exists(download_path) is False:
        raise Exception('Download path does not exist. Please specify a valid path in .env')

    fb_email = os.getenv('email')
    fb_pw = os.getenv('password')

    fb_client = Client(fb_email, fb_pw)

    threads = fb_client.fetchThreadList()

    # Find correct thread for given user URL
    my_thread = None
    for thread in threads:
        if thread.url == os.getenv('user_url'):
            my_thread = thread

    # Get Messages for my_thread
    if my_thread is not None:
        msg_count = os.getenv('messages')

        messages = fb_client.fetchThreadMessages(my_thread.uid, limit=msg_count)

        full_images = []

        # Extract Image attachments' full-sized image signed URLs (along with their original file extension)
        for message in messages:
            if len(message.attachments) > 0:
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
                time.sleep(0.5)
        else:
            print('No images to download in the last {count} messages'.format(count=msg_count))

    else:
        print('Thread not found for URL provided')

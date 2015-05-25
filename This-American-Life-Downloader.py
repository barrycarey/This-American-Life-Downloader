__author__ = 'Barry Carey'
import os
import threading
import urllib.request
import urllib.error
import time
from bs4 import BeautifulSoup
import re


# TODO Auto strip slash on end of path
# TODO Check if output directory exists, create it if not
# TODO Add duplicate detection
# TODO Add failed download output

###########################
#   CONFIGURATION AREA   ##
###########################

STARTING_EPISODE = 1
ENDING_EPISODE = 13
DOWNLOAD_THREADS = 5
OUTPUT_DIRECTORY = r"G:\your\download\path" # Do Not Include Trailing Slash In Path


##############################
#   END CONFIGURATION AREA   #
##############################


def dl_thread(url, ep_number, output_dir):

    episode_name = str(ep_number) + " - This American Life - " + get_episode_name(ep_number) + ".mp3"

    print("[+] Downloading: " + episode_name)

    try:
        with urllib.request.urlopen(url) as response:

            local_file_name = os.path.join(output_dir, episode_name)

            output_file = open(local_file_name, 'wb')
            data = response.read()
            output_file.write(data)
            output_file.close()

    except (urllib.error.HTTPError, urllib.error.URLError) as e:

            print('[x] ERROR: Failed to download episode: ', ep_number)
            print('[x] ERROR MSG: ' + e.msg)


def get_episode_name(ep_number):
    """
    Searches This American Life Site for episode number.  Then parses the page looking for an h3 tag that begins with the
    episode number. Uses the remainder of h3 tag as eposide name.

    Name is run through re to strip any chars that are not valid for file names

    :param ep_number:
    :return:
    """
    current_page = 1

    # Search up to 20 pages of results for episode name.
    while current_page <= 20:

        response = urllib.request.urlopen("http://www.thisamericanlife.org/search?page=" + str(current_page) + "&keys=" + str(ep_number))
        page = BeautifulSoup(response)

        for h3 in page.find_all('h3'):

            if h3.string[0:len(str(ep_number))] == str(ep_number):
                cleaned_filename = re.sub(r'[/\\:*?"<>|\']', '', h3.string[len(str(ep_number)) + 2:])
                return cleaned_filename

        current_page += 1

    return 'UNKNOWN EPISODE NAME'



def do_downloads(start_ep, end_ep, output_dir, download_threads):

    current_ep = start_ep
    base_url = "http://audio.thisamericanlife.org/jomamashouse/ismymamashouse/"

    while current_ep < end_ep:

        current_url = base_url + str(current_ep) + ".mp3"

        while threading.active_count() > download_threads:
                print('[x] Max download threads reached.  Waiting for threads to decrease')
                time.sleep(2)

        t = threading.Thread(target=dl_thread, args=(current_url, current_ep, output_dir))
        t.start()

        current_ep += 1

do_downloads(STARTING_EPISODE, ENDING_EPISODE, OUTPUT_DIRECTORY, DOWNLOAD_THREADS)

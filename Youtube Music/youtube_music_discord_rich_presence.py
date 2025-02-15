import json
import subprocess
import time
import pypresence
import requests
import pathlib
import os
from win32com.client import Dispatch

title = "Deciphering..."
artist = "Deciphering..."
start = int(time.time().real)
end = start + 1
thumbnail = "https://drive.usercontent.google.com/download?id=1kNJslXFWz8dWgUWenQG1EZAjuDf7UoB_"
url = "https://music.youtube.com/"

buttons = [
    {"label": "Listen", "url": url},
    {"label": "Git Repo", "url": "https://github.com/PhoenixJatrix/Discord-Rich-Presence-Python-Scripts"}
]

set_up_details_dir = "C:\\Users\\Public\\Downloads\\Youtube Music"
set_up_details_file = f"{set_up_details_dir}\\setup.txt"
bat_path = f"{set_up_details_dir}\\Youtube Music.bat"

oauth_client_id = None
google_apikey = None
chrome_path = None
status_logs = None
song_logs = None

status_logs_file = f"{set_up_details_dir}\\log.txt"
song_logs_file = f"{set_up_details_dir}\\history.txt"

def completed_setup() -> bool:
    return os.path.exists(set_up_details_file)

def setup():
    print("\nRead the readme.md file to learn how to get the required keys")
    oauth_input = input("Enter Discord oauth client ID: ")
    google_apikey_input = input("Enter Google Console apikey: ")
    chrome_path_input = input("Enter the path to your chrome.exe file: ")
    create_bin = input("Create a desktop shortcut as 'Youtube Music' (y|n): ")

    if not os.path.exists(set_up_details_dir):
        os.mkdir(set_up_details_dir)

    if os.path.exists(set_up_details_dir):
        set_up_details = open(set_up_details_file, "w")

        if create_bin.lower() in ["yes", "y"]:
            make_desktop_bat()

        _status_log = open(status_logs_file, "a")
        _song_logs = open(song_logs_file, "a")

        set_up_details.write(f"{oauth_input}\n{google_apikey_input}\n{chrome_path_input}")
        set_up_details.close()

        return oauth_input, google_apikey_input, chrome_path_input, _status_log, _song_logs
    else:
        print("set up failed, could not save setup.txt")
        return None

def get_details():
    set_up_details = open(set_up_details_file, "r")
    _oauth_client_id = set_up_details.readline()
    _google_apikey = set_up_details.readline()
    _chrome_path = set_up_details.readline()
    set_up_details.close()

    _status_log = open(status_logs_file, "a")
    _song_logs = open(song_logs_file, "a")
    return _oauth_client_id, _google_apikey, _chrome_path, _status_log, _song_logs

def get_tabs():
    response = requests.get("http://localhost:9222/json")
    return response.json()

def cast_time(time_str: str):
    total_time = 0

    modified_time = time_str.replace("PT", "")

    if "M" in modified_time:
        minutes = modified_time[0:modified_time.find("M")]
        total_time = int(minutes) * 60

    if "S" in modified_time:
        seconds = modified_time[modified_time.find("M") + 1:len(modified_time) - 1]
        total_time += int(seconds)

    return total_time

def log_message(message) :
    hour = time.localtime().tm_hour
    minute = time.localtime().tm_min
    sec = time.localtime().tm_sec
    time_of_day = "PM" if hour > 12 else "AM"

    if hour > 12:
        hour = hour - 12
    status_logs.write(f"{message} at {f"0{hour}" if hour < 10 else hour}:{f"0{minute}" if minute < 10 else minute}:{f"0{sec}" if sec < 10 else sec} {time_of_day} on {time.localtime().tm_year}:{time.localtime().tm_mon}:{time.localtime().tm_mday}\n\n")
    
def log_songs(message) :
    hour = time.localtime().tm_hour
    minute = time.localtime().tm_min
    sec = time.localtime().tm_sec
    time_of_day = "PM" if hour > 12 else "AM"

    if hour > 12:
        hour = hour - 12
    song_logs.write(f"{message} at {f"0{hour}" if hour < 10 else hour}:{f"0{minute}" if minute < 10 else minute}:{f"0{sec}" if sec < 10 else sec} {time_of_day} on {time.localtime().tm_year}:{time.localtime().tm_mon}:{time.localtime().tm_mday}\n\n")

def extract_id(target_url) -> str:
    if "&" in target_url:
        return updated_url[updated_url.find("=") + 1:updated_url.find("&")]
    else:
        return updated_url[updated_url.find("=") + 1:]

def make_desktop_bat():
    if not os.path.exists(bat_path):
        bat_file = open(bat_path, "w")
        bat_file.write(f"@echo off\npython \"{os.path.abspath(__file__)}\"\npause")
        bat_file.close()

        shell = Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(f"{pathlib.Path.home()}\\Desktop\\Youtube Music.lnk")
        shortcut.Targetpath = bat_path
        shortcut.IconLocation = f"{pathlib.Path(__file__).parent}\\Youtube_Music.ico"
        shortcut.save()

if __name__ == "__main__":
    while True:
        if completed_setup():
            oauth_client_id, google_apikey, chrome_path, status_logs, song_logs = get_details()
            log_message(f"initialized")
        else:
            details = setup()

            if details is not None:
                oauth_client_id, google_apikey, chrome_path, status_logs, song_logs = details
                log_message(f"first initialization")

        if chrome_path is not None:
            # opening chrome in a debug environment
            debugProcess = subprocess.Popen(f"{chrome_path} --remote-debugging-port=9222 --user-data-dir=C:\\ChromeDebug")

            # create an instance with the client ID
            rPresence = pypresence.Presence(oauth_client_id)

            rPresence.connect()
            rPresence.update(state=title, large_image=thumbnail, buttons=buttons, start=start, end=end, details=artist)

            while True:
                try:
                    tabs = list(get_tabs())

                    if tabs:
                        tab = tabs[0]

                        updated_url = str(tab["url"])
                        updated_id = extract_id(updated_url)

                        if url != updated_url:
                            req = requests.get(f"https://www.googleapis.com/youtube/v3/videos?part=snippet,contentDetails&id={updated_id}&key={google_apikey}", timeout = 15)

                            reqJson = req.json()

                            raw_items = list(json.loads(json.dumps(reqJson["items"])))

                            if len(raw_items) > 0:
                                items = raw_items[0]
                                updated_title = str(items["snippet"]["title"])
                                updated_thumbnail = items["snippet"]["thumbnails"]["default"]["url"]
                                duration = items["contentDetails"]["duration"]
                                updated_artist = str(items["snippet"]["channelTitle"])

                                if "-" in updated_title:
                                    updated_artist = updated_title[0:updated_title.find("-")].strip()
                                    updated_title = updated_title[updated_title.find("-") + 1:].strip()

                                title = updated_title
                                start = int(time.time().real)
                                end = start + cast_time(duration)
                                thumbnail = updated_thumbnail
                                artist = updated_artist

                                buttons = [
                                    {"label": "Listen", "url": updated_url},
                                    {"label": "Git Repo", "url": "https://github.com/PhoenixJatrix/Discord-Rich-Presence-Python-Scripts"},
                                ]

                                artist = artist if len(artist) > 2 else f"{artist}   "
                                title = title if len(title) > 2 else f"{title}   "
                                artist = artist.replace(" - Topic", "", -1)

                                url = updated_url
                                rPresence.update(state=artist, large_image=thumbnail, large_text=title, buttons=buttons, start=start, end=end, small_image="https://drive.usercontent.google.com/download?id=1kNJslXFWz8dWgUWenQG1EZAjuDf7UoB_", small_text="Made by PhoenixJatrix", details=title)

                                print(f"Title: {title}. Url: {url}")
                                log_songs(f"Title: {title}. Url: {url}")
                    else:
                        log_message(f"empty metadata for {url}")

                    time.sleep(15)
                except Exception as e:
                    print(e.args)
                    log_message(e)
                    break

        command = input("Encountered an issue. Restart? (y|n): ")

        if command.lower() in ["yes", "y"]:
            print("Restarting")
            log_message("restarting")

            continue
        else:
            log_message("end process")
            break
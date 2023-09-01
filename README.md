# Spotify Downloader script

Downloads your favourite tracks and artists into a directory of your choosing.

## Setup

- Clone the repo
- Open your terminal
- In the terminal, enter the directory in which the repo was cloned
- In the terminal, run `python3 -m venv local-env`
- In the terminal, run `pip install -r requirements.txt`
- In the terminal, run `source ./local-env/bin/activate`
- (In the terminal) Set your client id and client secret environment variables:
  - `export SPOTIFY_DOWNLOADER_CLIENT_ID=your_id`
  - `export SPOTIFY_DOWNLOADER_CLIENT_SECRET=your_secret`
- In the terminal, run `python script.py /path/to/your/directory`
- Allow the app to access your Spotify account. When you see text "Received authorization code. You can close this window." in your browser window, close it.
- When the script outputs "Job complete. Terminating.", your songs will be inside your folder

## Creating your Spotify app

Follow [this guide](https://scribehow.com/shared/Creating_an_app_in_Spotify_Developer_Dashboard__hFIcYmfgSXCL5zWHBosY1Q) to create your app. Then, you can use your client id and secret to retrieve the information about your Spotify account.

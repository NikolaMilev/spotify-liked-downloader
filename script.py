import argparse
import json
import os
import requests
import webbrowser
import csv
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

# Environment variables
client_id = os.environ.get('SPOTIFY_DOWNLOADER_CLIENT_ID')
client_secret = os.environ.get('SPOTIFY_DOWNLOADER_CLIENT_SECRET')
port = int(os.environ.get('SPOTIFY_DOWNLOADER_PORT', 8888))
redirect_uri = os.environ.get('SPOTIFY_DOWNLOADER_REDIRECT_URI', f'http://localhost:{port}/callback')


if not client_id:
    print("Please provide a client id in the SPOTIFY_DOWNLOADER_CLIENT_ID env variable.")
    exit()

if not client_secret:
    print("Please provide a client secret in the SPOTIFY_DOWNLOADER_CLIENT_SECRET env variable.")
    exit()

if not redirect_uri:
    print("Please provide a redirect uri in the SPOTIFY_DOWNLOADER_REDIRECT_URI env variable or just keep it without value.")
    exit()


liked_songs_file_name = 'liked_songs.json'
liked_songs_simple_file_name = 'liked_songs_simple.csv'
liked_artists_file_name = 'liked_artists.json'
liked_artists_simple_file_name = 'liked_artists_simple.csv'

should_shutdown = False  # flag to indicate whether server should shut down

# Function to exchange code for token
def exchange_code_for_token(code):
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': redirect_uri,
        'client_id': client_id,
        'client_secret': client_secret
    }
    response = requests.post('https://accounts.spotify.com/api/token', data=data)
    return response.json()['access_token']

# Function to fetch liked songs
def fetch_liked_songs(token):
    url = "https://api.spotify.com/v1/me/tracks"
    headers = {"Authorization": f"Bearer {token}"}
    liked_songs = []
    while url:
        response = requests.get(url, headers=headers)
        data = response.json()
        liked_songs.extend(data["items"])
        url = data["next"]
    return liked_songs

# Function to fetch liked artists
def fetch_liked_artists(token):
    url = "https://api.spotify.com/v1/me/following?type=artist"
    headers = {"Authorization": f"Bearer {token}"}
    liked_artists = []
    while url:
        response = requests.get(url, headers=headers)
        data = response.json()
        liked_artists.extend(data["artists"]["items"])
        url = data["artists"]["next"]
    return liked_artists

# HTTP request handler
class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global should_shutdown  # use global flag

        query = urlparse(self.path).query
        query_parameters = parse_qs(query)
        code = query_parameters.get("code")
        
        if code:
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(b"Received authorization code. You can close this window.")
            
            token = exchange_code_for_token(code[0])
            print(f"Successfully exchanged code for token.")
            
            # Fetch and save liked songs and artists
            liked_songs = fetch_liked_songs(token)
            print(f"Successfully fetched liked tracks.")
            liked_artists = fetch_liked_artists(token)
            print(f"Successfully fetched liked artists.")
            
            current_directory = os.getcwd()

            # Save as JSON
            with open(liked_songs_file_name, "w") as f:
                json.dump(liked_songs, f, indent=4)
                print(f"Successfully saved to {os.path.join(current_directory, liked_songs_file_name)}")

            with open(liked_artists_file_name, "w") as f:
                print(f"Successfully saved to {os.path.join(current_directory, liked_artists_file_name)}")
                
            # Save as simplified CSV
            with open(liked_songs_simple_file_name, "w", newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["Artist", "Track"])
                for song in liked_songs:
                    writer.writerow([song["track"]["artists"][0]["name"], song["track"]["name"]])
                print(f"Successfully saved to {os.path.join(current_directory, liked_songs_simple_file_name)}")

                    
            with open(liked_artists_simple_file_name, "w", newline='') as f:
                writer = csv.writer(f)
                for artist in liked_artists:
                    writer.writerow([artist["name"]])
                print(f"Successfully saved to {os.path.join(current_directory, liked_artists_simple_file_name)}")

            print("Job complete. Terminating.")
            should_shutdown = True

if __name__ == "__main__":
    # Argument parsing
    parser = argparse.ArgumentParser(description="Fetch Spotify liked songs and artists.")
    parser.add_argument("directory", type=str, help="Directory to save liked songs and artists files.")
    args = parser.parse_args()
    
    os.makedirs(args.directory, exist_ok=True)
    # Change to the specified directory
    os.chdir(args.directory)
    
    # Open the Spotify authorization URL in the default web browser
    scope = "user-library-read user-follow-read"
    auth_url = f"https://accounts.spotify.com/authorize?client_id={client_id}&response_type=code&redirect_uri={redirect_uri}&scope={scope}"
    webbrowser.open(auth_url)
    
    # Spin up the server
    server_address = ("", port)
    httpd = HTTPServer(server_address, RequestHandler)
    print(f"Serving at port {port}")
    
    while not should_shutdown:
        httpd.handle_request()
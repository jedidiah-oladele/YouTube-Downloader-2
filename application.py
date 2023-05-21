"""

https://youtu.be/U2Ww0iPEet4

https://youtube.com/playlist?list=PLbHrOSG7nVN0wdCsdXgj58l713p7c5WQ-

"""


import os
from dotenv import load_dotenv
from urllib.parse import urlparse, parse_qs
from flask import Flask, render_template, request
from helperfunctions import *

load_dotenv()

application = Flask(__name__)


@application.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        submitted_url = request.form["submitted_url"]

        try:
            video_data = return_youtube_data(submitted_url)
            return render_template("index.html", video_data=video_data)
        except ValueError:
            return render_template("index.html", invalid_url=True)

    else:
        return render_template("index.html")


def return_youtube_data(url):
    YOUTUBE_DATA_API_KEY = os.getenv("YOUTUBE_DATA_API_KEY")

    # Extract video ID from URL
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)

    video_id = query_params.get("v")
    playlist_id = query_params.get("list")

    if playlist_id:
        playlist_id = playlist_id[0]
        video_ids = get_playlist_data(YOUTUBE_DATA_API_KEY, playlist_id)
    elif video_id:
        video_ids = [video_id[0]]
    elif parsed_url.path:
        video_ids = [parsed_url.path.split("/")[-1]]

    else:
        raise ValueError("Invalid YouTube URL")

    videos_data = [get_youtube_video_data(YOUTUBE_DATA_API_KEY, id) for id in video_ids]
    return videos_data


if __name__ == "__main__":
    application.run(debug=True)

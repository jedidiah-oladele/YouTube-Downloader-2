import isodate
from googleapiclient.discovery import build
import pytube


def get_youtube_video_data(api_key, video_id):
    try:
        # Build the YouTube Data API service
        # TODO do not rebuild client each time
        youtube = build("youtube", "v3", developerKey=api_key)

        # Call the API to retrieve video details
        video_response = youtube.videos().list(part="snippet", id=video_id).execute()
        video_response_2 = (
            youtube.videos().list(part="contentDetails", id=video_id).execute()
        )

        # Extract video information
        video_snippet = video_response["items"][0]
        video_content_detials = video_response_2["items"][0]

        video_title = video_snippet["snippet"]["title"]
        thumbnail_urls = video_snippet["snippet"]["thumbnails"]

        # Get maximum thumbnail resolution
        thumbnail_res = ["maxres", "high", "standard", "medium", "default"]
        thumbnail_url = None

        for size in thumbnail_res:
            if size in thumbnail_urls:
                thumbnail_url = thumbnail_urls[size]["url"]
                break

        # Handle case when no thumbnail URL is found
        if thumbnail_url is None:
            thumbnail_url = "Thumbnail URL not available"

        download_link = thumbnail_url
        video_resolutions = get_video_resolutions(video_id)

        duration_str = video_content_detials["contentDetails"]["duration"]
        duration = isodate.parse_duration(duration_str)

        # Return the retrieved information
        return {
            "title": video_title,
            "duration": duration,
            "thumbnail_url": thumbnail_url,
            "download_link": download_link,
            "video_resolutions": video_resolutions,
        }

    except ValueError as e:
        print("Error:", str(e))


# Function to extract video ID from URL
def get_playlist_data(api_key, playlist_id):
    youtube = build("youtube", "v3", developerKey=api_key)

    # Accept playlist URL from user

    try:
        # Retrieve videos in the playlist
        playlist_items = []
        next_page_token = None

        while True:
            playlist_response = (
                youtube.playlistItems()
                .list(
                    part="snippet",
                    playlistId=playlist_id,
                    maxResults=50,
                    pageToken=next_page_token,
                )
                .execute()
            )

            playlist_items.extend(playlist_response["items"])
            next_page_token = playlist_response.get("nextPageToken")

            if not next_page_token:
                break

        # Extract video IDs
        video_ids = [
            item["snippet"]["resourceId"]["videoId"] for item in playlist_items
        ]

        # Print the retrieved video IDs
        return video_ids

    except ValueError as e:
        print("Error:", str(e))


def get_video_resolutions(video_id):
    video_url = f"https://www.youtube.com/watch?v={video_id}"

    # Create a YouTube object.
    pytube_youtube = pytube.YouTube(video_url)

    # Get the video's streams object.
    streams = pytube_youtube.streams
    streams = streams.filter(progressive=True).order_by("resolution")
    streams = streams[::-1]

    resolutions = [s.resolution for s in streams]
    return resolutions


def download_video_stream(streams, resolutions="1080p"):
    # Iterate over the streams object and get the stream with the desired quality.
    for stream in streams:
        if stream.resolution == resolutions:
            stream.download()

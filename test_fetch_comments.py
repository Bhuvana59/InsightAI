# test_fetch_comments.py
# Smallest possible script to verify: URL -> video ID -> real comments from YouTube.

import os
# 'os' lets us read environment variables (like our API key) from the system.

from dotenv import load_dotenv
# 'load_dotenv' reads the .env file and loads its contents into environment variables.

from googleapiclient.discovery import build
# 'build' creates a client object that knows how to talk to Google APIs (YouTube in our case).

from googleapiclient.errors import HttpError
# 'HttpError' is the exception Google's client raises when the API call fails
# (e.g. wrong key, video not found, comments disabled). We need this to catch errors properly.

from youtube_utils import extract_video_id
# Our own function from Step 3, reused here so we don't duplicate logic.


def get_youtube_client(api_key: str):
    """
    Builds and returns a YouTube API client object.
    'youtube' = the name of the API, 'v3' = the version we're using.
    This object is what we'll call .commentThreads().list() on later.
    """
    return build("youtube", "v3", developerKey=api_key)


def fetch_first_10_comments(youtube_client, video_id: str):
    """
    Calls the YouTube Data API v3 'commentThreads.list' endpoint to fetch
    the first 10 top-level comments for a given video ID.

    Returns a list of comment text strings, or raises HttpError if the
    request fails (e.g. comments disabled, video not found, bad API key).
    """
    request = youtube_client.commentThreads().list(
        part="snippet",       # 'snippet' = the actual comment data (text, author, likes, etc.)
        videoId=video_id,     # the video we want comments from
        maxResults=150,        # limit to 10 comments, since this is just a connectivity test
        textFormat="plainText"  # get plain text instead of HTML-formatted text
    )
    response = request.execute()  # this line actually sends the HTTP request to Google's servers

    comments = []
    # response["items"] is a list of "comment thread" objects (top-level comment + its replies info)
    for item in response["items"]:
        # Drill into the nested JSON structure to get just the comment text.
        # This path is fixed by YouTube's API response format -- it's always this shape.
        comment_text = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
        comments.append(comment_text)

    return comments


def main():
    # Load variables from .env into the environment (so os.getenv can see them).
    load_dotenv()

    # Read the API key we saved in .env. Returns None if the key is missing.
    api_key = os.getenv("YOUTUBE_API_KEY")

    if not api_key:
        # Fail early with a clear message instead of a confusing error later.
        print("ERROR: YOUTUBE_API_KEY not found. Check your .env file.")
        return

    # Ask the user for a YouTube URL directly in the terminal.
    url = input("Enter a YouTube video URL: ").strip()

    # Step 1: extract the video ID from whatever URL format the user typed.
    video_id = extract_video_id(url)

    if video_id is None:
        # Handles the "invalid URL" requirement -- stop here instead of calling the API.
        print("ERROR: Could not extract a valid video ID from that URL. "
              "Please check the link and try again.")
        return

    print(f"Extracted video ID: {video_id}")

    # Step 2: build the API client using our key.
    youtube_client = get_youtube_client(api_key)

    # Step 3: try fetching comments, but be ready to handle failures gracefully.
    try:
        comments = fetch_first_10_comments(youtube_client, video_id)

    except HttpError as e:
        # HttpError contains a status code (e.g. 403, 404) and a reason.
        # We check these to give the user a meaningful message instead of a raw stack trace.
        if e.resp.status == 403:
            print("ERROR: Comments are disabled for this video, "
                  "or your API key does not have permission.")
        elif e.resp.status == 404:
            print("ERROR: Video not found. Double-check the video ID/URL.")
        else:
            print(f"ERROR: YouTube API request failed (status {e.resp.status}). "
                  f"Details: {e}")
        return

    # Step 4: if we got here, the call succeeded. Print what we found.
    if not comments:
        print("No comments were returned for this video.")
        return

    print(f"\nFetched {len(comments)} comments:\n")
    for i, comment in enumerate(comments, start=1):
        print(f"{i}. {comment}\n")


# This ensures main() only runs when this file is executed directly,
# not when it's imported elsewhere (good Python practice).
if __name__ == "__main__":
    main()

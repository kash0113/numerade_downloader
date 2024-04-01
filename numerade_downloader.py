import argparse
import httpx
import re
import sys


def fetch_url_content(url: str) -> str:
    """
    Fetches content from the given URL and returns it as a string.
    """
    try:
        response = httpx.get(url)
        response.raise_for_status()
        return response.text
    except httpx.HTTPStatusError as e:
        print(f"HTTP error occurred: {e}")
        return ""
    except Exception as e:
        print(f"An error occurred: {e}")
        return ""


def extract_video_url(content: str) -> str:
    """
    Extracts the video URL from the given content using regex.
    """
    video_url_regex = r'videoUrl\s*=\s*"([^"]+)"'
    video_url_match = re.search(video_url_regex, content)
    return video_url_match.group(1) if video_url_match else None


def extract_bucket_folder(content: str) -> str:
    """
    Extracts the bucket folder from the given content using regex.
    """
    bucket_folder_regex = r'bucketFolder\s*=\s*"([^"]+)"'
    bucket_folder_match = re.search(bucket_folder_regex, content)
    return bucket_folder_match.group(1) if bucket_folder_match else None


def download_video(filename: str, video_url: str, bucket_folder: str) -> None:
    """
    Downloads the video using the provided video URL and bucket folder.
    """
    try:
        url = f"https://cdn.numerade.com/{bucket_folder}/{video_url}.mp4"
        with httpx.stream("GET", url) as response:
            with open(filename + ".mp4", "wb") as file:
                for chunk in response.iter_bytes():
                    file.write(chunk)
        print("Download Complete")
    except httpx.HTTPStatusError as e:
        print(f"HTTP error occurred: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Download video from a Numerade URL",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "url", nargs="?", help="The URL of the Numerade page containing the video"
    )

    try:
        args = parser.parse_args()
    except argparse.ArgumentError:
        parser.print_usage()
        print(
            "Example: numerade_downloader.py https://www.numerade.com/ask/question/example"
        )
        sys.exit()

    if args.url:
        if not args.url.startswith("https://www.numerade.com/ask/question/"):
            print(
                "Invalid URL format. URL must start with 'https://www.numerade.com/ask/question/'. Exiting..."
            )
            sys.exit(1)

        content = fetch_url_content(args.url)
        if content:
            filename = [part for part in args.url.split("/") if part][-1]
            video_url = extract_video_url(content)
            bucket_folder = extract_bucket_folder(content)
            if video_url and bucket_folder:
                download_video(filename, video_url, bucket_folder)
    else:
        parser.print_usage()
        print(
            "Example: numerade_downloader.py https://www.numerade.com/ask/question/example"
        )
        sys.exit()


if __name__ == "__main__":
    main()

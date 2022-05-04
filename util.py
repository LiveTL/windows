def get_ytid_from_url(url: str):
    """
    Get the youtube video id from a url.
    """
    if 'youtu.be' in url:
        return url.split('/')[-1]
    if 'youtube.com' in url:
        return url.split('v=')[-1].split('&')[0]
    return None


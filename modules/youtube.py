from datetime import datetime
import yt_dlp
import logging
import zoneinfo

def get_upcoming_streams(channel_id: str):
    opts = {
        'extract_flat': True,
        'skip_download': True,
        'quiet': True,
    }

    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(f"https://www.youtube.com/@{channel_id}/streams", download=False)
    
    live_entries = []
    for entry in info.get('entries', []):
        if entry.get('live_status') == 'was_live':
            continue

        release_ts = entry.get('release_timestamp')
        logging.info(f"Found stream: {entry.get('title')} (release at {datetime.fromtimestamp(release_ts, tz=zoneinfo.ZoneInfo('Asia/Tokyo')) if release_ts else 'unknown'})")
        live_entries.append({
            'url': entry.get('url'),
            'title': entry.get('title'),
            'start_at': datetime.fromtimestamp(release_ts, tz=zoneinfo.ZoneInfo('Asia/Tokyo')) if release_ts else None,
        })
    return live_entries

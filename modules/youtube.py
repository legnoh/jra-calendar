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
        status = entry.get('live_status')
        release_ts = entry.get('release_timestamp')
        if status == 'is_upcoming':
            start_at = datetime.fromtimestamp(release_ts, tz=zoneinfo.ZoneInfo('Asia/Tokyo'))
        elif status == 'is_live':
            start_at = datetime.now(zoneinfo.ZoneInfo('Asia/Tokyo')).replace(
                hour=9,
                minute=0,
                second=0,
                microsecond=0,
            )
        else:
            continue
        logging.info(f"Found stream: {entry.get('title')}")
        live_entries.append({
            'url': entry.get('url'),
            'title': entry.get('title'),
            'status': status,
            'start_at': start_at,
        })
    return live_entries

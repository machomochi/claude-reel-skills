"""Turn one Instagram reel into text + still pictures that Claude can read.

WHAT THIS IS (my notes):
    Claude can't watch a video. So this script does the "watching" for it:
      1. downloads the reel with yt-dlp,
      2. turns the speech into text with faster-whisper (runs on your own CPU,
         free, no API key),
      3. saves a still picture every 2 seconds, because a lot of reels only
         SAY "use this site" while the real name/URL/code is written ON SCREEN,
      4. deletes the video, keeping only the text and the stills.
    Claude then reads transcripts/<id>.json and looks at frames/<id>/*.jpg.

Usage:
    venv/Scripts/python -X utf8 transcribe.py <reel_url>      (Windows)
    venv/bin/python transcribe.py <reel_url>                  (macOS/Linux)

Output:
    transcripts/<shortcode>.json         caption + spoken transcript
    frames/<shortcode>/f_000s.jpg ...    one still every 2 s (max 45)

Only process videos you are allowed to download, and respect the site's terms.
"""
import json
import re
import sys
from pathlib import Path

import yt_dlp                          # downloads the video
from faster_whisper import WhisperModel  # speech-to-text, runs locally

# Everything is written next to this script, so the folder is self-contained.
ROOT = Path(__file__).resolve().parent


def decode_audio(path: Path):
    """Read the video's sound as 16 kHz mono numbers (what Whisper expects).

    I do this with PyAV myself because faster-whisper's own decoder clashed
    with the installed PyAV version. Result: a float32 array between -1 and 1.
    """
    import av
    import numpy as np

    resampler = av.AudioResampler(format="s16", layout="mono", rate=16000)
    chunks = []
    with av.open(str(path)) as container:
        for frame in container.decode(audio=0):
            for out in resampler.resample(frame):
                chunks.append(out.to_ndarray().reshape(-1))
        for out in resampler.resample(None):  # flush what's left in the buffer
            chunks.append(out.to_ndarray().reshape(-1))
    # 16-bit integers -> floats between -1.0 and 1.0
    return np.concatenate(chunks).astype(np.float32) / 32768.0


def save_frames(path: Path, out_dir: Path, every_s: float = 2.0, max_frames: int = 45):
    """Save one JPEG every `every_s` seconds so Claude can read on-screen text.

    Uses only PyAV (which ships its own copy of FFmpeg's libraries), so you
    don't need to install ffmpeg or Pillow separately.
    Pictures are scaled down to 720 px wide: still sharp enough to read text,
    but small enough not to waste tokens when Claude looks at them.
    """
    import av

    out_dir.mkdir(parents=True, exist_ok=True)
    saved, next_t = 0, 0.0
    with av.open(str(path)) as src:
        vs = src.streams.video[0]
        for frame in src.decode(video=0):
            # time of this frame in seconds
            t = float(frame.pts * vs.time_base) if frame.pts is not None else 0.0
            if t + 1e-6 < next_t:
                continue  # not time for the next still yet
            w = 720 if frame.width > 720 else frame.width
            h = int(frame.height * w / frame.width) // 2 * 2  # JPEG wants even sizes
            img = frame.reformat(width=w, height=h, format="yuvj420p")
            # write a single-picture "video" with the JPEG encoder = one .jpg file
            with av.open(str(out_dir / f"f_{int(t):03d}s.jpg"), "w", format="image2") as dst:
                st = dst.add_stream("mjpeg")
                st.width, st.height, st.pix_fmt = w, h, "yuvj420p"
                for pkt in st.encode(img):
                    dst.mux(pkt)
                for pkt in st.encode(None):
                    dst.mux(pkt)
            saved += 1
            next_t += every_s
            if saved >= max_frames:  # cap long videos (45 stills = 90 s)
                break
    return saved


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    url = sys.argv[1]

    # The "shortcode" is the reel's ID in the URL: /reel/<shortcode>/
    m = re.search(r"/(?:reel|reels|p)/([A-Za-z0-9_-]+)", url)
    if not m:
        print("ERROR: not a reel/post URL")
        return 2
    code = m.group(1)
    out_dir = ROOT / "downloads" / code
    out_dir.mkdir(parents=True, exist_ok=True)
    out_json = ROOT / "transcripts" / f"{code}.json"
    out_json.parent.mkdir(parents=True, exist_ok=True)

    # 1. Download. "best[ext=mp4]" asks for one file that already has sound,
    #    so we don't need ffmpeg to merge separate audio and video files.
    opts = {
        "outtmpl": str(out_dir / "video.%(ext)s"),
        "format": "best[ext=mp4]/best",
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
    }
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=True)
        video = Path(ydl.prepare_filename(info))

    # 2. Speech to text. "small" is a good balance of speed and accuracy on a
    #    normal laptop CPU; int8 keeps memory use low. vad_filter skips silence
    #    and music-only parts. The model downloads once (~500 MB) on first run.
    model = WhisperModel("small", device="cpu", compute_type="int8")
    segments, meta = model.transcribe(decode_audio(video), vad_filter=True)
    transcript = " ".join(s.text.strip() for s in segments)

    out_json.write_text(
        json.dumps(
            {
                "shortcode": code,
                "url": url,
                "author": info.get("uploader") or info.get("channel"),
                "caption": info.get("description"),
                "duration_s": info.get("duration"),
                "language": meta.language,
                "transcript": transcript,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    # 3. Stills. If this fails we still keep the transcript.
    try:
        n = save_frames(video, ROOT / "frames" / code)
        print(f"frames: {n} saved to {ROOT / 'frames' / code}")
    except Exception as e:
        print(f"frames: failed ({e})")

    # 4. Throw the video away: we only keep text and pictures.
    video.unlink(missing_ok=True)
    print(out_json)
    return 0


if __name__ == "__main__":
    sys.exit(main())

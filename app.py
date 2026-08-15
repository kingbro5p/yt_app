import os
import re
import subprocess

from flask import Flask, render_template, request, jsonify, Response, stream_with_context
import yt_dlp

app = Flask(__name__)

YDL_BASE_OPTS = {
    "quiet": True,
    "no_warnings": True,
    "skip_download": True,
    "noplaylist": True,
    "extract_flat": False,
}


def sanitize_filename(name: str) -> str:
    name = re.sub(r'[\\/*?:"<>|]', "", name or "video")
    return name.strip()[:150] or "video"


def format_duration(seconds):
    if not seconds:
        return None
    seconds = int(seconds)
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    if h:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/healthz")
def healthz():
    return jsonify({"status": "ok"})


@app.route("/api/info")
def api_info():
    url = (request.args.get("url") or "").strip()
    if not url:
        return jsonify({"error": "url প্যারামিটার দেওয়া হয়নি"}), 400

    try:
        with yt_dlp.YoutubeDL(YDL_BASE_OPTS) as ydl:
            info = ydl.extract_info(url, download=False)
    except Exception as e:
        return jsonify({"error": f"ভিডিও তথ্য আনা যায়নি: {str(e)}"}), 400

    if info.get("_type") == "playlist":
        return jsonify({"error": "এই লিংকটি একটি প্লেলিস্ট। অনুগ্রহ করে একটি একক ভিডিওর লিংক দিন।"}), 400

    seen_res = set()
    formats = []
    for f in info.get("formats", []):
        height = f.get("height")
        vcodec = f.get("vcodec")
        if not height or vcodec in (None, "none"):
            continue
        label = f"{height}p"
        if label in seen_res:
            continue
        seen_res.add(label)
        size = f.get("filesize") or f.get("filesize_approx")
        formats.append({
            "format_id": f.get("format_id"),
            "resolution": label,
            "height": height,
            "ext": "mp4",
            "has_audio": f.get("acodec") not in (None, "none"),
            "filesize_mb": round(size / (1024 * 1024), 1) if size else None,
        })

    formats.sort(key=lambda x: x["height"], reverse=True)

    audio_size = None
    for f in info.get("formats", []):
        if f.get("vcodec") in (None, "none") and f.get("acodec") not in (None, "none"):
            s = f.get("filesize") or f.get("filesize_approx")
            if s:
                audio_size = round(s / (1024 * 1024), 1)
                break

    return jsonify({
        "id": info.get("id"),
        "title": info.get("title"),
        "thumbnail": info.get("thumbnail"),
        "duration": format_duration(info.get("duration")),
        "uploader": info.get("uploader"),
        "webpage_url": info.get("webpage_url") or url,
        "formats": formats,
        "audio_size_mb": audio_size,
    })


@app.route("/api/download")
def api_download():
    url = (request.args.get("url") or "").strip()
    format_id = (request.args.get("format_id") or "").strip()
    mode = (request.args.get("mode") or "video").strip()  # "video" or "audio"

    if not url:
        return jsonify({"error": "url প্যারামিটার দেওয়া হয়নি"}), 400

    try:
        with yt_dlp.YoutubeDL(YDL_BASE_OPTS) as ydl:
            info = ydl.extract_info(url, download=False)
    except Exception as e:
        return jsonify({"error": f"ভিডিও তথ্য আনা যায়নি: {str(e)}"}), 400

    title = sanitize_filename(info.get("title", "video"))

    if mode == "audio":
        fmt = "bestaudio/best"
        out_ext = "mp3"
        cmd = [
            "yt-dlp", "--no-warnings", "--quiet", "--no-progress",
            "-f", fmt,
            "-x", "--audio-format", "mp3",
            "-o", "-",
            url,
        ]
        mimetype = "audio/mpeg"
    else:
        fmt = f"{format_id}+bestaudio/best" if format_id else "bestvideo[height<=720]+bestaudio/best[height<=720]/best"
        out_ext = "mp4"
        cmd = [
            "yt-dlp", "--no-warnings", "--quiet", "--no-progress",
            "-f", fmt,
            "--merge-output-format", "mp4",
            "-o", "-",
            url,
        ]
        mimetype = "video/mp4"

    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)

    def generate():
        try:
            while True:
                chunk = process.stdout.read(256 * 1024)
                if not chunk:
                    break
                yield chunk
        finally:
            try:
                process.stdout.close()
            except Exception:
                pass
            process.wait()

    filename = f"{title}.{out_ext}"
    return Response(
        stream_with_context(generate()),
        mimetype=mimetype,
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Cache-Control": "no-store",
        },
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)

# ReelGrab — YouTube ভিডিও ডাউনলোডার (ওয়েব ভার্সন)

মূল CLI স্ক্রিপ্ট (`downloader.py`) থেকে বানানো একটি Flask ওয়েব অ্যাপ। ইউজার একটি YouTube লিংক দিলে ভিডিওর প্রিভিউ (থাম্বনেইল, শিরোনাম, রেজোলিউশন লিস্ট) দেখায় এবং প্রতিটি রেজোলিউশনের জন্য আলাদা ডাউনলোড বাটন থাকে। MP3 (শুধু অডিও) ডাউনলোডও করা যায়।

## ফোল্ডার স্ট্রাকচার

```
app.py                  → Flask সার্ভার (info + download API)
templates/index.html    → মূল পেজ
static/css/style.css    → ফিল্মস্ট্রিপ থিম ডিজাইন
static/js/script.js     → ফ্রন্টএন্ড লজিক
requirements.txt        → Python ডিপেন্ডেন্সি
Procfile                → Railway/Heroku স্টার্ট কমান্ড
nixpacks.toml           → Railway বিল্ডে ffmpeg ইনস্টল করার জন্য
railway.json            → Railway ডিপ্লয় কনফিগ
```

## API

- `GET /api/info?url=<youtube_url>` — JSON রিটার্ন করে: `title`, `thumbnail`, `duration`, `uploader`, `formats[]` (প্রতিটিতে `resolution`, `format_id`, `filesize_mb`)।
- `GET /api/download?url=<youtube_url>&format_id=<id>&mode=video` — সিলেক্ট করা রেজোলিউশনে ভিডিও ফাইল স্ট্রিম করে ডাউনলোড করায় (mp4, সার্ভারে ffmpeg দিয়ে ভিডিও+অডিও merge হয়ে সরাসরি ব্রাউজারে পাঠানো হয়, ডিস্কে সেভ হয় না)।
- `GET /api/download?url=<youtube_url>&mode=audio` — শুধু অডিও (mp3)।

চাইলে হোমপেজেও `url` কোয়েরি প্যারামিটার দিয়ে সরাসরি লোড করা যায়, যেমন:

```
https://your-app.up.railway.app/?url=https://www.youtube.com/watch?v=xxxxxxxx
```

এই লিংকে ঢুকলেই পেজ অটোমেটিক ভিডিওটার তথ্য টেনে এনে দেখাবে (নিচে ডাউনলোড বাটনসহ)।

## লোকালি রান করা

```bash
pip install -r requirements.txt
# ffmpeg ইনস্টল থাকা লাগবে (video+audio merge করার জন্য):
# Ubuntu/Debian: sudo apt install ffmpeg
# macOS: brew install ffmpeg
python app.py
```

তারপর ব্রাউজারে `http://localhost:5000` খুলুন।

## Railway-তে ডিপ্লয়

1. এই ফোল্ডারটা একটা GitHub রিপোতে পুশ করুন।
2. Railway-তে গিয়ে **New Project → Deploy from GitHub repo** সিলেক্ট করে রিপোটা কানেক্ট করুন।
3. Railway `nixpacks.toml` দেখে Python + ffmpeg দুটোই ইনস্টল করবে, এবং `Procfile` দেখে `gunicorn` দিয়ে সার্ভার চালু করবে — কোনো এক্সট্রা কনফিগ লাগবে না।
4. ডিপ্লয় শেষে Railway একটা পাবলিক URL দেবে (Settings → Networking → Generate Domain), যেমন `https://reelgrab-production.up.railway.app`।
5. ওই URL-এ গিয়ে টেস্ট করুন, অথবা `?url=` প্যারামিটার দিয়ে API-এর মতো কল করুন।

## জরুরি নোট

- **কপিরাইট:** এই টুল দিয়ে যা ডাউনলোড করবেন তার স্বত্বাধিকার আপনার নিজের দায়িত্বে যাচাই করে নিতে হবে — YouTube-এর Terms of Service অনুযায়ী বেশিরভাগ কনটেন্ট ডাউনলোড করা নিষেধ, শুধুমাত্র ব্যক্তিগত/ফেয়ার-ইউজ ক্ষেত্রে সতর্কতার সাথে ব্যবহার করুন।
- **YouTube থ্রটলিং/ব্লক:** YouTube মাঝেমধ্যে সার্ভার IP থেকে আসা রিকোয়েস্ট ব্লক বা রেট-লিমিট করতে পারে (Railway-র শেয়ার্ড IP-এর কারণে)। এমন হলে `yt-dlp` আপডেট রাখা এবং প্রয়োজনে cookies/proxy সাপোর্ট যোগ করা লাগতে পারে।
- **স্টোরেজ:** ডাউনলোড সরাসরি স্ট্রিম হয়ে ইউজারের ব্রাউজারে যায়, সার্ভারের ডিস্কে ফাইল জমা থাকে না — তাই Railway-র ফ্রি/ছোট প্ল্যানেও স্টোরেজ নিয়ে সমস্যা হবে না।
- **প্লেলিস্ট:** আপাতত শুধু একক ভিডিও সাপোর্ট করে; প্লেলিস্ট লিংক দিলে এরর দেখাবে।

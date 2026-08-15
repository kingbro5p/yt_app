const form = document.getElementById("fetch-form");
const urlInput = document.getElementById("video-url");
const fetchBtn = document.getElementById("fetch-btn");
const errorMsg = document.getElementById("error-msg");
const resultSection = document.getElementById("result");
const loadingSection = document.getElementById("loading");

const thumbImg = document.getElementById("thumb-img");
const durationBadge = document.getElementById("duration-badge");
const titleEl = document.getElementById("video-title");
const uploaderEl = document.getElementById("video-uploader");
const formatList = document.getElementById("format-list");
const audioBtn = document.getElementById("audio-btn");

let currentUrl = "";

function showError(msg) {
  errorMsg.textContent = msg;
  errorMsg.hidden = false;
}

function clearError() {
  errorMsg.hidden = true;
  errorMsg.textContent = "";
}

function setLoading(isLoading) {
  fetchBtn.disabled = isLoading;
  fetchBtn.classList.toggle("loading", isLoading);
  loadingSection.hidden = !isLoading;
  if (isLoading) resultSection.hidden = true;
}

function formatSize(mb) {
  if (!mb) return "";
  if (mb >= 1024) return (mb / 1024).toFixed(1) + " GB";
  return mb.toFixed(0) + " MB";
}

async function fetchVideoInfo(videoUrl) {
  clearError();
  setLoading(true);
  try {
    const res = await fetch(`/api/info?url=${encodeURIComponent(videoUrl)}`);
    const data = await res.json();
    if (!res.ok) {
      throw new Error(data.error || "একটি সমস্যা হয়েছে।");
    }
    renderResult(videoUrl, data);
  } catch (err) {
    showError(err.message || "ভিডিও তথ্য আনা যায়নি। লিংকটি ঠিক আছে কিনা যাচাই করুন।");
  } finally {
    setLoading(false);
  }
}

function renderResult(videoUrl, data) {
  currentUrl = videoUrl;
  thumbImg.src = data.thumbnail || "";
  thumbImg.alt = data.title || "video thumbnail";
  durationBadge.textContent = data.duration || "";
  durationBadge.hidden = !data.duration;
  titleEl.textContent = data.title || "শিরোনাম পাওয়া যায়নি";
  uploaderEl.textContent = data.uploader ? `চ্যানেল: ${data.uploader}` : "";

  formatList.innerHTML = "";
  if (!data.formats || data.formats.length === 0) {
    formatList.innerHTML = `<p class="uploader">এই ভিডিওর জন্য কোনো ডাউনলোডযোগ্য ফরম্যাট পাওয়া যায়নি।</p>`;
  } else {
    data.formats.forEach((f) => {
      const row = document.createElement("div");
      row.className = "format-row";

      const info = document.createElement("div");
      info.className = "format-info";
      info.innerHTML = `<span class="format-res">${f.resolution}</span><span class="format-size">${formatSize(f.filesize_mb)}</span>`;

      const link = document.createElement("a");
      link.className = "download-link";
      link.textContent = "ডাউনলোড";
      link.href = `/api/download?url=${encodeURIComponent(videoUrl)}&format_id=${encodeURIComponent(f.format_id)}&mode=video`;

      row.appendChild(info);
      row.appendChild(link);
      formatList.appendChild(row);
    });
  }

  resultSection.hidden = false;
}

form.addEventListener("submit", (e) => {
  e.preventDefault();
  const videoUrl = urlInput.value.trim();
  if (!videoUrl) return;
  const params = new URLSearchParams(window.location.search);
  params.set("url", videoUrl);
  window.history.replaceState({}, "", `${window.location.pathname}?${params.toString()}`);
  fetchVideoInfo(videoUrl);
});

audioBtn.addEventListener("click", () => {
  if (!currentUrl) return;
  window.location.href = `/api/download?url=${encodeURIComponent(currentUrl)}&mode=audio`;
});

// Auto-load if ?url= is present in the address bar,
// e.g. https://your-app.up.railway.app/?url=https://youtu.be/xxxx
window.addEventListener("DOMContentLoaded", () => {
  const params = new URLSearchParams(window.location.search);
  const prefill = params.get("url");
  if (prefill) {
    urlInput.value = prefill;
    fetchVideoInfo(prefill);
  }
});

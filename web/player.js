/**
 * Watch-Cartoons – 2005-style YouTube player shell
 * Loads a video via ?v=VIDEO_ID (and optional title/channel query params).
 * Uses the modern YouTube iframe embed under a retro UI.
 * Classic Flash players from web archives no longer run in current browsers.
 */

(function () {
  "use strict";

  function qs(name) {
    var params = new URLSearchParams(window.location.search);
    return params.get(name) || "";
  }

  function $(id) {
    return document.getElementById(id);
  }

  var videoId = qs("v");
  var title = qs("title") || (videoId ? "YouTube Video" : "No video selected");
  var channel = qs("channel") || "";
  var published = qs("published") || "";

  var embedWrap = $("embed-wrap");
  var placeholder = $("stage-placeholder");
  var titleEl = $("video-title");
  var channelEl = $("channel-name");
  var publishedEl = $("published");
  var descEl = $("description");
  var progressFill = $("progress-fill");
  var timeDisplay = $("time-display");
  var btnPlay = $("btn-play");
  var btnMute = $("btn-mute");
  var btnFs = $("btn-fs");

  titleEl.textContent = decodeURIComponent(title);
  channelEl.textContent = channel ? decodeURIComponent(channel) : "Unknown channel";
  publishedEl.textContent = published ? decodeURIComponent(published).slice(0, 10) : "";
  descEl.textContent =
    qs("desc") ? decodeURIComponent(qs("desc")) : "Opened from Watch-Cartoons desktop app.";

  var player = null;
  var muted = false;
  var playing = false;
  var fakeProgress = 0;
  var progressTimer = null;

  function buildEmbed(id) {
    // youtube-nocookie embed, modest branding, related videos off where possible
    var src =
      "https://www.youtube-nocookie.com/embed/" +
      encodeURIComponent(id) +
      "?rel=0&modestbranding=1&enablejsapi=1";
    embedWrap.innerHTML =
      '<iframe id="yt-iframe" src="' +
      src +
      '" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>';
    embedWrap.style.display = "block";
    placeholder.style.display = "none";
    player = document.getElementById("yt-iframe");
  }

  function startFakeProgress() {
    stopFakeProgress();
    progressTimer = setInterval(function () {
      if (!playing) return;
      fakeProgress = Math.min(100, fakeProgress + 0.4);
      progressFill.style.width = fakeProgress + "%";
      var secs = Math.floor((fakeProgress / 100) * 180);
      var m = Math.floor(secs / 60);
      var s = secs % 60;
      timeDisplay.textContent =
        m + ":" + (s < 10 ? "0" : "") + s + " / 3:00";
    }, 500);
  }

  function stopFakeProgress() {
    if (progressTimer) {
      clearInterval(progressTimer);
      progressTimer = null;
    }
  }

  function togglePlay() {
    if (!videoId) {
      alert("No video ID. Open a video from the Watch-Cartoons app.");
      return;
    }
    if (!player) {
      buildEmbed(videoId);
    }
    playing = !playing;
    btnPlay.textContent = playing ? "❚❚" : "▶";
    if (playing) {
      startFakeProgress();
    } else {
      stopFakeProgress();
    }
  }

  function toggleMute() {
    muted = !muted;
    btnMute.textContent = muted ? "🔇" : "🔊";
  }

  function toggleFullscreen() {
    var stage = $("stage");
    if (!document.fullscreenElement) {
      if (stage.requestFullscreen) stage.requestFullscreen();
    } else if (document.exitFullscreen) {
      document.exitFullscreen();
    }
  }

  btnPlay.addEventListener("click", togglePlay);
  btnMute.addEventListener("click", toggleMute);
  btnFs.addEventListener("click", toggleFullscreen);

  $("progress-track").addEventListener("click", function (e) {
    var rect = e.currentTarget.getBoundingClientRect();
    var ratio = (e.clientX - rect.left) / rect.width;
    fakeProgress = Math.max(0, Math.min(100, ratio * 100));
    progressFill.style.width = fakeProgress + "%";
  });

  // Auto-load embed if v= is present
  if (videoId) {
    buildEmbed(videoId);
    playing = true;
    btnPlay.textContent = "❚❚";
    startFakeProgress();
  }
})();

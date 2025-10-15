// main.js

document.addEventListener('DOMContentLoaded', () => {
  const audio = document.getElementById('background-music');
  const muteBtn = document.getElementById('mute-btn');
  const volumeSlider = document.getElementById('volume-slider');

  // Play audio if stored in localStorage
  if (localStorage.getItem('musicPlaying') === 'true') {
    audio.play().catch(() => {});
  }

  // Play audio on first click or scroll (to satisfy browser autoplay policy)
  function playAudio() {
    if (audio.paused) {
      audio.play().catch(() => {});
      localStorage.setItem('musicPlaying', 'true');
    }
  }

  window.addEventListener('click', playAudio, { once: true });
  window.addEventListener('scroll', playAudio, { once: true });

  // Mute/unmute toggle
  muteBtn.addEventListener('click', () => {
    audio.muted = !audio.muted;
    muteBtn.textContent = audio.muted ? '🔇' : '🔊';
    localStorage.setItem('musicMuted', audio.muted ? 'true' : 'false');
  });

  // Volume slider control
  volumeSlider.addEventListener('input', () => {
    audio.volume = volumeSlider.value;
    audio.muted = audio.volume === 0;
    muteBtn.textContent = audio.muted ? '🔇' : '🔊';
    localStorage.setItem('musicVolume', audio.volume);
    localStorage.setItem('musicMuted', audio.muted ? 'true' : 'false');
  });

  // Load volume and mute state from localStorage
  const savedVolume = localStorage.getItem('musicVolume');
  const savedMuted = localStorage.getItem('musicMuted');

  if (savedVolume !== null) {
    audio.volume = parseFloat(savedVolume);
    volumeSlider.value = savedVolume;
  }

  if (savedMuted === 'true') {
    audio.muted = true;
    muteBtn.textContent = '🔇';
  } else {
    audio.muted = false;
    muteBtn.textContent = '🔊';
  }
});

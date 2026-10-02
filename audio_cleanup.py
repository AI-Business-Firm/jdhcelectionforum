from pathlib import Path
import subprocess
import numpy as np
import soundfile as sf
from scipy import signal, ndimage
import imageio_ffmpeg

source = Path('C:/Users/Nuffi/Downloads/Chorus of the Chesapeake.mp3')
out = Path('C:/Users/Nuffi/.codex/visualizations/2026/09/22/01a0c949-3bd6-7251-bc27-31396855187b/Howard-memorial-audio')
out.mkdir(parents=True, exist_ok=True)
ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
wav = out / 'gentle-cleanup.wav'
subprocess.run([ffmpeg, '-v', 'error', '-n', '-i', str(source), '-af',
    'highpass=f=55,afftdn=nr=7:nf=-40:tn=1:gs=8,volume=0.9',
    '-c:a', 'pcm_s24le', str(wav)], check=True)
x, sr = sf.read(wav, always_2d=True, dtype='float32')
f,t,z = signal.stft(x.T, fs=sr, nperseg=2048, noverlap=1536)
mag = np.sqrt(np.mean(np.abs(z)**2, axis=0))
# Reduce only bins with strong short-lived excess over their local baseline.
baseline = ndimage.median_filter(mag, size=(1, 61))
ratio = mag / (baseline + 1e-6)
band = (f > 700) & (f < 10000)
broad = np.mean(ratio[band] > 3, axis=0)
strength = np.clip((broad - .28) / .35, 0, 1)
excess = np.clip((ratio - 2) / 5, 0, 1)
mask = 1 - .55 * excess * strength[None, :]
mask[f < 250] = 1
mask = ndimage.gaussian_filter(mask, sigma=(1.2, 1.5))
_, y = signal.istft(z * mask[None, :, :], fs=sr, nperseg=2048, noverlap=1536)
y = y.T[:len(x)]
alt = out / 'softened-abrupt-noises.wav'
sf.write(alt, y, sr, subtype='PCM_24')
for p in [wav, alt]:
    target = p.with_suffix('.mp3')
    subprocess.run([ffmpeg, '-v', 'error', '-n', '-i', str(p), '-c:a', 'libmp3lame', '-b:a', '320k', str(target)], check=True)
    check, rate = sf.read(target, always_2d=True)
    assert rate == sr and len(check) == len(x) and np.isfinite(check).all()
    print(target, 'duration', len(check)/rate, 'peak', float(np.max(np.abs(check))))
print('Seconds with broad transient attenuation:', float(np.sum(strength > 0)*512/sr))

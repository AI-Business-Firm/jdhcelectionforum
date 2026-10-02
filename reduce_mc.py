from pathlib import Path
import subprocess
import numpy as np
import soundfile as sf
import imageio_ffmpeg

ff=imageio_ffmpeg.get_ffmpeg_exe()
src=Path('C:/Users/Nuffi/Downloads/Chorus of the Chesapeake.mp4')
out=Path('C:/Users/Nuffi/.codex/visualizations/2026/09/22/01a0c949-3bd6-7251-bc27-31396855187b/MC-reduced')
out.mkdir(parents=True,exist_ok=True)
raw=subprocess.run([ff,'-v','error','-i',str(src),'-map','0:a:0','-f','f32le','-ac','2','-ar','44100','-'],capture_output=True,check=True)
x=np.frombuffer(raw.stdout,dtype=np.float32).reshape(-1,2).copy()
sr=44100
n=49*sr
mid=np.mean(x[:n],axis=1)
side=(x[:n,0]-x[:n,1])/2
# Retain stereo differences; reduce common center by 16 dB.
gain=np.full(n,10**(-16/20),dtype=np.float32)
# Restore original audio over final 30 ms, ending exactly at 49 seconds.
fade=round(.03*sr)
gain[-fade:]=np.linspace(gain[0],1,fade)
y=x.copy()
y[:n,0]=gain*mid+side
y[:n,1]=gain*mid-side
assert np.array_equal(x[n:],y[n:])
assert np.max(np.abs(y))<=max(1.0,np.max(np.abs(x)))+.001
wav=out/'MC-reduced-audio.wav'
sf.write(wav,y,sr,subtype='FLOAT')
video=out/'Chorus of the Chesapeake - MC Reduced First 49 Seconds.mp4'
subprocess.run([ff,'-v','error','-n','-i',str(src),'-i',str(wav),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','256k','-movflags','+faststart',str(video)],check=True)
subprocess.run([ff,'-v','error','-n','-i',str(wav),'-ss','25','-t','30','-c:a','libmp3lame','-b:a','256k',str(out/'Preview - Original 0m25s to 0m55s.mp3')],check=True)
subprocess.run([ff,'-v','error','-i',str(video),'-f','null','-'],check=True)
print(video)
print('Audio samples:',len(y),'Seconds:',len(y)/sr,'Audio after 49 seconds identical before encoding:',np.array_equal(x[n:],y[n:]))

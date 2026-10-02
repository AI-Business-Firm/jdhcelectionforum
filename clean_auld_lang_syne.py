from pathlib import Path
import subprocess,json,re
import soundfile as sf
import imageio_ffmpeg
ff=imageio_ffmpeg.get_ffmpeg_exe()
src=Path('C:/Users/Nuffi/OneDrive/Desktop/OPA MUSIC/Auld Lang Syne - Trimmed Chorus of the Chesapeake.mp3')
out=Path('C:/Users/Nuffi/.codex/visualizations/2026/09/22/01a0c949-3bd6-7251-bc27-31396855187b/Howard-memorial-audio')
out.mkdir(parents=True,exist_ok=True)
base='highpass=f=50,afftdn=nr=5:nf=-45:tn=1:gs=10'
def measure(path, filters):
    r=subprocess.run([ff,'-hide_banner','-i',str(path),'-af',filters+',loudnorm=I=-16:TP=-2:LRA=11:print_format=json','-f','null','-'],capture_output=True,text=True,check=True)
    return json.loads(re.findall(r'\{[^{}]+\}',r.stderr)[-1])
m=measure(src,base)
norm=f"loudnorm=I=-16:TP=-2:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=false"
wav=out/'Auld Lang Syne - Cleaned and Louder.wav'
mp3=wav.with_suffix('.mp3')
subprocess.run([ff,'-v','error','-n','-i',str(src),'-af',base+','+norm,'-ar','44100','-c:a','pcm_s24le',str(wav)],check=True)
subprocess.run([ff,'-v','error','-n','-i',str(wav),'-c:a','libmp3lame','-b:a','320k',str(mp3)],check=True)
info=sf.info(mp3)
assert abs(info.duration-sf.info(src).duration)<.05
result=measure(mp3,'anull')
print('Duration:',info.duration,'Loudness:',result['input_i'],'True peak:',result['input_tp'])
print(mp3)
assert float(result['input_tp'])<0

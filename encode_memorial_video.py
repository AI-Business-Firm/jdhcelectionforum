from pathlib import Path
import subprocess
import imageio_ffmpeg
out = Path('C:/Users/Nuffi/.codex/visualizations/2026/09/22/01a0c949-3bd6-7251-bc27-31396855187b/Armed-Forces-Video')
audio = out.parent/'Howard-memorial-audio/The Vocal Majority - Armed Forces Medley - 3 Minutes.mp3'
durations = [5,35,29,36,29,30,16]
manifest = out/'slides.txt'
manifest.write_text(''.join(f"file 'slide-{i}.png'\nduration {d}\n" for i,d in enumerate(durations))+"file 'slide-6.png'\n")
ff = imageio_ffmpeg.get_ffmpeg_exe()
video = out/'Armed Forces Medley - Howard Hackman.mp4'
subprocess.run([ff,'-v','error','-n','-f','concat','-safe','0','-i',str(manifest),'-i',str(audio),'-map','0:v:0','-map','1:a:0','-t','180','-r','30','-c:v','libx264','-preset','veryfast','-tune','stillimage','-crf','19','-pix_fmt','yuv420p','-c:a','aac','-b:a','320k','-movflags','+faststart',str(video)],check=True)
subprocess.run([ff,'-hide_banner','-i',str(video),'-f','null','-'],check=True,stdout=subprocess.DEVNULL,stderr=(out/'validation.txt').open('w'))
print(video)

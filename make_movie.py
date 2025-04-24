from moviepy import *
from moviepy.video.tools.subtitles import SubtitlesClip

def create_black_background_video(audio_file, srt_file, output_video_file):
    
    # CRIANDO VIDEO FUNDO PRETO COM DURAÇÃO DO AUDIO
    audio = AudioFileClip(audio_file)
    video = ColorClip(size=(1080, 720), color=(0, 0, 0), duration=audio.duration)
    final_video = video.with_audio(audio)

    # CRIANDO LEGENDAS
    def make_textclip(txt):
                return TextClip(
                    font='/usr/share/fonts/truetype/ubuntu/Ubuntu-B.ttf',
                    text=txt,
                    font_size=40,
                    color="#ffffff",
                    stroke_color="#000000",
                    stroke_width=6,
                    text_align="center",
                    horizontal_align="center",
                    vertical_align="bottom",
                    bg_color=(0, 0, 0, 0),
                    size=(1080, 150),
                    method="caption",
                )
    subtitles = SubtitlesClip(subtitles=srt_file, make_textclip=make_textclip, encoding="utf-8")

    # VIDEO FINAL
    final_video = CompositeVideoClip([final_video, subtitles.with_position("center","bottom")])
    final_video.write_videofile(output_video_file, fps=24,  remove_temp=True, codec="libx264", audio_codec="aac")

# audio_file = "02_audios/d0519820-f844-453f-b7e1-3acb99f45c0e.wav"
# srt_file = "output_english.srt" 
# output_video_file = f"01_videos/video_{audio_file.replace('audios/', '').replace(".wav", "")}.mp4"
# create_black_background_video(audio_file, srt_file, output_video_file)
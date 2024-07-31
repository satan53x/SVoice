import os
import re
import gradio as gr
from funasr.utils.postprocess_utils import rich_transcription_postprocess
from moviepy.editor import VideoFileClip
from utils_text import *
from sense_voice import model
#from paraformer import model

video_formats = {
	'.mp4', '.avi', '.mov', '.mkv', '.flv', '.webm', 
	'.wmv', '.m4v', '.mpeg', '.mpg', '.3gp', '.ogg'
}
audio_formats = {
	'.mp3', '.aac', '.wav', '.flac', '.m4a', 
	'.wma', '.opus', '.aiff', '.alac', '.ogg'
}
subtitle_formats = {
	'.srt',
}

#-------------------------------------------------------------
def audio_to_srt(file_path):
	srt_path = os.path.splitext(file_path)[0] + ".srt"
	if os.path.isfile(srt_path):
		print(f"字幕文件已存在: {srt_path}")
		srt_path = srt_to_srt(srt_path)
		return srt_path
	print('开始处理音频文件: ' + file_path)
	res = model.generate(
		input=f"{file_path}",
		cache={},
		language="ja",  # "auto", "zh", "en", "yue", "ja", "ko", "nospeech"
		use_itn=True,
		batch_size_s=120,
		ban_emo_unk=True,
	)
	print('开始处理文本和时间戳')
	lines, lines_timestamp = text_postprocess(res[0]["text"], res[0]["timestamp"])
	#print(lines, lines_timestamp)
	#合并
	lines, lines_timestamp = merge_close_lines(lines, lines_timestamp)
	create_srt(lines, lines_timestamp, srt_path)
	print(f"保存字幕文件: {srt_path}")
	return srt_path

def srt_to_srt(srt_path):
	lines, lines_timestamp = read_srt(srt_path)
	srt_path = os.path.splitext(srt_path)[0] + ".new.srt"
	#合并
	lines, lines_timestamp = merge_close_lines(lines, lines_timestamp)
	create_srt(lines, lines_timestamp, srt_path)
	print(f"保存字幕文件: {srt_path}")
	return srt_path

def video_to_audio(video_path):
	audio_path = os.path.splitext(video_path)[0] + ".mp3"
	if os.path.isfile(audio_path):
		return audio_path
	video_clip = VideoFileClip(video_path)
	video_clip.audio.write_audiofile(audio_path)
	return audio_path

def file_to_srt(filepath):
	_, ext = os.path.splitext(filepath)
	if ext.lower() in video_formats:
		audio_path = video_to_audio(filepath)
		srt_path = audio_to_srt(audio_path)
	elif ext.lower() in audio_formats:
		srt_path = audio_to_srt(filepath)
	elif ext.lower() in subtitle_formats:
		srt_path = srt_to_srt(srt_path)
	else:
		srt_path = "不支持的文件格式"
	return srt_path

def process_files(inputStr):
	lst = re.split(r"[\r\n]+", inputStr)
	out = []
	for filepath in lst:
		ret = file_to_srt(filepath)
		out.append(ret)
	return "\n".join(out)

local_app = gr.Interface(
	fn=process_files, 
	inputs=[
		gr.Textbox(lines=3, placeholder=r"输入文件路径", interactive=True),
	], 
	outputs=[
		gr.Textbox(lines=3, interactive=False)
	]
)
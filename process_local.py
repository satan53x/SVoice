import os
import re
import time
import traceback
import gradio as gr
from funasr.utils.postprocess_utils import rich_transcription_postprocess
from moviepy.editor import VideoFileClip
from utils_text import *
from variable import Var

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
		return srt_path
	# --------------------------
	print('开始处理音频文件: ' + file_path)
	start = time.time()
	Var.init_model()
	if not Var.model:
		print("模型加载失败")
		return "模型加载失败"
	print('使用模型: ' + Var.name)
	res = Var.model.generate(
		input=f"{file_path}",
		cache={},
		language=Var.language, 
		use_itn=True,
		batch_size_s=120,
		ban_emo_unk=True,
	)
	end = time.time()
	print(f"音频转文本耗时: {end-start:.3f} s")
	# --------------------------
	print('开始处理文本和时间戳')
	lines, lines_timestamp = text_postprocess(res[0]["text"], res[0]["timestamp"])
	#print(lines, lines_timestamp)
	create_srt(lines, lines_timestamp, srt_path)
	print(f"保存字幕文件: {srt_path}")
	return srt_path

def srt_to_srt(srt_path):
	lines, lines_timestamp = read_srt(srt_path)
	srt_path = os.path.splitext(srt_path)[0] + ".new.srt"
	#合并
	lines, lines_timestamp = merge_close_lines(lines, 
		lines_timestamp, 
		max_gap=Var.config['max_gap'], 
		max_duration=Var.config['max_duration'], 
		max_char_len=Var.config['max_char_len'], 
		delay_when_gap=Var.config['delay_when_gap'], 
		ahead_when_gap=Var.config['ahead_when_gap'], 
		remove_end_punc=Var.config['remove_end_punc'],
		merge_str=Var.config['merge_str'],
	)
	create_srt(lines, lines_timestamp, srt_path)
	print(f"保存字幕文件: {srt_path}")
	return srt_path

def video_to_audio(video_path):
	audio_path = os.path.splitext(video_path)[0] + ".mp3"
	if os.path.isfile(audio_path):
		return audio_path
	video_clip = VideoFileClip(video_path)
	start = time.time()
	video_clip.audio.write_audiofile(audio_path)
	end = time.time()
	print(f"视频转音频耗时: {end-start:.3f} s")
	return audio_path

def file_to_srt(filepath):
	_, ext = os.path.splitext(filepath)
	if ext.lower() in video_formats:
		audio_path = video_to_audio(filepath)
		srt_path = audio_to_srt(audio_path)
		if Var.merge_short:
			srt_path = srt_to_srt(srt_path)
	elif ext.lower() in audio_formats:
		srt_path = audio_to_srt(filepath)
		if Var.merge_short:
			srt_path = srt_to_srt(srt_path)
	elif ext.lower() in subtitle_formats:
		#srt_path = srt_to_srt(srt_path)
		srt_path = ""
	else:
		srt_path = "不支持的文件格式: " + filepath
	return srt_path

def process_files(*args):
	yield gr.update(interactive=False, value="处理中..."), gr.update(value="")
	Var.init_args(args)
	files = parse_files(args[0])
	results = ''
	for i, filepath in enumerate(files):
		try:
			result = file_to_srt(filepath)
		except Exception as e:
			#print(e)
			traceback.print_exc()
			result = '处理失败: ' + filepath
		if not result:
			continue
		results += result
		if i + 1 < len(files):
			results += '\n'
			yield gr.update(), gr.update(value=results)
	yield gr.update(interactive=True, value="处理完成，继续进行提取"), results

def parse_files(text):
	files = []
	lst = re.split(r"[\r\n]+", text)
	for s in lst:
		if os.path.isfile(s):
			#文件
			files.append(s)
		elif os.path.isdir(s):
			#目录
			for t in os.listdir(s):
				path = os.path.join(s, t)
				if os.path.isfile(path):
					files.append(path)
	return files

#-------------------------------------------------------------
# app_interface = gr.Interface(
# 	fn=process_files, 
# 	inputs=[
# 		gr.Textbox(lines=3, placeholder=r"输入文件路径", interactive=True),
# 	], 
# 	outputs=[
# 		gr.Textbox(lines=3, interactive=False)
# 	]
# )

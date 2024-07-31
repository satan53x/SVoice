import re

text_split_pattern = re.compile(r" ?<[^>]+>")

def text_postprocess(text, timestamps, remove_end_punc=True):
	#清除控制代码并分割
	textList = text_split_pattern.split(text)
	start = 0
	lines = []
	lines_timestamp = []
	for line in textList:
		if line == "":
			continue
		#时间戳
		end = start + len(line) - 1
		lines_timestamp.append([timestamps[start][0], timestamps[end][1]])
		start = end + 1
		#文本
		if remove_end_punc:
			line = line.rstrip("。！.!")
		if line == "":
			line = " "
		lines.append(line)
	return lines, lines_timestamp

#合并时间接近的短句
def merge_close_lines(texts, timestamps, max_gap=1000, max_duration=5000, max_char_len=20, delay_when_gap=1000):
	merged_texts = []
	merged_timestamps = []
	i = 0
	while i < len(texts):
		current_text = texts[i]
		current_start, current_end = timestamps[i]
		while i + 1 < len(texts):
			next_start, next_end = timestamps[i + 1]
			gap = next_start - current_end
			if gap > max_gap or next_end - current_start > max_duration:
				#时间不匹配
				break
			if len(current_text) + len(texts[i + 1]) > max_char_len:
				#字数太多
				break
			# 合并当前字幕和下一个字幕
			current_text += "  " + texts[i + 1]
			current_end = next_end
			i += 1
		if delay_when_gap:
			current_end += delay_when_gap
			if i+1 < len(texts) and current_end > next_start:
				current_end = next_start - 100
		merged_texts.append(current_text)
		merged_timestamps.append((current_start, current_end))
		i += 1
	return merged_texts, merged_timestamps

# --------------------------------------------------------------
def create_srt(texts, timestamps, output_file):
	with open(output_file, 'w', encoding='utf-8') as f:
		for i, (text, timestamp) in enumerate(zip(texts, timestamps), 1):
			start_time = ms_to_srt_time(timestamp[0])
			end_time = ms_to_srt_time(timestamp[1])
			f.write(f"{i}\n")
			f.write(f"{start_time} --> {end_time}\n")
			f.write(f"{text}\n\n")

def ms_to_srt_time(timestamp_ms):
	timestamp_s = timestamp_ms // 1000
	hours, remainder = divmod(timestamp_s, 3600)
	minutes, seconds = divmod(remainder, 60)
	milliseconds = int(timestamp_ms % 1000)
	return f"{hours:02d}:{minutes:02d}:{int(seconds):02d},{milliseconds:03d}"

def read_srt(file_path):
	texts = []
	timestamps = []
	with open(file_path, 'r', encoding='utf-8') as file:
		content = file.read()
	# 分割每个字幕块
	subtitle_blocks = re.split(r'\n\n', content.strip())
	for block in subtitle_blocks:
		lines = block.split('\n')
		if len(lines) >= 3:  # 确保有时间戳和文本
			# 提取时间戳
			time_line = lines[1]
			start_time, end_time = time_line.split(' --> ')
			start_ms = srt_time_to_ms(start_time)
			end_ms = srt_time_to_ms(end_time)
			# 提取文本
			text = ' '.join(lines[2:])
			timestamps.append((start_ms, end_ms))
			texts.append(text)
	return texts, timestamps

def srt_time_to_ms(time_str):
	hours, minutes, seconds, milliseconds = time_str.replace(',', ':').split(':')
	return int(hours) * 3600000 + int(minutes) * 60000 + int(seconds) * 1000 + int(milliseconds)


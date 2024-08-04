# Set the device with environment, default is cuda:0
# export SENSEVOICE_DEVICE=cuda:1
import threading
import time
import webbrowser
from fastapi import FastAPI
import gradio as gr
import requests
from process_local import process_files
from variable import Var

def get_blocks():
	Var.load_config()
	with gr.Blocks() as app_blocks: 
		gr.Markdown("视频/音频转字幕")

		with gr.Row():
			input_files = gr.Textbox(lines=5, label="文件路径（支持文件夹）", placeholder="每行对应一个文件", interactive=True)

		with gr.Row():
			output_files = gr.Textbox(lines=5, label="结果", interactive=False)

		with gr.Row():
			name_nostamp = gr.Textbox(label="无时间戳模型", value=Var.name_nostamp, interactive=True)
			process_button = gr.Button("开始转换")

		with gr.Row():
			op_language = gr.Textbox(label="目标语言", value=Var.language)
			op_merge_short = gr.Checkbox(label="是否合并短句", value=Var.merge_short)
		
		process_button.click(
			fn=process_files,
			inputs=[input_files, name_nostamp, op_language, op_merge_short],
			outputs=[process_button, output_files]
		)
	return app_blocks

# --------------------------------------------------------------------
app = FastAPI()
local_app = get_blocks()
app = gr.mount_gradio_app(app, local_app, path=r"/")
local_app.queue()

def open_browser():
	url = "http://127.0.0.1:8600"
	while True:
		try:
			response = requests.get(url)
			if response.status_code == 200:
				webbrowser.open_new(url)
				break
		except requests.exceptions.ConnectionError:
			time.sleep(0.5)

if __name__ == "__main__":
	import uvicorn
	threading.Thread(target=open_browser).start()
	#uvicorn.run("run_web:app", host="127.0.0.1", port=8600, reload=True)
	uvicorn.run(app, host="127.0.0.1", port=8600)
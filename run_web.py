# Set the device with environment, default is cuda:0
# export SENSEVOICE_DEVICE=cuda:1
import threading
import time
import webbrowser
from fastapi import FastAPI, File, Form, UploadFile
import gradio as gr
import requests
from process_local import local_app



#-------------------------------------------------------------
app = FastAPI()
app = gr.mount_gradio_app(app, local_app, path=r"/")

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
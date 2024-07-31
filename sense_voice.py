import os
#from SenseVoice.model import SenseVoiceSmall
#from funasr import AutoModel
from auto_model import AutoModel

def create_model(model_dir="iic/SenseVoiceSmall"):
	model = AutoModel(
		model=model_dir,
		trust_remote_code=False,
		#remote_code="./SenseVoice/model.py",  
		vad_model="fsmn-vad",
		vad_kwargs={"max_single_segment_time": 30000},
		device="cuda:0",
		vad_timestamp=True,
	)
	return model

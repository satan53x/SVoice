from funasr import AutoModel

model_dir = "paraformer-zh"
model = AutoModel(
	model=model_dir,
	vad_model="fsmn-vad",
	vad_kwargs={"max_single_segment_time": 30000},
	device="cuda:0",
	sentence_timestamp=True,
)

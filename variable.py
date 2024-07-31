#import yaml
from ruamel.yaml import YAML
yaml = YAML()

class variable():
	#config
	config = {}
	language = 'ja' # auto, zh, en, yue, ja, ko, nospeech
	merge_short = True #合并短句
	name_nostamp = 'iic/SenseVoiceSmall' #无时间戳模型名
	name_stamp = '' #有时间戳模型名
	#var
	model = None #当前模型
	model_nostamp = None #当前无时间戳模型
	name = '' #当前模型名

	def init_args(self, args):
		self.name_nostamp = args[1]
		self.name_stamp = ''
		self.language = args[2]
		self.merge_short = args[3]
		self.save_config()

	def init_model(self):
		if self.name_nostamp:
			#无时间戳模型
			if not self.model_nostamp or self.name != self.name_nostamp:
				self.name = self.name_nostamp
				from sense_voice import create_model
				self.model_nostamp = create_model(self.name)
				self.model = self.model_nostamp
	
	def load_config(self):
		with open('config.yaml', 'r', encoding='utf-8') as file:
			self.config = yaml.load(file)
			self.language = self.config['language']
			self.merge_short = self.config['merge_short']
			self.name_nostamp = self.config['model_name_nostamp']

	def save_config(self):
		with open('config.yaml', 'w', encoding='utf-8') as file:
			self.config['language'] = self.language
			self.config['merge_short'] = self.merge_short
			self.config['model_name_nostamp'] = self.name_nostamp
			yaml.dump(self.config, file)

# ----------------------------------
Var = variable()
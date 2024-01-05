import os


TELEGRAM_TOKEN = os.environ['TELEGRAM_TOKEN']

APP_HOST = os.environ['APP_HOST']
APP_PORT = int(os.environ['APP_PORT'])

MODEL_NAME = os.environ['MODEL_NAME']
TOKENIZER_NAME = os.environ['TOKENIZER_NAME']

MODEL_SEED = int(os.environ['MODEL_SEED'])
HF_TOKEN = os.environ['HF_TOKEN']
OFFLOAD_FOLDER_NAME = os.environ['OFFLOAD_FOLDER_NAME']
MAX_COUNT_ATTEMPTS_TO_GENERATE_UNIQ_ANSWER = int(os.environ['MAX_COUNT_ATTEMPTS_TO_GENERATE_UNIQ_ANSWER'])
USE_WANDB = True if os.environ['USE_WANDB'] == "True" else False
WANDB_TOKEN  = os.environ['WANDB_TOKEN']


POSTGRESQL_HOST  = os.environ['POSTGRESQL_HOST']
POSTGRESQL_DB_NAME = os.environ['POSTGRESQL_DB_NAME']
POSTGRESQL_USER = os.environ['POSTGRESQL_USER']
POSTGRESQL_PASSWORD = os.environ['POSTGRESQL_PASSWORD']
POSTGRESQL_TABLE_NAME = os.environ['POSTGRESQL_TABLE_NAME']



TEMPERATURE = float(os.environ['TEMPERATURE'])
QUANT_BITS = int(os.environ['QUANT_BITS'])
MAX_NEW_TOKENS = int(os.environ['MAX_NEW_TOKENS'])
TOP_P = float(os.environ['TOP_P'])
TOP_K = float(os.environ['TOP_K'])


SIMILARITY_THRESHOLD = float(os.environ['SIMILARITY_THRESHOLD'])






















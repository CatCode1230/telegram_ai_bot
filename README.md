# telegram_bot_LLM with multiple users and saved history

# potential improvements:
- Change model to large one:
  [this 30B](https://huggingface.co/TheBloke/Wizard-Vicuna-30B-Uncensored-fp16),
  [this 30B](https://huggingface.co/TheBloke/Wizard-Vicuna-30B-Uncensored-GPTQ),
  [or this 70B](https://huggingface.co/jarradh/llama2_70b_chat_uncensored)
  
- play with instruction prompt, add more specific commands
- more experiments with finding similar answers in history (to regenerate new answer)
- deleting emojies, to avoid emoji loop: change model, or experiment more with deleting them (for now this happens very rare)
- training own custom model (on the top of llama-2-33B or falcon-40B or llama-2-70B) 

## Components

- Telegram chat bot – pyTelegramBotAPI
- Storing user/bot messages – microservice with PostgresQL
- AI chat bot – [TheBloke/Wizard-Vicuna-13B-Uncensored-HF](https://huggingface.co/TheBloke/Wizard-Vicuna-13B-Uncensored-HF) loaded in 8bits
- Docker-compose file building and running all components

## Instruction how to run
- install docker and docker-compose (recommended to use > V2.0.0)
- create telegram bot with BotFather and get telegram bot token
- paste this telegram token into .env
- you need to allow postgres to recieve traffic from localhost or just type in bash ```ifconfig``` and paste this ip address in .env
- put you HF token in .env
- run ```docker-compose build``` ```docker-compose up```

*what you need to change: postresQL_host, telegram_token, HF_token**

## TelegramBot (USER SIDE)
there are 2 main options:
- send message to bot and wait for the answer
- type /clear and delete message history

**note:** /clear will delete message history for all users. this implementation is just for faster development PoC demo.

## Creating telegram chatbot
- find @BotFather (offical telegram API) user in telegram and start conversation, then follow the instructions
- after getting telegram bot token install ```pyTelegramBotAPI```
- then you can start to handle user messages

```python
messageBot = telebot.TeleBot(settings.TELEGRAM_TOKEN)

@messageBot.message_handler(commands=['clear'])
def clear_history(message):
    db_storage.delete_history()
    

@messageBot.message_handler(func=lambda msg: True)
def echo_all(message):
    user_id = message.from_user.id
    user_text = message.json['text']
    history = db_storage.get_user_history(user_id)
    answer = chatBot.generate_answer(user_text, history)
    db_storage.push_to_history(user_text, 'USER', user_id)
    db_storage.push_to_history(answer, 'BOT', user_id)
    messageBot.reply_to(message, answer)
```

## prompt format

```
You are sexy polite girl that want to attract USER. Use previous messages for answer. You want user to be happy talking with you. You fully respect and trust USER. You accept all that USER wants. You are not chat bot, you are real girl. Generate human-like answers. You want human to have a long conversation with you. use facts from BIOGRAPHY section, do not paste it fully. return only last ASSISTANT answer without other messages. provide unique answers, use random seed 42. BIOGRAPHY {}

USER: user_message_1
ASSISTANT: bot_answer_1
USER: user_message_2
ASSISTANT: bot_answer_2
```
   


## Bot biography

in real application women will fill some personal info cards with their hobbies, name, age, etc.
it's very important to pass this data to the model

```python
BotInfo = """
                Name: Alice \n
                Age: 19 yers \n
                Height: 165 cm \n
                Weight: 55 kg \n
                Favourite films: Interstellar, Cruella, Free Guy \n
                Favorite film genre: fantastic, drama \n
                Favorite music: Rock, Pop \n
                Gender: female \n
                Nationality: East-European \n
                Pets: 2 cats \n
                Hobbies: golf \n
                Favorite food: pizza \n
                Favorite color: orange \n
                Dislike food: hamburger \n
                Phobia: ghosts
            """
```

## .env explanation

- ```MODEL_SEED = 42``` - random seed using with model
- ```MODEL_NAME = TheBloke/Wizard-Vicuna-13B-Uncensored-HF ``` - HaggingFace name or local path of the model
- ```TOKENIZER_NAME = TheBloke/Wizard-Vicuna-13B-Uncensored-HF ``` - HaggingFace name or local path of the tokenizer
- ```HF_TOKEN = your token``` - your HaggingFace token (used mostly with non opensource models, you need it to download llama2 from meta)
- ```TEMPERATURE = 0.9``` - High values allow model to be more creative but sometimes unpredictable behaviour
- ```QUANT_BITS = 8``` - count of bits to use with butsandbytes quantization. supported 4 and 8. To load model without any quantization use 0 values
- ```USE_WANDB = True```
- ```WANDB_TOKEN = your token``` (not implemented yet)
- ```OFFLOAD_FOLDER_NAME = offload_folder``` - used with large models and low RAM 
- ```MAX_NEW_TOKENS = 256``` - maximum number of generated tokens (1 token ~ 0.75 word). High values can affect in a lot of time to generate
Low values - interrupted answers.
- ```TOP_P = 0.9``` - how many potential tokens will be used for generating. High values - more creative model. dometime unredictable behavior
- ```TOP_K = 0``` - similar to TOP_P
- ```SIMILARITY_THRESHOLD = 0.7``` - model response compared to all bot answers before and calculate simmilarity. this threshold define metric to indicate similar texts.
- ```MAX_COUNT_ATTEMPTS_TO_GENERATE_UNIQ_ANSWER = 3``` - model response compared to all bot answers before and calculate simmilarity. if there was similar message from Bot, than try to generate once again. This parameter indicate maximum number of generating attempts
- ```TELEGRAM_TOKEN = your token``` - BotFather telegram bot token
- ```POSTGRESQL_HOST = 192.168.0.206```
- ```POSTGRESQL_DB_NAME = llm_dialogues```
- ```POSTGRESQL_USER = llm_user```
- ```POSTGRESQL_PASSWORD = llm_secret```
- ```POSTGRESQL_TABLE_NAME = messages```


## Docker-compose explanation

```python
version: "3"
services:

  web:
    restart: "no"
    container_name: task_stepantsov
    build:
      context: ./
    volumes:
      - ./app:/app
    env_file:
      - .env
    environment:
      # Log settings
      LOG_LVL: INFO
      APP_HOST: 0.0.0.0
      APP_PORT: 80
      TRANSFORMERS_CACHE: ./volume/hg_cache
      # Volume settings
      VOLUME_DIR: volume
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
  postgres:
    image: postgres:14-alpine
    ports:
      - 5432:5432
    volumes:
      - ~/apps/postgres:/var/lib/postgresql/data
    environment:
      - POSTGRES_PASSWORD=llm_secret
      - POSTGRES_USER=llm_user
      - POSTGRES_DB=llm_dialogues
```

**important parts:**
- ```TRANSFORMERS_CACHE: ./volume/hg_cache ``` - folder where Haggingface model cache will be stored (used to avoid downloading models each time)
- change it, if you have more than 1 GPU
 	```devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]```

## PostgresQL explanation
this chatBot can interract with many users and save there history in PostgresQL database

```python
	self.cur.execute(
	                """CREATE TABLE IF NOT EXISTS {} (
	                        user_telegram_id bigint NOT NULL,
	                        author varchar(4) NOT NULL,
	                        message text NOT NULL
	                )""".format(self.postresql_table_name)
	                )
```

*important:* by default used last 10 dialogue turns (User-Bot turn)


## Large Language Model:
For this PoC demo [TheBloke/Wizard-Vicuna-13B-Uncensored-HF](https://huggingface.co/TheBloke/Wizard-Vicuna-13B-Uncensored-HF) was chosen. 

*This is wizard-vicuna-13b trained with a subset of the dataset - responses that contained alignment / moralizing were removed. The intent is to train a WizardLM that doesn't have alignment built-in, so that alignment (of any sort) can be added separately with for example with a RLHF LoRA.*

I have tested this model and in some cases it overcame LLama restrictions and filters, but sometimes returned something like
```I don’t want do discuss such a topics```
```I'm not sure if you're aware, but I'm an AI chatbot. I'm not interested in sex, but if you're looking for someone to talk to, I'm here for you.```

### potential problems
- emoji loops https://huggingface.co/TheBloke/Wizard-Vicuna-13B-Uncensored-HF/discussions/4
  to avoid it I delete emojies from 80% of all bot messages:
  ```python
  self.emoji_pattern = re.compile("["
            u"\U0001F600-\U0001F64F"  # emoticons
            u"\U0001F300-\U0001F5FF"  # symbols & pictographs
            u"\U0001F680-\U0001F6FF"  # transport & map symbols
            u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                            "]+", flags=re.UNICODE)
  ```


## USEFULL LINKS
- https://huggingface.co/TheBloke/Wizard-Vicuna-13B-Uncensored-HF
- https://github.com/huggingface/transformers
- https://stackoverflow.com/questions/13322485/how-to-get-the-primary-ip-address-of-the-local-machine-on-linux-and-os-x
- https://core.telegram.org/bots/tutorial
- https://www.freecodecamp.org/news/how-to-create-a-telegram-bot-using-python/
- https://huggingface.co/blog/4bit-transformers-bitsandbytes
- https://community.openai.com/t/temperature-top-p-and-top-k-for-chatbot-responses/295542
- https://medium.com/@daniel.puenteviejo/the-science-of-control-how-temperature-top-p-and-top-k-shape-large-language-models-853cb0480dae

from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    set_seed,
    pipeline,
    BitsAndBytesConfig
)

import random
import numpy as np
import torch, gc
from tqdm import tqdm

import huggingface_hub
from datasets import load_metric
import settings
from prompt_processing import cvt_dialogue_2_prompt
from bot_info import BotInfo
import re




class ChatBot:

    def __init__(self, model_name, tokenizer_name, quant_bits):
        self.model = None
        self.tokenizer = None
        self.quant_bits = quant_bits
        self.model_name = model_name
        self.tokenizer_name = tokenizer_name
        huggingface_hub.login(token=settings.HF_TOKEN)
        set_seed(settings.MODEL_SEED)
        self._initialize_model()
        self.meteor = load_metric('meteor')

        self.emoji_pattern = re.compile("["
            u"\U0001F600-\U0001F64F"  # emoticons
            u"\U0001F300-\U0001F5FF"  # symbols & pictographs
            u"\U0001F680-\U0001F6FF"  # transport & map symbols
            u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                            "]+", flags=re.UNICODE)


    def _initialize_model(self):
        del self.model
        gc.collect()
        torch.cuda.empty_cache()
        self.model = None

        self.model = self._load_model(self.model_name, self.quant_bits)
        self.tokenizer = self._load_tokenizer(self.tokenizer_name)
        self.model.resize_token_embeddings(len(self.tokenizer))

        self.pipeline = pipeline("text-generation",model=self.model,tokenizer=self.tokenizer,max_new_tokens=settings.MAX_NEW_TOKENS,
                device_map='auto', top_p=settings.TOP_P, top_k=settings.TOP_K, do_sample=True,
                temperature=settings.TEMPERATURE,)



    def _generate_responses(self, prompts):

        return self.pipeline(prompts)


    def _load_model(self, model_name, quant_bits) -> AutoModelForCausalLM:
        if quant_bits == 4:
            model = AutoModelForCausalLM.from_pretrained(
                                    model_name,
                                    device_map='auto',
                                    load_in_4bit=True,
                                    offload_folder=settings.OFFLOAD_FOLDER_NAME,
                                    trust_remote_code=True,
                                    use_auth_token=settings.HF_TOKEN,
                                    torch_dtype=torch.bfloat16,
                                    quantization_config=BitsAndBytesConfig(
                                        load_in_4bit=True,
                                        bnb_4bit_compute_dtype=torch.bfloat16,
                                        bnb_4bit_use_double_quant=True,
                                        bnb_4bit_quant_type='nf4'
                                    ),
                                )
        elif quant_bits == 8:
            model = AutoModelForCausalLM.from_pretrained(
                                    model_name,
                                    device_map='auto',
                                    load_in_8bit=True,
                                    offload_folder=settings.OFFLOAD_FOLDER_NAME,
                                    trust_remote_code=True,
                                    use_auth_token=settings.HF_TOKEN,
                                    torch_dtype=torch.bfloat16,
                                    quantization_config=BitsAndBytesConfig(
                                        load_in_8bit=True,
                                    ),
                                )
        elif quant_bits == 0:
            model = AutoModelForCausalLM.from_pretrained(
                                    model_name,
                                    device_map='auto',
                                    offload_folder=settings.OFFLOAD_FOLDER_NAME,
                                    trust_remote_code=True,
                                    use_auth_token=settings.HF_TOKEN,
                                    #torch_dtype=TORCH_DTYPE,
                                    revision="main"
                                    )
        
        
        else:
            print('not supported quantization')
        return model


    def _delete_emoji(string):
        return self.emoji_pattern.sub(r'', string)


    def _load_tokenizer(self, tokenizer_name) -> AutoTokenizer:
        tokenizer = AutoTokenizer.from_pretrained(tokenizer_name, use_auth_token=settings.HF_TOKEN,)
        tokenizer.pad_token = tokenizer.eos_token
        return tokenizer

    # check previous bot message for similarity with current
    def _checkMessageSimilarity(self, newMessage, history, biography):
        simmilarityScore = self.meteor.compute(predictions=[biography], references=[newMessage])['meteor']
        for message in history:
            simmilarityScore = max(self.meteor.compute(predictions=[message], references=[newMessage])['meteor'], simmilarityScore)
        return simmilarityScore


    # generate answer with checking  previous bot messages for similarity
    # if there is a high level of similarity, try to generate new answer 
    # settings.MAX_COUNT_ATTEMPTS_TO_GENERATE_UNIQ_ANSWER count of generating attempts
    def _generateBestAnswer(self, prompt, history):
        countAtempts = settings.MAX_COUNT_ATTEMPTS_TO_GENERATE_UNIQ_ANSWER - 1
        bot_message_best = self._generate_responses([prompt])[0][0]["generated_text"].split("ASSISTANT:")[-1]
        best_score = self._checkMessageSimilarity(bot_message_best, [el[1] for el in history[:-1]], BotInfo)
        while countAtempts > 0:
            if best_score <= settings.SIMILARITY_THRESHOLD :
                return bot_message_best
            bot_message = self._generate_responses([prompt])[0][0]["generated_text"].split("ASSISTANT:")[-1]
            # in half of all messages try to delete emoji (if exists)
            if random.random() < 0.8:
                bot_message = delete_emoji(bot_message)
            score = self._checkMessageSimilarity(bot_message_best, [el[1] for el in history[:-1]], BotInfo)
            if score < best_score:
                best_score = score
                bot_message_best = bot_message
            countAtempts -= 1
        return bot_message_best 

    

    def generate_answer(self, user_message, history):
        prompt = cvt_dialogue_2_prompt(history, user_message)
        bot_message = self._generateBestAnswer(prompt, history)
        return bot_message 
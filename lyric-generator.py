#
# This script will generate lyrics based on a given theme and song title by leverage GPT-4-Turbo.
#

import os
import time
import threading
import argparse
import json
from openai import AzureOpenAI
from alive_progress import alive_bar, config_handler

long_time_call_finished = False

def endless_spinner():
    config_handler.set_global(length=100, spinner='classic')
    with alive_bar(0, spinner='dots_waves2', title='Generating Lyrics...', bar='blocks') as bar:
        while not long_time_call_finished:
            time.sleep(1)
            bar()

def load_prompt_file(language_code:str) -> str:
    prompt_file_name = 'prompts/prompt-{language_code}.md'.format(language_code=language_code)
    prompt_file_path = os.path.join(os.path.dirname(__file__), prompt_file_name)
    if not os.path.exists(prompt_file_path):
        print('The prompt file {prompt_file_path} does not exist.'.format(prompt_file_path=prompt_file_path))
        return None
    with open(prompt_file_path) as prompt_file:
        prompt = prompt_file.read()
        prompt_file.close()
        return prompt

def load_openai_config(config_path) -> dict:
    if config_path is not None:
        with open(config_path) as config_file:
            config = json.load(config_file)
            config_file.close()
            return config

def call_gpt_generate_lyrics(args, prompt:str) -> str:
    global long_time_call_finished
    prompt = prompt.format(keywords=args.keywords, theme=args.theme, amount=args.amount)
    message_text = [{"role": "system", "content": "你是一个专业的歌词创作者，在给唱片公司和著名歌星创作歌词。"},{"role":"user","content":"{prompt}".format(prompt=prompt)}]
    client = AzureOpenAI(azure_endpoint=args.openai_url, api_key=args.openai_key, api_version="2023-07-01-preview")
    response = client.chat.completions.create(
        model=args.deployment,
        messages=message_text,
        temperature=0.88,
        max_tokens=4096,
        top_p=0.95,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None)
    long_time_call_finished = True
    return str(response.choices[0].message.content)

def main():

    parser = argparse.ArgumentParser(description='A command tool that generate lyrics based on a given theme and song title.')
    parser.add_argument('--theme', type=str, help='The theme of the song')
    parser.add_argument('--keywords', type=str, help='The keywords that used to imagine to generate the lyrics')
    parser.add_argument('--amount', type=int, help='The amount of the songs to be generated', default=1)
    #OpenAI related arguments
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--config', type=str, help='The path to the config file')
    group.add_argument('--openai_url', type=str, help='The url of the OpenAI service endpoint base url')
    parser.add_argument('--openai_key', type=str, help='The key of the OpenAI service')
    parser.add_argument('--deployment', type=str, help='The deployment of the OpenAI service model')
    args = parser.parse_args()
    
    if args.config is not None:
        openai_config = load_openai_config(args.config)
        args.openai_url = openai_config['openai_url']
        args.openai_key = openai_config['openai_key']
        args.deployment = openai_config['deployment']
    
    if args.openai_key is None:
        print('The OpenAI service key must be specified.')
        return
    if args.deployment is None:
        print('The OpenAI service key must be specified.')
        return
    
    prompt = load_prompt_file('zh-cn')
    if prompt is None:
        return

    spinner_thread = threading.Thread(target=endless_spinner)
    spinner_thread.start()
    lyrics = call_gpt_generate_lyrics(args, prompt)
    spinner_thread.join()

    print(lyrics)

if __name__ == '__main__':
    main()
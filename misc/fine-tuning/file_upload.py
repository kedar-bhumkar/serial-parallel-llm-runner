from openai import OpenAI

import yaml

def getConfig(file_path):
    # Define the path to the YAML file
    yaml_file_path = file_path

    # Read the YAML file
    with open(yaml_file_path, 'r') as file:
        config = yaml.safe_load(file)
    return config

config = getConfig('..\config.yaml') 
client = OpenAI(
    api_key  = config["openai"]["key"],
    base_url = config["openai"]["url"],
)
client.files.create(
  file=open("formatted_conversation_data.jsonl", "rb"),
  purpose="fine-tune"
)
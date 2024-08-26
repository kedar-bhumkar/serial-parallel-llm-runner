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

client.fine_tuning.jobs.create(
  training_file="file-aI5HD8olkBFf7c6gSYUYyZ8Y", 
  model="gpt-4o-2024-08-06"
)
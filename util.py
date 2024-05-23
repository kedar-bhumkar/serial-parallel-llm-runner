from response_formatter import *
from constants import config_file
import json, yaml

def format_response(theFormatter,response):
    
    if(theFormatter != None):        
        converted_json = globals()[theFormatter](response)
        formatted_json = json.dumps(converted_json, indent=4)    
    else:    
        formatted_json = response
    
    return formatted_json



def getConfig(file_path):
    # Define the path to the YAML file
    yaml_file_path = file_path

    # Read the YAML file
    with open(yaml_file_path, 'r') as file:
        config = yaml.safe_load(file)
    return config
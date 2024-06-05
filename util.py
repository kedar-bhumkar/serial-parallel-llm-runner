from response_formatter import *
import json, yaml
import random
import re
from difflib import *

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




def getRunID(digits):
    if digits < 1:
        raise ValueError("Number of digits must be at least 1")
    
    lower_bound = 10**(digits - 1)
    upper_bound = (10**digits) - 1
    
    return random.randint(lower_bound, upper_bound)


def compare(resp1, resp2):
    #print(f'resp1-{resp1}')
    #print(f'resp2-{resp2}')

    resp1 = (re.sub(r'\s+', '', resp1[0])).lower()
    resp2 = (re.sub(r'\s+', '', resp2[0])).lower()

    print(f'resp1-{resp1}')
    print(f'resp2-{resp2}')


    diff = unified_diff(resp1 , resp2,n=0, lineterm='')    
    changes = ''.join(list(diff))
    print(f'diff-{changes}')

    if(resp1 == resp2):
        return True, changes
    else:
        return False, changes


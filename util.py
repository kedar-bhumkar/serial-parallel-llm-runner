from response_formatter import *
import json, yaml
import random
import re
from difflib import *
import Levenshtein
import tiktoken

def transform_response(theFormatter,response):
    
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


    diff = unified_diff(resp1 , resp2,n=0, lineterm='')    
    changes = ''.join(list(diff))
    print(f'diff-{changes}')

    ratio = SequenceMatcher(a=resp1, b=resp2).ratio()
    _ratio = f'diff_ratio-{ratio}'
    #print(f'ratio-{_ratio}')

    # Calculate Levenshtein distance
    distance = Levenshtein.distance(resp1, resp2)
    _distance = f'distance-{distance}'
    #print(f'Levenshtein distance-{_distance}')

    similarity_ratio = Levenshtein.ratio(resp1, resp2)    
    _similarity_ratio = f'similarity_ratio-{similarity_ratio}'
    #print(f'Similarity ratio-{_similarity_ratio}')    

    if(resp1 == resp2):
        return True, changes, f'{_ratio},{_distance},{_similarity_ratio}'
    else:
        return False, changes, f'{_ratio},{_distance},{_similarity_ratio}'

def format_response(response):
    return  (re.sub(r'\s+', '', response)).lower()

def num_tokens_from_string(string: str, encoding_name: str, type: str) -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    print(f'For {type} the no of tokens are {num_tokens}')
    return num_tokens

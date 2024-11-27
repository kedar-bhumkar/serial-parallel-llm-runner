from backend.core.service.response_formatter import *
import json, yaml
import random
import re
from difflib import *
import Levenshtein
import tiktoken
from backend.core.model.pydantic_models import *
from backend.core.logging.custom_logger import *
import re
from datetime import datetime, timedelta
from backend.core.utility.util import *
from backend.core.utility.shared import *

def transform_response(theFormatter,response):
    logger.critical('Inside  transform_response')
    if(theFormatter != None):        
        formatted_json = globals()[theFormatter](response)
        #formatted_json = json.dumps(converted_json, indent=4)    
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
    #logger.info(f'resp1-{resp1}')
    #logger.info(f'resp2-{resp2}')


    diff = unified_diff(resp1 , resp2,n=0, lineterm='')    
    changes = ''.join(list(diff))
    logger.critical(f'diff-{changes}')

    ratio = SequenceMatcher(a=resp1, b=resp2).ratio()
    _ratio = f'diff_ratio-{ratio}'
    #logger.info(f'ratio-{_ratio}')

    # Calculate Levenshtein distance
    distance = Levenshtein.distance(resp1, resp2)
    _distance = f'distance-{distance}'
    #logger.info(f'Levenshtein distance-{_distance}')

    similarity_ratio = Levenshtein.ratio(resp1, resp2)    
    _similarity_ratio = f'similarity_ratio-{similarity_ratio}'
    #logger.info(f'Similarity ratio-{_similarity_ratio}')    

    if(resp1 == resp2):
        return True, changes, f'{_ratio},{_distance},{_similarity_ratio}'
    else:
        return False, changes, f'{_ratio},{_distance},{_similarity_ratio}'


def num_tokens_from_string(string: str, encoding_name: str, type: str) -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    logger.critical(f'For {type} the no of tokens are {num_tokens}')
    return num_tokens

def get_Pydantic_Filtered_Response(page, response, formatter,response_type=None):
    logger.critical(f"page-{page} , formatter - {formatter},  response-{response} ")
    try:
        cls = globals()[page]
    except:
        logger.critical("No pydantic model defined")
    else:    
        logger.critical("pydantic model defined...")
        
        try:
            #logger.critical(f'****** response->{response}')
            validated_response = cls.model_validate_json(response)
            formatted_response = transform_response(formatter, validated_response)
            response= formatted_response.model_dump_json()       
            
        except Exception as e:    
            logger.critical(f"response validation failed -{e}")   
        else:
            logger.critical("response validation is successful ...")     
        
    finally:
        if(response_type == 'actual'):
            shared_data_instance.set_data('unformatted_response', response)               
        return trim_response(response)
    
    
def trim_response(response):
    return  (re.sub(r'\s+', '', response)).lower()



def parse_models(data):
    result = {}
    for key, value in data.items():        
        preferred_model = value.get('preferred_model')
        model_options = value.get('model_options')
        isActive = value.get("active")
        
        if preferred_model is not None and model_options is not None and isActive:
            result[key] = [preferred_model] + model_options

    return result


def combine_jsons(json_strings):
    #logger.critical(f"json_strings-{json_strings}")
    # Convert JSON strings to dictionaries
    json_dicts = [json.loads(json_string) for json_string in json_strings]

    # Combine all dictionaries into a single dictionary
    combined_dict = {}
    for d in json_dicts:
        combined_dict.update(d)

    # Convert the combined dictionary back to a JSON string
    combined_json = json.dumps(combined_dict, indent=4)

    return combined_json

def replace_dates(input_string):
    today = datetime.now()
    yesterday = today - timedelta(days=1)
    
    today_str = today.strftime('%d-%m-%Y')
    yesterday_str = yesterday.strftime('%d-%m-%Y')
    
    # Use regular expressions for case-insensitive replacement
    updated_string = re.sub(r'today', 'on '+ today_str, input_string, flags=re.IGNORECASE)
    updated_string = re.sub(r'yesterday', 'on ' + yesterday_str, updated_string, flags=re.IGNORECASE)
    
    #print(f'replaced dates prompt - {updated_string}' )

    return updated_string

def truncate_prompt(text):
    delimiter = "Return_data_constraints:"
    if delimiter in text:
        return text.split(delimiter)[0] 
    return text

def add_space_after_punctuation(input_string):
    punctuations = {',': ', ', ';': '; ', '.': '. '}
    
    # Replace each punctuation mark followed by no space with itself followed by a space
    for punctuation, replacement in punctuations.items():
        input_string = input_string.replace(punctuation, replacement)
        
    return input_string
from typing import Dict, Type, Literal
from pydantic_models import *
from custom_logger import *
import yaml
from constants import prompts_file
from fuzzy_matching import check_word_in_transcript
from shared import *


def ros_pe_formatter(data:ros):    
    logger.critical('Inside ros_pe_formatter ...')
    confidence_level ={}
    #@ToDo : revisit how to pass data between modules
    config = getConfig(prompts_file) 
    #shared_prompt =  (config['acd']['user_prompt']['ros']['serial']['input'])    
    shared_prompt = shared_data_instance.get_data('thePrompt')
    print(f"shared_user_prompt - {shared_prompt}")
    shared_error_detection = shared_data_instance.get_data('error_detection')
    print(f"shared_error_detection-{shared_error_detection}")
    
    #Construct field name: type dict . This would be used to get the actual class for a 'string' section name
    field_dict = get_field_types(ros)

    for section in data.dict():
        logger.critical(f"***** section- {section}")
        section_data = getattr(data, section)
        theAttr = getattr(section_data, 'Reviewed_and_Negative', None)
        
        # Remove n/a
        if theAttr!=None:
            if section_data.Reviewed_and_Negative.casefold() == 'na' :
                
                #logger.critical(f"***** correcting Reviewed_and_Negative")
                setattr(section_data, 'Reviewed_and_Negative', 'false')

        # Replace null with Other 
        theAttr = getattr(section_data, 'Not_Assessed_Reason', None)   
        
         

       
        if shared_error_detection!='false':
            print(f"Inside error detection....shared_error_detection-{shared_error_detection}")
            if section!='Reviewed_with' and section!= 'additional_notes':            
                # if any of the attribute values is not null or not na then check
                    # 1) If the section is assessed
                    # 2) if the section was mentioned in the matched words list of fuzzy wuzzy
                    # 3) If both are false flag the attribute as low-confidence in confidence map 
                
                section_model = field_dict.get(section)
                attributes = get_pydantic_attributes(globals()[section_model])
                print(attributes)

                assessed_field_name = find_assessed_field(globals()[section_model], Literal["Assessed", "Not Assessed"])
                
                if assessed_field_name!=None:
                    assessed_field_value = getattr(section_data,assessed_field_name,None)      
                    for attrib in attributes:                    
                        field_value =   getattr(section_data,attrib,None)  
                        print(f"section - {section} , assessed_field_name -{assessed_field_name}, theAttr-{attrib}, theAtrrib-value-{field_value} ")            
                        key = section + '-' + attrib                                
                        if(field_value!=None and field_value!='NA'):                                           
                            if(assessed_field_value == "Assessed"):
                                fuzzy_match = check_word_in_transcript(section_model, shared_prompt)
                                print(f"fuzzy_match for word {section_model} - is - {fuzzy_match}")
                                if(fuzzy_match):
                                    print('fuzzy matched ')
                                else:
                                    print('not fuzzy matched low confidence')                                
                                    print(f"section - {section_model} , assessed_field_name -{assessed_field_name}")  
                                    confidence_level[key] = f"section - {section_model} , assessed_field_name -{assessed_field_name} low - not fuzzy matched"
                            elif(assessed_field_value == "Not Assessed"): 
                                if(field_value == "false"):                                                    
                                    setattr(section_data, attrib, 'NA')     
                                
                            else:    
                                if(assessed_field_name!=attrib and field_value!='Other'):
                                    print(f"section - {section_model} , assessed_field_name -{assessed_field_name}")  
                                    print(f"attrib-{attrib}")
                                    print('not assessed low confidence')                                
                                    confidence_level[key] =  f"section - {section_model} , assessed_field_name -{assessed_field_name} low - not assessed section"
                        elif(assessed_field_value == "Not Assessed" and attrib == 'Not_Assessed_Reason' and field_value == None):    
                                    logger.critical(f"***** correcting Not_Assessed_Reason")
                                    setattr(section_data, 'Not_Assessed_Reason', 'Other')   
        else:
             print("Skipped  error detection....")

    print(f"confidence level - {confidence_level}")
    shared_data_instance.set_data('confidence_map', confidence_level)
    return data

# Function to dynamically fetch all attributes of a Pydantic class
def get_pydantic_attributes(model: BaseModel) -> Dict[str, str]:
    return {field_name: field for field_name, field in model.model_fields.items()}


# Function to dynamically get and return field types as a dictionary
def get_field_types(model: BaseModel) -> Dict[str, str]:


    field_types = {}
    for field_name, field in model.model_fields.items():
        field_type = field.annotation
        if hasattr(field_type, "__name__"):
            field_type_name = field_type.__name__
        else:
            field_type_name = str(field_type)
        field_types[field_name] = field_type_name
    return field_types


# Function to find the field with the specified type
def find_assessed_field(cls: Type[BaseModel], literal_type: Literal["Assessed", "Not Assessed"]) -> Optional[str]:
    for field_name, field in cls.model_fields.items():
        if field.annotation == literal_type:
            return field_name
    return None


field_dict = get_field_types(ros)
section_model = field_dict.get('CONSTITUTIONAL')
print(f'section_model-{section_model}')
#attributes = get_pydantic_attributes(globals()[section_model])
#print(attributes)

# Literal type to check
literal_type = Literal["Assessed", "Not Assessed"]
#field_name = find_assessed_field(Constitutional, literal_type)
#print(f"field_name -{field_name}")


def getConfig(file_path):
    # Define the path to the YAML file
    yaml_file_path = file_path

    # Read the YAML file
    with open(yaml_file_path, 'r') as file:
        config = yaml.safe_load(file)
    return config

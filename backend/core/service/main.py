import asyncio
from openai import AsyncOpenAI, OpenAI
import time
import argparse
from backend.core.logging.custom_logger import *
from backend.core.model.pydantic_models import *
from backend.core.utility.constants import *
from backend.core.utility.util import *
from backend.core.db.db_layer import *
from backend.core.db.db_stats import *
from backend.core.utility.fuzzy_matching import *
from backend.core.utility.phi_remover import *
from backend.core.utility.shared import *
import pandas as pd

clientSync = any
theModel = any
theFormatter = None
thePrompt = None
theSystemPrompt= None
run_mode = None
run_count= None
run_id = None
theIdealResponse = None
accuracy_check = None
test_map = {}

# Serial

db_data= []
i_data={}




def generate(client,count,prompt,page):    
    print("Entering method: generate")
    #logger.critical(f"generate - {prompt}")
    num_tokens_from_string(''.join([theSystemPrompt, prompt]), default_encoding, "input")
    #logger.critical(f"theSystemPrompt-{theSystemPrompt}")

    completion_params = {
       "messages": [
           {"role": "system", "content": theSystemPrompt},
           {"role": "user", "content": prompt}
       ],
       "model": theModel
   }

    completion_params.update(shared_data_instance.get_data('completion_params'))
    print(f"completion_params-{completion_params}")
 
    chat_completion = client.chat.completions.create(**completion_params)   

    response = chat_completion.choices[0].message.content
    print(f"chat_completion-total_tokens-{chat_completion.usage.total_tokens}")
    print(f"chat_completion-completion_tokens-{chat_completion.usage.completion_tokens}")
    print(f"chat_completion-prompt_tokens-{chat_completion.usage.prompt_tokens}")
    print(f"chat_completion-prompt_tokens_details_cached_tokens-{chat_completion.usage.prompt_tokens_details.cached_tokens}")
    #print(f"chat_completion.usage.completion_tokens_details.accepted_prediction_tokens-{chat_completion.usage.completion_tokens_details.accepted_prediction_tokens}")
    #print(f"chat_completion.usage.completion_tokens_details.rejected_prediction_tokens-{chat_completion.usage.completion_tokens_details.rejected_prediction_tokens}")
    #print(f"chat_completion.usage.completion_tokens_details.reasoning_tokens-{chat_completion.usage.completion_tokens_details.reasoning_tokens}")
    print(f"chat_completion.system_fingerprint-{chat_completion.system_fingerprint}")

    shared_data_instance.set_data('fingerprint', chat_completion.system_fingerprint)
    num_tokens_from_string(response, default_encoding, "output")
    #logger.critical(f'unformatted response...  {count} ...' , response)
    
    #This got replaced by the pydantic formatter
    #formatted_json = transform_response(theFormatter, response)
    #logger.info(f'response...  {count} ...' , formatted_json)
    return response
 
# Serial
def generate_serially(usecase, page, mode, prompt):  
    print("Entering method: generate_serially")
    global clientSync, thePrompt  
    config = getConfig(prompts_file) 
    #thePrompt = (config[usecase]['user_prompt'][page][mode]['input'])  
    thePrompt = prompt        
   
    thePrompt = prompt_constrainer(page,thePrompt,-1)
    return [generate(clientSync, 0, thePrompt, page)]





def init_AI_client(model_family, model):
    print("Entering method: init_AI_client")
    global clientSync, theModel
    
    config = getConfig(config_file)
    if(model==None):
        theModel =  config[model_family]["preferred_model"]
    else:    
        theModel = model

    completion_params = config[model_family]["parameters"]
    shared_data_instance.set_data('completion_params', completion_params)
       
    clientSync = OpenAI(
        api_key  = config[model_family]["key"],
        base_url = config[model_family]["url"],
    )

def init_prompts(usecase, page, mode):
    print("Entering method: init_prompts")
    global thePrompt,theSystemPrompt,theIdealResponse
    config = getConfig(prompts_file)     
    theSystemPrompt = config[usecase]['system_prompt']
    logger.critical(f"theSystemPrompt-{theSystemPrompt}")
    if(shared_data_instance.get_data('theIdealResponse') == None or shared_data_instance.get_data('theIdealResponse') == ''):
        theIdealResponse = config[usecase]['user_prompt'][page]['serial']['ideal_response']
    else:
        theIdealResponse = shared_data_instance.get_data('theIdealResponse')
  

def prompt_constrainer(page,thePrompt, count=None):
    print("Entering method: prompt_constrainer")
    logger.critical(f"trnascript-{thePrompt}")
    page_index = page
    negativePrompt = ''
    thePrompt = replace_dates(thePrompt)
    #remove phi/pii    
    if(shared_data_instance.get_data('phi_detection') == True):
        print(f"Inside phi detection ")
        thePrompt = remove_phi_pii_presidio(thePrompt)
    else:
        print(f"phi detection is off")
    
    sharedPrompt = thePrompt
    #Create copy so that we just get what the user said minus constraints 
    shared_data_instance.set_data('thePrompt', sharedPrompt)
    #logger.info(f"page_index-{page_index}")
    if(shared_data_instance.get_data('negative_prompt')== True):
        negativePrompt = fuzzyMatch(thePrompt)   
    logger.critical(f"negativePrompt-{negativePrompt}")

    start_time = time.time()
    try:
        if(count!=-1):
            page_index = page+ str(count)
        cls = globals()[page_index]
    except:
        logger.info(f"No pydantic model defined")
    else:    
        logger.info(f"pydantic model defined")
        response_schema_dict = cls.model_json_schema()
        response_schema_json = json.dumps(response_schema_dict, indent=2)    
        end_time = time.time()
        print(f"Time taken to get response schema - {end_time-start_time}")

        #logger.info(f"response_schema_json-{response_schema_json}")
        #print(f"response_schema_json-{response_schema_json}")
        constraints = "constraints"+ str(count)
        #print(f"constraints-{constraints}")
        logger.info(f"constraints-{constraints}")
        logger.info(f"thePrompt-{thePrompt}")
        
        # @todo REFACTOR THIS
        if(count == -1):
            thePrompt = thePrompt.format(constraints=response_schema_json,missing_sections=negativePrompt)
            #print(f"thePrompt-{thePrompt}")
            exit
        if(count == 0):
            thePrompt = thePrompt.format(constraints0=response_schema_json,missing_sections=negativePrompt)
        elif (count ==1):
            thePrompt = thePrompt.format(constraints1=response_schema_json,missing_sections=negativePrompt)
        elif (count ==2):
            thePrompt = thePrompt.format(constraints2=response_schema_json,missing_sections=negativePrompt)
        logger.info(f"thePrompt ****** -{thePrompt}")
    finally:
        return thePrompt
    



def sync_async_runner(usecase, page, mode, model_family,formatter, run_mode, sleep_time, model, prompt):    
    print("Entering method: sync_async_runner")
    global theFormatter, i_data, db_data
    db_data = []
    
    # Parallel invoker
    if(mode == None):
        mode = default_mode

    if(page == None):
        page = default_page     

    if(model_family == None):
        model_family = default_model_family

    if(formatter != None):
        theFormatter = formatter    
    
    if(usecase == None):
        usecase = default_usecase

    if(sleep_time == None):
        sleep_time = default_sleep    
    logger.info(f"model-{model}")
    init_AI_client(model_family, model)
    init_prompts(usecase, page, mode)



    if (mode == "serial" or  mode == "dual"):   
        # Serial invoker
        start = time.perf_counter()
        response = generate_serially(usecase, page, mode, prompt)        
        end = time.perf_counter() - start        
        response = response[0]
        
        logger.info(f"Serial Program finished in {end:0.2f} seconds.")

    
    if(run_mode !=None):
        response = log(usecase, page, response, end, mode)
        #logger.critical(f"f-response-{response}")

    time.sleep(sleep_time)

    return response



def log(usecase, page, response, time, mode):    
    print("Entering method: log")
    #logger.critical(f"logging in db ...mode={mode}, response ={response}")
    global theFormatter, i_data, db_data, run_id,theIdealResponse,thePrompt,test_map
    matches_idealResponse = None
    run_mode = shared_data_instance.get_data('run_mode')   
    repro_difflib_similarity = None
    accuracy_difflib_similarity = None

    formatted_real_response = get_Pydantic_Filtered_Response(page,response,theFormatter,response_type='actual')
    #print(f"formatted_real_response - {formatted_real_response}" )
    
    test_result = {}

    if(len(db_data)>0):
        isBaseline = False
        first_response = db_data[0]['response']
        matches_baseline, reproducibility_changes, repro_difflib_similarity = compare(get_Pydantic_Filtered_Response(page, first_response,None), get_Pydantic_Filtered_Response(page,response,None))
    else:
        isBaseline = True
        matches_baseline = True
        reproducibility_changes = ''
        repro_difflib_similarity = 1.0

    if(accuracy_check == "ON" and run_mode != 'test-llm'):
         logger.info(f"theIdealResponse - {theIdealResponse}, response -{response}")
         formatted_ideal_response = get_Pydantic_Filtered_Response(page,theIdealResponse, None)       
         #print(f"formatted_ideal_response - {formatted_ideal_response}" )
         shared_data_instance.set_data('theIdealResponse', formatted_ideal_response)
         matches_idealResponse, idealResponse_changes,accuracy_difflib_similarity = compare(formatted_ideal_response, formatted_real_response)
    elif(run_mode == 'test-llm'):
         logger.info(f"Running test")
         formatted_ideal_response = get_Pydantic_Filtered_Response(page,theIdealResponse, None)                
         matches_idealResponse, idealResponse_changes,accuracy_difflib_similarity = compare(formatted_ideal_response, formatted_real_response)
         test_result['matches_idealResponse'] = matches_idealResponse
         test_result['idealResponse_changes'] = idealResponse_changes
         test_result['accuracy_difflib_similarity'] = accuracy_difflib_similarity
         test_result['ideal_response'] = formatted_ideal_response
         test_result['actual_response'] = formatted_real_response
         test_result['original_response'] = shared_data_instance.get_data('original_response')  
         test_result['original_run_no'] = shared_data_instance.get_data('original_run_no')
         test_result['original_prompt'] = shared_data_instance.get_data('original_prompt')
         test_result['fingerprint'] = shared_data_instance.get_data('fingerprint')
         logger.critical(f"accuracy_difflib_similarity-{accuracy_difflib_similarity}")
         test_map[shared_data_instance.get_data('run_no')] = test_result
         
    else:
        matches_idealResponse = ""
        idealResponse_changes = ""    
        formatted_ideal_response = ""


    if(run_mode != 'test-llm'):
        if(mode=='parallel'):
            thePrompt = shared_data_instance.get_data('transcript')

        i_data = {
            'usecase':usecase,
            'mode':mode,
            'functionality':page,
            'llm':theModel,
            'llm_parameters':'temperature='+str(default_temperature),
            'isBaseline': isBaseline,
            'run_no': run_id,
            'system_prompt': theSystemPrompt,
            'user_prompt': truncate_prompt(thePrompt),
            'response': formatted_real_response,
            'ideal_response':formatted_ideal_response,
            'execution_time': time,
            'matches_baseline': matches_baseline,
            'matches_ideal':matches_idealResponse,
            'difference': reproducibility_changes,
            'ideal_response_difference': idealResponse_changes,
            'similarity_metric':f'accuracy_difflib_similarity->>{accuracy_difflib_similarity} -- repro_difflib_similarity->>{repro_difflib_similarity}',
            'use_for_training': shared_data_instance.get_data('use_for_training'),
            'fingerprint': shared_data_instance.get_data('fingerprint')
        }    
        db_data.append(i_data)
    #logger.info(f"** db_data - {db_data}")
    return formatted_real_response



def process_request(usecase, page, mode, model_family, formatter, run_mode, sleep, model, 
                   prompt, run_count, accuracy_check, negative_prompt, use_for_training, 
                   error_detection, phi_detection, test_size_limit=None, file_name=None, ideal_response=None):
    """Common processing logic for both CLI and API requests"""
    global run_id, theIdealResponse, test_map, db_data

    # Initialize defaults if not provided
    mode = mode or default_mode
    run_mode = run_mode or default_run_mode
    run_count = run_count or default_run_count
    accuracy_check = accuracy_check or default_accuracy_check
    use_for_training = use_for_training or default_use_for_training
    error_detection = error_detection or default_error_detection
    phi_detection = phi_detection or default_phi_detection
    logger.critical(
        f"usecase-{usecase}, page-{page}, mode-{mode}, family-{model_family}, "
        f"formatter-{formatter}, run_mode-{run_mode}, run_count-{run_count}, "
        f"sleep-{sleep}, accuracy_check-{accuracy_check}, model-{model}, "
        f"negative_prompt-{negative_prompt}, use_for_training-{use_for_training}, "
        f"phi_detection-{phi_detection}, file_name-{file_name}, ideal_response-{ideal_response}"
    )

    # Set shared data
    shared_data = {
        'negative_prompt': negative_prompt,
        'use_for_training': use_for_training,
        'error_detection': error_detection,
        'run_mode': run_mode,
        'phi_detection': phi_detection,
        'theIdealResponse': ideal_response,
        'prompt': prompt
    }
    for key, value in shared_data.items():
        shared_data_instance.set_data(key, value)

    run_id = getRunID(8)
    config = getConfig(prompts_file)

    # if file_name is provided, process each prompt in the file in serial mode on same llm
    if file_name is not None:
        df_prompts = load_prompt_from_file(file_name)        
        if df_prompts is not None:
            for index, row in df_prompts.iterrows():
                prompt = row['Transcript']
                if isinstance(prompt, str):
                    prompt = add_space_after_punctuation(prompt)
                    _process_same_llm(usecase, page, mode, model_family, formatter, run_mode, sleep, model, prompt, run_count, accuracy_check)
        else:
            logger.error(f"No prompts found in the file: {file_name}")

    else:
        # if file_name is not provided, process the prompt based on below logic        
        if prompt is None and mode != "test-llm":
            prompt = config[usecase]['user_prompt'][page][mode]['input']
            if isinstance(prompt, str):
                    prompt = add_space_after_punctuation(prompt)     
        

        # Process based on run mode
        if run_mode == "multiple-llm":
            return _process_multiple_llm(
                usecase, page, mode, formatter, run_mode, sleep, prompt
            )

        elif run_mode == "test-llm":
            return _process_test_llm(
                usecase, page, mode, model_family, formatter, 
                run_mode, sleep, model, test_size_limit
            )

        else:  # same-llm mode
            return _process_same_llm(
                usecase, page, mode, model_family, formatter,
                run_mode, sleep, model, prompt, run_count, accuracy_check
            )

def _process_multiple_llm(usecase, page, mode, formatter, run_mode, sleep, prompt):
    """Handle multiple LLM processing mode"""
    result = parse_models(getConfig(config_file))
    responses = []
    
    for model_family, models in result.items():
        for model in models:
            response = sync_async_runner(
                usecase, page, mode, model_family, 
                formatter, run_mode, sleep, model, prompt
            )
            responses.append(response)
    
    return responses

def _process_test_llm(usecase, page, mode, model_family, formatter, 
                     run_mode, sleep, model, test_size_limit):
    """Handle test LLM processing mode"""
    result = get_test_data(test_size_limit)
    
    for count, row in result.iterrows():
        logger.critical(f"Running test {count+1} of total {len(result)}")
        if row['user_prompt'] is not None:
            _setup_test_data(row)
            prompt = ''.join([
                'Return_data_constraints: {constraints} ',
                row['user_prompt'],
                '{missing_sections}'
            ])
            start_time = time.time()
            sync_async_runner(
                row['usecase'], row['functionality'], mode,
                model_family, formatter, run_mode, sleep, model, prompt
            )
            
            test_result =test_map[shared_data_instance.get_data('run_no')] 
            test_result['execution_time'] = round(time.time() - start_time, 2)


    return _generate_test_summary()

def _process_same_llm(usecase, page, mode, model_family, formatter,
                     run_mode, sleep, model, prompt, run_count, accuracy_check):
    """Handle same LLM processing mode"""
    response = [
        sync_async_runner(
            usecase, page, mode, model_family, formatter,
            run_mode, sleep, model, prompt
        ) for _ in range(run_count)
    ]
    
    confidence_map = shared_data_instance.get_data('confidence_map')
    
    if run_mode is not None:
        insert(db_data)
        print_reproducibility_stats(readWithGroupFilter(run_id))
    
    if accuracy_check == "ON":
        print_accuracy_stats(readWithGroupFilter(run_id))
        
    return {"response": response, "confidence_map": confidence_map, "ideal_response": shared_data_instance.get_data('theIdealResponse'), "prompt": shared_data_instance.get_data('prompt')}



def _setup_test_data(row):
    """Helper to set up shared data for test runs"""
    shared_data = {
        'theIdealResponse': row['ideal_response'],
        'run_no': row['run_no'],
        'ideal_response': row['ideal_response'], 
        'original_response': row['response'],
        'usecase': row['usecase'],
        'original_run_no': row['run_no'],
        'original_prompt': row['user_prompt']
    } 
    
    for key, value in shared_data.items():
        shared_data_instance.set_data(key, value)

def _generate_test_summary():
    """Generate and log test results summary"""
    total_tests = len(test_map)
    passed_tests = sum(1 for test in test_map.values() if test['matches_idealResponse'])
    failed_tests = total_tests - passed_tests
    pass_rate = f"{(passed_tests/total_tests)*100:.2f}%"
    average_execution_time = round(sum(test['execution_time'] for test in test_map.values()) / total_tests, 2)
    
    summary = {
        "AI model": theModel,
        "Tests Passed": passed_tests,
        "Tests Failed": failed_tests,
        "Total Tests": total_tests,
        "Pass Rate": pass_rate,
        "Average Execution Time": average_execution_time
    }
    
    logger.critical("\nTest Suite Results:")
    logger.critical("==================")
    for key, value in summary.items():
        logger.critical(f"{key}: {value}")
    
    save_test_results(test_map, theModel, total_tests, passed_tests, failed_tests, pass_rate, average_execution_time)
    return summary

def handleRequest(message: Message):
    """Handle API requests"""
    if isinstance(message.prompt, str):
        message.prompt = add_space_after_punctuation(message.prompt)
        
    return process_request( 
        usecase=message.usecase,
        page=message.page,
        mode=message.mode,
        model_family=message.family,
        formatter=message.formatter,
        run_mode=message.run_mode,
        sleep=message.sleep,
        model=message.model,
        prompt=message.prompt,
        run_count=message.run_count,
        accuracy_check=message.accuracy_check,
        negative_prompt=message.negative_prompt,
        use_for_training=message.use_for_training,
        error_detection=message.error_detection,
        phi_detection=message.phi_detection,
        ideal_response=message.ideal_response
    )




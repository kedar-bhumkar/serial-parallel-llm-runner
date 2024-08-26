import asyncio
from openai import AsyncOpenAI, OpenAI
import time
import argparse
from custom_logger import *
from pydantic_models import *
from constants import *
from util import *
from db_layer import *
from db_stats import *
from fuzzy_matching import *
from shared import *

clientSync = any
clientAsync = any
theModel = any
theFormatter = None
thePrompt = None
theSystemPrompt= None
run_mode = None
run_count= None
run_id = None
theIdealResponse = None
accuracy_check = None


# Serial

db_data= []
i_data={}

async def async_generate(client,count,prompt):        
    #logger.info(f"generate - {prompt}")
    num_tokens_from_string(''.join([theSystemPrompt, prompt]), default_encoding, "input")
    chat_completion = await client.chat.completions.create(
      messages=[
            {"role": "system", "content": theSystemPrompt},
            {"role": "user",   "content": prompt}
        ],
        model=theModel,
        temperature = default_temperature
    )

    response = chat_completion.choices[0].message.content
    num_tokens_from_string(response, default_encoding, "output")
    #logger.critical(f'unformatted response...  {count} ...' , response)
   
    #This got replaced by the pydantic formatter
    #formatted_json = transform_response(theFormatter, response)
    #logger.info(f'response...  {count} ...' , formatted_json)
    return response


def generate(client,count,prompt,page):    
    logger.critical(f"generate - {prompt}")
    num_tokens_from_string(''.join([theSystemPrompt, prompt]), default_encoding, "input")
    #logger.critical(f"prompt-{prompt}")
    chat_completion = client.chat.completions.create(
      messages=[
            {"role": "system", "content": theSystemPrompt},
            {"role": "user",   "content": prompt}
        ],
        model=theModel,
        temperature = default_temperature
    )
    response = chat_completion.choices[0].message.content
    num_tokens_from_string(response, default_encoding, "output")
    logger.info(f'unformatted response...  {count} ...' , response)
    
    #This got replaced by the pydantic formatter
    #formatted_json = transform_response(theFormatter, response)
    #logger.info(f'response...  {count} ...' , formatted_json)
    return response

# Serial
def generate_serially(usecase, page, mode, prompt):  
    global clientSync, thePrompt  
    config = getConfig(prompts_file) 
    #thePrompt = (config[usecase]['user_prompt'][page][mode]['input'])  
    thePrompt = prompt        
   
    thePrompt = prompt_constrainer(page,thePrompt,-1)
    return [generate(clientSync, 0, thePrompt, page)]


# Parallel
async def generate_concurrently(usecase, page, mode, prompt):
    global clientAsync    
    #thePrompt = (config[usecase]['user_prompt'][page][mode]['input'])  
    thePrompt = prompt
    #Todo - Support negative prompts . Need to support at chunk level
    tasks = [async_generate(clientAsync,count, prompt_constrainer(page, thePrompt[count], count)) for count in range(len(thePrompt))]    
    # gather returns all the results when all the threads finish execution
    results = await asyncio.gather(*tasks)
    results = combine_jsons(results)
    #logger.critical(f"results...{results}")

    return results


def init_AI_client(model_family, model):
    global clientSync, clientAsync, theModel
    
    config = getConfig(config_file)
    if(model==None):
        theModel =  config[model_family]["preferred_model"]
    else:    
        theModel = model

    clientAsync = AsyncOpenAI(
        api_key  = config[model_family]["key"],
        base_url = config[model_family]["url"],
    )        
    clientSync = OpenAI(
        api_key  = config[model_family]["key"],
        base_url = config[model_family]["url"],
    )

def init_prompts(usecase, page, mode):
    global thePrompt,theSystemPrompt,theIdealResponse
    config = getConfig(prompts_file)     
    theSystemPrompt = config[usecase]['system_prompt']
    #logger.critical(f"theSystemPrompt-{theSystemPrompt}")
    theIdealResponse = config[usecase]['user_prompt'][page]['serial']['ideal_response']
  

def prompt_constrainer(page,thePrompt, count=None):
     
    page_index = page
    negativePrompt = ''
    thePrompt = replace_dates(thePrompt)
    sharedPrompt = thePrompt
    #Create copy so that we just get what the user said minus constraints 
    shared_data_instance.set_data('thePrompt', sharedPrompt)
    #logger.info(f"page_index-{page_index}")
    if(shared_data_instance.get_data('negative_prompt')== 'ON'):
        negativePrompt = fuzzyMatch(thePrompt)   
    logger.critical(f"negativePrompt-{negativePrompt}")

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
        #logger.info(f"response_schema_json-{response_schema_json}")
        constraints = "constraints"+ str(count)
       
        logger.info(f"constraints-{constraints}")
        logger.info(f"thePrompt-{thePrompt}")
        
        # @todo REFACTOR THIS
        if(count == -1):
            thePrompt = thePrompt.format(constraints=response_schema_json,missing_sections=negativePrompt)
            print(f"thePrompt-{thePrompt}")
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

    if (mode == "parallel" or  mode == "dual"):
        start = time.perf_counter()    
        response = asyncio.run(generate_concurrently(usecase, page, mode, prompt))
        logger.info(f"parallel response - {response}")
        end = time.perf_counter() - start
        logger.info(f"Parallel Program finished in {end:0.2f} seconds.")

    if (mode == "serial" or  mode == "dual"):   
        # Serial invoker
        start = time.perf_counter()
        response = generate_serially(usecase, page, mode, prompt)        
        end = time.perf_counter() - start        
        response = response[0]
        logger.info(f"Serial Program finished in {end:0.2f} seconds.")

    
    if(run_mode !=None):
        log(usecase, page, response, end, mode)

    time.sleep(sleep_time)

    return response



def log(usecase, page, response, time, mode):    
    #logger.critical(f"logging in db ...mode={mode}, response ={response}")
    global theFormatter, i_data, db_data, run_id,theIdealResponse,thePrompt
    matches_idealResponse = None
   
    theIdealResponse = theIdealResponse
    repro_difflib_similarity = None
    accuracy_difflib_similarity = None
    similarity_metric=''
    formatted_real_response = get_Pydantic_Filtered_Response(page,response,theFormatter)
    print(f"formatted_real_response - {formatted_real_response}" )

    if(len(db_data)>0):
        isBaseline = False
        first_response = db_data[0]['response']
        matches_baseline, reproducibility_changes, repro_difflib_similarity = compare(get_Pydantic_Filtered_Response(page, first_response,None), get_Pydantic_Filtered_Response(page,response,None))
    else:
        isBaseline = True
        matches_baseline = True
        reproducibility_changes = ''
        repro_difflib_similarity = 1.0

    if(accuracy_check == "ON"):
         logger.info(f"theIdealResponse - {theIdealResponse}, response -{response}")
         formatted_ideal_response = get_Pydantic_Filtered_Response(page,theIdealResponse, None)       
         print(f"formatted_ideal_response - {formatted_ideal_response}" )
         matches_idealResponse, idealResponse_changes,accuracy_difflib_similarity = compare(formatted_ideal_response, formatted_real_response)
    else:
        matches_idealResponse = ""
        idealResponse_changes = ""    
        formatted_ideal_response = ""


    #logger.info(f'accuracy_difflib_similarity-{accuracy_difflib_similarity}, repro_difflib_similarity-{repro_difflib_similarity}')
    
    #logger.info(f'similarity_metric-{similarity_metric}')
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
        'use_for_training': shared_data_instance.get_data('use_for_training')
    }

    db_data.append(i_data)
    #logger.info(f"** db_data - {db_data}")


def handleRequest(message:Message):
    global run_count, run_mode,db_data,run_id,accuracy_check
    logger.critical(f"usecase..-{message.usecase}, page-{message.page}, mode-{message.mode}, family-{message.family}, formatter-{message.formatter}, run_mode-{message.run_mode}, run_count-{message.run_count}, sleep-{message.sleep}, accuracy_check - {accuracy_check}, model-{message.model}, negative_prompt-{message.negative_prompt}, use_for_training - {message.use_for_training} ")
    logger.critical(f"prompt-{message.prompt}")
    config = getConfig(prompts_file) 

    run_mode = message.run_mode
    run_count = message.run_count 
    accuracy_check = message.accuracy_check
    shared_data_instance.set_data('negative_prompt', message.negative_prompt)
    shared_data_instance.set_data('use_for_training', message.use_for_training)
    shared_data_instance.set_data('error_detection', message.error_detection)
    message.prompt = add_space_after_punctuation(message.prompt)

    if(message.mode=="parallel"):   
        shared_data_instance.set_data('transcript',    message.prompt)
        prompts  = config[message.usecase]['user_prompt'][message.page]['parallel']['input'] 
        prompt =[]
        for count in range(len(prompts)):
            prompt.append(prompts[count].replace("{transcript}",message.prompt))
        message.prompt = prompt

    run_id = getRunID(8)
    response = [sync_async_runner(message.usecase, message.page, message.mode, message.family, message.formatter, message.run_mode, message.sleep, message.model, message.prompt) for _ in range(message.run_count)]
    confidence_map = shared_data_instance.get_data('confidence_map')
    logger.critical(f'confidence map - {confidence_map}')            
    insert(db_data)     
    
    if(accuracy_check=="ON"):
        print_accuracy_stats(readWithGroupFilter(run_id))

    return {"response": response, "confidence_map":confidence_map}


def main():


    global run_count, run_mode,db_data,run_id,accuracy_check
    # Create the parser
    parser = argparse.ArgumentParser(description="Run any prompt on any model.")

    # Add named arguments
    parser.add_argument("--usecase", type=str, required=False, help="the usecase")
    parser.add_argument("--page", type=str, required=False, help="the page name")
    parser.add_argument("--mode", type=str, required=False, help="mode serial or parallel")
    parser.add_argument("--model", type=str, required=False, help="A valid LLM model name. Check supported providers as well if model is present")
    parser.add_argument("--model_family", type=str, required=False, help="openai openrouter lmstudio groq")
    parser.add_argument("--formatter", type=str, required=False, help="response formatting function")
    parser.add_argument("--run_mode", type=str, required=False, help="same-llm, multiple-llm")
    parser.add_argument("--run_count", type=int, required=False, help="How many times to run")
    parser.add_argument("--sleep", type=int, required=False, help="Pause between invocations")
    parser.add_argument("--accuracy_check", type=str, required=False, help="Compare against supplied ideal response. Values - ON, OFF")
    parser.add_argument("--negative_prompt", type=str, required=False, help="Compute unspoken sections as NOT ASSESSED using fuzzy matching Values - ON, OFF")
    parser.add_argument("--use_for_training", type=str, required=False, help="Count this row for training / finetuning - true, false")
    parser.add_argument("--error_detection", type=str, required=False, help="Perform error detection/confidence map computation  - true, false")


    # Parse the arguments
    args = parser.parse_args()
    run_mode = args.run_mode
    run_count = args.run_count 
    accuracy_check = args.accuracy_check
    shared_data_instance.set_data('negative_prompt', args.negative_prompt)
    mode = args.mode
    use_for_training = args.use_for_training
    error_detection = args.error_detection
    
    if(run_mode == None):
        run_mode = default_run_mode
    if(run_count == None):
        run_count = default_run_count
    if(accuracy_check == None):
        accuracy_check = default_accuracy_check    
    if(use_for_training == None):
        use_for_training = default_use_for_training
    if(error_detection == None):
         error_detection = default_error_detection    
    shared_data_instance.set_data('use_for_training', use_for_training)
    shared_data_instance.set_data('error_detection', error_detection)
    # Parallel invoker
    if(mode == None):
        mode = default_mode        

    logger.critical(f"usecase-{args.usecase}, page-{args.page}, mode-{mode}, model_family-{args.model_family}, formatter-{args.formatter}, run_mode-{args.run_mode}, run_count-{args.run_count}, sleep-{args.sleep}, accuracy_check - {accuracy_check}, model-{args.model}, negative_prompt-{args.negative_prompt}, use_for_training - {use_for_training}")
    
    run_id = getRunID(8)
    config = getConfig(prompts_file) 

    if(mode=="parallel"):   
        transcript   = config[args.usecase]['user_prompt'][args.page][mode]['transcript']  
        transcript = add_space_after_punctuation(transcript)
        shared_data_instance.set_data('transcript', transcript)
        prompts  = config[args.usecase]['user_prompt'][args.page][mode]['input'] 
        prompt =[]
        for count in range(len(prompts)):
            prompt.append(prompts[count].replace("{transcript}",transcript))
    else:    
        prompt = config[args.usecase]['user_prompt'][args.page][mode]['input']  
        prompt = add_space_after_punctuation(prompt)

    if(run_mode == "multiple-llm"):
        logger.info(f"multiple-llm mode")
        result = parse_models(getConfig(config_file)) 
        for model_family, value in result.items():
            for model in value:
                #logger.info(f"model_family-{model_family} - model -{model}")
                [sync_async_runner(args.usecase, args.page, mode, model_family, args.formatter, run_mode, args.sleep, model, prompt)]
    else:    
        logger.info(f"same-llm mode")
        [sync_async_runner(args.usecase, args.page, mode, args.model_family, args.formatter, run_mode, args.sleep, args.model, prompt) for _ in range(run_count)]

    confidence_map = shared_data_instance.get_data('confidence_map')
    logger.critical(f'confidence map - {confidence_map}')    

    #logger.info(f"db_data - {db_data}")    
    if(run_mode !=None):
        insert(db_data)
        print_reproducibility_stats(readWithGroupFilter(run_id))    
    
    if(accuracy_check=="ON"):
        print_accuracy_stats(readWithGroupFilter(run_id))

if __name__ == "__main__":
    main()


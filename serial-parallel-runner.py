import asyncio
from openai import AsyncOpenAI, OpenAI
import time
import argparse
from pydantic_models import *
from constants import *
from util import *
from db_layer import *
from db_stats import *



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
    #print(f"generate - {prompt}")

    chat_completion = await client.chat.completions.create(
      messages=[
            {"role": "system", "content": theSystemPrompt},
            {"role": "user",   "content": prompt}
        ],
        model=theModel,
        temperature = default_temperature
    )

    formatted_json = format_response(theFormatter, chat_completion.choices[0].message.content)
    print(f'response...  {count} ...' , formatted_json)
    return formatted_json


def generate(client,count,prompt,page):    
    print(f"generate - {prompt}")
    num_tokens_from_string(''.join([theSystemPrompt, prompt]), default_encoding, "input")

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
    #print(f'unformatted response...  {count} ...' , response)
    
    try:
        cls = globals()[page]
    except:
        print("No pydantic model defined")
    else:    
        validated_response = cls.model_validate_json(response)
        print(f"validated_response-{validated_response}")    

    finally:       
        formatted_json = transform_response(theFormatter, response)
        print(f'response...  {count} ...' , formatted_json)
        return formatted_json

# Serial
def generate_serially(page):  
    global clientSync  
    return [generate(clientSync, 0, thePrompt, page)]


# Parallel
async def generate_concurrently(page):
    global clientAsync
    
    tasks = [async_generate(clientAsync,count, thePrompt[count]) for count in range(len(thePrompt))]    
    # gather returns all the results when all the threads finish execution
    results = await asyncio.gather(*tasks)
    #print(f"results...{results}")


def init_AI_client(model_family, model):
    global clientSync, clientAsync, theModel
    
    config = getConfig(config_file)
    if(model==None):
        theModel =  config[model_family]["model"]
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
    thePrompt = prompt_constrainer(usecase,page, config, mode)
    theSystemPrompt = config[usecase]['system_prompt']
    theIdealResponse = config[usecase]['user_prompt'][page][mode]['ideal_response']
  

def prompt_constrainer(usecase,page, config, mode):
   
    thePrompt = (config[usecase]['user_prompt'][page][mode]['input']) 

    try:
        cls = globals()[page]
    except:
        print(f"No pydantic model defined")
    else:    
        print(f"cls->{cls}")
        response_schema_dict = cls.model_json_schema()
        response_schema_json = json.dumps(response_schema_dict, indent=2)    
        thePrompt = thePrompt.format(constraints=response_schema_json)
    finally:
        return thePrompt
    



def sync_async_runner(usecase, page, mode, model_family,formatter, run_mode, sleep_time, model):    
    global theFormatter, i_data, db_data
  
    
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

    init_AI_client(model_family, model)
    init_prompts(usecase, page, mode)

    if (mode == "parallel" or  mode == "dual"):
        start = time.perf_counter()    
        response = asyncio.run(generate_concurrently(page))
        end = time.perf_counter() - start
        print(f"Parallel Program finished in {end:0.2f} seconds.")

    if (mode == "serial" or  mode == "dual"):   
        # Serial invoker
        start = time.perf_counter()
        response = generate_serially(page)        
        end = time.perf_counter() - start        
        print(f"Serial Program finished in {end:0.2f} seconds.")


    print(f"run mode - {run_mode}")
    if(run_mode !=None):
        log(usecase, page, response, end, mode)

    time.sleep(sleep_time)


def log(usecase, page, response, time, mode):    
    print(f"logging in db ...mode={mode}")
    global theFormatter, i_data, db_data, run_id,theIdealResponse
    matches_idealResponse = None
    response = format_response(response[0])
    theIdealResponse = format_response(theIdealResponse)
    repro_difflib_similarity = None
    accuracy_difflib_similarity = None
    similarity_metric=''

    if(len(db_data)>0):
        isBaseline = False
        first_response = format_response(db_data[0]['response'])
        matches_baseline, reproducibility_changes, repro_difflib_similarity = compare(first_response, response)
    else:
        isBaseline = True
        matches_baseline = True
        reproducibility_changes = ''
        repro_difflib_similarity = 1.0

    if(accuracy_check == "ON"):
         matches_idealResponse, idealResponse_changes,accuracy_difflib_similarity = compare(theIdealResponse, response)
    else:
        matches_idealResponse = ""
        idealResponse_changes = ""

    print(f'accuracy_difflib_similarity-{accuracy_difflib_similarity}, repro_difflib_similarity-{repro_difflib_similarity}')
    
    print(f'similarity_metric-{similarity_metric}')

    i_data = {
        'usecase':usecase,
        'mode':mode,
        'functionality':page,
        'llm':theModel,
        'llm_parameters':'temperature='+str(default_temperature),
        'isBaseline': isBaseline,
        'run_no': run_id,
        'system_prompt': theSystemPrompt,
        'user_prompt': thePrompt,
        'response': response,
        'ideal_response':theIdealResponse,
        'execution_time': time,
        'matches_baseline': matches_baseline,
        'matches_ideal':matches_idealResponse,
        'difference': reproducibility_changes,
        'ideal_response_difference': idealResponse_changes,
        'similarity_metric':f'accuracy_difflib_similarity->>{accuracy_difflib_similarity} -- repro_difflib_similarity->>{repro_difflib_similarity}'
    }

    db_data.append(i_data)
    #print(f"** db_data - {db_data}")

def main():
    global run_count, run_mode,db_data,run_id,accuracy_check
    # Create the parser
    parser = argparse.ArgumentParser(description="Run any prompt on any model.")

    # Add named arguments
    parser.add_argument("--usecase", type=str, required=False, help="the usecase")
    parser.add_argument("--page", type=str, required=False, help="the page name")
    parser.add_argument("--mode", type=str, required=False, help="mode serial or parallel")
    parser.add_argument("--model", type=str, required=False, help="A valid LLM model name. Check supported providers as well if model is present")
    parser.add_argument("--model_family", type=str, required=False, help="openai openrouter lmstudio")
    parser.add_argument("--formatter", type=str, required=False, help="response formatting function")
    parser.add_argument("--run_mode", type=str, required=False, help="same-llm, multiple-llm")
    parser.add_argument("--run_count", type=int, required=False, help="How many times to run")
    parser.add_argument("--sleep", type=int, required=False, help="Pause between invocations")
    parser.add_argument("--accuracy_check", type=str, required=False, help="Compare against supplied ideal response. Values - ON, OFF")


    # Parse the arguments
    args = parser.parse_args()
    run_mode = args.run_mode
    run_count = args.run_count 
    accuracy_check = args.accuracy_check
    

    if(run_mode == None):
        run_mode = default_run_mode
    if(run_count == None):
        run_count = default_run_count
    if(accuracy_check == None):
        accuracy_check = default_accuracy_check

    print(f"usecase-{args.usecase}, page-{args.page}, mode-{args.mode}, model_family-{args.model_family}, formatter-{args.formatter}, run_mode-{args.run_mode}, run_count-{args.run_count}, sleep-{args.sleep}, accuracy_check - {accuracy_check}, model-{args.model}")
    
    if(run_mode !=None):
        run_id = getRunID(8)

    [sync_async_runner(args.usecase, args.page, args.mode, args.model_family, args.formatter, args.run_mode, args.sleep, args.model) for _ in range(run_count)]
    #print(f"db_data - {db_data}")
    
    if(run_mode !=None):
        insert(db_data)
        print_reproducibility_stats(readWithGroupFilter(run_id))    
    
    if(accuracy_check=="ON"):
        print_accuracy_stats(readWithGroupFilter(run_id))

if __name__ == "__main__":
    main()


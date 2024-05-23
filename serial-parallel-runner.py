import asyncio
from openai import AsyncOpenAI, OpenAI
import time
import argparse
from constants import *
from util import *

clientSync = any
clientAsync = any
theModel = any
theFormatter = None
thePrompt = None
theSystemPrompt= None
# Serial

async def async_generate(client,count,prompt):    
    print(f"generate - {prompt}")
    chat_completion = await client.chat.completions.create(
      messages=[
            {"role": "system", "content": theSystemPrompt},
            {"role": "user",   "content": prompt}
        ],
        model=theModel,
    )

    formatted_json = format_response(theFormatter, chat_completion.choices[0].message.content)
    print(f'response...  {count} ...' , formatted_json)
    return formatted_json


def generate(client,count,prompt):    
    print(f"generate - {prompt}")
    chat_completion = client.chat.completions.create(
      messages=[
            {"role": "system", "content": theSystemPrompt},
            {"role": "user",   "content": prompt}
        ],
        model=theModel,
    )
 
    formatted_json = format_response(theFormatter, chat_completion.choices[0].message.content)
    print(f'response...  {count} ...' , formatted_json)
    return formatted_json

# Serial
def generate_serially(page):  
    global clientSync  
    [generate(clientSync, 0, thePrompt)]


# Parallel
async def generate_concurrently(page):
    global clientAsync
    tasks = [async_generate(clientAsync,count, thePrompt[count]) for count in range(len(thePrompt))]
    # gather returns all the results when all the threads finish execution
    results = await asyncio.gather(*tasks)
    #print(f"results...{results}")


def init_AI_client(model_family):
    global clientSync, clientAsync, theModel
    
    config = getConfig(config_file)
    theModel =  config[model_family]["model"]

    clientAsync = AsyncOpenAI(
        api_key  = config[model_family]["key"],
        base_url = config[model_family]["url"],
    )        
    clientSync = OpenAI(
        api_key  = config[model_family]["key"],
        base_url = config[model_family]["url"],
    )

def init_prompts(usecase, page, mode):
    global thePrompt,theSystemPrompt
    config = getConfig(prompts_file)  
    thePrompt = config[usecase]['user_prompt'][page][mode]
    theSystemPrompt = config[usecase]['system_prompt']
    
  

def sync_async_runner(usecase, page, mode, model_family,formatter):    
    global theFormatter

    print(f"page-{page}, mode-{mode}, model_family-{model_family}, formatter-{formatter}")
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

    init_AI_client(model_family)
    init_prompts(usecase, page, mode)

    if (mode == "parallel" or  mode == "dual"):
        start = time.perf_counter()    
        asyncio.run(generate_concurrently(page))
        end = time.perf_counter() - start
        print(f"Parallel Program finished in {end:0.2f} seconds.")

    if (mode == "serial" or  mode == "dual"):   
        # Serial invoker
        start = time.perf_counter()
        generate_serially(page)
        end = time.perf_counter() - start
        print(f"Serial Program finished in {end:0.2f} seconds.")



def main():
    # Create the parser
    parser = argparse.ArgumentParser(description="Run any prompt on any model.")

    # Add named arguments
    parser.add_argument("--usecase", type=str, required=False, help="the usecase")
    parser.add_argument("--page", type=str, required=False, help="the page name")
    parser.add_argument("--mode", type=str, required=False, help="mode serial or parallel")
    parser.add_argument("--model_family", type=str, required=False, help="openai openrouter lmstudio")
    parser.add_argument("--formatter", type=str, required=False, help="response formatting function")

    # Parse the arguments
    args = parser.parse_args()


    [sync_async_runner(args.usecase, args.page, args.mode, args.model_family, args.formatter) for _ in range(1)]
   

if __name__ == "__main__":
    main()


import os
import asyncio
from openai import AsyncOpenAI, OpenAI
import time
import sys
import json
from constants import *


# Function to convert JSON to the required format
def convert_to_required_format(data):
    converted_data = {}
    print(f"data - {data}")
    data = json.loads(data)
    for key, value in data.items():
        isDict = isinstance(value, dict)
        print(f"value ={value} - isDict={isDict}")
        if isinstance(value, dict):
            for sub_key, sub_value in value.items():
                new_key = f"{key} {sub_key}"
                converted_data[new_key] = sub_value
        else:
            converted_data[key] = value        
    return converted_data

# Async client
clientAsync = AsyncOpenAI(
   api_key=os.environ.get("OPENAI_API_KEY"),
)

# Sync client
clientSync = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)

# Parallel
async def async_generate(count, prompt):
    print(f"prompt-{prompt}")
    chat_completion = await clientAsync.chat.completions.create(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": prompt}
        ],
        model=model,
    )    
    formatted_json = format_response(chat_completion.choices[0].message.content)
    print(f'Parallel response...  {count} ...' , formatted_json)
    return formatted_json

def format_response(response):
    converted_json = convert_to_required_format(response)
    formatted_json = json.dumps(converted_json, indent=4)    

    return formatted_json


async def generate_concurrently(page):
    
    tasks = [async_generate(count, prompt_parallel_dict[page][count]) for count in range(len(prompt_parallel_dict[page]))]
    # gather returns all the results when all the threads finish execution
    results = await asyncio.gather(*tasks)
    #print(f"results...{results}")


# Serial

def sync_generate(count,prompt):
    chat_completion = clientSync.chat.completions.create(
      messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": prompt}
        ],
        model=model,
    )
    formatted_json = format_response(chat_completion.choices[0].message.content)
    print(f'Parallel response...  {count} ...' , formatted_json)
    return formatted_json

def generate_serially(page):    
    [sync_generate(count, prompt_serial_dict[page][count]) for count in range(len(prompt_serial_dict[page]))]
    


def sync_async_runner(page, mode):
    # Parallel invoker
    if(mode == None):
        mode = "dual"

    if(page == None):
        page = "cchpi"     

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

# Get command-line arguments
arguments = sys.argv[1:]  # Exclude the script name

# Print the arguments
print("Command-line arguments:", arguments)
print("model:", model)
[sync_async_runner(arguments[0],arguments[1]) for _ in range(1)]
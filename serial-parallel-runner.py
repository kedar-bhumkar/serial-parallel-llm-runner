import os
import asyncio
from openai import AsyncOpenAI, OpenAI
import time
import sys

from constants import *

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
        model="gpt-3.5-turbo",
    )
    print(f'Parallel response...  {count} ...' , chat_completion.choices[0].message.content)
    return chat_completion.choices[0].message.content

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
        model="gpt-3.5-turbo",
    )
    print(f'\n\n Serial response...  {count} ...' , chat_completion.choices[0].message.content)
    return chat_completion.choices[0].message.content

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
[sync_async_runner(arguments[0],arguments[1]) for _ in range(1)]
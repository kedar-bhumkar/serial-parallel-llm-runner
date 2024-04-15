import os
import asyncio
from openai import AsyncOpenAI, OpenAI
import time

# small changs to system prompt can have big impact on overall response. Below step-by-step, emotional and objective prompting is used
system_prompt = """ You are a helpful clinical assistant. Look at the below Transcript from a doctor assessing a patient visit. You need to 
                    interpret it and return the response as mentioned in the Return_data_constraints section. It should contain the exact keys memtioned in that section. 
                    Keys are defined before the hyper seperator. Return the response as JSON.
                    Please do not hallucinate. Do not guess. Cross check your work. Think step by step. If you get this wrong someone's health may get impacted adversly. If you get it correct you will recive $100
                """

# Define an array of prompts broken by section(s)
prompt_array = [
        """Transcript:I visited a patient John Summers on April 1,2024 as part of a Follow up visit a this home. He is an old member of the program.
           Return_data_constraints: Visit Type - (Comprehensive,Annual,Follow-up,Acute,Acute/Reassessment,Discharge,RN Visit,RN Acute/Reassessment,RN Follow up,Post Transition,Post Hospital,Post Hospital Inpatient,Post Hospital ER/OBS/Outpatient,Superbill,Post Hospital Annual,Risk Stratification Assessment,SNF Initial,SNF Discharge Summary,SNF Interim Discharge Summary,SNF Follow up,SNF Admit,Telephonic RN Follow up,Telephonic Follow-up,Post Hospital Initial,Post Hospital Initial,Quarterly)
                                    Date of Visit - (should be in Date format , blank)""",

        """Transcript:I visited a patient John Summers on April 1,2024 as part of a Follow up visit a this home. He is an old member of the program.
           Return_data_constraints:   Member New or Established - (New,Established)
                                      Place of Service - (Home Nursing Facility, Skilled Nursing Facility, Assisted Living Facility, blank)""",
        """Transcript:I visited a patient John Summers on April 1,2024 as part of a Follow up visit a this home. He is an old member of the program. He had a  Fall from staircase and had been to the ER.      
                      He suffers from hypertension, had undergone a CABG 2 years back and has acute bronchotis.
           Return_data_constraints: Has there been a Fall? - (Yes,No)
                                    History of present illness - (record here any  medical history mentioned including diseases, conditions which he/she may have had) """                      
]
    

prompt_serial = ["""Transcript:I visited a patient John Summers on April 1,2024 as part of a Follow up visit a this home. He is an old member of the program.He is an old member of the program. He had a  Fall from staircase and had been to the ER.      
                      He suffers from hypertension, had undergone a CABG 2 years back and has acute bronchotis.
                    Return_data_constraints: Visit Type - (Comprehensive,Annual,Follow-up,Acute,Acute/Reassessment,Discharge,RN Visit,RN Acute/Reassessment,RN Follow up,Post Transition,Post Hospital,Post Hospital Inpatient,Post Hospital ER/OBS/Outpatient,Superbill,Post Hospital Annual,Risk Stratification Assessment,SNF Initial,SNF Discharge Summary,SNF Interim Discharge Summary,SNF Follow up,SNF Admit,Telephonic RN Follow up,Telephonic Follow-up,Post Hospital Initial,Post Hospital Initial,Quarterly)
                                             Date of Visit - (should be in Date format , blank)
                                             Member New or Established - (New,Established)
                                             Place of Service - (Home Nursing Facility, Skilled Nursing Facility, Assisted Living Facility, blank)
                                             Has there been a Fall? - (Yes,No)
                                             History of present illness - (record here any  medical history mentioned including diseases, conditions which he/she may have had) 
                 """]    

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

async def generate_concurrently():
    
    tasks = [async_generate(count, prompt_array[count]) for count in range(len(prompt_array))]
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

def generate_serially():    
    [sync_generate(count, prompt_serial[count]) for count in range(len(prompt_serial))]
    


def sync_async_runner():
    # Parallel invoker
    start = time.perf_counter()
    asyncio.run(generate_concurrently())
    end = time.perf_counter() - start
    print(f"Parallel Program finished in {end:0.2f} seconds.")


    # Serial invoker
    start = time.perf_counter()
    generate_serially()
    end = time.perf_counter() - start
    print(f"Serial Program finished in {end:0.2f} seconds.")


[sync_async_runner() for _ in range(1)]
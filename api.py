from typing import Optional, Union
from fastapi import FastAPI, Request
from pydantic import BaseModel, Field
import time
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from constants import *
from main import handleRequest
from pydantic_models import Message, AudioMessage
from audio_manager import *

theResponse = {"response": ["{\n  \"Reviewed_with\": \"Member\",\n  \"CONSTITUTIONAL\": {\n    \"Constitutional_ROS__c\": \"Assessed\",\n    \"Not_Assessed_Reason\": null,\n    \"Reviewed_and_Negative\": \"true\",\n    \"Fever\": \"NA\",\n    \"Chills\": \"NA\",\n    \"Fatigue\": \"NA\",\n    \"Change_in_Sleep\": \"NA\",\n    \"Change_in_Appetite\": \"NA\",\n    \"Unintentional_Weight_Loss\": \"NA\",\n    \"Unintentional_Weight_Gain\": \"NA\",\n    \"Night_Sweats\": \"NA\",\n    \"Weakness\": \"NA\"\n  },\n  \"EENT_EYES\": {\n    \"Eyes_ROS__c\": \"Assessed\",\n    \"Not_Assessed_Reason\": null,\n    \"Reviewed_and_Negative\": \"NA\",\n    \"Blurred_Vision\": \"NA\",\n    \"Drainage\": \"NA\",\n    \"Itching\": \"NA\",\n    \"Pain\": \"NA\",\n    \"Changes_in_Vision\": \"NA\",\n    \"Tearing\": \"NA\",\n    \"Dryness\": \"NA\",\n    \"Redness\": \"NA\",\n    \"Flashing_Lights\": \"NA\",\n    \"Double_Vision\": \"NA\",\n    \"Glasses_Contacts\": \"true\"\n  },\n  \"EENT_NOSE_AND_THROAT\": {\n    \"Nose_Throat_ROS__c\": \"Assessed\",\n    \"Not_Assessed_Reason\": null,\n    \"Reviewed_and_Negative\": \"NA\",\n    \"Nasal_Congestion\": \"NA\",\n    \"Sinus_Pressure\": \"NA\",\n    \"Nosebleeds\": \"NA\",\n    \"Hoarseness\": \"NA\",\n    \"Sore_Throat\": \"NA\",\n    \"Difficulty_Swallowing\": \"true\",\n    \"Difficulty_Chewing\": \"NA\",\n    \"Poor_Dentition\": \"NA\",\n    \"Sore_Tongue\": \"NA\",\n    \"Bleeding_Gums\": \"NA\",\n    \"Tooth_Pain\": \"NA\"\n  },\n  \"EENT_EARS\": {\n    \"Ears_ROS__c\": \"Not Assessed\",\n    \"Not_Assessed_Reason\": \"Other\",\n    \"Reviewed_and_Negative\": \"NA\",\n    \"Tinnitus\": \"NA\",\n    \"Ear_Pain\": \"NA\",\n    \"Change_in_Hearing\": \"NA\",\n    \"Drainage\": \"NA\"\n  },\n  \"CARDIOVASCULAR\": {\n    \"Cardiovascular_ROS__c\": \"Assessed\",\n    \"Not_Assessed_Reason\": null,\n    \"Reviewed_and_Negative\": \"true\",\n    \"Chest_Pain\": \"NA\",\n    \"Palpitations\": \"NA\",\n    \"Lightheadedness\": \"NA\",\n    \"Dizziness\": \"NA\",\n    \"Syncope\": \"NA\",\n    \"Edema\": \"NA\",\n    \"Pain_with_Walking\": \"NA\",\n    \"Use_of_Compression_Stockings\": \"NA\"\n  },\n  \"GERIATRIC_SYNDROME\": {\n    \"Compared_to_others_your_age\": \"Very Good\",\n    \"Self_Assessed_Mental\": \"Same\"\n  },\n  \"GENITOURINARY\": {\n    \"Genitourinary_ROS__c\": \"Assessed\",\n    \"Not_Assessed_Reason\": null,\n    \"Reviewed_and_Negative\": \"NA\",\n    \"Urgency\": \"NA\",\n    \"Frequency\": \"NA\",\n    \"Difficulty_Urinating\": \"true\",\n    \"Burning_with_Urination\": \"NA\",\n    \"Blood_in_Urine\": \"NA\",\n    \"Stress_Incontinence\": \"NA\",\n    \"Frequent_Infections\": \"NA\",\n    \"Urge_Incontinence\": \"NA\",\n    \"Nocturia\": \"NA\",\n    \"Testicular_Pain\": \"NA\",\n    \"Vaginal_Bleeding\": \"NA\",\n    \"Scrotal_Swelling\": \"NA\"\n  },\n  \"NEUROLOGICAL\": {\n    \"Neurological_ROS__c\": \"Assessed\",\n    \"Not_Assessed_Reason\": null,\n    \"Reviewed_and_Negative\": \"NA\",\n    \"Cognitive_Impairment\": \"false\",\n    \"Numbness\": \"true\",\n    \"Tingling\": \"true\",\n    \"Prickling_Sensation\": \"true\",\n    \"Burning_Sensation\": \"NA\",\n    \"Itching_Sensation\": \"NA\",\n    \"Pins_and_Needles\": \"true\",\n    \"Pain_d_t_Innocuous_Stimuli\": \"NA\",\n    \"Increased_Sensitivity_to_Pain\": \"NA\",\n    \"Dizziness\": \"NA\",\n    \"Lightheadedness\": \"NA\",\n    \"Vertigo\": \"NA\",\n    \"Fainting\": \"NA\",\n    \"Loss_of_Balance\": \"NA\",\n    \"Memory_Problems\": \"NA\",\n    \"Difficulty_Speaking\": \"NA\",\n    \"Motor_Weakness\": \"NA\",\n    \"Seizures\": \"NA\"\n  },\n  \"ENDOCRINE\": {\n    \"Endocrine_ROS__c\": \"Assessed\",\n    \"Not_Assessed_Reason\": null,\n    \"Reviewed_and_Negative\": \"NA\",\n    \"Excessive_Thirst\": \"true\",\n    \"Excessive_Hunger\": \"true\",\n    \"Increased_Urination\": \"NA\",\n    \"Heat_Intolerance\": \"true\",\n    \"Cold_Intolerance\": \"true\",\n    \"Hypoglycemic_Events\": \"NA\",\n    \"Hyperglycemic_Events\": \"NA\"\n  },\n  \"PSYCHOLOGICAL\": {\n    \"Psychological_ROS__c\": \"Assessed\",\n    \"Not_Assessed_Reason\": null,\n    \"Reviewed_and_Negative\": \"NA\",\n    \"Depression\": \"true\",\n    \"Withdrawn\": \"NA\",\n    \"Anxiety\": \"NA\",\n    \"Hallucinations\": \"NA\",\n    \"Sadness\": \"NA\",\n    \"Insomnia\": \"NA\",\n    \"Periods_of_High_Energy\": \"NA\",\n    \"Racing_Thoughts\": \"NA\",\n    \"Suicidal_Ideations\": \"NA\",\n    \"Homicidal_Ideations\": \"NA\",\n    \"Angry\": \"NA\",\n    \"Upset\": \"NA\",\n    \"Euthymic_Mood\": \"NA\"\n  },\n  \"PAIN_ASSESSMENT\": {\n    \"Cognitive_Impairment\": false,\n    \"Cognitive_Impairment_Type\": null,\n    \"Pain_Assessment_Completed\": \"Verbal\",\n    \"Verbal_Pain_Scale\": 0,\n    \"Description_of_Pain\": null,\n    \"Does_not_appear_to_be_in_pain\": true,\n    \"Non_Verbal_Pain_Indicators\": null,\n    \"What_Eases_the_Pain\": null,\n    \"Pain_Notes\": null\n  },\n  \"HEAD_AND_NECK\": {\n    \"Head_ROS__c\": \"Not Assessed\",\n    \"Not_Assessed_Reason\": \"Other\",\n    \"Reviewed_and_Negative\": \"NA\",\n    \"Headaches\": \"NA\",\n    \"Dizziness\": \"NA\",\n    \"Hair_Loss\": \"NA\",\n    \"Swollen_Glands\": \"NA\",\n    \"Neck_Stiffness\": \"NA\",\n    \"Previous_Head_Injury\": \"NA\",\n    \"Previous_Head_Injury_Describe\": null\n  },\n  \"RESPIRATORY\": {\n    \"Respiratory_ROS__c\": \"Assessed\",\n    \"Not_Assessed_Reason\": null,\n    \"Reviewed_and_Negative\": \"true\",\n    \"Chronic_Cough\": \"NA\",\n    \"Acute_Cough\": \"NA\",\n    \"Sputum\": \"NA\",\n    \"Shortness_of_Breath\": \"NA\",\n    \"Wheezing\": \"NA\",\n    \"Snoring\": \"NA\",\n    \"CPAP_BiPAP\": \"NA\"\n  },\n  \"GASTROINTESTINAL\": {\n    \"Gastrointestinal_ROS__c\": \"Assessed\",\n    \"Not_Assessed_Reason\": null,\n    \"Reviewed_and_Negative\": \"true\",\n    \"Heartburn\": \"NA\",\n    \"Nausea\": \"NA\",\n    \"Abdominal_Pain\": \"NA\",\n    \"Vomiting\": \"NA\",\n    \"Vomiting_Blood\": \"NA\",\n    \"Diarrhea\": \"NA\",\n    \"Constipation\": \"NA\",\n    \"Hemorrhoids\": \"NA\",\n    \"Fecal_Incontinence\": \"NA\",\n    \"Black_Stools\": \"NA\",\n    \"Bloody_Stools\": \"NA\",\n    \"Change_in_Bowel_Habits\": \"NA\"\n  },\n  \"INTEGUMENTARY\": {\n    \"Integumentary_ROS__c\": \"Not Assessed\",\n    \"Not_Assessed_Reason\": \"Other\",\n    \"Reviewed_and_Negative\": \"NA\",\n    \"Rash\": \"NA\",\n    \"Bruising\": \"NA\",\n    \"Abrasions\": \"NA\",\n    \"Skin_Tears\": \"NA\",\n    \"Lacerations\": \"NA\",\n    \"Surgical_Wounds\": \"NA\",\n    \"Diabetic_Ulcers\": \"NA\",\n    \"Pressure_Ulcers\": \"NA\",\n    \"Foot_Ulcers\": \"NA\",\n    \"Stasis_Ulcers\": \"NA\",\n    \"Poor_Healing_of_Wounds\": \"NA\",\n    \"Atypical_Skin_Lesion\": \"NA\",\n    \"Hair_Loss\": \"NA\"\n  },\n  \"MUSCULOSKELETAL\": {\n    \"Muscoloskeletal_ROS__c\": \"Assessed\",\n    \"Not_Assessed_Reason\": null,\n    \"Reviewed_and_Negative\": \"NA\",\n    \"Gait_Disturbances\": \"true\",\n    \"Muscle_Cramping\": \"NA\",\n    \"Muscle_Pain\": \"NA\",\n    \"Joint_Pain\": \"NA\",\n    \"Joint_Pain_Location\": null,\n    \"Joint_Stiffness\": \"NA\",\n    \"Joint_Stiffness_Location\": null,\n    \"Fractures\": \"true\",\n    \"Fractures_Locations\": \"Left femur\",\n    \"Date_of_Last_Fracture\": \"1996\"\n  },\n  \"DIABETIC_TESTING\": {\n    \"Non_Diabetic_Member\": true,\n    \"Member_Reported\": true,\n    \"Routine_Diabetic_Testing\": false,\n    \"Member_Reported_A1C\": null,\n    \"A1C_Date\": null\n  },\n  \"additional_notes\": \"He was once incarcerated in jail for 2 weeks.\"\n}" ],"confidence_map":{}}


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Server startup .....")    
    yield
    print("Server shutdown .......")

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    print(f"Request took {process_time} secs to complete")
    return response


@app.post("/acd")
def doChat( request:Request, message:Message):    
    print("Inside /acd")    
    
    print(f'prompt -  {message.prompt}, mode - {message.mode}')           

    if(message.formatter == None and message.usecase=="acd" and  (message.page == "ros" or message.page =="pe")):
        message.formatter = default_formatter

    response = handleRequest(message)

    return {"acd_response": response}
    #return {"acd_response": theResponse}

@app.post("/transcribe")
def doTranscribe( request:Request, audioMessage: AudioMessage):    
    print("Inside doTranscribe")    
    

    return transcribe(audioMessage.audio)

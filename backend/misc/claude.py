import anthropic
import json
from backend.core.model.pydantic_models import *
import os

theSystemPrompt =   """As a clinical assistant, your role is to carefully analyze a transcript from a doctor's assessment of a member visit. 
                    Your task is to interpret the transcript diligently and return the response in accordance with the 'Return_data_constraints' section. 
                    This section outlines specific details that must be included in your response. Your response must be accurately formatted as JSON to ensure
                    seamless integration with the system.It is crucial to avoid making any assumptions or errors in your analysis, as inaccuracies could have a
                    negative impact on the member's health. A correct response will earn you $100. Your attention to detail and precision in interpreting the transcript 
                    are essential to providing high-quality care for THE member. The response should adhere to the pydantic class model specification mentioned in the Return_data_constraints section.
                    This section has literal values and your response should only include one of these. Do not use False value if there is no mention of the condition in the transcript. 
                    Instead use NA if it is present in the specification. E.g.if the transcript includes a mention of a symptom called numbness then use the value true or false as per what is written. 
                    Else use NA. This is super important. DO NOT USE FALSE if the symptom is not mentioned. Another example: if the Literal values for a class variable are mentioned as 'Cognitive Impairment, member/Caregiver Refused, Poor Historian, Unconscious, Unresponsive, Other' only select an asnwer from these values.
                    Ensure the exact letter casing is maintained in response. E.g. if true is mentioned output true and not True. IF Follow-up is expected do not use lower casing and return follow-up
                    Do not add the characters ``` json anywhere in the response. Do not respond with messages like 'Here is the response in the required JSON format:' """

thePrompt = """ Transcript:Reviewed the following with the member today. Geriatric syndrome was assessed.
member reports overall health to be Very good
No change in Self-assessed mental health
Pain assessment completed verbally.
Verbal pain scale reported as  0 
Constitutional Reviewed and negative.
Eyes Assessed. members Uses glasses
Nose and throat Assessed. member reports  difficulty swallowing.
Respiratory was reviewed and negative.
Cardiovascular was Reviewed and negative.
Gastrointestinal was reviewed and negative.
Genitourinary was Assessed. member reports  difficulty urinating.
Cognitive impairment was not seen
NEUROLOGICAL was assessed . The member said she has had Numbness and tingling with Prickling sensation
It feels like Pins and needles
Musculoskeletal  assessed and gait disturbances were seen.
Reports history of fractures on Left femur. The last fracture was in 1996.
member informed that he is Non-diabetic.
Endocrine was assessed. The patient has hot and cold intolerance and has excessive thirst and hunger
Psychological assessment was done. She Reports depression. Manages it with activities.
Some additional notes about the member - He was once incacerated in jail for 2 weeks.
The below sections were not assessed:  The below sections were not assessed: Ears, NoseThroat, Nose and Throat, HeadAndNeck, Head and Neck, HeadandNeck, GeriatricSyndrome, Neck, Integumentary, Diabetic
Return_data_constraints: {constraints}"
"""

fullPrompt = """  Transcript:Reviewed the following with the member today. Geriatric syndrome was assessed.
member reports overall health to be Very good
No change in Self-assessed mental health
Pain assessment completed verbally.
Verbal pain scale reported as  0 
Constitutional Reviewed and negative.
Eyes Assessed. members Uses glasses
Nose and throat Assessed. member reports  difficulty swallowing.
Respiratory was reviewed and negative.
Cardiovascular was Reviewed and negative.
Gastrointestinal was reviewed and negative.
Genitourinary was Assessed. member reports  difficulty urinating.
Cognitive impairment was not seen
NEUROLOGICAL was assessed . The member said she has had Numbness and tingling with Prickling sensation
It feels like Pins and needles
Musculoskeletal  assessed and gait disturbances were seen.
Reports history of fractures on Left femur. The last fracture was in 1996.
member informed that he is Non-diabetic.
Endocrine was assessed. The patient has hot and cold intolerance and has excessive thirst and hunger
Psychological assessment was done. She Reports depression. Manages it with activities.
Some additional notes about the member - He was once incacerated in jail for 2 weeks.
The below sections were not assessed:  The below sections were not assessed: Ears, NoseThroat, Nose and Throat, HeadAndNeck, Head and Neck, HeadandNeck, GeriatricSyndrome, Neck, Integumentary, Diabetic
Return_data_constraints: {
  "$defs": {
    "Cardiovascular": {
      "properties": {
        "Cardiovascular_ROS__c": {
          "enum": [
            "Assessed",
            "Not Assessed"
          ],
          "title": "Cardiovascular Ros  C",
          "type": "string"
        },
        "Not_Assessed_Reason": {
          "anyOf": [
            {
              "enum": [
                "Cognitive Impairment",
                "Patient/Caregiver Refused",
                "Poor Historian",
                "Unconscious",
                "Unresponsive",
                "Other"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Not Assessed Reason"
        },
        "Reviewed_and_Negative": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Reviewed And Negative"
        },
        "Chest_Pain": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Chest Pain"
        },
        "Palpitations": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Palpitations"
        },
        "Lightheadedness": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Lightheadedness"
        },
        "Dizziness": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Dizziness"
        },
        "Syncope": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Syncope"
        },
        "Edema": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Edema"
        },
        "Pain_with_Walking": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Pain With Walking"
        },
        "Use_of_Compression_Stockings": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Use Of Compression Stockings"
        }
      },
      "required": [
        "Cardiovascular_ROS__c",
        "Not_Assessed_Reason",
        "Reviewed_and_Negative",
        "Chest_Pain",
        "Palpitations",
        "Lightheadedness",
        "Dizziness",
        "Syncope",
        "Edema",
        "Pain_with_Walking",
        "Use_of_Compression_Stockings"
      ],
      "title": "Cardiovascular",
      "type": "object"
    },
    "Constitutional": {
      "properties": {
        "Constitutional_ROS__c": {
          "enum": [
            "Assessed",
            "Not Assessed"
          ],
          "title": "Constitutional Ros  C",
          "type": "string"
        },
        "Not_Assessed_Reason": {
          "anyOf": [
            {
              "enum": [
                "Cognitive Impairment",
                "Patient/Caregiver Refused",
                "Poor Historian",
                "Unconscious",
                "Unresponsive",
                "Other"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Not Assessed Reason"
        },
        "Reviewed_and_Negative": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Reviewed And Negative"
        },
        "Fever": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Fever"
        },
        "Chills": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Chills"
        },
        "Fatigue": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Fatigue"
        },
        "Change_in_Sleep": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Change In Sleep"
        },
        "Change_in_Appetite": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Change In Appetite"
        },
        "Unintentional_Weight_Loss": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Unintentional Weight Loss"
        },
        "Unintentional_Weight_Gain": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Unintentional Weight Gain"
        },
        "Night_Sweats": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Night Sweats"
        },
        "Weakness": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Weakness"
        }
      },
      "required": [
        "Constitutional_ROS__c",
        "Not_Assessed_Reason",
        "Reviewed_and_Negative",
        "Fever",
        "Chills",
        "Fatigue",
        "Change_in_Sleep",
        "Change_in_Appetite",
        "Unintentional_Weight_Loss",
        "Unintentional_Weight_Gain",
        "Night_Sweats",
        "Weakness"
      ],
      "title": "Constitutional",
      "type": "object"
    },
    "DiabeticTesting": {
      "properties": {
        "Non_Diabetic_Member": {
          "title": "Non Diabetic Member",
          "type": "boolean"
        },
        "Member_Reported": {
          "title": "Member Reported",
          "type": "boolean"
        },
        "Routine_Diabetic_Testing": {
          "title": "Routine Diabetic Testing",
          "type": "boolean"
        },
        "Member_Reported_A1C": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Member Reported A1C"
        },
        "A1C_Date": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "A1C Date"
        }
      },
      "required": [
        "Non_Diabetic_Member",
        "Member_Reported",
        "Routine_Diabetic_Testing",
        "Member_Reported_A1C",
        "A1C_Date"
      ],
      "title": "DiabeticTesting",
      "type": "object"
    },
    "Ears": {
      "properties": {
        "Ears_ROS__c": {
          "enum": [
            "Assessed",
            "Not Assessed"
          ],
          "title": "Ears Ros  C",
          "type": "string"
        },
        "Not_Assessed_Reason": {
          "anyOf": [
            {
              "enum": [
                "Cognitive Impairment",
                "Patient/Caregiver Refused",
                "Poor Historian",
                "Unconscious",
                "Unresponsive",
                "Other"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Not Assessed Reason"
        },
        "Reviewed_and_Negative": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Reviewed And Negative"
        },
        "Tinnitus": {
          "anyOf": [
            {
              "enum": [
                "Left",
                "Right",
                "Bilateral",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Tinnitus"
        },
        "Ear_Pain": {
          "anyOf": [
            {
              "enum": [
                "Left",
                "Right",
                "Bilateral",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Ear Pain"
        },
        "Change_in_Hearing": {
          "anyOf": [
            {
              "enum": [
                "Left",
                "Right",
                "Bilateral",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Change In Hearing"
        },
        "Drainage": {
          "anyOf": [
            {
              "enum": [
                "Left",
                "Right",
                "Bilateral",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Drainage"
        }
      },
      "required": [
        "Ears_ROS__c",
        "Not_Assessed_Reason",
        "Reviewed_and_Negative",
        "Tinnitus",
        "Ear_Pain",
        "Change_in_Hearing",
        "Drainage"
      ],
      "title": "Ears",
      "type": "object"
    },
    "Endocrine": {
      "properties": {
        "Endocrine_ROS__c": {
          "enum": [
            "Assessed",
            "Not Assessed"
          ],
          "title": "Endocrine Ros  C",
          "type": "string"
        },
        "Not_Assessed_Reason": {
          "anyOf": [
            {
              "enum": [
                "Cognitive Impairment",
                "Patient/Caregiver Refused",
                "Poor Historian",
                "Unconscious",
                "Unresponsive",
                "Other"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Not Assessed Reason"
        },
        "Reviewed_and_Negative": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Reviewed And Negative"
        },
        "Excessive_Thirst": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Excessive Thirst"
        },
        "Excessive_Hunger": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Excessive Hunger"
        },
        "Increased_Urination": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Increased Urination"
        },
        "Heat_Intolerance": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Heat Intolerance"
        },
        "Cold_Intolerance": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Cold Intolerance"
        },
        "Hypoglycemic_Events": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Hypoglycemic Events"
        },
        "Hyperglycemic_Events": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Hyperglycemic Events"
        }
      },
      "required": [
        "Endocrine_ROS__c",
        "Not_Assessed_Reason",
        "Reviewed_and_Negative",
        "Excessive_Thirst",
        "Excessive_Hunger",
        "Increased_Urination",
        "Heat_Intolerance",
        "Cold_Intolerance",
        "Hypoglycemic_Events",
        "Hyperglycemic_Events"
      ],
      "title": "Endocrine",
      "type": "object"
    },
    "Eyes": {
      "properties": {
        "Eyes_ROS__c": {
          "enum": [
            "Assessed",
            "Not Assessed"
          ],
          "title": "Eyes Ros  C",
          "type": "string"
        },
        "Not_Assessed_Reason": {
          "anyOf": [
            {
              "enum": [
                "Cognitive Impairment",
                "Patient/Caregiver Refused",
                "Poor Historian",
                "Unconscious",
                "Unresponsive",
                "Other"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Not Assessed Reason"
        },
        "Reviewed_and_Negative": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Reviewed And Negative"
        },
        "Blurred_Vision": {
          "anyOf": [
            {
              "enum": [
                "Left",
                "Right",
                "Bilateral",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Blurred Vision"
        },
        "Drainage": {
          "anyOf": [
            {
              "enum": [
                "Left",
                "Right",
                "Bilateral",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Drainage"
        },
        "Itching": {
          "anyOf": [
            {
              "enum": [
                "Left",
                "Right",
                "Bilateral",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Itching"
        },
        "Pain": {
          "anyOf": [
            {
              "enum": [
                "Left",
                "Right",
                "Bilateral",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Pain"
        },
        "Changes_in_Vision": {
          "anyOf": [
            {
              "enum": [
                "Left",
                "Right",
                "Bilateral",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Changes In Vision"
        },
        "Tearing": {
          "anyOf": [
            {
              "enum": [
                "Left",
                "Right",
                "Bilateral",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Tearing"
        },
        "Dryness": {
          "anyOf": [
            {
              "enum": [
                "Left",
                "Right",
                "Bilateral",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Dryness"
        },
        "Redness": {
          "anyOf": [
            {
              "enum": [
                "Left",
                "Right",
                "Bilateral",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Redness"
        },
        "Flashing_Lights": {
          "anyOf": [
            {
              "enum": [
                "Left",
                "Right",
                "Bilateral",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Flashing Lights"
        },
        "Double_Vision": {
          "anyOf": [
            {
              "enum": [
                "Left",
                "Right",
                "Bilateral",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Double Vision"
        },
        "Glasses_Contacts": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Glasses Contacts"
        }
      },
      "required": [
        "Eyes_ROS__c",
        "Not_Assessed_Reason",
        "Reviewed_and_Negative",
        "Blurred_Vision",
        "Drainage",
        "Itching",
        "Pain",
        "Changes_in_Vision",
        "Tearing",
        "Dryness",
        "Redness",
        "Flashing_Lights",
        "Double_Vision",
        "Glasses_Contacts"
      ],
      "title": "Eyes",
      "type": "object"
    },
    "Gastrointestinal": {
      "properties": {
        "Gastrointestinal_ROS__c": {
          "enum": [
            "Assessed",
            "Not Assessed"
          ],
          "title": "Gastrointestinal Ros  C",
          "type": "string"
        },
        "Not_Assessed_Reason": {
          "anyOf": [
            {
              "enum": [
                "Cognitive Impairment",
                "Patient/Caregiver Refused",
                "Poor Historian",
                "Unconscious",
                "Unresponsive",
                "Other"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Not Assessed Reason"
        },
        "Reviewed_and_Negative": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Reviewed And Negative"
        },
        "Heartburn": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Heartburn"
        },
        "Nausea": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Nausea"
        },
        "Abdominal_Pain": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Abdominal Pain"
        },
        "Vomiting": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Vomiting"
        },
        "Vomiting_Blood": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Vomiting Blood"
        },
        "Diarrhea": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Diarrhea"
        },
        "Constipation": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Constipation"
        },
        "Hemorrhoids": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Hemorrhoids"
        },
        "Fecal_Incontinence": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Fecal Incontinence"
        },
        "Black_Stools": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Black Stools"
        },
        "Bloody_Stools": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Bloody Stools"
        },
        "Change_in_Bowel_Habits": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Change In Bowel Habits"
        }
      },
      "required": [
        "Gastrointestinal_ROS__c",
        "Not_Assessed_Reason",
        "Reviewed_and_Negative",
        "Heartburn",
        "Nausea",
        "Abdominal_Pain",
        "Vomiting",
        "Vomiting_Blood",
        "Diarrhea",
        "Constipation",
        "Hemorrhoids",
        "Fecal_Incontinence",
        "Black_Stools",
        "Bloody_Stools",
        "Change_in_Bowel_Habits"
      ],
      "title": "Gastrointestinal",
      "type": "object"
    },
    "Genitourinary": {
      "properties": {
        "Genitourinary_ROS__c": {
          "enum": [
            "Assessed",
            "Not Assessed"
          ],
          "title": "Genitourinary Ros  C",
          "type": "string"
        },
        "Not_Assessed_Reason": {
          "anyOf": [
            {
              "enum": [
                "Cognitive Impairment",
                "Patient/Caregiver Refused",
                "Poor Historian",
                "Unconscious",
                "Unresponsive",
                "Other"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Not Assessed Reason"
        },
        "Reviewed_and_Negative": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Reviewed And Negative"
        },
        "Urgency": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Urgency"
        },
        "Frequency": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Frequency"
        },
        "Difficulty_Urinating": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Difficulty Urinating"
        },
        "Burning_with_Urination": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Burning With Urination"
        },
        "Blood_in_Urine": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Blood In Urine"
        },
        "Stress_Incontinence": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Stress Incontinence"
        },
        "Frequent_Infections": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Frequent Infections"
        },
        "Urge_Incontinence": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Urge Incontinence"
        },
        "Nocturia": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Nocturia"
        },
        "Testicular_Pain": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Testicular Pain"
        },
        "Vaginal_Bleeding": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Vaginal Bleeding"
        },
        "Scrotal_Swelling": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Scrotal Swelling"
        }
      },
      "required": [
        "Genitourinary_ROS__c",
        "Not_Assessed_Reason",
        "Reviewed_and_Negative",
        "Urgency",
        "Frequency",
        "Difficulty_Urinating",
        "Burning_with_Urination",
        "Blood_in_Urine",
        "Stress_Incontinence",
        "Frequent_Infections",
        "Urge_Incontinence",
        "Nocturia",
        "Testicular_Pain",
        "Vaginal_Bleeding",
        "Scrotal_Swelling"
      ],
      "title": "Genitourinary",
      "type": "object"
    },
    "GeriatricSyndrome": {
      "properties": {
        "Compared_to_others_your_age": {
          "anyOf": [
            {
              "enum": [
                "Excellent",
                "Very Good",
                "Good",
                "Fair",
                "Poor",
                "Doesn't know/Unable to answer"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Compared To Others Your Age"
        },
        "Self_Assessed_Mental": {
          "anyOf": [
            {
              "enum": [
                "Better",
                "Same",
                "Worse",
                "Don't Know",
                "Consumer Unable to Answer"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Self Assessed Mental"
        }
      },
      "required": [
        "Compared_to_others_your_age",
        "Self_Assessed_Mental"
      ],
      "title": "GeriatricSyndrome",
      "type": "object"
    },
    "HeadAndNeck": {
      "properties": {
        "Head_ROS__c": {
          "enum": [
            "Assessed",
            "Not Assessed"
          ],
          "title": "Head Ros  C",
          "type": "string"
        },
        "Not_Assessed_Reason": {
          "anyOf": [
            {
              "enum": [
                "Cognitive Impairment",
                "Patient/Caregiver Refused",
                "Poor Historian",
                "Unconscious",
                "Unresponsive",
                "Other"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Not Assessed Reason"
        },
        "Reviewed_and_Negative": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Reviewed And Negative"
        },
        "Headaches": {
          "anyOf": [
            {
              "enum": [
                "Recurrent/Severe",
                "New Onset",
                "Migraines",
                "Sinus",
                "Tension",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Headaches"
        },
        "Dizziness": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Dizziness"
        },
        "Hair_Loss": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Hair Loss"
        },
        "Swollen_Glands": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Swollen Glands"
        },
        "Neck_Stiffness": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Neck Stiffness"
        },
        "Previous_Head_Injury": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Previous Head Injury"
        },
        "Previous_Head_Injury_Describe": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Previous Head Injury Describe"
        }
      },
      "required": [
        "Head_ROS__c",
        "Not_Assessed_Reason",
        "Reviewed_and_Negative",
        "Headaches",
        "Dizziness",
        "Hair_Loss",
        "Swollen_Glands",
        "Neck_Stiffness",
        "Previous_Head_Injury",
        "Previous_Head_Injury_Describe"
      ],
      "title": "HeadAndNeck",
      "type": "object"
    },
    "Integumentary": {
      "properties": {
        "Integumentary_ROS__c": {
          "enum": [
            "Assessed",
            "Not Assessed"
          ],
          "title": "Integumentary Ros  C",
          "type": "string"
        },
        "Not_Assessed_Reason": {
          "anyOf": [
            {
              "enum": [
                "Cognitive Impairment",
                "Patient/Caregiver Refused",
                "Poor Historian",
                "Unconscious",
                "Unresponsive",
                "Other"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Not Assessed Reason"
        },
        "Reviewed_and_Negative": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Reviewed And Negative"
        },
        "Rash": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Rash"
        },
        "Bruising": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Bruising"
        },
        "Abrasions": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Abrasions"
        },
        "Skin_Tears": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Skin Tears"
        },
        "Lacerations": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Lacerations"
        },
        "Surgical_Wounds": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Surgical Wounds"
        },
        "Diabetic_Ulcers": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Diabetic Ulcers"
        },
        "Pressure_Ulcers": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Pressure Ulcers"
        },
        "Foot_Ulcers": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Foot Ulcers"
        },
        "Stasis_Ulcers": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Stasis Ulcers"
        },
        "Poor_Healing_of_Wounds": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Poor Healing Of Wounds"
        },
        "Atypical_Skin_Lesion": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Atypical Skin Lesion"
        },
        "Hair_Loss": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Hair Loss"
        }
      },
      "required": [
        "Integumentary_ROS__c",
        "Not_Assessed_Reason",
        "Reviewed_and_Negative",
        "Rash",
        "Bruising",
        "Abrasions",
        "Skin_Tears",
        "Lacerations",
        "Surgical_Wounds",
        "Diabetic_Ulcers",
        "Pressure_Ulcers",
        "Foot_Ulcers",
        "Stasis_Ulcers",
        "Poor_Healing_of_Wounds",
        "Atypical_Skin_Lesion",
        "Hair_Loss"
      ],
      "title": "Integumentary",
      "type": "object"
    },
    "Musculoskeletal": {
      "properties": {
        "Muscoloskeletal_ROS__c": {
          "enum": [
            "Assessed",
            "Not Assessed"
          ],
          "title": "Muscoloskeletal Ros  C",
          "type": "string"
        },
        "Not_Assessed_Reason": {
          "anyOf": [
            {
              "enum": [
                "Cognitive Impairment",
                "Patient/Caregiver Refused",
                "Poor Historian",
                "Unconscious",
                "Unresponsive",
                "Other"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Not Assessed Reason"
        },
        "Reviewed_and_Negative": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Reviewed And Negative"
        },
        "Gait_Disturbances": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Gait Disturbances"
        },
        "Muscle_Cramping": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Muscle Cramping"
        },
        "Muscle_Pain": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Muscle Pain"
        },
        "Joint_Pain": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Joint Pain"
        },
        "Joint_Pain_Location": {
          "anyOf": [
            {
              "enum": [
                "(L) Shoulder",
                "(R) Shoulder",
                "(L) Elbow",
                "(R) Elbow",
                "(L) Wrist",
                "(R) Wrist",
                "(L) Finger(s)",
                "(R) Finger(s)",
                "(L) Hip",
                "(R) Hip",
                "(L) Knee",
                "(R) Knee",
                "(L) Ankle",
                "(R) Ankle",
                "(L) Toe(s)",
                "(R) Toe(s)"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Joint Pain Location"
        },
        "Joint_Stiffness": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Joint Stiffness"
        },
        "Joint_Stiffness_Location": {
          "anyOf": [
            {
              "enum": [
                "(L) Shoulder",
                "(R) Shoulder",
                "(L) Elbow",
                "(R) Elbow",
                "(L) Wrist",
                "(R) Wrist",
                "(L) Finger(s)",
                "(R) Finger(s)",
                "(L) Hip",
                "(R) Hip",
                "(L) Knee",
                "(R) Knee",
                "(L) Ankle",
                "(R) Ankle",
                "(L) Toe(s)",
                "(R) Toe(s)"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Joint Stiffness Location"
        },
        "Fractures": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Fractures"
        },
        "Fractures_Locations": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Fractures Locations"
        },
        "Date_of_Last_Fracture": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Date Of Last Fracture"
        }
      },
      "required": [
        "Muscoloskeletal_ROS__c",
        "Not_Assessed_Reason",
        "Reviewed_and_Negative",
        "Gait_Disturbances",
        "Muscle_Cramping",
        "Muscle_Pain",
        "Joint_Pain",
        "Joint_Pain_Location",
        "Joint_Stiffness",
        "Joint_Stiffness_Location",
        "Fractures",
        "Fractures_Locations",
        "Date_of_Last_Fracture"
      ],
      "title": "Musculoskeletal",
      "type": "object"
    },
    "Neurological": {
      "properties": {
        "Neurological_ROS__c": {
          "enum": [
            "Assessed",
            "Not Assessed"
          ],
          "title": "Neurological Ros  C",
          "type": "string"
        },
        "Not_Assessed_Reason": {
          "anyOf": [
            {
              "enum": [
                "Cognitive Impairment",
                "Patient/Caregiver Refused",
                "Poor Historian",
                "Unconscious",
                "Unresponsive",
                "Other"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Not Assessed Reason"
        },
        "Reviewed_and_Negative": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Reviewed And Negative"
        },
        "Cognitive_Impairment": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Cognitive Impairment"
        },
        "Numbness": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Numbness"
        },
        "Tingling": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Tingling"
        },
        "Prickling_Sensation": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Prickling Sensation"
        },
        "Burning_Sensation": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Burning Sensation"
        },
        "Itching_Sensation": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Itching Sensation"
        },
        "Pins_and_Needles": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Pins And Needles"
        },
        "Pain_d_t_Innocuous_Stimuli": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Pain D T Innocuous Stimuli"
        },
        "Increased_Sensitivity_to_Pain": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Increased Sensitivity To Pain"
        },
        "Dizziness": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Dizziness"
        },
        "Lightheadedness": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Lightheadedness"
        },
        "Vertigo": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Vertigo"
        },
        "Fainting": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Fainting"
        },
        "Loss_of_Balance": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Loss Of Balance"
        },
        "Memory_Problems": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Memory Problems"
        },
        "Difficulty_Speaking": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Difficulty Speaking"
        },
        "Motor_Weakness": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Motor Weakness"
        },
        "Seizures": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Seizures"
        }
      },
      "required": [
        "Neurological_ROS__c",
        "Not_Assessed_Reason",
        "Reviewed_and_Negative",
        "Cognitive_Impairment",
        "Numbness",
        "Tingling",
        "Prickling_Sensation",
        "Burning_Sensation",
        "Itching_Sensation",
        "Pins_and_Needles",
        "Pain_d_t_Innocuous_Stimuli",
        "Increased_Sensitivity_to_Pain",
        "Dizziness",
        "Lightheadedness",
        "Vertigo",
        "Fainting",
        "Loss_of_Balance",
        "Memory_Problems",
        "Difficulty_Speaking",
        "Motor_Weakness",
        "Seizures"
      ],
      "title": "Neurological",
      "type": "object"
    },
    "NoseThroat": {
      "properties": {
        "Nose_Throat_ROS__c": {
          "enum": [
            "Assessed",
            "Not Assessed"
          ],
          "title": "Nose Throat Ros  C",
          "type": "string"
        },
        "Not_Assessed_Reason": {
          "anyOf": [
            {
              "enum": [
                "Cognitive Impairment",
                "Patient/Caregiver Refused",
                "Poor Historian",
                "Unconscious",
                "Unresponsive",
                "Other"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Not Assessed Reason"
        },
        "Reviewed_and_Negative": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Reviewed And Negative"
        },
        "Nasal_Congestion": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Nasal Congestion"
        },
        "Sinus_Pressure": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Sinus Pressure"
        },
        "Nosebleeds": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Nosebleeds"
        },
        "Hoarseness": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Hoarseness"
        },
        "Sore_Throat": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Sore Throat"
        },
        "Difficulty_Swallowing": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Difficulty Swallowing"
        },
        "Difficulty_Chewing": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Difficulty Chewing"
        },
        "Poor_Dentition": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Poor Dentition"
        },
        "Sore_Tongue": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Sore Tongue"
        },
        "Bleeding_Gums": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Bleeding Gums"
        },
        "Tooth_Pain": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Tooth Pain"
        }
      },
      "required": [
        "Nose_Throat_ROS__c",
        "Not_Assessed_Reason",
        "Reviewed_and_Negative",
        "Nasal_Congestion",
        "Sinus_Pressure",
        "Nosebleeds",
        "Hoarseness",
        "Sore_Throat",
        "Difficulty_Swallowing",
        "Difficulty_Chewing",
        "Poor_Dentition",
        "Sore_Tongue",
        "Bleeding_Gums",
        "Tooth_Pain"
      ],
      "title": "NoseThroat",
      "type": "object"
    },
    "PainAssessment": {
      "properties": {
        "Cognitive_Impairment": {
          "title": "Cognitive Impairment",
          "type": "boolean"
        },
        "Cognitive_Impairment_Type": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Cognitive Impairment Type"
        },
        "Pain_Assessment_Completed": {
          "enum": [
            "Verbal",
            "Non-Verbal"
          ],
          "title": "Pain Assessment Completed",
          "type": "string"
        },
        "Verbal_Pain_Scale": {
          "enum": [
            0,
            1,
            2,
            3,
            4,
            5,
            6,
            7,
            8,
            9,
            10
          ],
          "title": "Verbal Pain Scale",
          "type": "integer"
        },
        "Description_of_Pain": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Description Of Pain"
        },
        "Does_not_appear_to_be_in_pain": {
          "title": "Does Not Appear To Be In Pain",
          "type": "boolean"
        },
        "Non_Verbal_Pain_Indicators": {
          "anyOf": [
            {
              "enum": [
                "Changes in activity/pattern",
                "Crying Out or Moaning",
                "Facial Expressions",
                "Mental Status Changes",
                "Grimacing",
                "Restlessness",
                "Rigid Posture",
                "Tears"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Non Verbal Pain Indicators"
        },
        "What_Eases_the_Pain": {
          "anyOf": [
            {
              "enum": [
                "Unable to Answer",
                "Position Change",
                "Medication",
                "Heat",
                "Cold",
                "Rest",
                "Activity",
                "Other"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "What Eases The Pain"
        },
        "Pain_Notes": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Pain Notes"
        }
      },
      "required": [
        "Cognitive_Impairment",
        "Cognitive_Impairment_Type",
        "Pain_Assessment_Completed",
        "Verbal_Pain_Scale",
        "Description_of_Pain",
        "Does_not_appear_to_be_in_pain",
        "Non_Verbal_Pain_Indicators",
        "What_Eases_the_Pain",
        "Pain_Notes"
      ],
      "title": "PainAssessment",
      "type": "object"
    },
    "Psychological": {
      "properties": {
        "Psychological_ROS__c": {
          "enum": [
            "Assessed",
            "Not Assessed"
          ],
          "title": "Psychological Ros  C",
          "type": "string"
        },
        "Not_Assessed_Reason": {
          "anyOf": [
            {
              "enum": [
                "Cognitive Impairment",
                "Patient/Caregiver Refused",
                "Poor Historian",
                "Unconscious",
                "Unresponsive",
                "Other"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Not Assessed Reason"
        },
        "Reviewed_and_Negative": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Reviewed And Negative"
        },
        "Depression": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Depression"
        },
        "Withdrawn": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Withdrawn"
        },
        "Anxiety": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Anxiety"
        },
        "Hallucinations": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Hallucinations"
        },
        "Sadness": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Sadness"
        },
        "Insomnia": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Insomnia"
        },
        "Periods_of_High_Energy": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Periods Of High Energy"
        },
        "Racing_Thoughts": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Racing Thoughts"
        },
        "Suicidal_Ideations": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Suicidal Ideations"
        },
        "Homicidal_Ideations": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Homicidal Ideations"
        },
        "Angry": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Angry"
        },
        "Upset": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Upset"
        },
        "Euthymic_Mood": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Euthymic Mood"
        }
      },
      "required": [
        "Psychological_ROS__c",
        "Not_Assessed_Reason",
        "Reviewed_and_Negative",
        "Depression",
        "Withdrawn",
        "Anxiety",
        "Hallucinations",
        "Sadness",
        "Insomnia",
        "Periods_of_High_Energy",
        "Racing_Thoughts",
        "Suicidal_Ideations",
        "Homicidal_Ideations",
        "Angry",
        "Upset",
        "Euthymic_Mood"
      ],
      "title": "Psychological",
      "type": "object"
    },
    "Respiratory": {
      "properties": {
        "Respiratory_ROS__c": {
          "enum": [
            "Assessed",
            "Not Assessed"
          ],
          "title": "Respiratory Ros  C",
          "type": "string"
        },
        "Not_Assessed_Reason": {
          "anyOf": [
            {
              "enum": [
                "Cognitive Impairment",
                "Patient/Caregiver Refused",
                "Poor Historian",
                "Unconscious",
                "Unresponsive",
                "Other"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Not Assessed Reason"
        },
        "Reviewed_and_Negative": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Reviewed And Negative"
        },
        "Chronic_Cough": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Chronic Cough"
        },
        "Acute_Cough": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Acute Cough"
        },
        "Sputum": {
          "anyOf": [
            {
              "enum": [
                "Clear",
                "Colored",
                "Bloody",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Sputum"
        },
        "Shortness_of_Breath": {
          "anyOf": [
            {
              "enum": [
                "At Rest",
                "Orthopnea",
                "PND",
                "With Normal Daily Activity",
                "With Moderate Exertion",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Shortness Of Breath"
        },
        "Wheezing": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Wheezing"
        },
        "Snoring": {
          "anyOf": [
            {
              "enum": [
                "true",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Snoring"
        },
        "CPAP_BiPAP": {
          "anyOf": [
            {
              "enum": [
                "Compliant",
                "Non-Compliant",
                "false",
                "NA"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Cpap Bipap"
        }
      },
      "required": [
        "Respiratory_ROS__c",
        "Not_Assessed_Reason",
        "Reviewed_and_Negative",
        "Chronic_Cough",
        "Acute_Cough",
        "Sputum",
        "Shortness_of_Breath",
        "Wheezing",
        "Snoring",
        "CPAP_BiPAP"
      ],
      "title": "Respiratory",
      "type": "object"
    }
  },
  "properties": {
    "Reviewed_with": {
      "anyOf": [
        {
          "enum": [
            "Member",
            "Facility Staff",
            "Facility Chart",
            "Family"
          ],
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "title": "Reviewed With"
    },
    "CONSTITUTIONAL": {
      "$ref": "#/$defs/Constitutional"
    },
    "EENT_EYES": {
      "$ref": "#/$defs/Eyes"
    },
    "EENT_NOSE_AND_THROAT": {
      "$ref": "#/$defs/NoseThroat"
    },
    "EENT_EARS": {
      "$ref": "#/$defs/Ears"
    },
    "CARDIOVASCULAR": {
      "$ref": "#/$defs/Cardiovascular"
    },
    "GERIATRIC_SYNDROME": {
      "$ref": "#/$defs/GeriatricSyndrome"
    },
    "GENITOURINARY": {
      "$ref": "#/$defs/Genitourinary"
    },
    "NEUROLOGICAL": {
      "$ref": "#/$defs/Neurological"
    },
    "ENDOCRINE": {
      "$ref": "#/$defs/Endocrine"
    },
    "PSYCHOLOGICAL": {
      "$ref": "#/$defs/Psychological"
    },
    "PAIN_ASSESSMENT": {
      "$ref": "#/$defs/PainAssessment"
    },
    "HEAD_AND_NECK": {
      "$ref": "#/$defs/HeadAndNeck"
    },
    "RESPIRATORY": {
      "$ref": "#/$defs/Respiratory"
    },
    "GASTROINTESTINAL": {
      "$ref": "#/$defs/Gastrointestinal"
    },
    "INTEGUMENTARY": {
      "$ref": "#/$defs/Integumentary"
    },
    "MUSCULOSKELETAL": {
      "$ref": "#/$defs/Musculoskeletal"
    },
    "DIABETIC_TESTING": {
      "$ref": "#/$defs/DiabeticTesting"
    },
    "additional_notes": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "title": "Additional_notes"
    }
  },
  "required": [
    "Reviewed_with",
    "CONSTITUTIONAL",
    "EENT_EYES",
    "EENT_NOSE_AND_THROAT",
    "EENT_EARS",
    "CARDIOVASCULAR",
    "GERIATRIC_SYNDROME",
    "GENITOURINARY",
    "NEUROLOGICAL",
    "ENDOCRINE",
    "PSYCHOLOGICAL",
    "PAIN_ASSESSMENT",
    "HEAD_AND_NECK",
    "RESPIRATORY",
    "GASTROINTESTINAL",
    "INTEGUMENTARY",
    "MUSCULOSKELETAL",
    "DIABETIC_TESTING",
    "additional_notes"
  ],
  "title": "ros",
  "type": "object"
}" """
cls = globals()['ros']
response_schema_dict = cls.model_json_schema()
response_schema_json = json.dumps(response_schema_dict, indent=2)   
thePrompt = thePrompt.format(constraints=response_schema_json)
print(thePrompt)

#client = anthropic.Anthropic()

message = client.messages.create(
    model="claude-3-5-sonnet-20240620",
    max_tokens=1000,
    temperature=0,    
    system=theSystemPrompt,
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": thePrompt
                }
            ]
        }
    ]
)
print(message.content)
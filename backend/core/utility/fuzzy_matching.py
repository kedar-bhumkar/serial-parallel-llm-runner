import re
from fuzzywuzzy import fuzz
# List of words to check in the transcript
words_to_check = [
    "Reviewed", "Constitutional", "Eyes", "Nose", "Throat", "Ears", "NoseThroat", "Nose and Throat","HeadAndNeck", "Head and Neck","HeadandNeck",
    "Cardiovascular", "GeriatricSyndrome", "Genitourinary", "Neurological", 
    "Endocrine", "Psychological", "PainAssessment", "Head", "Neck", 
    "Respiratory", "Gastrointestinal", "Integumentary", "Musculoskeletal", 
    "Diabetic", "notes"
]

# Transcript
transcript = """
Patient reports overall health to be Very good
No change in Self-assessed mental health
Pain assessment completed verbally.
Verbal pain scale reported as 0 
Constitutional Reviewed and negative.
Eyes Assessed. Patients Uses glasses
Nose and throat Assessed. Patient reports difficulty swallowing.
Respiratory was reviewed and negative.
Cardio vascular was Reviewed and negative.
Gastro intestinal was reviewed and negative.
Genito urinary was Assessed. The patient reports difficulty urinating.
Cognative impairment was not seen
The patient said she has Numbness and tingling with a Prickling sensation
It feels like Pins and needles
Musculoskeletal was assessed and gait disturbances were seen.
Reports history of fractures on Left femur. The last fracture was in 1996.
The patient informed me that he is Non-diabetic.
A sychological assessment was done. She Reports depression. Manages it with activities.
Some additional notes about the patient - He was once incarcerated in jail for 2 weeks

"""

# Function to check for presence of words with fuzzy matching
def check_words_in_transcript(words, transcript, threshold=0.75):
    found_words = {}
    transcript_words = transcript.split()
    
    for word in words:
        found = False
        for t_word in transcript_words:
            ratio = fuzz.ratio(word.lower(), t_word.lower())
            #print(f"word - {word}, t_word - {t_word}, ratio - {ratio}")
            if  ratio >= threshold:
                found = True
                break
        found_words[word] = found
    return found_words


# Function to check for presence of words with fuzzy matching
def check_word_in_transcript(word, transcript, threshold=0.75):
    words = None
    if(word == 'NoseThroat'):
        words = ['Nose', 'Throat']
    else:
        words = [word]

    found = False
    transcript_words = transcript.split()
    for word in words:
        for t_word in transcript_words:
            ratio = fuzz.ratio(word.lower(), t_word.lower())
            #print(f"word - {word}, t_word - {t_word}, ratio - {ratio}")
            if  ratio >= threshold:
                found = True
                break
    return found

def fuzzyMatch(transcript=transcript):
    # Check words in the transcript
    found_words = check_words_in_transcript(words_to_check, transcript)

    # Separate matched and unmatched words
    matched_words = [word for word, found in found_words.items() if found]
    unmatched_words = [word for word, found in found_words.items() if not found]

    #print(f"Transcript - {transcript}")

    # Display the results
    #print("Matched words:")
    #for word in matched_words:
       # print(word)

    message = ''        
    if(len(unmatched_words) > 0):
        # Message to append unmatched words
        message = "The below sections were not assessed: "
        message += ", ".join(unmatched_words)
    #print(f"message-{message}")
    return message


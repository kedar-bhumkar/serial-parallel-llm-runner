from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig

# Initialize Presidio Analyzer and Anonymizer
analyzer = AnalyzerEngine()
anonymizer = AnonymizerEngine()

def remove_phi_pii_presidio(text: str) -> str:
    
    # Specify the entities you want to detect, excluding 'DATE' and 'US_SOCIAL_SECURITY_NUMBER'
    entities_to_detect = ["PERSON", "PHONE_NUMBER", "EMAIL_ADDRESS","LOCATION","US_SSN","CREDIT_CARD","ADDRESS"]  # Add other entities as needed
    
    # Analyze the text to find PII entities
    results = analyzer.analyze(text=text, language="en", entities=entities_to_detect)
    print(results)
    
    if not results:
        return text
        
    # Create operator config for each entity type
    operators = {
        "PERSON": OperatorConfig("replace", {"new_value":"PERSON"}),
        "PHONE_NUMBER": OperatorConfig("replace", {"new_value":"PHONE"}),
        "EMAIL_ADDRESS": OperatorConfig("replace", {"new_value":"EMAIL"}),       
        "LOCATION": OperatorConfig("replace", {"new_value":"LOCATION"}),
        "US_SSN": OperatorConfig("replace", {"new_value":"SSN"}),
        "CREDIT_CARD": OperatorConfig("replace", {"new_value":"CREDIT_CARD"}),
        "ADDRESS": OperatorConfig("replace", {"new_value":"ADDRESS"})
    }

    # Anonymize the text
    try:
        result = anonymizer.anonymize(
            text=text,
            analyzer_results=results,
            operators=operators
        )
        return result.text
    except Exception as e:
        print(f"Anonymization error: {e}")
        return text

# Example usage
if __name__ == "__main__":
    text = """ Visit Type is Comprehensive Member New or Established is New Date of Visit is 05/18/2023 Place of Service is Assisted Living Facility How was visit Completed is Face to Face CC/Reason for Program Admission is Follow up on chronic conditions and management HPI is Member seen today for an initial comprehensive visit. He lives alone in an independent senior apartment. He has two cats for company. His son lives near by but he doesn't see him or talk often but does talk more often to his daughter in law. Denies falls in over 2 years. 1. HTN, CKD3A, afib, secondary hypercoagulability, anemia in CKD- continues on iron and vitamin C daily, coumadin managed by Holy Family coumadin clinic 2. Moderate protein calorie malnutrition, esophageal obstruction, hiatal hernia, vitamin D deficiency- swallowing ok now, has had dilation procedures in the past, continues on famotidine and vitamin d supplements. 3. BPH, obstructive uropathy- continues to self cath several times daily. 4. MDD, insomnia, RLS- manages depressive symptoms by planning daily outing on the bus. RLS managed with gabapentin, insomnia with melatonin with good effect. 5. OA- infrequent pain, but acetaminophen is effective when needed. Uses cane in the apartment and walker when out of apartment. No falls in more than 2 years.
      """
    
    cleaned_text = remove_phi_pii_presidio(text)
    print(cleaned_text)
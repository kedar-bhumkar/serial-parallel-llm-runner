**Brief**
Generic LLM client to run user defined prompts on any open AI format compatible model/probviders.
Currently supports below model factories
- OpenAi
- OpenRouter
- LMStudio local
- etc.


**Usage**
- install all dependencies
- python main.py

**Parameters**
- All parameters are optional
- If left blank, demo usecase will be used
  "--usecase" - the usecase"
    ("--page", type=str, required=False, help="the page name")
    ("--mode", type=str, required=False, help="mode serial or parallel")
    ("--model", type=str, required=False, help="A valid LLM model name. Check supported providers as well if model is present")
    ("--model_family", type=str, required=False, help="openai openrouter lmstudio groq")
    ("--formatter", type=str, required=False, help="response formatting function")
    ("--run_mode", type=str, required=False, help="same-llm, multiple-llm")
    ("--run_count", type=int, required=False, help="How many times to run")
    ("--sleep", type=int, required=False, help="Pause between invocations")
    ("--accuracy_check", type=str, required=False, help="Compare against supplied ideal response. Values - ON, OFF")
    ("--negative_prompt", type=str, required=False, help="Compute unspoken sections as NOT ASSESSED using fuzzy matching Values - ON, OFF")
    ("--use_for_training", type=str, required=False, help="Count this row for training / finetuning - true, false")

  **Config files**
  prompts.yaml - define the prompts in this as given in the demo usecase (for command line only)
  config.yaml - define the models here
  dbconfig.yaml - postgres connection details
  
**Features**
- Support command line and web interafce (FAST API)
- Web client supports - Whisper , transcription (auto /typed) submission, response viewer 
- Supports multiple model factories and preferred models within it
- Config driven prompts
- Supports prompt cleansing, value interpolation, negative prompt, pydantic model constrainer
- Supports batch mode of calling the llm multiple times for the same prompt
- Supports serial and parallel execution
- Supports response  parsing, validation, transformation, error detection/correction, confidence map computation using fuzzy logic (and custom rules)
- prompt, response and other parameters logged in a local postgres DB for analysis
- Supports accuracy calculation
- Supports result reproducibility calculation
- Supports token counting
- Supports computing the similarity scores using difflib and Levenstein algorithm



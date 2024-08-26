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
  - usecase - the usecase
  - page - the page name
  - mode - mode serial or parallel
  - model - A valid LLM model name. Check supported providers as well if model is present
  - model_family - openai openrouter lmstudio groq
  - formatter - response formatting function
  - run_mode - same-llm, multiple-llm
  - run_count - How many times to run
  - sleep- Pause between invocations
  - accuracy_check- Compare against supplied ideal response. Values - ON, OFF
  - negative_prompt - Compute unspoken sections as NOT ASSESSED using fuzzy matching Values - ON, OFF
  - use_for_training - Count this row for training / finetuning - true, false
  - error_detection - Perform error detection/confidence map computation  - true, false

  **Config files**
  - prompts.yaml - define the prompts in this as given in the demo usecase (for command line only)
  - config.yaml - define the models here
  - dbconfig.yaml - postgres connection details
  
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



**Brief**
Generic LLM client to run user defined prompts on any open AI format compatible model/probviders.
Currently supports below model factories
- OpenAi
- OpenRouter
- LMStudio local


**Usage**
- install all dependencies
- python serial-parallel-runner.py

**Parameters**
- All parameters are optional
- If left blank, demo usecase will be used
    --usecase - the usecase
    --page    -  the page name
    --mode    - mode serial or parallel execution (parallel execution only possible if prompt is broken into multiple segments
    --model_family - openai openrouter lmstudio
    --formatter - response formatting function

  **Main files**
  prompts.yaml - define the prompts in this as given in the demo usecase
  config.yaml - define the models here
  
**Features**
- Supports multiple model factories and models within it
- Config driven prompts
- Supports any prompt
- Supports batch mode of calling the llm multiple times for the same prompt
- Supports serial and parallel execution
- Supports response formatting via a 'formatter' function to change the output as desired
- prompt, response and other parameters logged in a local postgres DB for analysis
- Supports accuracy calculation
- Supports result reproducibility calculation
- Supports token counting
- Supports computing the similarity scores using difflib and Levenstein algorithm

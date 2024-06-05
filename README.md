**Brief**
Generic LLM client to run user defined prompts on any open AI format compatible model/probviders.
Currently supports
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
  

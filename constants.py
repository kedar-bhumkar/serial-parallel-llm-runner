#model = "gpt-3.5-turbo-0125"
#model="gpt-4o"
#model="meta-llama/llama-3-8b",
#model="lmstudio-community/Meta-Llama-3-8B-Instruct-GGUF"
standard_model = "gpt-3.5-turbo-0125"

config_file ="config.yaml"
prompts_file="prompts.yaml"
db_conn_file='db_config.yaml'

default_mode = "serial"
default_page = "demo"
default_model_family = "openai"
default_usecase = "demo"
default_temperature=0.1
default_run_mode = "same-llm"
default_run_count = 1
default_sleep = 0.75
default_accuracy_check = "ON"
default_encoding = "cl100k_base"
default_fuzzy_matching_threshold = 80
default_negative_prompt="ON"
default_formatter = "ros_pe_formatter"
default_use_for_training = False
default_error_detection = True


INSERT_QUERY = """
        INSERT INTO Run_stats (
            usecase,
            functionality,
            llm,
            llm_parameters,
            isBaseline,
            run_no,
            system_prompt,
            user_prompt,
            response,
            ideal_response,
            execution_time,
            matches_baseline,
            matches_ideal,
            difference,
            ideal_response_difference,
            mode,
            similarity_metric,
            run_date,
            use_for_training

        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """
READ_QUERY = """
        SELECT 
            run_no,
            execution_time,
            usecase,
            functionality,
            isbaseline,
            matches_baseline,
            matches_ideal,
            difference,
            ideal_response_difference,
            response 
        FROM Run_stats
        """

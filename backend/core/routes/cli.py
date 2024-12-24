import argparse
import time
from backend.core.service.main import process_request

def main():
    """Handle CLI requests"""
    parser = argparse.ArgumentParser(description="Run any prompt on any model.")
    
    # Add arguments
    parser.add_argument("--usecase", type=str, help="the usecase")
    parser.add_argument("--page", type=str, help="the page name")
    parser.add_argument("--mode", type=str, help="mode serial or parallel")
    parser.add_argument("--model", type=str, help="A valid LLM model name")
    parser.add_argument("--model_family", type=str, help="openai openrouter lmstudio groq")
    parser.add_argument("--formatter", type=str, help="response formatting function")
    parser.add_argument("--run_mode", type=str, help="same-llm, multiple-llm, test-llm")
    parser.add_argument("--run_count", type=int, help="How many times to run")
    parser.add_argument("--sleep", type=int, help="Pause between invocations")
    parser.add_argument("--accuracy_check", type=str, help="Compare against supplied ideal response")
    parser.add_argument("--negative_prompt", type=str, help="Compute unspoken sections")
    parser.add_argument("--use_for_training", type=str, help="Count this row for training")
    parser.add_argument("--error_detection", type=str, help="Perform error detection")
    parser.add_argument("--test_size_limit", type=int, help="How many test samples to run")
    parser.add_argument("--phi_detection", type=str, help="Perform PHI detection")
    parser.add_argument("--file_name", type=str, help="File name to use")
    parser.add_argument("--ideal_response", type=str, help="Ideal response to use")

    args = parser.parse_args()
    
    start_time = time.time()
    process_request( 
        usecase=args.usecase,
        page=args.page,
        mode=args.mode,
        model_family=args.model_family,
        formatter=args.formatter,
        run_mode=args.run_mode,
        sleep=args.sleep,
        model=args.model,
        prompt=None,  # Will be loaded from config
        run_count=args.run_count,
        accuracy_check=args.accuracy_check,
        negative_prompt=args.negative_prompt,
        use_for_training=args.use_for_training,
        error_detection=args.error_detection,
        phi_detection=args.phi_detection,
        test_size_limit=args.test_size_limit,
        file_name=args.file_name,
        ideal_response=args.ideal_response
    )
    
    process_time = time.time() - start_time
    print(f"Request took {process_time} secs to complete")

if __name__ == "__main__":
    main()


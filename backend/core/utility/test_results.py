from backend.core.db.db_layer import get_test_results, get_test_results_detail


def getTestResults(testId):
    
    df_detail = get_test_results_detail(testId)
    # Get the first record as a dictionary
    summary = df_detail.to_dict('records')[0]
    print(f"summary-{summary}")

    # Get results as a DataFrame
    df = get_test_results(testId)
    
    # Transform DataFrame into required format
    transformed_results = {
        f"test{idx}": {
            "ideal_response": row["original_response"] if summary.get("test_type") == "consistency" else row["ideal_response"],
            "actual_response": row["actual_response"],
            "original_prompt": row["original_prompt"],
            "test_results_detail_no": row["test_results_detail_no"],
            "trd_fingerprint": row["trd_fingerprint"],
            "rs_fingerprint": row["rs_fingerprint"]
        }
        for idx, row in df.iterrows()
    }
    
    results = {
        "transformed_results": transformed_results,
        "summary": summary
    }
    print(f"results-{results}")
    return results



#if __name__ == "__main__":
#    print(getTestResults(17))

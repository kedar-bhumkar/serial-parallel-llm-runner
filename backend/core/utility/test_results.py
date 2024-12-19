from backend.core.db.db_layer import get_test_results


def getTestResults(testId):
    # Get results as a DataFrame
    df = get_test_results(testId)
    
    # Transform DataFrame into required format
    transformed_results = {
        f"test{idx}": {
            "ideal_response": row["original_response"],
            "actual_response": row["actual_response"],
            "original_prompt": row["original_prompt"],
            "test_results_detail_no": row["test_results_detail_no"]
        }
        for idx, row in df.iterrows()
    }
    
    return transformed_results


if __name__ == "__main__":
    print(getTestResults(11))

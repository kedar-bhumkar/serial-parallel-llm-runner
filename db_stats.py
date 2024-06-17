from  db_layer import *

def print_reproducibility_stats(df):
    # Convert matches_baseline to boolean
    df['matches_baseline'] = df['matches_baseline'].astype(bool)
    # Group by run_no and matches_baseline and count the occurrences
    grouped = df.groupby(['run_no', 'matches_baseline']).size().unstack(fill_value=0)

    if True not in grouped.columns:
        grouped[True] = 0

    if False not in grouped.columns:
        grouped[False] = 0

    # Calculate the percentage columns
    grouped['% false'] = ((grouped[False] / (grouped[False] + grouped[True])) * 100).round(2)
    grouped['% true'] = ((grouped[True] / (grouped[False] + grouped[True])) * 100).round(2)

    # Display the grouped DataFrame
    #print(grouped)

    # Compute the true reproducibility
    numerator = grouped[True].sum()
    denominator = grouped[False].sum() + grouped[True].sum()
    #print(f'numerator={numerator} - denominator-{denominator}')

    true_value = ((numerator / denominator) * 100).round(2)

    true_value
    print(f'Reproducibility-{true_value}')


def print_accuracy_stats(df):
    # Convert matches_baseline to boolean
    df['matches_ideal'] = df['matches_ideal'].apply(lambda x: False if not x or x.lower() == 'false' else True)
    #print(f"df-matches_ideal->{df['matches_ideal']}")
    # Group by run_no and matches_baseline and count the occurrences
    grouped = df.groupby(['run_no', 'matches_ideal']).size().unstack(fill_value=0)

    if True not in grouped.columns:
        grouped[True] = 0

    if False not in grouped.columns:
        grouped[False] = 0

    # Calculate the percentage columns

    grouped['% false'] = ((grouped[False] / (grouped[False] + grouped[True])) * 100).round(2)
    grouped['% true'] = ((grouped[True] / (grouped[False] + grouped[True])) * 100).round(2)
    # Display the grouped DataFrame
    #print(grouped)

    # Compute the true reproducibility
    numerator = grouped[True].sum()
    denominator = grouped[False].sum() + grouped[True].sum()
    #print(f'numerator={numerator} - denominator-{denominator}')

    true_value = ((numerator / denominator) * 100).round(2)

 
    print(f'Accuracy-{true_value}')



def main():
    df = read(READ_QUERY)
    print_reproducibility_stats(df)
    print_accuracy_stats(df)

if __name__ == "__main__":
    main()

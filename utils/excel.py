import pandas as pd


def read_input_file(file_path):

    df = pd.read_excel(file_path)

    return df


def save_output_file(data, output_path):

    output_df = pd.DataFrame(data)

    output_df.to_excel(output_path, index=False)

    print(f"\nOutput saved to: {output_path}")
import pandas as pd
from pandas import DataFrame
from typing import Union

def generate_diff_dataframe(
    df_A: DataFrame,
    df_B: DataFrame,
    key_column: Union[str, list[str]]
) -> DataFrame:
    """
    差分データの生成
    Args:
        df_A (DataFrame): 比較元のデータフレーム
        df_B (DataFrame): 比較対象のデータフレーム
        key_column (str | list[str]): 主キー列名または複数主キーのリスト
    Returns:
        DataFrame: Bの構成に query_action 列を加えた差分付きデータフレーム
    """
    df_A = df_A.fillna("").copy()
    df_B = df_B.fillna("").copy()

    # outer join による統合とマージ情報の付与
    merged = pd.merge(df_A, df_B, on=key_column, how="outer", suffixes=('_A', '_B'), indicator=True)

    # 結果格納用リスト
    diff_rows = []

    # 各行の比較
    for _, row in merged.iterrows():
        key = row[key_column]
        if row['_merge'] == 'left_only':
            # Aにしかない → delete
            delete_row = df_A[df_A[key_column] == key].iloc[0].copy()
            delete_row['query_action'] = 'delete'
            diff_rows.append(delete_row)
        elif row['_merge'] == 'right_only':
            # Bにしかない → insert
            insert_row = df_B[df_B[key_column] == key].iloc[0].copy()
            insert_row['query_action'] = 'insert'
            diff_rows.append(insert_row)
        else:
            # 両方にある → 値を比較して update or skip
            row_A = df_A[df_A[key_column] == key].iloc[0]
            row_B = df_B[df_B[key_column] == key].iloc[0]

            if row_A.equals(row_B):
                action = 'skip'
            else:
                action = 'update'

            updated_row = row_B.copy()
            updated_row['query_action'] = action
            diff_rows.append(updated_row)

    # カラム順はBに合わせ、query_actionを最後に
    result_df = pd.DataFrame(diff_rows).fillna("").copy()
    columns_order = list(df_B.columns) + ['query_action']
    return result_df[columns_order]

def main():
    df_A = pd.DataFrame([
        {"id": 1, "name": "Alice", "age": 30},
        {"id": 2, "name": "Bob", "age": 25},
        {"id": 3, "name": "Charlie", "age": 40}
    ])

    df_B = pd.DataFrame([
        {"id": 1, "name": "Alice", "age": 31},
        {"id": 2, "name": "Bob", "age": 25},
        {"id": 4, "name": "Diana", "age": 22}
    ])

    diff_df = generate_diff_dataframe(df_A, df_B, key_column="id")
    print(diff_df)

if __name__ == "__main__":
    main()
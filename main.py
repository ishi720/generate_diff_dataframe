import pandas as pd

def generate_diff_dataframe(df_A, df_B, key_column):
    """
    差分データの生成
    Args:
        df_A: データフレームA
        df_B: データフレームB
        key_column: 主キーとなるカラム名
    Returns:
        差分付きデータフレーム（B側のカラム構成 + query_action列）
    """
    # 欠損値補完
    df_A = df_A.fillna("")
    df_B = df_B.fillna("")

    # outer join による統合とマージ情報の付与
    merged_A = pd.merge(df_A, df_B, on=key_column, how="outer", suffixes=('', '_B'), indicator=True)
    merged_B = pd.merge(df_A, df_B, on=key_column, how="outer", suffixes=('_A', ''), indicator=True)

    # 両方に存在するレコードを抽出
    both_df = merged_B[merged_B['_merge'] == 'both'].copy()

    # A, B それぞれの "both" 対象行を key_column をインデックスにして抽出
    df_A_both = df_A.set_index(key_column).loc[both_df[key_column]].sort_index()
    df_B_both = df_B.set_index(key_column).loc[both_df[key_column]].sort_index()

    # 差分比較
    differences = (df_A_both != df_B_both)
    diff_exists = differences.any(axis=1)

    # query_action列の追加
    df_B = df_B.copy()
    df_B['query_action'] = ''

    # 更新 or スキップの判定
    both_df = df_B.set_index(key_column).loc[both_df[key_column]].copy()
    both_df['query_action'] = 'skip'
    both_df.loc[diff_exists, 'query_action'] = 'update'

    # 削除対象
    only_A = merged_A[merged_A['_merge'] == 'left_only'][[key_column]].copy()
    only_A = pd.merge(only_A, df_A, on=key_column)
    only_A['query_action'] = 'delete'

    # 追加対象
    only_B = merged_B[merged_B['_merge'] == 'right_only'][[key_column]].copy()
    only_B = pd.merge(only_B, df_B.drop(columns='query_action'), on=key_column)
    only_B['query_action'] = 'insert'

    # カラム順に query_action を追加
    result_columns = list(df_B.columns)
    result_df = pd.concat([both_df, only_A[result_columns], only_B[result_columns]], ignore_index=True)

    return result_df

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
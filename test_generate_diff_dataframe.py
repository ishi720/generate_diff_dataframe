import pandas as pd
import pytest
from main import generate_diff_dataframe

@pytest.fixture
def sample_data():
    df_A = pd.DataFrame([
        {"id": 1, "name": "Alice", "age": 30},
        {"id": 2, "name": "Bob", "age": 25},
        {"id": 3, "name": "Charlie", "age": 40}
    ])

    df_B = pd.DataFrame([
        {"id": 1, "name": "Alice", "age": 31},  # age が変更 → update
        {"id": 2, "name": "Bob", "age": 25},    # 同一 → skip
        {"id": 4, "name": "Diana", "age": 22}   # 新規 → insert
    ])
    return df_A, df_B

def test_generate_diff_dataframe(sample_data):
    df_A, df_B = sample_data
    result = generate_diff_dataframe(df_A, df_B, key_column="id")

    # 結果を辞書のリスト変換
    result_dicts = result.to_dict(orient="records")

    # 期待している出力結果
    expected = [
        {"id": 1, "name": "Alice", "age": 31, "query_action": "update"},
        {"id": 2, "name": "Bob", "age": 25, "query_action": "skip"},
        {"id": 3, "name": "Charlie", "age": 40, "query_action": "delete"},
        {"id": 4, "name": "Diana", "age": 22, "query_action": "insert"}
    ]

    assert result_dicts == expected

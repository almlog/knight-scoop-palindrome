"""data_logic のユニットテスト。"""

import os
import tempfile
import pandas as pd
import pytest
from data_logic import (
    classify_word,
    ensure_columns,
    inject_legendary,
    load_csvs,
    load_data,
    prepare_datasets,
    REQUIRED_COLUMNS,
)


# ── フィクスチャ ──────────────────────────────────────────
@pytest.fixture
def sample_csv(tmp_path):
    """テスト用CSVを作成して返す。"""
    df = pd.DataFrame([
        {"品詞": "名詞", "品詞細分類": "一般", "ワード": "しるし", "ヨミガナ": "シルシ", "音素": "sh i r u sh i", "回文判定": "〇"},
        {"品詞": "動詞", "品詞細分類": "一般", "ワード": "ぬすむ", "ヨミガナ": "ヌスム", "音素": "n u s u m u", "回文判定": "×"},
        {"品詞": "名詞", "品詞細分類": "一般", "ワード": "夫", "ヨミガナ": "オット", "音素": "o t t o", "回文判定": "〇"},
        {"品詞": "動詞", "品詞細分類": "一般", "ワード": "かぶく", "ヨミガナ": "カブク", "音素": "k a b u k u", "回文判定": "〇"},
        {"品詞": "動物", "品詞細分類": "鳥類", "ワード": "カモメ", "ヨミガナ": "カモメ", "音素": "k a m o m e", "回文判定": "×"},
    ])
    fpath = tmp_path / "knight_scoop_all_keywords_investigation.csv"
    df.to_csv(fpath, index=False, encoding="utf-8-sig")
    return tmp_path


@pytest.fixture
def sample_df():
    """テスト用DataFrame。"""
    return pd.DataFrame([
        {"品詞": "名詞", "品詞細分類": "一般", "ワード": "しるし", "ヨミガナ": "シルシ", "音素": "sh i r u sh i", "回文判定": "〇"},
        {"品詞": "動詞", "品詞細分類": "一般", "ワード": "かぶく", "ヨミガナ": "カブク", "音素": "k a b u k u", "回文判定": "〇"},
        {"品詞": "名詞", "品詞細分類": "一般", "ワード": "夫", "ヨミガナ": "オット", "音素": "o t t o", "回文判定": "〇"},
        {"品詞": "動物", "品詞細分類": "鳥類", "ワード": "カモメ", "ヨミガナ": "カモメ", "音素": "k a m o m e", "回文判定": "×"},
    ])


# ── load_csvs ──────────────────────────────────────────────
class TestLoadCsvs:
    def test_loads_existing_csv(self, sample_csv):
        df, errors = load_csvs(str(sample_csv))
        assert len(df) == 5
        assert errors == []

    def test_missing_dir_returns_empty(self, tmp_path):
        df, errors = load_csvs(str(tmp_path / "nonexistent"))
        assert len(df) == 0

    def test_empty_csv_skipped(self, tmp_path):
        fpath = tmp_path / "knight_scoop_all_keywords_investigation.csv"
        pd.DataFrame().to_csv(fpath, index=False)
        df, errors = load_csvs(str(tmp_path))
        assert len(df) == 0

    def test_deduplicates_by_word(self, tmp_path):
        df = pd.DataFrame([
            {"ワード": "しるし", "回文判定": "〇"},
            {"ワード": "しるし", "回文判定": "〇"},
        ])
        fpath = tmp_path / "knight_scoop_all_keywords_investigation.csv"
        df.to_csv(fpath, index=False, encoding="utf-8-sig")
        result, _ = load_csvs(str(tmp_path))
        assert len(result) == 1


# ── inject_legendary ──────────────────────────────────────
class TestInjectLegendary:
    def test_adds_legendary_when_missing(self, sample_df):
        result = inject_legendary(sample_df)
        assert "オオエンマハンミョウ" in result["ワード"].values
        assert len(result) == len(sample_df) + 1

    def test_no_duplicate_if_already_exists(self):
        df = pd.DataFrame([{"ワード": "オオエンマハンミョウ", "回文判定": "〇"}])
        result = inject_legendary(df)
        assert len(result[result["ワード"] == "オオエンマハンミョウ"]) == 1


# ── ensure_columns ─────────────────────────────────────────
class TestEnsureColumns:
    def test_adds_missing_columns(self):
        df = pd.DataFrame({"ワード": ["テスト"]})
        result = ensure_columns(df)
        for col in REQUIRED_COLUMNS:
            assert col in result.columns

    def test_preserves_existing_data(self, sample_df):
        result = ensure_columns(sample_df)
        assert result["ワード"].tolist() == sample_df["ワード"].tolist()


# ── classify_word ──────────────────────────────────────────
class TestClassifyWord:
    def test_verb_general_is_yellow(self):
        assert classify_word({"品詞": "動詞", "品詞細分類": "一般"}) == "yellow"

    def test_noun_is_green(self):
        assert classify_word({"品詞": "名詞", "品詞細分類": "一般"}) == "green"

    def test_verb_non_general_is_green(self):
        assert classify_word({"品詞": "動詞", "品詞細分類": "非自立"}) == "green"

    def test_animal_is_green(self):
        assert classify_word({"品詞": "動物", "品詞細分類": "鳥類"}) == "green"

    def test_empty_row_is_green(self):
        assert classify_word({}) == "green"


# ── prepare_datasets ───────────────────────────────────────
class TestPrepareDatasets:
    def test_splits_correctly(self, sample_df):
        df_all, df_hits, df_green, df_yellow, df_miss = prepare_datasets(sample_df)
        assert len(df_hits) == 3  # しるし, かぶく, 夫
        assert len(df_miss) == 1  # カモメ
        assert len(df_green) == 2  # しるし, 夫 (名詞)
        assert len(df_yellow) == 1  # かぶく (動詞・一般)

    def test_quality_column_added(self, sample_df):
        df_all, *_ = prepare_datasets(sample_df)
        assert "品質" in df_all.columns

    def test_empty_df(self):
        empty = pd.DataFrame(columns=REQUIRED_COLUMNS)
        df_all, df_hits, df_green, df_yellow, df_miss = prepare_datasets(empty)
        assert len(df_hits) == 0
        assert len(df_miss) == 0


# ── load_data (統合テスト) ─────────────────────────────────
class TestLoadData:
    def test_full_pipeline(self, sample_csv):
        df, errors = load_data(str(sample_csv))
        assert "オオエンマハンミョウ" in df["ワード"].values
        assert len(df) == 6  # 5 + 1 legendary
        for col in REQUIRED_COLUMNS:
            assert col in df.columns

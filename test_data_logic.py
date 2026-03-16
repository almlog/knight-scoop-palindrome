"""data_logic のユニットテスト。"""

import os
import tempfile
import pandas as pd
import pytest
from data_logic import (
    APPROVED_APPROXIMATE,
    FREE_INPUT_MAX_LENGTH,
    classify_word,
    ensure_columns,
    inject_legendary,
    is_strict_palindrome,
    load_csvs,
    load_data,
    prepare_datasets,
    validate_free_input,
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
        {"品詞": "名詞", "品詞細分類": "一般", "ワード": "夫", "ヨミガナ": "オット", "音素": "o t t o", "回文判定": "〇"},
        {"品詞": "副詞", "品詞細分類": "一般", "ワード": "あかあか", "ヨミガナ": "アカアカ", "音素": "a k a a k a", "回文判定": "〇"},
        {"品詞": "動詞", "品詞細分類": "一般", "ワード": "うろうろ", "ヨミガナ": "ウロウロ", "音素": "u r o o r u", "回文判定": "〇"},
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
        df_all, df_hits, df_green, df_yellow, df_miss, df_review = prepare_datasets(sample_df)
        # 夫(o t t o)=厳密回文, あかあか(a k a a k a)=厳密回文, うろうろ(u r o o r u)=厳密回文
        assert len(df_hits) == 3
        assert len(df_review) == 0
        assert len(df_miss) == 1  # カモメ
        assert len(df_green) == 2  # 夫(名詞), あかあか(副詞)
        assert len(df_yellow) == 1  # うろうろ(動詞・一般)

    def test_quality_column_added(self, sample_df):
        df_all, *_ = prepare_datasets(sample_df)
        assert "品質" in df_all.columns

    def test_empty_df(self):
        empty = pd.DataFrame(columns=REQUIRED_COLUMNS)
        df_all, df_hits, df_green, df_yellow, df_miss, df_review = prepare_datasets(empty)
        assert len(df_hits) == 0
        assert len(df_miss) == 0


# ── is_strict_palindrome ───────────────────────────────────
class TestIsStrictPalindrome:
    def test_true_palindrome(self):
        assert is_strict_palindrome("a k a a k a") is True

    def test_single_phoneme(self):
        assert is_strict_palindrome("a") is True

    def test_symmetric(self):
        assert is_strict_palindrome("o t t o") is True

    def test_not_palindrome(self):
        assert is_strict_palindrome("o o ch u u") is False  # オウチュウ

    def test_urouro_is_palindrome(self):
        # u r o o r u は厳密に回文
        assert is_strict_palindrome("u r o o r u") is True

    def test_approximate_not_strict(self):
        # u r o o r o は o≠u で回文でない
        assert is_strict_palindrome("u r o o r o") is False

    def test_legendary_approximate(self):
        # オオエンマハンミョウ: e≠y
        assert is_strict_palindrome("o o e m m a h a m m y o o") is False

    def test_empty_string(self):
        assert is_strict_palindrome("") is False

    def test_none(self):
        assert is_strict_palindrome(None) is False


# ── prepare_datasets with verification ─────────────────────
class TestPrepareWithVerification:
    def test_strict_palindrome_is_confirmed(self):
        df = pd.DataFrame([
            {"品詞": "名詞", "品詞細分類": "一般", "ワード": "夫",
             "ヨミガナ": "オット", "音素": "o t t o", "回文判定": "〇"},
        ])
        df_all, df_hits, *_ = prepare_datasets(df)
        assert len(df_hits) == 1
        assert df_hits.iloc[0]["検証"] == "確認済み"

    def test_approximate_palindrome_needs_verification(self):
        df = pd.DataFrame([
            {"品詞": "動物", "品詞細分類": "鳥類", "ワード": "オウチュウ",
             "ヨミガナ": "オウチュウ", "音素": "o o ch u u", "回文判定": "〇"},
        ])
        df_all, df_hits, _, _, _, df_review = prepare_datasets(df)
        assert len(df_hits) == 0
        assert len(df_review) == 0  # NGなので要検証にも残らない

    def test_approved_approximate_is_confirmed(self):
        """ユーザーが聴いてOKと判定した近似回文は確認済みに入る。"""
        df = pd.DataFrame([
            {"品詞": "動詞", "品詞細分類": "一般", "ワード": "あえぎゃ",
             "ヨミガナ": "アエギャ", "音素": "a e g y a", "回文判定": "〇"},
        ])
        df_all, df_hits, _, _, _, df_review = prepare_datasets(df)
        assert len(df_hits) == 1
        assert df_hits.iloc[0]["検証"] == "確認済み"

    def test_approved_list_contains_four(self):
        assert "あえぎゃ" in APPROVED_APPROXIMATE
        assert "あえりゃ" in APPROVED_APPROXIMATE
        assert "おえよ" in APPROVED_APPROXIMATE
        assert "オオエンマハンミョウ" in APPROVED_APPROXIMATE
        assert len(APPROVED_APPROXIMATE) == 4

    def test_kanji_variant_approved_by_phoneme(self):
        """同じ音素パターンの漢字バリエーションも承認される。"""
        df = pd.DataFrame([
            {"品詞": "動詞", "品詞細分類": "一般", "ワード": "喘ぎゃ",
             "ヨミガナ": "アエギャ", "音素": "a e g y a", "回文判定": "〇"},
            {"品詞": "動詞", "品詞細分類": "一般", "ワード": "会えりゃ",
             "ヨミガナ": "アエリャ", "音素": "a e r y a", "回文判定": "〇"},
            {"品詞": "動詞", "品詞細分類": "一般", "ワード": "終えよ",
             "ヨミガナ": "オエヨ", "音素": "o e y o", "回文判定": "〇"},
        ])
        df_all, df_hits, _, _, _, df_review = prepare_datasets(df)
        assert len(df_hits) == 3  # 全部確認済み
        assert len(df_review) == 0

    def test_rejected_approximate_excluded(self):
        """NGと判定された近似回文は確認済みにも要検証にも入らない。"""
        df = pd.DataFrame([
            {"品詞": "動物", "品詞細分類": "鳥類", "ワード": "オウチュウ",
             "ヨミガナ": "オウチュウ", "音素": "o o ch u u", "回文判定": "〇"},
            {"品詞": "名詞", "品詞細分類": "一般", "ワード": "欧風",
             "ヨミガナ": "オウフウ", "音素": "o o f u u", "回文判定": "〇"},
        ])
        df_all, df_hits, _, _, _, df_review = prepare_datasets(df)
        assert len(df_hits) == 0
        assert len(df_review) == 0

    def test_non_hit_has_no_verification(self):
        df = pd.DataFrame([
            {"品詞": "名詞", "品詞細分類": "一般", "ワード": "テスト",
             "ヨミガナ": "テスト", "音素": "t e s u t o", "回文判定": "×"},
        ])
        df_all, *_ = prepare_datasets(df)
        assert df_all.iloc[0]["検証"] == ""


# ── validate_free_input ────────────────────────────────────
class TestValidateFreeInput:
    def test_valid_input(self):
        ok, msg = validate_free_input("オオエンマハンミョウ")
        assert ok is True
        assert msg == ""

    def test_empty(self):
        ok, msg = validate_free_input("")
        assert ok is False

    def test_too_long(self):
        ok, msg = validate_free_input("あ" * (FREE_INPUT_MAX_LENGTH + 1))
        assert ok is False
        assert "30" in msg

    def test_exactly_max(self):
        ok, msg = validate_free_input("あ" * FREE_INPUT_MAX_LENGTH)
        assert ok is True

    def test_whitespace_only(self):
        ok, msg = validate_free_input("   ")
        assert ok is False


# ── load_data (統合テスト) ─────────────────────────────────
class TestLoadData:
    def test_full_pipeline(self, sample_csv):
        df, errors = load_data(str(sample_csv))
        assert "オオエンマハンミョウ" in df["ワード"].values
        assert len(df) == 6  # 5 + 1 legendary
        for col in REQUIRED_COLUMNS:
            assert col in df.columns

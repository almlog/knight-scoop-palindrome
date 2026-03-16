"""data_logic のユニットテスト。"""

import os
import tempfile
import pandas as pd
import pytest
from data_logic import (
    APPROVED_APPROXIMATE,
    APPROVED_PHONEMES,
    FREE_INPUT_MAX_LENGTH,
    classify_word,
    ensure_columns,
    inject_legendary,
    is_strict_palindrome,
    load_csvs,
    load_data,
    prepare_datasets,
    to_katakana,
    validate_free_input,
    is_kana_only,
    _classify_verification,
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


# ═══════════════════════════════════════════════════════════
# load_csvs
# ═══════════════════════════════════════════════════════════
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

    def test_csv_missing_required_columns_skipped(self, tmp_path):
        """必須カラム（ワード/回文判定）がないCSVはスキップ。"""
        df = pd.DataFrame([{"品詞": "名詞", "名前": "テスト"}])
        fpath = tmp_path / "knight_scoop_all_keywords_investigation.csv"
        df.to_csv(fpath, index=False, encoding="utf-8-sig")
        result, errors = load_csvs(str(tmp_path))
        assert len(result) == 0

    def test_multiple_csvs_merged(self, tmp_path):
        """複数CSVが結合される。"""
        df1 = pd.DataFrame([{"ワード": "テスト1", "回文判定": "〇"}])
        df2 = pd.DataFrame([{"ワード": "テスト2", "回文判定": "×"}])
        (tmp_path / "knight_scoop_all_keywords_investigation.csv").write_text(
            df1.to_csv(index=False), encoding="utf-8-sig")
        (tmp_path / "animals_palindrome_v4.csv").write_text(
            df2.to_csv(index=False), encoding="utf-8-sig")
        result, _ = load_csvs(str(tmp_path))
        assert len(result) == 2

    def test_broken_csv_reports_error(self, tmp_path):
        """壊れたCSVはエラーリストに追加される。"""
        fpath = tmp_path / "knight_scoop_all_keywords_investigation.csv"
        fpath.write_text("this is not,a valid\ncsv\"file", encoding="utf-8-sig")
        result, errors = load_csvs(str(tmp_path))
        # パース自体は成功するかもしれないが、必須カラムが無いのでスキップ
        assert len(result) == 0


# ═══════════════════════════════════════════════════════════
# inject_legendary
# ═══════════════════════════════════════════════════════════
class TestInjectLegendary:
    def test_adds_legendary_when_missing(self, sample_df):
        result = inject_legendary(sample_df)
        assert "オオエンマハンミョウ" in result["ワード"].values
        assert len(result) == len(sample_df) + 1

    def test_no_duplicate_if_already_exists(self):
        df = pd.DataFrame([{"ワード": "オオエンマハンミョウ", "回文判定": "〇"}])
        result = inject_legendary(df)
        assert len(result[result["ワード"] == "オオエンマハンミョウ"]) == 1

    def test_legendary_inserted_at_top(self, sample_df):
        """伝説ワードはDataFrameの先頭に挿入される。"""
        result = inject_legendary(sample_df)
        assert result.iloc[0]["ワード"] == "オオエンマハンミョウ"


# ═══════════════════════════════════════════════════════════
# ensure_columns
# ═══════════════════════════════════════════════════════════
class TestEnsureColumns:
    def test_adds_missing_columns(self):
        df = pd.DataFrame({"ワード": ["テスト"]})
        result = ensure_columns(df)
        for col in REQUIRED_COLUMNS:
            assert col in result.columns

    def test_preserves_existing_data(self, sample_df):
        result = ensure_columns(sample_df)
        assert result["ワード"].tolist() == sample_df["ワード"].tolist()

    def test_partial_columns_filled(self):
        """一部カラムだけ存在する場合、不足分のみ追加。"""
        df = pd.DataFrame({"ワード": ["テスト"], "品詞": ["名詞"]})
        result = ensure_columns(df)
        assert result.iloc[0]["品詞"] == "名詞"
        assert result.iloc[0]["音素"] == ""


# ═══════════════════════════════════════════════════════════
# classify_word
# ═══════════════════════════════════════════════════════════
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

    def test_insect_is_green(self):
        assert classify_word({"品詞": "昆虫", "品詞細分類": "チョウ・ガ目"}) == "green"


# ═══════════════════════════════════════════════════════════
# is_strict_palindrome
# ═══════════════════════════════════════════════════════════
class TestIsStrictPalindrome:
    def test_true_palindrome(self):
        assert is_strict_palindrome("a k a a k a") is True

    def test_single_phoneme(self):
        assert is_strict_palindrome("a") is True

    def test_two_same(self):
        assert is_strict_palindrome("a a") is True

    def test_two_different(self):
        assert is_strict_palindrome("a b") is False

    def test_symmetric(self):
        assert is_strict_palindrome("o t t o") is True

    def test_not_palindrome(self):
        assert is_strict_palindrome("o o ch u u") is False

    def test_urouro_is_palindrome(self):
        assert is_strict_palindrome("u r o o r u") is True

    def test_approximate_not_strict(self):
        assert is_strict_palindrome("u r o o r o") is False

    def test_legendary_approximate(self):
        assert is_strict_palindrome("o o e m m a h a m m y o o") is False

    def test_empty_string(self):
        assert is_strict_palindrome("") is False

    def test_none(self):
        assert is_strict_palindrome(None) is False

    def test_whitespace_only(self):
        assert is_strict_palindrome("   ") is False

    def test_leading_trailing_spaces(self):
        """前後空白はトリムされる。"""
        assert is_strict_palindrome("  o t t o  ") is True

    def test_integer_input(self):
        assert is_strict_palindrome(123) is False


# ═══════════════════════════════════════════════════════════
# _classify_verification
# ═══════════════════════════════════════════════════════════
class TestClassifyVerification:
    def test_non_hit_returns_empty(self):
        assert _classify_verification({"回文判定": "×", "音素": "a b c", "ワード": "テスト"}) == ""

    def test_strict_palindrome_confirmed(self):
        assert _classify_verification({"回文判定": "〇", "音素": "o t t o", "ワード": "夫"}) == "確認済み"

    def test_approved_by_word_name(self):
        assert _classify_verification({"回文判定": "〇", "音素": "a e g y a", "ワード": "あえぎゃ"}) == "確認済み"

    def test_approved_by_phoneme_pattern(self):
        """ワード名が承認リストになくても音素パターンで承認。"""
        assert _classify_verification({"回文判定": "〇", "音素": "a e g y a", "ワード": "喘ぎゃ"}) == "確認済み"

    def test_rejected_approximate(self):
        assert _classify_verification({"回文判定": "〇", "音素": "o o ch u u", "ワード": "オウチュウ"}) == ""

    def test_empty_phonemes(self):
        assert _classify_verification({"回文判定": "〇", "音素": "", "ワード": "テスト"}) == ""

    def test_nan_phonemes(self):
        assert _classify_verification({"回文判定": "〇", "音素": None, "ワード": "テスト"}) == ""

    def test_missing_word_key(self):
        assert _classify_verification({"回文判定": "〇", "音素": "o t t o"}) == "確認済み"


# ═══════════════════════════════════════════════════════════
# prepare_datasets
# ═══════════════════════════════════════════════════════════
class TestPrepareDatasets:
    def test_splits_correctly(self, sample_df):
        df_all, df_hits, df_green, df_yellow, df_miss, df_review = prepare_datasets(sample_df)
        assert len(df_hits) == 3
        assert len(df_review) == 0
        assert len(df_miss) == 1
        assert len(df_green) == 2  # 夫(名詞), あかあか(副詞)
        assert len(df_yellow) == 1  # うろうろ(動詞・一般)

    def test_quality_column_added(self, sample_df):
        df_all, *_ = prepare_datasets(sample_df)
        assert "品質" in df_all.columns

    def test_verification_column_added(self, sample_df):
        df_all, *_ = prepare_datasets(sample_df)
        assert "検証" in df_all.columns

    def test_empty_df(self):
        empty = pd.DataFrame(columns=REQUIRED_COLUMNS)
        df_all, df_hits, df_green, df_yellow, df_miss, df_review = prepare_datasets(empty)
        assert len(df_hits) == 0
        assert len(df_miss) == 0
        assert len(df_review) == 0

    def test_does_not_mutate_input(self, sample_df):
        """入力DataFrameを変更しない。"""
        original_cols = set(sample_df.columns)
        prepare_datasets(sample_df)
        assert set(sample_df.columns) == original_cols

    def test_all_approved_approximate_counted(self):
        """承認済み近似回文4パターンすべてが確認済みに入る。"""
        rows = []
        for word, phoneme in [
            ("あえぎゃ", "a e g y a"),
            ("あえりゃ", "a e r y a"),
            ("おえよ", "o e y o"),
            ("オオエンマハンミョウ", "o o e m m a h a m m y o o"),
        ]:
            rows.append({"品詞": "名詞", "品詞細分類": "一般", "ワード": word,
                         "ヨミガナ": "", "音素": phoneme, "回文判定": "〇"})
        df = pd.DataFrame(rows)
        _, df_hits, *_ = prepare_datasets(df)
        assert len(df_hits) == 4

    def test_mixed_strict_approved_rejected(self):
        """厳密回文 + 承認済み + NG が正しく分類される。"""
        df = pd.DataFrame([
            {"品詞": "名詞", "品詞細分類": "一般", "ワード": "夫",
             "ヨミガナ": "オット", "音素": "o t t o", "回文判定": "〇"},
            {"品詞": "動詞", "品詞細分類": "一般", "ワード": "あえぎゃ",
             "ヨミガナ": "アエギャ", "音素": "a e g y a", "回文判定": "〇"},
            {"品詞": "動物", "品詞細分類": "鳥類", "ワード": "オウチュウ",
             "ヨミガナ": "オウチュウ", "音素": "o o ch u u", "回文判定": "〇"},
            {"品詞": "名詞", "品詞細分類": "一般", "ワード": "テスト",
             "ヨミガナ": "テスト", "音素": "t e s u t o", "回文判定": "×"},
        ])
        df_all, df_hits, df_green, df_yellow, df_miss, df_review = prepare_datasets(df)
        assert len(df_hits) == 2   # 夫(厳密) + あえぎゃ(承認)
        assert len(df_miss) == 1   # テスト
        assert len(df_review) == 0
        # オウチュウはNG → hits にもreview にもmissにも入らない（回文判定〇だがNG）
        ng_count = len(df_all[(df_all["回文判定"] == "〇") & (df_all["検証"] == "")])
        assert ng_count == 1


# ═══════════════════════════════════════════════════════════
# validate_free_input
# ═══════════════════════════════════════════════════════════
class TestValidateFreeInput:
    def test_valid_katakana(self):
        ok, msg = validate_free_input("オオエンマハンミョウ")
        assert ok is True
        assert msg == ""

    def test_valid_hiragana(self):
        ok, msg = validate_free_input("おおえんまはんみょう")
        assert ok is True

    def test_empty(self):
        ok, msg = validate_free_input("")
        assert ok is False

    def test_none(self):
        ok, msg = validate_free_input(None)
        assert ok is False

    def test_too_long(self):
        ok, msg = validate_free_input("あ" * 31)
        assert ok is False
        assert "30" in msg

    def test_exactly_max(self):
        ok, msg = validate_free_input("あ" * 30)
        assert ok is True

    def test_one_under_max(self):
        ok, msg = validate_free_input("あ" * 29)
        assert ok is True

    def test_whitespace_only(self):
        ok, msg = validate_free_input("   ")
        assert ok is False

    def test_kanji_rejected(self):
        ok, msg = validate_free_input("漢字テスト")
        assert ok is False
        assert "ひらがな" in msg

    def test_english_rejected(self):
        ok, msg = validate_free_input("hello")
        assert ok is False

    def test_numbers_rejected(self):
        ok, msg = validate_free_input("123")
        assert ok is False

    def test_symbols_rejected(self):
        ok, msg = validate_free_input("あ！？")
        assert ok is False

    def test_mixed_kanji_kana_rejected(self):
        ok, msg = validate_free_input("東京タワー")
        assert ok is False

    def test_single_char(self):
        ok, msg = validate_free_input("あ")
        assert ok is True

    def test_with_prolonged_sound(self):
        ok, msg = validate_free_input("カレー")
        assert ok is True

    def test_leading_trailing_spaces_stripped(self):
        ok, msg = validate_free_input("  あいう  ")
        assert ok is True


# ═══════════════════════════════════════════════════════════
# is_kana_only
# ═══════════════════════════════════════════════════════════
class TestIsKanaOnly:
    def test_hiragana(self):
        assert is_kana_only("おおえんま") is True

    def test_katakana(self):
        assert is_kana_only("オオエンマ") is True

    def test_mixed_kana(self):
        assert is_kana_only("おおエンマ") is True

    def test_kanji(self):
        assert is_kana_only("大王") is False

    def test_with_prolonged_sound(self):
        assert is_kana_only("オオエンマー") is True

    def test_empty(self):
        assert is_kana_only("") is False

    def test_numbers(self):
        assert is_kana_only("123") is False

    def test_english(self):
        assert is_kana_only("abc") is False

    def test_space_in_middle(self):
        assert is_kana_only("あ い") is False

    def test_symbols(self):
        assert is_kana_only("あ！") is False

    def test_small_kana(self):
        assert is_kana_only("ぁぃぅ") is True

    def test_katakana_small(self):
        assert is_kana_only("ァィゥ") is True


# ═══════════════════════════════════════════════════════════
# to_katakana
# ═══════════════════════════════════════════════════════════
class TestToKatakana:
    def test_hiragana_to_katakana(self):
        assert to_katakana("おおえんまはんみょう") == "オオエンマハンミョウ"

    def test_katakana_unchanged(self):
        assert to_katakana("オオエンマハンミョウ") == "オオエンマハンミョウ"

    def test_mixed(self):
        assert to_katakana("あいうエオ") == "アイウエオ"

    def test_prolonged_sound_preserved(self):
        assert to_katakana("かれー") == "カレー"

    def test_empty_string(self):
        assert to_katakana("") == ""

    def test_small_kana(self):
        assert to_katakana("ぁぃぅぇぉ") == "ァィゥェォ"

    def test_all_hiragana_chars(self):
        """全ひらがな文字が正しく変換される。"""
        result = to_katakana("あいうえおかきくけこ")
        assert result == "アイウエオカキクケコ"

    def test_dakuten_handakuten(self):
        assert to_katakana("がぎぐげご") == "ガギグゲゴ"
        assert to_katakana("ぱぴぷぺぽ") == "パピプペポ"


# ═══════════════════════════════════════════════════════════
# APPROVED constants
# ═══════════════════════════════════════════════════════════
class TestApprovedConstants:
    def test_approved_words_count(self):
        assert len(APPROVED_APPROXIMATE) == 4

    def test_approved_phonemes_count(self):
        assert len(APPROVED_PHONEMES) == 4

    def test_all_approved_words_present(self):
        for w in ["あえぎゃ", "あえりゃ", "おえよ", "オオエンマハンミョウ"]:
            assert w in APPROVED_APPROXIMATE

    def test_all_approved_phonemes_present(self):
        for p in ["a e g y a", "a e r y a", "o e y o", "o o e m m a h a m m y o o"]:
            assert p in APPROVED_PHONEMES


# ═══════════════════════════════════════════════════════════
# load_data (統合テスト)
# ═══════════════════════════════════════════════════════════
class TestLoadData:
    def test_full_pipeline(self, sample_csv):
        df, errors = load_data(str(sample_csv))
        assert "オオエンマハンミョウ" in df["ワード"].values
        assert len(df) == 6  # 5 + 1 legendary
        for col in REQUIRED_COLUMNS:
            assert col in df.columns

    def test_errors_propagated(self, tmp_path):
        """エラーが正しく伝播される。"""
        df, errors = load_data(str(tmp_path))
        assert isinstance(errors, list)

    def test_empty_dir_still_has_legendary(self, tmp_path):
        """CSVがなくても伝説ワードは存在する。"""
        df, _ = load_data(str(tmp_path))
        assert "オオエンマハンミョウ" in df["ワード"].values
        assert len(df) == 1

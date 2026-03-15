"""ビジネスロジック（UI非依存・テスト可能）。"""

import os
import io
import pandas as pd


# ── 定数 ──────────────────────────────────────────────────
REQUIRED_COLUMNS = ["品詞", "品詞細分類", "ワード", "ヨミガナ", "音素", "回文判定"]

CSV_FILES = [
    "knight_scoop_all_keywords_investigation.csv",
    "animals_palindrome_v4.csv",
    "inat_palindrome_v5.csv",
]

LEGENDARY_WORDS = [
    {
        "品詞": "特別枠",
        "品詞細分類": "伝説",
        "ワード": "オオエンマハンミョウ",
        "ヨミガナ": "オオエンマハンミョウ",
        "音素": "o o e m m a h a m m y o o",
        "回文判定": "〇",
    },
]


# ── データ読み込み ────────────────────────────────────────
def load_csvs(base_dir):
    """CSVファイルを読み込み、結合してDataFrameを返す。"""
    dfs = []
    errors = []

    for fname in CSV_FILES:
        fpath = os.path.join(base_dir, fname)
        try:
            df = pd.read_csv(fpath, encoding="utf-8-sig")
            if df.empty or not {"ワード", "回文判定"}.issubset(df.columns):
                continue
            dfs.append(df)
        except FileNotFoundError:
            continue
        except Exception as e:
            errors.append((fname, str(e)))
            continue

    if dfs:
        df_all = pd.concat(dfs, ignore_index=True).drop_duplicates(subset="ワード")
    else:
        df_all = pd.DataFrame(columns=REQUIRED_COLUMNS)

    return df_all, errors


def inject_legendary(df):
    """伝説ワードが未登録なら追加。"""
    existing = set(df["ワード"].tolist())
    new_rows = [lw for lw in LEGENDARY_WORDS if lw["ワード"] not in existing]
    if new_rows:
        df = pd.concat([pd.DataFrame(new_rows), df], ignore_index=True)
    return df


def ensure_columns(df):
    """必須カラムが存在しなければ空文字で追加。"""
    for col in REQUIRED_COLUMNS:
        if col not in df.columns:
            df[col] = ""
    return df


def load_data(base_dir):
    """CSV読み込み → 伝説ワード追加 → カラム保証 → 完成DataFrameを返す。"""
    df, errors = load_csvs(base_dir)
    df = inject_legendary(df)
    df = ensure_columns(df)
    return df, errors


# ── 回文検証 ──────────────────────────────────────────────
def is_strict_palindrome(phonemes_str):
    """音素列が厳密に回文かどうかを判定。"""
    if not isinstance(phonemes_str, str) or not phonemes_str.strip():
        return False
    p = phonemes_str.strip().split()
    return p == p[::-1]


# ── 品質分類 ──────────────────────────────────────────────
def classify_word(row):
    """ワードを green(新発見) / yellow(参考) に分類。"""
    if row.get("品詞") == "動詞" and row.get("品詞細分類") == "一般":
        return "yellow"
    return "green"


def _classify_verification(row):
    """回文判定〇のワードを厳密検証し、確認済み/要検証を返す。"""
    if row.get("回文判定") != "〇":
        return ""
    if is_strict_palindrome(row.get("音素", "")):
        return "確認済み"
    return "要検証"


def prepare_datasets(df_all):
    """全データから hits / green / yellow / miss を分割。検証カラム付き。"""
    df_all = df_all.copy()
    df_all["品質"] = df_all.apply(classify_word, axis=1)
    df_all["検証"] = df_all.apply(_classify_verification, axis=1)
    df_hits = df_all[(df_all["回文判定"] == "〇") & (df_all["検証"] == "確認済み")].copy()
    df_hits_green = df_hits[df_hits["品質"] == "green"]
    df_hits_yellow = df_hits[df_hits["品質"] == "yellow"]
    df_miss = df_all[df_all["回文判定"] != "〇"].copy()
    df_needs_review = df_all[df_all["検証"] == "要検証"].copy()
    return df_all, df_hits, df_hits_green, df_hits_yellow, df_miss, df_needs_review


# ── 音声生成 ──────────────────────────────────────────────
def generate_audio_bytes(reading):
    """ヨミガナから通常音声と逆再生音声のバイト列を返す。"""
    from gtts import gTTS
    from pydub import AudioSegment

    tts = gTTS(text=reading, lang="ja")
    mp3_fp = io.BytesIO()
    tts.write_to_fp(mp3_fp)
    mp3_fp.seek(0)
    audio = AudioSegment.from_file(mp3_fp, format="mp3")
    reversed_audio = audio.reverse()
    rev_fp = io.BytesIO()
    reversed_audio.export(rev_fp, format="mp3")
    rev_fp.seek(0)
    mp3_fp.seek(0)
    return mp3_fp.read(), rev_fp.read()

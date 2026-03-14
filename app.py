import streamlit as st
import pandas as pd
from gtts import gTTS
from pydub import AudioSegment
import io

st.set_page_config(page_title="逆再生ワード発見器", layout="wide")

st.title("🔄 逆再生ワード発見器（探偵ナイトスクープ提出用）")
st.write("数万件の辞書データから抽出された「音素回文（逆再生しても同じに聞こえる言葉）」の検証アプリです。")

@st.cache_data
def load_data():
    # ユーザーが抽出したCSVを読み込み（〇判定のみ）
    try:
        df = pd.read_csv("knight_scoop_all_keywords_investigation.csv")
        df_hits = df[df["回文判定"] == "〇"].copy()
    except:
        # エラー回避用の空枠
        df_hits = pd.DataFrame(columns=["品詞", "品詞細分類", "ワード", "ヨミガナ", "音素", "回文判定"])
    
    # 🌟 辞書にない「伝説のワード」を特別枠として確実に追加
    legendary_words = [
        {"品詞": "特別枠", "品詞細分類": "伝説", "ワード": "オオエンマハンミョウ", "ヨミガナ": "オオエンマハンミョウ", "音素": "o o e m m a h a m m y o o", "回文判定": "〇"},
        {"品詞": "特別枠", "品詞細分類": "伝説", "ワード": "オオショウ", "ヨミガナ": "オオショウ", "音素": "o o sh o o", "回文判定": "〇"},
        {"品詞": "特別枠", "品詞細分類": "伝説", "ワード": "エイセイ", "ヨミガナ": "エイセイ", "音素": "e e s e e", "回文判定": "〇"}
    ]
    
    # 重複を避けてリストの一番上に追加
    existing_words = df_hits["ワード"].tolist()
    for lw in legendary_words:
        if lw["ワード"] not in existing_words:
            df_hits = pd.concat([pd.DataFrame([lw]), df_hits], ignore_index=True)
            
    return df_hits

df_hits = load_data()

# --- サイドバー（分類フィルター） ---
st.sidebar.header("🔍 分類フィルター")
categories = ["すべて"] + list(df_hits["品詞"].unique())
selected_category = st.sidebar.selectbox("品詞を選択", categories)

if selected_category != "すべて":
    df_hits = df_hits[df_hits["品詞"] == selected_category]

st.write(f"**現在のリスト: {len(df_hits)} 件**")

# --- メイン画面（ワード選択と音声生成） ---
selected_word = st.selectbox("🎧 聴きたいワードを選んでください", df_hits["ワード"])

@st.cache_data
def generate_audio(word):
    # 通常音声 (gTTS)
    tts = gTTS(text=word, lang='ja')
    mp3_fp = io.BytesIO()
    tts.write_to_fp(mp3_fp)
    mp3_fp.seek(0)
    
    # 逆再生音声 (pydub)
    audio = AudioSegment.from_file(mp3_fp, format="mp3")
    reversed_audio = audio.reverse()
    rev_fp = io.BytesIO()
    reversed_audio.export(rev_fp, format="mp3")
    rev_fp.seek(0)
    
    mp3_fp.seek(0)
    return mp3_fp.read(), rev_fp.read()

if selected_word:
    st.subheader(f"【 {selected_word} 】")
    
    row = df_hits[df_hits["ワード"] == selected_word].iloc[0]
    st.text(f"分類: {row['品詞']} - {row['品詞細分類']}  |  音素: {row['音素']}")
    
    # 再生エリア（ボタン押下時にその場で音声を生成して返す）
    with st.spinner("音声を生成中..."):
        normal_bytes, reverse_bytes = generate_audio(selected_word)
        
        col1, col2 = st.columns(2)
        with col1:
            st.success("▶️ 通常再生")
            st.audio(normal_bytes, format="audio/mp3")
        with col2:
            st.warning("◀️ 逆再生（検証！）")
            st.audio(reverse_bytes, format="audio/mp3")

st.markdown("---")
st.markdown("### データテーブル（全件確認用）")
st.dataframe(df_hits[["品詞", "品詞細分類", "ワード", "ヨミガナ", "音素"]])

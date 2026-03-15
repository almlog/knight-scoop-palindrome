import os
import io
import streamlit as st
import pandas as pd
from gtts import gTTS
from pydub import AudioSegment

# ── ページ設定 ─────────────────────────────────────────────
st.set_page_config(
    page_title="音素回文発見プロジェクト｜探偵ナイトスクープ",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── カスタムCSS（白基調・スタイリッシュ）─────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Serif+JP:wght@400;500;700;900&family=Noto+Sans+JP:wght@300;400;500;700;900&family=Share+Tech+Mono&display=swap');

html, body, [class*="css"] {
    font-family: 'Noto Sans JP', sans-serif;
}

/* ── 全体背景：白基調 ── */
.stApp {
    background: #fafafa;
    color: #333;
}

/* ── サイドバー ── */
[data-testid="stSidebar"] {
    background: #ffffff !important;
    border-right: 1px solid #e0e0e0;
}
[data-testid="stSidebar"] * {
    color: #555 !important;
}

/* ── ヘッダーセクション ── */
header[data-testid="stHeader"] {
    background: transparent;
}

/* ── ナイトスクープ愛バナー（スターウォーズ風クロール） ── */
.knight-crawl-wrapper {
    background: linear-gradient(180deg, #000000 0%, #05051a 40%, #0a0a2e 100%);
    border-radius: 16px;
    height: 420px;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
    perspective: 300px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
}
/* 上部フェードアウト */
.knight-crawl-wrapper::after {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 100%;
    background: linear-gradient(
        180deg,
        rgba(0,0,0,0.9) 0%,
        transparent 30%,
        transparent 70%,
        rgba(0,0,0,0.95) 100%
    );
    pointer-events: none;
    z-index: 2;
}
.knight-crawl-container {
    position: absolute;
    top: 100%;
    left: 50%;
    transform: translateX(-50%);
    width: 80%;
    max-width: 600px;
    transform-origin: 50% 100%;
    animation: crawl 25s linear infinite;
}
@keyframes crawl {
    0% { top: 100%; }
    100% { top: -180%; }
}
.knight-crawl-title {
    font-family: 'Noto Serif JP', serif;
    font-size: 1.8rem;
    color: #ffd54f;
    letter-spacing: 0.2em;
    text-align: center;
    margin-bottom: 2rem;
    font-weight: 700;
    text-shadow: 0 0 20px rgba(255,213,79,0.4);
}
.knight-crawl-text {
    font-family: 'Noto Serif JP', serif;
    font-size: 1.05rem;
    color: #ffd54f;
    line-height: 2.2;
    text-align: justify;
    letter-spacing: 0.06em;
    font-weight: 500;
}
.knight-crawl-footer {
    font-family: 'Noto Serif JP', serif;
    font-size: 0.85rem;
    color: rgba(255,213,79,0.6);
    text-align: center;
    margin-top: 2.5rem;
    letter-spacing: 0.12em;
}
/* ── メインタイトル ── */
.main-title {
    font-family: 'Noto Serif JP', serif;
    font-size: 2rem;
    color: #1a237e;
    letter-spacing: 0.06em;
    margin-bottom: 0.1rem;
    font-weight: 700;
}
.sub-title {
    font-family: 'Noto Sans JP', sans-serif;
    font-size: 0.82rem;
    color: #999;
    letter-spacing: 0.08em;
    margin-bottom: 1.8rem;
    font-weight: 300;
}

/* ── 統計カード ── */
.stat-box {
    background: #ffffff;
    border: 1px solid #eee;
    border-radius: 12px;
    padding: 1.2rem 1rem;
    text-align: center;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    transition: transform 0.2s, box-shadow 0.2s;
}
.stat-box:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 16px rgba(0,0,0,0.08);
}
.stat-num {
    font-family: 'Share Tech Mono', monospace;
    font-size: 2rem;
    color: #1a237e;
    font-weight: 700;
}
.stat-label {
    font-size: 0.7rem;
    color: #999;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-top: 0.3rem;
}

/* ── セクション見出し ── */
.section-heading {
    font-family: 'Noto Sans JP', sans-serif;
    font-size: 1rem;
    color: #333;
    border-bottom: 2px solid #1a237e;
    padding-bottom: 0.4rem;
    margin: 1.5rem 0 1rem;
    letter-spacing: 0.06em;
    font-weight: 700;
}

/* ── 発見カード ── */
.hit-card {
    background: #ffffff;
    border: 1px solid #e8e8e8;
    border-left: 4px solid #e53935;
    border-radius: 10px;
    padding: 1.2rem 1.5rem;
    margin: 0.5rem 0;
    position: relative;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    cursor: pointer;
    transition: transform 0.2s, box-shadow 0.2s;
}
.hit-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(0,0,0,0.08);
}
.hit-badge {
    position: absolute;
    top: -10px;
    right: 12px;
    background: #e53935;
    color: white;
    font-size: 0.6rem;
    font-weight: 900;
    padding: 2px 10px;
    border-radius: 10px;
    letter-spacing: 0.1em;
}
.hit-word {
    font-family: 'Noto Serif JP', serif;
    font-size: 1.5rem;
    color: #1a237e;
    font-weight: bold;
    letter-spacing: 0.08em;
}
.hit-yomi {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.78rem;
    color: #888;
    margin-top: 0.2rem;
}
.phoneme-row {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.75rem;
    color: #43a047;
    margin-top: 0.4rem;
    letter-spacing: 0.05em;
}
.hit-meta {
    font-size: 0.7rem;
    color: #aaa;
    margin-top: 0.3rem;
}

/* ── 伝説カード ── */
.legendary-card {
    background: linear-gradient(135deg, #fff8e1 0%, #fff3c4 50%, #fffde7 100%);
    border: 2px solid #ff8f00;
    border-left: 6px solid #ff8f00;
    border-radius: 12px;
    padding: 1.8rem 2rem;
    margin: 1rem 0;
    position: relative;
    box-shadow: 0 4px 16px rgba(255,143,0,0.12);
}
.legendary-badge {
    position: absolute;
    top: -12px;
    right: 14px;
    background: linear-gradient(90deg, #ff8f00, #ffb300);
    color: #fff;
    font-size: 0.68rem;
    font-weight: 900;
    padding: 3px 12px;
    border-radius: 12px;
    letter-spacing: 0.12em;
}
.legendary-word {
    font-family: 'Noto Serif JP', serif;
    font-size: 2rem;
    color: #e65100;
    letter-spacing: 0.1em;
}

/* ── 選択ワード表示 ── */
.selected-word-box {
    background: #ffffff;
    border: 1px solid #e0e0e0;
    border-radius: 16px;
    padding: 2rem;
    text-align: center;
    margin-bottom: 1.5rem;
    box-shadow: 0 4px 16px rgba(0,0,0,0.05);
}
.selected-word-main {
    font-family: 'Noto Serif JP', serif;
    font-size: 2.8rem;
    letter-spacing: 0.12em;
    font-weight: 700;
}

/* ── 音素チップ ── */
.phoneme-viz {
    display: flex;
    justify-content: center;
    flex-wrap: wrap;
    gap: 6px;
    margin: 1rem 0;
}
.ph-chip {
    background: #e8f5e9;
    border: 1px solid #c8e6c9;
    border-radius: 6px;
    padding: 4px 12px;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.85rem;
    color: #2e7d32;
}
.ph-chip-rev {
    background: #fce4ec;
    border: 1px solid #f8bbd0;
    color: #c62828;
}

/* ── プレイヤーラベル ── */
.player-label-normal {
    font-size: 0.8rem;
    color: #1a237e;
    font-weight: 700;
    letter-spacing: 0.1em;
    margin-bottom: 0.5rem;
    text-align: center;
}
.player-label-reverse {
    font-size: 0.8rem;
    color: #e53935;
    font-weight: 700;
    letter-spacing: 0.1em;
    margin-bottom: 0.5rem;
    text-align: center;
}

/* ── ナイトスクープ風フッター ── */
.knight-footer {
    text-align: center;
    padding: 2rem 1rem;
    margin-top: 3rem;
    border-top: 1px solid #eee;
    color: #bbb;
    font-size: 0.75rem;
    letter-spacing: 0.08em;
}

/* ── ボタンスタイル ── */
.stButton > button {
    background: #ffffff;
    border: 1px solid #ddd;
    color: #1a237e;
    border-radius: 8px;
    font-size: 0.8rem;
    transition: all 0.2s;
}
.stButton > button:hover {
    background: #1a237e;
    color: #fff;
    border-color: #1a237e;
}

/* ── Streamlit要素の調整 ── */
.stTabs [data-baseweb="tab-list"] {
    gap: 0;
    background: #fff;
    border-radius: 12px;
    padding: 4px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px;
    color: #666;
    font-weight: 500;
    padding: 0.5rem 1.5rem;
}
.stTabs [aria-selected="true"] {
    background: #1a237e !important;
    color: #fff !important;
}
</style>
""", unsafe_allow_html=True)


# ── データ読み込み ─────────────────────────────────────────
@st.cache_data
def load_data():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    dfs = []

    for fname in [
        "knight_scoop_all_keywords_investigation.csv",
        "animals_palindrome_v4.csv",
        "inat_palindrome_v5.csv",
    ]:
        fpath = os.path.join(BASE_DIR, fname)
        try:
            df = pd.read_csv(fpath, encoding="utf-8-sig")
            if df.empty or not {"ワード", "回文判定"}.issubset(df.columns):
                continue
            dfs.append(df)
        except FileNotFoundError:
            continue
        except Exception as e:
            st.sidebar.warning(f"⚠ {fname}: {e}")
            continue

    if dfs:
        df_all = pd.concat(dfs, ignore_index=True).drop_duplicates(subset="ワード")
    else:
        df_all = pd.DataFrame(columns=["品詞", "品詞細分類", "ワード", "ヨミガナ", "音素", "回文判定"])

    legendary = [
        {
            "品詞": "特別枠",
            "品詞細分類": "伝説",
            "ワード": "オオエンマハンミョウ",
            "ヨミガナ": "オオエンマハンミョウ",
            "音素": "o o e m m a h a m m y o o",
            "回文判定": "〇",
        },
    ]
    existing = set(df_all["ワード"].tolist())
    new_rows = [lw for lw in legendary if lw["ワード"] not in existing]
    if new_rows:
        df_all = pd.concat([pd.DataFrame(new_rows), df_all], ignore_index=True)

    for col in ["品詞", "品詞細分類", "ワード", "ヨミガナ", "音素", "回文判定"]:
        if col not in df_all.columns:
            df_all[col] = ""

    return df_all


df_all = load_data()
df_hits = df_all[df_all["回文判定"] == "〇"].copy()
df_miss = df_all[df_all["回文判定"] != "〇"].copy()


# ── セッション状態の初期化 ──────────────────────────────────
if "selected_word_for_audio" not in st.session_state:
    st.session_state.selected_word_for_audio = None
if "active_tab" not in st.session_state:
    st.session_state.active_tab = None
if "show_message" not in st.session_state:
    st.session_state.show_message = True


# ── ナイトスクープ愛バナー ──────────────────────────────────
if st.session_state.show_message:
    st.markdown("""
    <div class="knight-crawl-wrapper">
        <div class="knight-crawl-container">
            <div class="knight-crawl-title">
                探偵ナイトスクープ様へ
            </div>
            <div class="knight-crawl-text">
                毎週、家族そろってTVerで観るのが我が家の楽しみでした。
                いつか何かの形で、この大好きな番組に関われたら──
                そんな夢をずっと抱いていました。<br><br>
                「逆から読んでも"オオエンマハンミョウ"」の回を観たとき、
                心の底から感動しました。<br><br>
                「これならば、自分のプログラミングの経験が役に立てる」と確信し、
                AIとプログラミングを駆使して、
                日本語31万語以上の音素解析に挑みました。<br><br>
                結果、351個の音素回文を発見。<br><br>
                この成果を、番組への感謝と愛を込めてお届けします。
            </div>
            <div class="knight-crawl-footer">
                ── 探偵ナイトスクープを愛する一視聴者・一エンジニアより ──
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("閉じる", key="close_msg"):
        st.session_state.show_message = False
        st.rerun()
else:
    if st.button("メッセージを読む", key="open_msg"):
        st.session_state.show_message = True
        st.rerun()


# ── ヘッダー ──────────────────────────────────────────────
st.markdown('<div class="main-title">音素回文発見プロジェクト</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Phonemic Palindrome Discovery System</div>', unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f'<div class="stat-box"><div class="stat-num">{len(df_all):,}</div><div class="stat-label">総調査ワード</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="stat-box"><div class="stat-num" style="color:#e53935">{len(df_hits):,}</div><div class="stat-label">回文ヒット</div></div>', unsafe_allow_html=True)
with c3:
    rate = len(df_hits) / len(df_all) * 100 if len(df_all) > 0 else 0
    st.markdown(f'<div class="stat-box"><div class="stat-num">{rate:.2f}%</div><div class="stat-label">ヒット率</div></div>', unsafe_allow_html=True)
with c4:
    cats = df_hits["品詞"].nunique()
    st.markdown(f'<div class="stat-box"><div class="stat-num">{cats}</div><div class="stat-label">カテゴリ数</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# ── サイドバー ────────────────────────────────────────────
st.sidebar.markdown("### 絞り込みフィルター")

st.sidebar.markdown("**回文判定**")
判定フィルター = st.sidebar.radio(
    label="判定",
    options=["発見ワードのみ（〇）", "全件表示", "未該当のみ（×）"],
    index=0,
    label_visibility="collapsed",
)

st.sidebar.markdown("---")

if 判定フィルター == "発見ワードのみ（〇）":
    df_target = df_hits.copy()
elif 判定フィルター == "未該当のみ（×）":
    df_target = df_miss.copy()
else:
    df_target = df_all.copy()

st.sidebar.markdown("**品詞カテゴリ**")
all_pos = sorted(df_target["品詞"].dropna().unique().tolist())
if "特別枠" in all_pos:
    all_pos = ["特別枠"] + [p for p in all_pos if p != "特別枠"]
selected_pos = st.sidebar.selectbox("品詞", ["すべて"] + all_pos)

if selected_pos != "すべて":
    df_target = df_target[df_target["品詞"] == selected_pos]

all_sub = sorted(df_target["品詞細分類"].dropna().unique().tolist())
selected_sub = st.sidebar.selectbox("品詞細分類", ["すべて"] + all_sub)

if selected_sub != "すべて":
    df_target = df_target[df_target["品詞細分類"] == selected_sub]

st.sidebar.markdown("---")

st.sidebar.markdown("**回文ヒット内訳**")
if len(df_hits) > 0:
    hit_by_pos = df_hits.groupby("品詞").size().sort_values(ascending=False)
    for pos, cnt in hit_by_pos.items():
        st.sidebar.markdown(
            f'<span style="font-size:0.75rem;color:#666">'
            f'{str(pos)[:8]}&nbsp;&nbsp;'
            f'<span style="color:#e53935;font-family:monospace;font-weight:700">{cnt}件</span>'
            f'</span>',
            unsafe_allow_html=True,
        )

st.sidebar.markdown("---")
st.sidebar.markdown(
    f'<span style="font-size:0.75rem;color:#999">表示中: {len(df_target):,} 件</span>',
    unsafe_allow_html=True,
)


# ── 音声生成 ──────────────────────────────────────────────
@st.cache_data
def generate_audio(word):
    tts = gTTS(text=word, lang="ja")
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


# ── タブ ─────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["🎧 音声検証", "🎉 発見ワード一覧", "📋 全データ"])


# ═══════════════════════════════════════════════════════════
# Tab1: 音声検証
# ═══════════════════════════════════════════════════════════
with tab1:
    col_left, col_right = st.columns([1, 1.5])

    with col_left:
        st.markdown('<div class="section-heading">ワードを選択</div>', unsafe_allow_html=True)

        word_options = df_target["ワード"].tolist()
        if not word_options:
            st.warning("条件に合うワードがありません")
            st.stop()

        # 他タブからの選択があればそれを初期値にする
        default_index = 0
        if st.session_state.selected_word_for_audio and st.session_state.selected_word_for_audio in word_options:
            default_index = word_options.index(st.session_state.selected_word_for_audio)

        selected_word = st.selectbox(
            "聴きたいワードを選択",
            word_options,
            index=default_index,
            label_visibility="collapsed",
        )

        row = df_target[df_target["ワード"] == selected_word].iloc[0]
        is_hit = row["回文判定"] == "〇"
        is_legendary = str(row.get("品詞細分類", "")) == "伝説"

        phonemes = str(row.get("音素", "")).split()
        phonemes_rev = phonemes[::-1]

        # ワード大表示
        if is_legendary:
            badge = '<span style="background:linear-gradient(90deg,#ff8f00,#ffb300);color:#fff;font-size:0.65rem;padding:2px 10px;border-radius:10px;font-weight:900">👑 伝説のワード</span>'
            word_color = "#e65100"
        elif is_hit:
            badge = '<span style="background:#e53935;color:white;font-size:0.65rem;padding:2px 8px;border-radius:10px;font-weight:900">発見ワード</span>'
            word_color = "#1a237e"
        else:
            badge = ""
            word_color = "#555"

        st.markdown(f"""
        <div class="selected-word-box">
            {badge}
            <div class="selected-word-main" style="color:{word_color}">{selected_word}</div>
            <div style="font-size:0.85rem;color:#999;margin-top:0.3rem">
                {row.get('品詞', '')} / {row.get('品詞細分類', '')}
            </div>
            <div style="font-family:'Share Tech Mono',monospace;font-size:0.88rem;color:#43a047;margin-top:0.5rem">
                [ {" · ".join(phonemes)} ]
            </div>
        </div>
        """, unsafe_allow_html=True)

        # 音素ビジュアライザー
        st.markdown('<div class="section-heading">音素の順方向 vs 逆方向</div>', unsafe_allow_html=True)
        fwd_html = "".join([f'<span class="ph-chip">{p}</span>' for p in phonemes])
        rev_html = "".join([f'<span class="ph-chip ph-chip-rev">{p}</span>' for p in phonemes_rev])
        st.markdown(f'<div class="phoneme-viz">{fwd_html}</div>', unsafe_allow_html=True)
        st.markdown('<div style="text-align:center;color:#999;font-size:0.8rem;margin:0.3rem 0">▼ 逆再生</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="phoneme-viz">{rev_html}</div>', unsafe_allow_html=True)

        if is_hit and phonemes:
            st.markdown('<div class="section-heading">マッチング詳細</div>', unsafe_allow_html=True)
            for f, r in zip(phonemes, phonemes_rev):
                if f == r:
                    st.markdown(f"✅ `{f}` = `{r}`")
                elif {f, r} in [{"e", "y"}, {"o", "u"}]:
                    st.markdown(f"🔁 `{f}` ≈ `{r}` （類似音）")

    with col_right:
        st.markdown('<div class="section-heading">音声再生</div>', unsafe_allow_html=True)

        with st.spinner("音声を生成中..."):
            normal_bytes, reverse_bytes = generate_audio(selected_word)

        a1, a2 = st.columns(2)
        with a1:
            st.markdown('<div class="player-label-normal">▶ 通常再生</div>', unsafe_allow_html=True)
            st.audio(normal_bytes, format="audio/mp3")
        with a2:
            st.markdown('<div class="player-label-reverse">◀ 逆再生（検証）</div>', unsafe_allow_html=True)
            st.audio(reverse_bytes, format="audio/mp3")

        if is_legendary:
            st.markdown("""
            <div style="background:linear-gradient(135deg,#fff8e1,#fff3c4);
                        border:2px solid #ff8f00;border-radius:16px;
                        padding:1.5rem;margin-top:1rem;text-align:center;
                        box-shadow:0 4px 16px rgba(255,143,0,0.1)">
                <div style="font-size:2.5rem">👑</div>
                <div style="font-family:'Zen Antique Soft',serif;font-size:1.4rem;
                            color:#e65100;margin:0.3rem 0">
                    伝説のワード
                </div>
                <div style="font-size:0.85rem;color:#bf360c;margin-top:0.5rem">
                    探偵ナイトスクープが発見した原点にして頂点
                </div>
            </div>
            """, unsafe_allow_html=True)
        elif is_hit:
            st.markdown("""
            <div style="background:#fff;border:1px solid #e53935;border-radius:12px;
                        padding:1.2rem;margin-top:1rem;text-align:center;
                        box-shadow:0 2px 8px rgba(229,57,53,0.08)">
                <div style="font-size:1.2rem;color:#e53935;font-weight:700;margin:0.3rem 0">
                    音素回文 確認済み
                </div>
                <div style="font-size:0.8rem;color:#888">
                    このワードは逆再生しても同じ音に聞こえます
                </div>
            </div>
            """, unsafe_allow_html=True)

        # 「オオエンマハンミョウ」ストーリーセクション
        st.markdown('<div class="section-heading">このプロジェクトについて</div>', unsafe_allow_html=True)
        st.markdown("""
        <div style="background:#fff;border:1px solid #eee;border-radius:12px;padding:1.5rem;
                    box-shadow:0 2px 8px rgba(0,0,0,0.03);line-height:1.8;font-size:0.88rem;color:#555">
            <strong style="color:#1a237e">音素回文</strong>とは、音の最小単位（音素）に分解したとき、
            前から読んでも後ろから読んでも同じ配列になる言葉です。<br><br>
            探偵ナイトスクープで紹介された<strong style="color:#e65100">「オオエンマハンミョウ」</strong>は、
            音素に分解すると <code style="background:#e8f5e9;padding:2px 6px;border-radius:4px;color:#2e7d32">
            o o e m m a h a m m y o o</code> となり、
            逆から読んでも同じ配列になります。<br><br>
            毎週TVerで家族そろって番組を観ていた制作者が、この回に心を打たれ、
            <strong style="color:#1a237e">「自分のプログラミング経験で貢献できる」</strong>と確信。
            AIとプログラミングを駆使し、日本語辞書データ<strong>31万語以上</strong>を
            音素解析して網羅的に探索した結果、<strong style="color:#e53935">351個</strong>の
            音素回文を発見しました。
        </div>
        """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════
# Tab2: 発見ワード一覧
# ═══════════════════════════════════════════════════════════
with tab2:
    st.markdown(
        f'<div class="section-heading">発見ワード一覧（{len(df_hits)} 件）</div>',
        unsafe_allow_html=True,
    )
    st.caption("ワードをクリックすると「音声検証」タブで再生できます")

    if len(df_hits) == 0:
        st.info("CSVファイルを配置するとここにワードが表示されます")
    else:
        # 伝説のワードを最上部に単独表示
        df_legendary = df_hits[df_hits["品詞細分類"] == "伝説"]
        df_normal_hits = df_hits[df_hits["品詞細分類"] != "伝説"]

        if not df_legendary.empty:
            st.markdown('<div class="section-heading">👑 伝説のワード</div>', unsafe_allow_html=True)
            for _, lrow in df_legendary.iterrows():
                st.markdown(f"""
                <div class="legendary-card">
                    <span class="legendary-badge">👑 伝説</span>
                    <div class="legendary-word">{lrow['ワード']}</div>
                    <div style="font-family:'Share Tech Mono',monospace;font-size:0.85rem;
                                color:#bf360c;margin-top:0.4rem">
                        [ {lrow.get('音素', '')} ]
                    </div>
                    <div style="font-size:0.75rem;color:#999;margin-top:0.3rem">
                        探偵ナイトスクープが世に知らしめた音素回文の原点
                    </div>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"🎧 {lrow['ワード']} を音声検証", key=f"legend_{lrow['ワード']}"):
                    st.session_state.selected_word_for_audio = lrow['ワード']
                    st.rerun()

        # 通常ヒットをカテゴリ別に表示
        for pos in sorted(df_normal_hits["品詞"].unique().tolist()):
            df_pos = df_normal_hits[df_normal_hits["品詞"] == pos]
            st.markdown(
                f'<div class="section-heading">■ {pos}（{len(df_pos)}件）</div>',
                unsafe_allow_html=True,
            )
            cols = st.columns(3)
            for idx, (_, hrow) in enumerate(df_pos.iterrows()):
                with cols[idx % 3]:
                    st.markdown(f"""
                    <div class="hit-card">
                        <span class="hit-badge">発見</span>
                        <div class="hit-word">{hrow['ワード']}</div>
                        <div class="hit-yomi">{hrow.get('ヨミガナ', '')}</div>
                        <div class="phoneme-row">[ {hrow.get('音素', '')} ]</div>
                        <div class="hit-meta">{hrow.get('品詞細分類', '')}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button(f"🎧 聴く", key=f"listen_{hrow['ワード']}"):
                        st.session_state.selected_word_for_audio = hrow['ワード']
                        st.rerun()


# ═══════════════════════════════════════════════════════════
# Tab3: 全データ
# ═══════════════════════════════════════════════════════════
with tab3:
    st.markdown(
        f'<div class="section-heading">全データ（{len(df_target):,} 件）</div>',
        unsafe_allow_html=True,
    )

    search = st.text_input(
        "ワード検索",
        placeholder="キーワードを入力...",
        label_visibility="collapsed",
    )
    if search:
        df_target = df_target[df_target["ワード"].str.contains(search, na=False)]

    def highlight_hits(row):
        if str(row.get("品詞細分類", "")) == "伝説":
            return ["background-color:#fff8e1;color:#e65100;font-weight:bold"] * len(row)
        if row.get("回文判定") == "〇":
            return ["background-color:#fce4ec;color:#c62828;font-weight:bold"] * len(row)
        return [""] * len(row)

    st.dataframe(
        df_target[["品詞", "品詞細分類", "ワード", "ヨミガナ", "音素", "回文判定"]]
        .style.apply(highlight_hits, axis=1),
        use_container_width=True,
        height=600,
    )


# ── フッター ─────────────────────────────────────────────
st.markdown("""
<div class="knight-footer">
    毎週TVerで家族そろって観ていた探偵ナイトスクープ。<br>
    「オオエンマハンミョウ」の回に感動し、AIとプログラミングで31万語を調査しました。<br>
    いつか番組に関わりたいという夢が、このプロジェクトの原動力です。<br><br>
    <span style="color:#1a237e;font-weight:500">探偵ナイトスクープ様、家族の笑顔をいつもありがとうございます。</span>
</div>
""", unsafe_allow_html=True)

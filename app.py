import streamlit as st
import pandas as pd
from gtts import gTTS
from pydub import AudioSegment
import io

# ── ページ設定 ─────────────────────────────────────────────
st.set_page_config(
    page_title="逆再生ワード発見器",
    page_icon="🔄",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── カスタムCSS（探偵ノワール × サイエンス風） ────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Zen+Antique+Soft&family=Share+Tech+Mono&family=Noto+Sans+JP:wght@400;700;900&display=swap');

/* ── ベース ── */
html, body, [class*="css"] {
    font-family: 'Noto Sans JP', sans-serif;
}
.stApp {
    background: #0a0a12;
    color: #e8e4d9;
}

/* ── サイドバー ── */
[data-testid="stSidebar"] {
    background: #0f0f1e !important;
    border-right: 1px solid #2a2a4a;
}
[data-testid="stSidebar"] * {
    color: #c8c4b8 !important;
}

/* ── タイトル ── */
.main-title {
    font-family: 'Zen Antique Soft', serif;
    font-size: 2.4rem;
    color: #f0e68c;
    text-shadow: 0 0 30px rgba(240,230,140,0.4);
    letter-spacing: 0.05em;
    margin-bottom: 0.2rem;
}
.sub-title {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.85rem;
    color: #6a7a9a;
    letter-spacing: 0.1em;
    margin-bottom: 2rem;
}

/* ── 発見カード（〇ヒット） ── */
.hit-card {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    border: 1px solid #e94560;
    border-left: 4px solid #e94560;
    border-radius: 8px;
    padding: 1.2rem 1.5rem;
    margin: 0.5rem 0;
    position: relative;
    cursor: pointer;
    transition: all 0.2s;
}
.hit-card:hover {
    border-color: #ff6b6b;
    box-shadow: 0 0 20px rgba(233,69,96,0.3);
    transform: translateX(4px);
}
.hit-badge {
    position: absolute;
    top: -10px;
    right: 12px;
    background: #e94560;
    color: white;
    font-size: 0.65rem;
    font-weight: 900;
    padding: 2px 8px;
    border-radius: 10px;
    letter-spacing: 0.1em;
}
.hit-word {
    font-family: 'Zen Antique Soft', serif;
    font-size: 1.6rem;
    color: #f0e68c;
    font-weight: bold;
    letter-spacing: 0.08em;
}
.hit-yomi {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.8rem;
    color: #a0b0c0;
    margin-top: 0.2rem;
}
.phoneme-row {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.78rem;
    color: #4ecdc4;
    margin-top: 0.4rem;
    letter-spacing: 0.05em;
}
.hit-meta {
    font-size: 0.72rem;
    color: #6a7a8a;
    margin-top: 0.3rem;
}

/* ── 選択中ワードの大表示 ── */
.selected-word-box {
    background: linear-gradient(180deg, #1e1e3a 0%, #12122a 100%);
    border: 1px solid #3a3a6a;
    border-radius: 12px;
    padding: 2rem;
    text-align: center;
    margin-bottom: 1.5rem;
}
.selected-word-main {
    font-family: 'Zen Antique Soft', serif;
    font-size: 3rem;
    color: #f0e68c;
    text-shadow: 0 0 40px rgba(240,230,140,0.5);
    letter-spacing: 0.12em;
}
.selected-phoneme {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.9rem;
    color: #4ecdc4;
    margin-top: 0.5rem;
    letter-spacing: 0.08em;
}

/* ── 音素ビジュアライザー ── */
.phoneme-viz {
    display: flex;
    justify-content: center;
    flex-wrap: wrap;
    gap: 6px;
    margin: 1rem 0;
}
.ph-chip {
    background: #1e3a4a;
    border: 1px solid #2a5a7a;
    border-radius: 4px;
    padding: 4px 10px;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.85rem;
    color: #4ecdc4;
}
.ph-chip-rev {
    background: #3a1e2e;
    border: 1px solid #7a2a4a;
    color: #ff6b9d;
}

/* ── 統計バー ── */
.stat-box {
    background: #12122a;
    border: 1px solid #2a2a4a;
    border-radius: 8px;
    padding: 1rem;
    text-align: center;
}
.stat-num {
    font-family: 'Share Tech Mono', monospace;
    font-size: 2rem;
    color: #f0e68c;
}
.stat-label {
    font-size: 0.72rem;
    color: #6a7a8a;
    letter-spacing: 0.1em;
    text-transform: uppercase;
}

/* ── セクション見出し ── */
.section-heading {
    font-family: 'Zen Antique Soft', serif;
    font-size: 1.1rem;
    color: #a0b0d0;
    border-bottom: 1px solid #2a2a4a;
    padding-bottom: 0.4rem;
    margin: 1.5rem 0 1rem;
    letter-spacing: 0.08em;
}

/* ── プレイヤーエリア ── */
.player-box {
    background: #0f1520;
    border: 1px solid #2a3a5a;
    border-radius: 10px;
    padding: 1.2rem;
    text-align: center;
}
.player-label-normal {
    font-size: 0.8rem;
    color: #4ecdc4;
    font-weight: bold;
    letter-spacing: 0.1em;
    margin-bottom: 0.5rem;
}
.player-label-reverse {
    font-size: 0.8rem;
    color: #ff6b9d;
    font-weight: bold;
    letter-spacing: 0.1em;
    margin-bottom: 0.5rem;
}
audio { width: 100%; }

/* ── streamlit デフォルト上書き ── */
.stSelectbox label, .stRadio label {
    color: #a0b0c0 !important;
}
div[data-testid="stMetricValue"] {
    color: #f0e68c !important;
}
.stDataFrame {
    background: #0f0f1e;
}
</style>
""", unsafe_allow_html=True)


# ── データ読み込み ─────────────────────────────────────────
@st.cache_data
def load_data():
    dfs = []

    for fname in [
        "knight_scoop_all_keywords_investigation.csv",
        "animals_palindrome_v4.csv",
        "inat_palindrome_v5.csv",
    ]:
        try:
            df = pd.read_csv(fname)
            # ── ★ 空ファイル・必要カラム不足を弾く ──
            if df.empty:
                continue
            required = {"ワード", "回文判定"}
            if not required.issubset(df.columns):
                continue
            dfs.append(df)
        except (FileNotFoundError, pd.errors.EmptyDataError, pd.errors.ParserError):
            # ファイルなし・空・壊れている → スキップ
            continue
        except Exception as e:
            st.sidebar.warning(f"⚠️ {fname} 読み込みスキップ: {e}")
            continue

    if dfs:
        df_all = pd.concat(dfs, ignore_index=True).drop_duplicates(subset="ワード")
    else:
        # ── ★ CSV が1件もなくても落ちない空DataFrame ──
        df_all = pd.DataFrame(columns=["品詞","品詞細分類","ワード","ヨミガナ","音素","回文判定"])

    # 手動追加（伝説のワード）
    legendary = [
        {"品詞":"特別枠","品詞細分類":"伝説","ワード":"オオエンマハンミョウ",
         "ヨミガナ":"オオエンマハンミョウ","音素":"o o e m m a h a m m y o o","回文判定":"〇"},
    ]
    existing = set(df_all["ワード"].tolist())
    new_rows = [lw for lw in legendary if lw["ワード"] not in existing]
    if new_rows:
        df_all = pd.concat([pd.DataFrame(new_rows), df_all], ignore_index=True)

    # ── ★ 必須カラムが欠けている場合も補完 ──
    for col in ["品詞","品詞細分類","ワード","ヨミガナ","音素","回文判定"]:
        if col not in df_all.columns:
            df_all[col] = ""

    return df_all

df_all = load_data()
df_hits = df_all[df_all["回文判定"] == "〇"].copy()
df_miss = df_all[df_all["回文判定"] != "〇"].copy()


# ── ヘッダー ──────────────────────────────────────────────
st.markdown('<div class="main-title">🔄 逆再生ワード発見器</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">探偵ナイトスクープ提出用 ／ 音素回文調査システム</div>', unsafe_allow_html=True)

# 統計表示
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f'<div class="stat-box"><div class="stat-num">{len(df_all):,}</div><div class="stat-label">総調査ワード</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="stat-box"><div class="stat-num" style="color:#e94560">{len(df_hits):,}</div><div class="stat-label">🎉 回文ヒット</div></div>', unsafe_allow_html=True)
with c3:
    rate = len(df_hits)/len(df_all)*100 if len(df_all) > 0 else 0
    st.markdown(f'<div class="stat-box"><div class="stat-num">{rate:.2f}%</div><div class="stat-label">ヒット率</div></div>', unsafe_allow_html=True)
with c4:
    cats = df_hits["品詞"].nunique()
    st.markdown(f'<div class="stat-box"><div class="stat-num">{cats}</div><div class="stat-label">カテゴリ数</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# ── サイドバー ────────────────────────────────────────────
st.sidebar.markdown("### 🔍 絞り込みフィルター")

# ★ 回文判定フィルター（新規追加）
st.sidebar.markdown("**回文判定**")
判定フィルター = st.sidebar.radio(
    label="判定",
    options=["🎉 発見ワードのみ（〇）", "📋 全件表示", "❌ 未該当のみ（×）"],
    index=0,
    label_visibility="collapsed",
)

st.sidebar.markdown("---")

# 品詞カテゴリフィルター
st.sidebar.markdown("**品詞カテゴリ**")

# 対象データを判定フィルターで決定
if 判定フィルター == "🎉 発見ワードのみ（〇）":
    df_target = df_hits.copy()
elif 判定フィルター == "❌ 未該当のみ（×）":
    df_target = df_miss.copy()
else:
    df_target = df_all.copy()

all_pos = sorted(df_target["品詞"].dropna().unique().tolist())
selected_pos = st.sidebar.selectbox("品詞", ["すべて"] + all_pos)

if selected_pos != "すべて":
    df_target = df_target[df_target["品詞"] == selected_pos]

# 品詞細分類フィルター
all_sub = sorted(df_target["品詞細分類"].dropna().unique().tolist())
selected_sub = st.sidebar.selectbox("品詞細分類", ["すべて"] + all_sub)

if selected_sub != "すべて":
    df_target = df_target[df_target["品詞細分類"] == selected_sub]

st.sidebar.markdown("---")

# ★ 回文カテゴリ内訳（新規追加）
st.sidebar.markdown("**📊 回文ヒット内訳**")
if len(df_hits) > 0:
    hit_by_pos = df_hits.groupby("品詞").size().sort_values(ascending=False)
    for pos, cnt in hit_by_pos.items():
        pct = cnt / len(df_hits) * 100
        bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
        st.sidebar.markdown(
            f'<span style="font-size:0.75rem;color:#a0b0c0">'
            f'{pos[:6]:<6} <span style="color:#e94560;font-family:monospace">{cnt:>4}件</span>'
            f'</span>',
            unsafe_allow_html=True
        )

st.sidebar.markdown("---")
st.sidebar.markdown(f'<span style="font-size:0.75rem;color:#6a7a8a">表示中: {len(df_target):,} 件</span>', unsafe_allow_html=True)


# ── メインコンテンツ（タブ） ──────────────────────────────
tab1, tab2, tab3 = st.tabs(["🎧 音声検証", "🎉 発見ワード一覧", "📋 全データ"])


# ── Tab1: 音声検証 ────────────────────────────────────────
with tab1:
    col_left, col_right = st.columns([1, 1.5])

    with col_left:
        st.markdown('<div class="section-heading">ワードを選択</div>', unsafe_allow_html=True)

        # 発見ワード優先で選択肢を並べる
        word_options = df_target["ワード"].tolist()
        if not word_options:
            st.warning("条件に合うワードがありません")
            st.stop()

        selected_word = st.selectbox(
            "聴きたいワードを選択",
            word_options,
            label_visibility="collapsed",
        )

        # 選択ワード情報
        row = df_target[df_target["ワード"] == selected_word].iloc[0]
        is_hit = row["回文判定"] == "〇"

        phonemes = str(row.get("音素","")).split()
        phonemes_rev = phonemes[::-1]

        # ワード大表示
        badge = '<span style="background:#e94560;color:white;font-size:0.65rem;padding:2px 8px;border-radius:10px;font-weight:900">🎉 発見ワード!!</span>' if is_hit else ""
        st.markdown(f"""
        <div class="selected-word-box">
            {badge}
            <div class="selected-word-main">{selected_word}</div>
            <div style="font-size:0.85rem;color:#6a7a9a;margin-top:0.3rem">
                {row.get('品詞','')} / {row.get('品詞細分類','')}
            </div>
            <div class="selected-phoneme">[ {" · ".join(phonemes)} ]</div>
        </div>
        """, unsafe_allow_html=True)

        # 音素ビジュアライザー（順・逆）
        st.markdown('<div class="section-heading">音素の順方向 vs 逆方向</div>', unsafe_allow_html=True)
        fwd_html = "".join([f'<span class="ph-chip">{p}</span>' for p in phonemes])
        rev_html = "".join([f'<span class="ph-chip ph-chip-rev">{p}</span>' for p in phonemes_rev])
        st.markdown(f'<div class="phoneme-viz">{fwd_html}</div>', unsafe_allow_html=True)
        st.markdown('<div style="text-align:center;color:#6a7a8a;font-size:0.8rem">▼ 逆再生</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="phoneme-viz">{rev_html}</div>', unsafe_allow_html=True)

        if is_hit:
            match_info = []
            for f, r in zip(phonemes, phonemes_rev):
                if f == r:
                    match_info.append(f"✅ `{f}` = `{r}`")
                elif {f,r} in [{'e','y'},{'o','u'}]:
                    match_info.append(f"🔁 `{f}` ≈ `{r}` (類似音)")
            st.markdown("**マッチング詳細**")
            for m in match_info:
                st.markdown(m)

    with col_right:
        st.markdown('<div class="section-heading">音声再生</div>', unsafe_allow_html=True)

        @st.cache_data
        def generate_audio(word):
            tts = gTTS(text=word, lang='ja')
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

        with st.spinner("音声生成中..."):
            normal_bytes, reverse_bytes = generate_audio(selected_word)

        a1, a2 = st.columns(2)
        with a1:
            st.markdown('<div class="player-box"><div class="player-label-normal">▶ 通常再生</div></div>', unsafe_allow_html=True)
            st.audio(normal_bytes, format="audio/mp3")
        with a2:
            st.markdown('<div class="player-box"><div class="player-label-reverse">◀ 逆再生（検証）</div></div>', unsafe_allow_html=True)
            st.audio(reverse_bytes, format="audio/mp3")

        if is_hit:
            st.markdown("""
            <div style="background:linear-gradient(135deg,#1a0a12,#2a0a1e);
                        border:1px solid #e94560;border-radius:10px;
                        padding:1.2rem;margin-top:1rem;text-align:center;">
                <div style="font-size:1.8rem">🎉</div>
                <div style="font-family:'Zen Antique Soft',serif;font-size:1.2rem;
                            color:#f0e68c;margin:0.3rem 0">発見ワード確定！！</div>
                <div style="font-size:0.8rem;color:#a0b0c0">
                    このワードは逆再生しても同じ音に聞こえます
                </div>
            </div>
            """, unsafe_allow_html=True)


# ── Tab2: 発見ワード一覧 ──────────────────────────────────
with tab2:
    st.markdown(f'<div class="section-heading">🎉 発見ワード一覧（{len(df_hits)} 件）</div>', unsafe_allow_html=True)

    if len(df_hits) == 0:
        st.info("CSVファイルを配置するとここにワードが表示されます")
    else:
        # カテゴリ別グルーピング表示
        pos_list = df_hits["品詞"].unique().tolist()
        # 特別枠を先頭に
        if "特別枠" in pos_list:
            pos_list = ["特別枠"] + [p for p in pos_list if p != "特別枠"]

        for pos in pos_list:
            df_pos = df_hits[df_hits["品詞"] == pos]
            st.markdown(f'<div class="section-heading">■ {pos}（{len(df_pos)}件）</div>', unsafe_allow_html=True)

            cols = st.columns(3)
            for idx, (_, row) in enumerate(df_pos.iterrows()):
                with cols[idx % 3]:
                    phoneme_str = str(row.get("音素",""))
                    st.markdown(f"""
                    <div class="hit-card">
                        <span class="hit-badge">発見!!</span>
                        <div class="hit-word">{row['ワード']}</div>
                        <div class="hit-yomi">{row.get('ヨミガナ', '')}</div>
                        <div class="phoneme-row">[ {phoneme_str} ]</div>
                        <div class="hit-meta">{row.get('品詞細分類','')}</div>
                    </div>
                    """, unsafe_allow_html=True)


# ── Tab3: 全データ ────────────────────────────────────────
with tab3:
    st.markdown(f'<div class="section-heading">📋 全データ（{len(df_target):,} 件）</div>', unsafe_allow_html=True)

    # 検索
    search = st.text_input("🔍 ワード検索", placeholder="キーワードを入力...", label_visibility="collapsed")
    if search:
        df_target = df_target[df_target["ワード"].str.contains(search, na=False)]

    # 〇を強調したスタイル付きDataFrame表示
    def highlight_hits(row):
        if row.get("回文判定") == "〇":
            return ["background-color: #1a0a18; color: #f0e68c; font-weight: bold"] * len(row)
        return [""] * len(row)

    st.dataframe(
        df_target[["品詞","品詞細分類","ワード","ヨミガナ","音素","回文判定"]]
        .style.apply(highlight_hits, axis=1),
        use_container_width=True,
        height=600,
    )

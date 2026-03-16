import os
import base64
import streamlit as st
import streamlit.components.v1 as components
from data_logic import (
    load_data,
    prepare_datasets,
    generate_audio_bytes,
    validate_free_input,
    filter_hits_only,
    paginate,
    to_katakana,
    FREE_INPUT_MAX_LENGTH,
    ITEMS_PER_PAGE,
)

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
/* サイドバー開閉ボタンを見えるように */
[data-testid="collapsedControl"] button {
    color: #1a237e !important;
    background: #fff !important;
    border: 1px solid #ddd !important;
    border-radius: 8px !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1) !important;
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

/* ── 固定プレイヤーバー ── */
.fixed-player-bar {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background: #fff;
    border-top: 2px solid #1a237e;
    padding: 0.8rem 2rem;
    z-index: 9999;
    box-shadow: 0 -4px 16px rgba(0,0,0,0.1);
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 1.5rem;
}
.fixed-player-word {
    font-family: 'Noto Serif JP', serif;
    font-size: 1.1rem;
    color: #1a237e;
    font-weight: 700;
}
.fixed-player-mode {
    font-size: 0.75rem;
    color: #888;
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

/* ── ラジオボタン（カテゴリフィルター）文字色修正 ── */
[data-testid="stRadio"] label {
    color: #333 !important;
}
[data-testid="stRadio"] [data-baseweb="radio"] {
    color: #333 !important;
}
[data-testid="stRadio"] p {
    color: #333 !important;
}
</style>
""", unsafe_allow_html=True)


# ── データ読み込み ─────────────────────────────────────────
@st.cache_data
def _load_all():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    df, errors = load_data(base_dir)
    df_all, df_hits, df_hits_green, df_hits_yellow, df_miss, df_needs_review = prepare_datasets(df)
    return df_all, df_hits, df_hits_green, df_hits_yellow, df_miss, df_needs_review, errors

df_all, df_hits, df_hits_green, df_hits_yellow, df_miss, df_needs_review, _load_errors = _load_all()
for fname, err in _load_errors:
    st.sidebar.warning(f"⚠ {fname}: {err}")


# ── セッション状態の初期化 ──────────────────────────────────
if "selected_word_for_audio" not in st.session_state:
    st.session_state.selected_word_for_audio = None
if "show_message" not in st.session_state:
    st.session_state.show_message = True
if "play_word" not in st.session_state:
    st.session_state.play_word = None
if "play_reading" not in st.session_state:
    st.session_state.play_reading = None
if "play_mode" not in st.session_state:
    st.session_state.play_mode = None
if "play_count" not in st.session_state:
    st.session_state.play_count = 0


# ── ナイトスクープ愛バナー ──────────────────────────────────
if st.session_state.show_message:
    st.markdown(f"""
    <div class="knight-crawl-wrapper">
        <div class="knight-crawl-container">
            <div class="knight-crawl-title">
                探偵ナイトスクープ様へ
            </div>
            <div class="knight-crawl-text">
                毎週の放送を、家族そろって観るのが我が家の楽しみでした。
                いつか何かの形で、この大好きな番組に関われたら──
                そんな夢をずっと抱いていました。<br><br>
                「逆から読んでも"オオエンマハンミョウ"」の回を観たとき、
                心の底から感動しました。<br><br>
                「これならば、自分のプログラミングの経験が役に立てる」と確信し、
                AIとプログラミングを駆使して、
                日本語{len(df_all):,}語の音素解析に挑みました。<br><br>
                結果、{len(df_hits):,}個の音素回文を発見。<br><br>
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

c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    st.markdown(f'<div class="stat-box"><div class="stat-num">{len(df_all):,}</div><div class="stat-label">総調査ワード</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="stat-box"><div class="stat-num" style="color:#2e7d32">{len(df_hits_green):,}</div><div class="stat-label">🟢 新発見ワード</div></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="stat-box"><div class="stat-num" style="color:#f9a825">{len(df_hits_yellow):,}</div><div class="stat-label">🟡 参考ワード</div></div>', unsafe_allow_html=True)
with c4:
    st.markdown(f'<div class="stat-box"><div class="stat-num" style="color:#e53935">{len(df_hits):,}</div><div class="stat-label">回文ヒット合計</div></div>', unsafe_allow_html=True)
with c5:
    rate = len(df_hits) / len(df_all) * 100 if len(df_all) > 0 else 0
    st.markdown(f'<div class="stat-box"><div class="stat-num">{rate:.2f}%</div><div class="stat-label">ヒット率</div></div>', unsafe_allow_html=True)

st.markdown("""
<div style="display:flex;gap:2rem;justify-content:center;margin:0.8rem 0 1.5rem;font-size:0.8rem;color:#666">
    <span>🟢 <strong>新発見ワード</strong>：意味が通じる独立した言葉</span>
    <span>🟡 <strong>参考ワード</strong>：活用形など、単体では意味が伝わりにくい言葉</span>
</div>
""", unsafe_allow_html=True)


# ── サイドバー（情報表示のみ）─────────────────────────────────
st.sidebar.markdown("### 📊 調査サマリー")

st.sidebar.markdown(
    f'<div style="background:#f5f5f5;border-radius:10px;padding:1rem;margin-bottom:0.8rem">'
    f'<div style="font-size:0.75rem;color:#999;letter-spacing:0.08em">総調査ワード</div>'
    f'<div style="font-family:monospace;font-size:1.5rem;color:#1a237e;font-weight:700">{len(df_all):,}</div>'
    f'</div>',
    unsafe_allow_html=True,
)

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


# ── 音声生成 ──────────────────────────────────────────────
@st.cache_data
def generate_audio(reading):
    return generate_audio_bytes(reading)


# ── 共通: カード再生関数 ────────────────────────────────────
def play_audio_inline(word, reading, key_suffix):
    """ボタン押下で即座に音声再生（固定バーで再生）。"""
    b1, b2 = st.columns(2)
    with b1:
        if st.button("▶ 通常", key=f"n_{key_suffix}"):
            st.session_state.play_word = word
            st.session_state.play_reading = reading
            st.session_state.play_mode = "normal"
            st.session_state.play_count += 1
    with b2:
        if st.button("◀ 逆再生", key=f"r_{key_suffix}"):
            st.session_state.play_word = word
            st.session_state.play_reading = reading
            st.session_state.play_mode = "reverse"
            st.session_state.play_count += 1


def render_word_cards(df_words, key_prefix, show_quality=False):
    """ワードカードを品詞別に3列で表示。"""
    if df_words.empty:
        st.info("該当するワードはありません")
        return

    # 伝説ワード
    df_leg = df_words[df_words["品詞細分類"] == "伝説"]
    df_normal = df_words[df_words["品詞細分類"] != "伝説"]

    if not df_leg.empty:
        st.markdown('<div class="section-heading">👑 伝説のワード</div>', unsafe_allow_html=True)
        for leg_idx, (_, lrow) in enumerate(df_leg.iterrows()):
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
            play_audio_inline(lrow['ワード'], lrow.get('ヨミガナ', lrow['ワード']), f"{key_prefix}_leg_{leg_idx}")

    for pos in sorted(df_normal["品詞"].unique().tolist()):
        df_pos = df_normal[df_normal["品詞"] == pos]
        if show_quality:
            gc = len(df_pos[df_pos["品質"] == "green"])
            yc = len(df_pos[df_pos["品質"] == "yellow"])
            count_label = f"🟢{gc}" + (f" 🟡{yc}" if yc > 0 else "")
        else:
            count_label = f"{len(df_pos)}件"
        st.markdown(
            f'<div class="section-heading">■ {pos}（{count_label}）</div>',
            unsafe_allow_html=True,
        )
        cols = st.columns(3)
        for idx, (_, hrow) in enumerate(df_pos.iterrows()):
            quality = hrow.get("品質", "green")
            if quality == "green":
                quality_icon, badge_bg, badge_text, badge_color, border_color = "🟢", "#2e7d32", "新発見", "#fff", "#2e7d32"
            else:
                quality_icon, badge_bg, badge_text, badge_color, border_color = "🟡", "#f9a825", "参考", "#333", "#f9a825"
            with cols[idx % 3]:
                st.markdown(f"""
                <div class="hit-card" style="border-left-color:{border_color}">
                    <span class="hit-badge" style="background:{badge_bg};color:{badge_color}">{quality_icon} {badge_text}</span>
                    <div class="hit-word">{hrow['ワード']}</div>
                    <div class="hit-yomi">{hrow.get('ヨミガナ', '')}</div>
                    <div class="phoneme-row">[ {hrow.get('音素', '')} ]</div>
                    <div class="hit-meta">{hrow.get('品詞細分類', '')}</div>
                </div>
                """, unsafe_allow_html=True)
                play_audio_inline(hrow['ワード'], hrow.get('ヨミガナ', hrow['ワード']), f"{key_prefix}_{pos}_{idx}")


def render_fixed_player(tab_key):
    """固定プレイヤーバー（再生中のワードがあれば表示）。"""
    if st.session_state.play_word:
        pw = st.session_state.play_word
        pm = st.session_state.play_mode
        mode_label = "▶ 通常再生" if pm == "normal" else "◀ 逆再生"
        mode_icon = "▶" if pm == "normal" else "◀"

        pr = st.session_state.play_reading or pw

        with st.status(f"{mode_icon} {pw}", expanded=True) as status:
            status.update(label=f"{mode_icon} {pw}　─　🔄 音声を生成しています...", state="running")
            normal_b, rev_b = generate_audio(pr)
            status.update(label=f"{mode_icon} {pw}　─　{mode_label}", state="complete")

        st.markdown(
            f'<div class="fixed-player-bar">'
            f'<span class="fixed-player-word">{pw}</span>'
            f'<span class="fixed-player-mode">{mode_label}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )
        pc = st.session_state.play_count
        audio_bytes = normal_b if pm == "normal" else rev_b
        audio_b64 = base64.b64encode(audio_bytes).decode()
        components.html(
            f'<audio id="ap_{pc}" controls style="width:100%" src="data:audio/mp3;base64,{audio_b64}"></audio>'
            f'<script>document.getElementById("ap_{pc}").play();</script>',
            height=54,
        )
        if st.button("閉じる", key=f"close_player_{tab_key}"):
            st.session_state.play_word = None
            st.session_state.play_reading = None
            st.session_state.play_mode = None
            st.rerun()


# ── タブ ─────────────────────────────────────────────────
_tab_names = [
    "🎤 自由入力",
    "📋 総調査ワード",
    "🟢 新発見ワード",
    "🟡 参考ワード",
    "📊 回文ヒット合計",
]
_has_review = len(df_needs_review) > 0
if _has_review:
    _tab_names.append(f"🔍 要検証（{len(df_needs_review)}）")
_tab_names.append("🎧 音声検証")

_tabs = st.tabs(_tab_names)
tab_free = _tabs[0]
tab1, tab2, tab3, tab4 = _tabs[1], _tabs[2], _tabs[3], _tabs[4]
if _has_review:
    tab5 = _tabs[5]
    tab6 = _tabs[6]
else:
    tab5 = None
    tab6 = _tabs[5]


# ═══════════════════════════════════════════════════════════
# Tab: 自由入力
# ═══════════════════════════════════════════════════════════
with tab_free:
    st.markdown(
        '<div class="section-heading">🎤 好きな言葉を逆再生してみよう</div>',
        unsafe_allow_html=True,
    )
    st.markdown(f"""
    <div style="font-size:0.82rem;color:#666;margin-bottom:1rem">
        ひらがな・カタカナで入力して、通常再生と逆再生を聴き比べられます。（{FREE_INPUT_MAX_LENGTH}文字以内）
    </div>
    """, unsafe_allow_html=True)

    free_text = st.text_input(
        "テキスト入力",
        placeholder="例: おおえんまはんみょう",
        label_visibility="collapsed",
        max_chars=FREE_INPUT_MAX_LENGTH,
    )

    if free_text:
        ok, err_msg = validate_free_input(free_text)
        if not ok:
            st.warning(err_msg)
        else:
            free_text_clean = free_text.strip()
            free_katakana = to_katakana(free_text_clean)
            st.markdown(f"""
            <div class="selected-word-box">
                <div class="selected-word-main" style="color:#1a237e">{free_katakana}</div>
                {'<div style="font-size:0.85rem;color:#999;margin-top:0.3rem">入力: ' + free_text_clean + '</div>' if free_text_clean != free_katakana else ''}
            </div>
            """, unsafe_allow_html=True)

            with st.spinner(f"「{free_katakana}」の音声を生成中..."):
                free_normal, free_reverse = generate_audio(free_katakana)

            free_n_b64 = base64.b64encode(free_normal).decode()
            free_r_b64 = base64.b64encode(free_reverse).decode()

            cache_buster = hash(free_text_clean)
            col_n, col_r = st.columns(2)
            with col_n:
                st.markdown('<div class="player-label-normal">▶ 通常再生</div>', unsafe_allow_html=True)
                st.markdown(
                    f'<audio controls style="width:100%" src="data:audio/mp3;base64,{free_n_b64}#n{cache_buster}"></audio>',
                    unsafe_allow_html=True,
                )
            with col_r:
                st.markdown('<div class="player-label-reverse">◀ 逆再生</div>', unsafe_allow_html=True)
                st.markdown(
                    f'<audio controls style="width:100%" src="data:audio/mp3;base64,{free_r_b64}#r{cache_buster}"></audio>',
                    unsafe_allow_html=True,
                )


# ═══════════════════════════════════════════════════════════
# Tab1: 総調査ワード
# ═══════════════════════════════════════════════════════════
with tab1:
    # ── カテゴリボタン ──
    categories = df_all.groupby("品詞").size().sort_values(ascending=False)
    cat_labels = ["すべて"] + [f"{pos}（{cnt:,}）" for pos, cnt in categories.items()]
    cat_keys = ["すべて"] + categories.index.tolist()

    selected_cat = st.radio(
        "カテゴリ",
        cat_keys,
        format_func=lambda x: x if x == "すべて" else f"{x}（{categories[x]:,}）",
        horizontal=True,
        label_visibility="collapsed",
    )

    df_display = df_all if selected_cat == "すべて" else df_all[df_all["品詞"] == selected_cat]

    # ── 品詞細分類フィルター（カテゴリ選択時） ──
    if selected_cat != "すべて":
        subcats = df_display["品詞細分類"].value_counts()
        if len(subcats) > 1:
            sub_keys = ["すべて"] + subcats.index.tolist()
            selected_sub = st.radio(
                "細分類",
                sub_keys,
                format_func=lambda x: x if x == "すべて" else f"{x}（{subcats[x]:,}）",
                horizontal=True,
                label_visibility="collapsed",
            )
            if selected_sub != "すべて":
                df_display = df_display[df_display["品詞細分類"] == selected_sub]

    # ── ワード検索 ──
    search_query = st.text_input(
        "ワード検索",
        placeholder="キーワードで絞り込み...",
        label_visibility="collapsed",
    )
    if search_query:
        df_display = df_display[df_display["ワード"].str.contains(search_query, na=False)]

    # ── 回文ヒットのみ表示トグル ──
    hit_count = len(df_display[(df_display["回文判定"] == "〇") & (df_display["検証"] == "確認済み")])
    total_count = len(df_display)
    show_hits_only = st.toggle(
        f"回文ヒットのみ表示（{hit_count} 件）",
        value=False,
        key="toggle_hits_only",
    )
    if show_hits_only:
        df_display = filter_hits_only(df_display)

    # ── ページネーション ──
    display_total = len(df_display)
    _, total_pages = paginate(df_display, page=1)

    st.markdown(
        f'<div class="section-heading">{display_total:,} 件</div>',
        unsafe_allow_html=True,
    )

    page_col1, page_col2, page_col3 = st.columns([1, 2, 1])
    with page_col2:
        current_page = st.number_input(
            "ページ",
            min_value=1,
            max_value=total_pages,
            value=1,
            step=1,
            label_visibility="collapsed",
        )
    with page_col3:
        st.markdown(f"<div style='padding-top:0.5rem;color:#888;font-size:0.8rem'>/ {total_pages} ページ</div>", unsafe_allow_html=True)

    df_page, _ = paginate(df_display, page=current_page)

    # ── カード表示（1ページ分のみ）──
    cols = st.columns(3)
    for idx, (_, row) in enumerate(df_page.iterrows()):
        is_hit = row.get("検証") == "確認済み"
        quality = row.get("品質", "green")

        if is_hit:
            if quality == "green":
                icon, border_color, badge_bg, badge_color, badge_text = "🟢", "#2e7d32", "#2e7d32", "#fff", "新発見"
            else:
                icon, border_color, badge_bg, badge_color, badge_text = "🟡", "#f9a825", "#f9a825", "#333", "参考"
        else:
            icon, border_color = "", "#ccc"

        with cols[idx % 3]:
            if is_hit:
                st.markdown(
                    f'<div class="hit-card" style="border-left-color:{border_color}">'
                    f'<span class="hit-badge" style="background:{badge_bg};color:{badge_color}">{icon} {badge_text}</span>'
                    f'<div class="hit-word">{row["ワード"]}</div>'
                    f'<div class="hit-yomi">{row.get("ヨミガナ", "")}</div>'
                    f'<div class="phoneme-row">[ {row.get("音素", "")} ]</div>'
                    f'<div class="hit-meta">{row.get("品詞細分類", "")}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f'<div style="background:#fff;border:1px solid #eee;border-left:3px solid {border_color};'
                    f'border-radius:8px;padding:0.8rem 1rem;margin:0.3rem 0">'
                    f'<div style="font-size:1rem;color:#333;font-weight:500">{row["ワード"]}</div>'
                    f'<div style="font-size:0.7rem;color:#999">{row.get("ヨミガナ", "")}　[ {row.get("音素", "")} ]</div>'
                    f'<div style="font-size:0.65rem;color:#bbb">{row.get("品詞細分類", "")}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
            play_audio_inline(
                row["ワード"],
                row.get("ヨミガナ", row["ワード"]),
                f"tab1_p{current_page}_{idx}",
            )



# ═══════════════════════════════════════════════════════════
# Tab2: 新発見ワード（緑）
# ═══════════════════════════════════════════════════════════
with tab2:
    st.markdown(
        f'<div class="section-heading">🟢 新発見ワード（{len(df_hits_green)} 件）</div>',
        unsafe_allow_html=True,
    )
    st.markdown("""
    <div style="font-size:0.82rem;color:#666;margin-bottom:1rem">
        独立した意味を持つ言葉として音素回文が成立するワード
    </div>
    """, unsafe_allow_html=True)
    render_word_cards(df_hits_green, "green")


# ═══════════════════════════════════════════════════════════
# Tab3: 参考ワード（黄）
# ═══════════════════════════════════════════════════════════
with tab3:
    st.markdown(
        f'<div class="section-heading">🟡 参考ワード（{len(df_hits_yellow)} 件）</div>',
        unsafe_allow_html=True,
    )
    st.markdown("""
    <div style="font-size:0.82rem;color:#666;margin-bottom:1rem">
        動詞の活用形など、単体では意味が伝わりにくいワード（ファクトとして報告）
    </div>
    """, unsafe_allow_html=True)
    render_word_cards(df_hits_yellow, "yellow")


# ═══════════════════════════════════════════════════════════
# Tab4: 回文ヒット合計
# ═══════════════════════════════════════════════════════════
with tab4:
    st.markdown(
        f'<div class="section-heading">回文ヒット合計（{len(df_hits)} 件）</div>',
        unsafe_allow_html=True,
    )
    st.markdown("""
    <div style="font-size:0.82rem;color:#666;line-height:1.7;margin-bottom:1rem">
        🟢 <strong>新発見ワード</strong>：独立した意味を持つ言葉<br>
        🟡 <strong>参考ワード</strong>：動詞の活用形など
    </div>
    """, unsafe_allow_html=True)
    render_word_cards(df_hits, "all", show_quality=True)


# ═══════════════════════════════════════════════════════════
# Tab5: 要検証（要検証ワードがある場合のみ表示）
# ═══════════════════════════════════════════════════════════
if _has_review and tab5 is not None:
    with tab5:
        st.markdown(
            f'<div class="section-heading">🔍 要検証ワード（{len(df_needs_review)} 件）</div>',
            unsafe_allow_html=True,
        )
        st.markdown("""
        <div style="font-size:0.82rem;color:#666;margin-bottom:1rem">
            音素の並びが厳密な回文ではないが、元データで回文判定〇とされたワード。<br>
            逆再生を聴いて、同じ音に聞こえるか確認してください。
        </div>
        """, unsafe_allow_html=True)
        if not df_needs_review.empty:
            cols = st.columns(3)
            for idx, (_, hrow) in enumerate(df_needs_review.iterrows()):
                phonemes = hrow.get("音素", "").strip().split()
                phonemes_rev = phonemes[::-1]
                with cols[idx % 3]:
                    st.markdown(
                        f'<div class="hit-card" style="border-left-color:#ff9800">'
                        f'<span class="hit-badge" style="background:#ff9800;color:#fff">🔍 要検証</span>'
                        f'<div class="hit-word">{hrow["ワード"]}</div>'
                        f'<div class="hit-yomi">{hrow.get("ヨミガナ", "")}</div>'
                        f'<div class="phoneme-row">順: [ {" ".join(phonemes)} ]</div>'
                        f'<div class="phoneme-row" style="color:#e53935">逆: [ {" ".join(phonemes_rev)} ]</div>'
                        f'<div class="hit-meta">{hrow.get("品詞", "")} / {hrow.get("品詞細分類", "")}</div>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )
                    play_audio_inline(
                        hrow["ワード"],
                        hrow.get("ヨミガナ", hrow["ワード"]),
                        f"review_{idx}",
                    )


# ═══════════════════════════════════════════════════════════
# Tab6: 音声検証
# ═══════════════════════════════════════════════════════════
with tab6:
    # ── ワード選択（回文ヒットのみ） ──
    word_options = df_hits["ワード"].tolist()
    if not word_options:
        st.warning("回文ヒットワードがありません")
        st.stop()

    default_index = 0
    if st.session_state.selected_word_for_audio and st.session_state.selected_word_for_audio in word_options:
        default_index = word_options.index(st.session_state.selected_word_for_audio)

    selected_word = st.selectbox(
        "聴きたいワードを選択",
        word_options,
        index=default_index,
        label_visibility="collapsed",
    )

    row = df_hits[df_hits["ワード"] == selected_word].iloc[0]
    is_hit = row["回文判定"] == "〇"
    is_legendary = str(row.get("品詞細分類", "")) == "伝説"
    phonemes = str(row.get("音素", "")).split()
    phonemes_rev = phonemes[::-1]

    # ── ワード表示 + 音声再生（横並び） ──
    if is_legendary:
        badge = '<span style="background:linear-gradient(90deg,#ff8f00,#ffb300);color:#fff;font-size:0.65rem;padding:2px 10px;border-radius:10px;font-weight:900">👑 伝説のワード</span>'
        word_color = "#e65100"
    elif is_hit:
        quality = row.get("品質", "green")
        if quality == "green":
            badge = '<span style="background:#2e7d32;color:white;font-size:0.65rem;padding:2px 8px;border-radius:10px;font-weight:900">🟢 新発見</span>'
        else:
            badge = '<span style="background:#f9a825;color:#333;font-size:0.65rem;padding:2px 8px;border-radius:10px;font-weight:900">🟡 参考</span>'
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

    # ── 音声プレイヤー ──
    selected_reading = str(row.get('ヨミガナ', selected_word))
    with st.spinner(f"「{selected_word}」の音声を生成中..."):
        normal_bytes, reverse_bytes = generate_audio(selected_reading)

    a1, a2 = st.columns(2)
    with a1:
        st.markdown('<div class="player-label-normal">▶ 通常再生</div>', unsafe_allow_html=True)
        st.audio(normal_bytes, format="audio/mp3")
    with a2:
        st.markdown('<div class="player-label-reverse">◀ 逆再生（検証）</div>', unsafe_allow_html=True)
        st.audio(reverse_bytes, format="audio/mp3")

    # ── 判定結果 ──
    if is_legendary:
        st.markdown("""
        <div style="background:linear-gradient(135deg,#fff8e1,#fff3c4);
                    border:2px solid #ff8f00;border-radius:16px;
                    padding:1.2rem;margin-top:1rem;text-align:center;
                    box-shadow:0 4px 16px rgba(255,143,0,0.1)">
            <span style="font-size:1.8rem">👑</span>
            <span style="font-family:'Noto Serif JP',serif;font-size:1.2rem;
                        color:#e65100;margin-left:0.5rem;vertical-align:middle">
                伝説のワード ── 探偵ナイトスクープが発見した原点にして頂点
            </span>
        </div>
        """, unsafe_allow_html=True)
    elif is_hit:
        st.markdown("""
        <div style="background:#f1f8e9;border:1px solid #2e7d32;border-radius:12px;
                    padding:1rem;margin-top:1rem;text-align:center">
            <span style="font-size:1.1rem;color:#2e7d32;font-weight:700">
                ✅ 音素回文 確認済み ── 逆再生しても同じ音に聞こえます
            </span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── 音素分析セクション ──
    col_fwd, col_rev = st.columns(2)
    with col_fwd:
        st.markdown('<div class="section-heading">▶ 順方向</div>', unsafe_allow_html=True)
        fwd_html = "".join([f'<span class="ph-chip">{p}</span>' for p in phonemes])
        st.markdown(f'<div class="phoneme-viz">{fwd_html}</div>', unsafe_allow_html=True)
    with col_rev:
        st.markdown('<div class="section-heading">◀ 逆方向</div>', unsafe_allow_html=True)
        rev_html = "".join([f'<span class="ph-chip ph-chip-rev">{p}</span>' for p in phonemes_rev])
        st.markdown(f'<div class="phoneme-viz">{rev_html}</div>', unsafe_allow_html=True)

    if is_hit and phonemes:
        st.markdown('<div class="section-heading">マッチング詳細</div>', unsafe_allow_html=True)
        match_cols = st.columns(min(len(phonemes), 8))
        for i, (f, r) in enumerate(zip(phonemes, phonemes_rev)):
            with match_cols[i % min(len(phonemes), 8)]:
                if f == r:
                    st.markdown(f'<div style="text-align:center;padding:4px"><span style="color:#2e7d32">✅</span><br><code>{f}</code></div>', unsafe_allow_html=True)
                elif {f, r} in [{"e", "y"}, {"o", "u"}]:
                    st.markdown(f'<div style="text-align:center;padding:4px"><span style="color:#f57c00">🔁</span><br><code>{f}≈{r}</code></div>', unsafe_allow_html=True)


# ── 固定プレイヤーバー（タブ外で1回だけ描画）──────────────────
render_fixed_player("global")

# ── フッター ─────────────────────────────────────────────
st.markdown(f"""
<div class="knight-footer">
    毎週の放送を家族そろって観ていた探偵ナイトスクープ。<br>
    「オオエンマハンミョウ」の回に感動し、AIとプログラミングで{len(df_all):,}語を調査しました。<br>
    いつか番組に関わりたいという夢が、このプロジェクトの原動力です。<br><br>
    <span style="color:#1a237e;font-weight:500">探偵ナイトスクープ様、家族の笑顔をいつもありがとうございます。</span>
</div>
""", unsafe_allow_html=True)

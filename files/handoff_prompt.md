# Handoff Prompt

## 今すぐやること
1. **要検証83件の聴き取り判別** — 要検証タブから各ワードの通常再生・逆再生を聴いて、同じ音に聞こえるか判断
2. **判別結果の反映** — ユーザーが「OK」としたものは確認済みへ、「NG」は除外
3. **探偵ナイトスクープ様へのメール送信**

## 現在の進捗
- app.py: UI担当（Streamlitアプリ）
- data_logic.py: ビジネスロジック（テスト済み）
- test_data_logic.py: 29テスト全GREEN
- Streamlit Cloudで自動デプロイ中

## 注意事項
- Streamlit Cloud は Python 3.11 + 古めのStreamlitバージョン
- `st.audio` に `key` パラメータを使わない
- `render_fixed_player` はタブ外で1回だけ呼ぶ
- CSSのワイルドカードセレクタに注意（ラジオボタン等に影響）

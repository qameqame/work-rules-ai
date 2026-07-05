import streamlit as st
import requests
import os

API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(page_title="就業規則AI", page_icon="📋")
st.title("📋 就業規則AI")
st.caption("就業規則について何でも質問してください。")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if msg.get("sources"):
            with st.expander("参照した条文"):
                for s in msg["sources"]:
                    st.caption(f"ファイル: {s.get('source', '不明')}  ページ: {s.get('page', '不明')}")

if question := st.chat_input("例：年次有給休暇は何日取得できますか？"):
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.write(question)

    with st.chat_message("assistant"):
        with st.spinner("就業規則を検索中..."):
            try:
                res = requests.post(
                    f"{API_URL}/ask",
                    json={"question": question},
                    timeout=120,
                )
                res.raise_for_status()
                data = res.json()
                answer = data["answer"]
                sources = data.get("sources", [])
            except requests.exceptions.Timeout:
                answer = "タイムアウトしました。モデルの読み込み中の可能性があります。しばらくしてから再度お試しください。"
                sources = []
            except Exception as e:
                answer = f"エラーが発生しました: {e}"
                sources = []

        st.write(answer)

        if sources:
            with st.expander("参照した条文"):
                for s in sources:
                    st.caption(f"ファイル: {s.get('source', '不明')}  ページ: {s.get('page', '不明')}")

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "sources": sources,
    })
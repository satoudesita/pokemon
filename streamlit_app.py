import streamlit as st
import pandas as pd
import sqlite3
import hashlib
import time

# パスワードをハッシュ化する関数
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

# ハッシュ化されたパスワードをチェックする関数
def check_hashes(password, hashed_text):
    if make_hashes(password) == hashed_text:
        return hashed_text
    return False

# テーブルを作成（存在しない場合）
def create_user_table(conn):
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS userstable(username TEXT, password TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS user_data(username TEXT, text_content TEXT)')
    conn.commit()

# 新しいユーザーを追加する関数
def add_user(conn, username, password):
    c = conn.cursor()
    c.execute('INSERT INTO userstable(username, password) VALUES (?, ?)', (username, password))
    conn.commit()

# ユーザーをログインさせる関数
def login_user(conn, username, password):
    c = conn.cursor()
    c.execute('SELECT * FROM userstable WHERE username = ? AND password = ?', (username, password))
    data = c.fetchall()
    return data

# ユーザーのテキストを保存する関数
def save_user_text(conn, username, text_content):
    c = conn.cursor()
    c.execute('INSERT OR REPLACE INTO user_data(username, text_content) VALUES (?, ?)', (username, text_content))
    conn.commit()

# ユーザーのテキストを取得する関数
def get_user_text(conn, username):
    c = conn.cursor()
    c.execute('SELECT text_content FROM user_data WHERE username = ?', (username,))
    data = c.fetchone()
    return data[0] if data else ""

def main():
    st.title("ログイン機能テスト")
    
    menu = ["ホーム", "ログイン", "サインアップ"]
    choice = st.sidebar.selectbox("メニュー", menu)

    # データベースに接続
    conn = sqlite3.connect('database.db')
    create_user_table(conn)

    if choice == "ホーム":
        st.subheader("ホーム画面です")

    elif choice == "ログイン":
        st.subheader("ログイン画面です")

        username = st.sidebar.text_input("ユーザー名を入力してください")
        password = st.sidebar.text_input("パスワードを入力してください", type='password')

        if st.sidebar.checkbox("ログイン"):
            hashed_pswd = make_hashes(password)
            result = login_user(conn, username, check_hashes(password, hashed_pswd))

            if result:
                st.success("{}さんでログインしました".format(username))

                # ユーザーの以前のテキストを取得
                user_text = get_user_text(conn, username)
                text_content = st.text_area("テキストを入力してください", value=user_text, height=300)

                if st.button("保存"):
                    save_user_text(conn, username, text_content)
                    st.success("テキストを保存しました")

            else:
                st.warning("ユーザー名かパスワードが間違っています")

    elif choice == "サインアップ":
        st.subheader("新しいアカウントを作成します")
        new_user = st.text_input("ユーザー名を入力してください")
        new_password = st.text_input("パスワードを入力してください", type='password')

        if st.button("サインアップ"):
            # ユーザー追加のリトライ処理
            retries = 5
            for i in range(retries):
                try:
                    add_user(conn, new_user, make_hashes(new_password))
                    st.success("アカウントの作成に成功しました")
                    st.info("ログイン画面からログインしてください")
                    break
                except sqlite3.OperationalError:
                    if i < retries - 1:  # 最後の試行でなければ
                        time.sleep(1)  # 待機してから再試行
                    else:
                        st.error("アカウントの作成に失敗しました。後ほど再試行してください。")

    # コネクションを閉じる
    conn.close()

if __name__ == '__main__':
    main()

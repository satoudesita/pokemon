import streamlit as st
import sqlite3
import hashlib
import time
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

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
    c.execute('CREATE TABLE IF NOT EXISTS userstable(username TEXT PRIMARY KEY, password TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS user_data(username TEXT PRIMARY KEY, text_content TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS study_data(username TEXT, date TEXT, study_hours REAL, score INTEGER)')
    conn.commit()

# 新しいユーザーを追加する関数
def add_user(conn, username, password):
    c = conn.cursor()
    c.execute('INSERT INTO userstable(username, password) VALUES (?, ?)', (username, password))
    conn.commit()

# ユーザー名の存在を確認する関数
def check_user_exists(conn, username):
    c = conn.cursor()
    c.execute('SELECT * FROM userstable WHERE username = ?', (username,))
    return c.fetchone() is not None

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

# 学習データを保存する関数
def save_study_data(conn, username, date, study_hours, score):
    c = conn.cursor()
    c.execute('INSERT INTO study_data(username, date, study_hours, score) VALUES (?, ?, ?, ?)',
              (username, date, study_hours, score))
    conn.commit()

# ユーザーの学習データを取得する関数
def get_study_data(conn, username):
    c = conn.cursor()
    c.execute('SELECT date, study_hours, score FROM study_data WHERE username = ?', (username,))
    return c.fetchall()

def main():
    st.title("ログイン機能テスト")
    
    menu = ["ホーム", "ログイン", "サインアップ"]
    choice = st.sidebar.selectbox("メニュー", menu)

    # データベースに接続
    conn = sqlite3.connect('database.db')
    create_user_table(conn)

    if choice == "ホーム":
        st.subheader("ホーム画面です")
        if 'username' in st.session_state:
            username = st.session_state['username']
            st.write(f"ようこそ、{username}さん！")

            # 学習データ入力フォーム
            with st.form(key='study_form'):
                date = st.date_input('学習日', value=datetime.now())
                study_hours = st.number_input('学習時間（時間）', min_value=0.0, step=0.5)
                score = st.number_input('テストのスコア', min_value=0, max_value=100, step=1)
                submit_button = st.form_submit_button(label='データを保存')

            # データの保存処理
            if submit_button:
                save_study_data(conn, username, date.strftime('%Y-%m-%d'), study_hours, score)
                st.success('データが保存されました！')

            # 保存されたデータの表示
            study_data = get_study_data(conn, username)
            if study_data:
                df = pd.DataFrame(study_data, columns=['Date', 'Study Hours', 'Score'])
                st.write('### 現在の学習データ')
                st.dataframe(df)

                # グラフ描画のオプション
                st.write('### グラフ表示')
                plot_type = st.selectbox('表示するグラフを選択してください', ['学習時間', 'スコア'])

                # グラフ描画
                fig, ax = plt.subplots()
                if plot_type == '学習時間':
                    ax.plot(df['Date'], df['Study Hours'], marker='o')
                    ax.set_title('日別学習時間の推移')
                    ax.set_xlabel('日付')
                    ax.set_ylabel('学習時間（時間）')
                elif plot_type == 'スコア':
                    ax.plot(df['Date'], df['Score'], marker='o', color='orange')
                    ax.set_title('日別スコアの推移')
                    ax.set_xlabel('日付')
                    ax.set_ylabel('スコア')
                st.pyplot(fig)
            else:
                st.write('データがまだ入力されていません。')
        else:
            st.warning("ログインしていません。")

    elif choice == "ログイン":
        st.subheader("ログイン画面です")

        username = st.sidebar.text_input("ユーザー名を入力してください")
        password = st.sidebar.text_input("パスワードを入力してください", type='password')

        if st.sidebar.checkbox("ログイン"):
            hashed_pswd = make_hashes(password)
            result = login_user(conn, username, check_hashes(password, hashed_pswd))

            if result:
                st.session_state['username'] = username
                st.success("{}さんでログインしました".format(username))
            else:
                st.warning("ユーザー名かパスワードが間違っています")

    elif choice == "サインアップ":
        st.subheader("新しいアカウントを作成します")
        new_user = st.text_input("ユーザー名を入力してください")
        new_password = st.text_input("パスワードを入力してください", type='password')

        if st.button("サインアップ"):
            # ユーザー名がすでに存在するか確認
            if check_user_exists(conn, new_user):
                st.error("このユーザー名は既に使用されています。別のユーザー名を選んでください。")
            else:
                try:
                    add_user(conn, new_user, make_hashes(new_password))
                    st.success("アカウントの作成に成功しました")
                    st.info("ログイン画面からログインしてください")
                except Exception as e:
                    st.error(f"アカウントの作成に失敗しました: {e}")

    # コネクションを閉じる
    conn.close()

if __name__ == '__main__':
    main()

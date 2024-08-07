import streamlit as st
import pandas as pd
from streamlit_autocomplete import st_autocomplete

# Excelファイルのパス
EXCEL_FILE_PATH = 'ポケモン.xlsx'

def load_data():
    # Excelファイルの「種族値」シートを読み込み
    df = pd.read_excel(EXCEL_FILE_PATH, sheet_name='種族値')
    return df

# データの読み込み
data = load_data()

# ポケモンの名前リストを取得
pokemon_names = data['ポケモン'].tolist()

st.title("ポケモンステータス表示")

# オートコンプリート機能付きのセレクトボックス
selected_pokemon = st_autocomplete("ポケモンの名前を入力してください", pokemon_names)

if selected_pokemon:
    # 選択されたポケモンでフィルタリング
    filtered_data = data[data['ポケモン'] == selected_pokemon]

    if not filtered_data.empty:
        # ステータス情報を表示（横並びにするためのCSSスタイルを適用）
        pokemon_info = filtered_data.iloc[0]
        st.write(f"ポケモン名: {pokemon_info['ポケモン']}")
        st.write(f"H: {pokemon_info['H']} | A: {pokemon_info['A']} | B: {pokemon_info['B']} | C: {pokemon_info['C']} | D: {pokemon_info['D']} | S: {pokemon_info['S']} | 合計: {pokemon_info['合計']}")
    else:
        st.write("該当するポケモンが見つかりませんでした。")

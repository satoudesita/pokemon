import streamlit as st
import pandas as pd

# Excelファイルのパス（適宜変更してください）
EXCEL_FILE_PATH = 'pokemon_data.xlsx'

def load_data():
    # Excelファイルを読み込み
    df = pd.read_excel(EXCEL_FILE_PATH)
    return df

def main():
    st.title("ポケモンステータス表示")

    # データの読み込み
    data = load_data()

    # ポケモンの名前をユーザーに入力してもらう
    pokemon_name = st.text_input("ポケモンの名前を入力してください")

    if pokemon_name:
        # 入力された名前でフィルタリング
        filtered_data = data[data['ポケモン'] == pokemon_name]

        if not filtered_data.empty:
            # ステータス情報を表示
            pokemon_info = filtered_data.iloc[0]
            st.write(f"ポケモン名: {pokemon_info['ポケモン']}")
            st.write(f"H: {pokemon_info['H']}")
            st.write(f"A: {pokemon_info['A']}")
            st.write(f"B: {pokemon_info['B']}")
            st.write(f"C: {pokemon_info['C']}")
            st.write(f"D: {pokemon_info['D']}")
            st.write(f"S: {pokemon_info['S']}")
            st.write(f"合計: {pokemon_info['合計']}")
        else:
            st.write("該当するポケモンが見つかりませんでした。")

if __name__ == "__main__":
    main()

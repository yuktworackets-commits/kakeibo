import streamlit as st
import db
from datetime import datetime
import pandas as pd
db.init_db()

if "amount" not in st.session_state:
    st.session_state.amount = 0

st.title("かんたん家計簿")

def yen(amount):
    return f"{amount:,}円"

def color_label(color):
    return f"{db.colors[color]['emoji']} {color}"

def add_amount(value):#ボタンを押したときの合計への加算
    st.session_state.amount += value


def clear_amount():#クリアボタン
    st.session_state.amount = 0

def register_expense():#登録ボタンに関する関数
    amount = st.session_state.amount
    color = st.session_state.color or db.defaultColor

    if amount == 0:
        st.toast("0円は登録できません")
        return

    db.add_expense(amount, color)
    st.toast(f"{yen(amount)} を登録しました")
    st.session_state.amount = 0
#以下は履歴ページに関する関数
def get_this_month():
    now = datetime.now(db.jpt)
    return db.get_expenses(now.year, now.month)


def save_memo():
    targetId = st.session_state.memoId
    memo = st.session_state.memoText
    ids = [e["id"] for e in get_this_month()]

    if targetId not in ids:
        st.toast(f"{targetId}番のデータはありません")
        return

    db.update_memo(targetId, memo)
    st.toast(f"{targetId}番のメモを保存しました")


def delete_by_id():
    targetId = st.session_state.deleteId
    ids = [e["id"] for e in get_this_month()]

    if targetId not in ids:
        st.toast(f"{targetId}番のデータはありません")
        return

    db.delete_expense(targetId)
    st.toast(f"{targetId}番を削除しました")
#以上は履歴ページに関する関数
#以下三つの関数は各タブを開いたときに、実行される。
def show_home():#出金入力画面
    st.header("支出")
    st.subheader(yen(st.session_state.amount))

    st.button("10,000円", on_click=add_amount, args=(10000,))
    st.button("1,000円", on_click=add_amount, args=(1000,))
    st.button("100円", on_click=add_amount, args=(100,))

    st.button("クリア", on_click=clear_amount)

    st.pills(
        "色",
        list(db.colors),
        selection_mode="single",
        default="緑",
        key="color",
        format_func=color_label,
    )

    st.button("支出を登録", on_click=register_expense)

def show_history():#履歴ページ
    expenses = get_this_month()
    st.dataframe(
        expenses,
        hide_index=True,
        column_config={
            "id": "番号",
            "amount": "金額",
            "color": "色",
            "memo": "メモ",
            "created_at": "登録日時",
        },
    )

    st.subheader("メモの編集")
    st.number_input("番号", min_value=1, step=1, key="memoId")
    st.text_input("メモ", key="memoText")
    st.button("メモを保存", on_click=save_memo)

    st.subheader("データの削除")
    st.number_input("番号", min_value=1, step=1, key="deleteId")
    st.button("削除", on_click=delete_by_id)

def show_summary():#集計ページ
    expenses = get_this_month()
    if not expenses:
        return

    df = pd.DataFrame(expenses)

    st.subheader("今月の合計")
    st.write(yen(df["amount"].sum()))

    st.subheader("色ごとの合計")
    byColor = df.groupby("color")["amount"].sum().sort_values(ascending=False)
    for color, amount in byColor.items():
        st.write(f"{color_label(color)}：{yen(amount)}")



homeTab, historyTab, summaryTab = st.tabs(["ホーム", "履歴", "集計"])

with homeTab:
    show_home()

with historyTab:
    show_history()


with summaryTab:
    show_summary()
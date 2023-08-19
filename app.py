import streamlit as st
import pandas as pd
import base64
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

item_ls = []
item_url_ls=[]
def browser_setup(chromedriver_path):
    """ブラウザを起動する関数"""
    #ブラウザの設定
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    #ブラウザの起動
    browser = webdriver.Chrome(executable_path = chromedriver_path , options = options)
    browser.implicitly_wait(3)
    return browser


def get_url(KEYWORD , browser):
    #売り切れ表示
    url = 'https://jp.mercari.com/search?keyword=' + KEYWORD + '&status=sold_out%7Ctrading'
    browser.get(url)
    browser.implicitly_wait(5)
    wait = WebDriverWait(browser, 10)

    #商品の詳細ページのURLを取得する
    # item_box = browser.find_elements_by_css_selector('#item-grid > ul > li')
    item_box = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '#item-grid > ul > li')))
    for item_elem in item_box:
        # item_url_ls.append(item_elem.find_element_by_css_selector('a').get_attribute('href'))
        # item_url_ls.append(item_elem.find_elements(By.CSS_SELECTOR, 'a').get_attribute('href'))
        item_urls = item_elem.find_elements(By.CSS_SELECTOR, 'a')
        for item_url in item_urls:
            item_url_ls.append(item_url.get_attribute('href'))

def is_contained(target_str, search_str):
    """
    target_str に search_str が含まれるかどうかを判定する関数
    """
    if target_str.find(search_str) >= 0:
        return True
    else:
        return False
    
def df_to_csv_local_url(df: pd.DataFrame , output_csv_path: str = "output.csv"):
    """ データフレーム型の表をcsv形式でダウンロードできるURLを生成する関数 """
    # csvの生成＆ローカルディレクトリ上に保存（「path_or_buf」を指定したら、戻り値は「None」）
    df.to_csv(path_or_buf=output_csv_path, index=False, encoding='utf-8-sig')
    # ダウロードできるaタグを生成
    csv = df.to_csv(index=False, encoding='utf-8-sig')
    b64 = base64.b64encode(csv.encode('utf-8-sig')).decode()  # some strings <-> bytes conversions necessary here
    csv_local_href = f'<a href="data:file/csv;base64,{b64}" download={output_csv_path}>CSVでダウンロード</a>'
    return csv_local_href


def page_mercari_com(browser):
    wait = WebDriverWait(browser, 10)
    #商品名 
    item_name = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#item-info > section:nth-child(1) > div.mer-spacing-b-12'))).text
    # 商品説明
    item_ex = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#item-info > section:nth-child(2) > div:nth-child(2)'))).text
    # 価格
    item_price = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#item-info [data-testid="price"] > span:last-child'))).text
    return item_name , item_ex , item_price


def page_mercari_shop_com(browser):
    wait = WebDriverWait(browser, 10)
    #商品名 
    item_name = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'h1'))).text
    # 商品説明
    item_ex = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#product-info > section:nth-child(2) > div:nth-child(2)'))).text
    # 価格
    item_price = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#product-info [data-testid="product-price"] > span:last-child'))).text
    return item_name , item_ex , item_price


def get_data(browser , getting_count):
    #商品情報の詳細を取得する
    count = 0
    st.write("")
    st.write(f"商品数 : {getting_count}件 のみを取得中 \n")
    for item_url in item_url_ls:
        count = count + 1
        if count <= getting_count:
            browser.get(item_url)
            time.sleep(3)

            #商品名〜画像URLを取得
            if is_contained(item_url, "shop"):  # 商品詳細ページが「mercari-shops.com」の場合
                item_name , item_ex , item_price = page_mercari_shop_com(browser)
            else:  # 商品詳細ページが「mercari.com」の場合
                item_name , item_ex , item_price = page_mercari_com(browser)
            
            data = {
                '商品名':item_name,
                '商品説明':item_ex,
                '価格':item_price,
                'URL':item_url,
            }
            item_ls.append(data)


def main():
    # ファイルパスの定義
    chromedriver_path =  "static/driver/chromedriver_114_linux"
    output_csv_path = "media/csv/output.csv"

    KEYWORD = ""
    st.title("メルカリ売れ行き商品を一括取得")
    st.write("<p></p>", unsafe_allow_html=True)
    st.markdown("販売状況が「売り切れ」のみの商品の情報を一括取得します。<br> ※ 約 45秒/10件 ほど処理に時間がかかります。", unsafe_allow_html=True)
    st.write("<p></p>", unsafe_allow_html=True)
    KEYWORD = st.text_input("検索キーワード")
    st.write("<p></p>", unsafe_allow_html=True)
    getting_count = st.text_input("取得する件数（ 数値のみ入力可能 ）") 
    st.write("")
    try:
        getting_count = int(getting_count)
    except:
        pass

    button_clicked = st.button("取得開始")
    if KEYWORD != "" and isinstance(getting_count , int) and button_clicked :
        getting_count = int(getting_count)
        browser = browser_setup(chromedriver_path)
        get_url(KEYWORD , browser)
        get_data(browser , getting_count)
        df = pd.DataFrame(item_ls)
        csv_local_href = df_to_csv_local_url(df , output_csv_path)
        st.markdown(csv_local_href , unsafe_allow_html=True)


if __name__ == '__main__':
    main()
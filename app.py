import streamlit as st
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time


item_ls = []
item_url_ls=[]
def browser_setup():
    """ブラウザを起動する関数"""
    #ブラウザの設定
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    #ブラウザの起動
    browser = webdriver.Chrome('chromedriver_112',options=options)
    browser.implicitly_wait(3)
    return browser


def get_url(KEYWORD , browser):
    #売り切れ表示
    url = 'https://jp.mercari.com/search?keyword=' + KEYWORD + '&status=sold_out%7Ctrading'
    browser.get(url)
    browser.implicitly_wait(5)

    #商品の詳細ページのURLを取得する
    # item_box = browser.find_elements_by_css_selector('#item-grid > ul > li')
    item_box = browser.find_elements(By.CSS_SELECTOR, '#item-grid > ul > li')
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


def page_mercari_com(browser):
    #商品名 
    item_name = browser.find_element(By.CSS_SELECTOR,'#item-info > section:nth-child(1) > div.mer-spacing-b-12').text
    # 商品説明
    shadow_root = browser.find_element(By.CSS_SELECTOR,'#item-info > section:nth-child(2) > mer-show-more').shadow_root
    item_ex = shadow_root.find_element(By.CSS_SELECTOR,'div.content.clamp').text
    # 価格
    item_price = browser.find_element(By.CSS_SELECTOR, '#item-info [data-testid="price"] > span:last-child').text
    # 画像のURL
    src = browser.find_element(By.CSS_SELECTOR,'div.slick-list div[data-index="0"] img').get_attribute('src')

    return item_name , item_ex , item_price , src


def page_mercari_shop_com(browser):
    #商品名 
    item_name = browser.find_element(By.CSS_SELECTOR, 'h1.chakra-heading.css-159ujot').text
    # 商品説明
    item_ex = browser.find_element(By.CSS_SELECTOR,'div.css-0 div.css-1x15fb3 p').text
    # 価格
    item_price = browser.find_element(By.CSS_SELECTOR,'.chakra-stack.css-xerlbm .css-x1sij0 .css-1vczxwq').text
    # 画像のURL
    src = browser.find_element(By.CSS_SELECTOR, 'div.css-1f8sh1y img').get_attribute('src')

    return item_name , item_ex , item_price , src


def get_data(browser):
    #商品情報の詳細を取得する
    count = 0
    print(f"商品数 : {len(item_url_ls)}個 \n")
    for item_url in item_url_ls:
        count = count + 1
        print(f"{count}個目")
        
        browser.get(item_url)
        time.sleep(3)

        #商品名〜画像URLを取得
        if is_contained(item_url, "shop"):  # 商品詳細ページが「mercari-shops.com」の場合
            item_name , item_ex , item_price , src = page_mercari_shop_com(browser)
        else:  # 商品詳細ページが「mercari.com」の場合
            item_name , item_ex , item_price , src = page_mercari_com(browser)
        
        data = {
            '商品名':item_name,
            '商品説明':item_ex,
            '価格':item_price,
            'URL':item_url,
            '画像URL':src
        }

        item_ls.append(data)


def main():
    KEYWORD = ""
    st.title("メルカリ売れ行き商品を一括取得")
    st.write("<p></p>", unsafe_allow_html=True)
    KEYWORD = st.text_input("検索キーワード")
    st.write("<p></p>", unsafe_allow_html=True)

    if KEYWORD != "":
        browser = browser_setup()
        get_url(KEYWORD , browser)
        get_data(browser)
        df = pd.DataFrame(item_ls)
        csv = df.to_csv(index=False)

        # CSVファイルのダウンロードボタンを表示
        st.download_button(
            label='CSVをダウンロード',
            data=csv,
            file_name='メルカリデータ.csv',
            mime='text/csv'
        )


if __name__ == '__main__':
    main()

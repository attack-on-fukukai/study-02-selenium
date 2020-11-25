import os
from selenium.webdriver import Chrome, ChromeOptions
import time
import pandas as pd
import logging
import math

# ログレベルを DEBUG に変更
logging.basicConfig(filename="LogFile.txt",encoding="utf-8",level=logging.INFO,format=" %(asctime)s - %(levelname)s - %(message)s")

### Chromeを起動する関数
def set_driver(driver_path,headless_flg):
    # Chromeドライバーの読み込み
    options = ChromeOptions()

    # ヘッドレスモード（画面非表示モード）をの設定
    if headless_flg==True:
        options.add_argument('--headless')

    # 起動オプションの設定
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36')
    #options.add_argument('log-level=3')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    options.add_argument('--incognito')          # シークレットモードの設定を付与

    # ChromeのWebDriverオブジェクトを作成する。
    return Chrome(executable_path=os.getcwd() + "\\" + driver_path,options=options)

### main処理
def main(search_keyword):

    logging.info("main処理の開始")

    try:
        logging.info("chromeを起動")

        # driverを起動
        driver=set_driver("chromedriver.exe",False)
        # Webサイトを開く
        driver.get("https://tenshoku.mynavi.jp/")
        time.sleep(5)
        # ポップアップを閉じる
        driver.execute_script('document.querySelector(".karte-close").click()')
        
        # ポップアップを閉じる
        driver.execute_script('document.querySelector(".karte-close").click()')

        # わざとエラーを発生させて、スルーされることを確認する
        raise Exception("わざとエラーを発生！")
    except:
        logging.info("わざと発生させたエラーをキャッチした")
        pass

    # 検索窓に入力
    driver.find_element_by_class_name("topSearch__text").send_keys(search_keyword)
    # 検索ボタンクリック
    driver.find_element_by_class_name("topSearch__button").click()
    
    logging.info("検索開始")
    
    #検索結果の件数を取得する
    time.sleep(20)  #読込みを待つために20秒間処理を止める
    _resultNum = driver.find_element_by_class_name("result__num").text    
    _resultNum = _resultNum.replace("件","")
    resultNum = int(_resultNum)

    logging.info("ヒット数：{}".format(_resultNum))

    # 全ページ数を求める
    allPageCnt = math.ceil(resultNum / 50)
    logging.info("全ページ数：{}".format(allPageCnt))

    if resultNum > 0:
    # 入力したキーワードで検索がヒットした場合        

        print("希望の仕事が{}件見つかりました！".format(_resultNum))
        print("\n")

        names = []
        copys = []
        statuss = []
        body0s = []
        body1s = []
        body2s = []
        body3s = []
        body4s = []

        cnt = 0
        for page in range(1,allPageCnt+1):
        # 2ページ目まで
            logging.info("{}ページ目を読込み".format(page))

            driver.get("https://tenshoku.mynavi.jp/list/kw{}/pg{}/?jobsearchType=14&searchType=18".format(search_keyword,page))
            elem_cassetteRecruit__contents = driver.find_elements_by_class_name("cassetteRecruit__content")
            for elem_cassetteRecruit__content in elem_cassetteRecruit__contents:
            #1案件ずつ
                cnt+=1
                logging.info("{}案件目を読込み".format(cnt))

                # 会社名を取得する
                name = elem_cassetteRecruit__content.find_element_by_class_name("cassetteRecruit__name").text
                
                # コピーを取得する
                copy = elem_cassetteRecruit__content.find_element_by_class_name("cassetteRecruit__copy").text

                # 雇用形態を取得する
                status = elem_cassetteRecruit__content.find_element_by_class_name("labelEmploymentStatus").text

                # 仕事内容 ～ 初年度年収を取得する
                elem_tableCondition__bodys = elem_cassetteRecruit__content.find_element_by_class_name("tableCondition").find_elements_by_class_name("tableCondition__body")
                
                body0 = elem_tableCondition__bodys[0].text
                body1 = elem_tableCondition__bodys[1].text
                body2 = elem_tableCondition__bodys[2].text
                body3 = elem_tableCondition__bodys[3].text
                if int(len(elem_tableCondition__bodys)) == 5:
                # 初年度年収が載っている案件
                    body4 = elem_tableCondition__bodys[4].text
                else:
                # 初年度年収が載っていない案件
                    body4 = ""
                
                # 画面に出力する
                print(name)
                print(copy)
                print(status)
                print(body0)
                print(body1)
                print(body2)
                print(body3)
                print(body4)
                print("\n")

                names.append(name)
                copys.append(copy)
                statuss.append(status)
                body0s.append(body0)
                body1s.append(body1)
                body2s.append(body2)
                body3s.append(body3)
                body4s.append(body4)
            
            if resultNum <= 50:
                break


        df = pd.DataFrame()    
        df["会社名"] = names
        df["コピー"] = copys
        df["雇用形態"] = statuss
        df["仕事内容"] = body0s
        df["対象となる方"] = body1s
        df["勤務地"] = body2s
        df["給与"] = body3s
        df["初年度年収"] = body4s
        df.to_csv('希望の仕事.csv', index=False,)
    else:
    #入力したキーワードで検索がヒットしなかった場合
        print("希望の仕事は見つかりませんでした")

    logging.info("main処理の終了")


### 直接起動された場合はmain()を起動(モジュールとして呼び出された場合は起動しないようにするため)
if __name__ == "__main__":    
    search_keyword =input("希望するキーワードを入力してください >>> ")
    logging.info("入力されたキーワード：{}".format(search_keyword))
    main(search_keyword)

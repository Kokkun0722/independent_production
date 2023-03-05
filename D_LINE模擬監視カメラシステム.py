# このプログラムは、
# Webカメラを使って監視カメラのようなものを作り、
# 人が部屋に入ったり出たりした場合に、
# その瞬間の画像と入室/退室のタイムスタンプを
# LINE Notifyを使って送信するプログラムです。

import cv2
import time
import requests
import datetime

# 設定値
HUMAN_THRESHOLD=2000
FRAME_RATE=1

# 検知結果
prev_exist=False
human_exist=False
human_move=0

# 画像送信の定数
url = "https://notify-api.line.me/api/notify" 
token = "XfeZrJIh1meAmMM38vJVlDoKvfzY2HrX2PpPEFqWRir"
headers = {"Authorization" : "Bearer "+ token} 

# カメラのキャプチャを開始する
cap = cv2.VideoCapture(0)

# 前フレームの画像
prev_frame = None

while True:

    # カメラからフレームを取得する
    ret, frame = cap.read()

    # キャプチャに失敗した場合は終了する
    if not ret:
        break

    # グレースケールに変換する
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # 初めてのフレームの場合は前フレームを更新する
    if prev_frame is None:
        prev_frame = gray
        continue

    # 面積の総和
    count = 0
    
    # 2つのフレームの差分を求める
    diff = cv2.absdiff(prev_frame, gray)

    # 閾値を設定して、差分画像を2値化する
    thresh = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)[1]

    # 輪郭を抽出する
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # 輪郭があれば、変化があったことを示す赤い矩形を描画する
    rect_num = 0
    center_sum_x = 0
    center_sum_y = 0
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        rect_num += 1
        count += w * h
        if(human_exist):
            color=(0, 0, 255)
        else:
            color=(255,255,0)
        cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)

    # 変化が大きければOを、そうでなければXを表示
    centroid=None
    if(count>HUMAN_THRESHOLD):
        human_exist=True
    else:
        human_exist=False
        
    # 結果を表示する
    human_move=human_exist-prev_exist
    print(human_exist,human_move)        

    cv2.imshow('frame', frame)
    
    #別の処理を行う
    if(human_move!=0):
        print("書き記す！！！")
        cv2.imwrite("output.jpg", frame)
        
        if(human_move==1):
            message="入室"
        else:
            message="退室"
        
        dt_now = datetime.datetime.now()
        
        payload = {"message" :  "\n"+str(dt_now)+"\n"+str(message)}
        image = r'C:\Users\kokku\output.jpg'
        files = {'imageFile': open(image, 'rb')}
        
        print("送信！")
        res = requests.post(url,params=payload,headers=headers,files=files)
    
    # 現在のフレームを前フレームとして更新する
    prev_frame = gray
    prev_exist=human_exist

    # キー入力を待つ
    key = cv2.waitKey(1) & 0xFF

    # 'q'キーが押された場合は終了する
    if key == ord('q'):
        break
    
    # 少し待つ
    time.sleep(1/FRAME_RATE)

# キャプチャをリリースし、ウィンドウを閉じる
cap.release()
cv2.destroyAllWindows()
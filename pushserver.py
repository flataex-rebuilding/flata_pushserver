import urllib.parse
from flask import Flask
from flask import url_for,render_template,request,jsonify,Response,json,make_response
from functools import wraps
from Database import MySQL 
from Sendfcm import FcmToken


app=Flask(__name__)

#사용자 닉네임과 토큰을 받아 현재 데이터베이스에 존재 유무에 따라 Insert 또는 Update를 처리해주는 함수
def InsertOrUpdate(re1,re2):
    db = MySQL().connect()
    cursor = db.cursor()
    sql = "SELECT * FROM TBL_APP_PUSH_TOKEN WHERE USER_ID = %s"
    cursor.execute(sql,[re1])
    results = cursor.fetchall()
    if not results:
        sql="INSERT INTO TBL_APP_PUSH_TOKEN (USER_ID, USER_TOKEN) VALUES (%s,%s)"
        t=(re1,re2)
        cursor.execute(sql,t)
        db.commit()
    else:
        sql="UPDATE TBL_APP_PUSH_TOKEN SET USER_TOKEN=%s WHERE USER_ID=%s"
        t=(re2,re1)
        cursor.execute(sql,t)
        db.commit()
    return results

#등록되어 있는 사용자에 한해 닉네임을 토큰으로 변환해주는 함수
def nick2token(nick_name):
    token="null"
    db = MySQL().connect()
    cursor = db.cursor()
    sql = "SELECT USER_TOKEN FROM TBL_APP_PUSH_TOKEN WHERE USER_ID = %s"
    cursor.execute(sql,nick_name)
    results = cursor.fetchone()    
    if not results:
        return "none"
    return results['USER_TOKEN']

#서버연결 여부 확인하는 End-Point
@app.route("/")
def intro():
    code="100"
    status="ok"
    reply="connected"
    return jsonify({'code':code,'status':status,'reply':reply,})

#Front-End에서 로그인시 토큰을 업데이트하거나 등록해주는 End-Point
@app.route('/renew-token', methods=['POST'])
def inserttoken():
    #sql = 'SELECT * FROM TBL_APP_PUSH_TOKEN'
    #cursor.execute(sql)
    #results = cursor.fetchall()  
    reply="none"
    re1=""
    re2=""
    status="ok"
    code="100"
    params = json.loads(request.get_data())
    if len(params) == 0:
        status= 'None parameter'
        code="505"
    for key in params.keys():
        if key=="nickNm":
            re1=params[key]
        if key=="fcmToken":
            re2=params[key]
    results=InsertOrUpdate(re1,re2)
    if not re1:
        status="err"
        code="501"
    if not re2:    
        status="err"
        code="502"
    if not params:
        reply = 'None parameter'
        status="err"
        code="505"      
    return jsonify({'code':code,'reply':results,'nickNm':re1,'fcmToken':re2,'status':status,})

#Admin Console에서 마케팅동의 사용자에게 메세지 전송하는 End-Point
@app.route('/send-agree',methods=['POST'])
def SendAgree():
    db = MySQL().connect()
    cursor = db.cursor()
    #전체사용자에게 메세지 전송 처리
    #마케팅 동의 사용자 불러오기
    code="100"
    status="ok"
    ret=0
    reply="none"
    params = json.loads(request.get_data())
    if len(params) == 0:
        code="405"
        status="err"
    for key in params.keys():
        if key=="title":
            title = params[key]
        if key=="contents":
            message = params[key] 
    if not title:
        code="401"
        status="err"
    if not message:
        code="402"
        status="err"
    reply='AllAgreeSended'
    if not params :
        reply= 'None Parameter'
    sql="SELECT NICK_NAME FROM TBL_ACCT_INFO WHERE MRKT_RECV_YN ='Y'"
    cursor.execute(sql)
    results = cursor.fetchall()   
    totTry=0
    for idx in results :        
        ret =  FcmToken.sendFcm(nick2token(idx["NICK_NAME"]),title,message)
        totTry=totTry+ret 
    return jsonify({'code':code,'reply':reply,'contents':message,'title':title,'status':status,'total_count':len(results),'success_count':totTry,})

#Admin Console에서 특정사용자(들)에게 메세지 전송하는 End-Point
@app.route('/send-user',methods=['POST'])
def SendUser():
    db = MySQL().connect()
    cursor = db.cursor()
    reply="none"
    code="100"
    status="ok"
    params = json.loads(request.get_data())
    if len(params) == 0:
        code="305"
        status="err"
    for key in params.keys():
        if key=="title":
            title = params[key]
        if key=="contents":
            message = params[key]
        if key=="users":
            userArr = params[key]
    if not title:
        code="301"
        status="err"
    if not message:
        code="302"
        status="err"
    if not userArr:
        code="303"
        status="err"
    totTry=0
    decodedUser=userArr.split(",")
    for idx in decodedUser:        
        print(nick2token(idx))
        ret = FcmToken.sendFcm(nick2token(idx),title,message)
        totTry=totTry+ret 
    reply = 'UserSended'
    if not params :
        code="305"
        status="err"
    return jsonify({'code':code,'reply':reply,'contents':message,'title':title,'status':status,'total_count':len(userArr),'success_count':totTry,})


#Main Root
#debug port 9001 :python3 pushserver.py
#product port 9002 : flask run  --port=9002
if __name__=="__main__":
    app.run(host='0.0.0.0',port=9001,debug=True)



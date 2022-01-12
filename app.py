from pymongo import MongoClient
import jwt
import datetime
import hashlib
from flask import Flask, render_template, jsonify, request, redirect, url_for
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['UPLOAD_FOLDER'] = "./static/profile_pics"

SECRET_KEY = 'SPARTA'

# client = MongoClient('3.37.129.172', 27017, username="test", password="test")
client = MongoClient('localhost', 27017)
db = client.datespot


@app.route('/')
def home():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])

        review_list = list(db.reviewlist.find({}, {'_id': False}));

        return render_template('reviewList.html', reviewList=review_list)
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))


@app.route('/login')
def login():
    msg = request.args.get("msg")
    return render_template('login.html', msg=msg)

@app.route('/logout')
def logout():
    session.clear
    return render_template('login.html')



@app.route('/register')
def move_register():
    return render_template('register.html')


@app.route('/sign_in', methods=['POST'])
def sign_in():
    # 로그인
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']

    pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    result = db.users.find_one({'username': username_receive, 'password': pw_hash})

    if result is not None:
        payload = {
            'id': username_receive,
            'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)  # 로그인 24시간 유지
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

        return jsonify({'result': 'success', 'token': token})
    # 찾지 못하면
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})


@app.route('/sign_up/save', methods=['POST'])
def sign_up():
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']
    password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    doc = {
        "username": username_receive,  # 아이디
        "password": password_hash,  # 비밀번호
        "profile_name": username_receive,  # 프로필 이름 기본값은 아이디
        "profile_pic": "",  # 프로필 사진 파일 이름
        "profile_pic_real": "profile_pics/profile_placeholder.png",  # 프로필 사진 기본 이미지
        "profile_info": ""  # 프로필 한 마디
    }
    db.users.insert_one(doc)
    return jsonify({'result': 'success'})


@app.route('/sign_up/check_dup', methods=['POST'])
def check_dup():
    username_receive = request.form['username_give']
    exists = bool(db.users.find_one({"username": username_receive}))
    return jsonify({'result': 'success', 'exists': exists})

# ------------------- 원석 작업 추가

## 리뷰 저장
@app.route('/api/review_input', methods=['POST'])
def insertReview():
    placeName = request.form['place_give']
    areaName = request.form['area_give']
    starScore = request.form['star_give']
    content = request.form['content_give']

    image = request.files["image_give"]

    # 이름 겹치지 않게 하기
    # 확장자 가져오기
    extension = image.filename.split('.')[-1];

    # 새로운 이름으로 만들기
    today = datetime.now();
    mytime = today.strftime('%Y-%m-%d-%H-%M-%S');

    # file-년-월-일-시-분-초 형태로 만들어서 이미지이름으로 저장
    filename = f'file-{mytime}';

    # fstring을 사용해서 경로 설정
    save_to = f'static/upload/{filename}.{extension}'
    # 저~~~~~장
    image.save(save_to)

    doc = {
        'place': placeName,
        'area': areaName,
        'score': starScore,
        'content': content,
        'images': f'{filename}.{extension}'
    }

    db.reviewlist.insert_one(doc)

    return jsonify({'msg': '저장 완료!'})
# ----------------------원석작업 끝


# 여기서 부터 지섭 작업

@app.route('/reviewlist')
def abc():
    review_list = list(db.reviewlist.find({}, {'_id': False}));

    return render_template('reviewList.html', reviewList=review_list)
# 이거는 reviewlist 랜더링 해주는 코드 입니다. 원석님



@app.route('/mypage')
def mypage():
    rows = list(db.reviewlist.find({}, {'_id': False}))
    print(rows)
    return render_template("mypage.html", rows = rows)

@app.route('/api/delete_review', methods=['POST'])
def delete_review():
    receive_file = request.form['give_file']
    print(receive_file)
    db.reviewlist.delete_one({'images': receive_file})
    # 리뷰 삭제하기
    return jsonify({'result': 'success', 'msg': '삭제 완료'})










if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)





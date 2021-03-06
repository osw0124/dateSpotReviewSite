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

client = MongoClient('3.37.129.172', 27017, username="test", password="test")
# client = MongoClient('localhost', 27017)
db = client.datespot


@app.route('/')
def home():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])

        user_id = payload['id'];

        review_list = list(db.reviewlist.find({}, {'_id': False}));

        return render_template('reviewList.html', reviewList=review_list, userid=user_id)
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))


@app.route('/login')
def login():
    msg = request.args.get("msg")
    return render_template('login.html', msg=msg)


@app.route('/register')
def move_register():
    return render_template('register.html')

# 로그인
@app.route('/sign_in', methods=['POST'])
def sign_in():
    # 클라이언트에서 보낸 아이디, 패스워드 저장
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']

    # 저장한 패스워드를 SHA256으로 암호화해서 해쉬 값으로 저장 암호화한 패스워드는 복호화가 불가능한듯
    pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    # db에 아이디와 패스워드 해쉬 값 조회
    result = db.users.find_one({'username': username_receive, 'password': pw_hash})

    # 조회 결과가 none이 아니라면(조회결과가 있다는 이야기고 따라서 로그인이 가능하다)
    if result is not None:
        # payload에 아이디와 토큰 유효시간 저장
        payload = {
            'id': username_receive,
            'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)  # 로그인 24시간 유지
        }
        # AWS에서는 .decode('utf-8')이 있어야 에러나 나지 않습니다.
        # 패이로드를 키로 암호화해서 토큰에 저장, 이는 키로 복호화가 가능한 듯, encoding과 encryption은 다르며 JWT는 서명용이라는 글이 있다
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256').decode('utf-8')

        # 성공 결과와 토큰 정보를 클라이언트에 리턴 합니다.
        return jsonify({'result': 'success', 'token': token})
    # 찾지 못하면
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})

# 회원가입
@app.route('/sign_up/save', methods=['POST'])
def sign_up():
    # 클라이언트에게 아이디와 패스워드를 받아 저장
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']
    # 패스워드 해쉬 값을 저장
    password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    # 회원 정보 db에 저장
    doc = {
        "username": username_receive,  # 아이디
        "password": password_hash,  # 비밀번호
    }
    db.users.insert_one(doc)
    # 클라이언트에게 가입 성공 전달
    return jsonify({'result': 'success'})

# 아이디 중복 확인
@app.route('/sign_up/check_dup', methods=['POST'])
def check_dup():
    # 사용하려는 아이디 수신
    username_receive = request.form['username_give']
    # bool 기능으로 중복 확인
    exists = bool(db.users.find_one({"username": username_receive}))
    # 클라이언트에게 중복 여부 전달
    return jsonify({'result': 'success', 'exists': exists})

# ------------------- 원석 작업 추가

## 리뷰 저장

@app.route('/api/review_input', methods=['POST'])
def insertReview():
    token_receive = request.cookies.get('mytoken')
    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
    user_id = payload['id']
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
        'id': user_id,
        'images': f'{filename}.{extension}'
    }

    db.reviewlist.insert_one(doc)

    return jsonify({'msg': '저장 완료!'})
# ----------------------원석작업 끝


# 여기서 부터 지섭 작업

@app.route('/reviewlist')
def abc():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        myid = payload['id']
        review_list = list(db.reviewlist.find({}, {'_id': False}));
        return render_template('reviewList.html', reviewList=review_list,userid=myid)
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))
# 이거는 reviewlist 랜더링 해주는 코드 입니다. 원석님


@app.route('/mypage')
def mypage():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        myid = payload['id']
        print(payload)
        rows = list(db.reviewlist.find({'id':myid}, {'_id': False}))
        print(rows)
        return render_template("mypage.html", rows=rows, myid=myid)

    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))

@app.route('/api/delete_review', methods=['POST'])
def delete_review():
    receive_file = request.form['give_file']
    print(receive_file)
    db.reviewlist.delete_one({'images': receive_file})
    # 리뷰 삭제하기
    return jsonify({'result': 'success', 'msg': '삭제 완료'})




if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)

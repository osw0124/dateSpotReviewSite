$(document).ready(function () {
    bsCustomFileInput.init();
});


const btn = document.querySelector('.addBtn');
const postBox = document.querySelector('.post-box');

btn.addEventListener('click', () => {
    postBox.classList.toggle('active');
});

// 별점 드래그 기능
// target은 input요소자체가 들어온다.
const drawStar = (target) => {
    // .star span 요소에 width값을 조절해서 별이 채워지는 구조이기에
    // input요소의 (value값 * 20)% 로 .star span 요소width값을 설정한다.
    document.querySelector(`.star span`).style.width = `${target.value * 20}%`;
}

// 파일업로드 change이벤트 발생시
const inputImage = document.querySelector('#customFile');
inputImage.addEventListener("change", (e) => {
    setThumbnail(e.target);
});

// 사진 미리보기 기능
function setThumbnail(input) {
    // 인풋 태그에 파일이 있는 경우
    if (input.files && input.files[0]) {

        // Filereader 인스턴스 생성
        const reader = new FileReader();

        // 이미지가 로드가 된 경우
        reader.onload = (e) => {
            const previewImage = document.querySelector('#image_container');
            previewImage.src = e.target.result;
        }
        // reader가 이미지 읽도록 하기
        reader.readAsDataURL(input.files[0]);
    }

}

// 리뷰 저장 함수
function review_Add() {

    // 버튼 클릭시 저장할지말지 예 또는 아니요
    if (confirm('저장 할까요?') === true) {
        let place = $('#place').val();
        // 장소칸이 빈칸일경우 경고창 띄우고 함수 종료
        if (place === '') {
            alert('장소를 입력해주세요');
            return false;
        }
        let area = $("#area").val();
        if (area === '') {
            alert('지역을 입력해주세요');
            return false;
        }
        let starScore = $('#starScore').val();
        if (starScore === '0') {
            alert('점수를 입력해주세요');
            return false;
        }
        let content = $("#content").val();
        if (content === '') {
            alert('내용을 입력해주세요');
            return false;
        }

        let image = $('#customFile')[0].files[0];
        if (image === undefined) {
            alert('사진을 선택해주세요');
            return false;
        }

        // userid 적혀있는 요소
        let useridEltext = document.querySelector('.userid').textContent;
        // 요소에서 text값 잘라서 id 추출
        let user_id = useridEltext.substring(0, useridEltext.length-2);



        // 이미지 업로드를 위한 FormData()
        let form_data = new FormData();

        // 이미지업로드기능이 있으면 form에
        // 나머지값들도 다 넣어줘서 서버에 전달해줘야 한다고 한다.
        form_data.append("image_give", image);
        form_data.append("place_give", place);
        form_data.append("area_give", area);
        form_data.append("star_give", starScore);
        form_data.append("content_give", content);
        form_data.append("id_give", user_id);

        $.ajax({
            type: "POST",
            url: "/api/review_input",
            data: form_data,
            cache: false,
            contentType: false,
            processData: false,
            success: function (response) {
                alert(response["msg"])
                window.location.reload();
            }
        });

    } else {
        return false;
    }


}

// 로그아웃
function logout() {
    $.removeCookie('mytoken');
    alert('로그아웃 완료!');
    window.location.href = '/login';
}









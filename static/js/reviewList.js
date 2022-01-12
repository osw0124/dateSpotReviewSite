    $(document).ready(function () {
        bsCustomFileInput.init();
    });




    //------------- 입력 js -------------

    const btn = document.querySelector('.addBtn');
    const postBox = document.querySelector('.post-box');

    btn.addEventListener('click', () => {
        postBox.classList.toggle('active');
    });


    const drawStar = (target) => {
        document.querySelector(`.star span`).style.width = `${target.value * 10}%`;
    }

    // 파일업로드 change이벤트 발생시
    const inputImage = document.querySelector('#customFile');
    inputImage.addEventListener("change", (e) => {
        setThumbnail(e.target);
    });

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

    function review_Add() {


        let place = $('#place').val();
        if(place === '') {alert('장소를 입력해주세요'); return false;}
        let area = $("#area").val();
        if(area === '') {alert('지역을 입력해주세요'); return false;}
        let starScore = $('#starScore').val();
        if(starScore === '0') {alert('점수를 입력해주세요'); return false;}
        let content = $("#content").val();
        if(content === '') {alert('내용을 입력해주세요'); return false;}

        let image = $('#customFile')[0].files[0];
        if(image === undefined) {alert('사진을 선택해주세요'); return false;}

        let form_data = new FormData();

        form_data.append("image_give", image);
        form_data.append("place_give", place);
        form_data.append("area_give", area);
        form_data.append("star_give", starScore);
        form_data.append("content_give", content);


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

    }



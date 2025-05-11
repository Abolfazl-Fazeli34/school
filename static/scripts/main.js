document.title = 'quran';
setTimeout(function() {
    let messages = document.querySelectorAll(".alert");
    messages.forEach(function(message) {
        message.style.opacity = "0";
        setTimeout(() => message.remove(), 500);
    });
}, 3000);

$(window).scroll(function (){
    let position = $(this).scrollTop();
    if (position >= 150){
        $('.header-top').addClass('header-fiexd-top');
    }else {
        $('.header-top').removeClass('header-fiexd-top');
    }
});
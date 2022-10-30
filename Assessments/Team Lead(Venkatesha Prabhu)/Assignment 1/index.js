var x = document.getElementById('login');
var y = document.getElementById('register');
var z = document.getElementById('btn');

var registerUser;
var loginUser;
function userReg(){
    let username = document.querySelector('#regName').value
    registerUser = Array.from(document.querySelectorAll('#register input'))
    .reduce((acc,input) => ({
        ...acc,[input.placeholder] : input.value
    }),{});
    localStorage.setItem("User_Details",username);
    locationChange();
}

function userLog(){
    let username = document.querySelector('#logName').value
    loginUser = Array.from(document.querySelectorAll('#login input'))
    .reduce((acc,input) => ({
        ...acc,[input.placeholder] : input.value
    }),{});
    localStorage.setItem("User_Details",username);
    locationChange();
}

function locationChange(){
    window.location = "greet.html";
}

function register(){
    x.style.left = "-400px";
    y.style.left = "50px";
    z.style.left = "110px";
}
function login(){
    x.style.left = "50px";
    y.style.left = "450px";
    z.style.left = "0";
}
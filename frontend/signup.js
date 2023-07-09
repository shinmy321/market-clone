const form = document.querySelector("#signup-form");

const checkPassword = () => {
  const formData = new FormData(form);
  const password1 = formData.get("password");
  const password2 = formData.get("password2");
  if (password1 === password2) {
    return true;
  } else false;
};

const handleSubmit = async (event) => {
  event.preventDefault();
  const formData = new FormData(form);
  const sha256Password = sha256(formData.get("password")); //암호화
  formData.set("password", sha256Password);

  const div = document.querySelector("#info");

  if (checkPassword()) {
    const res = await fetch("/signup", {
      method: "post",
      body: formData,
    });
    const data = await res.json();

    if (data === "200") {
      //  div.innerText = "회원가입에 성공했습니다";
      //  div.style.color = "blue";
      alert("회원 가입에 성공했습니다.");
      // 회원가입이 되고 로그인 페이지로 이동 시키기
      window.location.pathname = "/login.html";
    }
  } else {
    div.innerText = "비밀번호가 같지 않습니다";
    div.style.color = "red";
  }
};

form.addEventListener("submit", handleSubmit);

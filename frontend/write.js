const form = document.getElementById("write-form");

const handleSubmitForm = async (event) => {
  event.preventDefault();
  const body = new FormData(form);
  //세계시간 기준으로
  body.append("insertAT", new Date().getTime());
  try {
    const res = await fetch("/items", {
      method: "post",
      body,
    });
    const data = await res.json();
    if (data == "200") window.location.pathname = "/";
  } catch (error) {
    console.error(error);
  }
};

form.addEventListener("submit", handleSubmitForm);

import { ref } from "vue";
import { defineStore } from "pinia";

export const useUserStore = defineStore("user", () => {
  // 初始化时从 localStorage 读取，保证刷新后登录态不丢失
  const username = ref(localStorage.getItem("qny-username") || "");
  const email = ref(localStorage.getItem("qny-email") || "");
  const token = ref(localStorage.getItem("qny-token") || "");

  function setUserInfo({ username: name, email: mail, token: tk }) {
    username.value = name;
    email.value = mail;
    token.value = tk;
    // 同步到 localStorage
    localStorage.setItem("qny-username", name);
    localStorage.setItem("qny-email", mail);
    localStorage.setItem("qny-token", tk);
  }

  function clearUserInfo() {
    username.value = "";
    email.value = "";
    token.value = "";
    localStorage.removeItem("qny-username");
    localStorage.removeItem("qny-email");
    localStorage.removeItem("qny-token");
  }

  return { username, email, token, setUserInfo, clearUserInfo };
});

import { ref } from "vue";
import { defineStore } from "pinia";

export const useUserStore = defineStore("user", () => {
  const username = ref("");
  const email = ref("");
  const token = ref("");

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

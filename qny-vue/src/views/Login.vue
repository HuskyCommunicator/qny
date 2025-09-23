<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";

const router = useRouter();
const isLoginMode = ref(true);
const username = ref("");
const password = ref("");
const confirmPassword = ref("");
const rememberMe = ref(false);

const handleSubmit = () => {
  if (isLoginMode.value) {
    // 登录逻辑
    localStorage.setItem("qny-token", "mock-token");
    router.push("/agent-hall");
  } else {
    // 注册逻辑
    if (password.value !== confirmPassword.value) {
      alert("两次密码输入不一致");
      return;
    }
    // 模拟注册成功自动登录
    localStorage.setItem("qny-token", "mock-token");
    router.push("/agent-hall");
  }
};

const toggleMode = () => {
  isLoginMode.value = !isLoginMode.value;
  username.value = "";
  password.value = "";
  confirmPassword.value = "";
};
</script>

<template>
  <div class="login-container">
    <div class="login-box">
      <h1 class="login-title">{{ isLoginMode ? "欢迎登录" : "用户注册" }}</h1>

      <form @submit.prevent="handleSubmit" class="login-form">
        <div class="form-group">
          <label for="username">用户名</label>
          <input
            id="username"
            v-model="username"
            type="text"
            :placeholder="isLoginMode ? '请输入用户名' : '请输入注册用户名'"
          />
        </div>

        <div class="form-group">
          <label for="password">密码</label>
          <input
            id="password"
            v-model="password"
            type="password"
            placeholder="请输入密码"
          />
        </div>

        <div class="form-group" v-if="!isLoginMode">
          <label for="confirmPassword">确认密码</label>
          <input
            id="confirmPassword"
            v-model="confirmPassword"
            type="password"
            placeholder="请再次输入密码"
          />
        </div>

        <div class="remember-me" v-if="isLoginMode">
          <input id="remember" v-model="rememberMe" type="checkbox" />
          <label for="remember">记住我</label>
        </div>

        <button type="submit" class="login-btn">
          {{ isLoginMode ? "登 录" : "注 册" }}
        </button>
      </form>

      <div class="login-footer">
        <a href="#" @click.prevent="toggleMode">
          {{ isLoginMode ? "注册账号" : "已有账号？登录" }}
        </a>
        <a href="#" v-if="isLoginMode">忘记密码?</a>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  padding: 20px;
}

.login-box {
  background: white;
  padding: 30px;
  border-radius: 12px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  width: 25%;
  max-width: 450px;
}

.login-title {
  text-align: center;
  color: #333;
  font-size: 20px;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;

  label {
    color: #555;
    font-size: 14px;
  }

  input {
    padding: 12px 15px;
    border: 1px solid #ddd;
    border-radius: 6px;
    font-size: 14px;
    transition: border-color 0.3s;

    &:focus {
      outline: none;
      border-color: #4a89dc;
    }
  }
}

.remember-me {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 10px 0;

  label {
    color: #555;
    font-size: 14px;
    cursor: pointer;
  }
}

.login-btn {
  background: #4a89dc;
  color: white;
  border: none;
  padding: 12px;
  border-radius: 6px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.3s;

  &:hover {
    background: #3a70c2;
  }
}

.login-footer {
  display: flex;
  justify-content: space-between;
  margin-top: 20px;
  font-size: 14px;

  a {
    color: #4a89dc;
    text-decoration: none;

    &:hover {
      text-decoration: underline;
    }
  }
}
</style>

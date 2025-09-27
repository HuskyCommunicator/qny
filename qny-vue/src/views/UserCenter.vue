<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { getMeInfoAPI } from "../api/user";

const router = useRouter();
const user = ref({
  username: "",
  full_name: "",
  email: "",
  avatar: "https://placekitten.com/120/120",
});

async function fetchUserInfo() {
  try {
    const res = await getMeInfoAPI();
    user.value.username = res.username || "";
    user.value.full_name = res.full_name || "暂无";
    user.value.email = res.email || "";
    // 可扩展头像字段
  } catch (e) {
    // 可做错误处理
  }
}

function logout() {
  router.push("/login");
}

onMounted(() => {
  fetchUserInfo();
});
</script>

<template>
  <div class="user-center-bg">
    <div class="user-center-card">
      <div class="user-avatar-box">
        <img :src="user.avatar" class="user-avatar" />
      </div>
      <div class="user-info">
        <div class="user-name">用户名：{{ user.username }}</div>
        <div class="user-fullname">全名：{{ user.full_name || "未填写" }}</div>
        <div class="user-email">邮箱：{{ user.email }}</div>
      </div>
      <div class="user-actions">
        <button class="logout-btn" @click="logout">退出登录</button>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.user-center-bg {
  min-height: 100vh;
  background: linear-gradient(135deg, #f8fafc 0%, #e0e7ff 100%);
  display: flex;
  align-items: center;
  justify-content: center;
}
.user-center-card {
  background: #fff;
  border-radius: 22px;
  box-shadow: 0 8px 32px rgba(60, 72, 100, 0.1);
  padding: 48px 38px 36px 38px;
  min-width: 340px;
  max-width: 95vw;
  display: flex;
  flex-direction: column;
  align-items: center;
}
.user-avatar-box {
  margin-bottom: 18px;
}
.user-avatar {
  width: 110px;
  height: 110px;
  border-radius: 50%;
  border: 4px solid #e0e7ff;
  box-shadow: 0 2px 12px rgba(60, 72, 100, 0.1);
  background: #f8fafc;
}
.user-info {
  text-align: center;
  margin-bottom: 28px;
}
.user-name {
  font-size: 1.5rem;
  font-weight: 700;
  color: #3b3b5c;
  margin-bottom: 6px;
}
.user-role {
  font-size: 1.08rem;
  color: #6366f1;
  margin-bottom: 6px;
}
.user-email {
  color: #6b7280;
  font-size: 1rem;
  margin-bottom: 8px;
}
.user-desc {
  color: #64748b;
  font-size: 1rem;
  margin-bottom: 2px;
}
.user-actions {
  display: flex;
  gap: 18px;
  justify-content: center;
}
.user-actions button {
  border: none;
  border-radius: 20px;
  padding: 10px 28px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(99, 102, 241, 0.1);
  transition:
    background 0.2s,
    box-shadow 0.2s;
}
.logout-btn {
  background: linear-gradient(90deg, #f87171 0%, #fbbf24 100%);
  color: #fff;
}
.logout-btn:hover {
  background: linear-gradient(90deg, #fbbf24 0%, #f87171 100%);
  box-shadow: 0 4px 16px rgba(251, 191, 36, 0.18);
}
.edit-btn {
  background: linear-gradient(90deg, #6366f1 0%, #818cf8 100%);
  color: #fff;
}
.edit-btn:hover {
  background: linear-gradient(90deg, #818cf8 0%, #6366f1 100%);
  box-shadow: 0 4px 16px rgba(99, 102, 241, 0.18);
}
</style>

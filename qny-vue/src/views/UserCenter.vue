<script setup>
import { ElAvatar } from "element-plus";
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { getMeInfoAPI } from "../api/user";

const router = useRouter();
const user = ref({
  username: "",
  full_name: "",
  email: "",
  avatar: "https://cube.elemecdn.com/9/c2/f0ee8a3c7c9638a54940382568c9dpng.png",
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
        <el-avatar
          :size="110"
          src="https://cube.elemecdn.com/9/c2/f0ee8a3c7c9638a54940382568c9dpng.png"
        />
      </div>
      <div class="user-info">
        <div class="user-fullname">
          <span class="label">昵称：</span>
          <span class="value">{{ user.full_name || "未填写" }}</span>
        </div>
        <div class="user-name">
          <span class="label">用户名：</span>
          <span class="value">{{ user.username }}</span>
        </div>
        <div class="user-email">
          <span class="label">邮箱：</span>
          <span class="value">{{ user.email }}</span>
        </div>
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
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  margin-bottom: 28px;
  width: 100%;
  max-width: 320px;
  margin: 0 auto 28px auto;
}
.user-fullname,
.user-name,
.user-email {
  justify-content: center;
}
.user-fullname,
.user-name,
.user-email {
  display: flex;
  align-items: center;
  font-size: 1.18rem;
  color: #3b3b5c;
  margin-bottom: 12px;
  font-weight: 500;
  background: #f8fafc;
  border-radius: 8px;
  padding: 8px 16px;
  box-shadow: 0 2px 8px rgba(60, 72, 100, 0.04);
}
.label {
  width: 80px;
  color: #6366f1;
  font-weight: 700;
  font-size: 1.08rem;
  margin-right: 12px;
  text-align: right;
}
.value {
  flex: 1;
  font-size: 1.18rem;
  color: #22223b;
  font-weight: 500;
  word-break: break-all;
}
// ...existing code...
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

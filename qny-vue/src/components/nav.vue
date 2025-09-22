<script setup>
const logout = () => {
  console.log("Logout clicked");
  // Add actual logout logic here
};
</script>

<template>
  <nav class="navbar">
    <div class="navbar-left">
      <span class="system-name">标题</span>
    </div>

    <div class="navbar-right">
      <div class="user-info-container">
        <div class="user-info">
          <span>个人信息</span>
        </div>
        <div class="dropdown-menu">
          <div class="dropdown-item">个人中心</div>
          <div class="dropdown-item" @click="logout">退出登录</div>
        </div>
      </div>
    </div>
  </nav>
</template>

<style lang="scss" scoped>
.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  height: 60px;
  background-color: #545c64;
  color: white;
  position: relative;
  z-index: 99;

  .navbar-left {
    .system-name {
      font-size: 18px;
      font-weight: bold;
    }
  }

  .navbar-right {
    position: relative;

    .user-info-container {
      position: relative;
      cursor: pointer;
      padding: 10px 0;

      &:hover {
        background-color: rgba(255, 255, 255, 0.1);

        .dropdown-menu {
          display: block;
        }
      }
    }

    .user-info {
      position: relative;
    }

    .dropdown-menu {
      display: none;
      position: absolute;
      right: 0;
      top: 100%;
      background-color: white;
      color: #333;
      border-radius: 4px;
      box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
      min-width: 120px;
      z-index: 100;
      margin-top: -5px;
      padding-top: 5px;

      .dropdown-item {
        padding: 10px 15px;
        cursor: pointer;

        &:hover {
          background-color: #f5f5f5;
        }

        &:first-child {
          border-bottom: 1px solid #eee;
        }
      }
    }
  }
}
</style>

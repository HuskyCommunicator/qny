// const baseURL = "http://116.62.231.58:8000";
const baseURL = "http://localhost:8000";
const API = {
  // 用户相关接口
  USER: {
    INFO: baseURL + "/user/info", // 获取用户信息
    UPDATE: baseURL + "/user/update", // 更新用户信息
    REGISTER: baseURL + "/auth/register", // 注册
    LOGIN: baseURL + "/auth/login", // 登录
    // 可根据实际需求继续添加
  },
};

export default API;

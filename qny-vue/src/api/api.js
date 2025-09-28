const baseURL = "http://116.62.231.58:8000";
// const baseURL = "http://localhost:8000";
const API = {
  // 用户相关接口
  USER: {
    INFO: baseURL + "/user/info", // 获取用户信息
    UPDATE: baseURL + "/user/update", // 更新用户信息
    REGISTER: baseURL + "/auth/register", // 注册
    LOGIN: baseURL + "/auth/login", // 登录
    ME: baseURL + "/me", // 获取个人信息
  },
  AGENT: {
    MY_AGENTS: baseURL + "/me/agents", // 获取我的智能体列表
    AGENT_LIST: baseURL + "/role/list", // 获取智能体列表
    AGENT_ADD: baseURL + "/role/my/add", // 创建智能体
  },
};

export default API;
1;

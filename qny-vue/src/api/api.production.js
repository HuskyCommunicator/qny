// 生产环境 API 配置示例
// 请根据你的实际部署情况修改以下地址

// 方案1：如果你的后端部署在同一台服务器的不同端口
// const baseURL = "http://你的服务器IP:8000";

// 方案2：如果你的后端部署在不同服务器
// const baseURL = "http://后端服务器IP:8000";

// 方案3：如果使用域名和HTTPS
// const baseURL = "https://api.你的域名.com";

// 方案4：如果使用Nginx代理（推荐）
const baseURL = "/api"; // 这样会通过Nginx代理到后端

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
    CREATE_FROM_TEMPLATE: baseURL + "/role/create-from-template", // 从模板创建角色实例
  },
};

export default API;



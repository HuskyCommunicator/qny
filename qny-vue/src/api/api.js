const baseURL = "/compare/v1";
const API = {
  // 通用接口
  COMMON: {
    LOGIN: baseURL + "/user/login", // 用户登录
    REGISTER: baseURL + "/user/register", // 用户注册
    PROFILE: baseURL + "/user/profile", // 用户资料
    UPDATE_PROFILE: baseURL + "/user/profile", // 更新用户资料
  },

  // AI角色接口
  AGENTS: {
    PUBLIC: baseURL + "/agents/public", // 获取公共AI角色
    DETAIL: baseURL + "/agents/", // 获取AI角色详情 {id}
    MY_AGENTS: baseURL + "/agents/my", // 获取我的AI角色
    CREATE: baseURL + "/agents", // 创建AI角色
    UPDATE: baseURL + "/agents/", // 更新AI角色 {id}
    DELETE: baseURL + "/agents/", // 删除AI角色 {id}
  },

  // 聊天接口
  CHAT: {
    SESSIONS: baseURL + "/chat/sessions", // 获取会话列表
    CREATE_SESSION: baseURL + "/chat/sessions", // 创建会话
    MESSAGES: baseURL + "/chat/sessions/", // 获取会话消息 {id}/messages
    SEND_MESSAGE: baseURL + "/chat/messages", // 发送消息
  },
};

export default API;

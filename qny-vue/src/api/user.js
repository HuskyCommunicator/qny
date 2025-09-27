import request from "./axios";
import API from "./api";

export const login = (data) => {
  const formData = new FormData();
  for (const key in data) {
    formData.append(key, data[key]);
  }
  return request({
    url: API.USER.LOGIN,
    method: "post",
    data: formData,
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });
};

export const register = (data) => {
  return request({
    url: API.COMMON.REGISTER,
    method: "post",
    data,
  });
};
export const getMyAgents = () => {
  return request({
    url: API.USER.AGENTS,
    method: "get",
  });
};

export const getChatHistory = (params) => {
  return request({
    url: API.USER.CHAT_HISTORY,
    method: "get",
    params,
  });
};

export const getMySessions = (params) => {
  return request({
    url: API.USER.SESSIONS,
    method: "get",
    params,
  });
};

export const getChatMessages = (sessionId, params) => {
  return request({
    url: API.USER.SESSION_MESSAGES.replace(":sessionId", sessionId),
    method: "get",
    params,
  });
};

export const deleteSession = (sessionId) => {
  return request({
    url: API.USER.DELETE_SESSION.replace(":sessionId", sessionId),
    method: "delete",
  });
};

export const clearChatHistory = (params) => {
  return request({
    url: API.USER.CHAT_HISTORY,
    method: "delete",
    params,
  });
};

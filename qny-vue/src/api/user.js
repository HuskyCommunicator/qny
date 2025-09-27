import request from "./axios";
import API from "./api";

export const loginAPI = (data) => {
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

export const registerAPI = (data) => {
  return request({
    url: API.USER.REGISTER,
    method: "post",
    data,
  });
};
export const getMyAgentsAPI = () => {
  return request({
    url: API.USER.AGENTS,
    method: "get",
  });
};

export const getChatHistoryAPI = (params) => {
  return request({
    url: API.USER.CHAT_HISTORY,
    method: "get",
    params,
  });
};

export const getMySessionsAPI = (params) => {
  return request({
    url: API.USER.SESSIONS,
    method: "get",
    params,
  });
};

export const getChatMessagesAPI = (sessionId, params) => {
  return request({
    url: API.USER.SESSION_MESSAGES.replace(":sessionId", sessionId),
    method: "get",
    params,
  });
};

export const deleteSessionAPI = (sessionId) => {
  return request({
    url: API.USER.DELETE_SESSION.replace(":sessionId", sessionId),
    method: "delete",
  });
};

export const clearChatHistoryAPI = (params) => {
  return request({
    url: API.USER.CHAT_HISTORY,
    method: "delete",
    params,
  });
};

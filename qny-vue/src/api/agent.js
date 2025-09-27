import request from "./axios";
import API from "./api";

// 获取我的智能体列表
export const getMyAgentsAPI = () => {
  return request({
    url: API.AGENT.MY_AGENTS,
    method: "get",
  });
};
export const getAgentListAPI = () => {
  return request({
    url: API.AGENT.AGENT_LIST,
    method: "get",
  });
};
// 可在此文件继续扩展其他智能体相关接口

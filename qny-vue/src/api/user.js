import request from './axios'

export const getMyAgents = () => {
  return request({
    url: '/me/agents',
    method: 'get'
  })
}

export const getChatHistory = (params) => {
  return request({
    url: '/me/chat-history',
    method: 'get',
    params
  })
}

export const getMySessions = (params) => {
  return request({
    url: '/me/sessions',
    method: 'get',
    params
  })
}

export const getChatMessages = (sessionId, params) => {
  return request({
    url: `/me/session/${sessionId}/messages`,
    method: 'get',
    params
  })
}

export const deleteSession = (sessionId) => {
  return request({
    url: `/me/session/${sessionId}`,
    method: 'delete'
  })
}

export const clearChatHistory = (params) => {
  return request({
    url: '/me/chat-history',
    method: 'delete',
    params
  })
}
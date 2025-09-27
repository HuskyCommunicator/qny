import request from './axios'

export const chatText = (data) => {
  return request({
    url: '/chat/text',
    method: 'post',
    data
  })
}

export const createSession = (data) => {
  return request({
    url: '/chat/session',
    method: 'post',
    data
  })
}

export const getSessions = (params) => {
  return request({
    url: '/chat/sessions',
    method: 'get',
    params
  })
}

export const getSessionMessages = (sessionId, params) => {
  return request({
    url: `/chat/session/${sessionId}/messages`,
    method: 'get',
    params
  })
}

export const deleteChatSession = (sessionId) => {
  return request({
    url: `/chat/session/${sessionId}`,
    method: 'delete'
  })
}

export const updateSessionTitle = (sessionId, title) => {
  return request({
    url: `/chat/session/${sessionId}/title`,
    method: 'put',
    data: { title }
  })
}

export const speechToText = (file) => {
  const formData = new FormData()
  formData.append('file', file)

  return request({
    url: '/chat/stt',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

export const textToSpeech = (data) => {
  return request({
    url: '/chat/tts',
    method: 'post',
    data
  })
}
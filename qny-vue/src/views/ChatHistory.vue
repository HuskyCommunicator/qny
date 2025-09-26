<template>
  <div class="chat-history-page">
    <div class="chat-history-topbar">
      <div class="history-scroll">
        <div
          v-for="session in sessions"
          :key="session.session_id"
          class="agent-item"
          :class="{ active: selectedSession?.session_id === session.session_id }"
          @click="selectSession(session)"
        >
          <img :src="session.role?.avatar_url || '/default-avatar.png'" class="agent-avatar" />
          <div class="agent-info">
            <div class="agent-name">{{ session.title || '新对话' }}</div>
            <div class="last-msg">{{ getLastMessage(session) }}</div>
            <div class="msg-time">{{ formatTime(session.last_message_at || session.created_at) }}</div>
          </div>
          <div class="session-actions">
            <el-button
              type="danger"
              size="small"
              circle
              @click.stop="deleteSession(session.session_id)"
            >
              <el-icon><Delete /></el-icon>
            </el-button>
          </div>
        </div>
      </div>
    </div>
    <main class="chat-history-main">
      <div v-if="loading" class="loading">
        <el-icon class="loading-icon"><Loading /></el-icon>
        <span>加载中...</span>
      </div>

      <div v-else-if="!selectedSession" class="empty-tip">
        <span>请选择上方的对话查看聊天记录</span>
      </div>

      <div v-else class="chat-messages">
        <div class="messages-header">
          <h3>{{ selectedSession.title || '对话记录' }}</h3>
          <div class="session-info">
            <span>{{ selectedSession.message_count }} 条消息</span>
            <span>{{ formatTime(selectedSession.created_at) }}</span>
          </div>
        </div>

        <div class="messages-container">
          <div
            v-for="message in messages"
            :key="message.id"
            class="message-item"
            :class="{ 'user-message': message.is_user_message, 'assistant-message': !message.is_user_message }"
          >
            <div class="message-avatar">
              <img :src="message.is_user_message ? '/user-avatar.png' : (selectedSession.role?.avatar_url || '/default-avatar.png')" />
            </div>
            <div class="message-content">
              <div class="message-text">{{ message.content }}</div>
              <div class="message-time">{{ formatTime(message.created_at) }}</div>
            </div>
          </div>
        </div>

        <div v-if="messages.length === 0" class="no-messages">
          <span>暂无消息记录</span>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Delete, Loading } from '@element-plus/icons-vue'
import { getMyAgents, getChatHistory, getMySessions, deleteSession as deleteSessionApi } from '@/api/user'
import { getChatMessages } from '@/api/chat'

const sessions = ref([])
const selectedSession = ref(null)
const messages = ref([])
const loading = ref(false)

// 获取会话列表
const fetchSessions = async () => {
  try {
    loading.value = true
    const response = await getMySessions()
    sessions.value = response.data || []
  } catch (error) {
    console.error('获取会话列表失败:', error)
    ElMessage.error('获取会话列表失败')
  } finally {
    loading.value = false
  }
}

// 选择会话
const selectSession = async (session) => {
  selectedSession.value = session
  await fetchMessages(session.session_id)
}

// 获取会话消息
const fetchMessages = async (sessionId) => {
  try {
    loading.value = true
    const response = await getChatMessages(sessionId)
    messages.value = response.data || []
  } catch (error) {
    console.error('获取消息失败:', error)
    ElMessage.error('获取消息失败')
  } finally {
    loading.value = false
  }
}

// 删除会话
const deleteSession = async (sessionId) => {
  try {
    await ElMessageBox.confirm('确定要删除这个对话吗？删除后无法恢复。', '确认删除', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await deleteSessionApi(sessionId)
    ElMessage.success('删除成功')

    // 如果删除的是当前选中的会话，清空选择
    if (selectedSession.value?.session_id === sessionId) {
      selectedSession.value = null
      messages.value = []
    }

    // 重新获取会话列表
    await fetchSessions()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除会话失败:', error)
      ElMessage.error('删除会话失败')
    }
  }
}

// 获取最后一条消息
const getLastMessage = (session) => {
  if (!session.last_message_at) return '开始对话'
  return '继续对话...'
}

// 格式化时间
const formatTime = (timeString) => {
  if (!timeString) return ''
  const date = new Date(timeString)
  const now = new Date()
  const diff = now - date

  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
  if (diff < 604800000) return `${Math.floor(diff / 86400000)}天前`

  return date.toLocaleDateString()
}

onMounted(() => {
  fetchSessions()
})
</script>

<style lang="scss" scoped>
.chat-history-page {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: linear-gradient(135deg, #f8fafc 0%, #e0e7ff 100%);
}
.chat-history-topbar {
  width: 100%;
  background: #fff;
  box-shadow: 0 2px 12px rgba(60, 72, 100, 0.06);
  padding: 18px 0 10px 0;
  border-bottom-left-radius: 24px;
  border-bottom-right-radius: 24px;
}
.history-scroll {
  display: flex;
  gap: 24px;
  overflow-x: auto;
  padding: 0 32px;
  scrollbar-width: thin;
  scrollbar-color: #e0e7ff #fff;
}
.agent-item {
  display: flex;
  align-items: center;
  min-width: 280px;
  background: #f8fafc;
  border-radius: 16px;
  padding: 12px 18px;
  margin-bottom: 2px;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(60, 72, 100, 0.06);
  border: 2px solid transparent;
  transition:
    background 0.18s,
    border 0.18s;

  &:hover {
    background: #e0e7ff;
    border: 2px solid #6366f1;
  }

  &.active {
    background: #e0e7ff;
    border: 2px solid #6366f1;
  }
}
.agent-avatar {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  margin-right: 14px;
  border: 2px solid #e0e7ff;
  background: #f8fafc;
  object-fit: cover;
}
.agent-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
}
.agent-name {
  font-size: 1.08rem;
  font-weight: 600;
  color: #2d3756;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.last-msg {
  color: #6b7280;
  font-size: 0.9rem;
  margin-top: 2px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.msg-time {
  color: #9ca3af;
  font-size: 0.8rem;
  margin-top: 2px;
}
.session-actions {
  margin-left: 8px;
}
.chat-history-main {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 32px;
}
.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  color: #6b7280;
}
.loading-icon {
  font-size: 2rem;
  animation: spin 1s linear infinite;
}
@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
.empty-tip {
  color: #a1a1aa;
  font-size: 1.2rem;
  background: #fff;
  padding: 32px 48px;
  border-radius: 18px;
  box-shadow: 0 2px 12px rgba(60, 72, 100, 0.06);
}
.chat-messages {
  width: 100%;
  max-width: 800px;
  height: 100%;
  background: #fff;
  border-radius: 18px;
  box-shadow: 0 2px 12px rgba(60, 72, 100, 0.06);
  display: flex;
  flex-direction: column;
}
.messages-header {
  padding: 24px;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  justify-content: space-between;
  align-items: center;

  h3 {
    margin: 0;
    color: #2d3756;
    font-size: 1.2rem;
  }
}
.session-info {
  display: flex;
  gap: 16px;
  color: #6b7280;
  font-size: 0.9rem;
}
.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.message-item {
  display: flex;
  gap: 12px;
  max-width: 80%;

  &.user-message {
    align-self: flex-end;
    flex-direction: row-reverse;

    .message-content {
      background: #6366f1;
      color: white;
    }
  }

  &.assistant-message {
    align-self: flex-start;
  }
}
.message-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  flex-shrink: 0;

  img {
    width: 100%;
    height: 100%;
    border-radius: 50%;
    object-fit: cover;
  }
}
.message-content {
  background: #f3f4f6;
  padding: 12px 16px;
  border-radius: 12px;
  max-width: 100%;
}
.message-text {
  word-wrap: break-word;
  line-height: 1.5;
  margin-bottom: 4px;
}
.message-time {
  font-size: 0.75rem;
  opacity: 0.7;
}
.no-messages {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 200px;
  color: #9ca3af;
  font-size: 1rem;
}
</style>

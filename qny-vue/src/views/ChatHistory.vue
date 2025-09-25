<template>
  <div class="chat-history-page">
    <div class="chat-history-topbar">
      <div class="history-scroll">
        <div v-for="agent in agents" :key="agent.id" class="agent-item">
          <img :src="agent.avatar" class="agent-avatar" />
          <div class="agent-info">
            <div class="agent-name">{{ agent.name }}</div>
            <div class="last-msg">{{ agent.lastMsg }}</div>
          </div>
        </div>
      </div>
    </div>
    <main class="chat-history-main">
      <div class="empty-tip">
        <span>请选择上方的智能体查看聊天记录</span>
      </div>
    </main>
  </div>
</template>

<script setup>
const agents = [
  {
    id: 1,
    name: "AI助手",
    avatar: "https://placekitten.com/100/100",
    lastMsg: "你好，有什么可以帮您？",
  },
  {
    id: 2,
    name: "编程专家",
    avatar: "https://placekitten.com/101/101",
    lastMsg: "请提供你的代码片段。",
  },
  {
    id: 3,
    name: "语言翻译",
    avatar: "https://placekitten.com/102/102",
    lastMsg: "Translation completed!",
  },
  {
    id: 4,
    name: "心理咨询",
    avatar: "https://placekitten.com/103/103",
    lastMsg: "保持积极心态很重要。",
  },
];
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
  min-width: 220px;
  background: #f8fafc;
  border-radius: 16px;
  padding: 10px 18px;
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
}
.agent-avatar {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  margin-right: 14px;
  border: 2px solid #e0e7ff;
  background: #f8fafc;
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
}
.last-msg {
  color: #6b7280;
  font-size: 0.95rem;
  margin-top: 3px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.chat-history-main {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}
.empty-tip {
  color: #a1a1aa;
  font-size: 1.2rem;
  background: #fff;
  padding: 32px 48px;
  border-radius: 18px;
  box-shadow: 0 2px 12px rgba(60, 72, 100, 0.06);
}
</style>

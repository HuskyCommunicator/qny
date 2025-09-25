<script setup>
import { useRoute } from "vue-router";
import { ref, onMounted } from "vue";

const route = useRoute();
const agentId = route.query.agent;
const agents = [
  { id: 1, name: "AI助手", avatar: "https://placekitten.com/100/100" },
  { id: 2, name: "编程专家", avatar: "https://placekitten.com/101/101" },
  { id: 3, name: "语言翻译", avatar: "https://placekitten.com/102/102" },
  { id: 4, name: "心理咨询", avatar: "https://placekitten.com/103/103" },
];
const agent = agents.find((a) => a.id == agentId) || agents[0];

const messages = ref([
  { from: "agent", text: "你好，我是" + agent.name + "，很高兴为你服务！" },
]);
const input = ref("");

function send() {
  if (!input.value.trim()) return;
  messages.value.push({ from: "user", text: input.value });
  setTimeout(() => {
    messages.value.push({ from: "agent", text: "收到：" + input.value });
  }, 600);
  input.value = "";
}
</script>

<template>
  <div class="chat-page">
    <div class="chat-header">
      <img :src="agent.avatar" class="chat-avatar" />
      <span class="chat-title">{{ agent.name }}</span>
    </div>
    <div class="chat-body" ref="chatBody">
      <div
        v-for="(msg, i) in messages"
        :key="i"
        :class="['chat-msg', msg.from]"
      >
        <div class="msg-bubble">
          <span>{{ msg.text }}</span>
        </div>
      </div>
    </div>
    <div class="chat-input-bar">
      <input v-model="input" @keyup.enter="send" placeholder="请输入消息..." />
      <button @click="send">发送</button>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.chat-page {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: linear-gradient(135deg, #f8fafc 0%, #e0e7ff 100%);
}
.chat-header {
  display: flex;
  align-items: center;
  padding: 18px 28px;
  background: #fff;
  box-shadow: 0 2px 12px rgba(60, 72, 100, 0.06);
  border-bottom-left-radius: 18px;
  border-bottom-right-radius: 18px;
}
.chat-avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  margin-right: 16px;
  border: 3px solid #e0e7ff;
  background: #f8fafc;
}
.chat-title {
  font-size: 1.3rem;
  font-weight: 600;
  color: #3b3b5c;
}
.chat-body {
  flex: 1;
  padding: 32px 0 24px 0;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 18px;
}
.chat-msg {
  display: flex;
  align-items: flex-end;
  padding: 0 32px;
}
.chat-msg.agent {
  justify-content: flex-start;
}
.chat-msg.user {
  justify-content: flex-end;
}
.msg-bubble {
  max-width: 60%;
  padding: 12px 18px;
  border-radius: 18px;
  font-size: 1rem;
  background: #fff;
  color: #2d3756;
  box-shadow: 0 2px 8px rgba(60, 72, 100, 0.08);
  margin-bottom: 2px;
}
.chat-msg.user .msg-bubble {
  background: linear-gradient(90deg, #6366f1 0%, #818cf8 100%);
  color: #fff;
  box-shadow: 0 2px 12px rgba(99, 102, 241, 0.1);
}
.chat-input-bar {
  display: flex;
  align-items: center;
  padding: 18px 32px;
  background: #fff;
  border-top-left-radius: 18px;
  border-top-right-radius: 18px;
  box-shadow: 0 -2px 12px rgba(60, 72, 100, 0.06);
}
.chat-input-bar input {
  flex: 1;
  border: none;
  border-radius: 20px;
  padding: 10px 18px;
  font-size: 1rem;
  background: #f0f4ff;
  margin-right: 16px;
  outline: none;
  box-shadow: 0 1px 4px rgba(60, 72, 100, 0.04);
  transition: box-shadow 0.2s;
}
.chat-input-bar input:focus {
  box-shadow: 0 2px 8px rgba(99, 102, 241, 0.1);
}
.chat-input-bar button {
  background: linear-gradient(90deg, #6366f1 0%, #818cf8 100%);
  color: #fff;
  border: none;
  border-radius: 20px;
  padding: 8px 28px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(99, 102, 241, 0.1);
  transition:
    background 0.2s,
    box-shadow 0.2s;
}
.chat-input-bar button:hover {
  background: linear-gradient(90deg, #818cf8 0%, #6366f1 100%);
  box-shadow: 0 4px 16px rgba(99, 102, 241, 0.18);
}
</style>

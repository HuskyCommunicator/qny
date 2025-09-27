<script setup>
import { ElIcon, ElLoading } from "element-plus";
import { Microphone } from "@element-plus/icons-vue";
import { ref, onMounted, nextTick } from "vue";
import { useRoute } from "vue-router";
import { sendChatTextAPI } from "../api/agent";
const recognizing = ref(false);
const showVoiceModal = ref(false);
let recognition;

if (window.SpeechRecognition || window.webkitSpeechRecognition) {
  const SpeechRecognition =
    window.SpeechRecognition || window.webkitSpeechRecognition;
  recognition = new SpeechRecognition();
  recognition.lang = "zh-CN";
  recognition.continuous = false;
  recognition.interimResults = false;

  recognition.onstart = () => {
    recognizing.value = true;
    showVoiceModal.value = true;
  };
  recognition.onend = () => {
    recognizing.value = false;
    showVoiceModal.value = false;
  };
  recognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript;
    input.value = transcript;
    recognizing.value = false;
    showVoiceModal.value = false;
  };
}

function toggleVoice() {
  if (!recognition) return;
  if (!recognizing.value) {
    recognition.start();
  } else {
    recognition.stop();
  }
}
const route = useRoute();
// 入口传递的角色信息
const agent = {
  name: route.query.display_name || route.query.name || "AI助手",
  avatar:
    route.query.avatar_url ||
    route.query.avatar ||
    "https://placekitten.com/100/100",
  description: route.query.description || "",
  personality: route.query.personality || "",
};

const messages = ref([
  {
    from: "agent",
    text: `你好，我是${agent.name}${agent.description ? "，" + agent.description : ""}。很高兴为你服务！`,
  },
]);
const input = ref("");

function send() {
  if (!input.value.trim()) return;
  const userMsg = input.value;
  messages.value.push({ from: "user", text: userMsg });
  // 构造会话id（简单用时间戳）
  const conversation_id = String(Date.now());
  sendChatTextAPI({
    role: "harry_potter",
    content: userMsg,
    conversation_id,
  })
    .then((res) => {
      // 后端返回 { content: "xxx" }
      setTimeout(() => {
        messages.value.push({ from: "agent", text: res.content || "(无回复)" });
      }, 3000); // 增加等待时间
    })
    .catch(() => {
      setTimeout(() => {
        messages.value.push({ from: "agent", text: "对话失败，请重试。" });
      }, 5000);
    });
  input.value = "";
}
</script>

<template>
  <div v-if="showVoiceModal" class="voice-modal">
    <div class="voice-modal-content">
      <el-icon style="font-size: 2.8rem; color: #6366f1; margin-bottom: 12px">
        <Microphone />
      </el-icon>
      <el-loading
        :loading="true"
        text="语音识别中..."
        style="margin-bottom: 12px"
      />
      <div class="voice-modal-text">正在识别语音...</div>
    </div>
  </div>
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
      <button
        @click="toggleVoice"
        class="voice-btn"
        :class="{ active: recognizing }"
        style="cursor: pointer"
      >
        <el-icon><Microphone /></el-icon>
      </button>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.voice-modal {
  position: fixed;
  left: 0;
  top: 0;
  width: 100vw;
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  background: rgba(60, 72, 100, 0.08);
  pointer-events: none;
}
.voice-modal-content {
  max-width: 340px;
  max-height: 260px;
  width: 90vw;
  height: auto;
  pointer-events: auto;
}
.voice-modal-content {
  background: rgba(255, 255, 255, 0.85);
  border-radius: 18px;
  box-shadow: 0 4px 32px rgba(60, 72, 100, 0.12);
  padding: 38px 48px 32px 48px;
  display: flex;
  flex-direction: column;
  align-items: center;
}
.voice-modal-text {
  font-size: 1.18rem;
  color: #6366f1;
  font-weight: 600;
  letter-spacing: 1px;
}
.voice-btn {
  background: #fff;
  color: #6366f1;
  border: none;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  margin-left: 8px;
  box-shadow: 0 2px 8px rgba(99, 102, 241, 0.08);
  cursor: pointer !important;
  transition:
    background 0.2s,
    color 0.2s;
  border: 2px solid #e0e7ff;
}
.voice-btn.active {
  background: #6366f1;
  color: #fff;
  border-color: #6366f1;
}
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

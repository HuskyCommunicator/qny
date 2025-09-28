<script setup>
import { ElIcon, ElLoading, ElMessage } from "element-plus";
import { Microphone, VideoPlay, VideoPause } from "@element-plus/icons-vue";
import { ref, onMounted, nextTick, onUnmounted } from "vue";
import { useRoute } from "vue-router";
import { sendChatTextAPI, speechToTextAPI, textToSpeechAPI } from "../api/agent";
const recognizing = ref(false);
const showVoiceModal = ref(false);
const isPlaying = ref(false);
const currentAudio = ref(null);
const audioQueue = ref([]);
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

// TTS功能
async function playTextToSpeech(text, voice = "longxiaochun") {
  try {
    const response = await textToSpeechAPI({
      content: text,
      voice: voice,
      format: "mp3"
    });
    
    if (response.audio_base64) {
      // 将base64转换为音频
      const audioData = atob(response.audio_base64);
      const audioBlob = new Blob([new Uint8Array(audioData)], { type: 'audio/mp3' });
      const audioUrl = URL.createObjectURL(audioBlob);
      
      // 创建音频对象
      const audio = new Audio(audioUrl);
      audioQueue.value.push(audio);
      
      // 如果当前没有播放音频，开始播放
      if (!isPlaying.value) {
        playNextAudio();
      }
    }
  } catch (error) {
    console.error("TTS播放失败:", error);
    ElMessage.error("语音播放失败");
  }
}

function playNextAudio() {
  if (audioQueue.value.length === 0) {
    isPlaying.value = false;
    return;
  }
  
  const audio = audioQueue.value.shift();
  currentAudio.value = audio;
  isPlaying.value = true;
  
  audio.onended = () => {
    URL.revokeObjectURL(audio.src);
    playNextAudio();
  };
  
  audio.onerror = () => {
    console.error("音频播放错误");
    isPlaying.value = false;
    playNextAudio();
  };
  
  audio.play().catch(error => {
    console.error("音频播放失败:", error);
    isPlaying.value = false;
    playNextAudio();
  });
}

function stopAudio() {
  if (currentAudio.value) {
    currentAudio.value.pause();
    currentAudio.value.currentTime = 0;
    URL.revokeObjectURL(currentAudio.value.src);
  }
  audioQueue.value = [];
  isPlaying.value = false;
  currentAudio.value = null;
}
const route = useRoute();
// 入口传递的角色信息
const agent = {
  id: route.query.role_id,
  name: route.query.display_name || route.query.name || "AI助手",
  avatar:
    route.query.avatar_url ||
    route.query.avatar ||
    "https://placekitten.com/100/100",
  description: route.query.description || "",
};

const messages = ref([
  {
    from: "agent",
    text: `你好，我是${agent.name}${agent.description ? "，" + agent.description : ""}。很高兴为你服务！`,
  },
]);
const input = ref("");

// 会话ID处理 - 优先使用URL参数，其次使用localStorage
const sessionId = ref(
  route.query.session_id || 
  localStorage.getItem(`chat-session-${agent.id}`) || 
  ""
);

async function send() {
  if (!input.value.trim()) return;
  const userMsg = input.value;
  messages.value.push({ from: "user", text: userMsg });
  input.value = ""; // 立即清空输入框
  await nextTick(); // 等待视图刷新

  // 构造请求体
  const payload = {
    content: userMsg,
  };
  
  // 如果有role_id，添加到请求中
  if (agent.id) {
    payload.role_id = agent.id;
  }
  
  if (sessionId.value) {
    payload.session_id = sessionId.value;
  }

  try {
    const res = await sendChatTextAPI(payload);
    // 处理session_id - 如果后端返回了新的session_id，更新本地存储
    if (res.session_id) {
      sessionId.value = res.session_id;
      // 使用角色特定的key存储session_id
      if (agent.id) {
        localStorage.setItem(`chat-session-${agent.id}`, res.session_id);
      } else {
        localStorage.setItem("chat-session-default", res.session_id);
      }
    }
    setTimeout(() => {
      const replyText = res.content || "(无回复)";
      messages.value.push({ from: "agent", text: replyText });
      
      // 自动播放AI回复的语音
      if (replyText !== "(无回复)") {
        playTextToSpeech(replyText);
      }
    }, 1000);
  } catch (err) {
    console.error("聊天请求失败:", err);
    setTimeout(() => {
      messages.value.push({ from: "agent", text: "对话失败，请重试。" });
    }, 1500);
  }
}

// 组件卸载时清理音频资源
onUnmounted(() => {
  stopAudio();
  if (recognition) {
    recognition.stop();
  }
});
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
          <!-- AI消息添加语音播放按钮 -->
          <div v-if="msg.from === 'agent'" class="msg-actions">
            <button 
              @click="playTextToSpeech(msg.text)"
              class="play-btn"
              :disabled="isPlaying"
              title="播放语音"
            >
              <el-icon>
                <VideoPlay v-if="!isPlaying" />
                <VideoPause v-else />
              </el-icon>
            </button>
          </div>
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
        title="语音输入"
      >
        <el-icon><Microphone /></el-icon>
      </button>
      <button
        v-if="isPlaying"
        @click="stopAudio"
        class="stop-btn"
        title="停止播放"
      >
        <el-icon><VideoPause /></el-icon>
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

.stop-btn {
  background: #fff;
  color: #ef4444;
  border: none;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  margin-left: 8px;
  box-shadow: 0 2px 8px rgba(239, 68, 68, 0.08);
  cursor: pointer;
  transition: background 0.2s, color 0.2s;
  border: 2px solid #fecaca;
}

.stop-btn:hover {
  background: #ef4444;
  color: #fff;
  border-color: #ef4444;
}

.msg-actions {
  display: flex;
  align-items: center;
  margin-top: 8px;
  gap: 8px;
}

.play-btn {
  background: rgba(99, 102, 241, 0.1);
  color: #6366f1;
  border: none;
  border-radius: 50%;
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s;
}

.play-btn:hover {
  background: #6366f1;
  color: #fff;
}

.play-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
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

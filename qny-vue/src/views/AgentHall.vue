<script setup>
const agents = [
  {
    id: 1,
    name: "AI助手",
    avatar: "https://placekitten.com/100/100",
    description: "全能助手，可以回答各种问题",
  },
  {
    id: 2,
    name: "编程专家",
    avatar: "https://placekitten.com/101/101",
    description: "帮助解决编程问题，支持多种语言",
  },
  {
    id: 3,
    name: "语言翻译",
    avatar: "https://placekitten.com/102/102",
    description: "多语言翻译，支持实时对话",
  },
  {
    id: 4,
    name: "心理咨询",
    avatar: "https://placekitten.com/103/103",
    description: "提供心理健康支持和咨询",
  },
];
</script>

<template>
  <div class="agent-hall">
    <h1>智能体大厅</h1>
    <div class="agent-list">
      <div v-for="agent in agents" :key="agent.id" class="agent-card">
        <img :src="agent.avatar" :alt="agent.name" class="avatar" />
        <h3>{{ agent.name }}</h3>
        <p>{{ agent.description }}</p>
        <div class="agent-action">
          <button
            @click="$router.push({ name: 'Chat', query: { agent: agent.id } })"
          >
            进入智能体
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.agent-hall {
  padding: 40px 24px;
  margin: 0;
  min-height: 100vh;
  background: linear-gradient(135deg, #f8fafc 0%, #e0e7ff 100%);
  border-radius: 24px;
  box-shadow: 0 8px 32px rgba(60, 72, 100, 0.08);

  h1 {
    text-align: center;
    margin-bottom: 40px;
    font-size: 2.6rem;
    color: #3b3b5c;
    letter-spacing: 2px;
    font-weight: 700;
    text-shadow: 0 2px 8px #e0e7ff;
  }
}

.agent-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(270px, 1fr));
  gap: 32px;
}

.agent-card {
  background: #fff;
  border: none;
  border-radius: 18px;
  padding: 32px 20px 24px 20px;
  text-align: center;
  box-shadow: 0 4px 24px rgba(60, 72, 100, 0.1);
  transition:
    transform 0.25s cubic-bezier(0.4, 2, 0.6, 1),
    box-shadow 0.25s;
  position: relative;
  overflow: hidden;

  &:hover {
    transform: translateY(-10px) scale(1.03);
    box-shadow: 0 12px 32px rgba(60, 72, 100, 0.18);
    background: linear-gradient(120deg, #f0f4ff 60%, #e0e7ff 100%);
  }

  .avatar {
    width: 90px;
    height: 90px;
    border-radius: 50%;
    object-fit: cover;
    margin-bottom: 18px;
    border: 4px solid #e0e7ff;
    box-shadow: 0 2px 12px rgba(60, 72, 100, 0.1);
    background: #f8fafc;
    transition: border-color 0.2s;
  }

  h3 {
    margin: 12px 0 8px 0;
    color: #2d3756;
    font-size: 1.3rem;
    font-weight: 600;
    letter-spacing: 1px;
  }

  p {
    color: #6b7280;
    font-size: 15px;
    margin-bottom: 20px;
    min-height: 40px;
  }

  .agent-action {
    margin-top: 10px;
    display: flex;
    justify-content: center;

    button {
      background: linear-gradient(90deg, #6366f1 0%, #818cf8 100%);
      color: #fff;
      border: none;
      border-radius: 20px;
      padding: 8px 24px;
      font-size: 15px;
      font-weight: 500;
      cursor: pointer;
      box-shadow: 0 2px 8px rgba(99, 102, 241, 0.1);
      transition:
        background 0.2s,
        box-shadow 0.2s;
      &:hover {
        background: linear-gradient(90deg, #818cf8 0%, #6366f1 100%);
        box-shadow: 0 4px 16px rgba(99, 102, 241, 0.18);
      }
    }
  }
}
</style>

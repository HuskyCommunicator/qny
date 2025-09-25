<script setup>
import AgentCard from "../components/AgentCard.vue";
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
      <AgentCard
        v-for="agent in agents"
        :key="agent.id"
        :name="agent.name"
        :avatar="agent.avatar"
        :description="agent.description"
        :showAction="true"
        actionText="进入智能体"
        @action="$router.push({ name: 'Chat', query: { agent: agent.id } })"
      />
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
</style>

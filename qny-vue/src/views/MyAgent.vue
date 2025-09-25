<script setup>
import { useRouter } from "vue-router";
import AgentCard from '../components/AgentCard.vue';
const router = useRouter();
const myAgents = [
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
];
function goCreate() {
  router.push({ name: "CreateAgent" });
}
</script>

<template>
  <div class="my-agent-page">
    <h1>我的智能体</h1>
    <div class="agent-list">
      <AgentCard
        v-for="agent in myAgents"
        :key="agent.id"
        :name="agent.name"
        :avatar="agent.avatar"
        :description="agent.description"
        :showAction="true"
        actionText="进入智能体"
        @action="$router.push({ name: 'Chat', query: { agent: agent.id } })"
      />
      <AgentCard add addText="创建智能体" @add="goCreate" />
    </div>
  </div>
</template>

<style lang="scss" scoped>
.my-agent-page {
  padding: 40px 24px;
  min-height: 100vh;
  background: linear-gradient(135deg, #f8fafc 0%, #e0e7ff 100%);
  border-radius: 0;
}
.my-agent-page h1 {
  text-align: center;
  margin-bottom: 40px;
  font-size: 2.2rem;
  color: #3b3b5c;
  letter-spacing: 2px;
  font-weight: 700;
  text-shadow: 0 2px 8px #e0e7ff;
}
.agent-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(270px, 1fr));
  gap: 32px;
  max-width: 1200px;
  margin: 0 auto;
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
  cursor: pointer;
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
    margin-bottom: 18px;
  }
}
</style>
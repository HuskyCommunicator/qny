<script setup>
// 保留下方唯一一份 router 声明和 handleAgentAction
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import AgentCard from "../components/AgentCard.vue";
import { getAgentListAPI } from "../api/agent";

const agents = ref([]);
const router = useRouter();

async function fetchAgents() {
  try {
    const res = await getAgentListAPI();
    // 兼容 roles 或直接数组结构
    if (Array.isArray(res)) {
      agents.value = res;
    } else if (Array.isArray(res.roles)) {
      agents.value = res.roles;
    } else {
      agents.value = [];
    }
  } catch (e) {
    agents.value = [];
  }
}
function handleAgentAction(agent) {
  const conversation_id = Math.random().toString(36).slice(2) + Date.now();
  router.push({
    name: "Chat",
    query: {
      conversation_id,
      ...agent,
    },
  });
}

onMounted(() => {
  fetchAgents();
});
</script>

<template>
  <div class="agent-hall">
    <h1>智能体大厅</h1>
    <div class="agent-list">
      <AgentCard
        v-for="agent in agents"
        :key="agent.name"
        :display_name="agent.display_name"
        :avatar_url="agent.avatar_url"
        :description="agent.description"
        :skills="agent.skills"
        :showAction="true"
        actionText="进入智能体"
        @action="handleAgentAction(agent)"
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

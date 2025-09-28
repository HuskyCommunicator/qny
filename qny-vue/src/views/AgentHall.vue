<script setup>
// 保留下方唯一一份 router 声明和 handleAgentAction
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import AgentCard from "../components/AgentCard.vue";
import { getAgentListAPI, createRoleFromTemplateAPI } from "../api/agent";

const agents = ref([]);
const loading = ref(false);
const router = useRouter();

async function fetchAgents() {
  try {
    loading.value = true;
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
    console.error("获取角色列表失败:", e);
    agents.value = [];
  } finally {
    loading.value = false;
  }
}

async function handleAgentAction(agent) {
  try {
    // 如果角色有ID，直接进入聊天
    if (agent.id) {
      // 检查是否有现有的session_id
      const existingSessionId = localStorage.getItem(`chat-session-${agent.id}`);
      
      router.push({
        name: "Chat",
        query: {
          role_id: agent.id,
          name: agent.name,
          display_name: agent.display_name,
          avatar_url: agent.avatar_url,
          description: agent.description,
          // 如果有现有会话，传递session_id
          ...(existingSessionId && { session_id: existingSessionId }),
        },
      });
      return;
    }

    // 如果角色没有ID（是模板），先创建角色实例
    if (agent.is_builtin) {
      loading.value = true;
      const createdRole = await createRoleFromTemplateAPI(agent.name);
      
      // 创建成功后，使用新创建的角色进入聊天
      router.push({
        name: "Chat",
        query: {
          role_id: createdRole.id,
          name: createdRole.name,
          display_name: createdRole.display_name,
          avatar_url: createdRole.avatar_url,
          description: createdRole.description,
        },
      });
    }
  } catch (error) {
    console.error("创建角色实例失败:", error);
    // 如果创建失败，仍然可以进入聊天（使用模板信息）
    router.push({
      name: "Chat",
      query: {
        role_id: null, // 没有ID的角色
        name: agent.name,
        display_name: agent.display_name,
        avatar_url: agent.avatar_url,
        description: agent.description,
      },
    });
  } finally {
    loading.value = false;
  }
}

onMounted(() => {
  fetchAgents();
});
</script>

<template>
  <div class="agent-hall">
    <h1>智能体大厅</h1>
    <div v-if="loading" class="loading-container">
      <div class="loading-text">正在加载角色...</div>
    </div>
    <div v-else class="agent-list">
      <AgentCard
        v-for="agent in agents"
        :key="agent.id || agent.name"
        :display_name="agent.display_name"
        :avatar_url="agent.avatar_url"
        :description="agent.description"
        :skills="agent.skills"
        :showAction="true"
        :actionText="agent.id ? '进入智能体' : '创建并进入'"
        :isBuiltin="agent.is_builtin"
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

.loading-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 200px;
}

.loading-text {
  font-size: 1.2rem;
  color: #6366f1;
  font-weight: 500;
}
</style>

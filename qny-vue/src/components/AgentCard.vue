<template>
  <div class="agent-card" :class="{ 'add-card': add }" @click="handleClick">
    <template v-if="add">
      <div class="add-plus">+</div>
      <div class="add-text">{{ addText || "创建智能体" }}</div>
    </template>
    <template v-else>
      <img :src="avatar_url" :alt="display_name" class="avatar" />
      <h3>{{ display_name }}</h3>
      <p class="agent-desc">{{ description }}</p>
      <div class="agent-personality">
        <span class="personality-label">性格：</span>
        <span class="personality-value">{{ personality }}</span>
      </div>
      <div v-if="showAction" class="agent-action">
        <button @click.stop="onAction">{{ actionText || "进入智能体" }}</button>
      </div>
    </template>
  </div>
</template>

<script setup>
const props = defineProps({
  display_name: String,
  avatar_url: String,
  description: String,
  personality: String,
  showAction: Boolean,
  actionText: String,
  add: Boolean,
  addText: String,
});
const emit = defineEmits(["action", "add"]);
function onAction() {
  emit("action");
}
function handleClick() {
  if (props.add) emit("add");
}
</script>

<style lang="scss" scoped>
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
  .agent-desc {
    color: #6b7280;
    font-size: 15px;
    margin-bottom: 12px;
    min-height: 40px;
  }
  .agent-personality {
    font-size: 14px;
    color: #6366f1;
    margin-bottom: 16px;
    .personality-label {
      font-weight: 500;
      margin-right: 4px;
    }
    .personality-value {
      font-weight: 400;
    }
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
.add-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #6366f1;
  background: linear-gradient(135deg, #f0f4ff 60%, #e0e7ff 100%);
  border: 2px dashed #a5b4fc;
  box-shadow: none;
  .add-plus {
    font-size: 3.2rem;
    font-weight: 700;
    margin-bottom: 10px;
    line-height: 1;
  }
  .add-text {
    font-size: 1.1rem;
    font-weight: 500;
    color: #6366f1;
  }
  &:hover {
    background: linear-gradient(120deg, #e0e7ff 60%, #f0f4ff 100%);
    border-color: #6366f1;
    color: #6366f1;
    box-shadow: 0 4px 16px rgba(99, 102, 241, 0.1);
  }
}
</style>

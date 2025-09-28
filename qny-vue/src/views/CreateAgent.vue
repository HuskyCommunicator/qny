<template>
  <div class="create-agent-page">
    <div class="create-agent-container">
      <h2>创建智能体</h2>
      <div class="form-row">
        <label>名称：</label>
        <input v-model="name" placeholder="请输入智能体名称" />
      </div>
      <div class="form-row">
        <label>描述：</label>
        <textarea
          v-model="description"
          placeholder="请输入智能体描述"
        ></textarea>
      </div>
      <div class="form-row">
        <label>系统提示：</label>
        <textarea
          v-model="system_prompt"
          placeholder="请输入系统提示词"
        ></textarea>
      </div>
      <div class="form-row">
        <button @click="submit">创建</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { addAgentAPI } from "../api/agent";

const router = useRouter();
const name = ref("");
const description = ref("");
const system_prompt = ref("");

async function submit() {
  if (!name.value) {
    ElMessage.error("请输入智能体名称");
    return;
  }
  if (!description.value) {
    ElMessage.error("请输入描述");
    return;
  }
  if (!system_prompt.value) {
    ElMessage.error("请输入系统提示词");
    return;
  }
  try {
    const res = await addAgentAPI({
      name: name.value,
      description: description.value,
      system_prompt: system_prompt.value,
    });
    if (res && (res.code === 200 || res.status === 200)) {
      ElMessage.success("创建成功");
      router.push({ name: "MyAgent" });
    } else {
      ElMessage.error(res.msg || "创建失败");
    }
  } catch (err) {
    ElMessage.error("创建失败，请重试");
  }
}
</script>

<style lang="scss" scoped>
.create-agent-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #f8fafc 0%, #e0e7ff 100%);
  display: flex;
  align-items: center;
  justify-content: center;
}
.create-agent-container {
  background: #fff;
  border-radius: 18px;
  box-shadow: 0 4px 24px rgba(60, 72, 100, 0.1);
  padding: 40px 32px 32px 32px;
  min-width: 340px;
  max-width: 90vw;
}
.create-agent-container h2 {
  text-align: center;
  margin-bottom: 32px;
  color: #3b3b5c;
  font-size: 1.5rem;
  font-weight: 700;
}
.form-row {
  display: flex;
  align-items: flex-start;
  margin-bottom: 22px;
}
.form-row label {
  width: 60px;
  color: #2d3756;
  font-weight: 500;
  margin-right: 10px;
  line-height: 2.2;
}
.form-row input,
.form-row textarea {
  flex: 1;
  border: 1px solid #e0e7ff;
  border-radius: 8px;
  padding: 8px 12px;
  font-size: 1rem;
  background: #f8fafc;
  outline: none;
  transition: border 0.2s;
}
.form-row input:focus,
.form-row textarea:focus {
  border: 1.5px solid #6366f1;
}
.form-row textarea {
  min-height: 60px;
  resize: vertical;
}
.form-row button {
  width: 100%;
  background: linear-gradient(90deg, #6366f1 0%, #818cf8 100%);
  color: #fff;
  border: none;
  border-radius: 20px;
  padding: 10px 0;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(99, 102, 241, 0.1);
  transition:
    background 0.2s,
    box-shadow 0.2s;
}
.form-row button:hover {
  background: linear-gradient(90deg, #818cf8 0%, #6366f1 100%);
  box-shadow: 0 4px 16px rgba(99, 102, 241, 0.18);
}
</style>

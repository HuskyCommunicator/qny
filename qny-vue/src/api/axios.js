import API from "./api";
import axios from "axios";
import { ElMessage } from "element-plus";
const CancelToken = axios.CancelToken;
const source = CancelToken.source();

const instance = axios.create({
  baseURL: API.baseURL,
  timeout: 30000,
  cancelToken: source.token,
  headers: {
    "X-Requested-With": "XMLHttpRequest",
    Accept: "application/json",
    "Content-Type": "application/json",
  },
});

// 请求拦截器
instance.interceptors.request.use(
  async (config) => {
    // 添加Authorization token到请求头
    const token = localStorage.getItem("qny-token");
    if (token) {
      config.headers["Authorization"] = `Bearer ${token}`;
    }

    // 特殊处理文件上传请求
    if (config.data instanceof FormData) {
      config.headers["Content-Type"] = "multipart/form-data";
    }

    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
instance.interceptors.response.use(
  (response) => {
    // 直接返回响应数据
    return response.data;
  },
  (error) => {
    // 处理HTTP错误
    if (error.response) {
      switch (error.response.status) {
        case 401:
        case 405:
          ElMessage.error("登录已过期，请重新登录");
          localStorage.removeItem("token");
          if (typeof router !== "undefined" && router.push) {
            router.push("/login");
          } else {
            window.location.href = "/login";
          }
          break;
        case 403:
          ElMessage.error("拒绝访问");
          break;
        case 404:
          ElMessage.error("请求资源不存在");
          break;
        case 500:
          ElMessage.error("服务器错误");
          break;
        default:
          ElMessage.error(error.response?.data?.detail || error.message);
      }
    } else if (error.request) {
      ElMessage.error("网络连接失败");
    }

    // 如果是取消的请求，不显示错误
    if (axios.isCancel(error)) {
      return Promise.reject("请求已取消");
    }

    return Promise.reject(error);
  }
);

// 添加取消请求方法
export function cancelRequest(message) {
  source.cancel(message);
}

// 导出配置好的axios实例
const request = instance;

// 同时导出cancelRequest方法
export { request as default };

import axios from "axios";
import { Message } from "element-ui";
import router from "@/router";

const CancelToken = axios.CancelToken;
const source = CancelToken.source();

const instance = axios.create({
  baseURL: process.env.VUE_APP_URL,
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
    // 添加access-token到请求头
    const token = localStorage.getItem("access-token");
    if (token) {
      config.headers["access-token"] = token;
    }

    // 添加固定请求头
    config.headers["LANGUAGE"] = "zh";
    config.headers["ORG-ID"] = "XXX";

    // 特殊处理文件上传请求
    if (config.data instanceof FormData) {
      config.headers["Content-Type"] = "multipart/form-data";
    }

    return config;
  },
  (error) => {
    // loadingInstance.close();
    return Promise.reject(error);
  }
);

// 响应拦截器
instance.interceptors.response.use(
  async (response) => {
    // loadingInstance.close();

    if (response && response.data) {
      // 处理token无效情况
      if (response.data.resultMsg === "未登录异常:token 无效") {
        localStorage.removeItem("access-token");
        Message.error("登录已过期，请重新登录");
        router.push("/login");
      }
      // 处理resultCode不等于100000的情况(排除100009)
      if (
        response.data.resultCode &&
        response.data.resultCode !== "100000" &&
        response.data.resultCode !== "100009"
      ) {
        return Promise.reject(response.data);
      }
    }

    // 返回完整response对象以便访问headers
    return response;
  },
  (error) => {
    // loadingInstance.close();

    // 处理HTTP错误
    if (error.response) {
      switch (error.response.status) {
        case 401:
          Message.error("未授权，请重新登录");
          break;
        case 403:
          Message.error("拒绝访问");
          break;
        case 404:
          Message.error("请求资源不存在");
          break;
        case 500:
          Message.error("服务器错误");
          break;
        default:
          Message.error(error.message);
      }
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
const http = instance;

// 同时导出cancelRequest方法
export { http as default };

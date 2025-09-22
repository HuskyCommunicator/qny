const baseURL = "/compare/v1";
const API = {
  // 通用接口
  COMMON: {
    LOGIN: baseURL + "/user/login", // 用户登录
    CHECKJWT: baseURL + "/user/checkJWT", // 校验JWT
    GET_WATER_MASK_BASE64: baseURL + "/user/getWaterMaskBase64", // 获取水印点阵图片BASE64值
  },
};

export default API;

/**
 * API 服务基础配置
 *
 * 提供统一的HTTP客户端和API调用封装
 */
import axios from 'axios';

// API基础配置
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8002';
const API_VERSION = '/api';

// 创建axios实例
const apiClient = axios.create({
  baseURL: `${API_BASE_URL}${API_VERSION}`,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
});

// 请求拦截器
apiClient.interceptors.request.use(
  (config) => {
    // 添加请求时间戳
    config.metadata = { startTime: new Date() };

    // 添加认证token（如果需要）
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    console.log(`🚀 API请求: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('❌ API请求配置错误:', error);
    return Promise.reject(error);
  }
);

// 响应拦截器
apiClient.interceptors.response.use(
  (response) => {
    // 计算请求耗时
    const endTime = new Date();
    const duration = endTime.getTime() - response.config.metadata.startTime.getTime();

    console.log(
      `✅ API响应: ${response.config.method?.toUpperCase()} ${response.config.url} (${duration}ms)`,
      response.data
    );

    return response;
  },
  (error) => {
    // 统一错误处理
    const { response, config } = error;

    if (config) {
      const endTime = new Date();
      const duration = endTime.getTime() - config.metadata.startTime.getTime();
      console.error(
        `❌ API错误: ${config.method?.toUpperCase()} ${config.url} (${duration}ms)`,
        response?.data || error.message
      );
    }

    // 处理特定HTTP状态码
    if (response) {
      switch (response.status) {
        case 401:
          // 未授权，清除token并跳转登录
          localStorage.removeItem('authToken');
          window.location.href = '/login';
          break;
        case 403:
          console.error('🚫 权限不足');
          break;
        case 404:
          console.error('🔍 资源未找到');
          break;
        case 429:
          console.error('🚦 请求频率过高，请稍后重试');
          break;
        case 500:
          console.error('🔥 服务器内部错误');
          break;
        default:
          console.error(`⚠️  HTTP ${response.status}: ${response.data?.message || '请求失败'}`);
      }
    } else if (error.code === 'ECONNABORTED') {
      console.error('⏰ 请求超时');
    } else {
      console.error('🌐 网络连接错误');
    }

    return Promise.reject(error);
  }
);

// 基础API类
class BaseAPI {
  constructor(endpoint) {
    this.endpoint = endpoint;
  }

  /**
   * 获取列表数据
   * @param {Object} params - 查询参数
   * @returns {Promise} API响应
   */
  async getList(params = {}) {
    try {
      const response = await apiClient.get(this.endpoint, { params });
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  /**
   * 获取单个实体详情
   * @param {number} id - 实体ID
   * @returns {Promise} API响应
   */
  async getDetail(id) {
    try {
      const response = await apiClient.get(`${this.endpoint}/${id}`);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  /**
   * 搜索实体
   * @param {string} query - 搜索关键词
   * @param {Object} filters - 过滤条件
   * @returns {Promise} API响应
   */
  async search(query, filters = {}) {
    try {
      const params = { search: query, ...filters };
      const response = await apiClient.get(`${this.endpoint}/search`, { params });
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  /**
   * 创建新实体
   * @param {Object} data - 实体数据
   * @returns {Promise} API响应
   */
  async create(data) {
    try {
      const response = await apiClient.post(this.endpoint, data);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  /**
   * 更新实体
   * @param {number} id - 实体ID
   * @param {Object} data - 更新数据
   * @returns {Promise} API响应
   */
  async update(id, data) {
    try {
      const response = await apiClient.put(`${this.endpoint}/${id}`, data);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  /**
   * 删除实体
   * @param {number} id - 实体ID
   * @returns {Promise} API响应
   */
  async delete(id) {
    try {
      const response = await apiClient.delete(`${this.endpoint}/${id}`);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  /**
   * 错误处理
   * @param {Error} error - 错误对象
   * @returns {Object} 格式化的错误信息
   */
  handleError(error) {
    const { response } = error;

    if (response?.data) {
      // 服务器返回的错误信息
      return {
        success: false,
        error: response.data.error || response.data.message || '请求失败',
        code: response.data.code,
        details: response.data.details,
        status: response.status,
      };
    } else if (error.code === 'ECONNABORTED') {
      // 请求超时
      return {
        success: false,
        error: '请求超时，请检查网络连接',
        code: 'TIMEOUT',
      };
    } else {
      // 网络或其他错误
      return {
        success: false,
        error: '网络连接失败，请稍后重试',
        code: 'NETWORK_ERROR',
      };
    }
  }
}

// 系统API
class SystemAPI {
  /**
   * 健康检查
   * @returns {Promise} 系统状态
   */
  async healthCheck() {
    try {
      const response = await apiClient.get('/health');
      return response.data;
    } catch (error) {
      throw new BaseAPI().handleError(error);
    }
  }

  /**
   * 获取系统统计
   * @returns {Promise} 统计信息
   */
  async getStats() {
    try {
      const response = await apiClient.get('/stats');
      return response.data;
    } catch (error) {
      throw new BaseAPI().handleError(error);
    }
  }

  /**
   * 获取数据源状态
   * @returns {Promise} 数据源状态
   */
  async getDataSourceStatus() {
    try {
      const response = await apiClient.get('/data-sources/status');
      return response.data;
    } catch (error) {
      throw new BaseAPI().handleError(error);
    }
  }
}

// 通用搜索API
class SearchAPI {
  /**
   * 全局搜索
   * @param {string} query - 搜索关键词
   * @param {Object} options - 搜索选项
   * @returns {Promise} 搜索结果
   */
  async search(query, options = {}) {
    try {
      const params = {
        q: query,
        ...options
      };
      const response = await apiClient.get('/search', { params });
      return response.data;
    } catch (error) {
      throw new BaseAPI().handleError(error);
    }
  }

  /**
   * 获取搜索建议
   * @param {string} query - 搜索关键词
   * @returns {Promise} 建议列表
   */
  async getSuggestions(query) {
    try {
      const response = await apiClient.get('/search/suggestions', {
        params: { q: query }
      });
      return response.data;
    } catch (error) {
      throw new BaseAPI().handleError(error);
    }
  }
}

// 文件上传API
class UploadAPI {
  /**
   * 上传图片
   * @param {File} file - 图片文件
   * @param {Object} metadata - 图片元数据
   * @param {Function} onProgress - 进度回调
   * @returns {Promise} 上传结果
   */
  async uploadImage(file, metadata = {}, onProgress) {
    try {
      const formData = new FormData();
      formData.append('file', file);

      // 添加元数据
      Object.keys(metadata).forEach(key => {
        formData.append(key, metadata[key]);
      });

      const response = await apiClient.post('/images/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          if (onProgress) {
            const percentCompleted = Math.round(
              (progressEvent.loaded * 100) / progressEvent.total
            );
            onProgress(percentCompleted);
          }
        },
      });

      return response.data;
    } catch (error) {
      throw new BaseAPI().handleError(error);
    }
  }
}

// 导出API实例
export const systemAPI = new SystemAPI();
export const searchAPI = new SearchAPI();
export const uploadAPI = new UploadAPI();

// 导出基础类供其他服务继承
export { BaseAPI, apiClient };

// 导出配置
export const API_CONFIG = {
  BASE_URL: API_BASE_URL,
  VERSION: API_VERSION,
  TIMEOUT: 10000,
};

// 工具函数
export const utils = {
  /**
   * 构建查询参数
   * @param {Object} params - 参数对象
   * @returns {string} 查询字符串
   */
  buildQueryString(params) {
    const searchParams = new URLSearchParams();
    Object.keys(params).forEach(key => {
      const value = params[key];
      if (value !== null && value !== undefined && value !== '') {
        searchParams.append(key, value);
      }
    });
    return searchParams.toString();
  },

  /**
   * 格式化API错误信息
   * @param {Object} error - 错误对象
   * @returns {string} 用户友好的错误信息
   */
  formatError(error) {
    if (error.code === 'TIMEOUT') {
      return '请求超时，请检查网络连接后重试';
    } else if (error.code === 'NETWORK_ERROR') {
      return '网络连接失败，请检查网络设置';
    } else if (error.status === 404) {
      return '请求的资源不存在';
    } else if (error.status === 500) {
      return '服务器暂时不可用，请稍后重试';
    } else {
      return error.error || '操作失败，请重试';
    }
  },

  /**
   * 防抖函数
   * @param {Function} func - 要防抖的函数
   * @param {number} wait - 等待时间（毫秒）
   * @returns {Function} 防抖后的函数
   */
  debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  },
};

export default {
  systemAPI,
  searchAPI,
  uploadAPI,
  BaseAPI,
  apiClient,
  API_CONFIG,
  utils,
};
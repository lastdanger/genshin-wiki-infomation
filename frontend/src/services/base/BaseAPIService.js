/**
 * 基础API服务类
 *
 * 提供统一的HTTP请求封装，包括：
 * - 请求/响应拦截
 * - 错误处理
 * - 请求重试
 * - 请求取消
 * - 日志记录
 *
 * 所有domain API服务都应继承此类
 */
import axios from 'axios';
import { createErrorFromResponse, isRetryableError } from '../errors';
import { setupInterceptors } from './interceptors';
import { retryRequest } from './retryPolicy';

class BaseAPIService {
  constructor(baseURL = '/api', timeout = 30000) {
    // 创建axios实例
    this.client = axios.create({
      baseURL: baseURL || process.env.REACT_APP_API_BASE_URL || '/api',
      timeout,
      headers: {
        'Content-Type': 'application/json'
      }
    });

    // 设置拦截器
    setupInterceptors(this.client);

    // 请求取消管理
    this.cancelTokenSource = null;
  }

  /**
   * GET请求
   *
   * @param {string} url - 请求URL
   * @param {Object} params - URL查询参数
   * @param {Object} config - 额外的axios配置
   * @returns {Promise<any>}
   */
  async get(url, params = {}, config = {}) {
    return this.request({
      method: 'GET',
      url,
      params,
      ...config
    });
  }

  /**
   * POST请求
   *
   * @param {string} url - 请求URL
   * @param {Object} data - 请求body数据
   * @param {Object} config - 额外的axios配置
   * @returns {Promise<any>}
   */
  async post(url, data = {}, config = {}) {
    return this.request({
      method: 'POST',
      url,
      data,
      ...config
    });
  }

  /**
   * PUT请求
   *
   * @param {string} url - 请求URL
   * @param {Object} data - 请求body数据
   * @param {Object} config - 额外的axios配置
   * @returns {Promise<any>}
   */
  async put(url, data = {}, config = {}) {
    return this.request({
      method: 'PUT',
      url,
      data,
      ...config
    });
  }

  /**
   * PATCH请求
   *
   * @param {string} url - 请求URL
   * @param {Object} data - 请求body数据
   * @param {Object} config - 额外的axios配置
   * @returns {Promise<any>}
   */
  async patch(url, data = {}, config = {}) {
    return this.request({
      method: 'PATCH',
      url,
      data,
      ...config
    });
  }

  /**
   * DELETE请求
   *
   * @param {string} url - 请求URL
   * @param {Object} config - 额外的axios配置
   * @returns {Promise<any>}
   */
  async delete(url, config = {}) {
    return this.request({
      method: 'DELETE',
      url,
      ...config
    });
  }

  /**
   * 通用请求方法
   *
   * @param {Object} config - axios请求配置
   * @returns {Promise<any>}
   */
  async request(config) {
    try {
      // 发送请求
      const response = await this.client.request(config);

      // 返回响应数据
      return response.data;
    } catch (error) {
      // 创建标准化的错误对象
      const standardError = createErrorFromResponse(error, config);

      // 判断是否需要重试
      if (isRetryableError(standardError)) {
        try {
          // 执行重试
          const retryResponse = await retryRequest(this.client, config);
          return retryResponse.data;
        } catch (retryError) {
          // 重试仍然失败，抛出错误
          throw createErrorFromResponse(retryError, config);
        }
      }

      // 不可重试的错误直接抛出
      throw standardError;
    }
  }

  /**
   * 取消当前正在进行的请求
   */
  cancelRequest(message = '请求已取消') {
    if (this.cancelTokenSource) {
      this.cancelTokenSource.cancel(message);
      this.cancelTokenSource = null;
    }
  }

  /**
   * 创建新的取消token
   *
   * @returns {Object} - axios取消token
   */
  getCancelToken() {
    this.cancelTokenSource = axios.CancelToken.source();
    return this.cancelTokenSource.token;
  }

  /**
   * 上传文件
   *
   * @param {string} url - 上传URL
   * @param {FormData} formData - 表单数据
   * @param {Function} onProgress - 上传进度回调
   * @returns {Promise<any>}
   */
  async upload(url, formData, onProgress = null) {
    const config = {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    };

    if (onProgress) {
      config.onUploadProgress = (progressEvent) => {
        const percentCompleted = Math.round(
          (progressEvent.loaded * 100) / progressEvent.total
        );
        onProgress(percentCompleted);
      };
    }

    return this.post(url, formData, config);
  }

  /**
   * 批量请求（并行）
   *
   * @param {Array<Object>} requests - 请求配置数组
   * @returns {Promise<Array>}
   */
  async batchRequest(requests) {
    try {
      const promises = requests.map(config => this.request(config));
      return await Promise.all(promises);
    } catch (error) {
      // 有一个请求失败就抛出错误
      throw error;
    }
  }

  /**
   * 批量请求（并行，允许部分失败）
   *
   * @param {Array<Object>} requests - 请求配置数组
   * @returns {Promise<Array>} - 包含成功和失败结果的数组
   */
  async batchRequestAllSettled(requests) {
    const promises = requests.map(config =>
      this.request(config)
        .then(data => ({ status: 'fulfilled', value: data }))
        .catch(error => ({ status: 'rejected', reason: error }))
    );
    return await Promise.all(promises);
  }
}

export default BaseAPIService;

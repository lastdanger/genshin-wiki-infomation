/**
 * 全局搜索API服务
 *
 * 提供跨实体的统一搜索功能
 */
import BaseAPIService from './base/BaseAPIService';

class SearchAPIService extends BaseAPIService {
  constructor() {
    super('/api');
  }

  /**
   * 全局搜索
   * 搜索所有类型的实体（角色、武器、圣遗物、怪物等）
   *
   * @param {string} query - 搜索关键词
   * @param {Object} options - 搜索选项
   * @param {Array<string>} options.types - 限制搜索的实体类型
   * @param {number} options.limit - 每个类型返回的结果数量
   * @returns {Promise<Object>} - 分类的搜索结果
   */
  async globalSearch(query, options = {}) {
    if (!query || query.trim() === '') {
      return {
        characters: [],
        weapons: [],
        artifacts: [],
        monsters: []
      };
    }

    try {
      const params = {
        q: query,
        ...options
      };

      const response = await this.get('/search', params);
      return response.data || response;
    } catch (error) {
      console.error('全局搜索失败:', error);
      throw error;
    }
  }

  /**
   * 搜索建议
   * 获取搜索关键词的自动补全建议
   *
   * @param {string} query - 搜索关键词
   * @param {number} limit - 建议数量限制
   * @returns {Promise<Array>} - 搜索建议列表
   */
  async getSearchSuggestions(query, limit = 10) {
    if (!query || query.trim() === '') {
      return [];
    }

    try {
      const params = {
        q: query,
        limit
      };

      const response = await this.get('/search/suggestions', params);
      return response.data || response;
    } catch (error) {
      console.error('获取搜索建议失败:', error);
      // 搜索建议失败不应该阻断用户操作
      return [];
    }
  }

  /**
   * 获取搜索历史
   *
   * @param {number} limit - 历史记录数量限制
   * @returns {Promise<Array>} - 搜索历史列表
   */
  async getSearchHistory(limit = 10) {
    try {
      // 从本地存储获取搜索历史
      const history = localStorage.getItem('searchHistory');
      if (!history) {
        return [];
      }

      const historyList = JSON.parse(history);
      return historyList.slice(0, limit);
    } catch (error) {
      console.error('获取搜索历史失败:', error);
      return [];
    }
  }

  /**
   * 保存搜索历史
   *
   * @param {string} query - 搜索关键词
   */
  async saveSearchHistory(query) {
    if (!query || query.trim() === '') {
      return;
    }

    try {
      const history = await this.getSearchHistory(100);

      // 去重并添加到开头
      const newHistory = [
        query,
        ...history.filter(item => item !== query)
      ].slice(0, 50); // 最多保存50条

      localStorage.setItem('searchHistory', JSON.stringify(newHistory));
    } catch (error) {
      console.error('保存搜索历史失败:', error);
    }
  }

  /**
   * 清空搜索历史
   */
  async clearSearchHistory() {
    try {
      localStorage.removeItem('searchHistory');
    } catch (error) {
      console.error('清空搜索历史失败:', error);
    }
  }

  /**
   * 删除单条搜索历史
   *
   * @param {string} query - 要删除的搜索关键词
   */
  async removeSearchHistoryItem(query) {
    try {
      const history = await this.getSearchHistory(100);
      const newHistory = history.filter(item => item !== query);
      localStorage.setItem('searchHistory', JSON.stringify(newHistory));
    } catch (error) {
      console.error('删除搜索历史失败:', error);
    }
  }

  /**
   * 获取热门搜索
   *
   * @param {number} limit - 返回数量限制
   * @returns {Promise<Array>} - 热门搜索列表
   */
  async getPopularSearches(limit = 10) {
    try {
      const response = await this.get('/search/popular', { limit });
      return response.data || response;
    } catch (error) {
      console.error('获取热门搜索失败:', error);
      return [];
    }
  }

  /**
   * 搜索统计
   * 记录搜索行为用于分析
   *
   * @param {string} query - 搜索关键词
   * @param {number} resultCount - 搜索结果数量
   */
  async logSearch(query, resultCount) {
    try {
      await this.post('/search/log', {
        query,
        result_count: resultCount,
        timestamp: new Date().toISOString()
      });
    } catch (error) {
      // 日志记录失败不应该影响用户体验
      console.warn('记录搜索日志失败:', error);
    }
  }
}

// 导出单例
const searchAPI = new SearchAPIService();
export default searchAPI;

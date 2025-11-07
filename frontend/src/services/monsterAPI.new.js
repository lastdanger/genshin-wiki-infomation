/**
 * 怪物API服务 (重构版本)
 */
import BaseAPIService from './base/BaseAPIService';

class MonsterAPIService extends BaseAPIService {
  constructor() {
    super('/api');
  }

  async getMonsterList(params = {}) {
    try {
      const response = await this.get('/monsters/', params);
      return response.data || response;
    } catch (error) {
      console.error('获取怪物列表失败:', error);
      throw error;
    }
  }

  async getMonsterDetail(monsterId) {
    if (!monsterId) throw new Error('怪物ID不能为空');
    try {
      const response = await this.get(`/monsters/${monsterId}`);
      return response.data || response;
    } catch (error) {
      console.error(`获取怪物详情失败 (ID: ${monsterId}):`, error);
      throw error;
    }
  }

  async searchMonsters(query, options = {}) {
    if (!query || query.trim() === '') return [];
    try {
      const params = { search: query, ...options };
      const response = await this.get('/monsters/search', params);
      return response.data || response;
    } catch (error) {
      console.error('搜索怪物失败:', error);
      throw error;
    }
  }

  async getMonstersByType(type, limit = 20) {
    if (!type) throw new Error('怪物类型不能为空');
    try {
      const response = await this.get(`/monsters/type/${type}`, { limit });
      return response.data || response;
    } catch (error) {
      console.error(`获取${type}类型怪物失败:`, error);
      throw error;
    }
  }

  async getMonsterFilters() {
    try {
      const response = await this.get('/monsters/filters');
      return response.data || response;
    } catch (error) {
      console.error('获取怪物筛选选项失败:', error);
      throw error;
    }
  }

  async getMonsterStats() {
    try {
      const response = await this.get('/monsters/stats');
      return response.data || response;
    } catch (error) {
      console.error('获取怪物统计失败:', error);
      throw error;
    }
  }

  // 管理功能
  async createMonster(monsterData) {
    try {
      const response = await this.post('/monsters/', monsterData);
      return response.data || response;
    } catch (error) {
      console.error('创建怪物失败:', error);
      throw error;
    }
  }

  async updateMonster(id, monsterData) {
    if (!id) throw new Error('怪物ID不能为空');
    try {
      const response = await this.put(`/monsters/${id}`, monsterData);
      return response.data || response;
    } catch (error) {
      console.error(`更新怪物失败 (ID: ${id}):`, error);
      throw error;
    }
  }

  async deleteMonster(id) {
    if (!id) throw new Error('怪物ID不能为空');
    try {
      const response = await this.delete(`/monsters/${id}`);
      return response.data || response;
    } catch (error) {
      console.error(`删除怪物失败 (ID: ${id}):`, error);
      throw error;
    }
  }

  // 辅助方法
  getMonsterTypeDisplay(type) {
    const typeMap = {
      'common': '普通怪物',
      'elite': '精英怪物',
      'boss': 'BOSS',
      'weekly_boss': '周本BOSS'
    };
    return typeMap[type] || type;
  }
}

const monsterAPI = new MonsterAPIService();
export default monsterAPI;

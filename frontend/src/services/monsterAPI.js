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

// 怪物工具函数
export const formatMonsterName = (monster) => {
  if (!monster) return '未知怪物';
  return monster.name || monster.name_en || '未知怪物';
};

export const getMonsterFamilyDisplay = (family) => {
  const familyMap = {
    'hilichurl': '丘丘人',
    'slime': '史莱姆',
    'treasure_hoarder': '盗宝团',
    'fatui': '愚人众',
    'abyss': '深渊',
    'automaton': '自律机关',
    'beast': '野兽',
    'elemental': '元素生物'
  };
  return familyMap[family] || family;
};

export const getMonsterCategoryColor = (category) => {
  const colorMap = {
    'common': '#95a5a6',
    'elite': '#3498db',
    'boss': '#e74c3c',
    'weekly_boss': '#9b59b6'
  };
  return colorMap[category] || '#95a5a6';
};

export const getMonsterTypeIcon = (type) => {
  const iconMap = {
    'common': '👾',
    'elite': '⚔️',
    'boss': '👹',
    'weekly_boss': '💀'
  };
  return iconMap[type] || '👾';
};

export const getMonsterElementColor = (element) => {
  const colorMap = {
    'pyro': '#ff6b6b',
    'hydro': '#4dabf7',
    'anemo': '#74c0fc',
    'electro': '#b197fc',
    'dendro': '#8ce99a',
    'cryo': '#91d5ff',
    'geo': '#ffd666',
    'physical': '#868e96'
  };
  return colorMap[element?.toLowerCase()] || '#868e96';
};

export const isMonsterBoss = (monster) => {
  return monster?.type === 'boss' || monster?.type === 'weekly_boss';
};

export const isMonsterElite = (monster) => {
  return monster?.type === 'elite';
};

export const getMonsterDifficultyDisplay = (level) => {
  if (level >= 90) return '极难';
  if (level >= 80) return '困难';
  if (level >= 70) return '中等';
  if (level >= 60) return '简单';
  return '很简单';
};

export const formatMonsterLevel = (level) => {
  return `Lv. ${level || 1}`;
};

export const formatExpReward = (exp) => {
  if (!exp) return '0';
  return exp.toLocaleString();
};

export const formatMoraReward = (mora) => {
  if (!mora) return '0';
  return mora.toLocaleString();
};

export const getResistanceLevel = (value) => {
  if (value >= 70) return '极高';
  if (value >= 50) return '高';
  if (value >= 30) return '中等';
  if (value >= 10) return '低';
  if (value > 0) return '很低';
  if (value === 0) return '无';
  return '弱点';
};

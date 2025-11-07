/**
 * 圣遗物API服务 (重构版本)
 */
import BaseAPIService from './base/BaseAPIService';

class ArtifactAPIService extends BaseAPIService {
  constructor() {
    super('/api');
  }

  async getArtifactList(params = {}) {
    try {
      const response = await this.get('/artifacts/', params);
      return response.data || response;
    } catch (error) {
      console.error('获取圣遗物列表失败:', error);
      throw error;
    }
  }

  async getArtifactDetail(artifactId) {
    if (!artifactId) throw new Error('圣遗物ID不能为空');
    try {
      const response = await this.get(`/artifacts/${artifactId}`);
      return response.data || response;
    } catch (error) {
      console.error(`获取圣遗物详情失败 (ID: ${artifactId}):`, error);
      throw error;
    }
  }

  async getArtifactSets() {
    try {
      const response = await this.get('/artifacts/sets');
      return response.data || response;
    } catch (error) {
      console.error('获取圣遗物套装失败:', error);
      throw error;
    }
  }

  async searchArtifacts(query, options = {}) {
    if (!query || query.trim() === '') return [];
    try {
      const params = { search: query, ...options };
      const response = await this.get('/artifacts/search', params);
      return response.data || response;
    } catch (error) {
      console.error('搜索圣遗物失败:', error);
      throw error;
    }
  }

  async getArtifactFilters() {
    try {
      const response = await this.get('/artifacts/filters');
      return response.data || response;
    } catch (error) {
      console.error('获取圣遗物筛选选项失败:', error);
      throw error;
    }
  }

  async getArtifactStats() {
    try {
      const response = await this.get('/artifacts/stats');
      return response.data || response;
    } catch (error) {
      console.error('获取圣遗物统计失败:', error);
      throw error;
    }
  }

  async getArtifactRecommendations(characterId) {
    if (!characterId) throw new Error('角色ID不能为空');
    try {
      const response = await this.get(`/artifacts/recommendations/${characterId}`);
      return response.data || response;
    } catch (error) {
      console.error(`获取角色${characterId}的圣遗物推荐失败:`, error);
      throw error;
    }
  }

  // 管理功能
  async createArtifact(artifactData) {
    try {
      const response = await this.post('/artifacts/', artifactData);
      return response.data || response;
    } catch (error) {
      console.error('创建圣遗物失败:', error);
      throw error;
    }
  }

  async updateArtifact(id, artifactData) {
    if (!id) throw new Error('圣遗物ID不能为空');
    try {
      const response = await this.put(`/artifacts/${id}`, artifactData);
      return response.data || response;
    } catch (error) {
      console.error(`更新圣遗物失败 (ID: ${id}):`, error);
      throw error;
    }
  }

  async deleteArtifact(id) {
    if (!id) throw new Error('圣遗物ID不能为空');
    try {
      const response = await this.delete(`/artifacts/${id}`);
      return response.data || response;
    } catch (error) {
      console.error(`删除圣遗物失败 (ID: ${id}):`, error);
      throw error;
    }
  }

  // 辅助方法
  getSetBonusDisplay(setName) {
    // 可以添加套装效果的显示逻辑
    return setName;
  }

  getRarityDisplay(rarity) {
    return '★'.repeat(rarity);
  }
}

const artifactAPI = new ArtifactAPIService();
export default artifactAPI;

// 圣遗物常量
export const ARTIFACT_SLOTS = {
  FLOWER: 'flower',
  PLUME: 'plume',
  SANDS: 'sands',
  GOBLET: 'goblet',
  CIRCLET: 'circlet'
};

export const MAIN_STAT_TYPES = {
  HP: 'HP',
  ATK: 'ATK',
  DEF: 'DEF',
  HP_PERCENT: 'HP%',
  ATK_PERCENT: 'ATK%',
  DEF_PERCENT: 'DEF%',
  ELEMENTAL_MASTERY: 'Elemental Mastery',
  ENERGY_RECHARGE: 'Energy Recharge%',
  CRIT_RATE: 'CRIT Rate%',
  CRIT_DMG: 'CRIT DMG%',
  HEALING_BONUS: 'Healing Bonus%',
  ELEMENTAL_DMG_BONUS: 'Elemental DMG Bonus%'
};

export const SOURCES = {
  DOMAIN: 'domain',
  BOSS: 'boss',
  CRAFTING: 'crafting'
};

export const RARITIES = [1, 2, 3, 4, 5];

// 圣遗物工具函数
export const artifactUtils = {
  /**
   * 获取部位显示名称
   */
  getSlotDisplayName: (slot) => {
    const slotNames = {
      [ARTIFACT_SLOTS.FLOWER]: '生之花',
      [ARTIFACT_SLOTS.PLUME]: '死之羽',
      [ARTIFACT_SLOTS.SANDS]: '时之沙',
      [ARTIFACT_SLOTS.GOBLET]: '空之杯',
      [ARTIFACT_SLOTS.CIRCLET]: '理之冠'
    };
    return slotNames[slot] || slot;
  },

  /**
   * 获取稀有度星级显示
   */
  getRarityStars: (rarity) => {
    return '★'.repeat(rarity);
  },

  /**
   * 获取稀有度样式类名
   */
  getRarityColorClass: (rarity) => {
    return `rarity-${rarity}`;
  },

  /**
   * 格式化主属性显示
   */
  formatMainStat: (type, value) => {
    return `${type} ${value}`;
  },

  /**
   * 格式化副属性列表
   */
  formatSubStats: (subStats) => {
    if (!subStats || !Array.isArray(subStats)) return [];
    return subStats.map(stat => ({
      ...stat,
      display: `${stat.stat_type} +${stat.stat_value}`
    }));
  },

  /**
   * 获取套装效果描述
   */
  getSetBonusDescription: (setBonuses) => {
    if (!setBonuses || !Array.isArray(setBonuses)) return [];
    return setBonuses;
  }
};

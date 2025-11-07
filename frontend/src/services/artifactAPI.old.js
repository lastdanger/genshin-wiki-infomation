/**
 * 圣遗物API服务
 *
 * 提供圣遗物相关的所有API调用封装
 */
import { BaseAPI, apiClient } from './api';

class ArtifactAPI extends BaseAPI {
  constructor() {
    super('/artifacts');
  }

  /**
   * 获取圣遗物列表
   * @param {Object} params - 查询参数
   * @param {number} params.page - 页码
   * @param {number} params.per_page - 每页数量
   * @param {string} params.set_name - 套装名称过滤
   * @param {string} params.slot - 部位过滤
   * @param {number} params.rarity - 稀有度过滤
   * @param {string} params.source - 获取方式过滤
   * @param {string} params.main_stat_type - 主属性类型过滤
   * @param {string} params.search - 搜索关键词
   * @param {string} params.sort_by - 排序字段
   * @param {string} params.sort_order - 排序方向
   * @returns {Promise} API响应
   */
  async getArtifactList(params = {}) {
    try {
      // 设置默认参数
      const defaultParams = {
        page: 1,
        per_page: 20,
        sort_by: 'name',
        sort_order: 'asc',
        ...params
      };

      // 过滤空值参数
      const filteredParams = Object.keys(defaultParams).reduce((acc, key) => {
        const value = defaultParams[key];
        if (value !== null && value !== undefined && value !== '') {
          acc[key] = value;
        }
        return acc;
      }, {});

      const response = await this.getList(filteredParams);
      return response;
    } catch (error) {
      console.error('获取圣遗物列表失败:', error);
      throw error;
    }
  }

  /**
   * 获取圣遗物详情
   * @param {number} artifactId - 圣遗物ID
   * @returns {Promise} 圣遗物详情
   */
  async getArtifactDetail(artifactId) {
    try {
      const response = await this.getDetail(artifactId);
      return response;
    } catch (error) {
      console.error(`获取圣遗物详情失败 (ID: ${artifactId}):`, error);
      throw error;
    }
  }

  /**
   * 搜索圣遗物
   * @param {string} query - 搜索关键词
   * @param {number} limit - 结果数量限制
   * @returns {Promise} 搜索结果
   */
  async searchArtifacts(query, limit = 20) {
    try {
      const response = await this.search(query, { limit });
      return response;
    } catch (error) {
      console.error('搜索圣遗物失败:', error);
      throw error;
    }
  }

  /**
   * 根据套装名称获取圣遗物
   * @param {string} setName - 套装名称
   * @param {number} limit - 数量限制
   * @returns {Promise} 圣遗物列表
   */
  async getArtifactsBySet(setName, limit = 20) {
    try {
      const response = await apiClient.get(`/artifacts/set/${encodeURIComponent(setName)}`, {
        params: { limit }
      });
      return response.data;
    } catch (error) {
      console.error(`获取套装圣遗物失败 (套装: ${setName}):`, error);
      throw this.handleError(error);
    }
  }

  /**
   * 根据部位获取圣遗物
   * @param {string} slot - 圣遗物部位
   * @param {number} limit - 数量限制
   * @returns {Promise} 圣遗物列表
   */
  async getArtifactsBySlot(slot, limit = 20) {
    try {
      const response = await apiClient.get(`/artifacts/slot/${slot}`, {
        params: { limit }
      });
      return response.data;
    } catch (error) {
      console.error(`获取部位圣遗物失败 (部位: ${slot}):`, error);
      throw this.handleError(error);
    }
  }

  /**
   * 获取圣遗物统计信息
   * @returns {Promise} 统计数据
   */
  async getArtifactStats() {
    try {
      const response = await apiClient.get('/artifacts/stats/overview');
      return response.data;
    } catch (error) {
      console.error('获取圣遗物统计失败:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 获取过滤选项
   * @returns {Promise} 过滤选项数据
   */
  async getFilterOptions() {
    try {
      const response = await apiClient.get('/artifacts/filters/options');
      return response.data;
    } catch (error) {
      console.error('获取过滤选项失败:', error);
      throw this.handleError(error);
    }
  }
}

// 圣遗物相关常量
export const ARTIFACT_SLOTS = {
  FLOWER: 'flower',
  PLUME: 'plume',
  SANDS: 'sands',
  GOBLET: 'goblet',
  CIRCLET: 'circlet'
};

export const MAIN_STAT_TYPES = {
  HP: 'HP',
  HP_PERCENT: 'HP%',
  ATK: 'ATK',
  ATK_PERCENT: 'ATK%',
  DEF: 'DEF',
  DEF_PERCENT: 'DEF%',
  ENERGY_RECHARGE: 'Energy Recharge',
  ELEMENTAL_MASTERY: 'Elemental Mastery',
  CRIT_RATE: 'CRIT Rate',
  CRIT_DMG: 'CRIT DMG',
  HEALING_BONUS: 'Healing Bonus',
  PYRO_DMG: 'Pyro DMG Bonus',
  HYDRO_DMG: 'Hydro DMG Bonus',
  ANEMO_DMG: 'Anemo DMG Bonus',
  ELECTRO_DMG: 'Electro DMG Bonus',
  DENDRO_DMG: 'Dendro DMG Bonus',
  CRYO_DMG: 'Cryo DMG Bonus',
  GEO_DMG: 'Geo DMG Bonus',
  PHYSICAL_DMG: 'Physical DMG Bonus'
};

export const SOURCES = {
  DOMAIN: '副本',
  WORLD_BOSS: '世界BOSS',
  WEEKLY_BOSS: '周本BOSS',
  EVENT: '活动',
  SHOP: '商店',
  CRAFT: '合成'
};

export const RARITIES = [3, 4, 5];

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
  getSetEffectDescription: (setEffects) => {
    if (!setEffects) return '';

    const effects = [];
    if (setEffects['2']) {
      effects.push(`2件套：${setEffects['2'].description}`);
    }
    if (setEffects['4']) {
      effects.push(`4件套：${setEffects['4'].description}`);
    }

    return effects.join('\n');
  },

  /**
   * 判断是否为完整套装
   */
  isCompleteSet: (artifacts) => {
    return artifacts && artifacts.length >= 4;
  },

  /**
   * 获取套装完整度百分比
   */
  getSetCompleteness: (artifacts) => {
    const count = artifacts ? artifacts.length : 0;
    return Math.min(count / 5 * 100, 100);
  }
};

// 在ArtifactAPI类中添加CRUD方法
ArtifactAPI.prototype.createArtifact = async function(artifactData) {
  try {
    return await this.create(artifactData);
  } catch (error) {
    console.error('创建圣遗物失败:', error);
    throw error;
  }
};

ArtifactAPI.prototype.updateArtifact = async function(artifactId, artifactData) {
  try {
    return await this.update(artifactId, artifactData);
  } catch (error) {
    console.error('更新圣遗物失败:', error);
    throw error;
  }
};

ArtifactAPI.prototype.deleteArtifact = async function(artifactId) {
  try {
    return await this.delete(artifactId);
  } catch (error) {
    console.error('删除圣遗物失败:', error);
    throw error;
  }
};

// 创建并导出API实例
const artifactAPI = new ArtifactAPI();
export default artifactAPI;
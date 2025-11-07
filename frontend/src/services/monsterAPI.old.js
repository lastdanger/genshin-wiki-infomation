/**
 * 怪物 API 服务
 *
 * 提供怪物相关的API接口调用
 */

import { BaseAPI, apiClient } from './api';

class MonsterAPI extends BaseAPI {
  constructor() {
    super('/monsters');
  }

  /**
   * 获取怪物列表
   * @param {Object} params 查询参数
   * @returns {Promise} 怪物列表数据
   */
  async getMonsterList(params = {}) {
    return this.getList(params);
  }

  /**
   * 获取怪物详情
   * @param {number} id 怪物ID
   * @returns {Promise} 怪物详情数据
   */
  async getMonsterById(id) {
    return this.getDetail(id);
  }

  /**
   * 搜索怪物
   * @param {string} query 搜索关键词
   * @param {number} limit 返回数量限制
   * @returns {Promise} 搜索结果
   */
  async searchMonsters(query, limit = 20) {
    return this.search(query, { limit });
  }

  /**
   * 获取怪物统计信息
   * @returns {Promise} 统计数据
   */
  async getMonsterStats() {
    try {
      const response = await apiClient.get('/monsters/stats/overview');
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  /**
   * 根据类别获取怪物
   * @param {string} category 怪物类别
   * @param {number} limit 返回数量限制
   * @returns {Promise} 怪物列表
   */
  async getMonstersByCategory(category, limit = 20) {
    try {
      const response = await apiClient.get(`/monsters/category/${category}`, {
        params: { limit }
      });
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  /**
   * 根据族群获取怪物
   * @param {string} family 怪物族群
   * @param {number} limit 返回数量限制
   * @returns {Promise} 怪物列表
   */
  async getMonstersByFamily(family, limit = 20) {
    try {
      const response = await apiClient.get(`/monsters/family/${family}`, {
        params: { limit }
      });
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  /**
   * 根据元素获取怪物
   * @param {string} element 元素类型
   * @param {number} limit 返回数量限制
   * @returns {Promise} 怪物列表
   */
  async getMonstersByElement(element, limit = 20) {
    try {
      const response = await apiClient.get(`/monsters/element/${element}`, {
        params: { limit }
      });
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  /**
   * 根据地区获取怪物
   * @param {string} region 地区名称
   * @param {number} limit 返回数量限制
   * @returns {Promise} 怪物列表
   */
  async getMonstersByRegion(region, limit = 20) {
    try {
      const response = await apiClient.get(`/monsters/region/${region}`, {
        params: { limit }
      });
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  /**
   * 根据等级范围获取怪物
   * @param {number} minLevel 最小等级
   * @param {number} maxLevel 最大等级
   * @param {number} limit 返回数量限制
   * @returns {Promise} 怪物列表
   */
  async getMonstersByLevelRange(minLevel, maxLevel, limit = 20) {
    try {
      const response = await apiClient.get('/monsters/level/range', {
        params: { min_level: minLevel, max_level: maxLevel, limit }
      });
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  /**
   * 获取过滤选项
   * @returns {Promise} 可用的过滤选项
   */
  async getFilterOptions() {
    try {
      const response = await apiClient.get('/monsters/filters/options');
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  /**
   * 创建新怪物
   * @param {Object} monsterData - 怪物数据
   * @returns {Promise} 创建结果
   */
  async createMonster(monsterData) {
    try {
      return await this.create(monsterData);
    } catch (error) {
      console.error('创建怪物失败:', error);
      throw error;
    }
  }

  /**
   * 更新怪物信息
   * @param {number} monsterId - 怪物ID
   * @param {Object} monsterData - 怪物数据
   * @returns {Promise} 更新结果
   */
  async updateMonster(monsterId, monsterData) {
    try {
      return await this.update(monsterId, monsterData);
    } catch (error) {
      console.error('更新怪物失败:', error);
      throw error;
    }
  }

  /**
   * 删除怪物
   * @param {number} monsterId - 怪物ID
   * @returns {Promise} 删除结果
   */
  async deleteMonster(monsterId) {
    try {
      return await this.delete(monsterId);
    } catch (error) {
      console.error('删除怪物失败:', error);
      throw error;
    }
  }

  /**
   * 获取怪物详情 (增强版本，与其他API保持一致)
   * @param {number} monsterId - 怪物ID
   * @returns {Promise} 怪物详情
   */
  async getMonsterDetail(monsterId) {
    try {
      const response = await this.getDetail(monsterId);
      return response;
    } catch (error) {
      console.error(`获取怪物详情失败 (ID: ${monsterId}):`, error);
      throw error;
    }
  }

  /**
   * 增强的怪物列表获取 (支持更多参数)
   * @param {Object} params - 查询参数
   * @param {number} params.page - 页码
   * @param {number} params.per_page - 每页数量
   * @param {string} params.monster_type - 怪物类型过滤
   * @param {string} params.category - 怪物分类过滤
   * @param {string} params.element - 元素类型过滤
   * @param {string} params.region - 地区过滤
   * @param {string} params.search - 搜索关键词
   * @param {string} params.sort_by - 排序字段
   * @param {string} params.sort_order - 排序方向
   * @returns {Promise} API响应
   */
  async getMonsterListEnhanced(params = {}) {
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
      console.error('获取怪物列表失败:', error);
      throw error;
    }
  }
}

// 实用函数

/**
 * 格式化怪物名称
 * @param {Object} monster 怪物数据
 * @returns {string} 格式化后的名称
 */
export const formatMonsterName = (monster) => {
  if (!monster) return '';
  return monster.name || monster.name_en || `Monster #${monster.id}`;
};

/**
 * 获取怪物类别颜色
 * @param {string} category 怪物类别
 * @returns {string} 对应的颜色类
 */
export const getMonsterCategoryColor = (category) => {
  const colors = {
    '普通怪物': 'normal',
    '精英怪物': 'elite',
    '周本Boss': 'weekly-boss',
    '世界Boss': 'world-boss'
  };
  return colors[category] || 'normal';
};

/**
 * 获取怪物元素颜色
 * @param {string} element 元素类型
 * @returns {string} 对应的颜色类
 */
export const getMonsterElementColor = (element) => {
  if (!element) return 'physical';

  const colors = {
    'Pyro': 'pyro',
    'Hydro': 'hydro',
    'Anemo': 'anemo',
    'Electro': 'electro',
    'Dendro': 'dendro',
    'Cryo': 'cryo',
    'Geo': 'geo'
  };
  return colors[element] || 'physical';
};

/**
 * 格式化怪物等级范围
 * @param {number} level 怪物等级
 * @returns {string} 格式化的等级范围
 */
export const formatMonsterLevel = (level) => {
  if (!level) return 'Lv.1';
  return `Lv.${level}`;
};

/**
 * 格式化怪物掉落率
 * @param {number} dropRate 掉落率
 * @returns {string} 格式化的掉落率
 */
export const formatDropRate = (dropRate) => {
  if (!dropRate) return '0%';
  return `${dropRate}%`;
};

/**
 * 获取怪物弱点提示
 * @param {Array} weakPoints 弱点列表
 * @returns {string} 弱点提示文本
 */
export const getWeakPointTips = (weakPoints) => {
  if (!weakPoints || weakPoints.length === 0) return '无明显弱点';
  return weakPoints.join('、');
};

/**
 * 获取怪物抗性等级
 * @param {number} resistance 抗性值
 * @returns {Object} 抗性等级和颜色
 */
export const getResistanceLevel = (resistance) => {
  if (resistance >= 50) {
    return { level: '高抗性', color: 'high-resistance' };
  } else if (resistance > 0) {
    return { level: '抗性', color: 'resistance' };
  } else if (resistance < 0) {
    return { level: '弱点', color: 'weakness' };
  } else {
    return { level: '普通', color: 'normal' };
  }
};

/**
 * 检查怪物是否为Boss
 * @param {Object} monster 怪物数据
 * @returns {boolean} 是否为Boss
 */
export const isMonsterBoss = (monster) => {
  return monster?.is_boss || ['周本Boss', '世界Boss'].includes(monster?.category);
};

/**
 * 检查怪物是否为精英
 * @param {Object} monster 怪物数据
 * @returns {boolean} 是否为精英怪物
 */
export const isMonsterElite = (monster) => {
  return monster?.is_elite || monster?.category === '精英怪物';
};

/**
 * 格式化怪物经验奖励
 * @param {number} expReward 经验奖励
 * @returns {string} 格式化的经验值
 */
export const formatExpReward = (expReward) => {
  if (!expReward) return '0 EXP';
  return `${expReward} EXP`;
};

/**
 * 格式化摩拉奖励
 * @param {number} moraReward 摩拉奖励
 * @returns {string} 格式化的摩拉值
 */
export const formatMoraReward = (moraReward) => {
  if (!moraReward) return '0 摩拉';
  return `${moraReward} 摩拉`;
};

// 创建并导出API实例
const monsterAPI = new MonsterAPI();
export default monsterAPI;
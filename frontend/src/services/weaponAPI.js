/**
 * 武器API服务 (重构版本)
 *
 * 使用新的BaseAPIService架构，提供：
 * - 统一的错误处理
 * - 自动重试机制
 * - 请求/响应拦截
 * - 完整的CRUD操作
 */
import BaseAPIService from './base/BaseAPIService';

class WeaponAPIService extends BaseAPIService {
  constructor() {
    super('/api');
  }

  /**
   * 获取武器列表
   *
   * @param {Object} params - 查询参数
   * @param {number} params.page - 页码
   * @param {number} params.per_page - 每页数量
   * @param {string} params.weapon_type - 武器类型过滤
   * @param {number} params.rarity - 稀有度过滤
   * @param {string} params.source - 获取方式过滤
   * @param {string} params.search - 搜索关键词
   * @param {string} params.sort_by - 排序字段
   * @param {string} params.sort_order - 排序方向
   * @returns {Promise<Object>} - { weapons, total, page, pages }
   */
  async getWeaponList(params = {}) {
    try {
      const response = await this.get('/weapons/', params);
      return response.data || response;
    } catch (error) {
      console.error('获取武器列表失败:', error);
      throw error;
    }
  }

  /**
   * 获取武器详情
   *
   * @param {string|number} weaponId - 武器ID
   * @returns {Promise<Object>} - 武器详情
   */
  async getWeaponDetail(weaponId) {
    if (!weaponId) {
      throw new Error('武器ID不能为空');
    }

    try {
      const response = await this.get(`/weapons/${weaponId}`);
      return response.data || response;
    } catch (error) {
      console.error(`获取武器详情失败 (ID: ${weaponId}):`, error);
      throw error;
    }
  }

  /**
   * 搜索武器
   *
   * @param {string} query - 搜索关键词
   * @param {Object} options - 搜索选项
   * @returns {Promise<Array>} - 匹配的武器列表
   */
  async searchWeapons(query, options = {}) {
    if (!query || query.trim() === '') {
      return [];
    }

    try {
      const params = { search: query, ...options };
      const response = await this.get('/weapons/search', params);
      return response.data || response;
    } catch (error) {
      console.error('搜索武器失败:', error);
      throw error;
    }
  }

  /**
   * 根据武器类型获取武器列表
   *
   * @param {string} weaponType - 武器类型
   * @param {number} limit - 结果限制数量
   * @returns {Promise<Array>} - 武器列表
   */
  async getWeaponsByType(weaponType, limit = 20) {
    if (!weaponType) {
      throw new Error('武器类型不能为空');
    }

    try {
      const response = await this.get(`/weapons/type/${weaponType}`, { limit });
      return response.data || response;
    } catch (error) {
      console.error(`获取${weaponType}类型武器失败:`, error);
      throw error;
    }
  }

  /**
   * 根据稀有度获取武器列表
   *
   * @param {number} rarity - 稀有度
   * @param {number} limit - 结果限制数量
   * @returns {Promise<Array>} - 武器列表
   */
  async getWeaponsByRarity(rarity, limit = 20) {
    if (!rarity) {
      throw new Error('稀有度不能为空');
    }

    try {
      const response = await this.get(`/weapons/rarity/${rarity}`, { limit });
      return response.data || response;
    } catch (error) {
      console.error(`获取${rarity}星武器失败:`, error);
      throw error;
    }
  }

  /**
   * 获取武器筛选选项
   *
   * @returns {Promise<Object>} - 筛选选项
   */
  async getWeaponFilters() {
    try {
      const response = await this.get('/weapons/filters/options');
      return response.data || response;
    } catch (error) {
      console.error('获取武器筛选选项失败:', error);
      throw error;
    }
  }

  /**
   * 获取武器统计信息
   *
   * @returns {Promise<Object>} - 统计数据
   */
  async getWeaponStats() {
    try {
      const response = await this.get('/weapons/stats/overview');
      return response.data || response;
    } catch (error) {
      console.error('获取武器统计失败:', error);
      throw error;
    }
  }

  /**
   * 获取武器对比数据
   *
   * @param {Array<string|number>} weaponIds - 武器ID数组
   * @returns {Promise<Object>} - 对比数据
   */
  async compareWeapons(weaponIds) {
    if (!weaponIds || weaponIds.length === 0) {
      throw new Error('武器ID列表不能为空');
    }

    if (weaponIds.length > 5) {
      throw new Error('最多只能对比5把武器');
    }

    try {
      const response = await this.post('/weapons/compare', { weapon_ids: weaponIds });
      return response.data || response;
    } catch (error) {
      console.error('武器对比失败:', error);
      throw error;
    }
  }

  /**
   * 获取武器推荐（根据角色）
   *
   * @param {string|number} characterId - 角色ID
   * @returns {Promise<Array>} - 推荐武器列表
   */
  async getWeaponRecommendations(characterId) {
    if (!characterId) {
      throw new Error('角色ID不能为空');
    }

    try {
      const response = await this.get(`/weapons/recommendations/${characterId}`);
      return response.data || response;
    } catch (error) {
      console.error(`获取角色${characterId}的武器推荐失败:`, error);
      throw error;
    }
  }

  // ==================== 管理功能 ====================

  /**
   * 创建武器（管理员功能）
   *
   * @param {Object} weaponData - 武器数据
   * @returns {Promise<Object>} - 创建的武器
   */
  async createWeapon(weaponData) {
    try {
      const response = await this.post('/weapons/', weaponData);
      return response.data || response;
    } catch (error) {
      console.error('创建武器失败:', error);
      throw error;
    }
  }

  /**
   * 更新武器（管理员功能）
   *
   * @param {string|number} id - 武器ID
   * @param {Object} weaponData - 更新的武器数据
   * @returns {Promise<Object>} - 更新后的武器
   */
  async updateWeapon(id, weaponData) {
    if (!id) {
      throw new Error('武器ID不能为空');
    }

    try {
      const response = await this.put(`/weapons/${id}`, weaponData);
      return response.data || response;
    } catch (error) {
      console.error(`更新武器失败 (ID: ${id}):`, error);
      throw error;
    }
  }

  /**
   * 删除武器（管理员功能）
   *
   * @param {string|number} id - 武器ID
   * @returns {Promise<Object>} - 删除结果
   */
  async deleteWeapon(id) {
    if (!id) {
      throw new Error('武器ID不能为空');
    }

    try {
      const response = await this.delete(`/weapons/${id}`);
      return response.data || response;
    } catch (error) {
      console.error(`删除武器失败 (ID: ${id}):`, error);
      throw error;
    }
  }

  // ==================== 辅助方法 ====================

  /**
   * 获取武器类型的显示名称
   *
   * @param {string} weaponType - 武器类型
   * @returns {string} - 中文名称
   */
  getWeaponTypeDisplay(weaponType) {
    const typeMap = {
      'Sword': '单手剑',
      'sword': '单手剑',
      'Claymore': '双手剑',
      'claymore': '双手剑',
      'Polearm': '长柄武器',
      'polearm': '长柄武器',
      'Bow': '弓',
      'bow': '弓',
      'Catalyst': '法器',
      'catalyst': '法器'
    };
    return typeMap[weaponType] || weaponType;
  }

  /**
   * 获取稀有度显示
   *
   * @param {number} rarity - 稀有度
   * @returns {string} - 显示文本
   */
  getRarityDisplay(rarity) {
    return '★'.repeat(rarity);
  }

  /**
   * 获取武器类型的图标类名
   *
   * @param {string} weaponType - 武器类型
   * @returns {string} - CSS类名
   */
  getWeaponTypeIcon(weaponType) {
    const iconMap = {
      'Sword': 'weapon-sword',
      'sword': 'weapon-sword',
      'Claymore': 'weapon-claymore',
      'claymore': 'weapon-claymore',
      'Polearm': 'weapon-polearm',
      'polearm': 'weapon-polearm',
      'Bow': 'weapon-bow',
      'bow': 'weapon-bow',
      'Catalyst': 'weapon-catalyst',
      'catalyst': 'weapon-catalyst'
    };
    return iconMap[weaponType] || 'weapon-default';
  }

  /**
   * 获取稀有度的CSS类名
   *
   * @param {number} rarity - 稀有度
   * @returns {string} - CSS类名
   */
  getRarityClass(rarity) {
    return `rarity-${rarity}`;
  }

  /**
   * 格式化武器属性值
   *
   * @param {string} statType - 属性类型
   * @param {string} statValue - 属性值
   * @returns {string} - 格式化后的值
   */
  formatStatValue(statType, statValue) {
    if (!statValue) return '';

    // 百分比属性
    const percentStats = ['CRIT Rate', 'CRIT DMG', 'Energy Recharge', 'Elemental Mastery'];
    if (percentStats.some(stat => statType?.includes(stat))) {
      return `${statValue}%`;
    }

    return statValue;
  }

  /**
   * 获取武器获取方式的显示颜色
   *
   * @param {string} source - 获取方式
   * @returns {string} - 颜色名称
   */
  getSourceColor(source) {
    const colorMap = {
      '祈愿': 'purple',
      '锻造': 'blue',
      '活动': 'orange',
      '商店': 'green',
      '任务奖励': 'cyan',
      '成就奖励': 'gold'
    };
    return colorMap[source] || 'default';
  }

  /**
   * 检查是否为五星武器
   *
   * @param {number} rarity - 稀有度
   * @returns {boolean}
   */
  isFiveStar(rarity) {
    return rarity === 5;
  }

  /**
   * 检查是否为四星武器
   *
   * @param {number} rarity - 稀有度
   * @returns {boolean}
   */
  isFourStar(rarity) {
    return rarity === 4;
  }
}

// 导出单例
const weaponAPI = new WeaponAPIService();
export default weaponAPI;

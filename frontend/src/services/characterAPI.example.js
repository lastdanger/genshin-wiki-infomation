/**
 * 角色API服务
 *
 * 提供角色相关的所有API调用方法
 * 这是使用新架构重构后的示例版本
 *
 * 使用方法:
 * import characterAPI from '@/services/characterAPI';
 * const characters = await characterAPI.getCharacterList({ element: '火' });
 */
import BaseAPIService from './base/BaseAPIService';

class CharacterAPIService extends BaseAPIService {
  constructor() {
    super('/api'); // 设置baseURL
  }

  /**
   * 获取角色列表
   *
   * @param {Object} filters - 筛选条件
   * @param {string} filters.search - 搜索关键词
   * @param {string} filters.element - 元素类型
   * @param {string} filters.weapon_type - 武器类型
   * @param {number} filters.rarity - 稀有度
   * @param {string} filters.sort_by - 排序字段
   * @param {string} filters.sort_order - 排序方向
   * @param {number} filters.page - 页码
   * @param {number} filters.per_page - 每页数量
   * @returns {Promise<Object>} - { characters, total, page, pages }
   */
  async getCharacterList(filters = {}) {
    try {
      const response = await this.get('/characters/', filters);
      return response.data || response;
    } catch (error) {
      console.error('获取角色列表失败:', error);
      throw error;
    }
  }

  /**
   * 获取角色详情
   *
   * @param {string|number} id - 角色ID
   * @returns {Promise<Object>} - 角色详细信息
   */
  async getCharacterDetail(id) {
    if (!id) {
      throw new Error('角色ID不能为空');
    }

    try {
      const response = await this.get(`/characters/${id}`);
      return response.data || response;
    } catch (error) {
      console.error(`获取角色详情失败 (ID: ${id}):`, error);
      throw error;
    }
  }

  /**
   * 搜索角色
   *
   * @param {string} query - 搜索关键词
   * @param {Object} options - 搜索选项
   * @returns {Promise<Array>} - 匹配的角色列表
   */
  async searchCharacters(query, options = {}) {
    if (!query || query.trim() === '') {
      return [];
    }

    try {
      const response = await this.get('/characters/search', {
        q: query,
        ...options
      });
      return response.data || response;
    } catch (error) {
      console.error('搜索角色失败:', error);
      throw error;
    }
  }

  /**
   * 获取角色的技能信息
   *
   * @param {string|number} characterId - 角色ID
   * @returns {Promise<Array>} - 技能列表
   */
  async getCharacterSkills(characterId) {
    if (!characterId) {
      throw new Error('角色ID不能为空');
    }

    try {
      const response = await this.get(`/characters/${characterId}/skills`);
      return response.data || response;
    } catch (error) {
      console.error(`获取角色技能失败 (ID: ${characterId}):`, error);
      throw error;
    }
  }

  /**
   * 获取角色的天赋信息
   *
   * @param {string|number} characterId - 角色ID
   * @returns {Promise<Array>} - 天赋列表
   */
  async getCharacterTalents(characterId) {
    if (!characterId) {
      throw new Error('角色ID不能为空');
    }

    try {
      const response = await this.get(`/characters/${characterId}/talents`);
      return response.data || response;
    } catch (error) {
      console.error(`获取角色天赋失败 (ID: ${characterId}):`, error);
      throw error;
    }
  }

  /**
   * 获取角色筛选选项
   * （元素类型、武器类型、稀有度等）
   *
   * @returns {Promise<Object>} - 筛选选项
   */
  async getCharacterFilters() {
    try {
      const response = await this.get('/characters/filters');
      return response.data || response;
    } catch (error) {
      console.error('获取筛选选项失败:', error);
      throw error;
    }
  }

  /**
   * 获取角色统计信息
   *
   * @returns {Promise<Object>} - 统计数据
   */
  async getCharacterStats() {
    try {
      const response = await this.get('/characters/stats');
      return response.data || response;
    } catch (error) {
      console.error('获取角色统计失败:', error);
      throw error;
    }
  }

  // ==================== 管理功能 ====================

  /**
   * 创建角色（管理员功能）
   *
   * @param {Object} characterData - 角色数据
   * @returns {Promise<Object>} - 创建的角色
   */
  async createCharacter(characterData) {
    try {
      const response = await this.post('/characters/', characterData);
      return response.data || response;
    } catch (error) {
      console.error('创建角色失败:', error);
      throw error;
    }
  }

  /**
   * 更新角色（管理员功能）
   *
   * @param {string|number} id - 角色ID
   * @param {Object} characterData - 更新的角色数据
   * @returns {Promise<Object>} - 更新后的角色
   */
  async updateCharacter(id, characterData) {
    if (!id) {
      throw new Error('角色ID不能为空');
    }

    try {
      const response = await this.put(`/characters/${id}`, characterData);
      return response.data || response;
    } catch (error) {
      console.error(`更新角色失败 (ID: ${id}):`, error);
      throw error;
    }
  }

  /**
   * 部分更新角色（管理员功能）
   *
   * @param {string|number} id - 角色ID
   * @param {Object} partialData - 部分更新的数据
   * @returns {Promise<Object>} - 更新后的角色
   */
  async patchCharacter(id, partialData) {
    if (!id) {
      throw new Error('角色ID不能为空');
    }

    try {
      const response = await this.patch(`/characters/${id}`, partialData);
      return response.data || response;
    } catch (error) {
      console.error(`部分更新角色失败 (ID: ${id}):`, error);
      throw error;
    }
  }

  /**
   * 删除角色（管理员功能）
   *
   * @param {string|number} id - 角色ID
   * @returns {Promise<Object>} - 删除结果
   */
  async deleteCharacter(id) {
    if (!id) {
      throw new Error('角色ID不能为空');
    }

    try {
      const response = await this.delete(`/characters/${id}`);
      return response.data || response;
    } catch (error) {
      console.error(`删除角色失败 (ID: ${id}):`, error);
      throw error;
    }
  }

  /**
   * 批量删除角色（管理员功能）
   *
   * @param {Array<string|number>} ids - 角色ID数组
   * @returns {Promise<Object>} - 删除结果
   */
  async batchDeleteCharacters(ids) {
    if (!ids || ids.length === 0) {
      throw new Error('角色ID列表不能为空');
    }

    try {
      const response = await this.post('/characters/batch-delete', { ids });
      return response.data || response;
    } catch (error) {
      console.error('批量删除角色失败:', error);
      throw error;
    }
  }

  // ==================== 辅助方法 ====================

  /**
   * 获取元素类型的显示名称
   *
   * @param {string} element - 元素类型英文
   * @returns {string} - 中文名称
   */
  getElementDisplay(element) {
    const elementMap = {
      'pyro': '火',
      'hydro': '水',
      'anemo': '风',
      'electro': '雷',
      'dendro': '草',
      'cryo': '冰',
      'geo': '岩'
    };
    return elementMap[element] || element;
  }

  /**
   * 获取武器类型的显示名称
   *
   * @param {string} weaponType - 武器类型英文
   * @returns {string} - 中文名称
   */
  getWeaponTypeDisplay(weaponType) {
    const weaponMap = {
      'sword': '单手剑',
      'claymore': '双手剑',
      'polearm': '长柄武器',
      'bow': '弓',
      'catalyst': '法器'
    };
    return weaponMap[weaponType] || weaponType;
  }

  /**
   * 获取稀有度的显示文本
   *
   * @param {number} rarity - 稀有度
   * @returns {string} - 显示文本
   */
  getRarityDisplay(rarity) {
    return `${'★'.repeat(rarity)}`;
  }
}

// 导出单例
const characterAPI = new CharacterAPIService();
export default characterAPI;

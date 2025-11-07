/**
 * 角色API服务 (重构版本)
 *
 * 使用新的BaseAPIService架构，提供：
 * - 统一的错误处理
 * - 自动重试机制
 * - 请求/响应拦截
 * - 完整的CRUD操作
 */
import BaseAPIService from './base/BaseAPIService';

class CharacterAPIService extends BaseAPIService {
  constructor() {
    super('/api'); // 设置baseURL
  }

  /**
   * 获取角色列表
   *
   * @param {Object} params - 查询参数
   * @param {number} params.page - 页码
   * @param {number} params.per_page - 每页数量
   * @param {string} params.element - 元素类型过滤
   * @param {string} params.weapon_type - 武器类型过滤
   * @param {number} params.rarity - 稀有度过滤
   * @param {string} params.region - 地区过滤
   * @param {string} params.search - 搜索关键词
   * @param {string} params.sort_by - 排序字段
   * @param {string} params.sort_order - 排序方向
   * @returns {Promise<Object>} - { characters, total, page, pages }
   */
  async getCharacterList(params = {}) {
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

      const response = await this.get('/characters/', filteredParams);
      return response.data || response;
    } catch (error) {
      console.error('获取角色列表失败:', error);
      throw error;
    }
  }

  /**
   * 获取角色详情
   *
   * @param {string|number} characterId - 角色ID
   * @param {Object} options - 选项
   * @param {boolean} options.include_skills - 是否包含技能信息
   * @param {boolean} options.include_talents - 是否包含天赋信息
   * @returns {Promise<Object>} - 角色详情
   */
  async getCharacterDetail(characterId, options = {}) {
    if (!characterId) {
      throw new Error('角色ID不能为空');
    }

    try {
      const response = await this.get(`/characters/${characterId}`);
      const characterData = response.data || response;

      // 如果需要额外的技能信息，单独请求
      if (options.include_skills !== false) {
        try {
          const skillsResponse = await this.getCharacterSkills(characterId);
          characterData.skills = skillsResponse.skills || skillsResponse;
        } catch (skillsError) {
          console.warn('获取技能信息失败:', skillsError);
          characterData.skills = [];
        }
      }

      // 如果需要天赋信息
      if (options.include_talents) {
        try {
          const talentsResponse = await this.getCharacterTalents(characterId);
          characterData.talents = talentsResponse.talents || talentsResponse;
        } catch (talentError) {
          console.warn('获取天赋信息失败:', talentError);
          characterData.talents = [];
        }
      }

      return characterData;
    } catch (error) {
      console.error(`获取角色详情失败 (ID: ${characterId}):`, error);
      throw error;
    }
  }

  /**
   * 获取角色技能列表
   *
   * @param {string|number} characterId - 角色ID
   * @param {string} skillType - 技能类型过滤
   * @returns {Promise<Object>} - 技能列表
   */
  async getCharacterSkills(characterId, skillType = null) {
    if (!characterId) {
      throw new Error('角色ID不能为空');
    }

    try {
      const params = skillType ? { skill_type: skillType } : {};
      const response = await this.get(`/characters/${characterId}/skills`, params);
      return response.data || response;
    } catch (error) {
      console.error(`获取角色技能失败 (ID: ${characterId}):`, error);
      throw error;
    }
  }

  /**
   * 获取角色天赋信息
   *
   * @param {string|number} characterId - 角色ID
   * @returns {Promise<Object>} - 天赋列表
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
   * 搜索角色
   *
   * @param {string} query - 搜索关键词
   * @param {Object} filters - 过滤条件
   * @returns {Promise<Array>} - 匹配的角色列表
   */
  async searchCharacters(query, filters = {}) {
    if (!query || query.trim() === '') {
      return [];
    }

    try {
      const params = { search: query, ...filters };
      const response = await this.get('/characters/search', params);
      return response.data || response;
    } catch (error) {
      console.error('搜索角色失败:', error);
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
    return '★'.repeat(rarity);
  }
}

// 导出单例
const characterAPI = new CharacterAPIService();
export default characterAPI;

// 常量定义
export const ELEMENTS = {
  PYRO: 'Pyro',
  HYDRO: 'Hydro',
  ANEMO: 'Anemo',
  ELECTRO: 'Electro',
  DENDRO: 'Dendro',
  CRYO: 'Cryo',
  GEO: 'Geo'
};

export const WEAPON_TYPES = {
  SWORD: 'Sword',
  CLAYMORE: 'Claymore',
  POLEARM: 'Polearm',
  BOW: 'Bow',
  CATALYST: 'Catalyst'
};

export const REGIONS = {
  MONDSTADT: 'Mondstadt',
  LIYUE: 'Liyue',
  INAZUMA: 'Inazuma',
  SUMERU: 'Sumeru',
  FONTAINE: 'Fontaine',
  NATLAN: 'Natlan',
  SNEZHNAYA: 'Snezhnaya'
};

export const RARITIES = {
  FOUR_STAR: 4,
  FIVE_STAR: 5
};

// 角色工具函数
export const characterUtils = {
  /**
   * 格式化角色名称显示
   */
  formatCharacterName(character) {
    if (!character) return '';
    return character.name || character.name_en || '未知角色';
  },

  /**
   * 获取角色星级显示
   */
  getRarityStars(rarity) {
    return '★'.repeat(rarity || 0);
  },

  /**
   * 获取元素颜色类名
   */
  getElementColorClass(element) {
    const elementColors = {
      'pyro': 'element-pyro',
      'hydro': 'element-hydro',
      'anemo': 'element-anemo',
      'electro': 'element-electro',
      'dendro': 'element-dendro',
      'cryo': 'element-cryo',
      'geo': 'element-geo'
    };
    return elementColors[element] || 'element-default';
  },

  /**
   * 格式化角色属性显示
   */
  formatCharacterStats(character) {
    if (!character.base_stats) return {};

    return {
      hp: character.base_stats.hp?.toLocaleString() || '0',
      atk: character.base_stats.atk?.toLocaleString() || '0',
      def: character.base_stats.def_?.toLocaleString() || '0'
    };
  },

  /**
   * 检查角色是否为新角色（最近30天）
   */
  isNewCharacter(character) {
    if (!character.created_at) return false;

    const createdDate = new Date(character.created_at);
    const thirtyDaysAgo = new Date();
    thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);

    return createdDate > thirtyDaysAgo;
  }
};

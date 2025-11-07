/**
 * 角色API服务
 *
 * 提供角色相关的所有API调用封装
 */
import { BaseAPI } from './api';

class CharacterAPI extends BaseAPI {
  constructor() {
    super('/characters');
  }

  /**
   * 获取角色列表
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
   * @returns {Promise} API响应
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

      const response = await this.getList(filteredParams);
      return response;
    } catch (error) {
      console.error('获取角色列表失败:', error);
      throw error;
    }
  }

  /**
   * 获取角色详情
   * @param {number} characterId - 角色ID
   * @param {Object} options - 选项
   * @param {boolean} options.include_skills - 是否包含技能信息
   * @param {boolean} options.include_talents - 是否包含天赋信息
   * @returns {Promise} 角色详情
   */
  async getCharacterDetail(characterId, options = {}) {
    try {
      const params = {
        include_skills: true,
        include_talents: true,
        ...options
      };

      const response = await this.getDetail(characterId);

      // 如果需要额外的技能信息，单独请求
      if (params.include_skills) {
        try {
          const skillsResponse = await this.getCharacterSkills(characterId);
          response.data.skills = skillsResponse.data.skills;
        } catch (skillsError) {
          console.warn('获取技能信息失败:', skillsError);
          response.data.skills = [];
        }
      }

      return response;
    } catch (error) {
      console.error('获取角色详情失败:', error);
      throw error;
    }
  }

  /**
   * 获取角色技能列表
   * @param {number} characterId - 角色ID
   * @param {string} skillType - 技能类型过滤
   * @returns {Promise} 技能列表
   */
  async getCharacterSkills(characterId, skillType = null) {
    try {
      const { apiClient } = await import('./api');
      const params = skillType ? { skill_type: skillType } : {};
      const response = await apiClient.get(
        `${this.endpoint}/${characterId}/skills`,
        { params }
      );
      return response.data;
    } catch (error) {
      console.error('获取角色技能失败:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 搜索角色
   * @param {string} query - 搜索关键词
   * @param {number} limit - 结果数量限制
   * @returns {Promise} 搜索结果
   */
  async searchCharacters(query, limit = 20) {
    try {
      const { apiClient } = await import('./api');
      const response = await apiClient.get(
        `${this.endpoint}/search/`,
        {
          params: {
            query: query,
            limit: limit
          }
        }
      );
      return response.data;
    } catch (error) {
      console.error('角色搜索失败:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 获取角色统计信息
   * @returns {Promise} 统计信息
   */
  async getCharacterStats() {
    try {
      const { apiClient } = await import('./api');
      const response = await apiClient.get(`${this.endpoint}/stats/`);
      return response.data;
    } catch (error) {
      console.error('获取角色统计失败:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 获取可用的过滤选项
   * @returns {Promise} 过滤选项
   */
  async getFilterOptions() {
    try {
      const { apiClient } = await import('./api');
      const response = await apiClient.get(`${this.endpoint}/filters/`);
      return response.data;
    } catch (error) {
      console.error('获取过滤选项失败:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 获取热门角色（基于搜索频率等）
   * @param {number} limit - 数量限制
   * @returns {Promise} 热门角色列表
   */
  async getPopularCharacters(limit = 10) {
    try {
      const response = await this.getCharacterList({
        per_page: limit,
        sort_by: 'created_at',
        sort_order: 'desc'
      });
      return response;
    } catch (error) {
      console.error('获取热门角色失败:', error);
      throw error;
    }
  }

  /**
   * 获取推荐角色（基于用户喜好等）
   * @param {Object} userPreferences - 用户偏好
   * @returns {Promise} 推荐角色列表
   */
  async getRecommendedCharacters(userPreferences = {}) {
    try {
      // 基于用户偏好构建推荐查询
      let params = { per_page: 12 };

      if (userPreferences.favoriteElement) {
        params.element = userPreferences.favoriteElement;
      }

      if (userPreferences.favoriteWeaponType) {
        params.weapon_type = userPreferences.favoriteWeaponType;
      }

      if (userPreferences.preferredRarity) {
        params.rarity = userPreferences.preferredRarity;
      }

      const response = await this.getCharacterList(params);
      return response;
    } catch (error) {
      console.error('获取推荐角色失败:', error);
      throw error;
    }
  }

  /**
   * 根据元素类型获取角色
   * @param {string} element - 元素类型
   * @param {number} limit - 数量限制
   * @returns {Promise} 角色列表
   */
  async getCharactersByElement(element, limit = 20) {
    try {
      const response = await this.getCharacterList({
        element: element,
        per_page: limit,
        sort_by: 'name',
        sort_order: 'asc'
      });
      return response;
    } catch (error) {
      console.error(`获取${element}元素角色失败:`, error);
      throw error;
    }
  }

  /**
   * 根据武器类型获取角色
   * @param {string} weaponType - 武器类型
   * @param {number} limit - 数量限制
   * @returns {Promise} 角色列表
   */
  async getCharactersByWeaponType(weaponType, limit = 20) {
    try {
      const response = await this.getCharacterList({
        weapon_type: weaponType,
        per_page: limit,
        sort_by: 'name',
        sort_order: 'asc'
      });
      return response;
    } catch (error) {
      console.error(`获取${weaponType}武器角色失败:`, error);
      throw error;
    }
  }

  /**
   * 根据稀有度获取角色
   * @param {number} rarity - 稀有度 (4或5)
   * @param {number} limit - 数量限制
   * @returns {Promise} 角色列表
   */
  async getCharactersByRarity(rarity, limit = 20) {
    try {
      const response = await this.getCharacterList({
        rarity: rarity,
        per_page: limit,
        sort_by: 'name',
        sort_order: 'asc'
      });
      return response;
    } catch (error) {
      console.error(`获取${rarity}星角色失败:`, error);
      throw error;
    }
  }

  /**
   * 批量获取角色详情
   * @param {number[]} characterIds - 角色ID数组
   * @returns {Promise} 角色详情数组
   */
  async getBatchCharacterDetails(characterIds) {
    try {
      const promises = characterIds.map(id => this.getCharacterDetail(id));
      const results = await Promise.allSettled(promises);

      return results.map((result, index) => ({
        id: characterIds[index],
        success: result.status === 'fulfilled',
        data: result.status === 'fulfilled' ? result.value.data : null,
        error: result.status === 'rejected' ? result.reason : null
      }));
    } catch (error) {
      console.error('批量获取角色详情失败:', error);
      throw error;
    }
  }
}

// 创建单例实例
const characterAPI = new CharacterAPI();

// 常用的元素类型和武器类型常量
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

// 工具函数
export const characterUtils = {
  /**
   * 格式化角色名称显示
   * @param {Object} character - 角色对象
   * @returns {string} 格式化的名称
   */
  formatCharacterName(character) {
    if (!character) return '';
    return character.name || character.name_en || '未知角色';
  },

  /**
   * 获取角色星级显示
   * @param {number} rarity - 稀有度
   * @returns {string} 星级字符串
   */
  getRarityStars(rarity) {
    return '★'.repeat(rarity || 0);
  },

  /**
   * 获取元素颜色类名
   * @param {string} element - 元素类型
   * @returns {string} CSS类名
   */
  getElementColorClass(element) {
    const elementColors = {
      [ELEMENTS.PYRO]: 'element-pyro',
      [ELEMENTS.HYDRO]: 'element-hydro',
      [ELEMENTS.ANEMO]: 'element-anemo',
      [ELEMENTS.ELECTRO]: 'element-electro',
      [ELEMENTS.DENDRO]: 'element-dendro',
      [ELEMENTS.CRYO]: 'element-cryo',
      [ELEMENTS.GEO]: 'element-geo'
    };
    return elementColors[element] || 'element-default';
  },

  /**
   * 格式化角色属性显示
   * @param {Object} character - 角色对象
   * @returns {Object} 格式化的属性
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
   * @param {Object} character - 角色对象
   * @returns {boolean} 是否为新角色
   */
  isNewCharacter(character) {
    if (!character.created_at) return false;

    const createdDate = new Date(character.created_at);
    const thirtyDaysAgo = new Date();
    thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);

    return createdDate > thirtyDaysAgo;
  }
};

// 在CharacterAPI类中添加CRUD方法
CharacterAPI.prototype.createCharacter = async function(characterData) {
  try {
    return await this.create(characterData);
  } catch (error) {
    console.error('创建角色失败:', error);
    throw error;
  }
};

CharacterAPI.prototype.updateCharacter = async function(characterId, characterData) {
  try {
    return await this.update(characterId, characterData);
  } catch (error) {
    console.error('更新角色失败:', error);
    throw error;
  }
};

CharacterAPI.prototype.deleteCharacter = async function(characterId) {
  try {
    return await this.delete(characterId);
  } catch (error) {
    console.error('删除角色失败:', error);
    throw error;
  }
};

export default characterAPI;
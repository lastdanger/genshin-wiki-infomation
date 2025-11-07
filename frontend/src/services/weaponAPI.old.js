/**
 * 武器相关 API 服务
 *
 * 提供武器数据的增删改查、搜索、统计等功能
 */

import { BaseAPI, apiClient } from './api';

class WeaponAPI extends BaseAPI {
    constructor() {
        super('/weapons');
    }

    /**
     * 获取武器列表
     * @param {Object} params - 查询参数
     * @param {number} params.page - 页码
     * @param {number} params.per_page - 每页数量
     * @param {string} params.weapon_type - 武器类型过滤
     * @param {number} params.rarity - 稀有度过滤
     * @param {string} params.source - 获取方式过滤
     * @param {string} params.search - 搜索关键词
     * @param {string} params.sort_by - 排序字段
     * @param {string} params.sort_order - 排序方向
     */
    async getWeaponList(params = {}) {
        return this.getList(params);
    }

    /**
     * 获取武器详情
     * @param {number} weaponId - 武器ID
     */
    async getWeaponDetail(weaponId) {
        return this.getDetail(weaponId);
    }

    /**
     * 创建武器
     * @param {Object} weaponData - 武器数据
     */
    async createWeapon(weaponData) {
        return this.create(weaponData);
    }

    /**
     * 更新武器
     * @param {number} weaponId - 武器ID
     * @param {Object} weaponData - 更新数据
     */
    async updateWeapon(weaponId, weaponData) {
        return this.update(weaponId, weaponData);
    }

    /**
     * 删除武器
     * @param {number} weaponId - 武器ID
     */
    async deleteWeapon(weaponId) {
        return this.delete(weaponId);
    }

    /**
     * 搜索武器
     * @param {string} query - 搜索关键词
     * @param {number} limit - 结果限制数量
     */
    async searchWeapons(query, limit = 20) {
        return this.search(query, { limit });
    }

    /**
     * 获取武器统计信息
     */
    async getWeaponStats() {
        try {
            const response = await apiClient.get('/weapons/stats/overview');
            return response.data;
        } catch (error) {
            throw this.handleError(error);
        }
    }

    /**
     * 根据武器类型获取武器列表
     * @param {string} weaponType - 武器类型
     * @param {number} limit - 结果限制数量
     */
    async getWeaponsByType(weaponType, limit = 20) {
        try {
            const response = await apiClient.get(`/weapons/type/${weaponType}`, {
                params: { limit }
            });
            return response.data;
        } catch (error) {
            throw this.handleError(error);
        }
    }

    /**
     * 根据稀有度获取武器列表
     * @param {number} rarity - 稀有度
     * @param {number} limit - 结果限制数量
     */
    async getWeaponsByRarity(rarity, limit = 20) {
        try {
            const response = await apiClient.get(`/weapons/rarity/${rarity}`, {
                params: { limit }
            });
            return response.data;
        } catch (error) {
            throw this.handleError(error);
        }
    }

    /**
     * 获取武器过滤选项
     */
    async getWeaponFilters() {
        try {
            const response = await apiClient.get('/weapons/filters/options');
            return response.data;
        } catch (error) {
            throw this.handleError(error);
        }
    }

    // ===== 工具方法 =====

    /**
     * 获取武器类型的显示名称
     * @param {string} weaponType - 武器类型
     */
    getWeaponTypeDisplay(weaponType) {
        const typeMap = {
            'Sword': '单手剑',
            'Claymore': '双手剑',
            'Polearm': '长柄武器',
            'Bow': '弓',
            'Catalyst': '法器'
        };
        return typeMap[weaponType] || weaponType;
    }

    /**
     * 获取稀有度显示
     * @param {number} rarity - 稀有度
     */
    getRarityDisplay(rarity) {
        return '★'.repeat(rarity);
    }

    /**
     * 获取武器类型的图标类名
     * @param {string} weaponType - 武器类型
     */
    getWeaponTypeIcon(weaponType) {
        const iconMap = {
            'Sword': 'weapon-sword',
            'Claymore': 'weapon-claymore',
            'Polearm': 'weapon-polearm',
            'Bow': 'weapon-bow',
            'Catalyst': 'weapon-catalyst'
        };
        return iconMap[weaponType] || 'weapon-default';
    }

    /**
     * 获取稀有度的CSS类名
     * @param {number} rarity - 稀有度
     */
    getRarityClass(rarity) {
        return `rarity-${rarity}`;
    }

    /**
     * 格式化武器属性值
     * @param {string} statType - 属性类型
     * @param {string} statValue - 属性值
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
     * @param {string} source - 获取方式
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
     * @param {number} rarity - 稀有度
     */
    isFiveStar(rarity) {
        return rarity === 5;
    }

    /**
     * 检查是否为四星武器
     * @param {number} rarity - 稀有度
     */
    isFourStar(rarity) {
        return rarity === 4;
    }
}

// 创建单例实例
const weaponAPI = new WeaponAPI();

export default weaponAPI;
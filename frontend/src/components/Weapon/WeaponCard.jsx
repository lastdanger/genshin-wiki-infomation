/**
 * 武器卡片组件
 *
 * 在武器列表中显示武器的基本信息
 */
import React from 'react';
import { Link } from 'react-router-dom';
import weaponAPI from '../../services/weaponAPI';
import './WeaponCard.css';

const WeaponCard = ({ weapon, onClick, className = '' }) => {
  if (!weapon) {
    return <div className="weapon-card weapon-card--loading">加载中...</div>;
  }

  const handleClick = (e) => {
    if (onClick) {
      e.preventDefault();
      onClick(weapon);
    }
  };

  const rarityStars = weaponAPI.getRarityDisplay(weapon.rarity);
  const rarityClass = weaponAPI.getRarityClass(weapon.rarity);
  const weaponTypeDisplay = weaponAPI.getWeaponTypeDisplay(weapon.weapon_type);
  const weaponTypeIcon = weaponAPI.getWeaponTypeIcon(weapon.weapon_type);
  const sourceColor = weaponAPI.getSourceColor(weapon.source);
  const isFiveStar = weaponAPI.isFiveStar(weapon.rarity);
  const isFourStar = weaponAPI.isFourStar(weapon.rarity);

  return (
    <Link
      to={`/weapons/${weapon.id}`}
      className={`weapon-card ${rarityClass} ${className}`}
      onClick={handleClick}
      aria-label={`查看武器 ${weapon.name} 的详细信息`}
    >
      {/* 武器图标区域 */}
      <div className="weapon-card__avatar">
        <div className="weapon-card__avatar-placeholder">
          <span className="weapon-card__avatar-icon">
            {getWeaponTypeIconDisplay(weapon.weapon_type)}
          </span>
        </div>

        {/* 稀有度星级 */}
        <div className={`weapon-card__rarity ${rarityClass}`}>
          {rarityStars}
        </div>

        {/* 五星武器特殊标识 */}
        {isFiveStar && (
          <div className="weapon-card__five-star-badge">
            五星
          </div>
        )}
      </div>

      {/* 武器信息区域 */}
      <div className="weapon-card__info">
        <div className="weapon-card__header">
          <h3 className="weapon-card__name" title={weapon.name}>
            {weapon.name}
          </h3>

          {weapon.name_en && (
            <p className="weapon-card__name-en" title={weapon.name_en}>
              {weapon.name_en}
            </p>
          )}
        </div>

        {/* 武器类型和基础攻击力 */}
        <div className="weapon-card__attributes">
          <div className={`weapon-card__type weapon-type-${weapon.weapon_type?.toLowerCase()}`}>
            <span className="weapon-card__type-icon">
              {weaponTypeIcon}
            </span>
            <span className="weapon-card__type-name">
              {weaponTypeDisplay}
            </span>
          </div>

          <div className="weapon-card__attack">
            <span className="weapon-card__attack-icon">⚔️</span>
            <span className="weapon-card__attack-value">
              基础攻击力 {weapon.base_attack}
            </span>
          </div>
        </div>

        {/* 副属性 */}
        {weapon.secondary_stat && weapon.secondary_stat_value && (
          <div className="weapon-card__secondary-stat">
            <span className="weapon-card__secondary-stat-label">
              {getStatDisplayName(weapon.secondary_stat)}
            </span>
            <span className="weapon-card__secondary-stat-value">
              {weaponAPI.formatStatValue(weapon.secondary_stat, weapon.secondary_stat_value)}
            </span>
          </div>
        )}

        {/* 被动技能 */}
        {weapon.passive_name && (
          <div className="weapon-card__passive">
            <div className="weapon-card__passive-name">
              {weapon.passive_name}
            </div>
            {weapon.passive_description && (
              <div className="weapon-card__passive-description">
                {weapon.passive_description.length > 80
                  ? `${weapon.passive_description.substring(0, 80)}...`
                  : weapon.passive_description
                }
              </div>
            )}
          </div>
        )}

        {/* 获取方式 */}
        {weapon.source && (
          <div className="weapon-card__source">
            <span className="weapon-card__source-icon">
              {getSourceIcon(weapon.source)}
            </span>
            <span
              className={`weapon-card__source-name source-${sourceColor}`}
            >
              {weapon.source}
            </span>
          </div>
        )}
      </div>

      {/* 悬停效果遮罩 */}
      <div className="weapon-card__overlay">
        <span className="weapon-card__overlay-text">点击查看详情</span>
      </div>
    </Link>
  );
};

// 获取武器类型图标显示
const getWeaponTypeIconDisplay = (weaponType) => {
  const typeIcons = {
    'Sword': '⚔️',
    'Claymore': '🗡️',
    'Polearm': '🔱',
    'Bow': '🏹',
    'Catalyst': '📖'
  };
  return typeIcons[weaponType] || '⚔️';
};

// 获取属性显示名称
const getStatDisplayName = (statType) => {
  const statNames = {
    'ATK%': '攻击力%',
    'DEF%': '防御力%',
    'HP%': '生命值%',
    'CRIT Rate': '暴击率',
    'CRIT DMG': '暴击伤害',
    'Energy Recharge': '元素充能效率',
    'Elemental Mastery': '元素精通',
    'Physical DMG Bonus': '物理伤害加成',
    'Pyro DMG Bonus': '火元素伤害加成',
    'Hydro DMG Bonus': '水元素伤害加成',
    'Anemo DMG Bonus': '风元素伤害加成',
    'Electro DMG Bonus': '雷元素伤害加成',
    'Dendro DMG Bonus': '草元素伤害加成',
    'Cryo DMG Bonus': '冰元素伤害加成',
    'Geo DMG Bonus': '岩元素伤害加成'
  };
  return statNames[statType] || statType;
};

// 获取获取方式图标
const getSourceIcon = (source) => {
  const sourceIcons = {
    '祈愿': '🎲',
    '锻造': '⚒️',
    '活动': '🎉',
    '商店': '🛒',
    '任务奖励': '📋',
    '成就奖励': '🏆'
  };
  return sourceIcons[source] || '📦';
};

// 武器卡片骨架屏组件
export const WeaponCardSkeleton = ({ className = '' }) => {
  return (
    <div className={`weapon-card weapon-card--skeleton ${className}`}>
      <div className="weapon-card__avatar">
        <div className="weapon-card__avatar-placeholder skeleton-loading"></div>
      </div>
      <div className="weapon-card__info">
        <div className="weapon-card__header">
          <div className="weapon-card__name skeleton-loading skeleton-text"></div>
          <div className="weapon-card__name-en skeleton-loading skeleton-text skeleton-text--small"></div>
        </div>
        <div className="weapon-card__attributes">
          <div className="skeleton-loading skeleton-text skeleton-text--small"></div>
          <div className="skeleton-loading skeleton-text skeleton-text--small"></div>
        </div>
        <div className="weapon-card__secondary-stat">
          <div className="skeleton-loading skeleton-text skeleton-text--small"></div>
        </div>
        <div className="weapon-card__passive">
          <div className="skeleton-loading skeleton-text skeleton-text--small"></div>
          <div className="skeleton-loading skeleton-text skeleton-text--tiny"></div>
        </div>
        <div className="weapon-card__source">
          <div className="skeleton-loading skeleton-text skeleton-text--tiny"></div>
        </div>
      </div>
    </div>
  );
};

export default WeaponCard;
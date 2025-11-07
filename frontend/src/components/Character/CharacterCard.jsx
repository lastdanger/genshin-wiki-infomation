/**
 * 角色卡片组件
 *
 * 在角色列表中显示角色的基本信息
 */
import React from 'react';
import { Link } from 'react-router-dom';
import { characterUtils, ELEMENTS, WEAPON_TYPES } from '../../services/characterAPI';
import './CharacterCard.css';

const CharacterCard = ({ character, onClick, className = '' }) => {
  if (!character) {
    return <div className="character-card character-card--loading">加载中...</div>;
  }

  const handleClick = (e) => {
    if (onClick) {
      e.preventDefault();
      onClick(character);
    }
  };

  const formatStats = characterUtils.formatCharacterStats(character);
  const elementClass = characterUtils.getElementColorClass(character.element);
  const rarityStars = characterUtils.getRarityStars(character.rarity);
  const isNew = characterUtils.isNewCharacter(character);

  return (
    <Link
      to={`/characters/${character.id}`}
      className={`character-card ${elementClass} ${className}`}
      onClick={handleClick}
      aria-label={`查看角色 ${character.name} 的详细信息`}
    >
      {/* 角色头像区域 */}
      <div className="character-card__avatar">
        <div className="character-card__avatar-placeholder">
          <span className="character-card__avatar-icon">
            {character.name?.[0] || '?'}
          </span>
        </div>

        {/* 稀有度星级 */}
        <div className={`character-card__rarity rarity-${character.rarity}`}>
          {rarityStars}
        </div>

        {/* 新角色标签 */}
        {isNew && (
          <div className="character-card__new-badge">
            新
          </div>
        )}
      </div>

      {/* 角色信息区域 */}
      <div className="character-card__info">
        <div className="character-card__header">
          <h3 className="character-card__name" title={character.name}>
            {character.name}
          </h3>

          {character.title && (
            <p className="character-card__title" title={character.title}>
              {character.title}
            </p>
          )}
        </div>

        {/* 元素和武器类型 */}
        <div className="character-card__attributes">
          <div className={`character-card__element ${elementClass}`}>
            <span className="character-card__element-icon">
              {getElementIcon(character.element)}
            </span>
            <span className="character-card__element-name">
              {getElementName(character.element)}
            </span>
          </div>

          <div className="character-card__weapon">
            <span className="character-card__weapon-icon">
              {getWeaponIcon(character.weapon_type)}
            </span>
            <span className="character-card__weapon-name">
              {getWeaponTypeName(character.weapon_type)}
            </span>
          </div>
        </div>

        {/* 基础属性预览 */}
        {character.base_stats && (
          <div className="character-card__stats">
            <div className="character-card__stat">
              <span className="character-card__stat-label">生命</span>
              <span className="character-card__stat-value">{formatStats.hp}</span>
            </div>
            <div className="character-card__stat">
              <span className="character-card__stat-label">攻击</span>
              <span className="character-card__stat-value">{formatStats.atk}</span>
            </div>
            <div className="character-card__stat">
              <span className="character-card__stat-label">防御</span>
              <span className="character-card__stat-value">{formatStats.def}</span>
            </div>
          </div>
        )}

        {/* 地区信息 */}
        {character.region && (
          <div className="character-card__region">
            <span className="character-card__region-icon">🏰</span>
            <span className="character-card__region-name">
              {getRegionName(character.region)}
            </span>
          </div>
        )}
      </div>

      {/* 悬停效果遮罩 */}
      <div className="character-card__overlay">
        <span className="character-card__overlay-text">点击查看详情</span>
      </div>
    </Link>
  );
};

// 获取元素图标
const getElementIcon = (element) => {
  const elementIcons = {
    [ELEMENTS.PYRO]: '🔥',
    [ELEMENTS.HYDRO]: '💧',
    [ELEMENTS.ANEMO]: '🌪️',
    [ELEMENTS.ELECTRO]: '⚡',
    [ELEMENTS.DENDRO]: '🌿',
    [ELEMENTS.CRYO]: '❄️',
    [ELEMENTS.GEO]: '🟡'
  };
  return elementIcons[element] || '❓';
};

// 获取元素中文名称
const getElementName = (element) => {
  const elementNames = {
    [ELEMENTS.PYRO]: '火',
    [ELEMENTS.HYDRO]: '水',
    [ELEMENTS.ANEMO]: '风',
    [ELEMENTS.ELECTRO]: '雷',
    [ELEMENTS.DENDRO]: '草',
    [ELEMENTS.CRYO]: '冰',
    [ELEMENTS.GEO]: '岩'
  };
  return elementNames[element] || element;
};

// 获取武器类型图标
const getWeaponIcon = (weaponType) => {
  const weaponIcons = {
    [WEAPON_TYPES.SWORD]: '⚔️',
    [WEAPON_TYPES.CLAYMORE]: '🗡️',
    [WEAPON_TYPES.POLEARM]: '🏹',
    [WEAPON_TYPES.BOW]: '🏹',
    [WEAPON_TYPES.CATALYST]: '📖'
  };
  return weaponIcons[weaponType] || '⚔️';
};

// 获取武器类型中文名称
const getWeaponTypeName = (weaponType) => {
  const weaponNames = {
    [WEAPON_TYPES.SWORD]: '单手剑',
    [WEAPON_TYPES.CLAYMORE]: '双手剑',
    [WEAPON_TYPES.POLEARM]: '长柄武器',
    [WEAPON_TYPES.BOW]: '弓',
    [WEAPON_TYPES.CATALYST]: '法器'
  };
  return weaponNames[weaponType] || weaponType;
};

// 获取地区中文名称
const getRegionName = (region) => {
  const regionNames = {
    'Mondstadt': '蒙德',
    'Liyue': '璃月',
    'Inazuma': '稻妻',
    'Sumeru': '须弥',
    'Fontaine': '枫丹',
    'Natlan': '纳塔',
    'Snezhnaya': '至冬'
  };
  return regionNames[region] || region;
};

// 角色卡片骨架屏组件
export const CharacterCardSkeleton = ({ className = '' }) => {
  return (
    <div className={`character-card character-card--skeleton ${className}`}>
      <div className="character-card__avatar">
        <div className="character-card__avatar-placeholder skeleton-loading"></div>
      </div>
      <div className="character-card__info">
        <div className="character-card__header">
          <div className="character-card__name skeleton-loading skeleton-text"></div>
          <div className="character-card__title skeleton-loading skeleton-text skeleton-text--small"></div>
        </div>
        <div className="character-card__attributes">
          <div className="skeleton-loading skeleton-text skeleton-text--small"></div>
          <div className="skeleton-loading skeleton-text skeleton-text--small"></div>
        </div>
        <div className="character-card__stats">
          <div className="character-card__stat">
            <div className="skeleton-loading skeleton-text skeleton-text--tiny"></div>
            <div className="skeleton-loading skeleton-text skeleton-text--tiny"></div>
          </div>
          <div className="character-card__stat">
            <div className="skeleton-loading skeleton-text skeleton-text--tiny"></div>
            <div className="skeleton-loading skeleton-text skeleton-text--tiny"></div>
          </div>
          <div className="character-card__stat">
            <div className="skeleton-loading skeleton-text skeleton-text--tiny"></div>
            <div className="skeleton-loading skeleton-text skeleton-text--tiny"></div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CharacterCard;
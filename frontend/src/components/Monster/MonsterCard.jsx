/**
 * MonsterCard 组件
 *
 * 显示怪物卡片信息的组件
 */

import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import './MonsterCard.css';
import {
  formatMonsterName,
  getMonsterCategoryColor,
  getMonsterElementColor,
  formatMonsterLevel,
  formatExpReward,
  formatMoraReward,
  isMonsterBoss,
  isMonsterElite
} from '../../services/monsterAPI';

const MonsterCard = ({ monster, onClick, showHover = true }) => {
  const [isHovered, setIsHovered] = useState(false);
  const [imageError, setImageError] = useState(false);

  if (!monster) {
    return <MonsterCardSkeleton />;
  }

  const handleClick = (e) => {
    if (onClick) {
      e.preventDefault();
      onClick(monster);
    }
  };

  const handleMouseEnter = () => {
    if (showHover) {
      setIsHovered(true);
    }
  };

  const handleMouseLeave = () => {
    if (showHover) {
      setIsHovered(false);
    }
  };

  const handleImageError = () => {
    setImageError(true);
  };

  const monsterName = formatMonsterName(monster);
  const categoryColor = getMonsterCategoryColor(monster.category);
  const elementColor = getMonsterElementColor(monster.element);
  const isBoss = isMonsterBoss(monster);
  const isElite = isMonsterElite(monster);

  return (
    <div className="monster-card-container">
      <Link
        to={`/monsters/${monster.id}`}
        className={`monster-card ${categoryColor} ${isHovered ? 'hovered' : ''}`}
        onClick={handleClick}
        onMouseEnter={handleMouseEnter}
        onMouseLeave={handleMouseLeave}
      >
        {/* 怪物图片 */}
        <div className="monster-card-image">
          {!imageError ? (
            <img
              src={monster.image || `/images/monsters/${monster.id}.png`}
              alt={monsterName}
              onError={handleImageError}
              loading="lazy"
            />
          ) : (
            <div className="monster-image-placeholder">
              <div className="monster-icon">
                {isBoss ? '👹' : isElite ? '💀' : '🦴'}
              </div>
            </div>
          )}

          {/* 怪物类别标签 */}
          <div className={`monster-category-badge ${categoryColor}`}>
            {monster.category}
          </div>

          {/* 元素标签 */}
          {monster.element && (
            <div className={`monster-element-badge ${elementColor}`}>
              {monster.element}
            </div>
          )}
        </div>

        {/* 怪物信息 */}
        <div className="monster-card-info">
          <div className="monster-header">
            <h3 className="monster-name" title={monsterName}>
              {monsterName}
            </h3>
            <div className="monster-level">
              {formatMonsterLevel(monster.level)}
            </div>
          </div>

          <div className="monster-details">
            <div className="monster-family">
              族群: {monster.family}
            </div>
            <div className="monster-stats">
              <span className="stat">
                <span className="stat-label">HP:</span>
                <span className="stat-value">{monster.hp?.toLocaleString()}</span>
              </span>
              <span className="stat">
                <span className="stat-label">ATK:</span>
                <span className="stat-value">{monster.attack?.toLocaleString()}</span>
              </span>
            </div>
            <div className="monster-rewards">
              <span className="reward">
                {formatExpReward(monster.exp_reward)}
              </span>
              <span className="reward">
                {formatMoraReward(monster.mora_reward)}
              </span>
            </div>
          </div>
        </div>

        {/* 悬停显示详细信息 */}
        {showHover && isHovered && (
          <div className="monster-card-hover">
            <div className="hover-content">
              <div className="hover-section">
                <h4>基础信息</h4>
                <p><strong>等级:</strong> {formatMonsterLevel(monster.level)}</p>
                <p><strong>世界等级:</strong> {monster.world_level || 'N/A'}</p>
                <p><strong>仇恨范围:</strong> {monster.aggro_range}m</p>
              </div>

              {monster.weak_points && monster.weak_points.length > 0 && (
                <div className="hover-section">
                  <h4>弱点</h4>
                  <div className="weak-points">
                    {monster.weak_points.map((point, index) => (
                      <span key={index} className="weak-point">
                        {point}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {monster.drops && monster.drops.length > 0 && (
                <div className="hover-section">
                  <h4>主要掉落</h4>
                  <div className="drops-preview">
                    {monster.drops.slice(0, 3).map((drop, index) => (
                      <div key={index} className="drop-item">
                        <span className="drop-name">{drop.item_name}</span>
                        <span className="drop-rate">({drop.drop_rate}%)</span>
                      </div>
                    ))}
                    {monster.drops.length > 3 && (
                      <div className="more-drops">
                        +{monster.drops.length - 3} 更多
                      </div>
                    )}
                  </div>
                </div>
              )}

              {monster.description && (
                <div className="hover-section">
                  <h4>描述</h4>
                  <p className="monster-description">
                    {monster.description.length > 100
                      ? `${monster.description.substring(0, 100)}...`
                      : monster.description
                    }
                  </p>
                </div>
              )}
            </div>
          </div>
        )}
      </Link>
    </div>
  );
};

// 骨架屏组件
const MonsterCardSkeleton = () => {
  return (
    <div className="monster-card monster-card-skeleton">
      <div className="monster-card-image skeleton-shimmer">
        <div className="skeleton-placeholder"></div>
      </div>
      <div className="monster-card-info">
        <div className="monster-header">
          <div className="skeleton-line skeleton-title"></div>
          <div className="skeleton-line skeleton-level"></div>
        </div>
        <div className="monster-details">
          <div className="skeleton-line skeleton-family"></div>
          <div className="monster-stats">
            <div className="skeleton-line skeleton-stat"></div>
            <div className="skeleton-line skeleton-stat"></div>
          </div>
          <div className="monster-rewards">
            <div className="skeleton-line skeleton-reward"></div>
            <div className="skeleton-line skeleton-reward"></div>
          </div>
        </div>
      </div>
    </div>
  );
};

export { MonsterCardSkeleton };
export default MonsterCard;
/**
 * 圣遗物卡片组件
 *
 * 在圣遗物列表中显示圣遗物的基本信息
 */
import React from 'react';
import { Link } from 'react-router-dom';
import { artifactUtils, ARTIFACT_SLOTS } from '../../services/artifactAPI';
import './ArtifactCard.css';

const ArtifactCard = ({ artifact, onClick, className = '' }) => {
  if (!artifact) {
    return <div className="artifact-card artifact-card--loading">加载中...</div>;
  }

  const handleClick = (e) => {
    if (onClick) {
      e.preventDefault();
      onClick(artifact);
    }
  };

  const slotDisplayName = artifactUtils.getSlotDisplayName(artifact.slot);
  const rarityStars = artifactUtils.getRarityStars(artifact.rarity);
  const rarityClass = artifactUtils.getRarityColorClass(artifact.rarity);
  const mainStatDisplay = artifactUtils.formatMainStat(artifact.main_stat_type, artifact.main_stat_value);
  const subStats = artifactUtils.formatSubStats(artifact.sub_stats);

  return (
    <Link
      to={`/artifacts/${artifact.id}`}
      className={`artifact-card ${rarityClass} ${className}`}
      onClick={handleClick}
      aria-label={`查看圣遗物 ${artifact.name} 的详细信息`}
    >
      {/* 圣遗物图标区域 */}
      <div className="artifact-card__icon">
        <div className="artifact-card__icon-placeholder">
          <span className="artifact-card__slot-icon" data-slot={artifact.slot}>
            {getSlotIcon(artifact.slot)}
          </span>
        </div>

        {/* 稀有度星级 */}
        <div className={`artifact-card__rarity ${rarityClass}`}>
          {rarityStars}
        </div>
      </div>

      {/* 圣遗物信息区域 */}
      <div className="artifact-card__info">
        <div className="artifact-card__header">
          <h3 className="artifact-card__name" title={artifact.name}>
            {artifact.name}
          </h3>
          {artifact.name_en && (
            <p className="artifact-card__name-en" title={artifact.name_en}>
              {artifact.name_en}
            </p>
          )}
        </div>

        {/* 套装信息 */}
        <div className="artifact-card__set">
          <span className="artifact-card__set-name" title={artifact.set_name}>
            {artifact.set_name}
          </span>
          <span className="artifact-card__slot">
            {slotDisplayName}
          </span>
        </div>

        {/* 主属性 */}
        <div className="artifact-card__main-stat">
          <span className="artifact-card__main-stat-label">主属性</span>
          <span className="artifact-card__main-stat-value" title={mainStatDisplay}>
            {mainStatDisplay}
          </span>
        </div>

        {/* 副属性（显示前2个） */}
        {subStats && subStats.length > 0 && (
          <div className="artifact-card__sub-stats">
            <span className="artifact-card__sub-stats-label">副属性</span>
            <div className="artifact-card__sub-stats-list">
              {subStats.slice(0, 2).map((stat, index) => (
                <span key={index} className="artifact-card__sub-stat" title={stat.display}>
                  {stat.stat_type} +{stat.stat_value}
                </span>
              ))}
              {subStats.length > 2 && (
                <span className="artifact-card__sub-stats-more">
                  +{subStats.length - 2}个属性
                </span>
              )}
            </div>
          </div>
        )}

        {/* 获取方式 */}
        {artifact.source && (
          <div className="artifact-card__source">
            <span className="artifact-card__source-label">获取</span>
            <span className="artifact-card__source-value">{artifact.source}</span>
          </div>
        )}
      </div>

      {/* 悬停时显示套装效果 */}
      <div className="artifact-card__hover-info">
        <div className="artifact-card__set-effects">
          <h4>套装效果</h4>
          <div className="artifact-card__set-effects-content">
            {artifact.set_effects && artifact.set_effects['2'] && (
              <div className="set-effect">
                <span className="set-effect__count">2件套</span>
                <span className="set-effect__description">
                  {artifact.set_effects['2'].description}
                </span>
              </div>
            )}
            {artifact.set_effects && artifact.set_effects['4'] && (
              <div className="set-effect">
                <span className="set-effect__count">4件套</span>
                <span className="set-effect__description">
                  {artifact.set_effects['4'].description}
                </span>
              </div>
            )}
          </div>
        </div>
      </div>
    </Link>
  );
};

// 获取部位图标
const getSlotIcon = (slot) => {
  const slotIcons = {
    [ARTIFACT_SLOTS.FLOWER]: '🌸',
    [ARTIFACT_SLOTS.PLUME]: '🪶',
    [ARTIFACT_SLOTS.SANDS]: '⏳',
    [ARTIFACT_SLOTS.GOBLET]: '🏺',
    [ARTIFACT_SLOTS.CIRCLET]: '👑'
  };
  return slotIcons[slot] || '🔮';
};

// 圣遗物卡片骨架屏组件
export const ArtifactCardSkeleton = ({ className = '' }) => {
  return (
    <div className={`artifact-card artifact-card--skeleton ${className}`}>
      <div className="artifact-card__icon">
        <div className="artifact-card__icon-placeholder skeleton-shimmer"></div>
        <div className="artifact-card__rarity skeleton-shimmer"></div>
      </div>

      <div className="artifact-card__info">
        <div className="artifact-card__header">
          <div className="artifact-card__name skeleton-shimmer skeleton-text"></div>
          <div className="artifact-card__name-en skeleton-shimmer skeleton-text skeleton-text--small"></div>
        </div>

        <div className="artifact-card__set">
          <div className="artifact-card__set-name skeleton-shimmer skeleton-text"></div>
          <div className="artifact-card__slot skeleton-shimmer skeleton-text skeleton-text--small"></div>
        </div>

        <div className="artifact-card__main-stat">
          <div className="artifact-card__main-stat-label skeleton-shimmer skeleton-text skeleton-text--small"></div>
          <div className="artifact-card__main-stat-value skeleton-shimmer skeleton-text"></div>
        </div>

        <div className="artifact-card__sub-stats">
          <div className="artifact-card__sub-stats-label skeleton-shimmer skeleton-text skeleton-text--small"></div>
          <div className="artifact-card__sub-stats-list">
            <div className="artifact-card__sub-stat skeleton-shimmer skeleton-text skeleton-text--small"></div>
            <div className="artifact-card__sub-stat skeleton-shimmer skeleton-text skeleton-text--small"></div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ArtifactCard;
/**
 * 怪物详情页面
 *
 * 显示单个怪物的完整信息，包括属性、技能、掉落物品等
 */
import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import monsterAPI, {
  formatMonsterName,
  getMonsterCategoryColor,
  getMonsterElementColor,
  formatMonsterLevel,
  formatExpReward,
  formatMoraReward,
  isMonsterBoss,
  isMonsterElite,
  getResistanceLevel
} from '../services/monsterAPI';
import { utils } from '../services/api';
import './MonsterDetailPage.css';

const MonsterDetailPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();

  // 数据状态
  const [monster, setMonster] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // 族群相关状态
  const [familyMonsters, setFamilyMonsters] = useState([]);
  const [familyLoading, setFamilyLoading] = useState(false);

  // 界面状态
  const [activeTab, setActiveTab] = useState('overview'); // overview, abilities, drops, family

  // 加载怪物详情
  const loadMonsterDetail = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      console.log('🔍 加载怪物详情:', id);

      const response = await monsterAPI.getMonsterById(parseInt(id));

      if (response.success) {
        setMonster(response.data);
      } else {
        throw new Error(response.error || '获取怪物详情失败');
      }
    } catch (err) {
      console.error('❌ 加载怪物详情失败:', err);
      setError(utils.formatError(err));
    } finally {
      setLoading(false);
    }
  }, [id]);

  // 加载族群其他怪物
  const loadFamilyMonsters = useCallback(async () => {
    if (!monster || familyLoading) return;

    try {
      setFamilyLoading(true);

      const response = await monsterAPI.getMonstersByFamily(monster.family);

      if (response.success) {
        setFamilyMonsters(response.data.monsters || response.data || []);
      }
    } catch (err) {
      console.warn('获取族群信息失败:', err);
    } finally {
      setFamilyLoading(false);
    }
  }, [monster, familyLoading]);

  // 初始化加载
  useEffect(() => {
    loadMonsterDetail();
  }, [loadMonsterDetail]);

  // 加载族群信息
  useEffect(() => {
    if (monster && activeTab === 'family') {
      loadFamilyMonsters();
    }
  }, [monster, activeTab, loadFamilyMonsters]);

  // 渲染加载状态
  if (loading) {
    return (
      <div className="monster-detail-page">
        <div className="monster-detail-page__loading">
          <div className="loading-spinner"></div>
          <span>正在加载怪物详情...</span>
        </div>
      </div>
    );
  }

  // 渲染错误状态
  if (error) {
    return (
      <div className="monster-detail-page">
        <div className="monster-detail-page__error">
          <div className="error-message">
            <h3>😕 加载失败</h3>
            <p>{error}</p>
            <div className="error-actions">
              <button
                onClick={() => window.location.reload()}
                className="btn btn-primary"
              >
                重新加载
              </button>
              <Link to="/monsters" className="btn btn-secondary">
                返回列表
              </Link>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!monster) {
    return (
      <div className="monster-detail-page">
        <div className="monster-detail-page__error">
          <div className="error-message">
            <h3>😕 怪物不存在</h3>
            <p>找不到指定的怪物</p>
            <Link to="/monsters" className="btn btn-primary">
              返回列表
            </Link>
          </div>
        </div>
      </div>
    );
  }

  const monsterName = formatMonsterName(monster);
  const categoryColor = getMonsterCategoryColor(monster.category);
  const elementColor = getMonsterElementColor(monster.element);
  const isBoss = isMonsterBoss(monster);
  const isElite = isMonsterElite(monster);

  return (
    <div className="monster-detail-page">
      {/* 面包屑导航 */}
      <div className="breadcrumb">
        <Link to="/monsters">怪物信息</Link>
        <span className="separator">/</span>
        <span className="current">{monsterName}</span>
      </div>

      {/* 怪物基本信息头部 */}
      <div className="monster-detail-page__header">
        <div className="monster-header-content">
          <div className="monster-image-section">
            <div className="monster-main-image">
              <img
                src={monster.image || `/images/monsters/${monster.id}.png`}
                alt={monsterName}
                onError={(e) => {
                  e.target.style.display = 'none';
                  e.target.nextSibling.style.display = 'flex';
                }}
              />
              <div className="monster-image-placeholder" style={{ display: 'none' }}>
                <div className="monster-icon">
                  {isBoss ? '👹' : isElite ? '💀' : '🦴'}
                </div>
              </div>
            </div>
          </div>

          <div className="monster-info-section">
            <div className="monster-badges">
              <span className={`category-badge ${categoryColor}`}>
                {monster.category}
              </span>
              {monster.element && (
                <span className={`element-badge ${elementColor}`}>
                  {monster.element}
                </span>
              )}
            </div>

            <h1 className="monster-name">{monsterName}</h1>

            <div className="monster-basic-info">
              <div className="info-row">
                <span className="info-label">族群:</span>
                <span className="info-value">{monster.family}</span>
              </div>
              <div className="info-row">
                <span className="info-label">等级:</span>
                <span className="info-value">{formatMonsterLevel(monster.level)}</span>
              </div>
              {monster.world_level && (
                <div className="info-row">
                  <span className="info-label">世界等级:</span>
                  <span className="info-value">{monster.world_level}</span>
                </div>
              )}
              <div className="info-row">
                <span className="info-label">地区:</span>
                <span className="info-value">{monster.region}</span>
              </div>
            </div>

            <div className="monster-stats">
              <div className="stat-item">
                <div className="stat-value">{monster.hp?.toLocaleString()}</div>
                <div className="stat-label">生命值</div>
              </div>
              <div className="stat-item">
                <div className="stat-value">{monster.attack?.toLocaleString()}</div>
                <div className="stat-label">攻击力</div>
              </div>
              {monster.defense && (
                <div className="stat-item">
                  <div className="stat-value">{monster.defense.toLocaleString()}</div>
                  <div className="stat-label">防御力</div>
                </div>
              )}
              <div className="stat-item">
                <div className="stat-value">{formatExpReward(monster.exp_reward)}</div>
                <div className="stat-label">经验奖励</div>
              </div>
              <div className="stat-item">
                <div className="stat-value">{formatMoraReward(monster.mora_reward)}</div>
                <div className="stat-label">摩拉奖励</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 标签页导航 */}
      <div className="monster-detail-page__tabs">
        <div className="tabs-nav">
          <button
            className={`tab-button ${activeTab === 'overview' ? 'active' : ''}`}
            onClick={() => setActiveTab('overview')}
          >
            基本信息
          </button>
          <button
            className={`tab-button ${activeTab === 'abilities' ? 'active' : ''}`}
            onClick={() => setActiveTab('abilities')}
          >
            技能特点
          </button>
          <button
            className={`tab-button ${activeTab === 'drops' ? 'active' : ''}`}
            onClick={() => setActiveTab('drops')}
          >
            掉落物品
          </button>
          <button
            className={`tab-button ${activeTab === 'family' ? 'active' : ''}`}
            onClick={() => setActiveTab('family')}
          >
            同族群怪物
          </button>
        </div>

        <div className="tabs-content">
          {/* 基本信息标签 */}
          {activeTab === 'overview' && (
            <div className="tab-panel">
              <div className="overview-grid">
                <div className="overview-section">
                  <h3>基础属性</h3>
                  <div className="attributes-list">
                    <div className="attribute-item">
                      <span className="attribute-label">仇恨范围:</span>
                      <span className="attribute-value">{monster.aggro_range}m</span>
                    </div>
                    {monster.movement_speed && (
                      <div className="attribute-item">
                        <span className="attribute-label">移动速度:</span>
                        <span className="attribute-value">{monster.movement_speed}</span>
                      </div>
                    )}
                    {monster.spawn_locations && monster.spawn_locations.length > 0 && (
                      <div className="attribute-item">
                        <span className="attribute-label">出现位置:</span>
                        <div className="locations-list">
                          {monster.spawn_locations.map((location, index) => (
                            <span key={index} className="location-tag">{location}</span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>

                {monster.weak_points && monster.weak_points.length > 0 && (
                  <div className="overview-section">
                    <h3>弱点信息</h3>
                    <div className="weak-points-list">
                      {monster.weak_points.map((point, index) => (
                        <div key={index} className="weak-point-item">
                          {point}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {monster.resistances && Object.keys(monster.resistances).length > 0 && (
                  <div className="overview-section">
                    <h3>抗性信息</h3>
                    <div className="resistances-grid">
                      {Object.entries(monster.resistances).map(([element, resistance]) => {
                        const { level, color } = getResistanceLevel(resistance);
                        return (
                          <div key={element} className="resistance-item">
                            <span className="resistance-element">{element}:</span>
                            <span className={`resistance-value ${color}`}>
                              {resistance}% ({level})
                            </span>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                )}

                {monster.description && (
                  <div className="overview-section description-section">
                    <h3>怪物描述</h3>
                    <p className="monster-description">{monster.description}</p>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* 技能特点标签 */}
          {activeTab === 'abilities' && (
            <div className="tab-panel">
              {monster.abilities && monster.abilities.length > 0 ? (
                <div className="abilities-list">
                  {monster.abilities.map((ability, index) => (
                    <div key={index} className="ability-card">
                      <h4 className="ability-name">{ability.name}</h4>
                      <p className="ability-description">{ability.description}</p>
                      {ability.damage && (
                        <div className="ability-damage">
                          <span className="damage-label">伤害:</span>
                          <span className="damage-value">{ability.damage}</span>
                        </div>
                      )}
                      {ability.cooldown && (
                        <div className="ability-cooldown">
                          <span className="cooldown-label">冷却时间:</span>
                          <span className="cooldown-value">{ability.cooldown}秒</span>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <div className="empty-content">
                  <p>暂无技能信息</p>
                </div>
              )}
            </div>
          )}

          {/* 掉落物品标签 */}
          {activeTab === 'drops' && (
            <div className="tab-panel">
              {monster.drops && monster.drops.length > 0 ? (
                <div className="drops-list">
                  {monster.drops.map((drop, index) => (
                    <div key={index} className="drop-card">
                      <div className="drop-info">
                        <h4 className="drop-name">{drop.item_name}</h4>
                        <div className="drop-details">
                          <span className="drop-rate">掉落率: {drop.drop_rate}%</span>
                          {drop.quantity_min && drop.quantity_max && (
                            <span className="drop-quantity">
                              数量: {drop.quantity_min}-{drop.quantity_max}
                            </span>
                          )}
                        </div>
                      </div>
                      {drop.rarity && (
                        <div className={`drop-rarity rarity-${drop.rarity}`}>
                          {drop.rarity}星
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <div className="empty-content">
                  <p>暂无掉落信息</p>
                </div>
              )}
            </div>
          )}

          {/* 同族群怪物标签 */}
          {activeTab === 'family' && (
            <div className="tab-panel">
              <h3>族群: {monster.family}</h3>
              {familyLoading ? (
                <div className="loading-content">
                  <span>正在加载族群信息...</span>
                </div>
              ) : familyMonsters.length > 0 ? (
                <div className="family-monsters-grid">
                  {familyMonsters.map((familyMonster) => (
                    <div
                      key={familyMonster.id}
                      className={`family-monster-card ${familyMonster.id === monster.id ? 'current' : ''}`}
                      onClick={() => {
                        if (familyMonster.id !== monster.id) {
                          navigate(`/monsters/${familyMonster.id}`);
                        }
                      }}
                    >
                      <div className="family-monster-image">
                        <img
                          src={familyMonster.image || `/images/monsters/${familyMonster.id}.png`}
                          alt={formatMonsterName(familyMonster)}
                          onError={(e) => {
                            e.target.style.display = 'none';
                            e.target.nextSibling.style.display = 'flex';
                          }}
                        />
                        <div className="family-monster-placeholder" style={{ display: 'none' }}>
                          <div className="monster-icon">
                            {isMonsterBoss(familyMonster) ? '👹' : isMonsterElite(familyMonster) ? '💀' : '🦴'}
                          </div>
                        </div>
                      </div>
                      <div className="family-monster-info">
                        <h4 className="family-monster-name">
                          {formatMonsterName(familyMonster)}
                        </h4>
                        <div className="family-monster-details">
                          <span className="family-monster-level">
                            {formatMonsterLevel(familyMonster.level)}
                          </span>
                          <span className={`family-monster-category ${getMonsterCategoryColor(familyMonster.category)}`}>
                            {familyMonster.category}
                          </span>
                        </div>
                      </div>
                      {familyMonster.id === monster.id && (
                        <div className="current-marker">当前</div>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <div className="empty-content">
                  <p>暂无同族群怪物信息</p>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default MonsterDetailPage;

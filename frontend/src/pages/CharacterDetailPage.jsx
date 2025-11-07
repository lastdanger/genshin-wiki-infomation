/**
 * 角色详情页面
 *
 * 显示单个角色的完整信息，包括基本属性、技能、天赋等
 */
import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import characterAPI, { characterUtils } from '../services/characterAPI';
import { utils } from '../services/api';
import './CharacterDetailPage.css';

const CharacterDetailPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();

  // 数据状态
  const [character, setCharacter] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // 技能状态
  const [skills, setSkills] = useState([]);
  const [skillsLoading, setSkillsLoading] = useState(false);
  const [skillsError, setSkillsError] = useState(null);

  // 界面状态
  const [activeTab, setActiveTab] = useState('overview'); // overview, skills, talents, builds

  // 加载角色详情
  const loadCharacterDetail = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      console.log('🔍 加载角色详情:', id);

      const response = await characterAPI.getCharacterDetail(parseInt(id), {
        include_skills: true,
        include_talents: true
      });

      if (response.success) {
        setCharacter(response.data);

        // 如果响应中包含技能数据，直接设置
        if (response.data.skills) {
          setSkills(response.data.skills);
        }
      } else {
        throw new Error(response.error || '获取角色详情失败');
      }
    } catch (err) {
      console.error('❌ 加载角色详情失败:', err);
      setError(utils.formatError(err));
    } finally {
      setLoading(false);
    }
  }, [id]);

  // 加载角色技能
  const loadCharacterSkills = useCallback(async () => {
    if (!id || skills.length > 0) return;

    try {
      setSkillsLoading(true);
      setSkillsError(null);

      const response = await characterAPI.getCharacterSkills(parseInt(id));

      if (response.success) {
        setSkills(response.data.skills || []);
      } else {
        throw new Error(response.error || '获取技能信息失败');
      }
    } catch (err) {
      console.error('❌ 加载技能失败:', err);
      setSkillsError(utils.formatError(err));
    } finally {
      setSkillsLoading(false);
    }
  }, [id, skills.length]);

  // 初始化数据加载
  useEffect(() => {
    if (id) {
      loadCharacterDetail();
    }
  }, [id, loadCharacterDetail]);

  // 当角色数据加载完成后，加载技能数据
  useEffect(() => {
    if (character && !skills.length) {
      loadCharacterSkills();
    }
  }, [character, skills.length, loadCharacterSkills]);

  // 处理返回按钮
  const handleGoBack = useCallback(() => {
    navigate('/characters');
  }, [navigate]);

  // 渲染加载状态
  if (loading) {
    return (
      <div className="character-detail-page">
        <div className="character-detail-page__loading">
          <div className="loading-content">
            <div className="loading-spinner"></div>
            <h2>正在加载角色信息...</h2>
            <p>请稍候，我们正在为您准备详细的角色资料</p>
          </div>
        </div>
      </div>
    );
  }

  // 渲染错误状态
  if (error) {
    return (
      <div className="character-detail-page">
        <div className="character-detail-page__error">
          <div className="error-content">
            <h2>😕 加载失败</h2>
            <p>{error}</p>
            <div className="error-actions">
              <button className="btn btn-primary" onClick={() => window.location.reload()}>
                重新加载
              </button>
              <button className="btn btn-secondary" onClick={handleGoBack}>
                返回列表
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // 如果没有角色数据
  if (!character) {
    return (
      <div className="character-detail-page">
        <div className="character-detail-page__not-found">
          <div className="not-found-content">
            <h2>🔍 角色不存在</h2>
            <p>抱歉，我们没有找到ID为 {id} 的角色信息</p>
            <Link to="/characters" className="btn btn-primary">
              浏览所有角色
            </Link>
          </div>
        </div>
      </div>
    );
  }

  const formatStats = characterUtils.formatCharacterStats(character);
  const elementClass = characterUtils.getElementColorClass(character.element);
  const rarityStars = characterUtils.getRarityStars(character.rarity);

  return (
    <div className="character-detail-page">
      {/* 返回按钮 */}
      <div className="character-detail-page__nav">
        <button onClick={handleGoBack} className="btn-back">
          ← 返回角色列表
        </button>
      </div>

      {/* 角色头部信息 */}
      <div className={`character-detail-page__header ${elementClass}`}>
        <div className="character-header-content">
          <div className="character-avatar-section">
            <div className="character-avatar-container">
              <div className="character-avatar-placeholder">
                <span className="character-avatar-icon">
                  {character.name?.[0] || '?'}
                </span>
              </div>

              {/* 稀有度星级 */}
              <div className={`character-rarity rarity-${character.rarity}`}>
                {rarityStars}
              </div>
            </div>
          </div>

          <div className="character-info-section">
            <div className="character-main-info">
              <h1 className="character-name">{character.name}</h1>

              {character.title && (
                <p className="character-title">{character.title}</p>
              )}

              <div className="character-attributes">
                <div className={`character-element ${elementClass}`}>
                  <span className="attribute-icon">
                    {getElementIcon(character.element)}
                  </span>
                  <span className="attribute-name">
                    {getElementName(character.element)}
                  </span>
                </div>

                <div className="character-weapon">
                  <span className="attribute-icon">
                    {getWeaponIcon(character.weapon_type)}
                  </span>
                  <span className="attribute-name">
                    {getWeaponTypeName(character.weapon_type)}
                  </span>
                </div>

                {character.region && (
                  <div className="character-region">
                    <span className="attribute-icon">🏰</span>
                    <span className="attribute-name">
                      {getRegionName(character.region)}
                    </span>
                  </div>
                )}
              </div>

              {character.description && (
                <p className="character-description">
                  {character.description}
                </p>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* 标签页导航 */}
      <div className="character-detail-page__tabs">
        <div className="tabs-container">
          <button
            onClick={() => setActiveTab('overview')}
            className={`tab-btn ${activeTab === 'overview' ? 'active' : ''}`}
          >
            概览
          </button>
          <button
            onClick={() => setActiveTab('skills')}
            className={`tab-btn ${activeTab === 'skills' ? 'active' : ''}`}
          >
            技能天赋
          </button>
          <button
            onClick={() => setActiveTab('stats')}
            className={`tab-btn ${activeTab === 'stats' ? 'active' : ''}`}
          >
            属性数值
          </button>
        </div>
      </div>

      {/* 标签页内容 */}
      <div className="character-detail-page__content">
        {/* 概览标签页 */}
        {activeTab === 'overview' && (
          <div className="tab-content overview-tab">
            <div className="overview-grid">
              {/* 基础属性 */}
              <div className="info-card">
                <h3>基础属性</h3>
                <div className="stats-grid">
                  <div className="stat-item">
                    <span className="stat-label">生命值</span>
                    <span className="stat-value">{formatStats.hp}</span>
                  </div>
                  <div className="stat-item">
                    <span className="stat-label">攻击力</span>
                    <span className="stat-value">{formatStats.atk}</span>
                  </div>
                  <div className="stat-item">
                    <span className="stat-label">防御力</span>
                    <span className="stat-value">{formatStats.def}</span>
                  </div>
                </div>

                {/* 突破属性 */}
                {character.ascension_stats && (
                  <div className="ascension-stats">
                    <h4>突破属性</h4>
                    <div className="ascension-stat">
                      <span className="stat-label">{character.ascension_stats.stat}</span>
                      <span className="stat-value">{character.ascension_stats.value}</span>
                    </div>
                  </div>
                )}
              </div>

              {/* 角色信息 */}
              <div className="info-card">
                <h3>角色信息</h3>
                <div className="character-meta">
                  {character.birthday && (
                    <div className="meta-item">
                      <span className="meta-label">生日</span>
                      <span className="meta-value">{formatDate(character.birthday)}</span>
                    </div>
                  )}

                  {character.constellation_name && (
                    <div className="meta-item">
                      <span className="meta-label">命座</span>
                      <span className="meta-value">{character.constellation_name}</span>
                    </div>
                  )}

                  {character.affiliation && (
                    <div className="meta-item">
                      <span className="meta-label">所属</span>
                      <span className="meta-value">{character.affiliation}</span>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* 技能天赋标签页 */}
        {activeTab === 'skills' && (
          <div className="tab-content skills-tab">
            {skillsLoading ? (
              <div className="skills-loading">
                <p>正在加载技能信息...</p>
              </div>
            ) : skillsError ? (
              <div className="skills-error">
                <p>加载技能失败: {skillsError}</p>
                <button onClick={loadCharacterSkills} className="btn btn-primary">
                  重试
                </button>
              </div>
            ) : skills.length > 0 ? (
              <div className="skills-grid">
                {skills.map((skill, index) => (
                  <SkillCard key={skill.id || index} skill={skill} />
                ))}
              </div>
            ) : (
              <div className="no-skills">
                <p>暂无技能信息</p>
              </div>
            )}
          </div>
        )}

        {/* 属性数值标签页 */}
        {activeTab === 'stats' && (
          <div className="tab-content stats-tab">
            <div className="stats-detail">
              <div className="info-card">
                <h3>详细属性</h3>
                <div className="detailed-stats">
                  <div className="stat-row">
                    <span className="stat-name">基础生命值</span>
                    <span className="stat-number">{formatStats.hp}</span>
                  </div>
                  <div className="stat-row">
                    <span className="stat-name">基础攻击力</span>
                    <span className="stat-number">{formatStats.atk}</span>
                  </div>
                  <div className="stat-row">
                    <span className="stat-name">基础防御力</span>
                    <span className="stat-number">{formatStats.def}</span>
                  </div>

                  {character.ascension_stats && (
                    <div className="stat-row highlight">
                      <span className="stat-name">{character.ascension_stats.stat}</span>
                      <span className="stat-number">{character.ascension_stats.value}</span>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

// 技能卡片组件
const SkillCard = ({ skill }) => {
  return (
    <div className="skill-card">
      <div className="skill-header">
        <h4 className="skill-name">{skill.name}</h4>
        <span className="skill-type">{getSkillTypeName(skill.skill_type)}</span>
      </div>

      <p className="skill-description">{skill.description}</p>

      {/* 技能属性 */}
      <div className="skill-meta">
        {skill.cooldown && (
          <div className="skill-attribute">
            <span className="attr-label">冷却时间</span>
            <span className="attr-value">{skill.cooldown}秒</span>
          </div>
        )}

        {skill.energy_cost && (
          <div className="skill-attribute">
            <span className="attr-label">能量消耗</span>
            <span className="attr-value">{skill.energy_cost}</span>
          </div>
        )}
      </div>
    </div>
  );
};

// 辅助函数
const getElementIcon = (element) => {
  const icons = {
    'Pyro': '🔥', 'Hydro': '💧', 'Anemo': '🌪️', 'Electro': '⚡',
    'Dendro': '🌿', 'Cryo': '❄️', 'Geo': '🟡'
  };
  return icons[element] || '❓';
};

const getElementName = (element) => {
  const names = {
    'Pyro': '火', 'Hydro': '水', 'Anemo': '风', 'Electro': '雷',
    'Dendro': '草', 'Cryo': '冰', 'Geo': '岩'
  };
  return names[element] || element;
};

const getWeaponIcon = (weaponType) => {
  const icons = {
    'Sword': '⚔️', 'Claymore': '🗡️', 'Polearm': '🏹',
    'Bow': '🏹', 'Catalyst': '📖'
  };
  return icons[weaponType] || '⚔️';
};

const getWeaponTypeName = (weaponType) => {
  const names = {
    'Sword': '单手剑', 'Claymore': '双手剑', 'Polearm': '长柄武器',
    'Bow': '弓', 'Catalyst': '法器'
  };
  return names[weaponType] || weaponType;
};

const getRegionName = (region) => {
  const names = {
    'Mondstadt': '蒙德', 'Liyue': '璃月', 'Inazuma': '稻妻',
    'Sumeru': '须弥', 'Fontaine': '枫丹', 'Natlan': '纳塔', 'Snezhnaya': '至冬'
  };
  return names[region] || region;
};

const getSkillTypeName = (skillType) => {
  const names = {
    'normal_attack': '普通攻击',
    'elemental_skill': '元素战技',
    'elemental_burst': '元素爆发',
    'passive': '固有天赋'
  };
  return names[skillType] || skillType;
};

const formatDate = (dateString) => {
  if (!dateString) return '';

  try {
    const date = new Date(dateString);
    return date.toLocaleDateString('zh-CN', {
      month: 'long',
      day: 'numeric'
    });
  } catch {
    return dateString;
  }
};

export default CharacterDetailPage;
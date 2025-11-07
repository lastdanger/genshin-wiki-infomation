/**
 * 圣遗物详情页面
 *
 * 显示单个圣遗物的完整信息，包括属性、套装效果、获取方式等
 */
import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import artifactAPI, { artifactUtils } from '../services/artifactAPI';
import { utils } from '../services/api';
import './ArtifactDetailPage.css';

const ArtifactDetailPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();

  // 数据状态
  const [artifact, setArtifact] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // 套装相关状态
  const [setArtifacts, setSetArtifacts] = useState([]);
  const [setArtifactsLoading, setSetArtifactsLoading] = useState(false);

  // 界面状态
  const [activeTab, setActiveTab] = useState('overview'); // overview, set-effects, set-pieces

  // 加载圣遗物详情
  const loadArtifactDetail = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      console.log('🔍 加载圣遗物详情:', id);

      const response = await artifactAPI.getArtifactDetail(parseInt(id));

      if (response.success) {
        setArtifact(response.data);
      } else {
        throw new Error(response.error || '获取圣遗物详情失败');
      }
    } catch (err) {
      console.error('❌ 加载圣遗物详情失败:', err);
      setError(utils.formatError(err));
    } finally {
      setLoading(false);
    }
  }, [id]);

  // 加载套装其他件
  const loadSetArtifacts = useCallback(async () => {
    if (!artifact || setArtifactsLoading) return;

    try {
      setSetArtifactsLoading(true);

      const response = await artifactAPI.getArtifactsBySet(artifact.set_name);

      if (response.success) {
        setSetArtifacts(response.data.artifacts || []);
      }
    } catch (err) {
      console.warn('获取套装信息失败:', err);
    } finally {
      setSetArtifactsLoading(false);
    }
  }, [artifact, setArtifactsLoading]);

  // 初始化加载
  useEffect(() => {
    loadArtifactDetail();
  }, [loadArtifactDetail]);

  // 加载套装信息
  useEffect(() => {
    if (artifact && activeTab === 'set-pieces') {
      loadSetArtifacts();
    }
  }, [artifact, activeTab, loadSetArtifacts]);

  // 渲染加载状态
  if (loading) {
    return (
      <div className="artifact-detail-page">
        <div className="artifact-detail-page__loading">
          <div className="loading-spinner"></div>
          <span>正在加载圣遗物详情...</span>
        </div>
      </div>
    );
  }

  // 渲染错误状态
  if (error) {
    return (
      <div className="artifact-detail-page">
        <div className="artifact-detail-page__error">
          <div className="error-message">
            <h3>😕 加载失败</h3>
            <p>{error}</p>
            <div className="error-actions">
              <button
                className="btn btn-primary"
                onClick={() => window.location.reload()}
              >
                重新加载
              </button>
              <Link to="/artifacts" className="btn btn-secondary">
                返回列表
              </Link>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // 没有数据
  if (!artifact) {
    return (
      <div className="artifact-detail-page">
        <div className="artifact-detail-page__not-found">
          <h3>🔍 圣遗物不存在</h3>
          <p>请检查URL或返回列表页面</p>
          <Link to="/artifacts" className="btn btn-primary">
            返回圣遗物列表
          </Link>
        </div>
      </div>
    );
  }

  const slotDisplayName = artifactUtils.getSlotDisplayName(artifact.slot);
  const rarityStars = artifactUtils.getRarityStars(artifact.rarity);
  const rarityClass = artifactUtils.getRarityColorClass(artifact.rarity);
  const mainStatDisplay = artifactUtils.formatMainStat(artifact.main_stat_type, artifact.main_stat_value);
  const subStats = artifactUtils.formatSubStats(artifact.sub_stats);

  return (
    <div className="artifact-detail-page">
      {/* 返回按钮 */}
      <div className="artifact-detail-page__nav">
        <Link to="/artifacts" className="back-link">
          ← 返回圣遗物列表
        </Link>
      </div>

      {/* 圣遗物头部信息 */}
      <div className={`artifact-detail-page__header ${rarityClass}`}>
        <div className="header-content">
          <div className="artifact-icon">
            <div className="artifact-icon__placeholder">
              <span className="artifact-icon__slot" data-slot={artifact.slot}>
                {getSlotIcon(artifact.slot)}
              </span>
            </div>
            <div className={`artifact-icon__rarity ${rarityClass}`}>
              {rarityStars}
            </div>
          </div>

          <div className="artifact-info">
            <div className="artifact-info__header">
              <h1 className="artifact-name">{artifact.name}</h1>
              {artifact.name_en && (
                <p className="artifact-name-en">{artifact.name_en}</p>
              )}
            </div>

            <div className="artifact-info__meta">
              <span className="artifact-set">
                套装：<strong>{artifact.set_name}</strong>
              </span>
              <span className="artifact-slot">
                部位：<strong>{slotDisplayName}</strong>
              </span>
              <span className="artifact-rarity">
                稀有度：<strong>{artifact.rarity}★</strong>
              </span>
            </div>

            {artifact.description && (
              <p className="artifact-description">{artifact.description}</p>
            )}
          </div>
        </div>
      </div>

      {/* 标签导航 */}
      <div className="artifact-detail-page__tabs">
        <button
          className={`tab-button ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          基础信息
        </button>
        <button
          className={`tab-button ${activeTab === 'set-effects' ? 'active' : ''}`}
          onClick={() => setActiveTab('set-effects')}
        >
          套装效果
        </button>
        <button
          className={`tab-button ${activeTab === 'set-pieces' ? 'active' : ''}`}
          onClick={() => setActiveTab('set-pieces')}
        >
          套装件数
        </button>
      </div>

      {/* 内容区域 */}
      <div className="artifact-detail-page__content">
        {activeTab === 'overview' && (
          <div className="overview-tab">
            <div className="info-grid">
              {/* 主属性 */}
              <div className="info-card">
                <h3>主属性</h3>
                <div className="main-stat">
                  <span className="main-stat__type">{artifact.main_stat_type}</span>
                  <span className="main-stat__value">{artifact.main_stat_value}</span>
                </div>
              </div>

              {/* 副属性 */}
              {subStats && subStats.length > 0 && (
                <div className="info-card">
                  <h3>副属性</h3>
                  <div className="sub-stats">
                    {subStats.map((stat, index) => (
                      <div key={index} className="sub-stat">
                        <span className="sub-stat__type">{stat.stat_type}</span>
                        <span className="sub-stat__value">+{stat.stat_value}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* 获取方式 */}
              <div className="info-card">
                <h3>获取方式</h3>
                <div className="acquisition-info">
                  {artifact.source && (
                    <div className="acquisition-item">
                      <span className="acquisition-label">来源</span>
                      <span className="acquisition-value">{artifact.source}</span>
                    </div>
                  )}
                  {artifact.domain_name && (
                    <div className="acquisition-item">
                      <span className="acquisition-label">副本</span>
                      <span className="acquisition-value">{artifact.domain_name}</span>
                    </div>
                  )}
                  <div className="acquisition-item">
                    <span className="acquisition-label">最大等级</span>
                    <span className="acquisition-value">{artifact.max_level}</span>
                  </div>
                </div>
              </div>

              {/* 背景故事 */}
              {artifact.lore && (
                <div className="info-card lore-card">
                  <h3>背景故事</h3>
                  <p className="artifact-lore">{artifact.lore}</p>
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'set-effects' && (
          <div className="set-effects-tab">
            <div className="set-effects-container">
              <h2>{artifact.set_name} 套装效果</h2>

              {artifact.set_effects && (
                <div className="set-effects-list">
                  {artifact.set_effects['2'] && (
                    <div className="set-effect">
                      <div className="set-effect__header">
                        <span className="set-effect__count">2件套效果</span>
                        <span className="set-effect__name">{artifact.set_effects['2'].name}</span>
                      </div>
                      <div className="set-effect__description">
                        {artifact.set_effects['2'].description}
                      </div>
                    </div>
                  )}

                  {artifact.set_effects['4'] && (
                    <div className="set-effect">
                      <div className="set-effect__header">
                        <span className="set-effect__count">4件套效果</span>
                        <span className="set-effect__name">{artifact.set_effects['4'].name}</span>
                      </div>
                      <div className="set-effect__description">
                        {artifact.set_effects['4'].description}
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* 套装效果说明 */}
              <div className="set-effects-note">
                <h4>套装效果说明</h4>
                <ul>
                  <li>2件套效果：装备该套装中任意2件圣遗物即可获得效果</li>
                  <li>4件套效果：装备该套装中4件圣遗物即可获得效果（包含2件套效果）</li>
                  <li>套装效果可以与其他套装的2件套效果叠加</li>
                </ul>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'set-pieces' && (
          <div className="set-pieces-tab">
            <h2>{artifact.set_name} 套装组成</h2>

            {setArtifactsLoading ? (
              <div className="set-loading">
                <span>正在加载套装信息...</span>
              </div>
            ) : (
              <div className="set-pieces-grid">
                {setArtifacts.map((setArtifact) => (
                  <Link
                    key={setArtifact.id}
                    to={`/artifacts/${setArtifact.id}`}
                    className={`set-piece ${setArtifact.id === artifact.id ? 'current' : ''}`}
                  >
                    <div className="set-piece__icon">
                      <span data-slot={setArtifact.slot}>
                        {getSlotIcon(setArtifact.slot)}
                      </span>
                    </div>
                    <div className="set-piece__info">
                      <h4>{setArtifact.name}</h4>
                      <p>{artifactUtils.getSlotDisplayName(setArtifact.slot)}</p>
                      <span className="set-piece__main-stat">
                        {setArtifact.main_stat_type} {setArtifact.main_stat_value}
                      </span>
                    </div>
                  </Link>
                ))}
              </div>
            )}

            <div className="set-completion">
              <div className="completion-info">
                <span className="completion-text">
                  套装完整度：{setArtifacts.length}/5 件
                </span>
                <div className="completion-bar">
                  <div
                    className="completion-progress"
                    style={{ width: `${artifactUtils.getSetCompleteness(setArtifacts)}%` }}
                  ></div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

// 获取部位图标
const getSlotIcon = (slot) => {
  const slotIcons = {
    'flower': '🌸',
    'plume': '🪶',
    'sands': '⏳',
    'goblet': '🏺',
    'circlet': '👑'
  };
  return slotIcons[slot] || '🔮';
};

export default ArtifactDetailPage;

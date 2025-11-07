/**
 * 管理后台主页面
 *
 * 提供数据管理功能的导航和概览
 */
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './AdminPage.css';

// API服务
import characterAPI from '../services/characterAPI';
import weaponAPI from '../services/weaponAPI';
import artifactAPI from '../services/artifactAPI';
import monsterAPI from '../services/monsterAPI';

const AdminPage = () => {
  const navigate = useNavigate();
  const [stats, setStats] = useState({
    characters: { total: 0, loading: true },
    weapons: { total: 0, loading: true },
    artifacts: { total: 0, loading: true },
    monsters: { total: 0, loading: true }
  });

  // 获取统计数据
  useEffect(() => {
    const fetchStats = async () => {
      try {
        // 并行获取所有统计数据
        const [charactersRes, weaponsRes, artifactsRes, monstersRes] = await Promise.allSettled([
          characterAPI.getCharacterStats(),
          weaponAPI.getWeaponStats(),
          artifactAPI.getArtifactStats(),
          monsterAPI.getMonsterStats()
        ]);

        setStats({
          characters: {
            total: charactersRes.status === 'fulfilled' ? charactersRes.value?.total_characters || 0 : 0,
            loading: false
          },
          weapons: {
            total: weaponsRes.status === 'fulfilled' ? weaponsRes.value?.total_weapons || 0 : 0,
            loading: false
          },
          artifacts: {
            total: artifactsRes.status === 'fulfilled' ? artifactsRes.value?.total_artifacts || 0 : 0,
            loading: false
          },
          monsters: {
            total: monstersRes.status === 'fulfilled' ? monstersRes.value?.total_monsters || 0 : 0,
            loading: false
          }
        });
      } catch (error) {
        console.error('获取统计数据失败:', error);
        setStats(prev => ({
          ...prev,
          characters: { ...prev.characters, loading: false },
          weapons: { ...prev.weapons, loading: false },
          artifacts: { ...prev.artifacts, loading: false },
          monsters: { ...prev.monsters, loading: false }
        }));
      }
    };

    fetchStats();
  }, []);

  // 管理功能卡片数据
  const managementCards = [
    {
      title: '角色管理',
      description: '管理游戏角色信息、技能、天赋等数据',
      icon: '👤',
      count: stats.characters.total,
      loading: stats.characters.loading,
      path: '/admin/characters',
      color: 'character'
    },
    {
      title: '武器管理',
      description: '管理武器属性、被动技能、突破材料等数据',
      icon: '⚔️',
      count: stats.weapons.total,
      loading: stats.weapons.loading,
      path: '/admin/weapons',
      color: 'weapon'
    },
    {
      title: '圣遗物管理',
      description: '管理圣遗物套装、属性、获取方式等数据',
      icon: '💎',
      count: stats.artifacts.total,
      loading: stats.artifacts.loading,
      path: '/admin/artifacts',
      color: 'artifact'
    },
    {
      title: '怪物管理',
      description: '管理怪物信息、抗性、掉落物等数据',
      icon: '👹',
      count: stats.monsters.total,
      loading: stats.monsters.loading,
      path: '/admin/monsters',
      color: 'monster'
    }
  ];

  const handleCardClick = (path) => {
    navigate(path);
  };

  return (
    <div className="admin-page">
      {/* 页面头部 */}
      <header className="admin-header">
        <div className="admin-header-content">
          <h1>数据管理中心</h1>
          <p>原神游戏信息网站 - 后台管理系统</p>
        </div>
        <div className="admin-actions">
          <button className="admin-btn admin-btn-primary">
            📊 数据统计
          </button>
          <button className="admin-btn admin-btn-secondary">
            📥 数据导入
          </button>
          <button className="admin-btn admin-btn-secondary">
            📤 数据导出
          </button>
        </div>
      </header>

      {/* 功能卡片网格 */}
      <div className="admin-content">
        <div className="management-grid">
          {managementCards.map((card, index) => (
            <div
              key={index}
              className={`management-card management-card--${card.color}`}
              onClick={() => handleCardClick(card.path)}
            >
              <div className="management-card__header">
                <span className="management-card__icon">{card.icon}</span>
                <div className="management-card__info">
                  <h3 className="management-card__title">{card.title}</h3>
                  <div className="management-card__count">
                    {card.loading ? (
                      <div className="loading-spinner">载入中...</div>
                    ) : (
                      <span>{card.count} 条数据</span>
                    )}
                  </div>
                </div>
              </div>
              <p className="management-card__description">{card.description}</p>
              <div className="management-card__actions">
                <span className="management-card__action">📝 查看管理</span>
                <span className="management-card__arrow">→</span>
              </div>
            </div>
          ))}
        </div>

        {/* 快捷操作面板 */}
        <div className="quick-actions">
          <h2>快捷操作</h2>
          <div className="quick-actions-grid">
            <div className="quick-action-item" onClick={() => navigate('/admin/characters')}>
              <div className="quick-action-icon">➕</div>
              <div className="quick-action-content">
                <h3>添加角色</h3>
                <p>快速添加新角色信息</p>
              </div>
            </div>
            <div className="quick-action-item" onClick={() => navigate('/admin/weapons')}>
              <div className="quick-action-icon">⚡</div>
              <div className="quick-action-content">
                <h3>添加武器</h3>
                <p>快速添加新武器数据</p>
              </div>
            </div>
            <div className="quick-action-item">
              <div className="quick-action-icon">🔍</div>
              <div className="quick-action-content">
                <h3>数据检查</h3>
                <p>检查数据完整性和一致性</p>
              </div>
            </div>
            <div className="quick-action-item">
              <div className="quick-action-icon">🔄</div>
              <div className="quick-action-content">
                <h3>同步数据</h3>
                <p>从官方源同步最新数据</p>
              </div>
            </div>
          </div>
        </div>

        {/* 系统状态 */}
        <div className="system-status">
          <h2>系统状态</h2>
          <div className="status-grid">
            <div className="status-item status-item--success">
              <span className="status-icon">✅</span>
              <div className="status-content">
                <h4>数据库连接</h4>
                <p>正常</p>
              </div>
            </div>
            <div className="status-item status-item--success">
              <span className="status-icon">🌐</span>
              <div className="status-content">
                <h4>API服务</h4>
                <p>运行正常</p>
              </div>
            </div>
            <div className="status-item status-item--warning">
              <span className="status-icon">⚠️</span>
              <div className="status-content">
                <h4>缓存状态</h4>
                <p>需要刷新</p>
              </div>
            </div>
            <div className="status-item status-item--info">
              <span className="status-icon">📈</span>
              <div className="status-content">
                <h4>总数据量</h4>
                <p>{stats.characters.total + stats.weapons.total + stats.artifacts.total + stats.monsters.total} 条</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminPage;
/**
 * 怪物管理页面
 */
import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import monsterAPI from '../../services/monsterAPI';
import './AdminMonstersPage.css';

const AdminMonstersPage = () => {
  const navigate = useNavigate();

  // 状态管理
  const [monsters, setMonsters] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // 分页状态
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalCount, setTotalCount] = useState(0);
  const [pageSize] = useState(20);

  // 搜索和过滤状态
  const [searchTerm, setSearchTerm] = useState('');
  const [filters, setFilters] = useState({
    monster_type: '',
    category: '',
    element: '',
    region: ''
  });

  // 表单状态
  const [showForm, setShowForm] = useState(false);
  const [formMode, setFormMode] = useState('create'); // 'create' | 'edit'
  const [selectedMonster, setSelectedMonster] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    name_en: '',
    monster_type: '',
    category: '',
    level_range: '',
    element: '',
    resistances: {},
    immunities: [],
    hp_scaling: {},
    attack_patterns: [],
    weak_points: '',
    drops: [],
    locations: [],
    description: '',
    strategy_tips: ''
  });

  // 获取怪物列表
  const fetchMonsters = useCallback(async () => {
    try {
      setLoading(true);
      setError('');

      const params = {
        page: currentPage,
        per_page: pageSize,
        search: searchTerm,
        ...filters
      };

      // 过滤空值
      Object.keys(params).forEach(key => {
        if (params[key] === '' || params[key] === null || params[key] === undefined) {
          delete params[key];
        }
      });

      const response = await monsterAPI.getMonsterListEnhanced(params);

      setMonsters(response.data.items || response.data || []);
      setTotalPages(response.data.pages || 1);
      setTotalCount(response.data.total || 0);
    } catch (err) {
      console.error('获取怪物列表失败:', err);
      setError(err.message || '获取怪物列表失败');
    } finally {
      setLoading(false);
    }
  }, [currentPage, pageSize, searchTerm, filters]);

  // 初始化和数据变化时重新获取
  useEffect(() => {
    fetchMonsters();
  }, [fetchMonsters]);

  // 搜索处理
  const handleSearch = (e) => {
    e.preventDefault();
    setCurrentPage(1); // 重置到第一页
    fetchMonsters();
  };

  // 过滤器变化处理
  const handleFilterChange = (filterName, value) => {
    setFilters(prev => ({
      ...prev,
      [filterName]: value
    }));
    setCurrentPage(1);
  };

  // 表单处理
  const handleOpenForm = (mode, monster = null) => {
    setFormMode(mode);
    setSelectedMonster(monster);

    if (mode === 'edit' && monster) {
      setFormData({
        name: monster.name || '',
        name_en: monster.name_en || '',
        monster_type: monster.monster_type || '',
        category: monster.category || '',
        level_range: monster.level_range || '',
        element: monster.element || '',
        resistances: monster.resistances || {},
        immunities: monster.immunities || [],
        hp_scaling: monster.hp_scaling || {},
        attack_patterns: monster.attack_patterns || [],
        weak_points: monster.weak_points || '',
        drops: monster.drops || [],
        locations: monster.locations || [],
        description: monster.description || '',
        strategy_tips: monster.strategy_tips || ''
      });
    } else {
      setFormData({
        name: '',
        name_en: '',
        monster_type: '',
        category: '',
        level_range: '',
        element: '',
        resistances: {},
        immunities: [],
        hp_scaling: {},
        attack_patterns: [],
        weak_points: '',
        drops: [],
        locations: [],
        description: '',
        strategy_tips: ''
      });
    }

    setShowForm(true);
  };

  const handleCloseForm = () => {
    setShowForm(false);
    setSelectedMonster(null);
    setFormData({
      name: '',
      name_en: '',
      monster_type: '',
      category: '',
      level_range: '',
      element: '',
      resistances: {},
      immunities: [],
      hp_scaling: {},
      attack_patterns: [],
      weak_points: '',
      drops: [],
      locations: [],
      description: '',
      strategy_tips: ''
    });
  };

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      setLoading(true);

      if (formMode === 'create') {
        await monsterAPI.createMonster(formData);
      } else {
        await monsterAPI.updateMonster(selectedMonster.id, formData);
      }

      await fetchMonsters();
      handleCloseForm();
    } catch (err) {
      console.error('保存怪物失败:', err);
      setError(err.message || '保存怪物失败');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (monster) => {
    if (!window.confirm(`确定要删除怪物 "${monster.name}" 吗？此操作不可恢复。`)) {
      return;
    }

    try {
      setLoading(true);
      await monsterAPI.deleteMonster(monster.id);
      await fetchMonsters();
    } catch (err) {
      console.error('删除怪物失败:', err);
      setError(err.message || '删除怪物失败');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="admin-monsters-page">
      {/* 页面头部 */}
      <div className="admin-monsters-header">
        <div className="header-left">
          <button
            className="back-btn"
            onClick={() => navigate('/admin')}
          >
            ← 返回
          </button>
          <div className="header-title">
            <h1>怪物管理</h1>
            <p>管理游戏中的所有怪物信息</p>
          </div>
        </div>
        <div className="header-actions">
          <button
            className="create-btn"
            onClick={() => handleOpenForm('create')}
            disabled={loading}
          >
            + 添加怪物
          </button>
        </div>
      </div>

      {/* 错误消息 */}
      {error && (
        <div className="error-message">
          <span>{error}</span>
          <button className="close-error" onClick={() => setError('')}>×</button>
        </div>
      )}

      {/* 搜索和过滤 */}
      <div className="search-section">
        <form className="search-form" onSubmit={handleSearch}>
          <input
            type="text"
            placeholder="搜索怪物名称..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
          />
          <button type="submit" className="search-btn" disabled={loading}>
            搜索
          </button>
        </form>

        <div className="filters">
          <select
            className="filter-select"
            value={filters.monster_type}
            onChange={(e) => handleFilterChange('monster_type', e.target.value)}
          >
            <option value="">所有类型</option>
            <option value="Common Enemy">普通怪物</option>
            <option value="Elite Enemy">精英怪物</option>
            <option value="Boss">首领</option>
            <option value="Weekly Boss">周本首领</option>
            <option value="World Boss">世界首领</option>
          </select>

          <select
            className="filter-select"
            value={filters.category}
            onChange={(e) => handleFilterChange('category', e.target.value)}
          >
            <option value="">所有分类</option>
            <option value="Normal">普通</option>
            <option value="Elite">精英</option>
            <option value="Boss">首领</option>
          </select>

          <select
            className="filter-select"
            value={filters.element}
            onChange={(e) => handleFilterChange('element', e.target.value)}
          >
            <option value="">所有元素</option>
            <option value="Anemo">风</option>
            <option value="Geo">岩</option>
            <option value="Electro">雷</option>
            <option value="Dendro">草</option>
            <option value="Hydro">水</option>
            <option value="Pyro">火</option>
            <option value="Cryo">冰</option>
            <option value="None">无元素</option>
          </select>
        </div>
      </div>

      {/* 怪物列表 */}
      <div className="monsters-section">
        {loading && <div className="loading">加载中...</div>}

        {!loading && monsters.length === 0 && (
          <div className="empty-state">
            <div className="empty-icon">👹</div>
            <h3>暂无怪物数据</h3>
            <p>点击上方"添加怪物"按钮开始添加怪物信息</p>
          </div>
        )}

        {!loading && monsters.length > 0 && (
          <>
            <div className="monsters-table">
              <div className="table-header">
                <div>名称</div>
                <div>类型</div>
                <div>分类</div>
                <div>元素</div>
                <div>等级</div>
                <div>操作</div>
              </div>

              {monsters.map(monster => (
                <div key={monster.id} className="table-row">
                  <div className="col-name">
                    <div className="monster-name">
                      <strong>{monster.name}</strong>
                      {monster.name_en && <small>{monster.name_en}</small>}
                    </div>
                  </div>
                  <div className="col-type">{monster.monster_type || '未分类'}</div>
                  <div className="col-category">
                    <span className={`category category-${monster.category?.toLowerCase() || 'normal'}`}>
                      {monster.category || '普通'}
                    </span>
                  </div>
                  <div className="col-element">
                    <span className={`element element-${monster.element?.toLowerCase() || 'none'}`}>
                      {monster.element || '无'}
                    </span>
                  </div>
                  <div className="col-level">{monster.level_range || '未设定'}</div>
                  <div className="col-actions">
                    <button
                      className="edit-btn"
                      onClick={() => handleOpenForm('edit', monster)}
                      disabled={loading}
                    >
                      编辑
                    </button>
                    <button
                      className="delete-btn"
                      onClick={() => handleDelete(monster)}
                      disabled={loading}
                    >
                      删除
                    </button>
                  </div>
                </div>
              ))}
            </div>

            {/* 分页 */}
            <div className="pagination">
              <button
                className="page-btn"
                onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
                disabled={currentPage === 1 || loading}
              >
                上一页
              </button>
              <span className="page-info">
                第 {currentPage} 页，共 {totalPages} 页 ({totalCount} 条记录)
              </span>
              <button
                className="page-btn"
                onClick={() => setCurrentPage(prev => Math.min(prev + 1, totalPages))}
                disabled={currentPage === totalPages || loading}
              >
                下一页
              </button>
            </div>
          </>
        )}
      </div>

      {/* 表单弹窗 */}
      {showForm && (
        <div className="form-overlay">
          <div className="form-modal">
            <div className="form-header">
              <h2>{formMode === 'create' ? '添加怪物' : '编辑怪物'}</h2>
              <button className="close-form" onClick={handleCloseForm}>×</button>
            </div>

            <form className="monster-form" onSubmit={handleSubmit}>
              <div className="form-grid">
                <div className="form-group">
                  <label>怪物名称 *</label>
                  <input
                    type="text"
                    value={formData.name}
                    onChange={(e) => handleInputChange('name', e.target.value)}
                    placeholder="请输入怪物名称"
                    required
                  />
                </div>

                <div className="form-group">
                  <label>英文名称</label>
                  <input
                    type="text"
                    value={formData.name_en}
                    onChange={(e) => handleInputChange('name_en', e.target.value)}
                    placeholder="请输入英文名称"
                  />
                </div>

                <div className="form-group">
                  <label>怪物类型 *</label>
                  <select
                    value={formData.monster_type}
                    onChange={(e) => handleInputChange('monster_type', e.target.value)}
                    required
                  >
                    <option value="">请选择类型</option>
                    <option value="Common Enemy">普通怪物</option>
                    <option value="Elite Enemy">精英怪物</option>
                    <option value="Boss">首领</option>
                    <option value="Weekly Boss">周本首领</option>
                    <option value="World Boss">世界首领</option>
                  </select>
                </div>

                <div className="form-group">
                  <label>分类 *</label>
                  <select
                    value={formData.category}
                    onChange={(e) => handleInputChange('category', e.target.value)}
                    required
                  >
                    <option value="">请选择分类</option>
                    <option value="Normal">普通</option>
                    <option value="Elite">精英</option>
                    <option value="Boss">首领</option>
                  </select>
                </div>

                <div className="form-group">
                  <label>等级范围</label>
                  <input
                    type="text"
                    value={formData.level_range}
                    onChange={(e) => handleInputChange('level_range', e.target.value)}
                    placeholder="如: 1-90"
                  />
                </div>

                <div className="form-group">
                  <label>元素属性</label>
                  <select
                    value={formData.element}
                    onChange={(e) => handleInputChange('element', e.target.value)}
                  >
                    <option value="">无元素</option>
                    <option value="Anemo">风</option>
                    <option value="Geo">岩</option>
                    <option value="Electro">雷</option>
                    <option value="Dendro">草</option>
                    <option value="Hydro">水</option>
                    <option value="Pyro">火</option>
                    <option value="Cryo">冰</option>
                  </select>
                </div>

                <div className="form-group full-width">
                  <label>弱点部位</label>
                  <input
                    type="text"
                    value={formData.weak_points}
                    onChange={(e) => handleInputChange('weak_points', e.target.value)}
                    placeholder="如: 头部, 核心, 弱点等"
                  />
                </div>

                <div className="form-group full-width">
                  <label>描述</label>
                  <textarea
                    value={formData.description}
                    onChange={(e) => handleInputChange('description', e.target.value)}
                    placeholder="请输入怪物描述"
                    rows="3"
                  />
                </div>

                <div className="form-group full-width">
                  <label>攻略提示</label>
                  <textarea
                    value={formData.strategy_tips}
                    onChange={(e) => handleInputChange('strategy_tips', e.target.value)}
                    placeholder="请输入攻略建议和应对策略"
                    rows="3"
                  />
                </div>
              </div>

              <div className="form-actions">
                <button
                  type="button"
                  className="cancel-btn"
                  onClick={handleCloseForm}
                  disabled={loading}
                >
                  取消
                </button>
                <button
                  type="submit"
                  className="submit-btn"
                  disabled={loading}
                >
                  {loading ? '保存中...' : (formMode === 'create' ? '添加' : '保存')}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminMonstersPage;
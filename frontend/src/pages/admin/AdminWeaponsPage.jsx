/**
 * 武器管理页面
 *
 * 提供武器数据的完整CRUD管理功能
 */
import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import weaponAPI from '../../services/weaponAPI';
import './AdminWeaponsPage.css';

const AdminWeaponsPage = () => {
  const navigate = useNavigate();

  // 状态管理
  const [weapons, setWeapons] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedWeapon, setSelectedWeapon] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const [formMode, setFormMode] = useState('create'); // 'create' | 'edit'
  const [searchTerm, setSearchTerm] = useState('');

  // 分页状态
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(0);
  const [totalWeapons, setTotalWeapons] = useState(0);
  const perPage = 10;

  // 表单数据
  const [formData, setFormData] = useState({
    name: '',
    name_en: '',
    weapon_type: 'Sword',
    rarity: 4,
    base_attack: 0,
    secondary_stat: '',
    secondary_stat_value: '',
    description: '',
    lore: '',
    passive_name: '',
    passive_description: '',
    source: '祈愿',
    max_level: 90
  });

  // 武器类型选项
  const weaponTypes = [
    { value: 'Sword', label: '单手剑' },
    { value: 'Claymore', label: '双手剑' },
    { value: 'Polearm', label: '长柄武器' },
    { value: 'Bow', label: '弓' },
    { value: 'Catalyst', label: '法器' }
  ];

  // 获取方式选项
  const sourceOptions = ['祈愿', '锻造', '活动', '商店', '任务奖励', '成就奖励'];

  // 获取武器列表
  const fetchWeapons = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const params = {
        page: currentPage,
        per_page: perPage,
        search: searchTerm || undefined
      };

      const response = await weaponAPI.getWeaponList(params);

      if (response.success) {
        setWeapons(response.data.weapons || []);
        setTotalWeapons(response.data.total || 0);
        setTotalPages(response.data.pages || 0);
      } else {
        throw new Error(response.message || '获取武器列表失败');
      }
    } catch (err) {
      console.error('获取武器列表失败:', err);
      setError(err.message || '获取武器列表失败');
      setWeapons([]);
    } finally {
      setLoading(false);
    }
  }, [currentPage, searchTerm]);

  // 初始加载
  useEffect(() => {
    fetchWeapons();
  }, [fetchWeapons]);

  // 处理搜索
  const handleSearch = (e) => {
    e.preventDefault();
    setCurrentPage(1);
    fetchWeapons();
  };

  // 处理表单提交
  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      setLoading(true);

      if (formMode === 'create') {
        await weaponAPI.createWeapon(formData);
      } else {
        await weaponAPI.updateWeapon(selectedWeapon.id, formData);
      }

      // 重新获取列表
      await fetchWeapons();

      // 关闭表单
      handleCloseForm();

    } catch (err) {
      console.error('保存武器失败:', err);
      setError(err.message || '保存武器失败');
    } finally {
      setLoading(false);
    }
  };

  // 处理删除
  const handleDelete = async (weapon) => {
    if (!window.confirm(`确定要删除武器"${weapon.name}"吗？此操作不可恢复！`)) {
      return;
    }

    try {
      setLoading(true);
      await weaponAPI.deleteWeapon(weapon.id);
      await fetchWeapons();
    } catch (err) {
      console.error('删除武器失败:', err);
      setError(err.message || '删除武器失败');
    } finally {
      setLoading(false);
    }
  };

  // 打开创建表单
  const handleCreate = () => {
    setFormMode('create');
    setSelectedWeapon(null);
    setFormData({
      name: '',
      name_en: '',
      weapon_type: 'Sword',
      rarity: 4,
      base_attack: 0,
      secondary_stat: '',
      secondary_stat_value: '',
      description: '',
      lore: '',
      passive_name: '',
      passive_description: '',
      source: '祈愿',
      max_level: 90
    });
    setShowForm(true);
  };

  // 打开编辑表单
  const handleEdit = (weapon) => {
    setFormMode('edit');
    setSelectedWeapon(weapon);
    setFormData({
      name: weapon.name || '',
      name_en: weapon.name_en || '',
      weapon_type: weapon.weapon_type || 'Sword',
      rarity: weapon.rarity || 4,
      base_attack: weapon.base_attack || 0,
      secondary_stat: weapon.secondary_stat || '',
      secondary_stat_value: weapon.secondary_stat_value || '',
      description: weapon.description || '',
      lore: weapon.lore || '',
      passive_name: weapon.passive_name || '',
      passive_description: weapon.passive_description || '',
      source: weapon.source || '祈愿',
      max_level: weapon.max_level || 90
    });
    setShowForm(true);
  };

  // 关闭表单
  const handleCloseForm = () => {
    setShowForm(false);
    setSelectedWeapon(null);
    setError(null);
  };

  // 处理表单输入变化
  const handleInputChange = (e) => {
    const { name, value, type } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'number' ? parseInt(value) || 0 : value
    }));
  };

  // 分页处理
  const handlePageChange = (page) => {
    setCurrentPage(page);
  };

  return (
    <div className="admin-weapons-page">
      {/* 页面头部 */}
      <div className="admin-weapons-header">
        <div className="header-left">
          <button
            onClick={() => navigate('/admin')}
            className="back-btn"
          >
            ← 返回管理中心
          </button>
          <div className="header-title">
            <h1>武器管理</h1>
            <p>共 {totalWeapons} 把武器</p>
          </div>
        </div>

        <div className="header-actions">
          <button
            onClick={handleCreate}
            className="create-btn"
            disabled={loading}
          >
            ➕ 添加武器
          </button>
        </div>
      </div>

      {/* 搜索栏 */}
      <div className="search-section">
        <form onSubmit={handleSearch} className="search-form">
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="搜索武器名称、被动技能..."
            className="search-input"
          />
          <button type="submit" className="search-btn" disabled={loading}>
            🔍 搜索
          </button>
        </form>
      </div>

      {/* 错误提示 */}
      {error && (
        <div className="error-message">
          <span>⚠️ {error}</span>
          <button onClick={() => setError(null)} className="close-error">×</button>
        </div>
      )}

      {/* 武器列表 */}
      <div className="weapons-section">
        {loading && weapons.length === 0 ? (
          <div className="loading">加载中...</div>
        ) : (
          <>
            <div className="weapons-table">
              <div className="table-header">
                <span className="col-name">武器名称</span>
                <span className="col-type">类型</span>
                <span className="col-rarity">稀有度</span>
                <span className="col-attack">基础攻击力</span>
                <span className="col-source">获取方式</span>
                <span className="col-actions">操作</span>
              </div>

              {weapons.map(weapon => (
                <div key={weapon.id} className="table-row">
                  <span className="col-name">
                    <div className="weapon-name">
                      <strong>{weapon.name}</strong>
                      {weapon.name_en && <small>{weapon.name_en}</small>}
                    </div>
                  </span>
                  <span className="col-type">{weaponTypes.find(t => t.value === weapon.weapon_type)?.label || weapon.weapon_type}</span>
                  <span className="col-rarity">
                    <span className={`rarity rarity-${weapon.rarity}`}>
                      {'★'.repeat(weapon.rarity)}
                    </span>
                  </span>
                  <span className="col-attack">{weapon.base_attack}</span>
                  <span className="col-source">{weapon.source}</span>
                  <span className="col-actions">
                    <button
                      onClick={() => handleEdit(weapon)}
                      className="edit-btn"
                      disabled={loading}
                    >
                      ✏️ 编辑
                    </button>
                    <button
                      onClick={() => handleDelete(weapon)}
                      className="delete-btn"
                      disabled={loading}
                    >
                      🗑️ 删除
                    </button>
                  </span>
                </div>
              ))}
            </div>

            {/* 分页 */}
            {totalPages > 1 && (
              <div className="pagination">
                <button
                  onClick={() => handlePageChange(currentPage - 1)}
                  disabled={currentPage === 1 || loading}
                  className="page-btn"
                >
                  上一页
                </button>

                <span className="page-info">
                  第 {currentPage} 页，共 {totalPages} 页
                </span>

                <button
                  onClick={() => handlePageChange(currentPage + 1)}
                  disabled={currentPage === totalPages || loading}
                  className="page-btn"
                >
                  下一页
                </button>
              </div>
            )}
          </>
        )}

        {!loading && weapons.length === 0 && (
          <div className="empty-state">
            <div className="empty-icon">⚔️</div>
            <h3>暂无武器数据</h3>
            <p>点击"添加武器"按钮创建第一个武器</p>
          </div>
        )}
      </div>

      {/* 表单弹窗 */}
      {showForm && (
        <div className="form-overlay">
          <div className="form-modal">
            <div className="form-header">
              <h2>{formMode === 'create' ? '添加武器' : '编辑武器'}</h2>
              <button onClick={handleCloseForm} className="close-form">×</button>
            </div>

            <form onSubmit={handleSubmit} className="weapon-form">
              <div className="form-grid">
                {/* 基本信息 */}
                <div className="form-group">
                  <label htmlFor="name">武器名称 *</label>
                  <input
                    type="text"
                    id="name"
                    name="name"
                    value={formData.name}
                    onChange={handleInputChange}
                    required
                    placeholder="例如：原木刀"
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="name_en">英文名称</label>
                  <input
                    type="text"
                    id="name_en"
                    name="name_en"
                    value={formData.name_en}
                    onChange={handleInputChange}
                    placeholder="例如：Sapwood Blade"
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="weapon_type">武器类型 *</label>
                  <select
                    id="weapon_type"
                    name="weapon_type"
                    value={formData.weapon_type}
                    onChange={handleInputChange}
                    required
                  >
                    {weaponTypes.map(type => (
                      <option key={type.value} value={type.value}>
                        {type.label}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="form-group">
                  <label htmlFor="rarity">稀有度 *</label>
                  <select
                    id="rarity"
                    name="rarity"
                    value={formData.rarity}
                    onChange={handleInputChange}
                    required
                  >
                    <option value={3}>3星</option>
                    <option value={4}>4星</option>
                    <option value={5}>5星</option>
                  </select>
                </div>

                <div className="form-group">
                  <label htmlFor="base_attack">基础攻击力 *</label>
                  <input
                    type="number"
                    id="base_attack"
                    name="base_attack"
                    value={formData.base_attack}
                    onChange={handleInputChange}
                    required
                    min="1"
                    placeholder="例如：565"
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="secondary_stat">副属性类型</label>
                  <input
                    type="text"
                    id="secondary_stat"
                    name="secondary_stat"
                    value={formData.secondary_stat}
                    onChange={handleInputChange}
                    placeholder="例如：元素精通"
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="secondary_stat_value">副属性数值</label>
                  <input
                    type="text"
                    id="secondary_stat_value"
                    name="secondary_stat_value"
                    value={formData.secondary_stat_value}
                    onChange={handleInputChange}
                    placeholder="例如：165"
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="source">获取方式 *</label>
                  <select
                    id="source"
                    name="source"
                    value={formData.source}
                    onChange={handleInputChange}
                    required
                  >
                    {sourceOptions.map(source => (
                      <option key={source} value={source}>
                        {source}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="form-group">
                  <label htmlFor="max_level">最大等级</label>
                  <input
                    type="number"
                    id="max_level"
                    name="max_level"
                    value={formData.max_level}
                    onChange={handleInputChange}
                    min="1"
                    max="90"
                  />
                </div>

                {/* 描述信息 */}
                <div className="form-group full-width">
                  <label htmlFor="description">武器描述</label>
                  <textarea
                    id="description"
                    name="description"
                    value={formData.description}
                    onChange={handleInputChange}
                    rows="3"
                    placeholder="武器的基本描述信息"
                  />
                </div>

                <div className="form-group full-width">
                  <label htmlFor="lore">武器背景</label>
                  <textarea
                    id="lore"
                    name="lore"
                    value={formData.lore}
                    onChange={handleInputChange}
                    rows="3"
                    placeholder="武器的背景故事"
                  />
                </div>

                {/* 被动技能 */}
                <div className="form-group">
                  <label htmlFor="passive_name">被动技能名称</label>
                  <input
                    type="text"
                    id="passive_name"
                    name="passive_name"
                    value={formData.passive_name}
                    onChange={handleInputChange}
                    placeholder="例如：森林的箴言"
                  />
                </div>

                <div className="form-group full-width">
                  <label htmlFor="passive_description">被动技能描述</label>
                  <textarea
                    id="passive_description"
                    name="passive_description"
                    value={formData.passive_description}
                    onChange={handleInputChange}
                    rows="3"
                    placeholder="被动技能的详细效果描述"
                  />
                </div>
              </div>

              {/* 提交按钮 */}
              <div className="form-actions">
                <button
                  type="button"
                  onClick={handleCloseForm}
                  className="cancel-btn"
                  disabled={loading}
                >
                  取消
                </button>
                <button
                  type="submit"
                  className="submit-btn"
                  disabled={loading}
                >
                  {loading ? '保存中...' : (formMode === 'create' ? '创建武器' : '保存修改')}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminWeaponsPage;
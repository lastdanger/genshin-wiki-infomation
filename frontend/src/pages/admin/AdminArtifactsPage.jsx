/**
 * 圣遗物管理页面
 */
import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import artifactAPI, { ARTIFACT_SLOTS, MAIN_STAT_TYPES, SOURCES, RARITIES, artifactUtils } from '../../services/artifactAPI';
import './AdminArtifactsPage.css';

const AdminArtifactsPage = () => {
  const navigate = useNavigate();

  // 状态管理
  const [artifacts, setArtifacts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalArtifacts, setTotalArtifacts] = useState(0);

  // 表单状态
  const [showForm, setShowForm] = useState(false);
  const [formMode, setFormMode] = useState('create'); // 'create' or 'edit'
  const [selectedArtifact, setSelectedArtifact] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    name_en: '',
    set_name: '',
    set_name_en: '',
    slot: ARTIFACT_SLOTS.FLOWER,
    rarity: 5,
    description: '',
    lore: '',
    main_stat_type: MAIN_STAT_TYPES.HP,
    main_stat_value: '',
    sub_stats: [],
    set_effects: {
      '2': { effect_name: '', effect_description: '' },
      '4': { effect_name: '', effect_description: '' }
    },
    source: SOURCES.DOMAIN,
    domain_name: '',
    stat_progression: {},
    max_level: 20,
    is_set_piece: true
  });

  // 过滤状态
  const [filters, setFilters] = useState({
    set_name: '',
    slot: '',
    rarity: '',
    source: '',
    main_stat_type: ''
  });

  // 副属性编辑状态
  const [newSubStat, setNewSubStat] = useState({ stat_type: '', stat_value: '' });

  // 获取圣遗物列表
  const fetchArtifacts = useCallback(async (page = 1, search = '', filterOptions = {}) => {
    try {
      setLoading(true);
      setError(null);

      const params = {
        page,
        per_page: 10,
        search: search || undefined,
        ...Object.fromEntries(
          Object.entries(filterOptions).filter(([_, value]) => value)
        )
      };

      const response = await artifactAPI.getArtifactList(params);

      if (response.success) {
        setArtifacts(response.data.artifacts);
        setCurrentPage(response.data.page);
        setTotalPages(response.data.pages);
        setTotalArtifacts(response.data.total);
      } else {
        throw new Error(response.message || '获取圣遗物列表失败');
      }
    } catch (err) {
      console.error('获取圣遗物列表失败:', err);
      setError(err.message || '获取圣遗物列表失败');
      setArtifacts([]);
    } finally {
      setLoading(false);
    }
  }, []);

  // 初始化加载
  useEffect(() => {
    fetchArtifacts();
  }, [fetchArtifacts]);

  // 处理搜索
  const handleSearch = (e) => {
    e.preventDefault();
    setCurrentPage(1);
    fetchArtifacts(1, searchTerm, filters);
  };

  // 处理过滤
  const handleFilterChange = (filterType, value) => {
    const newFilters = { ...filters, [filterType]: value };
    setFilters(newFilters);
    setCurrentPage(1);
    fetchArtifacts(1, searchTerm, newFilters);
  };

  // 处理分页
  const handlePageChange = (newPage) => {
    if (newPage >= 1 && newPage <= totalPages) {
      setCurrentPage(newPage);
      fetchArtifacts(newPage, searchTerm, filters);
    }
  };

  // 打开创建表单
  const handleCreate = () => {
    setFormMode('create');
    setSelectedArtifact(null);
    setFormData({
      name: '',
      name_en: '',
      set_name: '',
      set_name_en: '',
      slot: ARTIFACT_SLOTS.FLOWER,
      rarity: 5,
      description: '',
      lore: '',
      main_stat_type: MAIN_STAT_TYPES.HP,
      main_stat_value: '',
      sub_stats: [],
      set_effects: {
        '2': { effect_name: '', effect_description: '' },
        '4': { effect_name: '', effect_description: '' }
      },
      source: SOURCES.DOMAIN,
      domain_name: '',
      stat_progression: {},
      max_level: 20,
      is_set_piece: true
    });
    setShowForm(true);
  };

  // 打开编辑表单
  const handleEdit = (artifact) => {
    setFormMode('edit');
    setSelectedArtifact(artifact);
    setFormData({
      name: artifact.name || '',
      name_en: artifact.name_en || '',
      set_name: artifact.set_name || '',
      set_name_en: artifact.set_name_en || '',
      slot: artifact.slot || ARTIFACT_SLOTS.FLOWER,
      rarity: artifact.rarity || 5,
      description: artifact.description || '',
      lore: artifact.lore || '',
      main_stat_type: artifact.main_stat_type || MAIN_STAT_TYPES.HP,
      main_stat_value: artifact.main_stat_value || '',
      sub_stats: artifact.sub_stats || [],
      set_effects: artifact.set_effects || {
        '2': { effect_name: '', effect_description: '' },
        '4': { effect_name: '', effect_description: '' }
      },
      source: artifact.source || SOURCES.DOMAIN,
      domain_name: artifact.domain_name || '',
      stat_progression: artifact.stat_progression || {},
      max_level: artifact.max_level || 20,
      is_set_piece: artifact.is_set_piece !== undefined ? artifact.is_set_piece : true
    });
    setShowForm(true);
  };

  // 关闭表单
  const handleCloseForm = () => {
    setShowForm(false);
    setSelectedArtifact(null);
    setFormMode('create');
    setNewSubStat({ stat_type: '', stat_value: '' });
  };

  // 处理表单输入
  const handleFormChange = (e) => {
    const { name, value, type, checked } = e.target;

    if (name.startsWith('set_effects.')) {
      const [_, setNum, field] = name.split('.');
      setFormData(prev => ({
        ...prev,
        set_effects: {
          ...prev.set_effects,
          [setNum]: {
            ...prev.set_effects[setNum],
            [field]: value
          }
        }
      }));
    } else {
      const convertedValue = type === 'number' ? parseInt(value) || 0 :
                           type === 'checkbox' ? checked : value;
      setFormData(prev => ({
        ...prev,
        [name]: convertedValue
      }));
    }
  };

  // 添加副属性
  const handleAddSubStat = () => {
    if (newSubStat.stat_type && newSubStat.stat_value) {
      setFormData(prev => ({
        ...prev,
        sub_stats: [...prev.sub_stats, { ...newSubStat }]
      }));
      setNewSubStat({ stat_type: '', stat_value: '' });
    }
  };

  // 删除副属性
  const handleRemoveSubStat = (index) => {
    setFormData(prev => ({
      ...prev,
      sub_stats: prev.sub_stats.filter((_, i) => i !== index)
    }));
  };

  // 提交表单
  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      setLoading(true);
      setError(null);

      // 数据验证
      if (!formData.name.trim()) {
        throw new Error('圣遗物名称不能为空');
      }
      if (!formData.set_name.trim()) {
        throw new Error('套装名称不能为空');
      }
      if (!formData.main_stat_value.trim()) {
        throw new Error('主属性数值不能为空');
      }

      if (formMode === 'create') {
        await artifactAPI.createArtifact(formData);
      } else {
        await artifactAPI.updateArtifact(selectedArtifact.id, formData);
      }

      await fetchArtifacts(currentPage, searchTerm, filters);
      handleCloseForm();
    } catch (err) {
      console.error('保存圣遗物失败:', err);
      setError(err.message || '保存圣遗物失败');
    } finally {
      setLoading(false);
    }
  };

  // 删除圣遗物
  const handleDelete = async (artifact) => {
    if (!window.confirm(`确定要删除圣遗物 "${artifact.name}" 吗？此操作不可撤销。`)) {
      return;
    }

    try {
      setLoading(true);
      setError(null);

      await artifactAPI.deleteArtifact(artifact.id);
      await fetchArtifacts(currentPage, searchTerm, filters);
    } catch (err) {
      console.error('删除圣遗物失败:', err);
      setError(err.message || '删除圣遗物失败');
    } finally {
      setLoading(false);
    }
  };

  // 关闭错误消息
  const handleCloseError = () => {
    setError(null);
  };

  return (
    <div className="admin-artifacts-page">
      {/* 页面头部 */}
      <div className="admin-artifacts-header">
        <div className="header-left">
          <button
            onClick={() => navigate('/admin')}
            className="back-btn"
            disabled={loading}
          >
            ← 返回管理中心
          </button>
          <div className="header-title">
            <h1>圣遗物管理</h1>
            <p>管理游戏圣遗物数据，包括套装效果、属性配置等</p>
          </div>
        </div>
        <div className="header-actions">
          <button
            onClick={handleCreate}
            className="create-btn"
            disabled={loading}
          >
            + 添加圣遗物
          </button>
        </div>
      </div>

      {/* 错误消息 */}
      {error && (
        <div className="error-message">
          <span>{error}</span>
          <button onClick={handleCloseError} className="close-error">×</button>
        </div>
      )}

      {/* 搜索和过滤区域 */}
      <div className="search-section">
        <form onSubmit={handleSearch} className="search-form">
          <input
            type="text"
            placeholder="搜索圣遗物名称、套装名称等..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
            disabled={loading}
          />
          <button type="submit" className="search-btn" disabled={loading}>
            搜索
          </button>
        </form>

        {/* 过滤器 */}
        <div className="filters">
          <input
            type="text"
            placeholder="套装名称"
            value={filters.set_name}
            onChange={(e) => handleFilterChange('set_name', e.target.value)}
            className="filter-input"
            disabled={loading}
          />

          <select
            value={filters.slot}
            onChange={(e) => handleFilterChange('slot', e.target.value)}
            className="filter-select"
            disabled={loading}
          >
            <option value="">所有部位</option>
            {Object.entries(ARTIFACT_SLOTS).map(([key, value]) => (
              <option key={key} value={value}>
                {artifactUtils.getSlotDisplayName(value)}
              </option>
            ))}
          </select>

          <select
            value={filters.rarity}
            onChange={(e) => handleFilterChange('rarity', e.target.value)}
            className="filter-select"
            disabled={loading}
          >
            <option value="">所有稀有度</option>
            {RARITIES.map(rarity => (
              <option key={rarity} value={rarity}>{rarity}星</option>
            ))}
          </select>

          <select
            value={filters.source}
            onChange={(e) => handleFilterChange('source', e.target.value)}
            className="filter-select"
            disabled={loading}
          >
            <option value="">所有来源</option>
            {Object.entries(SOURCES).map(([key, value]) => (
              <option key={key} value={value}>{value}</option>
            ))}
          </select>

          <select
            value={filters.main_stat_type}
            onChange={(e) => handleFilterChange('main_stat_type', e.target.value)}
            className="filter-select"
            disabled={loading}
          >
            <option value="">所有主属性</option>
            {Object.entries(MAIN_STAT_TYPES).map(([key, value]) => (
              <option key={key} value={value}>{value}</option>
            ))}
          </select>
        </div>
      </div>

      {/* 圣遗物列表 */}
      <div className="artifacts-section">
        {loading ? (
          <div className="loading">加载中...</div>
        ) : artifacts.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">💎</div>
            <h3>暂无圣遗物数据</h3>
            <p>点击"添加圣遗物"按钮创建第一个圣遗物</p>
          </div>
        ) : (
          <>
            {/* 圣遗物表格 */}
            <div className="artifacts-table">
              <div className="table-header">
                <div className="col-name">圣遗物信息</div>
                <div className="col-set">套装</div>
                <div className="col-slot">部位</div>
                <div className="col-rarity">稀有度</div>
                <div className="col-main-stat">主属性</div>
                <div className="col-actions">操作</div>
              </div>

              {artifacts.map((artifact) => (
                <div key={artifact.id} className="table-row">
                  <div className="col-name">
                    <div className="artifact-name">
                      <strong>{artifact.name}</strong>
                      {artifact.name_en && <small>{artifact.name_en}</small>}
                    </div>
                  </div>
                  <div className="col-set">{artifact.set_name}</div>
                  <div className="col-slot">
                    <span className={`slot slot-${artifact.slot}`}>
                      {artifactUtils.getSlotDisplayName(artifact.slot)}
                    </span>
                  </div>
                  <div className="col-rarity">
                    <span className={`rarity ${artifactUtils.getRarityColorClass(artifact.rarity)}`}>
                      {artifactUtils.getRarityStars(artifact.rarity)}
                    </span>
                  </div>
                  <div className="col-main-stat">
                    {artifactUtils.formatMainStat(artifact.main_stat_type, artifact.main_stat_value)}
                  </div>
                  <div className="col-actions">
                    <button
                      onClick={() => handleEdit(artifact)}
                      className="edit-btn"
                      disabled={loading}
                    >
                      编辑
                    </button>
                    <button
                      onClick={() => handleDelete(artifact)}
                      className="delete-btn"
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
                onClick={() => handlePageChange(currentPage - 1)}
                disabled={currentPage <= 1 || loading}
                className="page-btn"
              >
                上一页
              </button>
              <span className="page-info">
                第 {currentPage} 页，共 {totalPages} 页 (总共 {totalArtifacts} 个圣遗物)
              </span>
              <button
                onClick={() => handlePageChange(currentPage + 1)}
                disabled={currentPage >= totalPages || loading}
                className="page-btn"
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
              <h2>{formMode === 'create' ? '添加圣遗物' : '编辑圣遗物'}</h2>
              <button onClick={handleCloseForm} className="close-form">×</button>
            </div>

            <form onSubmit={handleSubmit} className="artifact-form">
              <div className="form-grid">
                {/* 基础信息 */}
                <div className="form-group">
                  <label>圣遗物名称 *</label>
                  <input
                    type="text"
                    name="name"
                    value={formData.name}
                    onChange={handleFormChange}
                    placeholder="输入圣遗物中文名"
                    required
                  />
                </div>

                <div className="form-group">
                  <label>英文名</label>
                  <input
                    type="text"
                    name="name_en"
                    value={formData.name_en}
                    onChange={handleFormChange}
                    placeholder="输入圣遗物英文名"
                  />
                </div>

                <div className="form-group">
                  <label>套装名称 *</label>
                  <input
                    type="text"
                    name="set_name"
                    value={formData.set_name}
                    onChange={handleFormChange}
                    placeholder="输入套装中文名"
                    required
                  />
                </div>

                <div className="form-group">
                  <label>套装英文名</label>
                  <input
                    type="text"
                    name="set_name_en"
                    value={formData.set_name_en}
                    onChange={handleFormChange}
                    placeholder="输入套装英文名"
                  />
                </div>

                <div className="form-group">
                  <label>部位 *</label>
                  <select
                    name="slot"
                    value={formData.slot}
                    onChange={handleFormChange}
                    required
                  >
                    {Object.entries(ARTIFACT_SLOTS).map(([key, value]) => (
                      <option key={key} value={value}>
                        {artifactUtils.getSlotDisplayName(value)}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="form-group">
                  <label>稀有度 *</label>
                  <select
                    name="rarity"
                    value={formData.rarity}
                    onChange={handleFormChange}
                    required
                  >
                    {RARITIES.map(rarity => (
                      <option key={rarity} value={rarity}>{rarity}星</option>
                    ))}
                  </select>
                </div>

                {/* 主属性 */}
                <div className="form-group">
                  <label>主属性类型 *</label>
                  <select
                    name="main_stat_type"
                    value={formData.main_stat_type}
                    onChange={handleFormChange}
                    required
                  >
                    {Object.entries(MAIN_STAT_TYPES).map(([key, value]) => (
                      <option key={key} value={value}>{value}</option>
                    ))}
                  </select>
                </div>

                <div className="form-group">
                  <label>主属性数值 *</label>
                  <input
                    type="text"
                    name="main_stat_value"
                    value={formData.main_stat_value}
                    onChange={handleFormChange}
                    placeholder="如：46.6%、311等"
                    required
                  />
                </div>

                {/* 获取方式 */}
                <div className="form-group">
                  <label>获取方式</label>
                  <select
                    name="source"
                    value={formData.source}
                    onChange={handleFormChange}
                  >
                    {Object.entries(SOURCES).map(([key, value]) => (
                      <option key={key} value={value}>{value}</option>
                    ))}
                  </select>
                </div>

                <div className="form-group">
                  <label>副本名称</label>
                  <input
                    type="text"
                    name="domain_name"
                    value={formData.domain_name}
                    onChange={handleFormChange}
                    placeholder="如：华池岩岫"
                  />
                </div>

                <div className="form-group">
                  <label>最大等级</label>
                  <input
                    type="number"
                    name="max_level"
                    value={formData.max_level}
                    onChange={handleFormChange}
                    min="1"
                    max="20"
                  />
                </div>

                <div className="form-group">
                  <label>
                    <input
                      type="checkbox"
                      name="is_set_piece"
                      checked={formData.is_set_piece}
                      onChange={handleFormChange}
                    />
                    是否为套装圣遗物
                  </label>
                </div>

                {/* 描述信息 */}
                <div className="form-group full-width">
                  <label>圣遗物描述</label>
                  <textarea
                    name="description"
                    value={formData.description}
                    onChange={handleFormChange}
                    placeholder="输入圣遗物的详细描述..."
                    rows="3"
                  />
                </div>

                <div className="form-group full-width">
                  <label>背景故事</label>
                  <textarea
                    name="lore"
                    value={formData.lore}
                    onChange={handleFormChange}
                    placeholder="输入圣遗物的背景故事..."
                    rows="3"
                  />
                </div>
              </div>

              {/* 副属性管理 */}
              <div className="sub-stats-section">
                <h3>副属性管理</h3>
                <div className="sub-stats-list">
                  {formData.sub_stats.map((subStat, index) => (
                    <div key={index} className="sub-stat-item">
                      <span>{subStat.stat_type} +{subStat.stat_value}</span>
                      <button
                        type="button"
                        onClick={() => handleRemoveSubStat(index)}
                        className="remove-sub-stat-btn"
                      >
                        删除
                      </button>
                    </div>
                  ))}
                </div>
                <div className="add-sub-stat">
                  <select
                    value={newSubStat.stat_type}
                    onChange={(e) => setNewSubStat({ ...newSubStat, stat_type: e.target.value })}
                    className="sub-stat-type"
                  >
                    <option value="">选择副属性类型</option>
                    {Object.entries(MAIN_STAT_TYPES).map(([key, value]) => (
                      <option key={key} value={value}>{value}</option>
                    ))}
                  </select>
                  <input
                    type="text"
                    value={newSubStat.stat_value}
                    onChange={(e) => setNewSubStat({ ...newSubStat, stat_value: e.target.value })}
                    placeholder="数值"
                    className="sub-stat-value"
                  />
                  <button
                    type="button"
                    onClick={handleAddSubStat}
                    className="add-sub-stat-btn"
                  >
                    添加
                  </button>
                </div>
              </div>

              {/* 套装效果 */}
              <div className="set-effects-section">
                <h3>套装效果</h3>
                <div className="set-effect-group">
                  <h4>2件套效果</h4>
                  <input
                    type="text"
                    name="set_effects.2.effect_name"
                    value={formData.set_effects['2']?.effect_name || ''}
                    onChange={handleFormChange}
                    placeholder="效果名称"
                    className="set-effect-name"
                  />
                  <textarea
                    name="set_effects.2.effect_description"
                    value={formData.set_effects['2']?.effect_description || ''}
                    onChange={handleFormChange}
                    placeholder="效果描述"
                    rows="2"
                    className="set-effect-desc"
                  />
                </div>
                <div className="set-effect-group">
                  <h4>4件套效果</h4>
                  <input
                    type="text"
                    name="set_effects.4.effect_name"
                    value={formData.set_effects['4']?.effect_name || ''}
                    onChange={handleFormChange}
                    placeholder="效果名称"
                    className="set-effect-name"
                  />
                  <textarea
                    name="set_effects.4.effect_description"
                    value={formData.set_effects['4']?.effect_description || ''}
                    onChange={handleFormChange}
                    placeholder="效果描述"
                    rows="2"
                    className="set-effect-desc"
                  />
                </div>
              </div>

              {/* 表单操作按钮 */}
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
                  {loading ? '保存中...' : '保存'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminArtifactsPage;
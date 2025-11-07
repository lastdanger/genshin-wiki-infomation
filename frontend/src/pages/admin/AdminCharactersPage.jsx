/**
 * 角色管理页面
 */
import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import characterAPI, { ELEMENTS, WEAPON_TYPES, REGIONS, RARITIES, characterUtils } from '../../services/characterAPI';
import './AdminCharactersPage.css';

const AdminCharactersPage = () => {
  const navigate = useNavigate();

  // 状态管理
  const [characters, setCharacters] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalCharacters, setTotalCharacters] = useState(0);

  // 表单状态
  const [showForm, setShowForm] = useState(false);
  const [formMode, setFormMode] = useState('create'); // 'create' or 'edit'
  const [selectedCharacter, setSelectedCharacter] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    name_en: '',
    element: ELEMENTS.PYRO,
    weapon_type: WEAPON_TYPES.SWORD,
    rarity: RARITIES.FOUR_STAR,
    region: REGIONS.MONDSTADT,
    base_stats: {
      hp: 0,
      atk: 0,
      def_: 0
    },
    ascension_stats: {
      stat: '',
      value: 0
    },
    description: '',
    birthday: '',
    constellation_name: '',
    title: '',
    affiliation: ''
  });

  // 过滤状态
  const [filters, setFilters] = useState({
    element: '',
    weapon_type: '',
    rarity: '',
    region: ''
  });

  // 获取角色列表
  const fetchCharacters = useCallback(async (page = 1, search = '', filterOptions = {}) => {
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

      const response = await characterAPI.getCharacterList(params);

      if (response.success) {
        setCharacters(response.data.characters);
        setCurrentPage(response.data.pagination.page);
        setTotalPages(response.data.pagination.total_pages);
        setTotalCharacters(response.data.pagination.total);
      } else {
        throw new Error(response.message || '获取角色列表失败');
      }
    } catch (err) {
      console.error('获取角色列表失败:', err);
      setError(err.message || '获取角色列表失败');
      setCharacters([]);
    } finally {
      setLoading(false);
    }
  }, []);

  // 初始化加载
  useEffect(() => {
    fetchCharacters();
  }, [fetchCharacters]);

  // 处理搜索
  const handleSearch = (e) => {
    e.preventDefault();
    setCurrentPage(1);
    fetchCharacters(1, searchTerm, filters);
  };

  // 处理过滤
  const handleFilterChange = (filterType, value) => {
    const newFilters = { ...filters, [filterType]: value };
    setFilters(newFilters);
    setCurrentPage(1);
    fetchCharacters(1, searchTerm, newFilters);
  };

  // 处理分页
  const handlePageChange = (newPage) => {
    if (newPage >= 1 && newPage <= totalPages) {
      setCurrentPage(newPage);
      fetchCharacters(newPage, searchTerm, filters);
    }
  };

  // 打开创建表单
  const handleCreate = () => {
    setFormMode('create');
    setSelectedCharacter(null);
    setFormData({
      name: '',
      name_en: '',
      element: ELEMENTS.PYRO,
      weapon_type: WEAPON_TYPES.SWORD,
      rarity: RARITIES.FOUR_STAR,
      region: REGIONS.MONDSTADT,
      base_stats: {
        hp: 0,
        atk: 0,
        def_: 0
      },
      ascension_stats: {
        stat: '',
        value: 0
      },
      description: '',
      birthday: '',
      constellation_name: '',
      title: '',
      affiliation: ''
    });
    setShowForm(true);
  };

  // 打开编辑表单
  const handleEdit = (character) => {
    setFormMode('edit');
    setSelectedCharacter(character);
    setFormData({
      name: character.name || '',
      name_en: character.name_en || '',
      element: character.element || ELEMENTS.PYRO,
      weapon_type: character.weapon_type || WEAPON_TYPES.SWORD,
      rarity: character.rarity || RARITIES.FOUR_STAR,
      region: character.region || REGIONS.MONDSTADT,
      base_stats: {
        hp: character.base_stats?.hp || 0,
        atk: character.base_stats?.atk || 0,
        def_: character.base_stats?.def_ || 0
      },
      ascension_stats: {
        stat: character.ascension_stats?.stat || '',
        value: character.ascension_stats?.value || 0
      },
      description: character.description || '',
      birthday: character.birthday || '',
      constellation_name: character.constellation_name || '',
      title: character.title || '',
      affiliation: character.affiliation || ''
    });
    setShowForm(true);
  };

  // 关闭表单
  const handleCloseForm = () => {
    setShowForm(false);
    setSelectedCharacter(null);
    setFormMode('create');
  };

  // 处理表单输入
  const handleFormChange = (e) => {
    const { name, value, type } = e.target;

    if (name.startsWith('base_stats.')) {
      const statName = name.split('.')[1];
      setFormData(prev => ({
        ...prev,
        base_stats: {
          ...prev.base_stats,
          [statName]: type === 'number' ? parseInt(value) || 0 : value
        }
      }));
    } else if (name.startsWith('ascension_stats.')) {
      const statName = name.split('.')[1];
      setFormData(prev => ({
        ...prev,
        ascension_stats: {
          ...prev.ascension_stats,
          [statName]: statName === 'value' ? parseFloat(value) || 0 : value
        }
      }));
    } else {
      const convertedValue = type === 'number' ? parseInt(value) || 0 : value;
      setFormData(prev => ({
        ...prev,
        [name]: convertedValue
      }));
    }
  };

  // 提交表单
  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      setLoading(true);
      setError(null);

      // 数据验证
      if (!formData.name.trim()) {
        throw new Error('角色名称不能为空');
      }

      if (formMode === 'create') {
        await characterAPI.createCharacter(formData);
      } else {
        await characterAPI.updateCharacter(selectedCharacter.id, formData);
      }

      await fetchCharacters(currentPage, searchTerm, filters);
      handleCloseForm();
    } catch (err) {
      console.error('保存角色失败:', err);
      setError(err.message || '保存角色失败');
    } finally {
      setLoading(false);
    }
  };

  // 删除角色
  const handleDelete = async (character) => {
    if (!window.confirm(`确定要删除角色 "${character.name}" 吗？此操作不可撤销。`)) {
      return;
    }

    try {
      setLoading(true);
      setError(null);

      await characterAPI.deleteCharacter(character.id);
      await fetchCharacters(currentPage, searchTerm, filters);
    } catch (err) {
      console.error('删除角色失败:', err);
      setError(err.message || '删除角色失败');
    } finally {
      setLoading(false);
    }
  };

  // 关闭错误消息
  const handleCloseError = () => {
    setError(null);
  };

  return (
    <div className="admin-characters-page">
      {/* 页面头部 */}
      <div className="admin-characters-header">
        <div className="header-left">
          <button
            onClick={() => navigate('/admin')}
            className="back-btn"
            disabled={loading}
          >
            ← 返回管理中心
          </button>
          <div className="header-title">
            <h1>角色管理</h1>
            <p>管理游戏角色数据，包括基础信息、属性配置等</p>
          </div>
        </div>
        <div className="header-actions">
          <button
            onClick={handleCreate}
            className="create-btn"
            disabled={loading}
          >
            + 添加角色
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
            placeholder="搜索角色名称、称号等..."
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
          <select
            value={filters.element}
            onChange={(e) => handleFilterChange('element', e.target.value)}
            className="filter-select"
            disabled={loading}
          >
            <option value="">所有元素</option>
            {Object.entries(ELEMENTS).map(([key, value]) => (
              <option key={key} value={value}>{value}</option>
            ))}
          </select>

          <select
            value={filters.weapon_type}
            onChange={(e) => handleFilterChange('weapon_type', e.target.value)}
            className="filter-select"
            disabled={loading}
          >
            <option value="">所有武器类型</option>
            {Object.entries(WEAPON_TYPES).map(([key, value]) => (
              <option key={key} value={value}>{value}</option>
            ))}
          </select>

          <select
            value={filters.rarity}
            onChange={(e) => handleFilterChange('rarity', e.target.value)}
            className="filter-select"
            disabled={loading}
          >
            <option value="">所有稀有度</option>
            <option value="4">4星</option>
            <option value="5">5星</option>
          </select>

          <select
            value={filters.region}
            onChange={(e) => handleFilterChange('region', e.target.value)}
            className="filter-select"
            disabled={loading}
          >
            <option value="">所有地区</option>
            {Object.entries(REGIONS).map(([key, value]) => (
              <option key={key} value={value}>{value}</option>
            ))}
          </select>
        </div>
      </div>

      {/* 角色列表 */}
      <div className="characters-section">
        {loading ? (
          <div className="loading">加载中...</div>
        ) : characters.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">👤</div>
            <h3>暂无角色数据</h3>
            <p>点击"添加角色"按钮创建第一个角色</p>
          </div>
        ) : (
          <>
            {/* 角色表格 */}
            <div className="characters-table">
              <div className="table-header">
                <div className="col-name">角色信息</div>
                <div className="col-element">元素</div>
                <div className="col-weapon">武器类型</div>
                <div className="col-rarity">稀有度</div>
                <div className="col-region">地区</div>
                <div className="col-actions">操作</div>
              </div>

              {characters.map((character) => (
                <div key={character.id} className="table-row">
                  <div className="col-name">
                    <div className="character-name">
                      <strong>{characterUtils.formatCharacterName(character)}</strong>
                      {character.title && <small>{character.title}</small>}
                    </div>
                  </div>
                  <div className="col-element">
                    <span className={`element ${characterUtils.getElementColorClass(character.element)}`}>
                      {character.element}
                    </span>
                  </div>
                  <div className="col-weapon">{character.weapon_type}</div>
                  <div className="col-rarity">
                    <span className={`rarity rarity-${character.rarity}`}>
                      {characterUtils.getRarityStars(character.rarity)}
                    </span>
                  </div>
                  <div className="col-region">{character.region || '-'}</div>
                  <div className="col-actions">
                    <button
                      onClick={() => handleEdit(character)}
                      className="edit-btn"
                      disabled={loading}
                    >
                      编辑
                    </button>
                    <button
                      onClick={() => handleDelete(character)}
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
                第 {currentPage} 页，共 {totalPages} 页 (总共 {totalCharacters} 个角色)
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
              <h2>{formMode === 'create' ? '添加角色' : '编辑角色'}</h2>
              <button onClick={handleCloseForm} className="close-form">×</button>
            </div>

            <form onSubmit={handleSubmit} className="character-form">
              <div className="form-grid">
                {/* 基础信息 */}
                <div className="form-group">
                  <label>角色名称 *</label>
                  <input
                    type="text"
                    name="name"
                    value={formData.name}
                    onChange={handleFormChange}
                    placeholder="输入角色中文名"
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
                    placeholder="输入角色英文名"
                  />
                </div>

                <div className="form-group">
                  <label>元素类型 *</label>
                  <select
                    name="element"
                    value={formData.element}
                    onChange={handleFormChange}
                    required
                  >
                    {Object.entries(ELEMENTS).map(([key, value]) => (
                      <option key={key} value={value}>{value}</option>
                    ))}
                  </select>
                </div>

                <div className="form-group">
                  <label>武器类型 *</label>
                  <select
                    name="weapon_type"
                    value={formData.weapon_type}
                    onChange={handleFormChange}
                    required
                  >
                    {Object.entries(WEAPON_TYPES).map(([key, value]) => (
                      <option key={key} value={value}>{value}</option>
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
                    <option value={4}>4星</option>
                    <option value={5}>5星</option>
                  </select>
                </div>

                <div className="form-group">
                  <label>所属地区</label>
                  <select
                    name="region"
                    value={formData.region}
                    onChange={handleFormChange}
                  >
                    <option value="">请选择地区</option>
                    {Object.entries(REGIONS).map(([key, value]) => (
                      <option key={key} value={value}>{value}</option>
                    ))}
                  </select>
                </div>

                {/* 基础属性 */}
                <div className="form-group">
                  <label>基础生命值 *</label>
                  <input
                    type="number"
                    name="base_stats.hp"
                    value={formData.base_stats.hp}
                    onChange={handleFormChange}
                    min="0"
                    required
                  />
                </div>

                <div className="form-group">
                  <label>基础攻击力 *</label>
                  <input
                    type="number"
                    name="base_stats.atk"
                    value={formData.base_stats.atk}
                    onChange={handleFormChange}
                    min="0"
                    required
                  />
                </div>

                <div className="form-group">
                  <label>基础防御力 *</label>
                  <input
                    type="number"
                    name="base_stats.def_"
                    value={formData.base_stats.def_}
                    onChange={handleFormChange}
                    min="0"
                    required
                  />
                </div>

                {/* 突破属性 */}
                <div className="form-group">
                  <label>突破属性类型</label>
                  <input
                    type="text"
                    name="ascension_stats.stat"
                    value={formData.ascension_stats.stat}
                    onChange={handleFormChange}
                    placeholder="如：暴击率、攻击力等"
                  />
                </div>

                <div className="form-group">
                  <label>突破属性数值</label>
                  <input
                    type="number"
                    name="ascension_stats.value"
                    value={formData.ascension_stats.value}
                    onChange={handleFormChange}
                    step="0.01"
                    min="0"
                  />
                </div>

                {/* 其他信息 */}
                <div className="form-group">
                  <label>角色称号</label>
                  <input
                    type="text"
                    name="title"
                    value={formData.title}
                    onChange={handleFormChange}
                    placeholder="如：蒲公英骑士"
                  />
                </div>

                <div className="form-group">
                  <label>命座名称</label>
                  <input
                    type="text"
                    name="constellation_name"
                    value={formData.constellation_name}
                    onChange={handleFormChange}
                    placeholder="角色命座名称"
                  />
                </div>

                <div className="form-group">
                  <label>所属组织</label>
                  <input
                    type="text"
                    name="affiliation"
                    value={formData.affiliation}
                    onChange={handleFormChange}
                    placeholder="如：西风骑士团"
                  />
                </div>

                <div className="form-group">
                  <label>生日</label>
                  <input
                    type="date"
                    name="birthday"
                    value={formData.birthday}
                    onChange={handleFormChange}
                  />
                </div>

                {/* 角色描述 */}
                <div className="form-group full-width">
                  <label>角色描述</label>
                  <textarea
                    name="description"
                    value={formData.description}
                    onChange={handleFormChange}
                    placeholder="输入角色的详细描述..."
                    rows="4"
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

export default AdminCharactersPage;
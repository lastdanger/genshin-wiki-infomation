/**
 * 角色列表页面
 *
 * 提供完整的角色浏览功能，包括搜索、过滤、排序和分页
 */
import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import characterAPI, { ELEMENTS, WEAPON_TYPES, REGIONS, RARITIES } from '../services/characterAPI';
import CharacterCard, { CharacterCardSkeleton } from '../components/Character/CharacterCard';
import { utils } from '../services/api';
import './CharacterListPage.css';

const CharacterListPage = () => {
  // 路由相关
  const [searchParams, setSearchParams] = useSearchParams();
  const navigate = useNavigate();

  // 数据状态
  const [characters, setCharacters] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [pagination, setPagination] = useState({
    page: 1,
    per_page: 20,
    total: 0,
    total_pages: 0,
    has_next: false,
    has_prev: false
  });

  // 过滤和搜索状态
  const [filters, setFilters] = useState({
    search: '',
    element: '',
    weapon_type: '',
    rarity: '',
    region: '',
    sort_by: 'name',
    sort_order: 'asc'
  });

  // 过滤选项
  const [filterOptions, setFilterOptions] = useState({
    elements: [],
    weapon_types: [],
    regions: [],
    rarities: []
  });

  // 统计信息
  const [stats, setStats] = useState(null);

  // 从URL参数初始化过滤条件
  useEffect(() => {
    const initialFilters = {
      search: searchParams.get('search') || '',
      element: searchParams.get('element') || '',
      weapon_type: searchParams.get('weapon_type') || '',
      rarity: searchParams.get('rarity') || '',
      region: searchParams.get('region') || '',
      sort_by: searchParams.get('sort_by') || 'name',
      sort_order: searchParams.get('sort_order') || 'asc'
    };

    const page = parseInt(searchParams.get('page')) || 1;

    setFilters(initialFilters);
    setPagination(prev => ({ ...prev, page }));
  }, [searchParams]);

  // 防抖搜索函数
  const debouncedSearch = useMemo(
    () => utils.debounce((searchTerm) => {
      updateFilters({ search: searchTerm });
    }, 500),
    []
  );

  // 加载角色列表数据
  const loadCharacters = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      // 构建查询参数
      const params = {
        page: pagination.page,
        per_page: pagination.per_page,
        ...filters
      };

      // 清理空值参数
      const cleanParams = Object.keys(params).reduce((acc, key) => {
        if (params[key] !== '' && params[key] !== null && params[key] !== undefined) {
          acc[key] = params[key];
        }
        return acc;
      }, {});

      console.log('🔍 加载角色列表:', cleanParams);

      const response = await characterAPI.getCharacterList(cleanParams);

      if (response.success) {
        setCharacters(response.data.characters);
        setPagination({
          ...pagination,
          ...response.data.pagination
        });
      } else {
        throw new Error(response.error || '获取角色列表失败');
      }
    } catch (err) {
      console.error('❌ 加载角色列表失败:', err);
      setError(utils.formatError(err));
      setCharacters([]);
    } finally {
      setLoading(false);
    }
  }, [pagination.page, pagination.per_page, filters]);

  // 加载过滤选项
  const loadFilterOptions = useCallback(async () => {
    try {
      const response = await characterAPI.getFilterOptions();
      if (response.success) {
        setFilterOptions(response.data.filters);
      }
    } catch (err) {
      console.warn('获取过滤选项失败:', err);
    }
  }, []);

  // 加载统计信息
  const loadStats = useCallback(async () => {
    try {
      const response = await characterAPI.getCharacterStats();
      if (response.success) {
        setStats(response.data);
      }
    } catch (err) {
      console.warn('获取统计信息失败:', err);
    }
  }, []);

  // 初始化数据加载
  useEffect(() => {
    loadFilterOptions();
    loadStats();
  }, [loadFilterOptions, loadStats]);

  // 加载角色数据
  useEffect(() => {
    loadCharacters();
  }, [loadCharacters]);

  // 更新过滤条件和URL参数
  const updateFilters = useCallback((newFilters) => {
    const updatedFilters = { ...filters, ...newFilters };
    setFilters(updatedFilters);

    // 重置到第一页
    setPagination(prev => ({ ...prev, page: 1 }));

    // 更新URL参数
    const params = new URLSearchParams();
    Object.keys(updatedFilters).forEach(key => {
      if (updatedFilters[key]) {
        params.set(key, updatedFilters[key]);
      }
    });
    params.set('page', '1');

    setSearchParams(params);
  }, [filters, setSearchParams]);

  // 页码变更
  const handlePageChange = useCallback((page) => {
    setPagination(prev => ({ ...prev, page }));

    const params = new URLSearchParams(searchParams);
    params.set('page', page.toString());
    setSearchParams(params);
  }, [searchParams, setSearchParams]);

  // 清除所有过滤条件
  const clearFilters = useCallback(() => {
    setFilters({
      search: '',
      element: '',
      weapon_type: '',
      rarity: '',
      region: '',
      sort_by: 'name',
      sort_order: 'asc'
    });
    setSearchParams({});
  }, [setSearchParams]);

  // 处理角色卡片点击
  const handleCharacterClick = useCallback((character) => {
    navigate(`/characters/${character.id}`);
  }, [navigate]);

  // 渲染加载状态
  if (loading && characters.length === 0) {
    return (
      <div className="character-list-page">
        <div className="character-list-page__header">
          <h1>角色信息</h1>
          <div className="character-list-page__loading">
            <span>正在加载角色数据...</span>
          </div>
        </div>

        <div className="character-list-page__content">
          <div className="character-grid">
            {Array(12).fill(0).map((_, index) => (
              <CharacterCardSkeleton key={index} />
            ))}
          </div>
        </div>
      </div>
    );
  }

  // 渲染错误状态
  if (error && characters.length === 0) {
    return (
      <div className="character-list-page">
        <div className="character-list-page__header">
          <h1>角色信息</h1>
        </div>

        <div className="character-list-page__error">
          <div className="error-message">
            <h3>😕 加载失败</h3>
            <p>{error}</p>
            <button
              className="btn btn-primary"
              onClick={() => window.location.reload()}
            >
              重新加载
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="character-list-page">
      {/* 页面头部 */}
      <div className="character-list-page__header">
        <div className="header-content">
          <h1>角色信息</h1>
          <p className="page-description">
            浏览原神中的所有角色，了解他们的基本属性、技能和背景信息
          </p>

          {/* 统计信息 */}
          {stats && (
            <div className="stats-summary">
              <div className="stat-item">
                <span className="stat-number">{stats.total_characters}</span>
                <span className="stat-label">个角色</span>
              </div>
              <div className="stat-divider">|</div>
              <div className="stat-item">
                <span className="stat-number">{Object.keys(stats.by_element || {}).length}</span>
                <span className="stat-label">种元素</span>
              </div>
              <div className="stat-divider">|</div>
              <div className="stat-item">
                <span className="stat-number">{Object.keys(stats.by_weapon_type || {}).length}</span>
                <span className="stat-label">种武器</span>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* 搜索和过滤区域 */}
      <div className="character-list-page__filters">
        <div className="filters-container">
          {/* 搜索框 */}
          <div className="filter-group filter-group--search">
            <label htmlFor="character-search">搜索角色</label>
            <input
              id="character-search"
              type="text"
              placeholder="输入角色名称、称号或描述..."
              value={filters.search}
              onChange={(e) => debouncedSearch(e.target.value)}
              className="search-input"
            />
          </div>

          {/* 过滤选项 */}
          <div className="filter-group">
            <label htmlFor="element-filter">元素类型</label>
            <select
              id="element-filter"
              value={filters.element}
              onChange={(e) => updateFilters({ element: e.target.value })}
              className="filter-select"
            >
              <option value="">全部元素</option>
              {Object.values(ELEMENTS).map(element => (
                <option key={element} value={element}>
                  {getElementName(element)}
                </option>
              ))}
            </select>
          </div>

          <div className="filter-group">
            <label htmlFor="weapon-filter">武器类型</label>
            <select
              id="weapon-filter"
              value={filters.weapon_type}
              onChange={(e) => updateFilters({ weapon_type: e.target.value })}
              className="filter-select"
            >
              <option value="">全部武器</option>
              {Object.values(WEAPON_TYPES).map(weaponType => (
                <option key={weaponType} value={weaponType}>
                  {getWeaponTypeName(weaponType)}
                </option>
              ))}
            </select>
          </div>

          <div className="filter-group">
            <label htmlFor="rarity-filter">稀有度</label>
            <select
              id="rarity-filter"
              value={filters.rarity}
              onChange={(e) => updateFilters({ rarity: e.target.value })}
              className="filter-select"
            >
              <option value="">全部星级</option>
              <option value="4">4星角色</option>
              <option value="5">5星角色</option>
            </select>
          </div>

          <div className="filter-group">
            <label htmlFor="region-filter">地区</label>
            <select
              id="region-filter"
              value={filters.region}
              onChange={(e) => updateFilters({ region: e.target.value })}
              className="filter-select"
            >
              <option value="">全部地区</option>
              {Object.keys(REGIONS).map(region => (
                <option key={region} value={REGIONS[region]}>
                  {getRegionName(REGIONS[region])}
                </option>
              ))}
            </select>
          </div>

          {/* 排序选项 */}
          <div className="filter-group">
            <label htmlFor="sort-filter">排序方式</label>
            <select
              id="sort-filter"
              value={`${filters.sort_by}-${filters.sort_order}`}
              onChange={(e) => {
                const [sort_by, sort_order] = e.target.value.split('-');
                updateFilters({ sort_by, sort_order });
              }}
              className="filter-select"
            >
              <option value="name-asc">名称 A-Z</option>
              <option value="name-desc">名称 Z-A</option>
              <option value="rarity-desc">稀有度从高到低</option>
              <option value="rarity-asc">稀有度从低到高</option>
              <option value="element-asc">元素类型</option>
              <option value="created_at-desc">最新添加</option>
            </select>
          </div>

          {/* 清除过滤条件 */}
          <div className="filter-group filter-group--actions">
            <button
              onClick={clearFilters}
              className="btn btn-secondary btn-clear"
              disabled={!Object.values(filters).some(value => value && value !== 'name' && value !== 'asc')}
            >
              清除筛选
            </button>
          </div>
        </div>
      </div>

      {/* 结果信息 */}
      <div className="character-list-page__results-info">
        <div className="results-meta">
          <span className="results-count">
            找到 <strong>{pagination.total}</strong> 个角色
          </span>
          {filters.search && (
            <span className="search-query">
              搜索 "<strong>{filters.search}</strong>"
            </span>
          )}
        </div>
      </div>

      {/* 角色列表 */}
      <div className="character-list-page__content">
        {characters.length > 0 ? (
          <>
            <div className="character-grid">
              {characters.map((character) => (
                <CharacterCard
                  key={character.id}
                  character={character}
                  onClick={handleCharacterClick}
                />
              ))}
            </div>

            {/* 分页 */}
            {pagination.total_pages > 1 && (
              <div className="pagination-container">
                <div className="pagination">
                  <button
                    onClick={() => handlePageChange(pagination.page - 1)}
                    disabled={!pagination.has_prev || loading}
                    className="pagination-btn pagination-btn--prev"
                  >
                    ← 上一页
                  </button>

                  <div className="pagination-info">
                    第 {pagination.page} / {pagination.total_pages} 页
                  </div>

                  <button
                    onClick={() => handlePageChange(pagination.page + 1)}
                    disabled={!pagination.has_next || loading}
                    className="pagination-btn pagination-btn--next"
                  >
                    下一页 →
                  </button>
                </div>
              </div>
            )}
          </>
        ) : (
          <div className="empty-state">
            <div className="empty-state-content">
              <h3>🔍 没有找到匹配的角色</h3>
              <p>尝试调整筛选条件或搜索关键词</p>
              <button onClick={clearFilters} className="btn btn-primary">
                清除所有筛选条件
              </button>
            </div>
          </div>
        )}
      </div>

      {/* 加载更多指示器 */}
      {loading && characters.length > 0 && (
        <div className="loading-indicator">
          <span>正在加载...</span>
        </div>
      )}
    </div>
  );
};

// 辅助函数
const getElementName = (element) => {
  const elementNames = {
    [ELEMENTS.PYRO]: '火',
    [ELEMENTS.HYDRO]: '水',
    [ELEMENTS.ANEMO]: '风',
    [ELEMENTS.ELECTRO]: '雷',
    [ELEMENTS.DENDRO]: '草',
    [ELEMENTS.CRYO]: '冰',
    [ELEMENTS.GEO]: '岩'
  };
  return elementNames[element] || element;
};

const getWeaponTypeName = (weaponType) => {
  const weaponNames = {
    [WEAPON_TYPES.SWORD]: '单手剑',
    [WEAPON_TYPES.CLAYMORE]: '双手剑',
    [WEAPON_TYPES.POLEARM]: '长柄武器',
    [WEAPON_TYPES.BOW]: '弓',
    [WEAPON_TYPES.CATALYST]: '法器'
  };
  return weaponNames[weaponType] || weaponType;
};

const getRegionName = (region) => {
  const regionNames = {
    'Mondstadt': '蒙德',
    'Liyue': '璃月',
    'Inazuma': '稻妻',
    'Sumeru': '须弥',
    'Fontaine': '枫丹',
    'Natlan': '纳塔',
    'Snezhnaya': '至冬'
  };
  return regionNames[region] || region;
};

export default CharacterListPage;
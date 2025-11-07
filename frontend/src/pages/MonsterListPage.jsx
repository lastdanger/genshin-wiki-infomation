/**
 * 怪物列表页面
 *
 * 提供完整的怪物浏览功能，包括搜索、过滤、排序和分页
 */
import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import monsterAPI from '../services/monsterAPI';
import MonsterCard, { MonsterCardSkeleton } from '../components/Monster/MonsterCard';
import { utils } from '../services/api';
import './MonsterListPage.css';

const MonsterListPage = () => {
  // 路由相关
  const [searchParams, setSearchParams] = useSearchParams();
  const navigate = useNavigate();

  // 数据状态
  const [monsters, setMonsters] = useState([]);
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
    category: '',
    family: '',
    element: '',
    level: '',
    world_level: '',
    region: '',
    sort_by: 'name',
    sort_order: 'asc'
  });

  // 统计信息
  const [stats, setStats] = useState(null);

  // 从URL参数初始化过滤条件
  useEffect(() => {
    const initialFilters = {
      search: searchParams.get('search') || '',
      category: searchParams.get('category') || '',
      family: searchParams.get('family') || '',
      element: searchParams.get('element') || '',
      level: searchParams.get('level') || '',
      world_level: searchParams.get('world_level') || '',
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

  // 加载怪物列表数据
  const loadMonsters = useCallback(async () => {
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

      console.log('🔍 加载怪物列表:', cleanParams);

      const response = await monsterAPI.getMonsterList(cleanParams);

      if (response.success) {
        setMonsters(response.data.monsters || response.data);
        setPagination({
          ...pagination,
          ...response.data
        });
      } else {
        throw new Error(response.error || '获取怪物列表失败');
      }
    } catch (err) {
      console.error('❌ 加载怪物列表失败:', err);
      setError(utils.formatError(err));
      setMonsters([]);
    } finally {
      setLoading(false);
    }
  }, [pagination.page, pagination.per_page, filters]);

  // 加载统计信息
  const loadStats = useCallback(async () => {
    try {
      const response = await monsterAPI.getMonsterStats();
      if (response.success) {
        setStats(response.data);
      }
    } catch (err) {
      console.warn('获取统计信息失败:', err);
    }
  }, []);

  // 初始化数据加载
  useEffect(() => {
    loadStats();
  }, [loadStats]);

  // 加载怪物数据
  useEffect(() => {
    loadMonsters();
  }, [loadMonsters]);

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
      category: '',
      family: '',
      element: '',
      level: '',
      world_level: '',
      region: '',
      sort_by: 'name',
      sort_order: 'asc'
    });
    setSearchParams({});
  }, [setSearchParams]);

  // 处理怪物卡片点击
  const handleMonsterClick = useCallback((monster) => {
    navigate(`/monsters/${monster.id}`);
  }, [navigate]);

  // 渲染加载状态
  if (loading && monsters.length === 0) {
    return (
      <div className="monster-list-page">
        <div className="monster-list-page__header">
          <h1>怪物信息</h1>
          <div className="monster-list-page__loading">
            <span>正在加载怪物数据...</span>
          </div>
        </div>

        <div className="monster-list-page__content">
          <div className="monster-grid">
            {Array(12).fill(0).map((_, index) => (
              <MonsterCardSkeleton key={index} />
            ))}
          </div>
        </div>
      </div>
    );
  }

  // 渲染错误状态
  if (error && monsters.length === 0) {
    return (
      <div className="monster-list-page">
        <div className="monster-list-page__header">
          <h1>怪物信息</h1>
        </div>

        <div className="monster-list-page__error">
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
    <div className="monster-list-page">
      {/* 页面头部 */}
      <div className="monster-list-page__header">
        <div className="header-content">
          <h1>怪物信息</h1>
          <p className="page-description">
            浏览原神中的所有怪物，了解它们的属性、技能和掉落物品
          </p>

          {/* 统计信息 */}
          {stats && (
            <div className="stats-summary">
              <div className="stat-item">
                <span className="stat-number">{stats.total_monsters}</span>
                <span className="stat-label">个怪物</span>
              </div>
              <div className="stat-divider">|</div>
              <div className="stat-item">
                <span className="stat-number">{Object.keys(stats.by_category || {}).length}</span>
                <span className="stat-label">个类别</span>
              </div>
              <div className="stat-divider">|</div>
              <div className="stat-item">
                <span className="stat-number">{Object.keys(stats.by_family || {}).length}</span>
                <span className="stat-label">个族群</span>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* 搜索和过滤区域 */}
      <div className="monster-list-page__filters">
        <div className="filters-container">
          {/* 搜索框 */}
          <div className="filter-group filter-group--search">
            <label htmlFor="monster-search">搜索怪物</label>
            <input
              id="monster-search"
              type="text"
              placeholder="输入怪物名称、族群或描述..."
              value={filters.search}
              onChange={(e) => debouncedSearch(e.target.value)}
              className="search-input"
            />
          </div>

          {/* 过滤选项 */}
          <div className="filter-group">
            <label htmlFor="category-filter">类别</label>
            <select
              id="category-filter"
              value={filters.category}
              onChange={(e) => updateFilters({ category: e.target.value })}
              className="filter-select"
            >
              <option value="">全部类别</option>
              <option value="普通怪物">普通怪物</option>
              <option value="精英怪物">精英怪物</option>
              <option value="周本Boss">周本Boss</option>
              <option value="世界Boss">世界Boss</option>
            </select>
          </div>

          <div className="filter-group">
            <label htmlFor="family-filter">族群</label>
            <select
              id="family-filter"
              value={filters.family}
              onChange={(e) => updateFilters({ family: e.target.value })}
              className="filter-select"
            >
              <option value="">全部族群</option>
              <option value="丘丘人">丘丘人</option>
              <option value="史莱姆">史莱姆</option>
              <option value="无相">无相</option>
              <option value="愚人众">愚人众</option>
              <option value="深渊法师">深渊法师</option>
              <option value="遗迹守卫">遗迹守卫</option>
            </select>
          </div>

          <div className="filter-group">
            <label htmlFor="element-filter">元素</label>
            <select
              id="element-filter"
              value={filters.element}
              onChange={(e) => updateFilters({ element: e.target.value })}
              className="filter-select"
            >
              <option value="">全部元素</option>
              <option value="Pyro">火元素</option>
              <option value="Hydro">水元素</option>
              <option value="Anemo">风元素</option>
              <option value="Electro">雷元素</option>
              <option value="Dendro">草元素</option>
              <option value="Cryo">冰元素</option>
              <option value="Geo">岩元素</option>
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
              <option value="蒙德">蒙德</option>
              <option value="璃月">璃月</option>
              <option value="稻妻">稻妻</option>
              <option value="须弥">须弥</option>
              <option value="枫丹">枫丹</option>
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
              <option value="category-asc">类别排序</option>
              <option value="level-desc">等级从高到低</option>
              <option value="level-asc">等级从低到高</option>
              <option value="hp-desc">血量从高到低</option>
              <option value="attack-desc">攻击力从高到低</option>
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
      <div className="monster-list-page__results-info">
        <div className="results-meta">
          <span className="results-count">
            找到 <strong>{pagination.total}</strong> 个怪物
          </span>
          {filters.search && (
            <span className="search-query">
              搜索 "<strong>{filters.search}</strong>"
            </span>
          )}
        </div>
      </div>

      {/* 怪物列表 */}
      <div className="monster-list-page__content">
        {monsters.length > 0 ? (
          <>
            <div className="monster-grid">
              {monsters.map((monster) => (
                <MonsterCard
                  key={monster.id}
                  monster={monster}
                  onClick={handleMonsterClick}
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
              <h3>🔍 没有找到匹配的怪物</h3>
              <p>尝试调整筛选条件或搜索关键词</p>
              <button onClick={clearFilters} className="btn btn-primary">
                清除所有筛选条件
              </button>
            </div>
          </div>
        )}
      </div>

      {/* 加载更多指示器 */}
      {loading && monsters.length > 0 && (
        <div className="loading-indicator">
          <span>正在加载...</span>
        </div>
      )}
    </div>
  );
};

export default MonsterListPage;

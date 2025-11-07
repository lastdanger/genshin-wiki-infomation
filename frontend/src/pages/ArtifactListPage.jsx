/**
 * 圣遗物列表页面
 *
 * 提供完整的圣遗物浏览功能，包括搜索、过滤、排序和分页
 */
import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import artifactAPI, { ARTIFACT_SLOTS, MAIN_STAT_TYPES, SOURCES, RARITIES } from '../services/artifactAPI';
import ArtifactCard, { ArtifactCardSkeleton } from '../components/Artifact/ArtifactCard';
import { utils } from '../services/api';
import './ArtifactListPage.css';

const ArtifactListPage = () => {
  // 路由相关
  const [searchParams, setSearchParams] = useSearchParams();
  const navigate = useNavigate();

  // 数据状态
  const [artifacts, setArtifacts] = useState([]);
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
    set_name: '',
    slot: '',
    rarity: '',
    source: '',
    main_stat_type: '',
    sort_by: 'name',
    sort_order: 'asc'
  });

  // 统计信息
  const [stats, setStats] = useState(null);

  // 从URL参数初始化过滤条件
  useEffect(() => {
    const initialFilters = {
      search: searchParams.get('search') || '',
      set_name: searchParams.get('set_name') || '',
      slot: searchParams.get('slot') || '',
      rarity: searchParams.get('rarity') || '',
      source: searchParams.get('source') || '',
      main_stat_type: searchParams.get('main_stat_type') || '',
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

  // 加载圣遗物列表数据
  const loadArtifacts = useCallback(async () => {
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

      console.log('🔍 加载圣遗物列表:', cleanParams);

      const response = await artifactAPI.getArtifactList(cleanParams);

      if (response.success) {
        setArtifacts(response.data.artifacts);
        setPagination({
          ...pagination,
          ...response.data
        });
      } else {
        throw new Error(response.error || '获取圣遗物列表失败');
      }
    } catch (err) {
      console.error('❌ 加载圣遗物列表失败:', err);
      setError(utils.formatError(err));
      setArtifacts([]);
    } finally {
      setLoading(false);
    }
  }, [pagination.page, pagination.per_page, filters]);

  // 加载统计信息
  const loadStats = useCallback(async () => {
    try {
      const response = await artifactAPI.getArtifactStats();
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

  // 加载圣遗物数据
  useEffect(() => {
    loadArtifacts();
  }, [loadArtifacts]);

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
      set_name: '',
      slot: '',
      rarity: '',
      source: '',
      main_stat_type: '',
      sort_by: 'name',
      sort_order: 'asc'
    });
    setSearchParams({});
  }, [setSearchParams]);

  // 处理圣遗物卡片点击
  const handleArtifactClick = useCallback((artifact) => {
    navigate(`/artifacts/${artifact.id}`);
  }, [navigate]);

  // 渲染加载状态
  if (loading && artifacts.length === 0) {
    return (
      <div className="artifact-list-page">
        <div className="artifact-list-page__header">
          <h1>圣遗物信息</h1>
          <div className="artifact-list-page__loading">
            <span>正在加载圣遗物数据...</span>
          </div>
        </div>

        <div className="artifact-list-page__content">
          <div className="artifact-grid">
            {Array(12).fill(0).map((_, index) => (
              <ArtifactCardSkeleton key={index} />
            ))}
          </div>
        </div>
      </div>
    );
  }

  // 渲染错误状态
  if (error && artifacts.length === 0) {
    return (
      <div className="artifact-list-page">
        <div className="artifact-list-page__header">
          <h1>圣遗物信息</h1>
        </div>

        <div className="artifact-list-page__error">
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
    <div className="artifact-list-page">
      {/* 页面头部 */}
      <div className="artifact-list-page__header">
        <div className="header-content">
          <h1>圣遗物信息</h1>
          <p className="page-description">
            浏览原神中的所有圣遗物，了解套装效果、属性加成和获取方式
          </p>

          {/* 统计信息 */}
          {stats && (
            <div className="stats-summary">
              <div className="stat-item">
                <span className="stat-number">{stats.total_artifacts}</span>
                <span className="stat-label">个圣遗物</span>
              </div>
              <div className="stat-divider">|</div>
              <div className="stat-item">
                <span className="stat-number">{Object.keys(stats.by_set || {}).length}</span>
                <span className="stat-label">个套装</span>
              </div>
              <div className="stat-divider">|</div>
              <div className="stat-item">
                <span className="stat-number">{Object.keys(stats.by_slot || {}).length}</span>
                <span className="stat-label">个部位</span>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* 搜索和过滤区域 */}
      <div className="artifact-list-page__filters">
        <div className="filters-container">
          {/* 搜索框 */}
          <div className="filter-group filter-group--search">
            <label htmlFor="artifact-search">搜索圣遗物</label>
            <input
              id="artifact-search"
              type="text"
              placeholder="输入圣遗物名称、套装名称或描述..."
              value={filters.search}
              onChange={(e) => debouncedSearch(e.target.value)}
              className="search-input"
            />
          </div>

          {/* 过滤选项 */}
          <div className="filter-group">
            <label htmlFor="set-filter">套装名称</label>
            <select
              id="set-filter"
              value={filters.set_name}
              onChange={(e) => updateFilters({ set_name: e.target.value })}
              className="filter-select"
            >
              <option value="">全部套装</option>
              <option value="绝缘之旗印">绝缘之旗印</option>
              <option value="华馆梦醒">华馆梦醒</option>
              <option value="千岩牢固">千岩牢固</option>
            </select>
          </div>

          <div className="filter-group">
            <label htmlFor="slot-filter">部位</label>
            <select
              id="slot-filter"
              value={filters.slot}
              onChange={(e) => updateFilters({ slot: e.target.value })}
              className="filter-select"
            >
              <option value="">全部部位</option>
              {Object.values(ARTIFACT_SLOTS).map(slot => (
                <option key={slot} value={slot}>
                  {getSlotName(slot)}
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
              {RARITIES.map(rarity => (
                <option key={rarity} value={rarity}>
                  {rarity}星圣遗物
                </option>
              ))}
            </select>
          </div>

          <div className="filter-group">
            <label htmlFor="source-filter">获取方式</label>
            <select
              id="source-filter"
              value={filters.source}
              onChange={(e) => updateFilters({ source: e.target.value })}
              className="filter-select"
            >
              <option value="">全部方式</option>
              {Object.values(SOURCES).map(source => (
                <option key={source} value={source}>
                  {source}
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
              <option value="set_name-asc">套装名称</option>
              <option value="rarity-desc">稀有度从高到低</option>
              <option value="rarity-asc">稀有度从低到高</option>
              <option value="slot-asc">部位顺序</option>
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
      <div className="artifact-list-page__results-info">
        <div className="results-meta">
          <span className="results-count">
            找到 <strong>{pagination.total}</strong> 个圣遗物
          </span>
          {filters.search && (
            <span className="search-query">
              搜索 "<strong>{filters.search}</strong>"
            </span>
          )}
        </div>
      </div>

      {/* 圣遗物列表 */}
      <div className="artifact-list-page__content">
        {artifacts.length > 0 ? (
          <>
            <div className="artifact-grid">
              {artifacts.map((artifact) => (
                <ArtifactCard
                  key={artifact.id}
                  artifact={artifact}
                  onClick={handleArtifactClick}
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
              <h3>🔍 没有找到匹配的圣遗物</h3>
              <p>尝试调整筛选条件或搜索关键词</p>
              <button onClick={clearFilters} className="btn btn-primary">
                清除所有筛选条件
              </button>
            </div>
          </div>
        )}
      </div>

      {/* 加载更多指示器 */}
      {loading && artifacts.length > 0 && (
        <div className="loading-indicator">
          <span>正在加载...</span>
        </div>
      )}
    </div>
  );
};

// 辅助函数
const getSlotName = (slot) => {
  const slotNames = {
    [ARTIFACT_SLOTS.FLOWER]: '生之花',
    [ARTIFACT_SLOTS.PLUME]: '死之羽',
    [ARTIFACT_SLOTS.SANDS]: '时之沙',
    [ARTIFACT_SLOTS.GOBLET]: '空之杯',
    [ARTIFACT_SLOTS.CIRCLET]: '理之冠'
  };
  return slotNames[slot] || slot;
};

export default ArtifactListPage;

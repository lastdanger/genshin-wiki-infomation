/**
 * 武器列表页面
 *
 * 显示武器列表，支持搜索、筛选、排序和分页功能
 */
import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import WeaponCard, { WeaponCardSkeleton } from '../components/Weapon/WeaponCard';
import weaponAPI from '../services/weaponAPI';
import { debounce } from 'lodash';
import './WeaponListPage.css';

const WeaponListPage = () => {
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();

  // 状态管理
  const [weapons, setWeapons] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [totalWeapons, setTotalWeapons] = useState(0);
  const [totalPages, setTotalPages] = useState(0);

  // 过滤选项
  const [filterOptions, setFilterOptions] = useState({
    weapon_types: [],
    sources: [],
    rarities: []
  });

  // 从URL参数初始化筛选条件
  const [filters, setFilters] = useState({
    search: searchParams.get('search') || '',
    weapon_type: searchParams.get('weapon_type') || '',
    rarity: searchParams.get('rarity') ? parseInt(searchParams.get('rarity')) : null,
    source: searchParams.get('source') || '',
    sort_by: searchParams.get('sort_by') || 'name',
    sort_order: searchParams.get('sort_order') || 'asc',
    page: parseInt(searchParams.get('page')) || 1,
    per_page: parseInt(searchParams.get('per_page')) || 20
  });

  // 统计信息
  const [stats, setStats] = useState(null);

  // 防抖搜索
  const debouncedSearch = useCallback(
    debounce((searchTerm) => {
      setFilters(prev => ({
        ...prev,
        search: searchTerm,
        page: 1
      }));
    }, 500),
    []
  );

  // 获取武器列表
  const fetchWeapons = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await weaponAPI.getWeaponList(filters);

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
  }, [filters]);

  // 获取过滤选项
  const fetchFilterOptions = useCallback(async () => {
    try {
      const response = await weaponAPI.getWeaponFilters();
      if (response.success) {
        setFilterOptions(response.data);
      }
    } catch (err) {
      console.error('获取过滤选项失败:', err);
    }
  }, []);

  // 获取统计信息
  const fetchStats = useCallback(async () => {
    try {
      const statsResponse = await weaponAPI.getWeaponStats();
      setStats(statsResponse);
    } catch (err) {
      console.error('获取武器统计失败:', err);
    }
  }, []);

  // 更新URL参数
  const updateURL = useCallback((newFilters) => {
    const params = new URLSearchParams();
    Object.entries(newFilters).forEach(([key, value]) => {
      if (value !== null && value !== undefined && value !== '') {
        params.set(key, value.toString());
      }
    });
    setSearchParams(params);
  }, [setSearchParams]);

  // 处理筛选条件变化
  const handleFilterChange = (key, value) => {
    const newFilters = {
      ...filters,
      [key]: value,
      page: key === 'page' ? value : 1
    };
    setFilters(newFilters);
    updateURL(newFilters);
  };

  // 处理搜索
  const handleSearch = (searchTerm) => {
    debouncedSearch(searchTerm);
  };

  // 处理武器卡片点击
  const handleWeaponClick = (weapon) => {
    navigate(`/weapons/${weapon.id}`);
  };

  // 重置筛选条件
  const resetFilters = () => {
    const defaultFilters = {
      search: '',
      weapon_type: '',
      rarity: null,
      source: '',
      sort_by: 'name',
      sort_order: 'asc',
      page: 1,
      per_page: 20
    };
    setFilters(defaultFilters);
    updateURL(defaultFilters);
  };

  // 初始化和数据获取
  useEffect(() => {
    fetchWeapons();
  }, [fetchWeapons]);

  useEffect(() => {
    fetchFilterOptions();
    fetchStats();
  }, [fetchFilterOptions, fetchStats]);

  // 渲染加载状态
  if (loading && weapons.length === 0) {
    return (
      <div className="weapon-list-page">
        <div className="container">
          <header className="weapon-list-page__header">
            <h1>武器图鉴</h1>
            <p>加载中...</p>
          </header>
          <div className="weapon-list-page__grid">
            {Array(8).fill(0).map((_, index) => (
              <WeaponCardSkeleton key={index} />
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="weapon-list-page">
        {/* 页面头部 */}
        <header className="weapon-list-header">
          <div className="weapon-list-title">
            <h1>武器图鉴</h1>
            <p className="weapon-list-subtitle">
              共 {totalWeapons} 把武器
              {stats && (
                <span className="weapon-list-stats">
                  （五星：{stats.by_rarity?.['5'] || 0} 把，四星：{stats.by_rarity?.['4'] || 0} 把，三星：{stats.by_rarity?.['3'] || 0} 把）
                </span>
              )}
            </p>
          </div>

          {/* 搜索框 */}
          <div className="weapon-list-search">
            <input
              type="text"
              placeholder="搜索武器名称、被动技能..."
              value={filters.search}
              onChange={(e) => {
                setFilters(prev => ({ ...prev, search: e.target.value }));
                handleSearch(e.target.value);
              }}
              className="weapon-list-search-input"
            />
            <span className="weapon-list-page__search-icon">🔍</span>
          </div>
        </header>

        {/* 筛选条件 */}
        <div className="weapon-list-page__filters">
          <div className="weapon-list-page__filter-row">
            {/* 武器类型筛选 */}
            <select
              value={filters.weapon_type}
              onChange={(e) => handleFilterChange('weapon_type', e.target.value)}
              className="weapon-list-page__filter-select"
            >
              <option value="">全部武器类型</option>
              {filterOptions.weapon_types.map(type => (
                <option key={type} value={type}>
                  {weaponAPI.getWeaponTypeDisplay(type)}
                </option>
              ))}
            </select>

            {/* 稀有度筛选 */}
            <select
              value={filters.rarity || ''}
              onChange={(e) => handleFilterChange('rarity', e.target.value ? parseInt(e.target.value) : null)}
              className="weapon-list-page__filter-select"
            >
              <option value="">全部稀有度</option>
              {filterOptions.rarities.map(rarity => (
                <option key={rarity} value={rarity}>
                  {weaponAPI.getRarityDisplay(rarity)} {rarity}星
                </option>
              ))}
            </select>

            {/* 获取方式筛选 */}
            <select
              value={filters.source}
              onChange={(e) => handleFilterChange('source', e.target.value)}
              className="weapon-list-page__filter-select"
            >
              <option value="">全部获取方式</option>
              {filterOptions.sources.map(source => (
                <option key={source} value={source}>
                  {source}
                </option>
              ))}
            </select>

            {/* 排序方式 */}
            <select
              value={`${filters.sort_by}-${filters.sort_order}`}
              onChange={(e) => {
                const [sortBy, sortOrder] = e.target.value.split('-');
                handleFilterChange('sort_by', sortBy);
                handleFilterChange('sort_order', sortOrder);
              }}
              className="weapon-list-page__filter-select"
            >
              <option value="name-asc">名称升序</option>
              <option value="name-desc">名称降序</option>
              <option value="rarity-desc">稀有度降序</option>
              <option value="rarity-asc">稀有度升序</option>
              <option value="base_attack-desc">攻击力降序</option>
              <option value="base_attack-asc">攻击力升序</option>
              <option value="weapon_type-asc">类型升序</option>
              <option value="created_at-desc">添加时间降序</option>
            </select>

            {/* 重置按钮 */}
            <button
              onClick={resetFilters}
              className="weapon-list-page__reset-btn"
              disabled={Object.values(filters).every(val => !val || val === 'name' || val === 'asc' || val === 1 || val === 20)}
            >
              重置
            </button>
          </div>

          {/* 每页显示数量 */}
          <div className="weapon-list-page__per-page">
            <label>
              每页显示：
              <select
                value={filters.per_page}
                onChange={(e) => handleFilterChange('per_page', parseInt(e.target.value))}
                className="weapon-list-page__per-page-select"
              >
                <option value={12}>12</option>
                <option value={20}>20</option>
                <option value={50}>50</option>
                <option value={100}>100</option>
              </select>
            </label>
          </div>
        </div>

        {/* 错误提示 */}
        {error && (
          <div className="weapon-list-page__error">
            <p>⚠️ {error}</p>
            <button onClick={fetchWeapons} className="weapon-list-page__retry-btn">
              重试
            </button>
          </div>
        )}

        {/* 武器网格 */}
        {!error && (
          <div className="weapon-list-page__content">
            {weapons.length > 0 ? (
              <>
                <div className="weapon-list-page__grid">
                  {weapons.map((weapon) => (
                    <WeaponCard
                      key={weapon.id}
                      weapon={weapon}
                      onClick={handleWeaponClick}
                      className={loading ? 'weapon-card--loading' : ''}
                    />
                  ))}
                </div>

                {/* 分页控件 */}
                {totalPages > 1 && (
                  <div className="weapon-list-page__pagination">
                    <button
                      onClick={() => handleFilterChange('page', Math.max(1, filters.page - 1))}
                      disabled={filters.page === 1}
                      className="weapon-list-page__page-btn"
                    >
                      上一页
                    </button>

                    <div className="weapon-list-page__page-info">
                      <span>第 {filters.page} 页，共 {totalPages} 页</span>
                    </div>

                    <button
                      onClick={() => handleFilterChange('page', Math.min(totalPages, filters.page + 1))}
                      disabled={filters.page === totalPages}
                      className="weapon-list-page__page-btn"
                    >
                      下一页
                    </button>
                  </div>
                )}
              </>
            ) : (
              <div className="weapon-list-page__empty">
                <div className="weapon-list-page__empty-icon">🔍</div>
                <h3>暂无武器数据</h3>
                <p>请尝试调整筛选条件或稍后重试</p>
                <button onClick={resetFilters} className="weapon-list-page__reset-btn">
                  重置筛选条件
                </button>
              </div>
            )}
          </div>
        )}

        {/* 加载更多指示器 */}
        {loading && weapons.length > 0 && (
          <div className="weapon-list-page__loading">
            <p>加载中...</p>
          </div>
        )}
    </div>
  );
};

export default WeaponListPage;
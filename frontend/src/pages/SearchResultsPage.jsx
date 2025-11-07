/**
 * 搜索结果页面组件
 */
import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import searchAPI from '../services/searchAPI';
import { getUserMessage } from '../services/errors';
import CharacterCard from '../components/Character/CharacterCard';
import LoadingSpinner from '../components/UI/LoadingSpinner';
import { ErrorMessage } from '../components/ErrorBoundary';
import './SearchResultsPage.css';

const SearchResultsPage = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [results, setResults] = useState({
    characters: [],
    weapons: [],
    artifacts: [],
    monsters: []
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const query = searchParams.get('q') || '';

  useEffect(() => {
    const performSearch = async () => {
      if (!query.trim()) {
        setResults({
          characters: [],
          weapons: [],
          artifacts: [],
          monsters: []
        });
        setLoading(false);
        return;
      }

      setLoading(true);
      setError(null);

      try {
        // 使用新的全局搜索 API
        const searchResults = await searchAPI.globalSearch(query.trim());
        setResults(searchResults);

        // 保存搜索历史
        await searchAPI.saveSearchHistory(query.trim());
      } catch (err) {
        console.error('搜索失败:', err);
        setError(getUserMessage(err));
      } finally {
        setLoading(false);
      }
    };

    performSearch();
  }, [query]);

  const handleCharacterClick = (character) => {
    navigate(`/characters/${character.id}`);
  };

  const getTotalResults = () => {
    return (
      (results.characters?.length || 0) +
      (results.weapons?.length || 0) +
      (results.artifacts?.length || 0) +
      (results.monsters?.length || 0)
    );
  };

  const hasResults = getTotalResults() > 0;

  const retrySearch = () => {
    window.location.reload();
  };

  if (loading) {
    return (
      <div className="search-results-page">
        <div className="container">
          <div className="search-header">
            <h1>搜索中...</h1>
          </div>
          <LoadingSpinner />
        </div>
      </div>
    );
  }

  return (
    <div className="search-results-page">
      <div className="container">
        <div className="search-header">
          <h1>
            搜索结果
            {query && (
              <span className="search-query">
                关于 "<span className="query-text">{query}</span>"
              </span>
            )}
          </h1>
          <div className="search-info">
            {error ? (
              <ErrorMessage
                message={error}
                type="error"
                onRetry={retrySearch}
              />
            ) : (
              <div className="results-count">
                找到 <span className="count-number">{getTotalResults()}</span> 个相关结果
              </div>
            )}
          </div>
        </div>

        {/* 无结果状态 */}
        {!error && !loading && !hasResults && (
          <div className="no-results">
            <div className="no-results-icon">🔍</div>
            <h3>没有找到相关角色</h3>
            <p>
              没有找到包含 "<strong>{query}</strong>" 的角色信息
            </p>
            <div className="search-suggestions-box">
              <h4>搜索建议：</h4>
              <ul>
                <li>检查关键词的拼写</li>
                <li>尝试使用更简短的关键词</li>
                <li>尝试搜索角色的中文名或英文名</li>
                <li>可以搜索元素类型，如 "火" "水" "风" 等</li>
              </ul>
            </div>
            <div className="quick-actions">
              <button
                onClick={() => navigate('/characters')}
                className="btn btn-primary"
              >
                浏览所有角色
              </button>
            </div>
          </div>
        )}

        {/* 搜索结果 */}
        {!error && !loading && hasResults && (
          <div className="search-results">
            {/* 角色结果 */}
            {results.characters && results.characters.length > 0 && (
              <div className="result-section">
                <h2 className="section-title">
                  角色 <span className="count">({results.characters.length})</span>
                </h2>
                <div className="results-grid">
                  {results.characters.map((character) => (
                    <CharacterCard
                      key={character.id}
                      character={character}
                      onClick={() => handleCharacterClick(character)}
                      showSkills={true}
                    />
                  ))}
                </div>
              </div>
            )}

            {/* 武器结果 */}
            {results.weapons && results.weapons.length > 0 && (
              <div className="result-section">
                <h2 className="section-title">
                  武器 <span className="count">({results.weapons.length})</span>
                </h2>
                <div className="results-list">
                  {results.weapons.map((weapon) => (
                    <div
                      key={weapon.id}
                      className="result-item"
                      onClick={() => navigate(`/weapons/${weapon.id}`)}
                    >
                      <span className="item-name">{weapon.name}</span>
                      <span className="item-type">{weapon.weapon_type}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* 圣遗物结果 */}
            {results.artifacts && results.artifacts.length > 0 && (
              <div className="result-section">
                <h2 className="section-title">
                  圣遗物 <span className="count">({results.artifacts.length})</span>
                </h2>
                <div className="results-list">
                  {results.artifacts.map((artifact) => (
                    <div
                      key={artifact.id}
                      className="result-item"
                      onClick={() => navigate(`/artifacts/${artifact.id}`)}
                    >
                      <span className="item-name">{artifact.name}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* 怪物结果 */}
            {results.monsters && results.monsters.length > 0 && (
              <div className="result-section">
                <h2 className="section-title">
                  怪物 <span className="count">({results.monsters.length})</span>
                </h2>
                <div className="results-list">
                  {results.monsters.map((monster) => (
                    <div
                      key={monster.id}
                      className="result-item"
                      onClick={() => navigate(`/monsters/${monster.id}`)}
                    >
                      <span className="item-name">{monster.name}</span>
                      <span className="item-type">{monster.type}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* 相关操作 */}
            <div className="search-actions">
              <div className="action-buttons">
                <button
                  onClick={() => navigate('/characters')}
                  className="btn btn-secondary"
                >
                  查看所有角色
                </button>
                <button
                  onClick={() => window.history.back()}
                  className="btn btn-outline"
                >
                  返回上一页
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default SearchResultsPage;

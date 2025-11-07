/**
 * 页面头部组件
 */
import React, { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import characterAPI from '../../services/characterAPI';
import './Header.css';

const Header = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [isSearching, setIsSearching] = useState(false);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const navigate = useNavigate();

  // 搜索建议的防抖处理
  const handleSearchInput = useCallback(async (query) => {
    if (!query || query.trim().length < 2) {
      setSearchResults([]);
      setShowSuggestions(false);
      return;
    }

    setIsSearching(true);
    try {
      const response = await characterAPI.searchCharacters(query.trim(), 5);
      if (response.success) {
        setSearchResults(response.data.results || []);
        setShowSuggestions(true);
      }
    } catch (error) {
      console.error('搜索失败:', error);
      setSearchResults([]);
    } finally {
      setIsSearching(false);
    }
  }, []);

  // 处理输入变化
  const handleInputChange = (e) => {
    const query = e.target.value;
    setSearchQuery(query);

    // 简单的防抖处理
    clearTimeout(window.searchTimeout);
    window.searchTimeout = setTimeout(() => {
      handleSearchInput(query);
    }, 300);
  };

  // 处理搜索提交
  const handleSearchSubmit = (e) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      setShowSuggestions(false);
      navigate(`/search?q=${encodeURIComponent(searchQuery.trim())}`);
    }
  };

  // 处理建议项点击
  const handleSuggestionClick = (character) => {
    setSearchQuery('');
    setShowSuggestions(false);
    navigate(`/characters/${character.id}`);
  };

  // 隐藏建议
  const hideSuggestions = () => {
    setTimeout(() => setShowSuggestions(false), 200);
  };

  return (
    <header className="header">
      <div className="header-container">
        <h1
          className="logo-text"
          onClick={() => navigate('/')}
          style={{ cursor: 'pointer' }}
        >
          原神游戏信息网站
        </h1>
        <div className="search-bar">
          <form onSubmit={handleSearchSubmit} className="search-form">
            <div className="search-input-container">
              <input
                type="text"
                value={searchQuery}
                onChange={handleInputChange}
                onBlur={hideSuggestions}
                placeholder="搜索角色、武器、圣遗物..."
                className="search-input"
              />
              <button type="submit" className="search-button" disabled={isSearching}>
                {isSearching ? '搜索中...' : '🔍'}
              </button>

              {/* 搜索建议下拉框 */}
              {showSuggestions && searchResults.length > 0 && (
                <div className="search-suggestions">
                  {searchResults.map((character) => (
                    <div
                      key={character.id}
                      className="search-suggestion-item"
                      onClick={() => handleSuggestionClick(character)}
                    >
                      <div className="suggestion-avatar">
                        <span className={`element-icon ${character.element?.toLowerCase()}`}>
                          {character.element?.charAt(0)}
                        </span>
                      </div>
                      <div className="suggestion-info">
                        <div className="suggestion-name">
                          {character.name} {character.name_en && `(${character.name_en})`}
                        </div>
                        <div className="suggestion-details">
                          <span className="suggestion-element">{character.element}</span>
                          <span className="suggestion-weapon">{character.weapon_type}</span>
                          <span className="suggestion-rarity">{'★'.repeat(character.rarity)}</span>
                        </div>
                      </div>
                    </div>
                  ))}
                  <div className="search-suggestion-more" onClick={() => handleSearchSubmit({ preventDefault: () => {} })}>
                    查看更多搜索结果...
                  </div>
                </div>
              )}
            </div>
          </form>
        </div>
      </div>
    </header>
  );
};

export default Header;
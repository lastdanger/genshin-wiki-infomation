/**
 * 导航组件
 */
import React from 'react';
import { Link, useLocation } from 'react-router-dom';

const Navigation = () => {
  const location = useLocation();

  const navItems = [
    { path: '/', label: '首页' },
    { path: '/characters', label: '角色' },
    { path: '/weapons', label: '武器' },
    { path: '/artifacts', label: '圣遗物' },
    { path: '/monsters', label: '怪物' },
    { path: '/game-mechanics', label: '游戏机制' },
    { path: '/gallery', label: '图片画廊' },
    { path: '/admin', label: '管理' },
  ];

  return (
    <nav className="navigation">
      <div className="container">
        <ul className="nav-list">
          {navItems.map((item) => (
            <li key={item.path} className="nav-item">
              <Link
                to={item.path}
                className={`nav-link ${location.pathname === item.path ? 'active' : ''}`}
              >
                {item.label}
              </Link>
            </li>
          ))}
        </ul>
      </div>
    </nav>
  );
};

export default Navigation;
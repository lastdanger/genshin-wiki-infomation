/**
 * 首页组件
 */
import React from 'react';

const HomePage = () => {
  return (
    <div className="home-page">
      <div className="hero-section">
        <h1>欢迎来到原神游戏信息网站</h1>
        <p>查找角色、武器、圣遗物、怪物等游戏信息</p>
      </div>

      <div className="quick-links">
        <div className="link-card">
          <h3>角色信息</h3>
          <p>查看所有角色的详细信息、技能和天赋</p>
        </div>
        <div className="link-card">
          <h3>武器信息</h3>
          <p>了解各种武器的属性和特效</p>
        </div>
        <div className="link-card">
          <h3>圣遗物信息</h3>
          <p>查看圣遗物套装效果和搭配推荐</p>
        </div>
        <div className="link-card">
          <h3>怪物信息</h3>
          <p>研究怪物弱点和应对策略</p>
        </div>
      </div>
    </div>
  );
};

export default HomePage;
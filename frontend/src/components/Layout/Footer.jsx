/**
 * 页面底部组件
 */
import React from 'react';

const Footer = () => {
  return (
    <footer className="footer">
      <div className="container">
        <div className="footer-content">
          <p>&copy; 2025 原神游戏信息网站. 所有权利保留.</p>
          <p>
            数据来源：
            <a href="https://wiki.biligame.com/ys/" target="_blank" rel="noopener noreferrer">
              哔哩哔哩游戏Wiki
            </a>
            、
            <a href="https://homdgcat.wiki/" target="_blank" rel="noopener noreferrer">
              玉衡杯数据库
            </a>
          </p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
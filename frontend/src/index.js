/**
 * 原神游戏信息网站 - React应用入口点
 *
 * 负责将App组件挂载到DOM中
 */
import React from 'react';
import { createRoot } from 'react-dom/client';
import './index.css';
import App from './App';

// 获取根容器元素
const container = document.getElementById('root');

// 创建React 18的根实例
const root = createRoot(container);

// 渲染应用
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

// 隐藏全局加载器（如果存在）
if (window.hideGlobalLoader) {
  // 稍微延迟隐藏，确保应用已完全渲染
  setTimeout(window.hideGlobalLoader, 800);
}
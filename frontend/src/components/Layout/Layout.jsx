/**
 * 布局组件
 *
 * 提供应用的基本布局结构
 */
import React from 'react';
import Header from './Header';
import Navigation from './Navigation';
import Footer from './Footer';
import './Layout.css';

const Layout = ({ children }) => {
  return (
    <div className="layout">
      <Header />
      <Navigation />
      <main className="main-content">
        {children}
      </main>
      <Footer />
    </div>
  );
};

export default Layout;
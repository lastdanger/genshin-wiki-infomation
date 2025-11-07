/**
 * 加载动画组件
 */
import React from 'react';

const LoadingSpinner = ({ message = '加载中...' }) => {
  return (
    <div className="loading-spinner">
      <div className="spinner"></div>
      <p className="loading-message">{message}</p>
    </div>
  );
};

export default LoadingSpinner;
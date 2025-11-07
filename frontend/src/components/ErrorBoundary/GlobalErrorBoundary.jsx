/**
 * 全局错误边界
 *
 * 捕获应用中所有未处理的React错误
 * 显示友好的错误页面，防止白屏
 */
import React, { Component } from 'react';
import ErrorFallback from './ErrorFallback';

class GlobalErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null
    };
  }

  static getDerivedStateFromError(error) {
    // 更新state使下一次渲染能够显示降级后的UI
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    // 记录错误信息
    console.error('全局错误边界捕获到错误:', error, errorInfo);

    this.setState({
      error,
      errorInfo
    });

    // 记录错误日志
    this.logError(error, errorInfo);
  }

  logError = (error, errorInfo) => {
    try {
      // 记录到本地存储
      const errorLog = {
        timestamp: new Date().toISOString(),
        error: {
          message: error.toString(),
          stack: error.stack
        },
        errorInfo: {
          componentStack: errorInfo.componentStack
        },
        userAgent: navigator.userAgent,
        url: window.location.href
      };

      // 存储到localStorage（实际项目中应该发送到服务器）
      const existingLogs = JSON.parse(localStorage.getItem('errorLogs') || '[]');
      existingLogs.push(errorLog);

      // 只保留最近的20条错误日志
      if (existingLogs.length > 20) {
        existingLogs.shift();
      }

      localStorage.setItem('errorLogs', JSON.stringify(existingLogs));

      // TODO: 发送到错误监控服务
      // sendErrorToMonitoring(errorLog);
    } catch (logError) {
      console.error('记录错误日志失败:', logError);
    }
  };

  resetError = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null
    });
  };

  render() {
    if (this.state.hasError) {
      return (
        <ErrorFallback
          error={this.state.error}
          errorInfo={this.state.errorInfo}
          resetError={this.resetError}
          showDetails={process.env.NODE_ENV === 'development'}
        />
      );
    }

    return this.props.children;
  }
}

export default GlobalErrorBoundary;

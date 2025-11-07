/**
 * 通用错误边界组件
 *
 * 可配置的局部错误边界，用于包裹特定组件或路由
 * 提供错误隔离、自定义fallback UI、错误重试等功能
 */
import React, { Component } from 'react';
import PropTypes from 'prop-types';
import ErrorFallback from './ErrorFallback';

class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
      retryCount: 0
    };
  }

  static getDerivedStateFromError(error) {
    // 更新state使下一次渲染能够显示降级后的UI
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    // 记录错误信息
    console.error('错误边界捕获到错误:', error, errorInfo);

    this.setState({
      error,
      errorInfo
    });

    // 调用自定义错误处理函数
    if (this.props.onError) {
      this.props.onError(error, errorInfo);
    }

    // 记录错误日志
    this.logError(error, errorInfo);
  }

  logError = (error, errorInfo) => {
    try {
      const errorLog = {
        timestamp: new Date().toISOString(),
        boundary: this.props.name || 'ErrorBoundary',
        error: {
          message: error.toString(),
          stack: error.stack
        },
        errorInfo: {
          componentStack: errorInfo.componentStack
        },
        userAgent: navigator.userAgent,
        url: window.location.href,
        retryCount: this.state.retryCount
      };

      // 存储到localStorage
      const existingLogs = JSON.parse(localStorage.getItem('errorLogs') || '[]');
      existingLogs.push(errorLog);

      // 只保留最近的20条错误日志
      if (existingLogs.length > 20) {
        existingLogs.shift();
      }

      localStorage.setItem('errorLogs', JSON.stringify(existingLogs));

      // TODO: 发送到错误监控服务
      // if (this.props.reportError) {
      //   this.props.reportError(errorLog);
      // }
    } catch (logError) {
      console.error('记录错误日志失败:', logError);
    }
  };

  resetError = () => {
    const { maxRetries = 3 } = this.props;

    // 检查是否超过最大重试次数
    if (this.state.retryCount >= maxRetries) {
      console.warn(`已达到最大重试次数 (${maxRetries})`);

      // 调用重试失败回调
      if (this.props.onResetFailed) {
        this.props.onResetFailed(this.state.error, this.state.retryCount);
      }
      return;
    }

    this.setState(prevState => ({
      hasError: false,
      error: null,
      errorInfo: null,
      retryCount: prevState.retryCount + 1
    }));

    // 调用重试成功回调
    if (this.props.onReset) {
      this.props.onReset(this.state.retryCount + 1);
    }
  };

  render() {
    const { hasError, error, errorInfo, retryCount } = this.state;
    const {
      children,
      fallback,
      FallbackComponent,
      showDetails,
      name,
      maxRetries = 3
    } = this.props;

    if (hasError) {
      // 如果提供了自定义的 fallback 组件
      if (FallbackComponent) {
        return (
          <FallbackComponent
            error={error}
            errorInfo={errorInfo}
            resetError={this.resetError}
            retryCount={retryCount}
            maxRetries={maxRetries}
          />
        );
      }

      // 如果提供了自定义的 fallback 函数
      if (fallback) {
        return fallback({
          error,
          errorInfo,
          resetError: this.resetError,
          retryCount,
          maxRetries
        });
      }

      // 使用默认的 ErrorFallback 组件
      return (
        <ErrorFallback
          error={error}
          errorInfo={errorInfo}
          resetError={this.resetError}
          showDetails={showDetails !== undefined ? showDetails : process.env.NODE_ENV === 'development'}
          title={name ? `${name} 遇到了错误` : undefined}
          retryCount={retryCount}
          maxRetries={maxRetries}
        />
      );
    }

    return children;
  }
}

ErrorBoundary.propTypes = {
  children: PropTypes.node.isRequired,

  // 错误边界名称（用于日志记录）
  name: PropTypes.string,

  // 自定义 fallback 组件
  FallbackComponent: PropTypes.elementType,

  // 自定义 fallback 函数
  fallback: PropTypes.func,

  // 是否显示错误详情
  showDetails: PropTypes.bool,

  // 最大重试次数
  maxRetries: PropTypes.number,

  // 错误回调
  onError: PropTypes.func,

  // 重置回调
  onReset: PropTypes.func,

  // 重置失败回调
  onResetFailed: PropTypes.func,

  // 错误上报函数
  reportError: PropTypes.func
};

ErrorBoundary.defaultProps = {
  name: 'ErrorBoundary',
  maxRetries: 3,
  showDetails: process.env.NODE_ENV === 'development'
};

export default ErrorBoundary;

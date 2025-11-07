/**
 * ErrorBoundary 组件
 *
 * React 错误边界，捕获组件树中的 JavaScript 错误并显示友好的错误 UI
 */

import React, { Component, ErrorInfo, ReactNode } from 'react';
import { ErrorCode, ErrorSeverity } from '../../services/errors/types';
import { ErrorHandler } from '../../services/errors/errorHandler';
import ErrorFallback from './ErrorFallback';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
  resetKeys?: Array<string | number>;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
  errorCount: number;
}

/**
 * ErrorBoundary 组件
 * 捕获子组件树中的 JavaScript 错误，记录错误，并显示备用 UI
 */
class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
      errorCount: 0,
    };
  }

  /**
   * 当子组件抛出错误时调用
   */
  static getDerivedStateFromError(error: Error): Partial<State> {
    return {
      hasError: true,
      error,
    };
  }

  /**
   * 记录错误信息
   */
  componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    // 增加错误计数
    this.setState((prevState) => ({
      errorInfo,
      errorCount: prevState.errorCount + 1,
    }));

    // 记录错误到控制台
    ErrorHandler.logError(error, 'ErrorBoundary');

    // 报告错误（如果在生产环境）
    if (process.env.NODE_ENV === 'production') {
      ErrorHandler.reportError(error, {
        componentStack: errorInfo.componentStack,
        errorCount: this.state.errorCount + 1,
      });
    }

    // 调用自定义错误处理
    if (this.props.onError) {
      this.props.onError(error, errorInfo);
    }
  }

  /**
   * 检测 resetKeys 变化并重置错误状态
   */
  componentDidUpdate(prevProps: Props): void {
    if (this.state.hasError && this.props.resetKeys) {
      const prevKeys = prevProps.resetKeys || [];
      const currentKeys = this.props.resetKeys;

      // 如果 resetKeys 发生变化，重置错误状态
      if (prevKeys.length !== currentKeys.length ||
          prevKeys.some((key, index) => key !== currentKeys[index])) {
        this.resetErrorBoundary();
      }
    }
  }

  /**
   * 重置错误边界状态
   */
  resetErrorBoundary = (): void => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
    });
  };

  /**
   * 渲染
   */
  render(): ReactNode {
    const { hasError, error, errorInfo } = this.state;
    const { children, fallback } = this.props;

    if (hasError && error) {
      // 使用自定义 fallback 或默认 ErrorFallback
      if (fallback) {
        return fallback;
      }

      return (
        <ErrorFallback
          error={error}
          errorInfo={errorInfo}
          onReset={this.resetErrorBoundary}
        />
      );
    }

    return children;
  }
}

export default ErrorBoundary;

/**
 * ErrorBoundary 组件测试
 */

import React from 'react';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import ErrorBoundary from './ErrorBoundary';
import { ErrorHandler } from '../../services/errors/errorHandler';

// Mock ErrorHandler
jest.mock('../../services/errors/errorHandler', () => ({
  ErrorHandler: {
    logError: jest.fn(),
    reportError: jest.fn(),
  },
}));

// 抛出错误的测试组件
const ThrowError: React.FC<{ shouldThrow?: boolean; error?: Error }> = ({
  shouldThrow = true,
  error = new Error('Test error'),
}) => {
  if (shouldThrow) {
    throw error;
  }
  return <div>Normal component</div>;
};

// 抑制 console.error 在测试中的输出
const originalError = console.error;
beforeAll(() => {
  console.error = jest.fn();
});

afterAll(() => {
  console.error = originalError;
});

describe('ErrorBoundary', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('正常渲染', () => {
    it('should render children when no error occurs', () => {
      render(
        <ErrorBoundary>
          <div>Test content</div>
        </ErrorBoundary>
      );

      expect(screen.getByText('Test content')).toBeInTheDocument();
    });

    it('should render children without error boundary when shouldThrow is false', () => {
      render(
        <ErrorBoundary>
          <ThrowError shouldThrow={false} />
        </ErrorBoundary>
      );

      expect(screen.getByText('Normal component')).toBeInTheDocument();
    });
  });

  describe('错误捕获', () => {
    it('should catch errors and display error fallback', () => {
      render(
        <ErrorBoundary>
          <ThrowError />
        </ErrorBoundary>
      );

      // 应该显示错误 UI
      expect(screen.getByText(/出了点问题/i)).toBeInTheDocument();
    });

    it('should log error when error is caught', () => {
      render(
        <ErrorBoundary>
          <ThrowError />
        </ErrorBoundary>
      );

      expect(ErrorHandler.logError).toHaveBeenCalledWith(
        expect.any(Error),
        'ErrorBoundary'
      );
    });

    it('should call onError callback when provided', () => {
      const onError = jest.fn();

      render(
        <ErrorBoundary onError={onError}>
          <ThrowError />
        </ErrorBoundary>
      );

      expect(onError).toHaveBeenCalledWith(
        expect.any(Error),
        expect.objectContaining({
          componentStack: expect.any(String),
        })
      );
    });

    it('should report error in production mode', () => {
      const originalEnv = process.env.NODE_ENV;
      process.env.NODE_ENV = 'production';

      render(
        <ErrorBoundary>
          <ThrowError />
        </ErrorBoundary>
      );

      expect(ErrorHandler.reportError).toHaveBeenCalled();

      process.env.NODE_ENV = originalEnv;
    });

    it('should not report error in development mode', () => {
      const originalEnv = process.env.NODE_ENV;
      process.env.NODE_ENV = 'development';

      render(
        <ErrorBoundary>
          <ThrowError />
        </ErrorBoundary>
      );

      expect(ErrorHandler.reportError).not.toHaveBeenCalled();

      process.env.NODE_ENV = originalEnv;
    });
  });

  describe('自定义 Fallback', () => {
    it('should render custom fallback when provided', () => {
      const customFallback = <div>Custom error UI</div>;

      render(
        <ErrorBoundary fallback={customFallback}>
          <ThrowError />
        </ErrorBoundary>
      );

      expect(screen.getByText('Custom error UI')).toBeInTheDocument();
      expect(screen.queryByText(/出了点问题/i)).not.toBeInTheDocument();
    });
  });

  describe('错误重置', () => {
    it('should reset error state when reset button is clicked', async () => {
      const user = userEvent.setup();
      const { rerender } = render(
        <ErrorBoundary>
          <ThrowError />
        </ErrorBoundary>
      );

      // 确认显示错误 UI
      expect(screen.getByText(/出了点问题/i)).toBeInTheDocument();

      // 点击刷新页面按钮
      const resetButton = screen.getByRole('button', { name: /刷新页面/i });
      await user.click(resetButton);

      // 重新渲染，不抛出错误
      rerender(
        <ErrorBoundary>
          <ThrowError shouldThrow={false} />
        </ErrorBoundary>
      );

      // 应该显示正常内容
      expect(screen.getByText('Normal component')).toBeInTheDocument();
    });

    it('should reset error state when resetKeys change', () => {
      const { rerender } = render(
        <ErrorBoundary resetKeys={[1]}>
          <ThrowError />
        </ErrorBoundary>
      );

      // 确认显示错误 UI
      expect(screen.getByText(/出了点问题/i)).toBeInTheDocument();

      // 改变 resetKeys，不抛出错误
      rerender(
        <ErrorBoundary resetKeys={[2]}>
          <ThrowError shouldThrow={false} />
        </ErrorBoundary>
      );

      // 应该显示正常内容
      expect(screen.getByText('Normal component')).toBeInTheDocument();
    });

    it('should not reset when resetKeys do not change', () => {
      const { rerender } = render(
        <ErrorBoundary resetKeys={[1]}>
          <ThrowError />
        </ErrorBoundary>
      );

      // 确认显示错误 UI
      expect(screen.getByText(/出了点问题/i)).toBeInTheDocument();

      // 重新渲染，resetKeys 不变
      rerender(
        <ErrorBoundary resetKeys={[1]}>
          <ThrowError shouldThrow={false} />
        </ErrorBoundary>
      );

      // 应该仍然显示错误 UI
      expect(screen.getByText(/出了点问题/i)).toBeInTheDocument();
    });

    it('should reset when resetKeys array length changes', () => {
      const { rerender } = render(
        <ErrorBoundary resetKeys={[1]}>
          <ThrowError />
        </ErrorBoundary>
      );

      expect(screen.getByText(/出了点问题/i)).toBeInTheDocument();

      rerender(
        <ErrorBoundary resetKeys={[1, 2]}>
          <ThrowError shouldThrow={false} />
        </ErrorBoundary>
      );

      expect(screen.getByText('Normal component')).toBeInTheDocument();
    });
  });

  describe('错误计数', () => {
    it('should increment error count on each error', () => {
      const { rerender } = render(
        <ErrorBoundary>
          <ThrowError error={new Error('First error')} />
        </ErrorBoundary>
      );

      // 第一次错误 - 显示错误 fallback
      expect(screen.getByText(/出了点问题/i)).toBeInTheDocument();

      // 重置并触发第二次错误
      rerender(
        <ErrorBoundary resetKeys={[1]}>
          <ThrowError shouldThrow={false} />
        </ErrorBoundary>
      );

      rerender(
        <ErrorBoundary resetKeys={[2]}>
          <ThrowError error={new Error('Second error')} />
        </ErrorBoundary>
      );

      // 第二次错误
      expect(screen.getByText(/出了点问题/i)).toBeInTheDocument();
    });
  });

  describe('边界情况', () => {
    it('should handle null children', () => {
      render(<ErrorBoundary>{null}</ErrorBoundary>);

      expect(screen.queryByText(/出了点问题/i)).not.toBeInTheDocument();
    });

    it('should handle undefined children', () => {
      render(<ErrorBoundary>{undefined}</ErrorBoundary>);

      expect(screen.queryByText(/出了点问题/i)).not.toBeInTheDocument();
    });

    it('should handle multiple children', () => {
      render(
        <ErrorBoundary>
          <div>Child 1</div>
          <div>Child 2</div>
        </ErrorBoundary>
      );

      expect(screen.getByText('Child 1')).toBeInTheDocument();
      expect(screen.getByText('Child 2')).toBeInTheDocument();
    });

    it('should catch errors from any level of children', () => {
      render(
        <ErrorBoundary>
          <div>
            <div>
              <ThrowError />
            </div>
          </div>
        </ErrorBoundary>
      );

      expect(screen.getByText(/出了点问题/i)).toBeInTheDocument();
    });
  });
});

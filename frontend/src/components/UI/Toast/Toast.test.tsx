/**
 * Toast 组件测试
 */

import React from 'react';
import { render, screen, waitFor, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ToastContainer, ToastMessage } from './Toast';

// Mock CSS to avoid import errors
jest.mock('./Toast.css', () => ({}));

describe('ToastContainer', () => {
  beforeEach(() => {
    jest.clearAllTimers();
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.runOnlyPendingTimers();
    jest.useRealTimers();
  });

  describe('显示 Toast', () => {
    it('should display toast when custom event is dispatched', () => {
      render(<ToastContainer />);

      // 触发自定义事件
      act(() => {
        window.dispatchEvent(
          new CustomEvent('toast:show', {
            detail: {
              type: 'success',
              message: 'Operation successful',
              duration: 5000,
            },
          })
        );
      });

      expect(screen.getByText('Operation successful')).toBeInTheDocument();
    });

    it('should display multiple toasts', () => {
      render(<ToastContainer />);

      act(() => {
        window.dispatchEvent(
          new CustomEvent('toast:show', {
            detail: {
              type: 'success',
              message: 'First toast',
            },
          })
        );

        window.dispatchEvent(
          new CustomEvent('toast:show', {
            detail: {
              type: 'error',
              message: 'Second toast',
            },
          })
        );
      });

      expect(screen.getByText('First toast')).toBeInTheDocument();
      expect(screen.getByText('Second toast')).toBeInTheDocument();
    });
  });

  describe('Toast 类型', () => {
    it('should render success toast with correct styling', () => {
      render(<ToastContainer />);

      act(() => {
        window.dispatchEvent(
          new CustomEvent('toast:show', {
            detail: {
              type: 'success',
              message: 'Success message',
            },
          })
        );
      });

      const toast = screen.getByRole('alert');
      expect(toast).toHaveClass('toast--success');
    });

    it('should render error toast with correct styling', () => {
      render(<ToastContainer />);

      act(() => {
        window.dispatchEvent(
          new CustomEvent('toast:show', {
            detail: {
              type: 'error',
              message: 'Error message',
            },
          })
        );
      });

      const toast = screen.getByRole('alert');
      expect(toast).toHaveClass('toast--error');
    });

    it('should render warning toast with correct styling', () => {
      render(<ToastContainer />);

      act(() => {
        window.dispatchEvent(
          new CustomEvent('toast:show', {
            detail: {
              type: 'warning',
              message: 'Warning message',
            },
          })
        );
      });

      const toast = screen.getByRole('alert');
      expect(toast).toHaveClass('toast--warning');
    });

    it('should render info toast with correct styling', () => {
      render(<ToastContainer />);

      act(() => {
        window.dispatchEvent(
          new CustomEvent('toast:show', {
            detail: {
              type: 'info',
              message: 'Info message',
            },
          })
        );
      });

      const toast = screen.getByRole('alert');
      expect(toast).toHaveClass('toast--info');
    });
  });

  describe('自动关闭', () => {
    it('should auto close toast after default duration (5s)', async () => {
      render(<ToastContainer />);

      act(() => {
        window.dispatchEvent(
          new CustomEvent('toast:show', {
            detail: {
              type: 'success',
              message: 'Auto close toast',
            },
          })
        );
      });

      expect(screen.getByText('Auto close toast')).toBeInTheDocument();

      // 快进 5 秒
      act(() => {
        jest.advanceTimersByTime(5000);
      });

      // 等待关闭动画（300ms）
      act(() => {
        jest.advanceTimersByTime(300);
      });

      await waitFor(() => {
        expect(screen.queryByText('Auto close toast')).not.toBeInTheDocument();
      });
    });

    it('should auto close toast after custom duration', async () => {
      render(<ToastContainer />);

      act(() => {
        window.dispatchEvent(
          new CustomEvent('toast:show', {
            detail: {
              type: 'success',
              message: 'Custom duration toast',
              duration: 3000,
            },
          })
        );
      });

      expect(screen.getByText('Custom duration toast')).toBeInTheDocument();

      // 快进 3 秒
      act(() => {
        jest.advanceTimersByTime(3000);
      });

      // 等待关闭动画
      act(() => {
        jest.advanceTimersByTime(300);
      });

      await waitFor(() => {
        expect(
          screen.queryByText('Custom duration toast')
        ).not.toBeInTheDocument();
      });
    });
  });

  describe('手动关闭', () => {
    it('should close toast when close button is clicked', async () => {
      const user = userEvent.setup({ delay: null });
      render(<ToastContainer />);

      act(() => {
        window.dispatchEvent(
          new CustomEvent('toast:show', {
            detail: {
              type: 'success',
              message: 'Manual close toast',
            },
          })
        );
      });

      expect(screen.getByText('Manual close toast')).toBeInTheDocument();

      // 点击关闭按钮
      const closeButton = screen.getByLabelText('关闭');
      await user.click(closeButton);

      // 等待关闭动画
      act(() => {
        jest.advanceTimersByTime(300);
      });

      await waitFor(() => {
        expect(
          screen.queryByText('Manual close toast')
        ).not.toBeInTheDocument();
      });
    });

    it('should only close the specific toast when multiple toasts exist', async () => {
      const user = userEvent.setup({ delay: null });
      render(<ToastContainer />);

      act(() => {
        window.dispatchEvent(
          new CustomEvent('toast:show', {
            detail: {
              type: 'success',
              message: 'First toast',
            },
          })
        );

        window.dispatchEvent(
          new CustomEvent('toast:show', {
            detail: {
              type: 'error',
              message: 'Second toast',
            },
          })
        );
      });

      expect(screen.getByText('First toast')).toBeInTheDocument();
      expect(screen.getByText('Second toast')).toBeInTheDocument();

      // 关闭第一个 toast
      const closeButtons = screen.getAllByLabelText('关闭');
      await user.click(closeButtons[0]);

      act(() => {
        jest.advanceTimersByTime(300);
      });

      await waitFor(() => {
        expect(screen.queryByText('First toast')).not.toBeInTheDocument();
      });

      // 第二个 toast 应该仍然存在
      expect(screen.getByText('Second toast')).toBeInTheDocument();
    });
  });

  describe('Toast 图标', () => {
    it('should display success icon for success type', () => {
      render(<ToastContainer />);

      act(() => {
        window.dispatchEvent(
          new CustomEvent('toast:show', {
            detail: {
              type: 'success',
              message: 'Success',
            },
          })
        );
      });

      const toast = screen.getByRole('alert');
      const icon = toast.querySelector('.toast__icon svg');
      expect(icon).toBeInTheDocument();
    });

    it('should display error icon for error type', () => {
      render(<ToastContainer />);

      act(() => {
        window.dispatchEvent(
          new CustomEvent('toast:show', {
            detail: {
              type: 'error',
              message: 'Error',
            },
          })
        );
      });

      const toast = screen.getByRole('alert');
      const icon = toast.querySelector('.toast__icon svg');
      expect(icon).toBeInTheDocument();
    });

    it('should display warning icon for warning type', () => {
      render(<ToastContainer />);

      act(() => {
        window.dispatchEvent(
          new CustomEvent('toast:show', {
            detail: {
              type: 'warning',
              message: 'Warning',
            },
          })
        );
      });

      const toast = screen.getByRole('alert');
      const icon = toast.querySelector('.toast__icon svg');
      expect(icon).toBeInTheDocument();
    });

    it('should display info icon for info type', () => {
      render(<ToastContainer />);

      act(() => {
        window.dispatchEvent(
          new CustomEvent('toast:show', {
            detail: {
              type: 'info',
              message: 'Info',
            },
          })
        );
      });

      const toast = screen.getByRole('alert');
      const icon = toast.querySelector('.toast__icon svg');
      expect(icon).toBeInTheDocument();
    });
  });

  describe('可访问性', () => {
    it('should have role="alert" for accessibility', () => {
      render(<ToastContainer />);

      act(() => {
        window.dispatchEvent(
          new CustomEvent('toast:show', {
            detail: {
              type: 'success',
              message: 'Accessible toast',
            },
          })
        );
      });

      const toast = screen.getByRole('alert');
      expect(toast).toBeInTheDocument();
    });

    it('should have aria-label on close button', () => {
      render(<ToastContainer />);

      act(() => {
        window.dispatchEvent(
          new CustomEvent('toast:show', {
            detail: {
              type: 'success',
              message: 'Toast with close button',
            },
          })
        );
      });

      const closeButton = screen.getByLabelText('关闭');
      expect(closeButton).toBeInTheDocument();
    });
  });

  describe('边界情况', () => {
    it('should handle empty message', () => {
      render(<ToastContainer />);

      act(() => {
        window.dispatchEvent(
          new CustomEvent('toast:show', {
            detail: {
              type: 'success',
              message: '',
            },
          })
        );
      });

      const toast = screen.getByRole('alert');
      expect(toast).toBeInTheDocument();
    });

    it('should handle very long message', () => {
      render(<ToastContainer />);

      const longMessage = 'A'.repeat(500);

      act(() => {
        window.dispatchEvent(
          new CustomEvent('toast:show', {
            detail: {
              type: 'success',
              message: longMessage,
            },
          })
        );
      });

      expect(screen.getByText(longMessage)).toBeInTheDocument();
    });

    it('should generate unique IDs for each toast', () => {
      render(<ToastContainer />);

      act(() => {
        window.dispatchEvent(
          new CustomEvent('toast:show', {
            detail: {
              type: 'success',
              message: 'Toast 1',
            },
          })
        );

        window.dispatchEvent(
          new CustomEvent('toast:show', {
            detail: {
              type: 'success',
              message: 'Toast 2',
            },
          })
        );
      });

      const toasts = screen.getAllByRole('alert');
      expect(toasts).toHaveLength(2);
    });
  });

  describe('组件卸载清理', () => {
    it('should cleanup event listeners on unmount', () => {
      const { unmount } = render(<ToastContainer />);

      const addEventListenerSpy = jest.spyOn(window, 'addEventListener');
      const removeEventListenerSpy = jest.spyOn(window, 'removeEventListener');

      unmount();

      expect(removeEventListenerSpy).toHaveBeenCalledWith(
        'toast:show',
        expect.any(Function)
      );

      addEventListenerSpy.mockRestore();
      removeEventListenerSpy.mockRestore();
    });
  });
});

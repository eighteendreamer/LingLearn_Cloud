import { Component, ReactNode } from "react";
import { Link } from "react-router";

import { AlertTriangle } from "lucide-react";

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="h-screen w-screen flex items-center justify-center bg-black">
          <div className="text-center px-4">
            <div className="flex justify-center mb-6 text-amber-500">
              <AlertTriangle className="h-20 w-20" />
            </div>
            <h1 className="text-2xl font-bold text-white mb-4">出错了</h1>
            <p className="text-gray-400 mb-6">{this.state.error?.message || "未知错误"}</p>
            <Link
              to="/"
              className="inline-block px-6 py-3 bg-emerald-500 text-white rounded-full font-medium hover:bg-emerald-600 transition-colors"
              onClick={() => this.setState({ hasError: false })}
            >
              返回首页
            </Link>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

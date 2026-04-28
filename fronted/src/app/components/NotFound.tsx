import { Link } from "react-router";
import { Home } from "lucide-react";

export function NotFound() {
  return (
    <div className="h-screen w-screen flex items-center justify-center bg-black">
      <div className="text-center px-4">
        <div className="text-8xl font-bold text-emerald-500 mb-4">404</div>
        <h1 className="text-3xl font-bold text-white mb-4">页面未找到</h1>
        <p className="text-gray-400 mb-8">抱歉，您访问的页面不存在</p>
        <Link
          to="/"
          className="inline-flex items-center gap-2 px-6 py-3 bg-emerald-500 text-white rounded-full font-medium hover:bg-emerald-600 transition-colors"
        >
          <Home className="w-5 h-5" />
          返回首页
        </Link>
      </div>
    </div>
  );
}

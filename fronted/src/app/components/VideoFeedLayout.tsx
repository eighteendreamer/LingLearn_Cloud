import { Outlet, Link, useLocation } from "react-router";
import { Home, Compass, BookOpen, User, Plus } from "lucide-react";
import { FloatingAIChat } from "./FloatingAIChat";
import { PageContextProvider } from "../page-context";

const navigation = [
  { name: "首页", path: "/", icon: Home },
  { name: "发现", path: "/discover", icon: Compass },
  { name: "创作", path: "/create", icon: Plus, isCreate: true },
  { name: "学习", path: "/my-learning", icon: BookOpen },
  { name: "我的", path: "/profile", icon: User },
];

export function VideoFeedLayout() {
  const location = useLocation();
  const isDiscoverWatchPage = location.pathname.startsWith("/discover/watch/");
  const hideBottomNav = location.pathname === "/ai-chat" || isDiscoverWatchPage;
  const hideFloatingAIChat = location.pathname === "/ai-chat" || isDiscoverWatchPage;

  return (
    <PageContextProvider>
      <div className="h-screen w-screen overflow-hidden bg-white relative">
        <div className="h-full overflow-hidden">
          <Outlet />
        </div>

        {!hideFloatingAIChat && <FloatingAIChat />}

        {!hideBottomNav && (
          <nav className="fixed bottom-0 left-0 right-0 bg-white/80 backdrop-blur-xl border-t border-gray-100 z-50 shadow-lg">
            <div className="max-w-screen-xl mx-auto px-4">
              <div className="flex items-center justify-around py-2">
                {navigation.map((item) => {
                  const Icon = item.icon;
                  const isActive = location.pathname === item.path;

                  if (item.isCreate) {
                    return (
                      <Link
                        key={item.path}
                        to={item.path}
                        className="flex flex-col items-center gap-1 py-2 px-4"
                      >
                        <div className="w-12 h-12 bg-gradient-to-br from-pink-500 via-red-500 to-yellow-500 rounded-2xl flex items-center justify-center shadow-lg hover:shadow-xl hover:scale-105 transition-all">
                          <Plus className="w-6 h-6 text-white" strokeWidth={2.5} />
                        </div>
                        <span className="text-xs text-gray-700 font-medium">{item.name}</span>
                      </Link>
                    );
                  }

                  return (
                    <Link
                      key={item.path}
                      to={item.path}
                      className={`flex flex-col items-center gap-1 py-2 px-4 transition-all ${
                        isActive
                          ? "text-emerald-600 scale-105"
                          : "text-gray-500 hover:text-gray-700"
                      }`}
                    >
                      <div className={`p-2 rounded-xl transition-all ${
                        isActive
                          ? "bg-emerald-100 shadow-md"
                          : "hover:bg-gray-100"
                      }`}>
                        <Icon className={`w-6 h-6 ${isActive ? "scale-110" : ""}`} strokeWidth={isActive ? 2.5 : 1.5} />
                      </div>
                      <span className={`text-xs ${isActive ? "font-semibold" : ""}`}>{item.name}</span>
                    </Link>
                  );
                })}
              </div>
            </div>
          </nav>
        )}
      </div>
    </PageContextProvider>
  );
}

import { useEffect } from "react";
import { RouterProvider } from "react-router";
import { router } from "./routes";
import { ErrorBoundary } from "./components/ErrorBoundary";
import { applyCurrentUserPreferences, watchSystemThemeChanges } from "./lib/user-preferences";

export default function App() {
  useEffect(() => {
    applyCurrentUserPreferences();

    const handleStorage = () => applyCurrentUserPreferences();
    const stopWatchingTheme = watchSystemThemeChanges(() => applyCurrentUserPreferences());

    window.addEventListener("storage", handleStorage);
    return () => {
      window.removeEventListener("storage", handleStorage);
      stopWatchingTheme();
    };
  }, []);

  return (
    <ErrorBoundary>
      <div className="min-h-screen w-full">
        <RouterProvider router={router} />
      </div>
    </ErrorBoundary>
  );
}

import { RouterProvider } from "react-router";
import { router } from "./routes";
import { ErrorBoundary } from "./components/ErrorBoundary";

export default function App() {
  return (
    <ErrorBoundary>
      <div className="h-screen w-screen overflow-hidden">
        <RouterProvider router={router} />
      </div>
    </ErrorBoundary>
  );
}
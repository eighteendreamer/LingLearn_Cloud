import { RouterProvider } from "react-router";
import { router } from "./routes";
import { ErrorBoundary } from "./components/ErrorBoundary";

export default function App() {
  return (
    <ErrorBoundary>
      <div className="min-h-screen w-full">
        <RouterProvider router={router} />
      </div>
    </ErrorBoundary>
  );
}

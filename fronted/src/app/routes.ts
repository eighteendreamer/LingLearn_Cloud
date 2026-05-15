import { createBrowserRouter } from "react-router";
import { VideoFeedLayout } from "./components/VideoFeedLayout";
import { VideoFeed } from "./components/VideoFeed";
import { MyLearning } from "./components/MyLearning";
import { Discover } from "./components/Discover";
import { DiscoverWatch } from "./components/DiscoverWatch";
import { Profile } from "./components/Profile";
import { NotFound } from "./components/NotFound";
import { AIChat } from "./components/AIChat";
import { StudentProfile } from "./components/StudentProfile";
import { LearningPath } from "./components/LearningPath";
import { OnlinePractice } from "./components/OnlinePractice";
import { LearningAssessment } from "./components/LearningAssessment";
import { LearningReport } from "./components/LearningReport";
import { Settings } from "./components/Settings";
import { Auth } from "./components/Auth";
import { Create } from "./components/Create";
import { ResourceCenter } from "./components/ResourceCenter";
import { EditProfile } from "./components/EditProfile";
import AdminLayout from "./components/admin/AdminLayout";
import AdminLogin from "./components/admin/AdminLogin";
import Dashboard from "./components/admin/Dashboard";
import UserManagement from "./components/admin/UserManagement";
import ContentManagement from "./components/admin/ContentManagement";
import CommentManagement from "./components/admin/CommentManagement";
import CategoryManagement from "./components/admin/CategoryManagement";
import TagManagement from "./components/admin/TagManagement";
import Statistics from "./components/admin/Statistics";
import AdminSettings from "./components/admin/AdminSettings";

export const router = createBrowserRouter([
  {
    path: "/",
    Component: VideoFeedLayout,
    children: [
      { index: true, Component: VideoFeed },
      { path: "my-learning", Component: MyLearning },
      { path: "discover", Component: Discover },
      { path: "discover/watch/:contentId", Component: DiscoverWatch },
      { path: "profile", Component: Profile },
      { path: "edit-profile", Component: EditProfile },
      { path: "ai-chat", Component: AIChat },
      { path: "student-profile", Component: StudentProfile },
      { path: "learning-path", Component: LearningPath },
      { path: "practice", Component: OnlinePractice },
      { path: "assessment", Component: LearningAssessment },
      { path: "report", Component: LearningReport },
      { path: "settings", Component: Settings },
      { path: "create", Component: Create },
      { path: "resources", Component: ResourceCenter },
    ],
  },
  {
    path: "/login",
    Component: Auth,
  },
  {
    path: "/admin/login",
    Component: AdminLogin,
  },
  {
    path: "/admin",
    Component: AdminLayout,
    children: [
      { path: "dashboard", Component: Dashboard },
      { path: "users", Component: UserManagement },
      { path: "contents", Component: ContentManagement },
      { path: "comments", Component: CommentManagement },
      { path: "categories", Component: CategoryManagement },
      { path: "tags", Component: TagManagement },
      { path: "statistics", Component: Statistics },
      { path: "settings", Component: AdminSettings },
    ],
  },
  {
    path: "*",
    Component: NotFound,
  },
]);

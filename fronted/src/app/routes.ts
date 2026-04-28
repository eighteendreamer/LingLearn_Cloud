import { createBrowserRouter } from "react-router";
import { VideoFeedLayout } from "./components/VideoFeedLayout";
import { VideoFeed } from "./components/VideoFeed";
import { MyLearning } from "./components/MyLearning";
import { Discover } from "./components/Discover";
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

export const router = createBrowserRouter([
  {
    path: "/",
    Component: VideoFeedLayout,
    children: [
      { index: true, Component: VideoFeed },
      { path: "my-learning", Component: MyLearning },
      { path: "discover", Component: Discover },
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
    path: "*",
    Component: NotFound,
  },
]);

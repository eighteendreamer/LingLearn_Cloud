import { useEffect, useState } from "react";
import { useNavigate } from "react-router";
import {
  Bell,
  Camera,
  Globe,
  Lock,
  Mail,
  MapPin,
  Palette,
  Phone,
  User,
} from "lucide-react";

import { ApiError } from "../lib/api";
import {
  fetchCurrentUser,
  logoutCurrentUser,
  updateMyProfile,
  updateMySettings,
  uploadMyAvatar,
} from "../lib/account";
import { getStoredCurrentUser, hasSession } from "../lib/session";
import type { CurrentUserResponse } from "../lib/types";

type SettingsFormState = {
  display_name: string;
  phone: string;
  email: string;
  learning_goal: string;
  location: string;
  theme: string;
  language: string;
  daily_reminder_enabled: boolean;
  progress_notice_enabled: boolean;
  badge_notice_enabled: boolean;
  weekly_report_enabled: boolean;
  two_factor_enabled: boolean;
  profile_public: boolean;
  learning_data_public: boolean;
};

const languageOptions = [
  { value: "zh-CN", label: "简体中文" },
  { value: "en-US", label: "English" },
  { value: "zh-TW", label: "繁體中文" },
];

const themeOptions = [
  { value: "light", label: "浅色模式" },
  { value: "dark", label: "深色模式" },
  { value: "system", label: "跟随系统" },
];

function buildSettingsForm(currentUser = getStoredCurrentUser()): SettingsFormState {
  const profile = currentUser?.profile;
  const settings = currentUser?.settings;

  return {
    display_name: profile?.display_name ?? "",
    phone: profile?.phone ?? "",
    email: profile?.email ?? "",
    learning_goal: profile?.learning_goal ?? "",
    location: profile?.location ?? "",
    theme: settings?.theme ?? "light",
    language: settings?.language ?? "zh-CN",
    daily_reminder_enabled: settings?.daily_reminder_enabled ?? true,
    progress_notice_enabled: settings?.progress_notice_enabled ?? true,
    badge_notice_enabled: settings?.badge_notice_enabled ?? false,
    weekly_report_enabled: settings?.weekly_report_enabled ?? true,
    two_factor_enabled: settings?.two_factor_enabled ?? false,
    profile_public: settings?.profile_public ?? true,
    learning_data_public: settings?.learning_data_public ?? false,
  };
}

function getAvatarUrl(currentUser = getStoredCurrentUser()) {
  return currentUser?.profile.avatar_url ?? "";
}

function initials(currentUser: CurrentUserResponse | null) {
  const value = currentUser?.profile.display_name || currentUser?.profile.username || "L";
  return value.trim().charAt(0).toUpperCase();
}

export function Settings() {
  const navigate = useNavigate();
  const [currentUser, setCurrentUser] = useState<CurrentUserResponse | null>(
    getStoredCurrentUser(),
  );
  const [formData, setFormData] = useState<SettingsFormState>(() => buildSettingsForm());
  const [savedForm, setSavedForm] = useState<SettingsFormState>(() => buildSettingsForm());
  const [avatarUrl, setAvatarUrl] = useState(() => getAvatarUrl());
  const [isLoading, setIsLoading] = useState(!getStoredCurrentUser());
  const [isSaving, setIsSaving] = useState(false);
  const [isUploadingAvatar, setIsUploadingAvatar] = useState(false);
  const [isLoggingOut, setIsLoggingOut] = useState(false);
  const [submitError, setSubmitError] = useState("");
  const [submitMessage, setSubmitMessage] = useState("");

  useEffect(() => {
    if (!hasSession()) {
      navigate("/login", { replace: true });
      return;
    }

    const load = async () => {
      setIsLoading(true);
      setSubmitError("");
      try {
        const me = await fetchCurrentUser();
        const nextForm = buildSettingsForm(me);
        setCurrentUser(me);
        setFormData(nextForm);
        setSavedForm(nextForm);
        setAvatarUrl(getAvatarUrl(me));
      } catch (error) {
        if (error instanceof ApiError && error.status === 401) {
          navigate("/login", { replace: true });
          return;
        }
        setSubmitError(error instanceof Error ? error.message : "加载设置失败");
      } finally {
        setIsLoading(false);
      }
    };

    void load();
  }, [navigate]);

  const handleInputChange = (
    event: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>,
  ) => {
    const { name, value, type } = event.target;
    const nextValue =
      type === "checkbox" && "checked" in event.target ? event.target.checked : value;

    setFormData((previous) => ({
      ...previous,
      [name]: nextValue,
    }));
    setSubmitError("");
    setSubmitMessage("");
  };

  const handleSave = async () => {
    setIsSaving(true);
    setSubmitError("");
    setSubmitMessage("");

    try {
      await updateMyProfile({
        display_name: formData.display_name.trim(),
        phone: formData.phone.trim() || null,
        email: formData.email.trim(),
        learning_goal: formData.learning_goal.trim() || null,
        location: formData.location.trim() || null,
      });

      const latest = await updateMySettings({
        theme: formData.theme,
        language: formData.language,
        daily_reminder_enabled: formData.daily_reminder_enabled,
        progress_notice_enabled: formData.progress_notice_enabled,
        badge_notice_enabled: formData.badge_notice_enabled,
        weekly_report_enabled: formData.weekly_report_enabled,
        two_factor_enabled: formData.two_factor_enabled,
        profile_public: formData.profile_public,
        learning_data_public: formData.learning_data_public,
      });

      const nextForm = buildSettingsForm(latest);
      setCurrentUser(latest);
      setFormData(nextForm);
      setSavedForm(nextForm);
      setAvatarUrl(getAvatarUrl(latest));
      setSubmitMessage("设置已保存");
    } catch (error) {
      if (error instanceof ApiError && error.status === 401) {
        navigate("/login", { replace: true });
        return;
      }
      setSubmitError(error instanceof Error ? error.message : "保存设置失败");
    } finally {
      setIsSaving(false);
    }
  };

  const handleAvatarChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    event.target.value = "";
    if (!file) {
      return;
    }

    setIsUploadingAvatar(true);
    setSubmitError("");
    setSubmitMessage("");

    try {
      const updatedUser = await uploadMyAvatar(file);
      const nextForm = buildSettingsForm(updatedUser);
      setCurrentUser(updatedUser);
      setFormData(nextForm);
      setSavedForm(nextForm);
      setAvatarUrl(getAvatarUrl(updatedUser));
      setSubmitMessage("头像已更新");
    } catch (error) {
      if (error instanceof ApiError && error.status === 401) {
        navigate("/login", { replace: true });
        return;
      }
      setSubmitError(error instanceof Error ? error.message : "头像上传失败");
    } finally {
      setIsUploadingAvatar(false);
    }
  };

  const handleReset = () => {
    setFormData(savedForm);
    setSubmitError("");
    setSubmitMessage("");
  };

  const handleLogout = async () => {
    setIsLoggingOut(true);
    try {
      await logoutCurrentUser();
      navigate("/login", { replace: true });
    } catch (error) {
      setSubmitError(error instanceof Error ? error.message : "退出登录失败");
    } finally {
      setIsLoggingOut(false);
    }
  };

  const progress = Math.min(
    100,
    Math.max(10, Math.round((currentUser?.profile.stats.total_learning_minutes ?? 0) / 10)),
  );

  return (
    <div className="h-full overflow-y-auto bg-gradient-to-br from-slate-50 via-white to-emerald-50 pb-28">
      <div className="mx-auto max-w-5xl p-8">
        <div className="mb-6">
          <h1 className="mb-2 text-2xl font-semibold text-gray-800">个人设置</h1>
          <p className="text-gray-600">头像、外观和语言设置现在都会保存并同步到当前账号。</p>
        </div>

        {(submitError || submitMessage) && (
          <div
            className={`mb-6 rounded-2xl px-4 py-3 text-sm ${
              submitError
                ? "border border-red-200 bg-red-50 text-red-600"
                : "border border-emerald-200 bg-emerald-50 text-emerald-700"
            }`}
          >
            {submitError || submitMessage}
          </div>
        )}

        <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
          <div className="lg:col-span-1">
            <div className="sticky top-8 rounded-xl bg-white p-6 shadow-sm">
              <div className="flex flex-col items-center">
                <div className="relative mb-4">
                  {avatarUrl ? (
                    <img
                      src={avatarUrl}
                      alt={currentUser?.profile.display_name || "avatar"}
                      className="h-24 w-24 rounded-full object-cover"
                    />
                  ) : (
                    <div className="flex h-24 w-24 items-center justify-center rounded-full bg-gradient-to-br from-emerald-400 to-teal-500 text-3xl font-bold text-white">
                      {initials(currentUser)}
                    </div>
                  )}
                  <label className="absolute bottom-0 right-0 flex h-8 w-8 cursor-pointer items-center justify-center rounded-full border-2 border-gray-100 bg-white shadow-lg transition-colors hover:bg-gray-50">
                    <input
                      type="file"
                      accept="image/png,image/jpeg,image/webp"
                      className="hidden"
                      onChange={handleAvatarChange}
                      disabled={isUploadingAvatar}
                    />
                    <Camera className="h-4 w-4 text-gray-600" />
                  </label>
                </div>
                <h3 className="mb-1 text-lg font-semibold text-gray-900">
                  {currentUser?.profile.display_name || "未命名用户"}
                </h3>
                <p className="mb-4 text-sm text-gray-500">{currentUser?.profile.email || "-"}</p>

                <div className="mt-4 w-full space-y-3">
                  <div className="flex items-center gap-3 text-sm text-gray-600">
                    <Mail className="h-4 w-4" />
                    <span>{formData.email || "未填写邮箱"}</span>
                  </div>
                  <div className="flex items-center gap-3 text-sm text-gray-600">
                    <Phone className="h-4 w-4" />
                    <span>{formData.phone || "未填写手机号"}</span>
                  </div>
                  <div className="flex items-center gap-3 text-sm text-gray-600">
                    <MapPin className="h-4 w-4" />
                    <span>{formData.location || "未填写所在地"}</span>
                  </div>
                </div>

                <div className="mt-6 w-full border-t border-gray-200 pt-6">
                  <div className="mb-2 text-xs text-gray-500">学习进度</div>
                  <div className="mb-2 h-2 w-full rounded-full bg-gray-100">
                    <div
                      className="h-2 rounded-full bg-gradient-to-r from-emerald-400 to-teal-500"
                      style={{ width: `${progress}%` }}
                    />
                  </div>
                  <div className="flex justify-between text-xs text-gray-600">
                    <span>累计学习</span>
                    <span className="font-semibold">
                      {currentUser?.profile.stats.total_learning_minutes ?? 0} 分钟
                    </span>
                  </div>
                </div>

                <button
                  type="button"
                  onClick={handleLogout}
                  disabled={isLoggingOut}
                  className="mt-6 w-full rounded-xl bg-gray-900 px-4 py-3 text-sm font-semibold text-white transition-colors hover:bg-gray-800 disabled:opacity-60"
                >
                  {isLoggingOut ? "退出中..." : "退出登录"}
                </button>
              </div>
            </div>
          </div>

          <div className="space-y-6 lg:col-span-2">
            <div className="rounded-xl bg-white p-6 shadow-sm">
              <div className="mb-6 flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-emerald-100">
                  <User className="h-5 w-5 text-emerald-600" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900">个人信息</h3>
              </div>
              <div className="space-y-4">
                <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
                  <div>
                    <label className="mb-2 block text-sm font-medium text-gray-700">昵称</label>
                    <input
                      type="text"
                      name="display_name"
                      value={formData.display_name}
                      onChange={handleInputChange}
                      disabled={isLoading}
                      className="w-full rounded-lg border border-gray-200 px-4 py-2.5 focus:border-transparent focus:outline-none focus:ring-2 focus:ring-emerald-500 disabled:opacity-60"
                    />
                  </div>
                  <div>
                    <label className="mb-2 block text-sm font-medium text-gray-700">手机号</label>
                    <input
                      type="text"
                      name="phone"
                      value={formData.phone}
                      onChange={handleInputChange}
                      disabled={isLoading}
                      className="w-full rounded-lg border border-gray-200 px-4 py-2.5 focus:border-transparent focus:outline-none focus:ring-2 focus:ring-emerald-500 disabled:opacity-60"
                    />
                  </div>
                </div>
                <div>
                  <label className="mb-2 block text-sm font-medium text-gray-700">邮箱</label>
                  <input
                    type="email"
                    name="email"
                    value={formData.email}
                    onChange={handleInputChange}
                    disabled={isLoading}
                    className="w-full rounded-lg border border-gray-200 px-4 py-2.5 focus:border-transparent focus:outline-none focus:ring-2 focus:ring-emerald-500 disabled:opacity-60"
                  />
                </div>
                <div>
                  <label className="mb-2 block text-sm font-medium text-gray-700">所在地</label>
                  <input
                    type="text"
                    name="location"
                    value={formData.location}
                    onChange={handleInputChange}
                    disabled={isLoading}
                    className="w-full rounded-lg border border-gray-200 px-4 py-2.5 focus:border-transparent focus:outline-none focus:ring-2 focus:ring-emerald-500 disabled:opacity-60"
                  />
                </div>
                <div>
                  <label className="mb-2 block text-sm font-medium text-gray-700">学习目标</label>
                  <textarea
                    name="learning_goal"
                    value={formData.learning_goal}
                    onChange={handleInputChange}
                    rows={3}
                    disabled={isLoading}
                    className="w-full resize-none rounded-lg border border-gray-200 px-4 py-2.5 focus:border-transparent focus:outline-none focus:ring-2 focus:ring-emerald-500 disabled:opacity-60"
                  />
                </div>
              </div>
            </div>

            <div className="rounded-xl bg-white p-6 shadow-sm">
              <div className="mb-6 flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-blue-100">
                  <Bell className="h-5 w-5 text-blue-600" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900">通知设置</h3>
              </div>
              <div className="space-y-4">
                {[
                  {
                    key: "daily_reminder_enabled",
                    title: "学习提醒",
                    desc: "每日固定时间提醒学习",
                  },
                  {
                    key: "progress_notice_enabled",
                    title: "进度更新",
                    desc: "学习进度变化时发送通知",
                  },
                  {
                    key: "badge_notice_enabled",
                    title: "成就徽章",
                    desc: "获得新成就时通知",
                  },
                  {
                    key: "weekly_report_enabled",
                    title: "周报推送",
                    desc: "每周学习总结提醒",
                  },
                ].map((item) => (
                  <div
                    key={item.key}
                    className="flex items-center justify-between rounded-lg bg-gray-50 p-4"
                  >
                    <div>
                      <p className="font-medium text-gray-900">{item.title}</p>
                      <p className="text-sm text-gray-600">{item.desc}</p>
                    </div>
                    <label className="relative inline-flex cursor-pointer items-center">
                      <input
                        type="checkbox"
                        name={item.key}
                        checked={Boolean(
                          formData[item.key as keyof SettingsFormState] as boolean | undefined,
                        )}
                        onChange={handleInputChange}
                        className="peer sr-only"
                      />
                      <div className="h-6 w-11 rounded-full bg-gray-200 after:absolute after:left-[2px] after:top-[2px] after:h-5 after:w-5 after:rounded-full after:border after:border-gray-300 after:bg-white after:transition-all after:content-[''] peer-checked:bg-emerald-500 peer-checked:after:translate-x-full peer-checked:after:border-white" />
                    </label>
                  </div>
                ))}
              </div>
            </div>

            <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
              <div className="rounded-xl bg-white p-6 shadow-sm">
                <div className="mb-6 flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-purple-100">
                    <Palette className="h-5 w-5 text-purple-600" />
                  </div>
                  <h3 className="text-lg font-semibold text-gray-900">外观</h3>
                </div>
                <div>
                  <label className="mb-2 block text-sm font-medium text-gray-700">主题模式</label>
                  <select
                    name="theme"
                    value={formData.theme}
                    onChange={handleInputChange}
                    className="w-full rounded-lg border border-gray-200 bg-white px-4 py-2.5 focus:border-transparent focus:outline-none focus:ring-2 focus:ring-emerald-500"
                  >
                    {themeOptions.map((option) => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="rounded-xl bg-white p-6 shadow-sm">
                <div className="mb-6 flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-orange-100">
                    <Globe className="h-5 w-5 text-orange-600" />
                  </div>
                  <h3 className="text-lg font-semibold text-gray-900">语言</h3>
                </div>
                <div>
                  <label className="mb-2 block text-sm font-medium text-gray-700">界面语言</label>
                  <select
                    name="language"
                    value={formData.language}
                    onChange={handleInputChange}
                    className="w-full rounded-lg border border-gray-200 bg-white px-4 py-2.5 focus:border-transparent focus:outline-none focus:ring-2 focus:ring-emerald-500"
                  >
                    {languageOptions.map((option) => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
            </div>

            <div className="rounded-xl bg-white p-6 shadow-sm">
              <div className="mb-6 flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-red-100">
                  <Lock className="h-5 w-5 text-red-600" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900">安全与隐私</h3>
              </div>
              <div className="space-y-4">
                {[
                  {
                    key: "two_factor_enabled",
                    title: "双重验证",
                    desc: "开启后登录安全性更高",
                  },
                  {
                    key: "profile_public",
                    title: "公开个人主页",
                    desc: "允许其他用户查看你的主页信息",
                  },
                  {
                    key: "learning_data_public",
                    title: "公开学习数据",
                    desc: "允许展示你的部分学习成果",
                  },
                ].map((item) => (
                  <div
                    key={item.key}
                    className="flex items-center justify-between rounded-lg bg-gray-50 p-4"
                  >
                    <div>
                      <p className="font-medium text-gray-900">{item.title}</p>
                      <p className="text-sm text-gray-600">{item.desc}</p>
                    </div>
                    <label className="relative inline-flex cursor-pointer items-center">
                      <input
                        type="checkbox"
                        name={item.key}
                        checked={Boolean(
                          formData[item.key as keyof SettingsFormState] as boolean | undefined,
                        )}
                        onChange={handleInputChange}
                        className="peer sr-only"
                      />
                      <div className="h-6 w-11 rounded-full bg-gray-200 after:absolute after:left-[2px] after:top-[2px] after:h-5 after:w-5 after:rounded-full after:border after:border-gray-300 after:bg-white after:transition-all after:content-[''] peer-checked:bg-emerald-500 peer-checked:after:translate-x-full peer-checked:after:border-white" />
                    </label>
                  </div>
                ))}
              </div>
            </div>

            <div className="flex justify-end gap-3">
              <button
                type="button"
                onClick={handleReset}
                className="rounded-lg bg-gray-100 px-6 py-2.5 font-medium text-gray-700 transition-colors hover:bg-gray-200"
              >
                取消
              </button>
              <button
                type="button"
                onClick={handleSave}
                disabled={isSaving || isLoading || isUploadingAvatar}
                className="rounded-lg bg-emerald-500 px-6 py-2.5 font-medium text-white transition-colors hover:bg-emerald-600 disabled:opacity-60"
              >
                {isSaving ? "保存中..." : "保存更改"}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

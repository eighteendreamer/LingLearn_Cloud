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
  const [isLoading, setIsLoading] = useState(!getStoredCurrentUser());
  const [isSaving, setIsSaving] = useState(false);
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
      const profileResult = await updateMyProfile({
        display_name: formData.display_name.trim(),
        phone: formData.phone.trim() || null,
        email: formData.email.trim(),
        learning_goal: formData.learning_goal.trim() || null,
        location: formData.location.trim() || null,
      });

      const settingsResult = await updateMySettings({
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

      const latest = settingsResult ?? profileResult;
      const nextForm = buildSettingsForm(latest);
      setCurrentUser(latest);
      setFormData(nextForm);
      setSavedForm(nextForm);
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
      <div className="max-w-5xl mx-auto p-8">
      <div className="mb-6">
        <h1 className="text-2xl font-semibold text-gray-800 mb-2">个人设置</h1>
        <p className="text-gray-600">这里已经接入后端接口，保存后会同步更新你的账号配置。</p>
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

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1">
          <div className="bg-white rounded-xl p-6 shadow-sm sticky top-8">
            <div className="flex flex-col items-center">
              <div className="relative mb-4">
                <div className="w-24 h-24 bg-gradient-to-br from-emerald-400 to-teal-500 rounded-full flex items-center justify-center text-white text-3xl font-bold">
                  {initials(currentUser)}
                </div>
                <button
                  type="button"
                  className="absolute bottom-0 right-0 w-8 h-8 bg-white rounded-full shadow-lg flex items-center justify-center border-2 border-gray-100 hover:bg-gray-50 transition-colors"
                >
                  <Camera className="w-4 h-4 text-gray-600" />
                </button>
              </div>
              <h3 className="font-semibold text-gray-900 text-lg mb-1">
                {currentUser?.profile.display_name || "未命名用户"}
              </h3>
              <p className="text-sm text-gray-500 mb-4">{currentUser?.profile.email || "-"}</p>

              <div className="w-full space-y-3 mt-4">
                <div className="flex items-center gap-3 text-sm text-gray-600">
                  <Mail className="w-4 h-4" />
                  <span>{formData.email || "未填写邮箱"}</span>
                </div>
                <div className="flex items-center gap-3 text-sm text-gray-600">
                  <Phone className="w-4 h-4" />
                  <span>{formData.phone || "未填写手机号"}</span>
                </div>
                <div className="flex items-center gap-3 text-sm text-gray-600">
                  <MapPin className="w-4 h-4" />
                  <span>{formData.location || "未填写所在地"}</span>
                </div>
              </div>

              <div className="w-full mt-6 pt-6 border-t border-gray-200">
                <div className="text-xs text-gray-500 mb-2">学习进度</div>
                <div className="w-full bg-gray-100 rounded-full h-2 mb-2">
                  <div
                    className="bg-gradient-to-r from-emerald-400 to-teal-500 h-2 rounded-full"
                    style={{ width: `${progress}%` }}
                  ></div>
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
                className="mt-6 w-full rounded-xl bg-gray-900 px-4 py-3 text-sm font-semibold text-white hover:bg-gray-800 transition-colors disabled:opacity-60"
              >
                {isLoggingOut ? "退出中..." : "退出登录"}
              </button>
            </div>
          </div>
        </div>

        <div className="lg:col-span-2 space-y-6">
          <div className="bg-white rounded-xl p-6 shadow-sm">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-10 h-10 bg-emerald-100 rounded-lg flex items-center justify-center">
                <User className="w-5 h-5 text-emerald-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900">个人信息</h3>
            </div>
            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">昵称</label>
                  <input
                    type="text"
                    name="display_name"
                    value={formData.display_name}
                    onChange={handleInputChange}
                    disabled={isLoading}
                    className="w-full px-4 py-2.5 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent disabled:opacity-60"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">手机号</label>
                  <input
                    type="text"
                    name="phone"
                    value={formData.phone}
                    onChange={handleInputChange}
                    disabled={isLoading}
                    className="w-full px-4 py-2.5 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent disabled:opacity-60"
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">邮箱</label>
                <input
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleInputChange}
                  disabled={isLoading}
                  className="w-full px-4 py-2.5 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent disabled:opacity-60"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">所在地</label>
                <input
                  type="text"
                  name="location"
                  value={formData.location}
                  onChange={handleInputChange}
                  disabled={isLoading}
                  className="w-full px-4 py-2.5 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent disabled:opacity-60"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">学习目标</label>
                <textarea
                  name="learning_goal"
                  value={formData.learning_goal}
                  onChange={handleInputChange}
                  rows={3}
                  disabled={isLoading}
                  className="w-full px-4 py-2.5 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent resize-none disabled:opacity-60"
                />
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl p-6 shadow-sm">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                <Bell className="w-5 h-5 text-blue-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900">通知设置</h3>
            </div>
            <div className="space-y-4">
              {[
                {
                  key: "daily_reminder_enabled",
                  title: "学习提醒",
                  desc: "每日学习时间提醒",
                },
                {
                  key: "progress_notice_enabled",
                  title: "进度更新",
                  desc: "学习进度变化通知",
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
                  className="flex items-center justify-between p-4 bg-gray-50 rounded-lg"
                >
                  <div>
                    <p className="font-medium text-gray-900">{item.title}</p>
                    <p className="text-sm text-gray-600">{item.desc}</p>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      name={item.key}
                      checked={Boolean(
                        formData[item.key as keyof SettingsFormState] as boolean | undefined,
                      )}
                      onChange={handleInputChange}
                      className="sr-only peer"
                    />
                    <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-emerald-200 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-emerald-500"></div>
                  </label>
                </div>
              ))}
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-white rounded-xl p-6 shadow-sm">
              <div className="flex items-center gap-3 mb-6">
                <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
                  <Palette className="w-5 h-5 text-purple-600" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900">外观</h3>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">主题模式</label>
                <select
                  name="theme"
                  value={formData.theme}
                  onChange={handleInputChange}
                  className="w-full px-4 py-2.5 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent bg-white"
                >
                  <option value="light">浅色模式</option>
                  <option value="dark">深色模式</option>
                  <option value="system">跟随系统</option>
                </select>
              </div>
            </div>

            <div className="bg-white rounded-xl p-6 shadow-sm">
              <div className="flex items-center gap-3 mb-6">
                <div className="w-10 h-10 bg-orange-100 rounded-lg flex items-center justify-center">
                  <Globe className="w-5 h-5 text-orange-600" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900">语言</h3>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">界面语言</label>
                <select
                  name="language"
                  value={formData.language}
                  onChange={handleInputChange}
                  className="w-full px-4 py-2.5 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent bg-white"
                >
                  <option value="zh-CN">简体中文</option>
                  <option value="en-US">English</option>
                  <option value="zh-TW">繁體中文</option>
                </select>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl p-6 shadow-sm">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-10 h-10 bg-red-100 rounded-lg flex items-center justify-center">
                <Lock className="w-5 h-5 text-red-600" />
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
                  className="flex items-center justify-between p-4 bg-gray-50 rounded-lg"
                >
                  <div>
                    <p className="font-medium text-gray-900">{item.title}</p>
                    <p className="text-sm text-gray-600">{item.desc}</p>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      name={item.key}
                      checked={Boolean(
                        formData[item.key as keyof SettingsFormState] as boolean | undefined,
                      )}
                      onChange={handleInputChange}
                      className="sr-only peer"
                    />
                    <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-emerald-200 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-emerald-500"></div>
                  </label>
                </div>
              ))}
            </div>
          </div>

          <div className="flex justify-end gap-3">
            <button
              type="button"
              onClick={handleReset}
              className="px-6 py-2.5 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors font-medium"
            >
              取消
            </button>
            <button
              type="button"
              onClick={handleSave}
              disabled={isSaving || isLoading}
              className="px-6 py-2.5 bg-emerald-500 text-white rounded-lg hover:bg-emerald-600 transition-colors font-medium disabled:opacity-60"
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

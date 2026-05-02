import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router";
import {
  ArrowLeft,
  Briefcase,
  Calendar,
  Camera,
  Mail,
  MapPin,
  Phone,
  Save,
  User,
} from "lucide-react";

import { ApiError } from "../lib/api";
import { fetchCurrentUser, updateMyProfile, uploadMyAvatar } from "../lib/account";
import { getStoredCurrentUser, hasSession } from "../lib/session";

type ProfileFormState = {
  display_name: string;
  bio: string;
  email: string;
  phone: string;
  location: string;
  profession: string;
  birthday: string;
  learning_goal: string;
};

function createFormState(currentUser = getStoredCurrentUser()): ProfileFormState {
  const profile = currentUser?.profile;
  return {
    display_name: profile?.display_name ?? "",
    bio: profile?.bio ?? "",
    email: profile?.email ?? "",
    phone: profile?.phone ?? "",
    location: profile?.location ?? "",
    profession: profile?.profession ?? "",
    birthday: profile?.birthday ?? "",
    learning_goal: profile?.learning_goal ?? "",
  };
}

function getAvatarUrl(currentUser = getStoredCurrentUser()) {
  return currentUser?.profile.avatar_url ?? "";
}

export function EditProfile() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState<ProfileFormState>(() => createFormState());
  const [avatarUrl, setAvatarUrl] = useState(() => getAvatarUrl());
  const [isLoading, setIsLoading] = useState(!getStoredCurrentUser());
  const [isSaving, setIsSaving] = useState(false);
  const [isUploadingAvatar, setIsUploadingAvatar] = useState(false);
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
        const currentUser = await fetchCurrentUser();
        setFormData(createFormState(currentUser));
        setAvatarUrl(getAvatarUrl(currentUser));
      } catch (error) {
        if (error instanceof ApiError && error.status === 401) {
          navigate("/login", { replace: true });
          return;
        }
        setSubmitError(error instanceof Error ? error.message : "加载资料失败");
      } finally {
        setIsLoading(false);
      }
    };

    void load();
  }, [navigate]);

  const handleInputChange = (
    event: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>,
  ) => {
    const { name, value } = event.target;
    setFormData((previous) => ({ ...previous, [name]: value }));
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
        bio: formData.bio.trim() || null,
        email: formData.email.trim(),
        phone: formData.phone.trim() || null,
        location: formData.location.trim() || null,
        profession: formData.profession.trim() || null,
        birthday: formData.birthday || null,
        learning_goal: formData.learning_goal.trim() || null,
      });
      navigate("/profile", { replace: true });
    } catch (error) {
      if (error instanceof ApiError && error.status === 401) {
        navigate("/login", { replace: true });
        return;
      }
      setSubmitError(error instanceof Error ? error.message : "保存资料失败");
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
      const currentUser = await uploadMyAvatar(file);
      setFormData(createFormState(currentUser));
      setAvatarUrl(getAvatarUrl(currentUser));
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

  return (
    <div className="h-screen overflow-y-auto bg-gradient-to-br from-blue-50 via-white to-emerald-50 pb-20">
      <div className="sticky top-0 z-10 flex items-center gap-3 border-b border-gray-200 bg-white/95 p-4 shadow-sm backdrop-blur-lg">
        <Link to="/profile">
          <ArrowLeft className="h-6 w-6 text-gray-700" />
        </Link>
        <div className="flex-1">
          <h1 className="text-lg font-semibold text-gray-900">编辑资料</h1>
          <p className="text-xs text-gray-600">保存后会同步更新到用户中心</p>
        </div>
        <button
          onClick={handleSave}
          disabled={isLoading || isSaving || isUploadingAvatar}
          className="flex items-center gap-2 rounded-lg bg-gradient-to-r from-emerald-500 to-teal-500 px-4 py-2 text-sm font-bold text-white transition-all hover:shadow-lg disabled:opacity-60"
        >
          <Save className="h-4 w-4" />
          {isSaving ? "保存中..." : "保存"}
        </button>
      </div>

      <div className="mx-auto max-w-2xl p-6">
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

        <div className="mb-6 rounded-2xl bg-white p-6 shadow-md">
          <div className="flex items-center gap-6">
            <div className="relative">
              {avatarUrl ? (
                <img
                  src={avatarUrl}
                  alt={formData.display_name || "avatar"}
                  className="h-20 w-20 rounded-full object-cover shadow-lg"
                />
              ) : (
                <div className="flex h-20 w-20 items-center justify-center rounded-full bg-gradient-to-br from-emerald-500 to-teal-500 text-2xl font-bold text-white shadow-lg">
                  {formData.display_name.trim().charAt(0).toUpperCase() || "L"}
                </div>
              )}
              <label className="absolute -bottom-1 -right-1 flex h-8 w-8 cursor-pointer items-center justify-center rounded-full border-2 border-emerald-500 bg-white shadow-md transition-colors hover:bg-emerald-50">
                <input
                  type="file"
                  accept="image/png,image/jpeg,image/webp"
                  className="hidden"
                  onChange={handleAvatarChange}
                  disabled={isUploadingAvatar}
                />
                <Camera className="h-4 w-4 text-emerald-600" />
              </label>
            </div>
            <div>
              <h3 className="mb-1 font-semibold text-gray-900">头像上传</h3>
              <p className="text-sm text-gray-600">
                {isUploadingAvatar
                  ? "头像上传中..."
                  : "头像会先上传到 MinIO，然后自动绑定到当前用户资料。"}
              </p>
            </div>
          </div>
        </div>

        <div className="mb-6 rounded-2xl bg-white p-6 shadow-md">
          <h3 className="mb-4 flex items-center gap-2 font-semibold text-gray-900">
            <User className="h-5 w-5 text-emerald-500" />
            基本信息
          </h3>
          <div className="space-y-4">
            <div>
              <label className="mb-2 block text-sm font-medium text-gray-700">昵称</label>
              <input
                type="text"
                name="display_name"
                value={formData.display_name}
                onChange={handleInputChange}
                placeholder="请输入昵称"
                disabled={isLoading}
                className="w-full rounded-xl border border-gray-200 bg-gray-50 px-4 py-3 text-gray-900 placeholder-gray-400 transition-all focus:border-transparent focus:outline-none focus:ring-2 focus:ring-emerald-500 disabled:opacity-60"
              />
            </div>

            <div>
              <label className="mb-2 block text-sm font-medium text-gray-700">个人简介</label>
              <textarea
                name="bio"
                value={formData.bio}
                onChange={handleInputChange}
                placeholder="介绍一下你的学习方向和兴趣"
                disabled={isLoading}
                className="w-full resize-none rounded-xl border border-gray-200 bg-gray-50 px-4 py-3 text-gray-900 placeholder-gray-400 transition-all focus:border-transparent focus:outline-none focus:ring-2 focus:ring-emerald-500 disabled:opacity-60"
                rows={3}
              />
            </div>

            <div>
              <label className="mb-2 block text-sm font-medium text-gray-700">职业</label>
              <div className="relative">
                <Briefcase className="absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-gray-400" />
                <input
                  type="text"
                  name="profession"
                  value={formData.profession}
                  onChange={handleInputChange}
                  placeholder="请输入职业"
                  disabled={isLoading}
                  className="w-full rounded-xl border border-gray-200 bg-gray-50 py-3 pl-12 pr-4 text-gray-900 placeholder-gray-400 transition-all focus:border-transparent focus:outline-none focus:ring-2 focus:ring-emerald-500 disabled:opacity-60"
                />
              </div>
            </div>

            <div>
              <label className="mb-2 block text-sm font-medium text-gray-700">学习目标</label>
              <textarea
                name="learning_goal"
                value={formData.learning_goal}
                onChange={handleInputChange}
                placeholder="例如：一个月内完成前后端项目实战"
                disabled={isLoading}
                className="w-full resize-none rounded-xl border border-gray-200 bg-gray-50 px-4 py-3 text-gray-900 placeholder-gray-400 transition-all focus:border-transparent focus:outline-none focus:ring-2 focus:ring-emerald-500 disabled:opacity-60"
                rows={3}
              />
            </div>
          </div>
        </div>

        <div className="mb-6 rounded-2xl bg-white p-6 shadow-md">
          <h3 className="mb-4 flex items-center gap-2 font-semibold text-gray-900">
            <Mail className="h-5 w-5 text-emerald-500" />
            联系方式
          </h3>
          <div className="space-y-4">
            <div>
              <label className="mb-2 block text-sm font-medium text-gray-700">邮箱</label>
              <div className="relative">
                <Mail className="absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-gray-400" />
                <input
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleInputChange}
                  placeholder="请输入邮箱"
                  disabled={isLoading}
                  className="w-full rounded-xl border border-gray-200 bg-gray-50 py-3 pl-12 pr-4 text-gray-900 placeholder-gray-400 transition-all focus:border-transparent focus:outline-none focus:ring-2 focus:ring-emerald-500 disabled:opacity-60"
                />
              </div>
            </div>

            <div>
              <label className="mb-2 block text-sm font-medium text-gray-700">手机号</label>
              <div className="relative">
                <Phone className="absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-gray-400" />
                <input
                  type="tel"
                  name="phone"
                  value={formData.phone}
                  onChange={handleInputChange}
                  placeholder="请输入手机号"
                  disabled={isLoading}
                  className="w-full rounded-xl border border-gray-200 bg-gray-50 py-3 pl-12 pr-4 text-gray-900 placeholder-gray-400 transition-all focus:border-transparent focus:outline-none focus:ring-2 focus:ring-emerald-500 disabled:opacity-60"
                />
              </div>
            </div>

            <div>
              <label className="mb-2 block text-sm font-medium text-gray-700">所在地</label>
              <div className="relative">
                <MapPin className="absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-gray-400" />
                <input
                  type="text"
                  name="location"
                  value={formData.location}
                  onChange={handleInputChange}
                  placeholder="请输入所在地"
                  disabled={isLoading}
                  className="w-full rounded-xl border border-gray-200 bg-gray-50 py-3 pl-12 pr-4 text-gray-900 placeholder-gray-400 transition-all focus:border-transparent focus:outline-none focus:ring-2 focus:ring-emerald-500 disabled:opacity-60"
                />
              </div>
            </div>
          </div>
        </div>

        <div className="rounded-2xl bg-white p-6 shadow-md">
          <h3 className="mb-4 flex items-center gap-2 font-semibold text-gray-900">
            <Calendar className="h-5 w-5 text-emerald-500" />
            其他信息
          </h3>
          <div>
            <label className="mb-2 block text-sm font-medium text-gray-700">生日</label>
            <div className="relative">
              <Calendar className="absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-gray-400" />
              <input
                type="date"
                name="birthday"
                value={formData.birthday}
                onChange={handleInputChange}
                disabled={isLoading}
                className="w-full rounded-xl border border-gray-200 bg-gray-50 py-3 pl-12 pr-4 text-gray-900 transition-all focus:border-transparent focus:outline-none focus:ring-2 focus:ring-emerald-500 disabled:opacity-60"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

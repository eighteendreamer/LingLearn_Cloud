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
import { fetchCurrentUser, updateMyProfile } from "../lib/account";
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

export function EditProfile() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState<ProfileFormState>(() => createFormState());
  const [isLoading, setIsLoading] = useState(!getStoredCurrentUser());
  const [isSaving, setIsSaving] = useState(false);
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
      const currentUser = await updateMyProfile({
        display_name: formData.display_name.trim(),
        bio: formData.bio.trim() || null,
        email: formData.email.trim(),
        phone: formData.phone.trim() || null,
        location: formData.location.trim() || null,
        profession: formData.profession.trim() || null,
        birthday: formData.birthday || null,
        learning_goal: formData.learning_goal.trim() || null,
      });
      setFormData(createFormState(currentUser));
      setSubmitMessage("资料已同步到后端");
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

  return (
    <div className="h-screen overflow-y-auto bg-gradient-to-br from-blue-50 via-white to-emerald-50 pb-20">
      <div className="sticky top-0 z-10 flex items-center gap-3 p-4 bg-white/95 backdrop-blur-lg border-b border-gray-200 shadow-sm">
        <Link to="/profile">
          <ArrowLeft className="w-6 h-6 text-gray-700" />
        </Link>
        <div className="flex-1">
          <h1 className="text-lg font-semibold text-gray-900">编辑资料</h1>
          <p className="text-xs text-gray-600">修改后会实时同步到用户中心</p>
        </div>
        <button
          onClick={handleSave}
          disabled={isLoading || isSaving}
          className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-emerald-500 to-teal-500 text-white rounded-lg text-sm font-bold hover:shadow-lg transition-all disabled:opacity-60"
        >
          <Save className="w-4 h-4" />
          {isSaving ? "保存中..." : "保存"}
        </button>
      </div>

      <div className="p-6 max-w-2xl mx-auto">
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

        <div className="bg-white rounded-2xl p-6 shadow-md mb-6">
          <div className="flex items-center gap-6">
            <div className="relative">
              <div className="w-20 h-20 rounded-full bg-gradient-to-br from-emerald-500 to-teal-500 flex items-center justify-center text-white text-2xl font-bold shadow-lg">
                {formData.display_name.trim().charAt(0).toUpperCase() || "L"}
              </div>
              <button
                type="button"
                className="absolute -bottom-1 -right-1 w-8 h-8 bg-white rounded-full shadow-md flex items-center justify-center border-2 border-emerald-500 hover:bg-emerald-50 transition-colors"
              >
                <Camera className="w-4 h-4 text-emerald-600" />
              </button>
            </div>
            <div>
              <h3 className="text-gray-900 font-semibold mb-1">头像上传待接入</h3>
              <p className="text-gray-600 text-sm">
                资料接口已经联通，头像后续接存储服务后可以直接补上。
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-2xl p-6 shadow-md mb-6">
          <h3 className="text-gray-900 font-semibold mb-4 flex items-center gap-2">
            <User className="w-5 h-5 text-emerald-500" />
            基本信息
          </h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">昵称</label>
              <input
                type="text"
                name="display_name"
                value={formData.display_name}
                onChange={handleInputChange}
                placeholder="请输入昵称"
                disabled={isLoading}
                className="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent transition-all disabled:opacity-60"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">个人简介</label>
              <textarea
                name="bio"
                value={formData.bio}
                onChange={handleInputChange}
                placeholder="介绍一下你的学习方向和兴趣"
                disabled={isLoading}
                className="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent transition-all resize-none disabled:opacity-60"
                rows={3}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">职业</label>
              <div className="relative">
                <Briefcase className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="text"
                  name="profession"
                  value={formData.profession}
                  onChange={handleInputChange}
                  placeholder="请输入职业"
                  disabled={isLoading}
                  className="w-full pl-12 pr-4 py-3 bg-gray-50 border border-gray-200 rounded-xl text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent transition-all disabled:opacity-60"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">学习目标</label>
              <textarea
                name="learning_goal"
                value={formData.learning_goal}
                onChange={handleInputChange}
                placeholder="例如：3 个月内完成前后端项目实战"
                disabled={isLoading}
                className="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent transition-all resize-none disabled:opacity-60"
                rows={3}
              />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-2xl p-6 shadow-md mb-6">
          <h3 className="text-gray-900 font-semibold mb-4 flex items-center gap-2">
            <Mail className="w-5 h-5 text-emerald-500" />
            联系方式
          </h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">邮箱</label>
              <div className="relative">
                <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleInputChange}
                  placeholder="请输入邮箱"
                  disabled={isLoading}
                  className="w-full pl-12 pr-4 py-3 bg-gray-50 border border-gray-200 rounded-xl text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent transition-all disabled:opacity-60"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">手机号</label>
              <div className="relative">
                <Phone className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="tel"
                  name="phone"
                  value={formData.phone}
                  onChange={handleInputChange}
                  placeholder="请输入手机号"
                  disabled={isLoading}
                  className="w-full pl-12 pr-4 py-3 bg-gray-50 border border-gray-200 rounded-xl text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent transition-all disabled:opacity-60"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">所在地</label>
              <div className="relative">
                <MapPin className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="text"
                  name="location"
                  value={formData.location}
                  onChange={handleInputChange}
                  placeholder="请输入所在地"
                  disabled={isLoading}
                  className="w-full pl-12 pr-4 py-3 bg-gray-50 border border-gray-200 rounded-xl text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent transition-all disabled:opacity-60"
                />
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-2xl p-6 shadow-md">
          <h3 className="text-gray-900 font-semibold mb-4 flex items-center gap-2">
            <Calendar className="w-5 h-5 text-emerald-500" />
            其他信息
          </h3>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">生日</label>
            <div className="relative">
              <Calendar className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="date"
                name="birthday"
                value={formData.birthday}
                onChange={handleInputChange}
                disabled={isLoading}
                className="w-full pl-12 pr-4 py-3 bg-gray-50 border border-gray-200 rounded-xl text-gray-900 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent transition-all disabled:opacity-60"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

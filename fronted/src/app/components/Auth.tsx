import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router";
import { Eye, EyeOff, GraduationCap, Lock, Mail, User } from "lucide-react";

import { ApiError } from "../lib/api";
import { loginWithPassword, registerWithPassword } from "../lib/account";
import { hasSession } from "../lib/session";

export function Auth() {
  const [isLogin, setIsLogin] = useState(true);
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [formData, setFormData] = useState({
    account: "",
    username: "",
    email: "",
    password: "",
    confirmPassword: "",
  });
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [submitError, setSubmitError] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    if (hasSession()) {
      navigate("/profile", { replace: true });
    }
  }, [navigate]);

  const validateForm = () => {
    const nextErrors: Record<string, string> = {};

    if (isLogin) {
      if (!formData.account.trim()) {
        nextErrors.account = "请输入用户名或邮箱";
      }
    } else {
      if (!formData.username.trim()) {
        nextErrors.username = "请输入用户名";
      } else if (formData.username.trim().length < 3) {
        nextErrors.username = "用户名至少 3 个字符";
      }

      if (!formData.email.trim()) {
        nextErrors.email = "请输入邮箱";
      } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
        nextErrors.email = "请输入有效的邮箱地址";
      }
    }

    if (!formData.password) {
      nextErrors.password = "请输入密码";
    } else if (formData.password.length < 6) {
      nextErrors.password = "密码至少 6 个字符";
    }

    if (!isLogin) {
      if (!formData.confirmPassword) {
        nextErrors.confirmPassword = "请再次输入密码";
      } else if (formData.password !== formData.confirmPassword) {
        nextErrors.confirmPassword = "两次输入的密码不一致";
      }
    }

    setErrors(nextErrors);
    return Object.keys(nextErrors).length === 0;
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setSubmitError("");

    if (!validateForm()) {
      return;
    }

    setIsLoading(true);
    try {
      if (isLogin) {
        await loginWithPassword({
          account: formData.account.trim(),
          password: formData.password,
        });
      } else {
        const username = formData.username.trim();
        await registerWithPassword({
          username,
          email: formData.email.trim(),
          password: formData.password,
          display_name: username,
        });
      }
      navigate("/profile", { replace: true });
    } catch (error) {
      if (error instanceof ApiError) {
        setSubmitError(error.message);
      } else {
        setSubmitError("请求失败，请稍后重试");
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = event.target;
    setFormData((previous) => ({ ...previous, [name]: value }));
    setSubmitError("");

    if (errors[name]) {
      setErrors((previous) => ({ ...previous, [name]: "" }));
    }
  };

  const switchMode = () => {
    setIsLogin((previous) => !previous);
    setErrors({});
    setSubmitError("");
    setFormData({
      account: "",
      username: "",
      email: "",
      password: "",
      confirmPassword: "",
    });
  };

  return (
    <div className="min-h-screen overflow-y-auto bg-gradient-to-br from-emerald-400 via-teal-400 to-blue-500 px-4 py-8 md:flex md:items-center md:justify-center">
      <div className="mx-auto w-full max-w-md">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-white rounded-2xl shadow-lg mb-4 hover:scale-105 transition-transform">
            <GraduationCap className="w-10 h-10 text-emerald-600" />
          </div>
          <h1 className="text-3xl font-bold text-white mb-2">智能学习平台</h1>
          <p className="text-emerald-100">登录后即可同步你的学习档案与个性化设置</p>
        </div>

        <div className="bg-white rounded-3xl shadow-2xl p-8">
          <div className="flex mb-8 bg-gray-100 rounded-xl p-1">
            <button
              onClick={() => setIsLogin(true)}
              className={`flex-1 py-2.5 rounded-lg text-sm font-medium transition-all ${
                isLogin
                  ? "bg-gradient-to-r from-emerald-500 to-teal-500 text-white shadow-md"
                  : "text-gray-600 hover:text-gray-900"
              }`}
              type="button"
            >
              登录
            </button>
            <button
              onClick={() => setIsLogin(false)}
              className={`flex-1 py-2.5 rounded-lg text-sm font-medium transition-all ${
                !isLogin
                  ? "bg-gradient-to-r from-emerald-500 to-teal-500 text-white shadow-md"
                  : "text-gray-600 hover:text-gray-900"
              }`}
              type="button"
            >
              注册
            </button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-5">
            {isLogin ? (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  账号
                </label>
                <div className="relative">
                  <User className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <input
                    type="text"
                    name="account"
                    value={formData.account}
                    onChange={handleInputChange}
                    placeholder="请输入用户名或邮箱"
                    className={`w-full pl-12 pr-4 py-3.5 bg-gray-50 border rounded-xl text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent transition-all ${
                      errors.account ? "border-red-500" : "border-gray-200"
                    }`}
                  />
                </div>
                {errors.account && (
                  <p className="mt-1.5 text-sm text-red-500">{errors.account}</p>
                )}
              </div>
            ) : (
              <>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    用户名
                  </label>
                  <div className="relative">
                    <User className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                    <input
                      type="text"
                      name="username"
                      value={formData.username}
                      onChange={handleInputChange}
                      placeholder="请输入用户名"
                      className={`w-full pl-12 pr-4 py-3.5 bg-gray-50 border rounded-xl text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent transition-all ${
                        errors.username ? "border-red-500" : "border-gray-200"
                      }`}
                    />
                  </div>
                  {errors.username && (
                    <p className="mt-1.5 text-sm text-red-500">{errors.username}</p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    邮箱
                  </label>
                  <div className="relative">
                    <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                    <input
                      type="email"
                      name="email"
                      value={formData.email}
                      onChange={handleInputChange}
                      placeholder="请输入邮箱"
                      className={`w-full pl-12 pr-4 py-3.5 bg-gray-50 border rounded-xl text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent transition-all ${
                        errors.email ? "border-red-500" : "border-gray-200"
                      }`}
                    />
                  </div>
                  {errors.email && (
                    <p className="mt-1.5 text-sm text-red-500">{errors.email}</p>
                  )}
                </div>
              </>
            )}

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                密码
              </label>
              <div className="relative">
                <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type={showPassword ? "text" : "password"}
                  name="password"
                  value={formData.password}
                  onChange={handleInputChange}
                  placeholder="请输入密码"
                  className={`w-full pl-12 pr-12 py-3.5 bg-gray-50 border rounded-xl text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent transition-all ${
                    errors.password ? "border-red-500" : "border-gray-200"
                  }`}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword((previous) => !previous)}
                  className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors"
                >
                  {showPassword ? (
                    <EyeOff className="w-5 h-5" />
                  ) : (
                    <Eye className="w-5 h-5" />
                  )}
                </button>
              </div>
              {errors.password && (
                <p className="mt-1.5 text-sm text-red-500">{errors.password}</p>
              )}
            </div>

            {!isLogin && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  确认密码
                </label>
                <div className="relative">
                  <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <input
                    type={showConfirmPassword ? "text" : "password"}
                    name="confirmPassword"
                    value={formData.confirmPassword}
                    onChange={handleInputChange}
                    placeholder="请再次输入密码"
                    className={`w-full pl-12 pr-12 py-3.5 bg-gray-50 border rounded-xl text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent transition-all ${
                      errors.confirmPassword ? "border-red-500" : "border-gray-200"
                    }`}
                  />
                  <button
                    type="button"
                    onClick={() => setShowConfirmPassword((previous) => !previous)}
                    className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors"
                  >
                    {showConfirmPassword ? (
                      <EyeOff className="w-5 h-5" />
                    ) : (
                      <Eye className="w-5 h-5" />
                    )}
                  </button>
                </div>
                {errors.confirmPassword && (
                  <p className="mt-1.5 text-sm text-red-500">{errors.confirmPassword}</p>
                )}
              </div>
            )}

            {submitError && (
              <div className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-600">
                {submitError}
              </div>
            )}

            <button
              type="submit"
              disabled={isLoading}
              className="w-full py-3.5 bg-gradient-to-r from-emerald-500 to-teal-500 text-white rounded-xl font-bold hover:shadow-lg hover:scale-105 transition-all disabled:opacity-70 disabled:cursor-not-allowed disabled:hover:scale-100"
            >
              {isLoading ? "处理中..." : isLogin ? "登录" : "注册"}
            </button>
          </form>

          <div className="mt-6 text-center">
            <p className="text-gray-600 text-sm">
              {isLogin ? "还没有账号？" : "已经有账号了？"}
              <button
                onClick={switchMode}
                className="text-emerald-600 hover:text-emerald-700 font-medium ml-1 transition-colors"
                type="button"
              >
                {isLogin ? "立即注册" : "立即登录"}
              </button>
            </p>
          </div>

          <div className="mt-6">
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-gray-200"></div>
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-4 bg-white text-gray-500">或</span>
              </div>
            </div>
            <Link
              to="/"
              className="mt-4 w-full py-3.5 bg-gray-100 text-gray-700 rounded-xl font-medium hover:bg-gray-200 hover:scale-105 transition-all flex items-center justify-center gap-2"
            >
              游客模式访问
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}

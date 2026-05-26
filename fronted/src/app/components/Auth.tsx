import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router";
import { ArrowLeft, Eye, EyeOff, GraduationCap, KeyRound, Lock, Mail, User } from "lucide-react";

import { ApiError } from "../lib/api";
import {
  confirmPasswordReset,
  loginWithPassword,
  registerWithPassword,
  requestPasswordReset,
} from "../lib/account";
import { hasSession } from "../lib/session";
import { Tabs, TabsList, TabsTrigger } from "./ui/tabs";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { Button } from "./ui/button";

type AuthMode = "auth" | "reset-request" | "reset-confirm";

export function Auth() {
  const [activeTab, setActiveTab] = useState<"login" | "register">("login");
  const [mode, setMode] = useState<AuthMode>("auth");
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [formData, setFormData] = useState({
    account: "",
    username: "",
    email: "",
    resetCode: "",
    password: "",
    confirmPassword: "",
  });
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [submitError, setSubmitError] = useState("");
  const [successMessage, setSuccessMessage] = useState("");
  const [maskedResetEmail, setMaskedResetEmail] = useState("");
  const [resetExpiresInSeconds, setResetExpiresInSeconds] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    if (hasSession()) {
      navigate("/profile", { replace: true });
    }
  }, [navigate]);

  const validateForm = () => {
    const nextErrors: Record<string, string> = {};

    if (mode === "reset-request") {
      if (!formData.account.trim()) {
        nextErrors.account = "请输入登录账号";
      }
      setErrors(nextErrors);
      return Object.keys(nextErrors).length === 0;
    }

    if (mode === "reset-confirm") {
      if (!formData.resetCode.trim()) {
        nextErrors.resetCode = "请输入邮箱验证码";
      } else if (!/^\d{4,12}$/.test(formData.resetCode.trim())) {
        nextErrors.resetCode = "验证码格式不正确";
      }
      if (!formData.password) {
        nextErrors.password = "请输入新密码";
      } else if (formData.password.length < 6) {
        nextErrors.password = "密码至少 6 个字符";
      }
      if (!formData.confirmPassword) {
        nextErrors.confirmPassword = "请再次输入新密码";
      } else if (formData.password !== formData.confirmPassword) {
        nextErrors.confirmPassword = "两次输入的密码不一致";
      }
      setErrors(nextErrors);
      return Object.keys(nextErrors).length === 0;
    }

    if (activeTab === "login") {
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

    if (activeTab === "register") {
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
    setSuccessMessage("");

    if (!validateForm()) {
      return;
    }

    setIsLoading(true);
    try {
      if (mode === "reset-request") {
        const response = await requestPasswordReset({
          account: formData.account.trim(),
        });
        setResetExpiresInSeconds(response.expires_in_seconds);
        setMaskedResetEmail(response.masked_email || "");
        setSuccessMessage(response.message);
        if (response.sent) {
          setMode("reset-confirm");
        }
        return;
      }

      if (mode === "reset-confirm") {
        const response = await confirmPasswordReset({
          account: formData.account.trim(),
          code: formData.resetCode.trim(),
          new_password: formData.password,
        });
        setSuccessMessage(response.message);
        setMode("auth");
        setActiveTab("login");
        setFormData((previous) => ({
          ...previous,
          resetCode: "",
          password: "",
          confirmPassword: "",
        }));
        return;
      }

      if (activeTab === "login") {
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
    setSuccessMessage("");

    if (errors[name]) {
      setErrors((previous) => ({ ...previous, [name]: "" }));
    }
  };

  const handleTabChange = (value: string) => {
    setActiveTab(value as "login" | "register");
    setMode("auth");
    setErrors({});
    setSubmitError("");
    setSuccessMessage("");
    setMaskedResetEmail("");
    setFormData({
      account: "",
      username: "",
      email: "",
      resetCode: "",
      password: "",
      confirmPassword: "",
    });
  };

  const openPasswordReset = () => {
    setMode("reset-request");
    setActiveTab("login");
    setErrors({});
    setSubmitError("");
    setSuccessMessage("");
    setMaskedResetEmail("");
    setFormData((previous) => ({
      ...previous,
      resetCode: "",
      password: "",
      confirmPassword: "",
    }));
  };

  const backToLogin = () => {
    setMode("auth");
    setActiveTab("login");
    setErrors({});
    setSubmitError("");
    setSuccessMessage("");
    setMaskedResetEmail("");
    setResetExpiresInSeconds(0);
    setFormData((previous) => ({
      ...previous,
      resetCode: "",
      password: "",
      confirmPassword: "",
    }));
  };

  const submitLabel =
    mode === "reset-request"
      ? "发送验证码"
      : mode === "reset-confirm"
        ? "重置密码"
        : activeTab === "login"
          ? "登录"
          : "注册";

  return (
    <div className="flex min-h-screen bg-white">
      {/* 左侧横幅 (70%) */}
      <div className="hidden lg:flex lg:w-[70%] bg-slate-950 relative flex-col justify-between p-12 overflow-hidden">
        {/* 现代背景光效 - 网格与柔和光晕 */}
        <div className="absolute inset-0 bg-[linear-gradient(to_right,#4f4f4f2e_1px,transparent_1px),linear-gradient(to_bottom,#4f4f4f2e_1px,transparent_1px)] bg-[size:14px_24px] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_0%,#000_70%,transparent_100%)]"></div>
        <div className="absolute top-[-10%] left-[-10%] w-[50%] h-[50%] rounded-full bg-emerald-500/20 blur-[120px] pointer-events-none" />
        <div className="absolute bottom-[-10%] right-[-10%] w-[50%] h-[50%] rounded-full bg-teal-500/20 blur-[120px] pointer-events-none" />
        <div className="absolute top-[40%] right-[10%] w-[30%] h-[30%] rounded-full bg-blue-500/20 blur-[100px] pointer-events-none" />
        
        <div className="relative z-10 max-w-3xl mt-10">
          <div className="bg-white/10 w-16 h-16 rounded-2xl flex items-center justify-center backdrop-blur-md mb-8 border border-white/10 shadow-2xl">
            <GraduationCap className="w-10 h-10 text-emerald-400" />
          </div>
          <h1 className="text-4xl xl:text-6xl font-bold tracking-tight text-white mb-6 leading-tight drop-shadow-sm">
            探索知识的边界 <br /> 
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-teal-400">点亮你的学习之旅</span>
          </h1>
          <p className="text-lg xl:text-xl text-slate-300 max-w-xl leading-relaxed font-medium">
            加入我们的智能学习平台，体验个性化内容推荐与 AI 辅助学习。记录每一次进步，与优秀的学习者共同成长。
          </p>
        </div>
        
        <div className="relative z-10 text-slate-400 text-sm font-medium">
          &copy; {new Date().getFullYear()} LingLearn Cloud. All rights reserved.
        </div>
      </div>

      {/* 右侧表单 (30%) */}
      <div className="w-full lg:w-[30%] min-w-[380px] flex flex-col justify-center bg-white p-6 sm:p-10 lg:p-12 shadow-[-20px_0_40px_-10px_rgba(0,0,0,0.05)] z-10 relative overflow-y-auto">
        <div className="w-full max-w-[400px] mx-auto">
          {/* 移动端顶部标题 (仅在窄屏显示) */}
          <div className="lg:hidden flex flex-col items-center mb-8 space-y-4">
            <div className="bg-emerald-50 p-3.5 rounded-2xl shadow-sm border border-emerald-100">
              <GraduationCap className="w-10 h-10 text-emerald-600" />
            </div>
            <div className="text-center space-y-1">
              <h1 className="text-2xl font-bold tracking-tight text-gray-900">智能学习平台</h1>
              <p className="text-sm text-gray-500">
                登录后即可同步你的学习档案
              </p>
            </div>
          </div>

          {/* 桌面端顶部标题 */}
          <div className="hidden lg:block mb-8">
            <h2 className="text-3xl font-bold text-gray-900 mb-2">欢迎回来</h2>
            <p className="text-sm text-gray-500 font-medium">登录或注册以继续访问您的账号</p>
          </div>

          {mode !== "auth" && (
            <button
              type="button"
              onClick={backToLogin}
              className="mb-6 inline-flex items-center gap-2 text-sm font-medium text-gray-500 transition-colors hover:text-emerald-600"
            >
              <ArrowLeft className="h-4 w-4" />
              返回登录
            </button>
          )}

          {mode !== "auth" && (
            <div className="mb-8 space-y-2">
              <div className="inline-flex h-11 w-11 items-center justify-center rounded-xl bg-emerald-50 text-emerald-600">
                <KeyRound className="h-5 w-5" />
              </div>
              <h2 className="text-2xl font-bold text-gray-900">
                {mode === "reset-request" ? "找回账号密码" : "设置新密码"}
              </h2>
              <p className="text-sm leading-6 text-gray-500">
                {mode === "reset-request"
                  ? "输入你的登录账号，我们会向该账号绑定邮箱发送验证码。"
                  : `验证码已发送至绑定邮箱${maskedResetEmail ? ` ${maskedResetEmail}` : ""}，请在 ${Math.ceil(resetExpiresInSeconds / 60) || 10} 分钟内完成重置。`}
              </p>
            </div>
          )}

          {mode === "auth" && (
            <Tabs
              defaultValue="login"
              value={activeTab}
              onValueChange={handleTabChange}
              className="w-full"
            >
              <TabsList className="grid w-full grid-cols-2 mb-8 bg-gray-100 rounded-xl p-1 h-auto">
                <TabsTrigger
                  value="login"
                  className="py-2.5 rounded-lg text-sm font-medium transition-all data-[state=active]:bg-gradient-to-r data-[state=active]:from-emerald-500 data-[state=active]:to-teal-500 data-[state=active]:text-white data-[state=active]:shadow-md text-gray-600 hover:text-gray-900"
                >
                  登录
                </TabsTrigger>
                <TabsTrigger
                  value="register"
                  className="py-2.5 rounded-lg text-sm font-medium transition-all data-[state=active]:bg-gradient-to-r data-[state=active]:from-emerald-500 data-[state=active]:to-teal-500 data-[state=active]:text-white data-[state=active]:shadow-md text-gray-600 hover:text-gray-900"
                >
                  注册
                </TabsTrigger>
              </TabsList>
            </Tabs>
          )}

          <form onSubmit={handleSubmit} className="space-y-5">
            {mode === "auth" && (
              <>
                {activeTab === "login" && (
                  <div className="space-y-2">
                    <Label htmlFor="account" className="text-gray-700 font-medium">账号</Label>
                    <div className="relative">
                      <User className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                      <Input
                        id="account"
                        type="text"
                        name="account"
                        value={formData.account}
                        onChange={handleInputChange}
                        placeholder="用户名或邮箱"
                        className={`pl-10 py-5 bg-gray-50/50 border-gray-200 rounded-xl focus-visible:ring-emerald-500 focus-visible:border-transparent transition-colors ${errors.account ? "border-red-500 focus-visible:ring-red-500 bg-red-50/50" : "hover:border-gray-300"}`}
                      />
                    </div>
                    {errors.account && (
                      <p className="text-sm font-medium text-red-500">{errors.account}</p>
                    )}
                  </div>
                )}

                {activeTab === "register" && (
                  <>
                    <div className="space-y-2">
                      <Label htmlFor="username" className="text-gray-700 font-medium">用户名</Label>
                      <div className="relative">
                        <User className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                        <Input
                          id="username"
                          type="text"
                          name="username"
                          value={formData.username}
                          onChange={handleInputChange}
                          placeholder="请输入用户名"
                          className={`pl-10 py-5 bg-gray-50/50 border-gray-200 rounded-xl focus-visible:ring-emerald-500 focus-visible:border-transparent transition-colors ${errors.username ? "border-red-500 focus-visible:ring-red-500 bg-red-50/50" : "hover:border-gray-300"}`}
                        />
                      </div>
                      {errors.username && (
                        <p className="text-sm font-medium text-red-500">{errors.username}</p>
                      )}
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="email" className="text-gray-700 font-medium">邮箱</Label>
                      <div className="relative">
                        <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                        <Input
                          id="email"
                          type="email"
                          name="email"
                          value={formData.email}
                          onChange={handleInputChange}
                          placeholder="请输入邮箱"
                          className={`pl-10 py-5 bg-gray-50/50 border-gray-200 rounded-xl focus-visible:ring-emerald-500 focus-visible:border-transparent transition-colors ${errors.email ? "border-red-500 focus-visible:ring-red-500 bg-red-50/50" : "hover:border-gray-300"}`}
                        />
                      </div>
                      {errors.email && (
                        <p className="text-sm font-medium text-red-500">{errors.email}</p>
                      )}
                    </div>
                  </>
                )}
              </>
            )}

            {mode === "reset-request" && (
              <div className="space-y-2">
                <Label htmlFor="reset-account" className="text-gray-700 font-medium">账号</Label>
                <div className="relative">
                  <User className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <Input
                    id="reset-account"
                    type="text"
                    name="account"
                    value={formData.account}
                    onChange={handleInputChange}
                    placeholder="请输入登录账号"
                    className={`pl-10 py-5 bg-gray-50/50 border-gray-200 rounded-xl focus-visible:ring-emerald-500 focus-visible:border-transparent transition-colors ${errors.account ? "border-red-500 focus-visible:ring-red-500 bg-red-50/50" : "hover:border-gray-300"}`}
                  />
                </div>
                {errors.account && (
                  <p className="text-sm font-medium text-red-500">{errors.account}</p>
                )}
              </div>
            )}

            {mode === "reset-confirm" && (
              <div className="space-y-2">
                <Label htmlFor="reset-code" className="text-gray-700 font-medium">邮箱验证码</Label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <Input
                    id="reset-code"
                    type="text"
                    inputMode="numeric"
                    name="resetCode"
                    value={formData.resetCode}
                    onChange={handleInputChange}
                    placeholder="请输入验证码"
                    className={`pl-10 py-5 bg-gray-50/50 border-gray-200 rounded-xl focus-visible:ring-emerald-500 focus-visible:border-transparent transition-colors ${errors.resetCode ? "border-red-500 focus-visible:ring-red-500 bg-red-50/50" : "hover:border-gray-300"}`}
                  />
                </div>
                {errors.resetCode && (
                  <p className="text-sm font-medium text-red-500">{errors.resetCode}</p>
                )}
              </div>
            )}

            {mode !== "reset-request" && (
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <Label htmlFor="password" className="text-gray-700 font-medium">
                    {mode === "reset-confirm" ? "新密码" : "密码"}
                  </Label>
                  {mode === "auth" && activeTab === "login" && (
                    <button
                      type="button"
                      className="text-sm font-medium text-emerald-600 hover:text-emerald-700 hover:underline transition-colors"
                      onClick={openPasswordReset}
                    >
                      忘记密码？
                    </button>
                  )}
                </div>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <Input
                    id="password"
                    type={showPassword ? "text" : "password"}
                    name="password"
                    value={formData.password}
                    onChange={handleInputChange}
                    placeholder={mode === "reset-confirm" ? "请输入新密码" : "请输入密码"}
                    className={`pl-10 pr-10 py-5 bg-gray-50/50 border-gray-200 rounded-xl focus-visible:ring-emerald-500 focus-visible:border-transparent transition-colors ${errors.password ? "border-red-500 focus-visible:ring-red-500 bg-red-50/50" : "hover:border-gray-300"}`}
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors"
                    tabIndex={-1}
                  >
                    {showPassword ? (
                      <EyeOff className="w-5 h-5" />
                    ) : (
                      <Eye className="w-5 h-5" />
                    )}
                  </button>
                </div>
                {errors.password && (
                  <p className="text-sm font-medium text-red-500">{errors.password}</p>
                )}
              </div>
            )}

            {(mode === "reset-confirm" || (mode === "auth" && activeTab === "register")) && (
              <div className="space-y-2">
                <Label htmlFor="confirmPassword" className="text-gray-700 font-medium">
                  {mode === "reset-confirm" ? "确认新密码" : "确认密码"}
                </Label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <Input
                    id="confirmPassword"
                    type={showConfirmPassword ? "text" : "password"}
                    name="confirmPassword"
                    value={formData.confirmPassword}
                    onChange={handleInputChange}
                    placeholder={mode === "reset-confirm" ? "请再次输入新密码" : "请再次输入密码"}
                    className={`pl-10 pr-10 py-5 bg-gray-50/50 border-gray-200 rounded-xl focus-visible:ring-emerald-500 focus-visible:border-transparent transition-colors ${errors.confirmPassword ? "border-red-500 focus-visible:ring-red-500 bg-red-50/50" : "hover:border-gray-300"}`}
                  />
                  <button
                    type="button"
                    onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors"
                    tabIndex={-1}
                  >
                    {showConfirmPassword ? (
                      <EyeOff className="w-5 h-5" />
                    ) : (
                      <Eye className="w-5 h-5" />
                    )}
                  </button>
                </div>
                {errors.confirmPassword && (
                  <p className="text-sm font-medium text-red-500">{errors.confirmPassword}</p>
                )}
              </div>
            )}

            {submitError && (
              <div className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-600">
                {submitError}
              </div>
            )}

            {successMessage && (
              <div className="rounded-xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-700">
                {successMessage}
              </div>
            )}

            <div className="pt-4">
              <Button
                type="submit"
                className="w-full py-6 bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-600 hover:to-teal-600 text-white rounded-xl text-base font-bold shadow-md hover:shadow-lg transition-all border-0"
                disabled={isLoading}
              >
                {isLoading ? "处理中..." : submitLabel}
              </Button>
            </div>

            {mode === "reset-confirm" && (
              <Button
                type="button"
                variant="ghost"
                className="w-full rounded-xl text-sm font-bold text-emerald-700 hover:bg-emerald-50 hover:text-emerald-800"
                disabled={isLoading}
                onClick={() => setMode("reset-request")}
              >
                重新发送验证码
              </Button>
            )}

            {mode === "auth" && (
              <div className="mt-8">
                <div className="relative">
                  <div className="absolute inset-0 flex items-center">
                    <div className="w-full border-t border-gray-200"></div>
                  </div>
                  <div className="relative flex justify-center text-sm">
                    <span className="px-4 bg-white text-gray-400 font-medium">或</span>
                  </div>
                </div>
                
                <Button 
                  variant="outline" 
                  asChild 
                  className="w-full mt-6 py-6 bg-white text-gray-700 rounded-xl text-sm font-bold hover:bg-gray-50 hover:text-gray-900 border-gray-200 shadow-sm transition-all"
                >
                  <Link to="/">以游客身份继续</Link>
                </Button>
              </div>
            )}
          </form>
        </div>
      </div>
    </div>
  );
}

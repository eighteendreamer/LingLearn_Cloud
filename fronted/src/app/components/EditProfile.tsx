import { useState } from "react";
import { Link } from "react-router";
import { ArrowLeft, Camera, User, Mail, Phone, MapPin, Briefcase, Calendar, Save } from "lucide-react";

export function EditProfile() {
  const [formData, setFormData] = useState({
    nickname: "张同学",
    bio: "全栈开发 | 终身学习",
    email: "zhang@example.com",
    phone: "",
    location: "",
    profession: "学生",
    birthday: "",
  });

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSave = () => {
    console.log("保存资料:", formData);
    alert("资料保存成功！");
  };

  return (
    <div className="h-screen overflow-y-auto bg-gradient-to-br from-blue-50 via-white to-emerald-50 pb-20">
      {/* 头部 */}
      <div className="sticky top-0 z-10 flex items-center gap-3 p-4 bg-white/95 backdrop-blur-lg border-b border-gray-200 shadow-sm">
        <Link to="/profile">
          <ArrowLeft className="w-6 h-6 text-gray-700" />
        </Link>
        <div className="flex-1">
          <h1 className="text-lg font-semibold text-gray-900">编辑资料</h1>
          <p className="text-xs text-gray-600">完善你的个人信息</p>
        </div>
        <button
          onClick={handleSave}
          className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-emerald-500 to-teal-500 text-white rounded-lg text-sm font-bold hover:shadow-lg transition-all"
        >
          <Save className="w-4 h-4" />
          保存
        </button>
      </div>

      <div className="p-6 max-w-2xl mx-auto">
        {/* 头像编辑 */}
        <div className="bg-white rounded-2xl p-6 shadow-md mb-6">
          <div className="flex items-center gap-6">
            <div className="relative">
              <div className="w-20 h-20 rounded-full bg-gradient-to-br from-emerald-500 to-teal-500 flex items-center justify-center text-white text-2xl font-bold shadow-lg">
                {formData.nickname.charAt(0)}
              </div>
              <button className="absolute -bottom-1 -right-1 w-8 h-8 bg-white rounded-full shadow-md flex items-center justify-center border-2 border-emerald-500 hover:bg-emerald-50 transition-colors">
                <Camera className="w-4 h-4 text-emerald-600" />
              </button>
            </div>
            <div>
              <h3 className="text-gray-900 font-semibold mb-1">更换头像</h3>
              <p className="text-gray-600 text-sm">点击右侧相机图标上传新头像</p>
            </div>
          </div>
        </div>

        {/* 基本信息 */}
        <div className="bg-white rounded-2xl p-6 shadow-md mb-6">
          <h3 className="text-gray-900 font-semibold mb-4 flex items-center gap-2">
            <User className="w-5 h-5 text-emerald-500" />
            基本信息
          </h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                昵称
              </label>
              <input
                type="text"
                name="nickname"
                value={formData.nickname}
                onChange={handleInputChange}
                placeholder="请输入昵称"
                className="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent transition-all"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                个人简介
              </label>
              <textarea
                name="bio"
                value={formData.bio}
                onChange={handleInputChange}
                placeholder="介绍一下自己..."
                className="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent transition-all resize-none"
                rows={3}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                职业
              </label>
              <div className="relative">
                <Briefcase className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="text"
                  name="profession"
                  value={formData.profession}
                  onChange={handleInputChange}
                  placeholder="请输入职业"
                  className="w-full pl-12 pr-4 py-3 bg-gray-50 border border-gray-200 rounded-xl text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent transition-all"
                />
              </div>
            </div>
          </div>
        </div>

        {/* 联系方式 */}
        <div className="bg-white rounded-2xl p-6 shadow-md mb-6">
          <h3 className="text-gray-900 font-semibold mb-4 flex items-center gap-2">
            <Mail className="w-5 h-5 text-emerald-500" />
            联系方式
          </h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                邮箱
              </label>
              <div className="relative">
                <Mail className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleInputChange}
                  placeholder="请输入邮箱"
                  className="w-full pl-12 pr-4 py-3 bg-gray-50 border border-gray-200 rounded-xl text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent transition-all"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                手机号
              </label>
              <div className="relative">
                <Phone className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="tel"
                  name="phone"
                  value={formData.phone}
                  onChange={handleInputChange}
                  placeholder="请输入手机号"
                  className="w-full pl-12 pr-4 py-3 bg-gray-50 border border-gray-200 rounded-xl text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent transition-all"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                所在地
              </label>
              <div className="relative">
                <MapPin className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="text"
                  name="location"
                  value={formData.location}
                  onChange={handleInputChange}
                  placeholder="请输入所在地"
                  className="w-full pl-12 pr-4 py-3 bg-gray-50 border border-gray-200 rounded-xl text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent transition-all"
                />
              </div>
            </div>
          </div>
        </div>

        {/* 其他信息 */}
        <div className="bg-white rounded-2xl p-6 shadow-md">
          <h3 className="text-gray-900 font-semibold mb-4 flex items-center gap-2">
            <Calendar className="w-5 h-5 text-emerald-500" />
            其他信息
          </h3>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              生日
            </label>
            <div className="relative">
              <Calendar className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="date"
                name="birthday"
                value={formData.birthday}
                onChange={handleInputChange}
                className="w-full pl-12 pr-4 py-3 bg-gray-50 border border-gray-200 rounded-xl text-gray-900 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent transition-all"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
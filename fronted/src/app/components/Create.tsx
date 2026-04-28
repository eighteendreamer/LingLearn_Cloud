import { useState } from "react";
import { ArrowLeft, Upload, Play, Image, FileText, Video, Link as LinkIcon } from "lucide-react";
import { Link } from "react-router";

export function Create() {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [category, setCategory] = useState("编程");
  const [coverImage, setCoverImage] = useState<File | null>(null);
  const [videoFile, setVideoFile] = useState<File | null>(null);

  const categories = ["编程", "算法", "前端", "后端", "数据库", "AI/ML"];

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    console.log({ title, description, category, coverImage, videoFile });
    alert("作品创建功能开发中...");
  };

  return (
    <div className="h-screen overflow-y-auto bg-gradient-to-br from-blue-50 via-white to-emerald-50 pb-20">
      <div className="sticky top-0 z-10 flex items-center gap-3 p-4 bg-white/95 backdrop-blur-lg border-b border-gray-200 shadow-sm">
        <Link to="/">
          <ArrowLeft className="w-6 h-6 text-gray-700" />
        </Link>
        <div>
          <h1 className="text-lg font-semibold text-gray-900">创作中心</h1>
          <p className="text-xs text-gray-600">分享你的学习成果</p>
        </div>
      </div>

      <div className="p-6 max-w-2xl mx-auto">
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              作品标题
            </label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="给你的作品起个标题吧"
              className="w-full px-4 py-3 bg-white border border-gray-200 rounded-xl text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent"
              maxLength={50}
            />
            <p className="mt-1 text-xs text-gray-500 text-right">{title.length}/50</p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              作品描述
            </label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="介绍一下你的作品吧..."
              className="w-full px-4 py-3 bg-white border border-gray-200 rounded-xl text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent resize-none"
              rows={4}
              maxLength={500}
            />
            <p className="mt-1 text-xs text-gray-500 text-right">{description.length}/500</p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              分类
            </label>
            <div className="flex flex-wrap gap-2">
              {categories.map((cat) => (
                <button
                  key={cat}
                  type="button"
                  onClick={() => setCategory(cat)}
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                    category === cat
                      ? "bg-emerald-500 text-white"
                      : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                  }`}
                >
                  {cat}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              上传视频
            </label>
            <div
              className={`border-2 border-dashed rounded-xl p-8 text-center transition-colors cursor-pointer ${
                videoFile
                  ? "border-emerald-500 bg-emerald-50"
                  : "border-gray-300 hover:border-emerald-500 hover:bg-gray-50"
              }`}
              onDragOver={(e) => e.preventDefault()}
              onDrop={(e) => {
                e.preventDefault();
                const file = e.dataTransfer.files[0];
                if (file && file.type.startsWith("video/")) {
                  setVideoFile(file);
                }
              }}
            >
              <input
                type="file"
                accept="video/*"
                className="hidden"
                id="video-upload"
                onChange={(e) => {
                  const file = e.target.files?.[0];
                  if (file) setVideoFile(file);
                }}
              />
              <label htmlFor="video-upload" className="cursor-pointer">
                {videoFile ? (
                  <div className="flex items-center justify-center gap-3">
                    <Video className="w-8 h-8 text-emerald-500" />
                    <span className="text-emerald-600 font-medium">{videoFile.name}</span>
                  </div>
                ) : (
                  <>
                    <Upload className="w-10 h-10 text-gray-400 mx-auto mb-3" />
                    <p className="text-gray-600 font-medium mb-1">点击或拖拽上传视频</p>
                    <p className="text-gray-400 text-sm">支持 MP4、MOV 格式，最大 500MB</p>
                  </>
                )}
              </label>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              封面图片
            </label>
            <div
              className={`border-2 border-dashed rounded-xl p-8 text-center transition-colors cursor-pointer ${
                coverImage
                  ? "border-emerald-500 bg-emerald-50"
                  : "border-gray-300 hover:border-emerald-500 hover:bg-gray-50"
              }`}
            >
              <input
                type="file"
                accept="image/*"
                className="hidden"
                id="cover-upload"
                onChange={(e) => {
                  const file = e.target.files?.[0];
                  if (file) setCoverImage(file);
                }}
              />
              <label htmlFor="cover-upload" className="cursor-pointer">
                {coverImage ? (
                  <div className="flex items-center justify-center gap-3">
                    <Image className="w-8 h-8 text-emerald-500" />
                    <span className="text-emerald-600 font-medium">{coverImage.name}</span>
                  </div>
                ) : (
                  <>
                    <Image className="w-10 h-10 text-gray-400 mx-auto mb-3" />
                    <p className="text-gray-600 font-medium mb-1">点击上传封面图片</p>
                    <p className="text-gray-400 text-sm">支持 JPG、PNG 格式</p>
                  </>
                )}
              </label>
            </div>
          </div>

          <div className="flex gap-3 pt-4">
            <Link
              to="/"
              className="flex-1 py-3.5 bg-gray-100 text-gray-700 rounded-xl font-medium hover:bg-gray-200 transition-colors text-center"
            >
              取消
            </Link>
            <button
              type="submit"
              className="flex-1 py-3.5 bg-gradient-to-r from-emerald-500 to-teal-500 text-white rounded-xl font-semibold hover:from-emerald-600 hover:to-teal-600 transition-all shadow-lg hover:shadow-xl"
            >
              发布作品
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

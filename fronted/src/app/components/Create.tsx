import { useEffect, useState } from "react";
import { ArrowLeft, Image, Upload, Video, X, Plus } from "lucide-react";
import { Link, useNavigate } from "react-router";

import { ApiError } from "../lib/api";
import { createContent, fetchContentCategories } from "../lib/content";
import { uploadFileToStorage, uploadMultipartFileToStorage } from "../lib/storage";
import type { ContentCategoryResponse } from "../lib/types";

function getErrorMessage(error: unknown) {
  if (error instanceof ApiError) {
    return error.message;
  }

  if (error instanceof Error) {
    return error.message;
  }

  return "上传失败，请检查后端服务和 MinIO 配置。";
}

export function Create() {
  const navigate = useNavigate();
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [categories, setCategories] = useState<ContentCategoryResponse[]>([]);
  const [selectedCategoryId, setSelectedCategoryId] = useState<number | null>(null);
  const [customTags, setCustomTags] = useState<string[]>([]);
  const [tagInput, setTagInput] = useState("");
  const [coverImage, setCoverImage] = useState<File | null>(null);
  const [videoFile, setVideoFile] = useState<File | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitMessage, setSubmitMessage] = useState("");
  const [videoProgress, setVideoProgress] = useState(0);
  const [isLoadingCategories, setIsLoadingCategories] = useState(true);

  useEffect(() => {
    let cancelled = false;

    async function loadCategories() {
      setIsLoadingCategories(true);
      try {
        const data = await fetchContentCategories();
        if (cancelled) {
          return;
        }
        setCategories(data);
        setSelectedCategoryId((current) => current ?? data[0]?.id ?? null);
      } catch (error) {
        if (!cancelled) {
          setSubmitMessage(getErrorMessage(error));
        }
      } finally {
        if (!cancelled) {
          setIsLoadingCategories(false);
        }
      }
    }

    loadCategories();
    return () => {
      cancelled = true;
    };
  }, []);

  const selectedCategory = categories.find((item) => item.id === selectedCategoryId) ?? null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!title.trim()) {
      setSubmitMessage("请输入作品标题。");
      return;
    }

    if (!selectedCategoryId || !selectedCategory) {
      setSubmitMessage("请选择一个有效的分类标签。");
      return;
    }

    if (!videoFile) {
      setSubmitMessage("请先上传视频文件。");
      return;
    }

    if (!coverImage) {
      setSubmitMessage("请先上传封面图片。");
      return;
    }

    setIsSubmitting(true);
    setVideoProgress(0);
    setSubmitMessage("正在分片上传视频到 MinIO，请稍候...");

    try {
      const videoAsset = await uploadMultipartFileToStorage(videoFile, "content_video", {
        onProgress: (progress) => {
          setVideoProgress(progress);
          setSubmitMessage(`正在分片上传视频到 MinIO... ${progress}%`);
        },
      });
      setSubmitMessage("视频分片上传完成，正在上传封面...");

      const coverAsset = await uploadFileToStorage(coverImage, "content_cover");

      setSubmitMessage("封面上传完成，正在发布内容...");
      const hashtags = selectedCategory ? [selectedCategory.name, ...customTags] : [...customTags];
      await createContent({
        title: title.trim(),
        summary: description.trim() || null,
        category_id: selectedCategoryId,
        cover_asset_id: coverAsset.asset_id,
        primary_media_asset_id: videoAsset.asset_id,
        content_type: "short_video",
        hashtags: Array.from(new Set(hashtags)).filter(Boolean),
      });

      setSubmitMessage("作品发布成功，正在返回首页...");
      window.setTimeout(() => {
        navigate("/");
      }, 800);
    } catch (error) {
      setSubmitMessage(getErrorMessage(error));
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="h-screen overflow-y-auto bg-gradient-to-br from-blue-50 via-white to-emerald-50 pb-20">
      <div className="sticky top-0 z-10 flex items-center gap-3 border-b border-gray-200 bg-white/95 p-4 shadow-sm backdrop-blur-lg">
        <Link to="/">
          <ArrowLeft className="h-6 w-6 text-gray-700" />
        </Link>
        <div>
          <h1 className="text-lg font-semibold text-gray-900">创作中心</h1>
          <p className="text-xs text-gray-600">上传视频、封面并直接发布到首页 feed</p>
        </div>
      </div>

      <div className="mx-auto max-w-2xl p-6">
        <form onSubmit={handleSubmit} className="space-y-6">
          {submitMessage ? (
            <div className="rounded-xl border border-emerald-100 bg-emerald-50 px-4 py-3 text-sm text-emerald-700">
              {submitMessage}
            </div>
          ) : null}

          {isSubmitting && videoProgress > 0 ? (
            <div className="space-y-2">
              <div className="h-2 overflow-hidden rounded-full bg-emerald-100">
                <div
                  className="h-full rounded-full bg-emerald-500 transition-all"
                  style={{ width: `${videoProgress}%` }}
                />
              </div>
              <p className="text-xs text-emerald-700">视频上传进度 {videoProgress}%</p>
            </div>
          ) : null}

          <div>
            <label className="mb-2 block text-sm font-medium text-gray-700">作品标题</label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="给你的作品起一个标题"
              className="w-full rounded-xl border border-gray-200 bg-white px-4 py-3 text-gray-900 placeholder-gray-400 focus:border-transparent focus:outline-none focus:ring-2 focus:ring-emerald-500"
              maxLength={50}
            />
            <p className="mt-1 text-right text-xs text-gray-500">{title.length}/50</p>
          </div>

          <div>
            <label className="mb-2 block text-sm font-medium text-gray-700">作品描述</label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="简单介绍一下这条内容"
              className="w-full resize-none rounded-xl border border-gray-200 bg-white px-4 py-3 text-gray-900 placeholder-gray-400 focus:border-transparent focus:outline-none focus:ring-2 focus:ring-emerald-500"
              rows={4}
              maxLength={500}
            />
            <p className="mt-1 text-right text-xs text-gray-500">{description.length}/500</p>
          </div>

          <div>
            <label className="mb-2 block text-sm font-medium text-gray-700">分类标签</label>
            <div className="flex flex-wrap gap-2 mb-3">
              {isLoadingCategories ? (
                <span className="text-sm text-gray-500">正在加载分类...</span>
              ) : null}
              {!isLoadingCategories && categories.length === 0 ? (
                <span className="text-sm text-red-500">暂无可用分类，请检查分类初始化。</span>
              ) : null}
              {categories.map((item) => (
                <button
                  key={item.id}
                  type="button"
                  onClick={() => setSelectedCategoryId(item.id)}
                  className={`rounded-lg px-4 py-2 text-sm font-medium transition-all ${
                    selectedCategoryId === item.id
                      ? "bg-emerald-500 text-white shadow-md shadow-emerald-500/20"
                      : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                  }`}
                >
                  {item.name}
                </button>
              ))}
            </div>
            
            <div className="flex flex-wrap items-center gap-2">
              {customTags.map((tag) => (
                <span key={tag} className="inline-flex items-center gap-1 rounded-lg bg-emerald-50 px-3 py-1.5 text-sm font-medium text-emerald-700 border border-emerald-100">
                  #{tag}
                  <button
                    type="button"
                    onClick={() => setCustomTags(tags => tags.filter(t => t !== tag))}
                    className="ml-1 text-emerald-500 hover:text-emerald-700 focus:outline-none bg-emerald-100 hover:bg-emerald-200 rounded-full p-0.5 transition-colors"
                  >
                    <X className="h-3 w-3" />
                  </button>
                </span>
              ))}
              
              {customTags.length < 5 && (
                <div className="relative flex items-center">
                  <Plus className="absolute left-2.5 h-4 w-4 text-gray-400" />
                  <input
                    type="text"
                    value={tagInput}
                    onChange={(e) => setTagInput(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === "Enter") {
                        e.preventDefault();
                        const val = tagInput.trim();
                        if (val && !customTags.includes(val) && !categories.some(c => c.name === val)) {
                          setCustomTags([...customTags, val]);
                          setTagInput("");
                        }
                      }
                    }}
                    placeholder="自定义标签，按回车添加..."
                    className="w-52 rounded-lg border border-gray-200 bg-white py-1.5 pl-8 pr-3 text-sm text-gray-900 placeholder-gray-400 focus:border-transparent focus:outline-none focus:ring-2 focus:ring-emerald-500 shadow-sm"
                    maxLength={15}
                  />
                </div>
              )}
            </div>
            <p className="mt-2 text-xs text-gray-400">还可添加 {5 - customTags.length} 个自定义标签，不仅限于分类</p>
          </div>

          <div>
            <label className="mb-2 block text-sm font-medium text-gray-700">上传视频</label>
            <div
              className={`cursor-pointer rounded-xl border-2 border-dashed p-8 text-center transition-colors ${
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
                  if (file) {
                    setVideoFile(file);
                  }
                }}
              />
              <label htmlFor="video-upload" className="cursor-pointer">
                {videoFile ? (
                  <div className="flex items-center justify-center gap-3">
                    <Video className="h-8 w-8 text-emerald-500" />
                    <span className="font-medium text-emerald-600">{videoFile.name}</span>
                  </div>
                ) : (
                  <>
                    <Upload className="mx-auto mb-3 h-10 w-10 text-gray-400" />
                    <p className="mb-1 font-medium text-gray-600">点击或拖拽上传视频</p>
                    <p className="text-sm text-gray-400">支持 MP4、MOV、WEBM，按片上传，最大 500MB</p>
                  </>
                )}
              </label>
            </div>
          </div>

          <div>
            <label className="mb-2 block text-sm font-medium text-gray-700">封面图片</label>
            <div
              className={`cursor-pointer rounded-xl border-2 border-dashed p-8 text-center transition-colors ${
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
                  if (file) {
                    setCoverImage(file);
                  }
                }}
              />
              <label htmlFor="cover-upload" className="cursor-pointer">
                {coverImage ? (
                  <div className="flex items-center justify-center gap-3">
                    <Image className="h-8 w-8 text-emerald-500" />
                    <span className="font-medium text-emerald-600">{coverImage.name}</span>
                  </div>
                ) : (
                  <>
                    <Image className="mx-auto mb-3 h-10 w-10 text-gray-400" />
                    <p className="mb-1 font-medium text-gray-600">点击上传封面图片</p>
                    <p className="text-sm text-gray-400">支持 JPG、PNG、WEBP，最大 10MB</p>
                  </>
                )}
              </label>
            </div>
          </div>

          <div className="flex gap-3 pt-4">
            <Link
              to="/"
              className="flex-1 rounded-xl bg-gray-100 py-3.5 text-center font-medium text-gray-700 transition-colors hover:bg-gray-200"
            >
              取消
            </Link>
            <button
              type="submit"
              disabled={isSubmitting || isLoadingCategories || categories.length === 0}
              className="flex-1 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-500 py-3.5 font-semibold text-white shadow-lg transition-all hover:from-emerald-600 hover:to-teal-600 hover:shadow-xl disabled:cursor-not-allowed disabled:opacity-60"
            >
              {isSubmitting ? "处理中..." : "发布作品"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

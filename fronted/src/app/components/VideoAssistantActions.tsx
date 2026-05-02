interface VideoAssistantActionsProps {
  disabled?: boolean;
  practiceLoading?: boolean;
  onAnalyze: () => void;
  onGeneratePractice: () => void;
  onGenerateSummary: () => void;
}

export function VideoAssistantActions({
  disabled = false,
  practiceLoading = false,
  onAnalyze,
  onGeneratePractice,
  onGenerateSummary,
}: VideoAssistantActionsProps) {
  return (
    <div className="rounded-2xl border border-emerald-100 bg-emerald-50/70 p-3">
      <div className="mb-2 text-xs font-medium text-emerald-700">当前视频快捷动作</div>
      <div className="grid grid-cols-1 gap-2 sm:grid-cols-3">
        <button
          onClick={onAnalyze}
          disabled={disabled}
          className="rounded-xl border border-white/80 bg-white px-3 py-2 text-left text-sm text-gray-800 shadow-sm transition-colors hover:bg-emerald-50 disabled:cursor-not-allowed disabled:opacity-50"
        >
          解析当前视频
        </button>
        <button
          onClick={onGeneratePractice}
          disabled={disabled || practiceLoading}
          className="rounded-xl border border-white/80 bg-white px-3 py-2 text-left text-sm text-gray-800 shadow-sm transition-colors hover:bg-emerald-50 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {practiceLoading ? "正在生成练习..." : "生成同主题练习"}
        </button>
        <button
          onClick={onGenerateSummary}
          disabled={disabled}
          className="rounded-xl border border-white/80 bg-white px-3 py-2 text-left text-sm text-gray-800 shadow-sm transition-colors hover:bg-emerald-50 disabled:cursor-not-allowed disabled:opacity-50"
        >
          生成视频总结
        </button>
      </div>
    </div>
  );
}

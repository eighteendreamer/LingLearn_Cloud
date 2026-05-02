const DEFAULT_LANGUAGE = "zh-CN";
const ENGLISH_LANGUAGE_PREFIX = "en";

const exactTextMap = new Map<string, string>([
  ["首页", "Home"],
  ["发现", "Discover"],
  ["创作", "Create"],
  ["学习", "Learn"],
  ["我的", "Me"],
  ["保存", "Save"],
  ["保存中...", "Saving..."],
  ["编辑资料", "Edit Profile"],
  ["头像上传", "Upload Avatar"],
  ["头像上传中...", "Uploading avatar..."],
  ["头像已更新", "Avatar updated"],
  ["头像上传失败", "Avatar upload failed"],
  ["基本信息", "Basic Info"],
  ["昵称", "Display Name"],
  ["个人简介", "Bio"],
  ["职业", "Profession"],
  ["学习目标", "Learning Goal"],
  ["联系方式", "Contact Info"],
  ["邮箱", "Email"],
  ["手机号", "Phone"],
  ["所在地", "Location"],
  ["出生日期", "Birthday"],
  ["个人设置", "Settings"],
  ["个人信息", "Profile Info"],
  ["学习进度", "Learning Progress"],
  ["累计学习", "Total Learning"],
  ["累计学习时长", "Total Study Time"],
  ["退出登录", "Sign Out"],
  ["外观", "Appearance"],
  ["主题模式", "Theme"],
  ["浅色模式", "Light"],
  ["深色模式", "Dark"],
  ["跟随系统", "System"],
  ["语言", "Language"],
  ["界面语言", "Interface Language"],
  ["安全与隐私", "Security & Privacy"],
  ["双重验证", "Two-Factor Authentication"],
  ["资料公开", "Public Profile"],
  ["学习数据公开", "Learning Data Visibility"],
  ["通知提醒", "Notifications"],
  ["每日提醒", "Daily Reminder"],
  ["进度提醒", "Progress Updates"],
  ["成就徽章", "Achievement Badges"],
  ["周报推送", "Weekly Digest"],
  ["设置已保存", "Settings saved"],
  ["重置", "Reset"],
  ["个人中心", "Profile"],
  ["还没有登录", "Not Signed In"],
  ["去登录", "Go to Sign In"],
  ["获赞", "Likes"],
  ["关注", "Following"],
  ["粉丝", "Followers"],
  ["学习工具", "Learning Tools"],
  ["推荐", "Recommended"],
  ["进入", "Open"],
  ["作品", "Works"],
  ["偏好", "Preferences"],
  ["我的学习", "My Learning"],
  ["学习时长", "Study Time"],
  ["已收藏", "Saved"],
  ["连续天数", "Streak"],
  ["完成目标", "Goals Completed"],
  ["查看全部", "View All"],
  ["最近观看", "Recent Watch"],
  ["刚刚", "Just now"],
  ["在线练习", "Online Practice"],
  ["开始练习", "Start Practice"],
  ["选中", "Selected"],
  ["题目数", "Questions"],
  ["难度", "Difficulty"],
  ["分类", "Category"],
  ["学习报告", "Learning Report"],
  ["平均分数", "Average Score"],
  ["平均正确率", "Average Accuracy"],
  ["活跃天数", "Active Days"],
  ["练习次数", "Practice Sessions"],
  ["登录", "Sign In"],
  ["注册", "Sign Up"],
  ["账号", "Account"],
  ["密码", "Password"],
  ["确认密码", "Confirm Password"],
  ["用户名", "Username"],
  ["返回首页", "Back to Home"],
  ["页面走丢了", "Page Not Found"],
]);

const exactAttributeMap = new Map<string, string>([
  ["请输入昵称", "Enter your display name"],
  ["介绍一下你的学习方向和兴趣", "Tell us about your learning focus and interests"],
  ["请输入职业", "Enter your profession"],
  ["例如：一个月内完成前后端项目实战", "Example: Finish a full-stack project within one month"],
  ["请输入邮箱", "Enter your email"],
  ["请输入手机号", "Enter your phone number"],
  ["请输入所在地", "Enter your location"],
  ["请选择生日", "Choose your birthday"],
]);

type ReplacementRule = {
  pattern: RegExp;
  format: (match: RegExpExecArray) => string;
};

const replacementRules: ReplacementRule[] = [
  {
    pattern: /^连续学习\s*(\d+)\s*天$/u,
    format: ([, days]) => `${days} day${days === "1" ? "" : "s"} streak`,
  },
  {
    pattern: /^(\d+)\s*分钟$/u,
    format: ([, value]) => `${value} min`,
  },
  {
    pattern: /^(\d+)\s*小时$/u,
    format: ([, value]) => `${value} h`,
  },
  {
    pattern: /^(\d+)\s*天$/u,
    format: ([, value]) => `${value} day${value === "1" ? "" : "s"}`,
  },
  {
    pattern: /^(\d+)\s*个$/u,
    format: ([, value]) => value,
  },
  {
    pattern: /^已学习\s*(\d+)%$/u,
    format: ([, value]) => `${value}% learned`,
  },
  {
    pattern: /^(\d+)\s*分钟前$/u,
    format: ([, value]) => `${value} min ago`,
  },
  {
    pattern: /^(\d+)\s*小时前$/u,
    format: ([, value]) => `${value} h ago`,
  },
  {
    pattern: /^(\d+)\s*天前$/u,
    format: ([, value]) => `${value} d ago`,
  },
  {
    pattern: /^(\d+)\s*个工具可用$/u,
    format: ([, value]) => `${value} tools available`,
  },
  {
    pattern: /^累计学习\s*(\d+)\s*分钟$/u,
    format: ([, value]) => `Total Learning ${value} min`,
  },
];

const textOriginals = new WeakMap<Text, string>();
const attributeOriginals = new WeakMap<Element, Map<string, string>>();

let observer: MutationObserver | null = null;
let mutationLocked = false;
let activeLanguage = DEFAULT_LANGUAGE;

function canUseDom() {
  return typeof window !== "undefined" && typeof document !== "undefined";
}

function isEnglishLanguage(language: string) {
  return language.toLowerCase().startsWith(ENGLISH_LANGUAGE_PREFIX);
}

function preserveWhitespace(original: string, translated: string) {
  const leading = original.match(/^\s*/u)?.[0] ?? "";
  const trailing = original.match(/\s*$/u)?.[0] ?? "";
  return `${leading}${translated}${trailing}`;
}

function translateText(rawText: string) {
  const trimmed = rawText.trim();
  if (!trimmed) {
    return rawText;
  }

  if (exactTextMap.has(trimmed)) {
    return preserveWhitespace(rawText, exactTextMap.get(trimmed)!);
  }

  for (const rule of replacementRules) {
    const match = rule.pattern.exec(trimmed);
    if (match) {
      return preserveWhitespace(rawText, rule.format(match));
    }
  }

  return rawText;
}

function translateAttribute(rawText: string) {
  const trimmed = rawText.trim();
  if (!trimmed) {
    return rawText;
  }

  if (exactAttributeMap.has(trimmed)) {
    return preserveWhitespace(rawText, exactAttributeMap.get(trimmed)!);
  }

  return translateText(rawText);
}

function updateTextNode(node: Text) {
  if (!textOriginals.has(node)) {
    textOriginals.set(node, node.data);
  }

  const storedOriginal = textOriginals.get(node) ?? node.data;
  const storedTranslated = translateText(storedOriginal);
  if (node.data !== storedOriginal && node.data !== storedTranslated) {
    textOriginals.set(node, node.data);
  }

  const original = textOriginals.get(node) ?? node.data;
  const nextValue = isEnglishLanguage(activeLanguage) ? translateText(original) : original;
  if (node.data !== nextValue) {
    node.data = nextValue;
  }
}

function updateElementAttributes(element: Element) {
  const attributeNames = ["placeholder", "title", "aria-label"];
  let stored = attributeOriginals.get(element);

  for (const attributeName of attributeNames) {
    const currentValue = element.getAttribute(attributeName);
    if (currentValue == null) {
      continue;
    }

    if (!stored) {
      stored = new Map<string, string>();
      attributeOriginals.set(element, stored);
    }

    if (!stored.has(attributeName)) {
      stored.set(attributeName, currentValue);
    }

    const storedOriginal = stored.get(attributeName) ?? currentValue;
    const storedTranslated = translateAttribute(storedOriginal);
    if (currentValue !== storedOriginal && currentValue !== storedTranslated) {
      stored.set(attributeName, currentValue);
    }

    const original = stored.get(attributeName) ?? currentValue;
    const nextValue = isEnglishLanguage(activeLanguage)
      ? translateAttribute(original)
      : original;
    if (element.getAttribute(attributeName) !== nextValue) {
      element.setAttribute(attributeName, nextValue);
    }
  }
}

function walkNode(node: Node) {
  if (node.nodeType === Node.TEXT_NODE) {
    updateTextNode(node as Text);
    return;
  }

  if (node.nodeType !== Node.ELEMENT_NODE) {
    return;
  }

  const element = node as Element;
  updateElementAttributes(element);
  for (const childNode of Array.from(element.childNodes)) {
    walkNode(childNode);
  }
}

function syncDocumentText() {
  if (!canUseDom() || !document.body) {
    return;
  }

  mutationLocked = true;
  try {
    walkNode(document.body);
  } finally {
    mutationLocked = false;
  }
}

function ensureObserver() {
  if (!canUseDom() || observer) {
    return;
  }

  observer = new MutationObserver((mutations) => {
    if (mutationLocked) {
      return;
    }

    mutationLocked = true;
    try {
      for (const mutation of mutations) {
        if (mutation.type === "characterData") {
          updateTextNode(mutation.target as Text);
          continue;
        }

        if (mutation.type === "attributes" && mutation.target instanceof Element) {
          updateElementAttributes(mutation.target);
          continue;
        }

        if (mutation.type === "childList") {
          for (const addedNode of Array.from(mutation.addedNodes)) {
            walkNode(addedNode);
          }
        }
      }
    } finally {
      mutationLocked = false;
    }
  });

  observer.observe(document.body, {
    subtree: true,
    childList: true,
    characterData: true,
    attributes: true,
    attributeFilter: ["placeholder", "title", "aria-label"],
  });
}

function stopObserver() {
  observer?.disconnect();
  observer = null;
}

export function applyRuntimeLanguage(language: string) {
  if (!canUseDom()) {
    return;
  }

  activeLanguage = language || DEFAULT_LANGUAGE;
  syncDocumentText();

  if (isEnglishLanguage(activeLanguage)) {
    ensureObserver();
    return;
  }

  stopObserver();
}

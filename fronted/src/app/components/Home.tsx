import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

export function Home() {
  const weekData = [
    { day: "周一", hours: 2.5 },
    { day: "周二", hours: 3.2 },
    { day: "周三", hours: 1.8 },
    { day: "周四", hours: 4.1 },
    { day: "周五", hours: 3.5 },
    { day: "周六", hours: 5.2 },
    { day: "周日", hours: 4.8 },
  ];

  const courseData = [
    { month: "1月", count: 15 },
    { month: "2月", count: 19 },
    { month: "3月", count: 23 },
    { month: "4月", count: 28 },
  ];

  const upcomingClasses = [
    { time: "09:00", title: "Python编程基础", type: "在线课程", date: "15 March" },
    { time: "12:00", title: "数据结构与算法", type: "直播课", date: "15 March" },
    { time: "17:00", title: "Web开发实战", type: "录播课", date: "17 March" },
    { time: "02:00", title: "机器学习入门", type: "在线课程", date: "18 March" },
    { time: "03:00", title: "数据库设计", type: "直播课", date: "20 March" },
  ];

  const notices = [
    {
      title: "本周作业提交截止时间",
      date: "Wed, Feb 24, 2021 - 12:00 pm - 1:00 pm",
      img: "/api/placeholder/60/60",
    },
    {
      title: "新课程上线通知",
      date: "Wed, Feb 24, 2021 - 12:00 pm - 1:00 pm",
      img: "/api/placeholder/60/60",
    },
    {
      title: "期末考试安排",
      date: "Wed, Feb 24, 2021 - 12:00 pm - 1:00 pm",
      img: "/api/placeholder/60/60",
    },
  ];

  return (
    <div className="p-8 max-w-7xl mx-auto">
      <div className="mb-6">
        <h1 className="text-2xl font-semibold text-gray-800">总览</h1>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
        <div className="bg-white rounded-xl p-6 shadow-sm">
          <div className="text-sm text-gray-500 mb-2">学习总数</div>
          <div className="text-4xl font-bold text-gray-800 mb-4">930</div>
          <ResponsiveContainer width="100%" height={60}>
            <BarChart data={weekData}>
              <Bar dataKey="hours" fill="#fb923c" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white rounded-xl p-6 shadow-sm">
          <div className="text-sm text-gray-500 mb-2">课程数</div>
          <div className="text-4xl font-bold text-gray-800 mb-4">19</div>
          <ResponsiveContainer width="100%" height={60}>
            <LineChart data={courseData}>
              <Line type="monotone" dataKey="count" stroke="#10b981" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white rounded-xl p-6 shadow-sm">
          <div className="text-sm text-gray-500 mb-2">分配课程</div>
          <div className="text-4xl font-bold text-gray-800 mb-4">04</div>
          <ResponsiveContainer width="100%" height={60}>
            <BarChart data={[{ v: 3 }, { v: 5 }, { v: 4 }, { v: 6 }, { v: 3 }, { v: 4 }]}>
              <Bar dataKey="v" fill="#fbbf24" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-white rounded-xl p-6 shadow-sm">
          <h3 className="font-semibold text-gray-800 mb-4">课程设计</h3>
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={[
              { month: "Mon", value: 30 },
              { month: "Tue", value: 45 },
              { month: "Wed", value: 28 },
              { month: "Thu", value: 60 },
              { month: "Fri", value: 48 },
              { month: "Sat", value: 75 },
              { month: "Sun", value: 65 },
            ]}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="month" stroke="#999" />
              <YAxis stroke="#999" />
              <Tooltip />
              <Line type="monotone" dataKey="value" stroke="#10b981" strokeWidth={3} dot={{ fill: "#10b981", r: 4 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white rounded-xl p-6 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold text-gray-800">即将开始的课程</h3>
            <span className="text-xs text-gray-500">15 March</span>
          </div>
          <div className="space-y-3 max-h-64 overflow-y-auto">
            {upcomingClasses.map((cls, idx) => (
              <div key={idx} className="flex items-start gap-3 pb-3 border-b border-gray-100 last:border-0">
                <div className="text-emerald-500 font-semibold text-sm mt-1">{cls.time}</div>
                <div className="flex-1">
                  <div className="text-sm font-medium text-gray-800">{cls.title}</div>
                  <div className="text-xs text-gray-500">{cls.type}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
        <div className="bg-white rounded-xl p-6 shadow-sm">
          <h3 className="font-semibold text-gray-800 mb-4">通知板</h3>
          <div className="space-y-4">
            {notices.map((notice, idx) => (
              <div key={idx} className="flex gap-4 items-start">
                <div className="w-12 h-12 bg-emerald-100 rounded-lg flex-shrink-0"></div>
                <div className="flex-1">
                  <h4 className="text-sm font-medium text-gray-800">{notice.title}</h4>
                  <p className="text-xs text-gray-500 mt-1">{notice.date}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white rounded-xl p-6 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold text-gray-800">考试安排</h3>
            <span className="text-xs text-gray-500">March, 2021</span>
          </div>
          <div className="grid grid-cols-7 gap-2 mb-4">
            {["一", "二", "三", "四", "五", "六", "日"].map((day) => (
              <div key={day} className="text-center text-xs text-gray-500 font-medium">
                {day}
              </div>
            ))}
          </div>
          <div className="grid grid-cols-7 gap-2">
            {Array.from({ length: 35 }, (_, i) => {
              const day = i - 0;
              const isToday = day === 16;
              const hasExam = [8, 13, 20, 27].includes(day);
              return (
                <div
                  key={i}
                  className={`aspect-square flex items-center justify-center text-sm rounded-lg ${
                    isToday
                      ? "bg-emerald-500 text-white font-bold"
                      : hasExam
                      ? "bg-emerald-50 text-emerald-600 font-semibold"
                      : day > 0 && day <= 31
                      ? "text-gray-700"
                      : "text-gray-300"
                  }`}
                >
                  {day > 0 && day <= 31 ? day : ""}
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}

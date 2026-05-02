from app.modules.practice.service import PracticeService


def test_normalize_generated_bank_keeps_valid_questions() -> None:
    normalized = PracticeService._normalize_generated_bank(
        {
            "bank_title": "MySQL 安装练习",
            "bank_description": "围绕安装与启动生成练习。",
            "difficulty": "medium",
            "questions": [
                {
                    "question_type": "single_choice",
                    "content": "安装 MySQL 演示中使用的服务名是什么？",
                    "difficulty": "easy",
                    "explanation": "安装时将服务名配置为 MySQL80。",
                    "options": [
                        {"content": "MySQL57", "is_correct": False},
                        {"content": "MySQL80", "is_correct": True},
                        {"content": "mysql", "is_correct": False},
                        {"content": "db80", "is_correct": False},
                    ],
                },
                {
                    "question_type": "single_choice",
                    "content": "命令行启动 MySQL 服务的命令是？",
                    "difficulty": "easy",
                    "explanation": "Windows 下可使用 net start MySQL80。",
                    "options": [
                        {"content": "mysql start", "is_correct": False},
                        {"content": "service mysql start", "is_correct": False},
                        {"content": "net start MySQL80", "is_correct": True},
                        {"content": "systemctl start mysql", "is_correct": False},
                    ],
                },
                {
                    "question_type": "single_choice",
                    "content": "连接 MySQL 的命令是？",
                    "difficulty": "easy",
                    "explanation": "可在命令行使用 mysql -u root -p。",
                    "options": [
                        {"content": "mysql -u root -p", "is_correct": True},
                        {"content": "mysql root login", "is_correct": False},
                        {"content": "sql -root -p", "is_correct": False},
                        {"content": "connect mysql root", "is_correct": False},
                    ],
                },
            ],
        },
        fallback_title="MySQL",
        fallback_summary="summary",
        question_count=3,
    )

    assert normalized["bank_title"] == "MySQL 安装练习"
    assert len(normalized["questions"]) == 3
    assert normalized["questions"][0]["question_type"] == "single_choice"
    assert normalized["questions"][0]["options"][1]["option_key"] == "B"


def test_normalize_generated_bank_converts_multi_correct_to_multiple_choice() -> None:
    normalized = PracticeService._normalize_generated_bank(
        {
            "questions": [
                {
                    "question_type": "single_choice",
                    "content": "哪些方式可以启动 MySQL 服务？",
                    "options": [
                        {"content": "services.msc", "is_correct": True},
                        {"content": "net start MySQL80", "is_correct": True},
                        {"content": "删除 data 目录", "is_correct": False},
                        {"content": "修改 hosts 文件", "is_correct": False},
                    ],
                },
                {
                    "question_type": "single_choice",
                    "content": "连接命令需要哪些信息？",
                    "options": [
                        {"content": "用户名", "is_correct": True},
                        {"content": "密码", "is_correct": True},
                        {"content": "显卡驱动", "is_correct": False},
                        {"content": "浏览器插件", "is_correct": False},
                    ],
                },
                {
                    "question_type": "single_choice",
                    "content": "表在数据模型中的作用是什么？",
                    "options": [
                        {"content": "存储数据", "is_correct": True},
                        {"content": "管理显示器", "is_correct": False},
                        {"content": "编译 SQL", "is_correct": False},
                        {"content": "启动操作系统", "is_correct": False},
                    ],
                },
            ]
        },
        fallback_title="MySQL",
        fallback_summary="summary",
        question_count=3,
    )

    assert normalized["questions"][0]["question_type"] == "multiple_choice"

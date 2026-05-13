# 每日备忘录与任务管理

一个使用 Python 标准库 Tkinter 实现的本地桌面小工具。当前版本主打“按日期管理待办任务”，数据使用 SQLite 保存在本地。

## 运行

```powershell
cd F:\python\daily_memo_app
python main.py
```

## 当前功能

- 顶部显示当前选择日期
- 点击日历图标展开月历并选择日期
- 待办区域为空时显示“今日还没有代办任务”
- 点击空白区域新增代办
- 每个代办支持标题和具体内容
- 代办以圆角小卡片显示
- 点击代办卡片进入编辑页面
- 编辑页面左上角删除，右上角完成
- 待办过多时可使用鼠标滚轮滚动查看
- 数据保存在本地 SQLite 数据库

## 数据位置

```text
F:\python\daily_memo_app\data\daily_memo.db
```

## 打包

安装 PyInstaller 后可执行：

```powershell
pyinstaller --noconsole --onefile --name DailyMemo main.py
```

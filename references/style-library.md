# 风格库（小红书 3:4 知识卡片 · 1080×1440 样卡实测）

共 8 套成对风格（每套 `cards/styles*/{name}-cover.html` 封面 + `{name}-page.html` 内容页），另有原版暖米白荧光笔风格。写新卡时：选定风格 → 参照样卡 token（底色/强调色/字体/圆角/边框）与结构骨架 → 写完必跑 `scripts/check-overflow.py`。预览墙 `gallery.html` 由 `scripts/build-gallery.py` 扫描生成，新风格需在脚本的 STYLES 表登记。

## 封面统一约定（2026.9 审查后定稿）

- 大标题 90–116px、900 字重，位置略偏左但不贴边（左侧留白比右侧多 ~30-40px，微居中）
- 中文钩子「AI 写代码快到飞起，先崩掉的是流程」为主视觉，英文/风格术语只能做辅助元素
- 下半屏必须有内容型装饰承接（阶段序列/目录/数据格/水印），不允许大面积死区
- CTA 统一「左滑开拆 →」；背书统一「Anthropic 官方 · 2026.8」

## 8 套风格总表

| 风格 | 底色 | 强调色 | 关键元素 |
|---|---|---|---|
| Brutal 新粗野 | #f2efe9 | 黄 #ffd02f / 粉 #ff5d8f / 蓝 #4d9de0 | 4px 黑框、硬阴影、撞色块、mono 点缀 |
| Terminal 终端（浅白） | #eef1f5 窗外 / #fff 窗内 | 绿 #1a7f37 / 蓝 #0550ae / 紫 #8250df / 琥珀 #bf8700 | 等宽、窗口 chrome、prompt、代码块 |
| Editorial 杂志编辑 | #f7f4ee | 朱红 #c8321e | 宋体大标题、报头、细规则线、目录栏 |
| Zen 日式极简 | #f4f2ed | 朱红 #c73e3a | 细线框、竖排侧注、印章、「環」字水印 |
| Bento 便当盒 | #f3f1ec | 黄 #ffd43b / 绿 #8be28f / 黑卡 | 大圆角模块、黑色大 hero 卡突出主体 |
| Swiss 瑞士网格 | #ffffff | 红 #e0311d / 黑 | 大号无衬线、红方块、十字标记、描边数字 |
| Memphis 孟菲斯 | #fffdf6 | 黄 #ffd166 / 粉 #ef476f / 青 #06d6a0 / 蓝 #118ab2 | 几何贴纸按网格布点、黑框彩底行、S1-S6 色块串 |
| Doodle 手绘 | 纸纹 #f9f3e6 | 墨 #3b3a36 / 红铅笔 #d95763 / 蓝笔 #4a69bd / 荧光黄 #f7d774 | 楷体手写标题、歪扭圆角手绘框(border-radius 不规则)、胶带、波浪红下划线、马克笔高亮 |

原版风格（暖米白荧光笔：#faf6ef 底 / #ffd591 荧光标记 / #d4570e 强调橙）见 `cards/sdlc-xhs-01.html`。

## 封面/内容页分工约定（第二轮起）

- **封面**：kicker 胶囊/标签 + 超大主标题（88–118px）+ 可选一句副标题 + 极少装饰 + 底部引导（SWIPE→/左滑开拆）。元素 ≤6 组，一眼读完主题。
- **内容页**：每行一个知识点（序号+名称+一句话+产物 tag），正文 22–25px，行距 ≥1.4；每页 ≤7 个条目，宁可拆页不要压缩。

## 实测坑（新增）

- **全幅装饰层会触发溢出误报**：`position:absolute; inset:0` 的纸纹/光晕 div 会被 check-overflow 判 OVERFLOW。改成 body 的多层 background（repeating/radial-gradient 叠加）实现，视觉等价且不进 DOM 测量。见 riso / glass 样卡。
- **套版错位字用 text-shadow**：`::after content:attr(data-t)` 绝对定位在多行标题换行处会错乱；`text-shadow:6px 6px 0 <色>` 永远跟随基线，riso 标准做法。
- **装饰图形必须整体落在 40px 安全区内**：绝对定位的圆/三角按元素 rect 计量，压边即 OVERFLOW。
- 内容页吸底彩色结论框触发 quality-check「底部条带杂色」WARN 属已知误报，以 check-overflow 通过为准（同 SKILL.md 既有记录）。

# 风格库（小红书 3:4 知识卡片 · 1080×1440 样卡实测）

共 10 套成对风格（每套 `cards/styles*/{name}-cover.html` 封面 + `{name}-page.html` 内容页），另有原版暖米白荧光笔风格。写新卡时：选定风格 → 参照样卡 token（底色/强调色/字体/圆角/边框）与结构骨架 → 写完必跑 `scripts/check-overflow.py`。预览墙 `gallery.html` 由 `scripts/build-gallery.py` 扫描生成，新风格需在脚本的 STYLES 表登记。

## 10 套风格总表

| 风格 | 底色 | 强调色 | 关键元素 |
|---|---|---|---|
| Brutal 新粗野 | #f2efe9 | 黄 #ffd02f / 粉 #ff5d8f / 蓝 #4d9de0 | 4px 黑框、硬阴影、撞色块、mono 点缀 |
| Terminal 终端 | #0a0e14 | 绿 #3fb950 / 蓝 #79c0ff / 紫 #d2a8ff | 全等宽、窗口 chrome、prompt、光标 |
| Editorial 杂志编辑 | #f7f4ee | 朱红 #c8321e | 宋体大标题、报头、细规则线、罗马数字 |
| Zen 日式极简 | #f4f2ed | 朱红 #c73e3a | 细线框、竖排侧注、印章、大留白 |
| Glass 玻璃拟态 | 深紫渐变+光晕 | 紫罗兰→青渐变 | 磨砂卡(rgba白+backdrop-blur)、渐变字、大数字格 |
| Bento 便当盒 | #f3f1ec | 黄 #ffd43b / 绿 #8be28f / 橙 #ff5c38 / 黑卡 | 大圆角模块、大数字统计格、深色 hero 格 |
| Swiss 瑞士网格 | #ffffff | 红 #e0311d / 黑 | 大号无衬线、红色方块、十字标记、粗规则线 |
| Riso 双色印刷 | 纸感 #fbf6ea | 蓝 #1d3fa3 / 荧光粉 #ff4d6d | 半调网点、套版错位字(text-shadow)、双色条 |
| Memphis 孟菲斯 | #fffdf6 | 黄 #ffd166 / 粉 #ef476f / 青 #06d6a0 / 蓝 #118ab2 | 几何贴纸、黑框彩底行、之齿分隔 |
| Art Deco 装饰艺术 | 墨绿渐变 #0f241d | 金 #d4af37 / 象牙 #f2ead8 | 双线金框、扇形放射、菱形分隔、衬线居中 |

原版风格（暖米白荧光笔：#faf6ef 底 / #ffd591 荧光标记 / #d4570e 强调橙）见 `cards/sdlc-xhs-01.html`。

## 封面/内容页分工约定（第二轮起）

- **封面**：kicker 胶囊/标签 + 超大主标题（88–118px）+ 可选一句副标题 + 极少装饰 + 底部引导（SWIPE→/左滑开拆）。元素 ≤6 组，一眼读完主题。
- **内容页**：每行一个知识点（序号+名称+一句话+产物 tag），正文 22–25px，行距 ≥1.4；每页 ≤7 个条目，宁可拆页不要压缩。

## 实测坑（新增）

- **全幅装饰层会触发溢出误报**：`position:absolute; inset:0` 的纸纹/光晕 div 会被 check-overflow 判 OVERFLOW。改成 body 的多层 background（repeating/radial-gradient 叠加）实现，视觉等价且不进 DOM 测量。见 riso / glass 样卡。
- **套版错位字用 text-shadow**：`::after content:attr(data-t)` 绝对定位在多行标题换行处会错乱；`text-shadow:6px 6px 0 <色>` 永远跟随基线，riso 标准做法。
- **装饰图形必须整体落在 40px 安全区内**：绝对定位的圆/三角按元素 rect 计量，压边即 OVERFLOW。
- 内容页吸底彩色结论框触发 quality-check「底部条带杂色」WARN 属已知误报，以 check-overflow 通过为准（同 SKILL.md 既有记录）。

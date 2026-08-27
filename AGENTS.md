# asymptote-zh 工作指南

Asymptote 官方手册（`asymptote.pdf`）中文翻译项目。源文档为 **Texinfo** 格式
（上游 `vectorgraphics/asymptote` 仓库的 `doc/` 目录，基准为 `asy-doc-latest/`）。

本工作流由 `tex-manual-translation` skill（LaTeX 版）适配为 Texinfo 版：
翻译纪律、术语表、检查脚本方法论照搬；构建链、中文环境、元素规则按下文本项目化。

## 0. 文件布局与编辑权限

asy-doc-latest/          上游最新版基准（翻译以此为准，只读）
                         ——当前 asymptote-zh.texi 已同步至该版本
asy-doc/                 上游旧版存档（只读；历史对照用）
asy-doc-latest/ 其余资产与 asy-doc 相同处沿用根目录现有副本
asymptote.en.texi        英文原版快照（review 与对照用，只读）
asymptote-zh.pdf         最终产物（214 页）
version.texi             已自建：@set VERSION 3.14git / Datadir / Docdir
txi-zh.tex               字体覆盖层（中文思源宋体 + 西文 Libertinus/LMMono）
latexusage.pdf           抽取的缺图（来自官方 asymptote.pdf 第 120 页）
*.asy *.pdf options …    构建依赖（@verbatiminclude/@image 引用），只读
scripts/                 check_env_balance.py、find_at_before_cjk.py、
                         find_untranslated.py、texindex-mini.py
glossary.md              术语表（含 140+ 条目），后续修订时共享维护
```

除 `asymptote-zh.texi`、`glossary.md`、`scripts/`、`AGENTS.md` 外的一切保持只读。
若发现缺依赖文件，从 `asy-doc-latest/` 复制到根目录，不动原目录。

## 1. 构建工作流（已端到端验证，约 10 秒/轮）

环境：TeX Live 2026（xetex、libertinus-fonts、lm、zhspacing 均在发行版内）；
系统字体 `C:\Windows\Fonts\NotoSerifCJKsc-Regular.otf` 与 `simkai.ttf`。

在仓库根目录：

```bash
xetex -interaction=nonstopmode asymptote-zh.texi
python scripts/texindex-mini.py asymptote-zh.cp
xetex -interaction=nonstopmode asymptote-zh.texi
python scripts/texindex-mini.py asymptote-zh.cp
xetex -interaction=nonstopmode asymptote-zh.texi
```

验收：`grep -c '^!' asymptote-zh.log` 为 0；译稿基准约 **214 页**（中文较
英文紧凑；英文 Libertinus 基准为 225 页）。抽查：`pdftoppm -png -r 60 -f N -l N
asymptote-zh.pdf pg` 渲染目检。**禁止改用 pdftex**（中文会被整体丢弃）；
编译失败时**先删中间文件再重试**；禁止 `--shell-escape` 类危险选项。

## 2. 字体栈（已配置，勿动）

| 用途 | 字体 | 来源 |
|---|---|---|
| 中文 | 思源宋体 Noto Serif CJK SC / 楷体 | Windows 系统字体 |
| 西文衬线 rm/it/bf/sl/sc | Libertinus Serif（+onum 旧式数字，sc 加 +smcp） | TeX Live libertinus-fonts |
| 西文无衬线 sf | Libertinus Sans | 同上 |
| 等宽 tt | Latin Modern Mono | TeX Live lm |
| 数学 | Computer Modern（默认保留） | TeX Live |

实现于根目录 `txi-zh.tex`：覆盖 `\setfont` 一处生效全部字号组；XeTeX 文件名
字体必须用 `"[文件.otf]:features"` 方括号语法；`\dimexpr` 尺寸计算必须先除后乘
（先乘会在大字号溢出 16384pt 上限）。图内文字字体来自嵌入 PDF 本身，随图走。

`txi-zh.tex` 还含四项关键补丁（改动前先理解，删掉会退化）：
1. **粗体形态映射**：texinfo.tex 的标题字号组用 `\rmbshape`/`\itbshape`/
   `\slbshape`/`\sfbshape`/`\scbshape`（bx 系粗体形态），`\westfontfile` 必须映射
   全部九种 shape，否则标题西文落入 `cmr10` 兜底变成 Computer Modern。
2. **中西边界胶水**：zhspacing 的 `\zhs@skipsp@ces` 在空格被吃掉后仅当下一
   token 为字母/其他字符时补 `\skipenzh`；遇 `{`（内联 `@code{}`）或控制序列
   （`@math` 等）时空格已消且无胶水 → 零间距。已加终极 else 分支统一补
   `\skipenzh`（0.25em）。
3. **无组字体保存/恢复**：zhspacing 的 `\zhgroupsavefont` 用
   `\begingroup/\endgroup` 对，在列表边界处会失衡（"Missing }"）；已改为
   `\edef\zhs@savedfont{\the\font}` 捕获-重选方案。
4. **CJK 字体词间距**：Noto/楷体的 `fontdimen2=0`，`\tclose` 会把它传给
   `\spaceskip`；已对全部 mc/gt 字体控制序列按各自 quad 写入 0.25em。

**catcode 陷阱**：txi-zh.tex 在 `\globaldefs=1` 下被 `\input`，补丁中含 `@` 的
宏名必须包在 `{\catcode64=11 ... \catcode64=0 }` 中（显式恢复，组的隐式恢复在
globaldefs 下失效；且 `@` 此时是转义符，`` `\@ `` 取不到字符码，只能用数值 64）。

## 3. 翻译纪律（逐字翻译）

这是**由 AI 逐字执行的翻译任务**：逐段阅读英文原文，理解含义，用中文重新表达，
逐行编辑写入译文。**不得用正则替换等自动化批量工具翻译正文**；脚本只用于检查。

### 任务分解

用 todo 按 `@chapter`（共 20 章）建立任务列表，顺序推进，完成一章标记一章。

### 翻译范围（Texinfo 元素规则）

**不译（保留英文原样）**：
- 所有代码环境与代码命令：`@example`、`@verbatim`、`@verbatiminclude` 引入的
  86 个 `.asy` 文件（含其中注释——本项目明确约定**画图代码内注释不翻译**，
  `.asy` 文件零改动）、`@code`、`@env`、`@file`、`@command`、`@option`、
  `@kbd`、`@key`、`@samp`、`@var` 内容
- 结构键：`@node` 名、`@menu`/`@detailmenu` 条目、`@xref/@pxref/@ref` 的
  节点参数、`@anchor{}`、`@cindex` 等索引排序键（中文说明如需可另加新条目，
  不改原键）、`@value{}` 引用
- 工具名、模块名、文件名、命令行选项、键名与选项值（术语表 §glossary）

**要译**：
- `@chapter/@section/@subsection` 标题文本（Texinfo 无 texorpdfstring 机制，
  标题自动进 PDF 书签，直接译即可）
- 正文段落、`@quotation` 内文字、`@table/@itemize/@enumerate` 的 `@item`
  类别名与描述、`@deffn` 类命令行的说明部分（函数名参数保留）
- `@footnote{}` 按正文译；`@uref{url,显示文本}` URL 不译、显示文本译；
  `@acronym{PDF}` 首次出现译全称时可写「便携文档格式(PDF)」

### 术语一致性

严格遵循 `glossary.md`；无对应译名保留英文；专有名词首次出现括注英文，
如「引导(guide)」。

### 标点与编辑规则

- 正文全角标点（，。：；），代码/命令紧邻处用半角括号；省略号用 `……`
- **黄金法则**：编辑只改文本行，绝不动 `@end xxx`、`@menu`、`@node` 等
  结构行；替换范围内若含结构标记，必须在替换正文原样写回
- 行号以最近一次工具响应为准，绝不凭记忆（编辑会重排全部行号）
- 中文标点前不留 `\`（`@math`/`@tex` 内）；`@` 后不直接跟中文字符
  （`@，` 会被解析为未定义命令）——用 §4 脚本检测

### 界面词

「章/节/附录/见/页」等功能词由 `@documentlanguage zh_CN` 经 txi-zh.tex
自动汉化，正文不要手工重复翻译。

## 4. 每章验证关卡

每译完一章：

1. `python scripts/check_env_balance.py asymptote-zh.texi`
   —— `@env`/`@end env` 配对（11 种环境）
2. `python scripts/find_at_before_cjk.py asymptote-zh.texi`
   —— 检出 `@中文` / `\中文` 会导致的未定义命令
3. `python scripts/find_untranslated.py asymptote-zh.texi`
   —— 代码环境外 5+ 连续英文词，疑似漏译
4. 跑 §1 完整三遍编译，log 零 `!` 错误

编译报错先对照英文原版查环境标记；脚本 1 定位丢失标记，脚本 2 定位坏转义，
修复后重编译。未定义引用类警告在交叉引用章翻译完前属正常。

## 5. 大文档并行化

按 `@chapter`/`@section` 标题拆给子代理，各自逐字翻译负责的章节。
上游翻译推进会使行号持续漂移——**子代理必须搜索章节标题定位，不依赖行号**。
所有子代理共享根目录 `glossary.md` 保持术语一致；每章完成后由主会话跑 §4
关卡再合并推进。

## 6. 已知事项

- `version.texi` 上游构建时生成、仓库无：已自建；版本号取自上游 master 的
  `configure.ac`（`AC_INIT`，当前为 3.14git，快照与 master 的 doc 逐字节一致）。
  上游发新版后同步快照时仅需改此值重编译
- `latexusage.pdf` 唯一缺图，抽取自仓库官方 `asymptote.pdf` 第 120 页
- `texi2any` 在 Windows TeX Live 不存在；出 PDF 一律走 §1 xetex 手动流程。
  需要 node/menu 静态检查时可 `wsl sudo apt install texinfo` 辅助校验
- 索引由 `texindex-mini.py` 合并（含 `@subentry` 二级条目），输出
  `@entry{文本}{页码}`/`@secondary`/`@initial` 格式；**.cps 首行不得以
  `\` 开头**（texinfo.tex 按旧格式拒读）
- `@node Top` 与下一个 `@node` 之间的内容在 TeX 输出中按设计丢弃
  （官方用于跳过 `@ifnottex` 段）——正文永远写在真实章节内
- 索引排序键保持英文，mini-texindex 按字节排序；如新增中文 `@cindex`
  条目，排序将落在字母区之后，可接受

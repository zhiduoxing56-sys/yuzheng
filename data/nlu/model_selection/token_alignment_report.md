# SYS-014 Stage 4A Tokenizer / Span 对齐报告

权威标注保持 raw Unicode `[char_start, char_end)`；token BIO 仅动态派生，不回写冻结数据。

## hfl/chinese-electra-180g-small-discriminator

- tokenizer fast：`True`
- 抽样数：`206`
- 覆盖：`{"AREA": 124, "VALUE": 88, "NEGATION": 69, "MULTI": 52}`
- TOKEN_ALIGNMENT_FAILURES：`0`

未发现失败样本。

## hfl/rbt3

- tokenizer fast：`True`
- 抽样数：`206`
- 覆盖：`{"AREA": 124, "VALUE": 88, "NEGATION": 69, "MULTI": 52}`
- TOKEN_ALIGNMENT_FAILURES：`0`

未发现失败样本。

## hfl/chinese-macbert-base

- tokenizer fast：`True`
- 抽样数：`206`
- 覆盖：`{"AREA": 124, "VALUE": 88, "NEGATION": 69, "MULTI": 52}`
- TOKEN_ALIGNMENT_FAILURES：`0`

未发现失败样本。

## 结论

BIO 投影只在 tokenizer 阶段产生；任何失败均作为模型兼容性证据，不修改 frozen annotation。

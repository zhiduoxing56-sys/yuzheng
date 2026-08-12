# RBT3 exp001 Negation 诊断

## Epoch 5 结论

- NEGATED recall：`0.708333`（support=24）
- HEADLIGHT_OFF negated recall：`0.000000`
- ACCELERATE negated recall：`0.600000`
- Sentence Negation Head 漏判：`7`
- Sentence/NEGATION Slot 不一致：`9`
- `NEGATION_DIAGNOSIS_REQUIRED = YES`

## Sentence Negation Head 漏判样本

- `SYS014-POC-0546` `不要把前照灯关掉`：intent=HEADLIGHT_OFF，marker=不要，sentence=NOT_NEGATED，NEGATION slot detected=YES
- `SYS014-POC-0547` `别把前照灯关掉`：intent=HEADLIGHT_OFF，marker=别，sentence=NOT_NEGATED，NEGATION slot detected=YES
- `SYS014-POC-0548` `先别把前照灯关掉`：intent=HEADLIGHT_OFF，marker=先别，sentence=NOT_NEGATED，NEGATION slot detected=YES
- `SYS014-POC-0549` `不用把前照灯关掉`：intent=HEADLIGHT_OFF，marker=不用，sentence=NOT_NEGATED，NEGATION slot detected=YES
- `SYS014-POC-0550` `请勿把前照灯关掉`：intent=HEADLIGHT_OFF，marker=请勿，sentence=NOT_NEGATED，NEGATION slot detected=YES
- `SYS014-POC-0566` `不用再提点速度`：intent=ACCELERATE，marker=不用，sentence=NOT_NEGATED，NEGATION slot detected=YES
- `SYS014-POC-0567` `请勿再提点速度`：intent=ACCELERATE，marker=请勿，sentence=NOT_NEGATED，NEGATION slot detected=NO

## Sentence Head 与 NEGATION Slot Head 不一致

- `SYS014-POC-0546` `不要把前照灯关掉`：sentence=NOT_NEGATED，slot detected=YES
- `SYS014-POC-0547` `别把前照灯关掉`：sentence=NOT_NEGATED，slot detected=YES
- `SYS014-POC-0548` `先别把前照灯关掉`：sentence=NOT_NEGATED，slot detected=YES
- `SYS014-POC-0549` `不用把前照灯关掉`：sentence=NOT_NEGATED，slot detected=YES
- `SYS014-POC-0550` `请勿把前照灯关掉`：sentence=NOT_NEGATED，slot detected=YES
- `SYS014-POC-0564` `别再提点速度`：sentence=NEGATED，slot detected=NO
- `SYS014-POC-0565` `先别再提点速度`：sentence=NEGATED，slot detected=NO
- `SYS014-POC-0566` `不用再提点速度`：sentence=NOT_NEGATED，slot detected=YES
- `SYS014-POC-0584` `请勿踩刹车`：sentence=NEGATED，slot detected=NO

## 模板集中性

`{"ACCELERATE|不用": 1, "ACCELERATE|请勿": 1, "HEADLIGHT_OFF|不用": 1, "HEADLIGHT_OFF|不要": 1, "HEADLIGHT_OFF|先别": 1, "HEADLIGHT_OFF|别": 1, "HEADLIGHT_OFF|请勿": 1}`

短板集中在 HEADLIGHT_OFF 的否定模板和 ACCELERATE 的部分“不用/请勿”模板。Sentence Head 与 Slot Head 并非始终一致，因此不能用其中一个 head 的 argmax替代另一个安全信号。本阶段没有修改冻结数据。

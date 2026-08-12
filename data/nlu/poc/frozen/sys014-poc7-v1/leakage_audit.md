# sys014-poc7-v1 泄漏审计

| 检查项 | 计数 | 结果 |
|---|---|---|
| exact_cross_split_duplicates | 0 | PASS |
| normalized_cross_split_duplicates | 0 | PASS |
| template_signature_cross_split_duplicates | 0 | PASS |
| mechanical_near_duplicate_cross_split_failures | 0 | PASS |
| family_leakage_failures | 0 | PASS |
| split_group_leakage_failures | 0 | PASS |
| test_asset_in_train | 0 | PASS |
| unassigned_count | 0 | PASS |

- split group assignment digest: `194f3b12d4e67f8c84711a27a9a5ce292d1155e6e460254cf6d76aabf2658f9b`
- 分组边：paraphrase family、template signature、mechanical signature。
- Safety Gold 未参与 group 切分，且与 TRAIN/VALIDATION/TEST 全局去重。
- 所有指标必须为 0 才能冻结。

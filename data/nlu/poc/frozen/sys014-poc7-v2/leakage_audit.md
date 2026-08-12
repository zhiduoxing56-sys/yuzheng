# sys014-poc7-v2 泄漏审计

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

- split group assignment digest: `3edffd92d72f25c2884a0c366ecc18e77c1c1d150f4bdcb0a668010c204a6482`
- 分组边：refined synthetic family、slot-aware template signature、mechanical near-duplicate signature。
- TEST_ASSET group 强制进入 TEST；Safety Gold 完全不参与切分优化。
- 所有泄漏指标为 0。

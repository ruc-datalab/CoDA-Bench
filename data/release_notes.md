# Dataset release 1.0.1 — 2026-09-29

Fixes GitHub issue #1: source-community names were used without their source type, causing expand and filter communities with the same numeric name to collide. This release restores complete source identifiers, corrects 186 full-split mappings (including 16 hard tasks), and adds 18 previously omitted archives. Existing archive bytes are unchanged.

Full/hard task counts and instance IDs remain 1,009/119. The full release uses 49 communities; the hard subset uses 22. Both task files retain the Hugging Face question, answer, and answer-guideline content; GitHub is synchronized to that version. Reference-code input paths are made portable where the intended path resolves uniquely inside the corrected archive. A mapping correction changes the evaluation environment and previous results must retain their original dataset revision; this release does not claim that historical scores are unchanged.

For hard IDs 0 and 1 (full IDs 39 and 44), use community_4.tar.zst. Both reference programs were executed and reproduced their recorded answers. Full IDs 92 and 93 were traced to the original google-job-skills notebook, assigned to community_5, and executed successfully against that archive.

## Upgrade

Update the GitHub checkout and run `python scripts/setup_dataset.py --data-dir ./datasets`. Metadata is always refreshed, missing archives are downloaded, and all installed archives are checked against the SHA-256 manifest. Unchanged verified archives can be reused. Use `--revision <HF commit SHA>` to pin a release. Partial installation: `--community community_4` (repeat for more communities).

Data is extracted to `datasets/communities/community_N/full_community`, which matches the evaluation runner. Source mappings and archive checksums are included in both repositories; large archives are distributed on Hugging Face.

## Validation scope and remaining limitations

All 49 archives passed full SHA-256 verification. Dependency paths were inspected for all 187 remapped tasks. This is not a complete re-evaluation of all reference programs or answer correctness. Some existing programs use external downloads, embedded/fallback data, or unresolved non-source paths (notably full IDs 111 and 136); these are separate reference-code quality issues and are not silently replaced with guessed data. Published questions and answers are unchanged from the prior HF revision.

Full ID 74 retains its published community_27 mapping: dependency inspection found the required brazilianstates files there, but not in the historical community_1 candidate. Its reference program was also executed against the retained community and reproduced the expected answer.

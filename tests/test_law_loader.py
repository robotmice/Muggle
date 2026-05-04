import unittest
import tempfile
from unittest.mock import MagicMock, patch
from muggle.infra.loaders.law_loader import LawLoader, ARTICLE_PATTERN
from muggle.infra.registry.vector import VectorStoreManager


class TestLawLoaderParsing(unittest.TestCase):
    """Test chapter-article parsing logic without hitting Milvus."""

    SAMPLE = """\
# Test Law

---

## 目录

- 第一章
- 第二章

---

## 第一章 总则

**第一条** 这是第一条的内容。

**第二条** 这是第二条的内容，可能会有比较长的文本。

## 第二章 基本养老保险

**第十条** 职工应当参加基本养老保险。

*来源：测试来源*
"""

    def setUp(self):
        self.vs = MagicMock(spec=VectorStoreManager)
        self.vs.embed_text.return_value = [0.1] * 1024

    def test_article_pattern_matches_chinese_numerals(self):
        cases = [
            ("**第一条**", "第一条"),
            ("**第十条**", "第十条"),
            ("**第二十三条**", "第二十三条"),
            ("**第一百条**", "第一百条"),
        ]
        for text, expected in cases:
            match = ARTICLE_PATTERN.search(text)
            self.assertIsNotNone(match, f"No match for {text}")
            self.assertEqual(match.group(1), expected)

    def test_skips_toc_chapter(self):
        loader = LawLoader(self.vs, lang_tag="zh-CN")
        loader.segment_splitter.split_text = MagicMock(return_value=[])

        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", encoding="utf-8", delete=False) as f:
            f.write(self.SAMPLE)
            temp_path = f.name

        try:
            loader.load_from_file(temp_path)
        finally:
            import os
            os.unlink(temp_path)

        self.vs.upsert.assert_called_once()
        records = self.vs.upsert.call_args[0][0]

        headers = [r["header"] for r in records]
        self.assertIn("第一章 总则 — 第一条", headers)
        self.assertIn("第一章 总则 — 第二条", headers)
        self.assertIn("第二章 基本养老保险 — 第十条", headers)

        # Verify chapter-prefixed format
        for h in headers:
            self.assertIn(" — ", h, f"Header '{h}' missing chapter prefix separator")

        # TOC should not produce records
        for r in records:
            self.assertNotIn("目录", r["header"])

        for r in records:
            self.assertEqual(r["lang_tag"], "zh-CN")
            self.assertEqual(len(r["header_vector"]), 1024)
            self.assertEqual(len(r["content_vector"]), 1024)

    def test_lang_tag_default(self):
        loader = LawLoader(self.vs)
        self.assertEqual(loader.lang_tag, "zh-CN")

    def test_rejects_unsupported_lang(self):
        with self.assertRaises(ValueError):
            LawLoader(self.vs, lang_tag="fr-FR")

    def test_idempotent_ids(self):
        loader = LawLoader(self.vs)
        id1 = loader._generate_id("test text")
        id2 = loader._generate_id("test text")
        self.assertEqual(id1, id2)
        # Same text should not match different text
        id3 = loader._generate_id("different text")
        self.assertNotEqual(id1, id3)


if __name__ == '__main__':
    unittest.main()

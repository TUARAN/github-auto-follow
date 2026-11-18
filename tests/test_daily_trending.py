#!/usr/bin/env python3
"""每日热门清单的本地冒烟测试：解析、合并、落盘、后端读取。不访问 Star / Follow API。"""
from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "backend"))

import daily_trending  # noqa: E402
import trending as trending_store  # noqa: E402

FIXTURE = ROOT / "tests" / "fixtures" / "trending_sample.html"


class ParseTrendingHtmlTests(unittest.TestCase):
    def setUp(self):
        self.html = FIXTURE.read_text(encoding="utf-8")

    def test_parses_core_fields_and_ignores_star_login_link(self):
        repos = daily_trending.parse_trending_html(self.html, "GitHub 今日趋势")
        self.assertEqual(len(repos), 2)
        first = repos[0]
        self.assertEqual(first["full_name"], "octo-org/hello-world")
        self.assertEqual(first["description"], "A demo repository used in tests.")
        self.assertEqual(first["language"], "Python")
        self.assertEqual(first["stars"], 12345)
        self.assertEqual(first["url"], "https://github.com/octo-org/hello-world")
        self.assertIn("当天新增 791 star", first["reason"])
        self.assertTrue(all("/login" not in r["url"] for r in repos))

    def test_unescapes_description_and_weekly_reason(self):
        repos = daily_trending.parse_trending_html(self.html, "GitHub 本周趋势")
        second = repos[1]
        self.assertEqual(second["full_name"], "example-user/weekly-tool")
        self.assertEqual(second["description"], "Another demo with an ampersand & angle <tag>.")
        self.assertEqual(second["language"], "")
        self.assertEqual(second["stars"], 1024)
        self.assertIn("本周新增 2048 star", second["reason"])


class MergeAndLimitTests(unittest.TestCase):
    def test_merge_deduplicates_and_respects_limit(self):
        a = [{"full_name": "a/one", "stars": 1}, {"full_name": "a/two", "stars": 2}]
        b = [{"full_name": "a/two", "stars": 9}, {"full_name": "b/three", "stars": 3}]
        merged = daily_trending.merge_repos((a, b), limit=2)
        self.assertEqual([r["full_name"] for r in merged], ["a/one", "a/two"])

    def test_clamp_limit(self):
        self.assertEqual(daily_trending.clamp_limit(1), 20)
        self.assertEqual(daily_trending.clamp_limit(30), 30)
        self.assertEqual(daily_trending.clamp_limit(99), 50)


class PersistenceAndApiReadTests(unittest.TestCase):
    def setUp(self):
        self.tmpdir = Path(tempfile.mkdtemp(prefix="trending-test-"))
        self.addCleanup(shutil.rmtree, self.tmpdir, True)

    def test_write_prune_and_backend_loader(self):
        items = [
            {
                "full_name": "octo-org/hello-world",
                "description": "demo",
                "language": "Python",
                "stars": 12,
                "url": "https://github.com/octo-org/hello-world",
                "reason": "GitHub 今日趋势",
            }
        ]
        daily_trending.write_digest(self.tmpdir, "2026-11-17", items, ["test"])
        daily_trending.write_digest(self.tmpdir, "2026-11-01", items, ["test"])
        kept = daily_trending.prune_old_digests(self.tmpdir, "2026-11-17", retention_days=7)
        daily_trending.write_index(self.tmpdir, kept)

        self.assertTrue((self.tmpdir / "2026-11-17.json").is_file())
        self.assertFalse((self.tmpdir / "2026-11-01.json").exists())
        index = json.loads((self.tmpdir / "index.json").read_text(encoding="utf-8"))
        self.assertEqual(index["latest"], "2026-11-17")
        self.assertEqual(index["dates"], ["2026-11-17"])

        original_dir = trending_store.DEFAULT_DATA_DIR
        trending_store.DEFAULT_DATA_DIR = self.tmpdir
        self.addCleanup(setattr, trending_store, "DEFAULT_DATA_DIR", original_dir)
        # Disable remote fallback in this test
        self.addCleanup(lambda: None)
        import os
        old = os.environ.get("TRENDING_FALLBACK_URL")
        os.environ["TRENDING_FALLBACK_URL"] = ""
        os.environ["TRENDING_DATA_DIR"] = str(self.tmpdir)
        self.addCleanup(lambda: os.environ.pop("TRENDING_DATA_DIR", None))
        if old is None:
            self.addCleanup(lambda: os.environ.pop("TRENDING_FALLBACK_URL", None))
        else:
            self.addCleanup(lambda: os.environ.__setitem__("TRENDING_FALLBACK_URL", old))

        digest = trending_store.load_digest()
        self.assertEqual(digest["date"], "2026-11-17")
        self.assertEqual(digest["count"], 1)
        self.assertEqual(digest["items"][0]["full_name"], "octo-org/hello-world")
        self.assertEqual(trending_store.load_index()["dates"], ["2026-11-17"])
        self.assertIsNone(trending_store.load_digest("2020-01-01"))


class SafetyTests(unittest.TestCase):
    def test_new_feature_source_has_no_star_or_follow_writes(self):
        files = [
            ROOT / "scripts" / "daily_trending.py",
            ROOT / "backend" / "trending.py",
        ]
        call_patterns = (
            r"""['"]https?://api\.github\.com/user/starred""",
            r"""[fFrR]?['"].*/user/starred""",
            r"""['"]https?://api\.github\.com/user/following""",
            r"""[fFrR]?['"].*/user/following/""",
        )
        for path in files:
            source = path.read_text(encoding="utf-8")
            for pattern in call_patterns:
                self.assertIsNone(
                    __import__("re").search(pattern, source),
                    f"{path} should not call {pattern}",
                )
            self.assertNotIn("requests.put", source)
            self.assertNotIn("requests.delete", source)
            self.assertNotIn("session.put", source)
            self.assertNotIn("session.delete", source)


class TranslationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_cache_key_is_stable_and_distinct(self):
        key_a = daily_trending.translation_cache_key("a/one", "Same text.")
        key_a2 = daily_trending.translation_cache_key("a/one", "Same text.")
        key_b = daily_trending.translation_cache_key("a/two", "Same text.")
        key_c = daily_trending.translation_cache_key("a/one", "Different text.")
        self.assertEqual(key_a, key_a2)
        self.assertNotEqual(key_a, key_b)
        self.assertNotEqual(key_a, key_c)

    def test_cache_roundtrip_and_prune(self):
        daily_trending.save_translation_cache(self.tmp, {"k1": {"zh": "示例", "at": "2020-01-01T00:00:00+00:00"}})
        loaded = daily_trending.load_translation_cache(self.tmp)
        self.assertEqual(loaded["k1"]["zh"], "示例")
        pruned = daily_trending.prune_translation_cache(loaded)
        self.assertEqual(pruned, {})

    def test_translate_skips_without_valid_key(self):
        items = [{"full_name": "a/one", "description": "A demo repository.", "description_zh": ""}]
        result = daily_trending.translate_descriptions(items, self.tmp, None)
        self.assertEqual(result[0]["description_zh"], "")
        result = daily_trending.translate_descriptions(items, self.tmp, "sk-你的密钥")
        self.assertEqual(result[0]["description_zh"], "")

    def test_write_digest_includes_description_zh(self):
        items = [{
            "full_name": "a/one",
            "description": "A demo repository.",
            "description_zh": "一个演示仓库。",
            "language": "Python",
            "stars": 1,
            "url": "https://github.com/a/one",
            "reason": "GitHub 今日趋势",
        }]
        path = daily_trending.write_digest(self.tmp, "2026-11-18", items, ["test"])
        payload = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(payload["items"][0]["description_zh"], "一个演示仓库。")


if __name__ == "__main__":
    unittest.main()

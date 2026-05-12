"""parse_body() unit tests"""
import pytest
from parser.content import parse_body


class TestParseBody:
    """Test body text parsing"""

    def test_complete_body(self):
        """Full output: title/intro/body/closing/tags"""
        content = """标题：Test Title
开头：This is the intro text.
正文：
Section One
Content for section one
Section Two
Content for section two
结尾：Follow me for more
标签：#AI #Tech #Test"""
        result = parse_body(content)
        assert result["title"] == "Test Title"
        assert result["intro"] == "This is the intro text."
        assert len(result["sections"]) == 2
        assert result["sections"][0]["title"] == "Section One"
        assert result["closing"] == "Follow me for more"
        assert "#AI" in result["tags"]

    def test_missing_tags(self):
        """Missing tags field"""
        content = """标题：Test Title
开头：Test intro
正文：
Section Title
Section Content
结尾：Test ending"""
        result = parse_body(content)
        assert result["title"] == "Test Title"
        assert result["tags"] == []

    def test_empty_input(self):
        """Empty input"""
        result = parse_body("")
        assert result["title"] == ""
        assert result["sections"] == []

    def test_none_input(self):
        """None input"""
        result = parse_body(None)
        assert result["title"] == ""
        assert result["sections"] == []

    def test_only_title_and_intro(self):
        """Only title and intro"""
        content = """标题：Title Only
开头：Intro Only"""
        result = parse_body(content)
        assert result["title"] == "Title Only"
        assert result["intro"] == "Intro Only"
        assert result["sections"] == []

    def test_markdown_headers_in_body(self):
        """Markdown headers (### xxx) in body"""
        content = """标题：Test
开头：Test intro
正文：
### Block One Title
Block one content here
### Block Two Title
Block two content here
结尾：End
标签：#tag"""
        result = parse_body(content)
        assert len(result["sections"]) == 2
        assert result["sections"][0]["title"] == "Block One Title"
        assert result["sections"][1]["title"] == "Block Two Title"

    def test_short_phrase_as_section_title(self):
        """Short phrase (<=15 chars, no punctuation) recognized as section title"""
        content = """标题：Test
开头：Test intro
正文：
Feature A
This is feature A content
Feature B
This is feature B content
结尾：End
标签：#tag"""
        result = parse_body(content)
        assert len(result["sections"]) == 2
        assert result["sections"][0]["title"] == "Feature A"
        assert "feature A content" in result["sections"][0]["content"]

    def test_long_phrase_as_content_not_title(self):
        """Lines over 15 chars should be content, not title"""
        content = """标题：Test
开头：Test intro
正文：
Short Title
This is a very long line that exceeds fifteen characters and should be treated as content
结尾：End
标签：#tag"""
        result = parse_body(content)
        # With a short title preceding, the long line becomes content
        assert len(result["sections"]) == 1
        assert "exceeds fifteen characters" in result["sections"][0]["content"]
import unittest
from unittest.mock import patch

import agents


SOURCE_TEXT = "Original source text"
SOURCE_ID = "page-1-text-1"


def sample_document():

    return {
        "metadata": {},
        "pages": [{
            "page_number": 1,
            "blocks": [{
                "type": "text",
                "bbox": [0, 0, 1, 1],
                "text": SOURCE_TEXT
            }]
        }]
    }


def valid_response(block_id=SOURCE_ID, block_type="paragraph", level=None):

    block = {
        "id": block_id,
        "type": block_type
    }

    if level is not None:
        block["level"] = level

    return {"blocks": [block]}


class ClassificationTests(unittest.TestCase):

    def test_valid_json(self):

        with patch.object(
            agents,
            "ask_ollama",
            return_value='{"blocks": [{"id": "page-1-text-1", "type": "paragraph"}]}'
        ):
            html = agents.format_article(sample_document())

        self.assertIn(SOURCE_TEXT, html)
        self.assertIn("<p>", html)

    def test_json_surrounded_by_fences(self):

        response = "```json\n" + str(valid_response()).replace("'", '"') + "\n```"

        with patch.object(agents, "ask_ollama", return_value=response):
            html = agents.format_article(sample_document())

        self.assertIn(SOURCE_TEXT, html)

    def test_malformed_json_then_valid_json_retries_once(self):

        responses = ["{malformed", '{"blocks": [{"id": "page-1-text-1", "type": "heading", "level": 1}]}']

        with patch.object(agents, "ask_ollama", side_effect=responses) as ask:
            html = agents.format_article(sample_document())

        self.assertEqual(ask.call_count, 2)
        self.assertIn("<h1>", html)

    def test_malformed_json_on_both_attempts(self):

        with patch.object(
            agents,
            "ask_ollama",
            side_effect=["{malformed", "still malformed"]
        ):
            with self.assertRaisesRegex(ValueError, "after one retry"):
                agents.format_article(sample_document())

    def test_missing_blocks_array(self):

        with patch.object(agents, "ask_ollama", return_value="{}"):
            with self.assertRaisesRegex(ValueError, "blocks array"):
                agents.format_article(sample_document())

    def test_unknown_block_id(self):

        response = valid_response(block_id="unknown")

        with patch.object(agents, "ask_ollama", return_value=str(response).replace("'", '"')):
            with self.assertRaisesRegex(ValueError, "unknown block ID"):
                agents.format_article(sample_document())

    def test_invalid_classification_type(self):

        response = valid_response(block_type="not-a-type")

        with patch.object(agents, "ask_ollama", return_value=str(response).replace("'", '"')):
            with self.assertRaisesRegex(ValueError, "invalid classification type"):
                agents.format_article(sample_document())

    def test_invalid_heading_level(self):

        response = valid_response(block_type="heading", level=4)

        with patch.object(agents, "ask_ollama", return_value=str(response).replace("'", '"')):
            with self.assertRaisesRegex(ValueError, "invalid heading level"):
                agents.format_article(sample_document())


if __name__ == "__main__":
    unittest.main()
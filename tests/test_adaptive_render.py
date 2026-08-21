import unittest

from shooter import render_adaptive_html


class RenderAdaptiveHtmlTests(unittest.TestCase):
    def test_injects_canvas_override_before_closing_head(self):
        source = "<html><head><title>Card</title></HEAD><body>Hi</body></html>"

        result = render_adaptive_html(source, 1920, 1080)

        self.assertIn("width: 1920px !important", result)
        self.assertIn("height: 1080px !important", result)
        self.assertLess(result.index("cardshot-adaptive-canvas"), result.index("</HEAD>"))
        self.assertEqual(source, "<html><head><title>Card</title></HEAD><body>Hi</body></html>")

    def test_injects_escaped_base_href(self):
        result = render_adaptive_html(
            "<html><head></head><body></body></html>",
            1080,
            1440,
            'file:///tmp/a&b"/',
        )

        self.assertIn('<base href="file:///tmp/a&amp;b&quot;/">', result)

    def test_prepends_override_when_head_is_missing(self):
        result = render_adaptive_html("<body>Hi</body>", 1080, 1080)

        self.assertTrue(result.startswith("<style id=\"cardshot-adaptive-canvas\">"))

    def test_rejects_non_positive_dimensions(self):
        for width, height in ((0, 100), (100, 0), (-1, 100), (100, -1)):
            with self.subTest(width=width, height=height):
                with self.assertRaises(ValueError):
                    render_adaptive_html("<html></html>", width, height)


if __name__ == "__main__":
    unittest.main()

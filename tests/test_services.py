import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError, URLError
from chatia import services as s


class ServicesTest(unittest.TestCase):
    @patch("chatia.services.request.urlopen")
    def test_draft_payload_and_extraction(self, opened):
        opened.return_value.__enter__.return_value = io.BytesIO(json.dumps({
            "output": [{"type": "reasoning"}, {"type": "message", "content": [
                {"type": "output_text", "text": "Hola"}, {"type": "output_text", "text": "Gracias"}]}]}).encode())
        self.assertEqual(s.draft("Consulta", "test-token", "test-model"), "Hola\nGracias")
        req = opened.call_args.args[0]
        self.assertEqual(req.full_url, "https://api.openai.com/v1/responses")
        self.assertEqual(json.loads(req.data)["input"], "Consulta")
        self.assertEqual(req.headers["Authorization"], "Bearer test-token")

    @patch("chatia.services.post_json", return_value={"messages": [{"id": "wamid.test"}]})
    def test_send_one_explicit_request(self, post):
        self.assertEqual(s.send_whatsapp("Hola", "+12345678901", "test", "123", "v23.0"), "wamid.test")
        post.assert_called_once()
        url, token, payload = post.call_args.args
        self.assertEqual(url, "https://graph.facebook.com/v23.0/123/messages")
        self.assertEqual(payload["to"], "12345678901")
        self.assertEqual(payload["text"], {"preview_url": False, "body": "Hola"})

    @patch("chatia.services.post_json")
    def test_invalid_send_never_calls_network(self, post):
        for recipient, phone, version, text in [
            ("+12 345", "123", "v23.0", "Hola"),
            ("12345678901", "../x", "v23.0", "Hola"),
            ("12345678901", "123", "https://evil", "Hola"),
            ("12345678901", "123", "v23.0", " "),
            ("12345678901", "123", "v23.0", "a" * 4097)]:
            with self.subTest(recipient=recipient, text_length=len(text)):
                with self.assertRaises(s.ServiceError):
                    s.send_whatsapp(text, recipient, "test", phone, version)
        post.assert_not_called()

    @patch("chatia.services.request.urlopen")
    def test_http_error_redacted_and_no_retry(self, opened):
        opened.side_effect = HTTPError("https://example.invalid", 401, "test-secret", {}, io.BytesIO(b"test-secret"))
        with self.assertRaises(s.ServiceError) as raised:
            s.post_json("https://example.invalid", "test-secret", {})
        self.assertNotIn("test-secret", str(raised.exception))
        self.assertIn("401", str(raised.exception))
        opened.assert_called_once()

    @patch("chatia.services.request.urlopen", side_effect=URLError("test-secret"))
    def test_timeout_uncertainty_no_retry(self, opened):
        with self.assertRaises(s.ServiceError) as raised:
            s.post_json("https://example.invalid", "test", {})
        self.assertIn("verificá", str(raised.exception))
        self.assertNotIn("test-secret", str(raised.exception))
        opened.assert_called_once()

    @patch("chatia.services.request.urlopen")
    def test_missing_key_no_network(self, opened):
        with self.assertRaises(s.ServiceError):
            s.post_json("https://example.invalid", "", {})
        opened.assert_not_called()

    @patch("chatia.services.post", return_value={"text": "Transcripción"})
    def test_audio_multipart_does_not_include_local_path(self, post):
        with tempfile.TemporaryDirectory() as folder:
            audio = Path(folder) / "private-name.wav"
            audio.write_bytes(b"fake-audio")
            self.assertEqual(s.transcribe_cloud(str(audio), "test", "test-model"), "Transcripción")
            url, token, body, content_type = post.call_args.args
            self.assertIn(b"fake-audio", body)
            self.assertIn(b'filename="audio.wav"', body)
            self.assertNotIn(b"private-name", body)
            self.assertIn("boundary=", content_type)
            self.assertTrue(body.endswith(b"--\r\n"))

    @patch("chatia.services.post")
    def test_invalid_audio_no_network(self, post):
        with tempfile.TemporaryDirectory() as folder:
            audio = Path(folder) / "empty.wav"
            audio.touch()
            with self.assertRaises(s.ServiceError):
                s.transcribe_cloud(str(audio), "test", "model")
            audio = Path(folder) / "input.ogg"
            audio.write_bytes(b"test")
            with self.assertRaises(s.ServiceError):
                s.transcribe_cloud(str(audio), "test", "model")
        post.assert_not_called()

    @patch("chatia.services.post_json", return_value={})
    def test_ambiguous_send_not_reported_as_success(self, post):
        with self.assertRaises(s.ServiceError):
            s.send_whatsapp("Hola", "12345678901", "test", "123", "v23.0")
        post.assert_called_once()

    @patch("chatia.services.post_json", return_value={"output": []})
    def test_empty_model_response(self, post):
        with self.assertRaises(s.ServiceError):
            s.draft("Hola", "test", "model")


if __name__ == "__main__":
    unittest.main()

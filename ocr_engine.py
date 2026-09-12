import os

# Disable oneDNN / MKL-DNN before importing Paddle/PaddleOCR.
os.environ["FLAGS_use_mkldnn"] = "0"
os.environ["FLAGS_use_onednn"] = "0"

from pathlib import Path
from typing import Any

from config import OCR_MIN_CONFIDENCE


class OCRFailure(RuntimeError):
    """Raised when OCR cannot be initialized or executed."""
    pass


class PaddleOCREngine:
    """
    PaddleOCR wrapper for the SIH26034 compliance pipeline.

    Compatible with PaddleOCR 3.x and provides a fallback
    for older PaddleOCR versions.
    """

    def __init__(self, lang: str = "en"):
        try:
            from paddleocr import PaddleOCR
        except ImportError as exc:
            raise OCRFailure(
                "PaddleOCR is not installed."
            ) from exc

        try:
            # PaddleOCR 3.x
            self.engine = PaddleOCR(
                lang=lang,
                device="cpu",
                use_doc_orientation_classify=True,
                use_doc_unwarping=True,
                use_textline_orientation=True,
            )

        except TypeError:
            # Compatibility fallback for older versions
            self.engine = PaddleOCR(
                lang=lang
            )

    @staticmethod
    def _to_python(value: Any):
        """Convert NumPy/Paddle objects to normal Python objects."""

        if hasattr(value, "tolist"):
            try:
                return value.tolist()
            except Exception:
                pass

        return value

    def _parse_new_result(self, item):
        """
        Parse PaddleOCR 3.x OCRResult objects.

        Expected fields:
            rec_texts
            rec_scores
            rec_boxes
        """

        # Try to convert OCRResult to dictionary
        if hasattr(item, "json"):
            try:
                payload = item.json

                if callable(payload):
                    payload = payload()

                if isinstance(payload, str):
                    import json
                    payload = json.loads(payload)

                if isinstance(payload, dict):
                    item = payload

            except Exception:
                pass

        # Get result dictionary
        if isinstance(item, dict):
            data = item.get("res", item)
        else:
            data = getattr(item, "res", item)

        if not isinstance(data, dict):
            return []

        # Text
        texts = data.get("rec_texts")

        if texts is None:
            texts = data.get("texts", [])

        # Confidence
        scores = data.get("rec_scores")

        if scores is None:
            scores = data.get("scores", [])

        # Bounding boxes
        boxes = data.get("rec_boxes")

        if boxes is None:
            boxes = data.get("boxes")

        if boxes is None:
            boxes = data.get("rec_polys")

        if boxes is None:
            boxes = []

        # Convert to Python
        texts = self._to_python(texts)
        scores = self._to_python(scores)
        boxes = self._to_python(boxes)

        if texts is None:
            texts = []

        if scores is None:
            scores = []

        if boxes is None:
            boxes = []

        if not isinstance(texts, (list, tuple)):
            texts = [texts]

        if not isinstance(scores, (list, tuple)):
            scores = [scores]

        if not isinstance(boxes, (list, tuple)):
            boxes = [boxes]

        records = []

        for i, text in enumerate(texts):

            text = str(text).strip()

            if not text:
                continue

            # Confidence
            score = None

            if i < len(scores):
                try:
                    score = float(scores[i])
                except (TypeError, ValueError):
                    score = None

            # Confidence filtering
            if (
                score is not None
                and score < OCR_MIN_CONFIDENCE
            ):
                continue

            # Bounding box
            box = None

            if i < len(boxes):
                box = self._to_python(boxes[i])

            records.append(
                {
                    "text": text,
                    "confidence": score,
                    "box": box,
                }
            )

        return records

    def _parse_old_result(self, result):
        """
        Parse older PaddleOCR .ocr() output.

        Typical format:

        [
            [
                [
                    [[x1,y1],[x2,y2],...],
                    ["text", confidence]
                ]
            ]
        ]
        """

        records = []

        if not result:
            return records

        try:
            pages = result if isinstance(result, list) else [result]

            for page in pages:

                if not page:
                    continue

                for line in page:

                    if not line or len(line) < 2:
                        continue

                    box = line[0]
                    payload = line[1]

                    if isinstance(payload, (list, tuple)):

                        if len(payload) == 0:
                            continue

                        text = str(payload[0]).strip()

                        if len(payload) > 1:
                            try:
                                score = float(payload[1])
                            except (TypeError, ValueError):
                                score = None
                        else:
                            score = None

                    else:
                        text = str(payload).strip()
                        score = None

                    if not text:
                        continue

                    if (
                        score is not None
                        and score < OCR_MIN_CONFIDENCE
                    ):
                        continue

                    records.append(
                        {
                            "text": text,
                            "confidence": score,
                            "box": self._to_python(box),
                        }
                    )

        except Exception:
            return []

        return records

    def predict(self, image_path: str | Path):
        """
        Run OCR on the supplied image.

        PaddleOCR 3.x uses:
            predict()

        Older versions use:
            ocr()
        """

        image_path = str(image_path)

        # =========================================================
        # PaddleOCR 3.x
        # =========================================================

        if hasattr(self.engine, "predict"):

            try:
                result = self.engine.predict(image_path)

                all_records = []

                for item in result:
                    records = self._parse_new_result(item)
                    all_records.extend(records)

                return all_records

            except Exception as exc:
                raise OCRFailure(
                    f"PaddleOCR prediction failed for "
                    f"'{image_path}': {exc}"
                ) from exc

        # =========================================================
        # Older PaddleOCR
        # =========================================================

        if hasattr(self.engine, "ocr"):

            try:
                result = self.engine.ocr(image_path)

                return self._parse_old_result(result)

            except Exception as exc:
                raise OCRFailure(
                    f"Legacy PaddleOCR execution failed for "
                    f"'{image_path}': {exc}"
                ) from exc

        raise OCRFailure(
            "Installed PaddleOCR exposes neither "
            "predict() nor ocr()."
        )


# =============================================================
# PUBLIC FUNCTION USED BY pipeline.py
# =============================================================

def run_ocr(image_path: str | Path):
    """
    Run OCR and return standardized OCR records.
    """

    engine = PaddleOCREngine()

    return engine.predict(image_path)
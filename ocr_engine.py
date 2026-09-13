import os
from pathlib import Path
from typing import Any

os.environ["FLAGS_use_mkldnn"] = "0"
os.environ["FLAGS_use_onednn"] = "0"

from config import OCR_MIN_CONFIDENCE, OCR_KEEP_CONFIDENCE

class OCRFailure(RuntimeError):
    """Raised when OCR cannot be initialized or executed."""
    pass


class PaddleOCREngine:
    """
    Robust PaddleOCR wrapper for SIH26034.

    Improvements:
    - Does not discard weak OCR boxes.
    - Runs OCR on original + enhanced image variants when OpenCV is available.
    - Fuses duplicate boxes from multiple passes.
    - Preserves bounding boxes so downstream field association can use layout.
    """

    def __init__(self, lang: str = "en", multi_pass: bool = True):
        try:
            from paddleocr import PaddleOCR
        except ImportError as exc:
            raise OCRFailure("PaddleOCR is not installed.") from exc

        self.multi_pass = multi_pass
        self._temp_files = []

        try:
            self.engine = PaddleOCR(
                lang=lang,
                device="cpu",
                use_doc_orientation_classify=True,
                use_doc_unwarping=True,
                use_textline_orientation=True,
            )
        except TypeError:
            self.engine = PaddleOCR(lang=lang)

    @staticmethod
    def _to_python(value: Any):
        if hasattr(value, "tolist"):
            try:
                return value.tolist()
            except Exception:
                pass
        return value

    @staticmethod
    def _box_rect(box):
        if not box:
            return None
        try:
            if len(box) == 4 and all(isinstance(v, (int, float)) for v in box):
                return tuple(float(v) for v in box)
            xs = [float(p[0]) for p in box]
            ys = [float(p[1]) for p in box]
            return min(xs), min(ys), max(xs), max(ys)
        except Exception:
            return None

    @staticmethod
    def _iou(a, b):
        ra, rb = PaddleOCREngine._box_rect(a), PaddleOCREngine._box_rect(b)
        if not ra or not rb:
            return 0.0
        ax1, ay1, ax2, ay2 = ra
        bx1, by1, bx2, by2 = rb
        ix1, iy1 = max(ax1, bx1), max(ay1, by1)
        ix2, iy2 = min(ax2, bx2), min(ay2, by2)
        iw, ih = max(0, ix2-ix1), max(0, iy2-iy1)
        inter = iw * ih
        if inter <= 0:
            return 0.0
        aa = max(0, ax2-ax1) * max(0, ay2-ay1)
        ab = max(0, bx2-bx1) * max(0, by2-by1)
        union = aa + ab - inter
        return inter / union if union else 0.0

    @staticmethod
    def _norm_text(text):
        return " ".join(str(text).lower().split())

    def _parse_new_result(self, item):
        if hasattr(item, "json"):
            try:
                payload = item.json
                payload = payload() if callable(payload) else payload
                if isinstance(payload, str):
                    import json
                    payload = json.loads(payload)
                if isinstance(payload, dict):
                    item = payload
            except Exception:
                pass

        data = item.get("res", item) if isinstance(item, dict) else getattr(item, "res", item)
        if not isinstance(data, dict):
            return []

        texts = self._to_python(data.get("rec_texts", data.get("texts", []))) or []
        scores = self._to_python(data.get("rec_scores", data.get("scores", []))) or []
        boxes = self._to_python(data.get("rec_boxes", data.get("boxes", data.get("rec_polys", [])))) or []

        if not isinstance(texts, (list, tuple)): texts = [texts]
        if not isinstance(scores, (list, tuple)): scores = [scores]
        if not isinstance(boxes, (list, tuple)): boxes = [boxes]

        records = []
        for i, text in enumerate(texts):
            text = str(text).strip()
            if not text:
                continue
            score = None
            if i < len(scores):
                try: score = float(scores[i])
                except (TypeError, ValueError): pass
            box = self._to_python(boxes[i]) if i < len(boxes) else None
            records.append({
                "text": text,
                "confidence": score,
                "box": box,
                "low_confidence": score is not None and score < OCR_KEEP_CONFIDENCE,
                "ocr_pass": "paddle",
            })
        return records

    def _parse_old_result(self, result):
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
                    box, payload = line[0], line[1]
                    if isinstance(payload, (list, tuple)):
                        if not payload:
                            continue
                        text = str(payload[0]).strip()
                        try: score = float(payload[1]) if len(payload) > 1 else None
                        except (TypeError, ValueError): score = None
                    else:
                        text, score = str(payload).strip(), None
                    if not text:
                        continue
                    records.append({
                        "text": text,
                        "confidence": score,
                        "box": self._to_python(box),
                        "low_confidence": score is not None and score < OCR_KEEP_CONFIDENCE,
                        "ocr_pass": "paddle",
                    })
        except Exception:
            return []
        return records

    def _predict_one(self, image_path):
        if hasattr(self.engine, "predict"):
            try:
                result = self.engine.predict(str(image_path))
                records = []
                for item in result:
                    records.extend(self._parse_new_result(item))
                return records
            except Exception as exc:
                raise OCRFailure(f"PaddleOCR prediction failed for '{image_path}': {exc}") from exc

        if hasattr(self.engine, "ocr"):
            try:
                return self._parse_old_result(self.engine.ocr(str(image_path)))
            except Exception as exc:
                raise OCRFailure(f"Legacy PaddleOCR execution failed for '{image_path}': {exc}") from exc

        raise OCRFailure("Installed PaddleOCR exposes neither predict() nor ocr().")

    def _make_variants(self, image_path):
        """Create same-size enhanced variants; coordinates stay aligned to original."""
        variants = [str(image_path)]
        if not self.multi_pass:
            return variants

        try:
            import cv2
            import numpy as np

            img = cv2.imread(str(image_path))
            if img is None:
                return variants

            # Keep exact dimensions so OCR boxes remain compatible.
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(gray)
            enhanced = cv2.GaussianBlur(enhanced, (0, 0), 1.0)
            enhanced = cv2.addWeighted(gray, 1.6, enhanced, -0.6, 0)
            sharpened = cv2.addWeighted(gray, 1.8, cv2.GaussianBlur(gray, (0,0), 2.0), -0.8, 0)

            stem = str(Path(image_path).with_suffix(""))
            for suffix, arr in [("_enhanced", enhanced), ("_sharp", sharpened)]:
                out = f"{stem}{suffix}.ocr_tmp.png"
                cv2.imwrite(out, arr)
                variants.append(out)
                self._temp_files.append(out)
        except Exception:
            # OpenCV is an optimization, not a hard dependency.
            pass
        return variants

    def _fuse(self, passes):
        fused = []
        for records in passes:
            for rec in records:
                text = self._norm_text(rec.get("text", ""))
                box = rec.get("box")
                duplicate = None
                for old in fused:
                    same_text = text and text == self._norm_text(old.get("text", ""))
                    overlap = self._iou(box, old.get("box"))
                    if same_text and overlap >= 0.35:
                        duplicate = old
                        break
                if duplicate is None:
                    fused.append(dict(rec))
                else:
                    old_score = duplicate.get("confidence")
                    new_score = rec.get("confidence")
                    if (new_score or 0) > (old_score or 0):
                        duplicate.update(rec)
                    duplicate["ocr_pass"] = "multi_pass_fused"
                    duplicate["low_confidence"] = (duplicate.get("confidence") or 1) < OCR_KEEP_CONFIDENCE

        # Stable visual order: top-to-bottom, then left-to-right.
        def key(r):
            rect = self._box_rect(r.get("box"))
            return (rect[1] if rect else 10**9, rect[0] if rect else 10**9)
        fused.sort(key=key)
        for i, rec in enumerate(fused):
            rec["ocr_index"] = i
        return fused

    def predict(self, image_path: str | Path):
        variants = self._make_variants(image_path)
        try:
            passes = [self._predict_one(p) for p in variants]
            return self._fuse(passes)
        finally:
            for p in self._temp_files:
                try: Path(p).unlink(missing_ok=True)
                except Exception: pass
            self._temp_files.clear()


def run_ocr(image_path: str | Path):
    return PaddleOCREngine().predict(image_path)

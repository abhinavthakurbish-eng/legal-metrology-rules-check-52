"""
reports/annotate.py
-------------------
Visual Evidence Annotation Engine for Packaging Compliance Inspection.
Draws color-coded bounding boxes and statutory tags using OpenCV or PIL.
"""

import os

try:
    import cv2
    import numpy as np
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


def create_annotated_image(image_path, compliance_results, output_path, image_index=0):
    """
    Draw color-coded bounding boxes on the package image for detected declarations:
    - Green for Compliant
    - Amber/Orange for Partial
    - Red for Non-Compliant/Missing
    """
    if not os.path.exists(image_path):
        return False

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Status color mapping
    colors_rgb = {
        "COMPLIANT": (16, 185, 129),       # Green
        "PARTIAL_COMPLIANCE": (245, 158, 11), # Orange
        "NON_COMPLIANT": (239, 68, 68)     # Red
    }

    # If OpenCV is available, use fast OpenCV drawing
    if CV2_AVAILABLE:
        try:
            img = cv2.imread(image_path)
            if img is not None:
                overlay = img.copy()
                h_img, w_img = img.shape[:2]

                colors_bgr = {
                    "COMPLIANT": (129, 185, 16),
                    "PARTIAL_COMPLIANCE": (11, 158, 245),
                    "NON_COMPLIANT": (68, 68, 239)
                }

                for item in compliance_results:
                    bbox_info = item.get("bounding_box")
                    if not bbox_info or bbox_info.get("image_index") != image_index:
                        continue

                    x, y, w, h = bbox_info["bbox"]
                    x = max(0, min(x, w_img - 10))
                    y = max(0, min(y, h_img - 10))
                    w = max(20, min(w, w_img - x))
                    h = max(15, min(h, h_img - y))

                    status = item.get("status", "NON_COMPLIANT")
                    color = colors_bgr.get(status, (68, 68, 239))
                    rule_name = item.get("rule_name", "Statutory Field")
                    status_label = "PASS" if status == "COMPLIANT" else ("WARN" if status == "PARTIAL_COMPLIANCE" else "FAIL")

                    cv2.rectangle(overlay, (x, y), (x + w, y + h), color, 3)

                    tag_text = f"[{status_label}] {rule_name[:20]}"
                    font = cv2.FONT_HERSHEY_SIMPLEX
                    (text_w, text_h), _ = cv2.getTextSize(tag_text, font, 0.5, 1)

                    tag_y1 = max(0, y - text_h - 8)
                    cv2.rectangle(img, (x, tag_y1), (x + text_w + 10, y), color, -1)
                    cv2.putText(img, tag_text, (x + 5, y - 4), font, 0.5, (255, 255, 255), 1, cv2.LINE_AA)

                cv2.addWeighted(overlay, 0.7, img, 0.3, 0, img)
                cv2.imwrite(output_path, img)
                return True
        except Exception:
            pass

    # PIL Fallback
    if PIL_AVAILABLE:
        try:
            with Image.open(image_path) as im:
                im = im.convert("RGB")
                draw = ImageDraw.Draw(im)
                w_img, h_img = im.size

                for item in compliance_results:
                    bbox_info = item.get("bounding_box")
                    if not bbox_info or bbox_info.get("image_index") != image_index:
                        continue

                    x, y, w, h = bbox_info["bbox"]
                    x1 = max(0, min(x, w_img - 10))
                    y1 = max(0, min(y, h_img - 10))
                    x2 = max(x1 + 20, min(x1 + w, w_img))
                    y2 = max(y1 + 15, min(y1 + h, h_img))

                    status = item.get("status", "NON_COMPLIANT")
                    color = colors_rgb.get(status, (239, 68, 68))
                    rule_name = item.get("rule_name", "Statutory Field")
                    status_label = "PASS" if status == "COMPLIANT" else ("WARN" if status == "PARTIAL_COMPLIANCE" else "FAIL")

                    # Draw rectangle
                    draw.rectangle([x1, y1, x2, y2], outline=color, width=3)
                    # Draw label banner
                    tag_text = f"[{status_label}] {rule_name[:20]}"
                    draw.rectangle([x1, max(0, y1 - 20), min(w_img, x1 + 160), y1], fill=color)
                    draw.text((x1 + 4, max(0, y1 - 16)), tag_text, fill=(255, 255, 255))

                im.save(output_path, "JPEG", quality=90)
                return True
        except Exception:
            pass

    return False

"""对单张图片做文字检测和识别。"""

import os
from io import BytesIO
from typing import List, Union

import numpy as np
from PIL import Image, UnidentifiedImageError

from .parse_types import OcrLine

ImageSource = Union[str, os.PathLike, bytes, bytearray, np.ndarray, Image.Image]

_engine = None


def ocr_image(image: ImageSource) -> List[OcrLine]:
    """识别图片中的文字。

    Args:
        image: 图片路径、二进制、PIL 图片，或 RGB numpy 数组。
            数组形状为 (H, W)、(H, W, 3) 或 (H, W, 4)。浮点数组取值在
            0–1 时按 0–255 缩放。带透明通道的图片会铺在白色背景上。

    Returns:
        按阅读顺序排列的文字行。没有检测到文字时返回空列表。
    """
    rgb = _to_rgb_array(image)
    raw = _get_engine()(rgb)
    return _lines_from_ocr_output(raw)


def _to_rgb_array(image: ImageSource) -> np.ndarray:
    """把支持的图片输入转成 uint8 RGB 数组，形状为 (H, W, 3)。"""
    if isinstance(image, (str, os.PathLike)):
        path = os.fspath(image)
        if not os.path.isfile(path):
            raise FileNotFoundError(f"图片文件不存在: {path}")
        try:
            with Image.open(path) as img:
                img.load()
                return _pil_to_rgb(img)
        except UnidentifiedImageError as exc:
            raise ValueError(f"无法识别的图片文件: {path}") from exc
    if isinstance(image, (bytes, bytearray)):
        if not image:
            raise ValueError("图片数据为空")
        try:
            with Image.open(BytesIO(image)) as img:
                img.load()
                return _pil_to_rgb(img)
        except UnidentifiedImageError as exc:
            raise ValueError("无法识别的图片数据") from exc
    if isinstance(image, Image.Image):
        return _pil_to_rgb(image)
    if isinstance(image, np.ndarray):
        return _array_to_rgb(image)
    raise TypeError(f"不支持的图片类型: {type(image).__name__}")


def _lines_from_ocr_output(raw) -> List[OcrLine]:
    """把视觉模块的 OCR 返回值转成 OcrLine。没有文字时返回空列表。"""
    if not raw or not isinstance(raw, list):
        return []
    lines = []
    for item in raw:
        box, recognition = item
        text, score = recognition
        if not text or len(box) != 4:
            continue
        points = tuple((float(point[0]), float(point[1])) for point in box)
        lines.append(OcrLine(text=text, score=float(score), box=points))
    return lines


def _get_engine():
    global _engine
    if _engine is None:
        from ragflow.deepdoc.vision import OCR

        _engine = OCR()
    return _engine


def _pil_to_rgb(img: Image.Image) -> np.ndarray:
    if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
        rgba = img.convert("RGBA")
        background = Image.new("RGB", rgba.size, (255, 255, 255))
        background.paste(rgba, mask=rgba.getchannel("A"))
        rgb = background
    else:
        rgb = img.convert("RGB")
    return np.ascontiguousarray(rgb, dtype=np.uint8)


def _array_to_rgb(arr: np.ndarray) -> np.ndarray:
    if arr.ndim == 2:
        image = Image.fromarray(_as_uint8(arr), mode="L")
    elif arr.ndim == 3 and arr.shape[2] in (3, 4):
        channels = arr.shape[2]
        mode = "RGB" if channels == 3 else "RGBA"
        image = Image.fromarray(_as_uint8(arr[..., :channels]), mode=mode)
    else:
        raise ValueError(
            f"图片数组形状应为 (H, W)、(H, W, 3) 或 (H, W, 4)，当前为 {arr.shape}"
        )
    return _pil_to_rgb(image)


def _as_uint8(arr: np.ndarray) -> np.ndarray:
    if np.issubdtype(arr.dtype, np.floating):
        values = arr.astype(np.float32)
        if values.size and float(np.nanmax(values)) <= 1.0:
            values = values * 255.0
        return np.ascontiguousarray(np.clip(values, 0, 255).astype(np.uint8))
    return np.ascontiguousarray(np.clip(arr, 0, 255).astype(np.uint8))

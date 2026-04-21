import numpy as np
from imwatermark import WatermarkDecoder, WatermarkEncoder
from PIL import Image

_WATERMARK_BITS = 64  # 8 bytes


def embed_watermark(image: Image.Image, asset_id: str) -> Image.Image:
    payload = asset_id.replace("-", "")[:8].encode("ascii").ljust(8, b"\x00")
    bgr = np.array(image.convert("RGB"))[:, :, ::-1].copy()
    encoder = WatermarkEncoder()
    encoder.set_watermark("bytes", payload)
    bgr_wm = encoder.encode(bgr, "dwtDctSvd")
    rgb = bgr_wm[:, :, ::-1]
    return Image.fromarray(rgb.astype(np.uint8))


def decode_watermark(image: Image.Image) -> bytes:
    bgr = np.array(image.convert("RGB"))[:, :, ::-1].copy()
    decoder = WatermarkDecoder("bytes", _WATERMARK_BITS)
    return decoder.decode(bgr, "dwtDctSvd")

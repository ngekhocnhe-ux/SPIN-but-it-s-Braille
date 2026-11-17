
import cv2
import numpy as np

from PIL import Image, ImageEnhance, ImageFilter, ImageOps


BITS = [
    (0, 0, 0x01),
    (0, 1, 0x02),
    (0, 2, 0x04),
    (1, 0, 0x08),
    (1, 1, 0x10),
    (1, 2, 0x20),
    (0, 3, 0x40),
    (1, 3, 0x80),
]


class BrailleConverter:
    def __init__(
        self,
        columns=120,
        contrast=2.0,
        sharpen=True,
        invert=False
    ):
        self.columns = columns
        self.contrast = contrast
        self.sharpen = sharpen
        self.invert = invert

    def convert(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(rgb)

        w, h = img.size

        new_h = max(
            4,
            int(h / w * self.columns * 2.8)
        )
        new_h = ((new_h + 3) // 4) * 4

        img = img.resize(
            (self.columns * 2, new_h),
            Image.Resampling.LANCZOS
        )

        # Giữ màu gốc
        color_array = np.asarray(img, dtype=np.uint8)

        # Xử lý ảnh xám để tạo hình Braille
        gray = ImageOps.autocontrast(img.convert("L"))
        gray = ImageEnhance.Contrast(gray).enhance(
            self.contrast
        )

        if self.sharpen:
            gray = gray.filter(ImageFilter.SHARPEN)

        if self.invert:
            gray = ImageOps.invert(gray)

        bw = gray.convert(
            "1",
            dither=Image.Dither.FLOYDSTEINBERG
        )

        pixels = np.asarray(bw, dtype=np.uint8)

        # Nền đen: chấm Braille biểu diễn vùng sáng
        bright = pixels != 0

        rows = new_h // 4

        cells = bright.reshape(
            rows, 4, self.columns, 2
        )

        color_cells = color_array.reshape(
            rows, 4, self.columns, 2, 3
        )

        # Tính mã Braille bằng NumPy
        mask = np.zeros(
            (rows, self.columns),
            dtype=np.uint8
        )

        for dx, dy, bit in BITS:
            mask |= cells[:, dy, :, dx].astype(
                np.uint8
            ) * bit

        # Màu trung bình của mỗi ô 2x4
        colors = color_cells.mean(
            axis=(1, 3)
        ).astype(np.uint8)

        # Trả về hai ma trận thay vì danh sách tuple
        return mask, colors

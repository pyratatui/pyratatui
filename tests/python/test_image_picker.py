"""tests for ImagePicker protocol constructors"""
import os, tempfile, struct, zlib, pytest
from pyratatui import ImagePicker, ImageState, ImageWidget

def _make_png(path, w=4, h=4):
    def chunk(n, d):
        c = n+d; return struct.pack(">I",len(d))+c+struct.pack(">I",zlib.crc32(c)&0xFFFFFFFF)
    png = (b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB",w,h,8,2,0,0,0))
        + chunk(b"IDAT", zlib.compress((b"\x00"+b"\xFF\x00\x00"*w)*h))
        + chunk(b"IEND", b""))
    open(path,"wb").write(png)

class TestImagePicker:
    def test_halfblocks(self): assert isinstance(ImagePicker.halfblocks(), ImagePicker)
    def test_kitty(self):      assert isinstance(ImagePicker.kitty(), ImagePicker)
    def test_sixel(self):      assert isinstance(ImagePicker.sixel(), ImagePicker)
    def test_with_font_size(self): assert isinstance(ImagePicker.with_font_size(8,16), ImagePicker)
    def test_from_query(self):
        try: assert isinstance(ImagePicker.from_query(), ImagePicker)
        except RuntimeError: pytest.skip("no TTY")
    def test_repr(self):
        assert repr(ImagePicker.halfblocks()) == "ImagePicker"
        assert repr(ImagePicker.kitty())      == "ImagePicker"
        assert repr(ImagePicker.sixel())      == "ImagePicker"

class TestImagePickerLoad:
    def test_load_halfblocks(self):
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f: p=f.name
        try: _make_png(p); assert isinstance(ImagePicker.halfblocks().load(p), ImageState)
        finally: os.unlink(p)
    def test_load_kitty(self):
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f: p=f.name
        try: _make_png(p); assert isinstance(ImagePicker.kitty().load(p), ImageState)
        finally: os.unlink(p)
    def test_load_sixel(self):
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f: p=f.name
        try: _make_png(p); assert isinstance(ImagePicker.sixel().load(p), ImageState)
        finally: os.unlink(p)
    def test_load_missing(self):
        with pytest.raises(OSError): ImagePicker.halfblocks().load("/nope.png")
    def test_load_invalid(self):
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            f.write(b"not a png"); p=f.name
        try:
            with pytest.raises(Exception): ImagePicker.halfblocks().load(p)
        finally: os.unlink(p)

class TestImageState:
    def test_path(self):
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f: p=f.name
        try: _make_png(p); assert ImagePicker.halfblocks().load(p).path == p
        finally: os.unlink(p)
    def test_no_direct_instantiation(self):
        with pytest.raises(TypeError): ImageState()

class TestImageWidget:
    def test_instantiation(self): assert isinstance(ImageWidget(), ImageWidget)
    def test_repr(self):          assert repr(ImageWidget()) == "ImageWidget"

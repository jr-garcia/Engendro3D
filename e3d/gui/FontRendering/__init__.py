from .japanese_range import jrange


class CharRangesEnum:
    latin = ('latin', (0x0020, 0x007F))
    katakana = ('katakana', (0x30A0, 0x30FF))
    egipt_hieroglyphs = ('egipt_hieroglyphs', (0x13000, 0x1342F))
    japanese = ('japanese', jrange)

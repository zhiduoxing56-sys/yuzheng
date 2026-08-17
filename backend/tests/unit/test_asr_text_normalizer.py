from app.services.asr.text_normalizer import TraditionalChineseNormalizer


def test_traditional_asr_text_is_converted_to_simplified() -> None:
    normalizer = TraditionalChineseNormalizer()

    assert normalizer.to_simplified("請幫我打開左側車門") == "请帮我打开左侧车门"


def test_simplified_asr_text_is_preserved() -> None:
    normalizer = TraditionalChineseNormalizer()

    assert normalizer.to_simplified("请帮我打开左侧车门") == "请帮我打开左侧车门"

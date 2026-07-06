"""Tests for tgbot.i18n — bot-level i18n module."""
import pytest

from tgbot.i18n import DEFAULT_LANG, SUPPORTED_LANGS, TRANSLATIONS, get_lang, t_bot


# ---------------------------------------------------------------------------
# get_lang
# ---------------------------------------------------------------------------

class TestGetLang:
    def test_russian_code_returns_ru(self):
        assert get_lang('ru') == 'ru'

    def test_russian_regional_code_returns_ru(self):
        assert get_lang('ru-RU') == 'ru'

    def test_english_code_returns_en(self):
        assert get_lang('en') == 'en'

    def test_ukrainian_code_falls_back_to_en(self):
        assert get_lang('uk') == 'en'

    def test_none_falls_back_to_en(self):
        assert get_lang(None) == 'en'

    def test_empty_string_falls_back_to_en(self):
        assert get_lang('') == 'en'

    def test_unknown_code_falls_back_to_en(self):
        assert get_lang('zh') == 'en'

    def test_default_lang_is_en(self):
        assert DEFAULT_LANG == 'en'


# ---------------------------------------------------------------------------
# t_bot — basic translations
# ---------------------------------------------------------------------------

class TestTBotTranslations:
    def test_russian_btn_back(self):
        assert t_bot('btn_back', 'ru') == '↩️ Назад'

    def test_english_btn_back(self):
        assert t_bot('btn_back', 'en') == '↩️ Back'

    def test_russian_btn_next(self):
        assert t_bot('btn_next', 'ru') == '➡️ Дальше'

    def test_english_btn_next(self):
        assert t_bot('btn_next', 'en') == '➡️ Next'

    def test_russian_hello(self):
        assert t_bot('hello', 'ru') == 'Привет, '

    def test_english_hello(self):
        assert t_bot('hello', 'en') == 'Hello, '

    def test_fallback_on_missing_key_returns_key(self):
        assert t_bot('nonexistent_key_xyz', 'ru') == 'nonexistent_key_xyz'

    def test_fallback_on_missing_key_english(self):
        assert t_bot('nonexistent_key_xyz', 'en') == 'nonexistent_key_xyz'

    def test_unknown_lang_falls_back_to_default_lang(self):
        # Should return the DEFAULT_LANG translation
        result = t_bot('btn_back', 'zh')
        assert result == t_bot('btn_back', DEFAULT_LANG)

    def test_default_lang_used_when_no_lang_arg(self):
        # No lang kwarg → uses DEFAULT_LANG
        assert t_bot('btn_back') == t_bot('btn_back', DEFAULT_LANG)


# ---------------------------------------------------------------------------
# t_bot — kwargs formatting
# ---------------------------------------------------------------------------

class TestTBotFormatting:
    def test_format_with_name_kwarg_english(self):
        result = t_bot('enter_height_for', 'en', name='Site Alpha')
        assert 'Site Alpha' in result

    def test_format_with_name_kwarg_russian(self):
        result = t_bot('enter_height_for', 'ru', name='Точка А')
        assert 'Точка А' in result

    def test_format_with_btn_next_kwarg_english(self):
        btn = t_bot('btn_next', 'en')
        result = t_bot('coords_entered_default_heights', 'en', btn_next=btn)
        assert btn in result

    def test_format_with_file_id_kwarg(self):
        result = t_bot('file_id_saved', 'en', file_id='abc123')
        assert 'abc123' in result

    def test_format_missing_kwarg_returns_raw_template(self):
        # Missing required kwarg should not raise, just return the template
        result = t_bot('enter_height_for', 'en')
        # Returns raw template string (without substitution)
        assert 'enter_height_for' not in result  # key is NOT returned; template is


# ---------------------------------------------------------------------------
# TRANSLATIONS completeness
# ---------------------------------------------------------------------------

class TestTranslationsCompleteness:
    def test_all_supported_langs_present(self):
        for lang in SUPPORTED_LANGS:
            assert lang in TRANSLATIONS, f"Language '{lang}' missing from TRANSLATIONS"

    def test_same_keys_in_all_languages(self):
        ru_keys = set(TRANSLATIONS['ru'].keys())
        en_keys = set(TRANSLATIONS['en'].keys())
        missing_in_en = ru_keys - en_keys
        missing_in_ru = en_keys - ru_keys
        assert not missing_in_en, f"Keys in 'ru' but not 'en': {missing_in_en}"
        assert not missing_in_ru, f"Keys in 'en' but not 'ru': {missing_in_ru}"

    def test_no_empty_translations(self):
        """All translation values must be non-empty strings (except known empty ones)."""
        allowed_empty = {'btn_like'}  # intentionally blank emoji-only
        for lang, strings in TRANSLATIONS.items():
            for key, value in strings.items():
                if key in allowed_empty:
                    continue
                assert value, f"Empty translation: lang='{lang}', key='{key}'"

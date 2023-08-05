__version__ = '0.1.0'

from html5lib.sanitizer import HTMLSanitizer


class HTMLSanitizerWithIframe(HTMLSanitizer):
    def __init__(self, *args, **kwargs):
        self.allowed_elements.extend(['iframe',])

        self.allowed_attributes.extend([
            'frameborder',
            'allowfullscreen',
            'webkitallowfullscreen',
            'mozallowfullscreen'])

        self.allowed_css_properties.extend([
            'left',
            'right',
            'top',
            'bottom',
            'position',
            'padding',
            'padding-left',
            'padding-right',
            'padding-top',
            'padding-bottom'])

        super(HTMLSanitizerWithIframe, self).__init__(*args, **kwargs)

domain=collective.favorites
i18ndude rebuild-pot --pot $domain.pot --merge $domain-manual.pot --create $domain ../
i18ndude sync --pot $domain.pot */LC_MESSAGES/$domain.po

i18ndude sync --pot plone-manual.pot */LC_MESSAGES/plone.po

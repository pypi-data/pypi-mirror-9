from plone.directives import form
from seantis.people.types.base import PersonBase


class ITranslator(form.Schema):
    form.model("translator.xml")


class Translator(PersonBase):

    @property
    def phone_numbers(self):

        phone_numbers = []

        if self.mobile_phone:
            phone_numbers.append('<div class="mobile-phone">{}</div>'.format(
                self.mobile_phone
            ))

        if self.private_phone:
            phone_numbers.append('<div class="private-phone">{}</div>'.format(
                self.private_phone
            ))

        if self.work_phone:
            phone_numbers.append('<div class="work-phone">{}</div>'.format(
                self.work_phone
            ))

        return u'\n'.join(phone_numbers)

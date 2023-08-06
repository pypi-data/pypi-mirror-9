from enum import Enum
from django.core.exceptions import ImproperlyConfigured

from django.http import JsonResponse


class PopupValidAction(Enum):
    new_form = 0
    close = 1
    reload = 2
    redirect = 3


class PopupFormMixin(object):
    form_valid_action = PopupValidAction.reload
    template_name = 'dcbase/form/popup-form.html'
    form_url = None
    dialog_title = None
    submit_text = 'Submit'
    submit_style = 'primary'
    success_url = ''

    def get_form_valid_action(self):
        return self.form_valid_action

    def get_form_url(self):
        if self.form_url is None:
            return self.request.path
        return self.form_url

    def get_submit_text(self):
        return self.submit_text

    def get_dialog_title(self):
        return self.dialog_title

    def get_submit_style(self):
        return self.submit_style

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['form_url'] = self.get_form_url()
        data['dialog_title'] = self.get_dialog_title()
        data['submit_text'] = self.get_submit_text()
        data['submit_style'] = self.get_submit_style()
        return data

    def popup_form_valid(self):
        action = self.get_form_valid_action()

        if action == PopupValidAction.new_form:
            return self._create_new_form_response()

        responseData = {'action': action.name}
        if action == PopupValidAction.redirect:
            responseData['url'] = self.get_success_url()

        return JsonResponse(responseData)

    def get_new_form(self):
        kwargs = {
            'initial': self.get_initial(),
            'prefix': self.get_prefix(),
        }
        form_class = self.get_form_class()
        form = form_class(**kwargs)
        return form

    def _create_new_form_response(self):
        form = self.get_new_form()
        context = self.get_context_data(form=form)
        return self.render_to_response(context)

    def form_valid(self, form):
        super().form_valid(form)
        return self.popup_form_valid()

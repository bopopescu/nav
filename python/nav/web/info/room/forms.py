# -*- coding: utf-8 -*-
#
# Copyright (C) 2012 UNINETT AS
#
# This file is part of Network Administration Visualized (NAV).
#
# NAV is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License version 2 as published by
# the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.  You should have received a copy of the GNU General Public License
# along with NAV. If not, see <http://www.gnu.org/licenses/>.
#

from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms_foundation.layout import (Layout, Row, Column, Submit, Field,
                                            Fieldset)


class SearchForm(forms.Form):
    query = forms.CharField(max_length=100, label='', required=False)

    def __init__(self, *args, **kwargs):
        super(SearchForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = 'room-search'
        self.helper.form_method = 'GET'
        self.helper.layout = Layout(
            Row(
                Column(Field('query', placeholder='Room'),
                       css_class='medium-9'),
                Column(Submit('submit', 'Search', css_class='postfix'),
                       css_class='medium-3'),
                css_class='collapse'
            )
        )


class UploadForm(forms.Form):
    """Form to upload images for a room"""
    title = forms.CharField(max_length=50, required=False, label='')
    roomimage = forms.ImageField(label='')

    def __init__(self, *args, **kwargs):
        super(UploadForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Fieldset(
                'Upload image',
                Row(
                    Column('roomimage', css_class='medium-3'),
                    Column(Field('title', placeholder='Image caption'),
                           css_class='medium-6'),
                    Column(
                        Submit('submit', 'Upload image', css_class='postfix'),
                        css_class='medium-3')
                )
            )
        )

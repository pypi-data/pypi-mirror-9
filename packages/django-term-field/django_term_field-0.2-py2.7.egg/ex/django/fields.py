# -*- coding:utf-8 -*-
import datetime

import django
from django.core.exceptions import ValidationError
from django import forms
from django.forms.util import ErrorList


DEFAULT_TIME_VALUE = datetime.time(23, 59, 59)


class EndTimeField(forms.TimeField):
    def __init__(self, alt_time_value=DEFAULT_TIME_VALUE, *args, **kwargs):
        self.alt_time_value = alt_time_value
        super(EndTimeField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        result = super(EndTimeField, self).to_python(value)
        if result is None:
            return self.alt_time_value
        return result


class EndDateTimeField(forms.SplitDateTimeField):
    '''期間の終了日時を扱うためのフィールド。

    No.    日付        時刻      期待値
    ================================================
    1      <None>      <None>    None
    2      2014-12-13  <None>    2014-12-13 23:59:59
    3      2014-12-13  15:00     2014-12-13 15:00:00
    '''

    def __init__(self, alt_time_value=DEFAULT_TIME_VALUE,
                 input_date_formats=None, input_time_formats=None,
                 *args, **kwargs):
        '''終了日時を扱うためのフィールド。

        時刻フィールドに空白値を入力された場合、強制的に23:59:59を補う。
        require_all_fieldsは必ずFalseで後続処理に渡さないとおかしくなる。
        日付を入力しない場合
            フィールド自体がrequired ->     必須エラー
            フィールド自体はnot required -> 必ずNoneを返す
        時刻を入力しない場合
            必ず23:59:59で補われる。
        '''
        if django.VERSION[:2] >= (1, 7):
            kwargs['require_all_fields'] = False

        errors = self.default_error_messages.copy()
        if 'error_messages' in kwargs:
            errors.update(kwargs['error_messages'])
        localize = kwargs.get('localize', False)
        fields = (
            forms.DateField(
                input_formats=input_date_formats,
                error_messages={'invalid': errors['invalid_date']},
                localize=localize,
                required=False),
            EndTimeField(
                alt_time_value=alt_time_value,
                input_formats=input_time_formats,
                error_messages={'invalid': errors['invalid_time']},
                localize=localize,
                required=False),
        )
        forms.MultiValueField.__init__(self, fields, *args, **kwargs)

    def clean(self, value):
        if not value:
            if self.required:
                raise ValidationError(
                    self.error_messages['required'], code='required'
                )
            else:
                return self.compress([])

        date_field, time_field = self.fields
        date_value, time_value = value
        empties = self._compat_empty_values()
        if self.required and date_value in empties:
            raise ValidationError(
                self.error_messages['required'], code='required'
            )

        clean_data, errors = [], ErrorList()
        for f, v in ((date_field, date_value), (time_field, time_value)):
            try:
                clean_data.append(f.clean(v))
            except ValidationError as e:
                errors.extend(e.error_list)
        if errors:
            raise ValidationError(errors)
        out = self.compress(clean_data)
        self.validate(out)
        self.run_validators(out)
        return out

    def _compat_empty_values(self):
        if hasattr(self, 'empty_values'):
            return self.empty_values
        else:
            import django.core.validators
            return django.core.validators.EMPTY_VALUES

    def compress(self, data_list):
        values = data_list
        if data_list:
            empties = self._compat_empty_values()
            date, time = [x not in empties for x in data_list]
            if not date and time:
                # 時刻だけ入力したとき
                if not self.required:
                    values = []
                else:
                    raise ValidationError(
                        self.error_messages['invalid_date'],
                        code='invalid_date'
                    )
        return super(EndDateTimeField, self).compress(values)

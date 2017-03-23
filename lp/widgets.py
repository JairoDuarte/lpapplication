from datetime import date
from django.forms import widgets
from django.template import loader

class DateSelectorWidget(widgets.MultiWidget):
    def __init__(self, min_year, max_year, attrs=None):
        # Create choices for days, months and years
        days = [(day, day) for day in range(1, 32)]
        months = [
            (1, 'Janvier'), (2, 'Février'), (3, 'Mars'), (4, 'Avril'),
            (5, 'Mai'), (6, 'Juin'), (7, 'Juillet'), (8, 'Août'),
            (9, 'Septembre'), (10, 'Octobre'), (11, 'Novembre'),
            (12, 'Décembre'),
        ]
        years = [(year, year) for year in range(max_year, min_year, -1)]
        _widgets = (
            widgets.Select(attrs=attrs, choices=days),
            widgets.Select(attrs=attrs, choices=months),
            widgets.Select(attrs=attrs, choices=years),
        )
        super(DateSelectorWidget, self).__init__(_widgets, attrs)
    def decompress(self, value):
        if value:
            return [value.day, value.month, value.year]
        return [None, None, None]
    def format_output(self, rendered_widgets):
        return loader.get_template('lp/widgets/datepicker.html').render({'rendered_widgets': rendered_widgets})
    def value_from_datadict(self, data, files, name):
        datelist = [
            widget.value_from_datadict(data, files, name + '_%s' % i)
            for i, widget in enumerate(self.widgets)
        ]
        try:
            d = date(day=int(datelist[0]), month=int(datelist[1]), year=int(datelist[2]))
        except ValueError:
            return ''
        else:
            return d

class SchoolYearWidget(widgets.Select):
    def __init__(self, min_year, max_year, attrs=None):
        _choices = [
            (year, str(year - 1) + '/' + str(year))
            for year in range(max_year, min_year, -1)
        ]
        super(SchoolYearWidget, self).__init__(attrs=attrs, choices=_choices)

class CustomModelSelect(widgets.Select):
    def __init__(self, model, is_optional=False, attrs=None):
        _choices = [
            (str(obj.pk), str(obj))
            for obj in model.objects.all()
        ]
        if is_optional:
            _choices.append(('-1', 'Autre...'))
        super(CustomModelSelect, self).__init__(attrs=attrs, choices=_choices)

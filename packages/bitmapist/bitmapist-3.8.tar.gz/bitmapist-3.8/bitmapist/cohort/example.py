import bitmapist
from werkzeug.wrappers import Request, Response
from bitmapist.cohort import render_html_form, render_html_data, get_dates_data



@Request.application
def application(request):

    load_test_data()

    event_names = bitmapist.get_event_names()
    selections1 = selections2 = [(e, e) for e in event_names]
    select1 = select2 = select3 = 'active'

    html_form = render_html_form(
        action_url='/_Cohort',
        selections1=selections1,
        selections2=selections2,
        time_group='days',
        select1=select1,
        select2=select2,
        select3=select3,
    )


    dates_data = get_dates_data(select1, select2, select3,
                                time_group='days', system='default',
                                as_precent=True, num_results=25)

    html_data = render_html_data(
            dates_data,
            as_precent=True,
            time_group='days',
            num_results=25)

    return Response(u'%s%s' % (html_form, html_data), content_type='text/html')


def load_test_data():
    event_names = bitmapist.get_event_names()
    if event_names:
        return


if __name__ == '__main__':
    from werkzeug.serving import run_simple
    run_simple('localhost', 4000, application,
               use_reloader=True, use_debugger=True)

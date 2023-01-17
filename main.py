from datetime import datetime
import flask
from flask import request, jsonify
from flask import Flask
import holidays

from vacations import get_vacation_recommendation

app = Flask(__name__)

@app.route('/vacation', methods=['GET'])
def vacation():
    start = request.args.get('start')
    end = request.args.get('end')
    max_len = request.args.get('max_len')
    min_len = request.args.get('min_len')
    max_non_holiday_days = request.args.get('max_non_holiday_days')
    country = request.args.get('country')
    sub_region = request.args.get('sub_region')
    if country is None:
        country = 'DE'
    if sub_region is None:
        sub_region = 'SN'

    if start is None or end is None or max_len is None or min_len is None or max_non_holiday_days is None:
        return jsonify({'error': 'missing parameters'}), 400
    
    start = datetime.strptime(start, '%Y-%m-%d').date()
    end = datetime.strptime(end, '%Y-%m-%d').date()
    max_len = int(max_len)
    min_len = int(min_len)
    max_non_holiday_days = int(max_non_holiday_days)

    calendar = holidays.country_holidays(country, subdiv=sub_region)
    recs = get_vacation_recommendation(start, end, calendar, max_len, min_len, max_non_holiday_days)
    out = []
    for rec in recs:
        out.append(rec.__dict__)
    #[{"end":"Wed, 26 Dec 2018 00:00:00 GMT","n_days":5,"n_holidays":4,"ratio":0.8,"start":"Sat, 22 Dec 2018 00:00:00 GMT"},{"end":"Sun, 30 Dec 2018 00:00:00 GMT","n_days":9,"n_holidays":6,"ratio":0.6666666666666666,"start":"Sat, 22 Dec 2018 00:00:00 GMT"},{"end":"Wed, 26 Dec 2018 00:00:00 GMT","n_days":3,"n_holidays":2,"ratio":0.6666666666666666,"start":"Mon, 24 Dec 2018 00:00:00 GMT"},{"end":"Sun, 30 Dec 2018 00:00:00 GMT","n_days":6,"n_holidays":4,"ratio":0.6666666666666666,"start":"Tue, 25 Dec 2018 00:00:00 GMT"},{"end":"Mon, 31 Dec 2018 00:00:00 GMT","n_days":3,"n_holidays":2,"ratio":0.6666666666666666,"start":"Sat, 29 Dec 2018 00:00:00 GMT"}]
    return flask.render_template('results.html', recs=out)

# simple example page for testing above code
@app.route('/')
def index():
    return flask.render_template('index.html')

if __name__ == '__main__':
    app.run(port=3000)

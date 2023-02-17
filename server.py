from flask import Flask, request, jsonify
from flask_restful import Resource, Api
import sqlite3
import redis
import json
import hashlib
import datetime

app = Flask(__name__)
api = Api(app)

redis_conn = redis.Redis(host='localhost', port=6379, db=0)

# Helper to add CO2 totals
def accumulator(container, key, item):
    if key in container:
        container[key] += item
    else:
        container[key] = item
    
def construct_individual_key(business, date):
    return f'{business}_{date}'

# Function to construct a cache key based on the query parameters
def construct_cache_keys(start_date, end_date, business_facilities):
    cache_keys = []
    for business in business_facilities:
        for delta in range(0, (end_date - start_date).days):
            new_start_date = start_date + datetime.timedelta(days=delta)
            key = construct_individual_key(business, new_start_date)
            cache_keys.append(key)
                
    return cache_keys

# Helper to execute DB queries
def sql_query(business_facilities, start_date, end_date, response):
    conn = sqlite3.connect('transactions.db')
    c = conn.cursor()
    query = "SELECT [Business Facility], [TRANSACTION DATE], SUM(CO2_ITEM) FROM transactions WHERE [TRANSACTION DATE] BETWEEN ? AND ? AND [Business Facility] IN ({}) GROUP BY [Business Facility], [TRANSACTION DATE]".format(','.join(['?']*len(business_facilities)))
    params = [start_date, end_date] + business_facilities
    
    c.execute(query, params)
    results = c.fetchall()

    conn.close()

    for result in results:
        to_cache = {}
        business_facility = result[0]
        date = result[1]
        co2_item_sum = result[2]

        redis_conn.setex(construct_individual_key(business_facility, date), 30, json.dumps(co2_item_sum))
    
        accumulator(response, business_facility, co2_item_sum)

class Emissions(Resource):
    def get(self):

        response = {}

        start_date = datetime.datetime.strptime(request.args.get('startDate'), '%Y-%m-%d').date()
        end_date = datetime.datetime.strptime(request.args.get('endDate'), '%Y-%m-%d').date()
        business_facilities = request.args.getlist('businessFacility')

        # Construct list of possible cache keys based on query parameters
        cache_keys = construct_cache_keys(start_date, end_date, business_facilities)
        unhit_cache_keys = []
        hit_cache_keys = []
        
        # Check cache for each possible cache key
        for cache_key in cache_keys:
            cache_data = redis_conn.get(cache_key)
            if cache_data is not None:
                co2_item = json.loads(cache_data.decode('utf-8'))
                split_key = cache_key.split('_')
                accumulator(response, split_key[0], co2_item)
                hit_cache_keys.append(cache_key)
            else:
                unhit_cache_keys.append(cache_key)

        if len(unhit_cache_keys) == 0:
            return jsonify(response)
        elif len(unhit_cache_keys) > 0 and len(hit_cache_keys) > 0:
            # Initialise params for sql_query
            date_keys = []
            business_facilities_cache = []

            # Get range of dates that are not cached
            for key in unhit_cache_keys:
                split_key = key.split('_')
                business_facility = [split_key[0]]
                date_keys.append(split_key[1])
                if business_facility in business_facilities_cache:
                    continue
                else:
                    business_facilities_cache.append(business_facility)

                
            dates = [datetime.datetime.strptime(date, '%Y-%m-%d') for date in date_keys]
            dates.sort()
            start_date = end_date = dates[0]
            ranges = []
            for date in dates[1:]:
                if date - end_date == datetime.timedelta(days=1):
                    end_date = date
                else:
                    ranges.append((start_date, end_date))
                    start_date = end_date = date

            ranges.append((start_date, end_date))

            # For uncached date ranges, query DB
            for date in ranges:
                sql_query(business_facilities, date[0], date[1], response)
                
            return jsonify(response)

        # If query is entirely new, default to this block
        sql_query(business_facilities, start_date, end_date, response)
 
        return jsonify(response)


api.add_resource(Emissions, '/emissions')

if __name__ == '__main__':
    app.run(debug=True)

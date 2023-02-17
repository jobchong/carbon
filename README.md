# Installation

## Prerequisites:

1. Redis
2. Sqlite3
3. Python3

## Installation:

1. `pip3 install flask flask_restful sqlite3 redis`

## Startup:

1. `bash start.sh`

## Query:

1. `curl "http://127.0.0.1:5000/emissions?startDate=2021-01-01&endDate=2021-02-01&businessFacility=GreenEat%20Changi"`

## Response example:

```
{
  "GreenEat Changi": 8480.792301958998,
  "Heybo Marina Bay Link Mall": 38115.101313650994
}
```

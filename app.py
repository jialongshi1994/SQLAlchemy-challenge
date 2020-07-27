from flask import Flask, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Resources/hawaii.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)
db.reflect()
all_table = {table_obj.name: table_obj for table_obj in db.get_tables_for_bind()}
print(all_table)


@app.route('/')
def hello_world():
    return render_template("home_page.html")


@app.route('/api/v1.0/precipitation', methods=['GET'])
def list_precipitation():
    data = db.session.query(all_table["measurement"].c.date.label('date'),
                            all_table["measurement"].c.prcp.label("prcp")).all()
    return render_template('list_precipitation.html', data=data)


@app.route('/api/v1.0/stations', methods=['GET'])
def list_stations():
    data = db.session.query(all_table["station"]).all()
    print(data)
    return render_template('list_stations.html', data=data)


@app.route('/api/v1.0/tobs', methods=['GET'])
def list_tobs():
    data_sub = db.session.query(all_table["measurement"].c.station.label('station'),
                                func.count(all_table["measurement"].c.station).label('station_count')).group_by(
        all_table["measurement"].c.station).subquery()
    data_2_sub = db.session.query(data_sub.c.station.label('station'), func.max(data_sub.c.station_count)).subquery()
    data = db.session.query(all_table["measurement"].c.date, all_table['measurement'].c.tobs,
                            all_table['measurement'].c.station).filter(
        all_table['measurement'].c.station == data_2_sub.c.station).all()
    return render_template('list_tobs.html', data=data)


@app.route('/api/v1.0/<start>/<end>', methods=['GET'])
def get_data(start, end):
    sel = [all_table['measurement'].c.station, func.min(all_table['measurement'].c.tobs),
           func.avg(all_table['measurement'].c.tobs),
           func.max(all_table['measurement'].c.tobs)]
    data = db.session.query(*sel).filter(all_table["measurement"].c.date >= start,
                                         all_table["measurement"].c.date >= end).group_by(
        all_table["measurement"].c.station).all()

    return render_template('static.html', data=data)


if __name__ == '__main__':
    app.run(debug=True)

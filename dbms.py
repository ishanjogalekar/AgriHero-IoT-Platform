import sqlite3
import bcrypt
from datetime import datetime
from flask_login import UserMixin
from flask_restful import Resource, reqparse
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer


class DB:
    def __init__(self, db_name):
        self.db_name = db_name

    def create_user_table(self):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute('''CREATE TABLE users 
                        (id integer PRIMARY KEY,
                        username text UNIQUE NOT NULL,
                        email text UNIQUE NOT NULL,
                        image_file text DEFAULT 'default.jpg',
                        password text NOT NULL)''')
        conn.commit()
        conn.close()

    def create_sensor_table(self):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute('''CREATE TABLE sensors 
                                (id integer PRIMARY KEY,
                                u_id integer,
                                datetime smalldatetime NOT NULL,
                                temperature text NOT NULL,
                                humidity text NOT NULL,
                                avg_soil_humidity text NOT NULL,
                                rain text NOT NULL,
                                wind_speed text NOT NULL,
                                camera_analysis text NOT NULL,
                                water_status text NOT NULL,
                                gas text NOT NULL,
                                color text NOT NULL,
                                status text NOT NULL)''')
        conn.commit()
        c.close()
        conn.close()

    def create_listings_table(self):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute('''CREATE TABLE listings 
                                (id integer PRIMARY KEY,
                                u_id integer,
                                datetime smalldatetime NOT NULL,
                                name text NOT NULL,
                                price real NOT NULL,
                                units text NOT NULL,
                                info text NOT NULL,
                                image_name text NOT NULL,
                                location text NOT NULL,
                                verified text NOT NULL,
                                negotiable text NOT NULL)''')
        conn.commit()
        c.close()
        conn.close()

    def add_user(self, username, email, password):
        encoded_pw = password.encode('utf-8')
        hashed_pw = bcrypt.hashpw(encoded_pw, bcrypt.gensalt())
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        data = (username, email, hashed_pw)
        try:
            c.execute('''INSERT INTO users (username, email, password)
                            VALUES (?, ?, ?)''', data)
            conn.commit()
            c.close()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            conn.commit()
            c.close()
            conn.close()
            return False

    def add_sensor(self, user_id, time, date, temp, humid, avg_soil_humid,
                   rain, wind, cam, water_status, gas, color, status):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        dt_object = datetime.strptime(date+' '+time, '%d/%m/%y %H:%M:%S')

        data = (user_id, dt_object.strftime('%d/%m/%y %H:%M:%S'), temp, humid, avg_soil_humid,
                rain, wind, cam, water_status, gas, color, status)
        c.execute('''INSERT INTO sensors (u_id, datetime, temperature, humidity, avg_soil_humidity, rain, wind_speed, camera_analysis, water_status, gas, color, status)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', data)
        conn.commit()
        c.close()
        conn.close()

    @classmethod
    def add_sensor_api(cls, user_id, time, date, temp, humid, avg_soil_humid,
                       rain, wind, cam, water_status, gas, color, status):
        dt_object = datetime.strptime(date + ' ' + time, '%d/%m/%y %H:%M:%S')
        conn = sqlite3.connect('site.db')
        c = conn.cursor()
        data = (user_id, dt_object.strftime('%d/%m/%y %H:%M:%S'), temp, humid, avg_soil_humid,
                rain, wind, cam, water_status, gas, color, status)
        c.execute('''INSERT INTO sensors (u_id, datetime, temperature, humidity, avg_soil_humidity, rain, wind_speed, camera_analysis, water_status, gas, color, status)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', data)
        conn.commit()
        c.close()
        conn.close()

    @classmethod
    def add_listing(cls, user_id, time, date, name, price, units, info, image_name, location, verified, negotiable):
        dt_object = datetime.strptime(date + ' ' + time, '%d/%m/%y %H:%M:%S')

        conn = sqlite3.connect('site.db')
        c = conn.cursor()
        data = (user_id, dt_object.strftime('%d/%m/%y %H:%M:%S'), name, price, info, units, image_name, location, verified, negotiable)

        c.execute('''INSERT INTO listings (u_id, datetime, name, price, units, info, image_name, location, verified, negotiable)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', data)
        conn.commit()
        c.close()
        conn.close()

        return True

    def is_email(self, email):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute('''SELECT password FROM users
                                WHERE email=?''', (email,))
        emails = c.fetchone()
        c.close()
        conn.close()
        if emails is None:
            return False
        else:
            return True

    def is_username(self, username):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute('''SELECT password FROM users
                                WHERE username=?''', (username,))
        usernames = c.fetchone()
        c.close()
        conn.close()
        if usernames is None:
            return False
        else:
            return True

    def check_login(self, username, password):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute('''SELECT password FROM users
                        WHERE username=?''', (username,))
        try:
            hashed_pd = c.fetchone()[0]
        except TypeError:
            return False
        c.close()
        conn.close()
        return bcrypt.checkpw(password.encode('utf-8'), hashed_pd)

    def get_sensor(self, username=None):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        if username is None:
            c.execute('''SELECT users.username, sensors.datetime, sensors.temperature, sensors.humidity, sensors.avg_soil_humidity, sensors.rain, sensors.wind_speed, sensors.camera_analysis, sensors.water_status, sensors.gas, sensors.color, sensors.status
                            FROM users
                            JOIN sensors
                            ON users.id=sensors.u_id
                            ORDER BY datetime DESC
                            LIMIT 1''')
        else:
            c.execute('''SELECT sensors.datetime, sensors.temperature, sensors.humidity, sensors.avg_soil_humidity, sensors.rain, sensors.wind_speed, sensors.camera_analysis, sensors.water_status, sensors.gas, sensors.color, sensors.status
                            FROM users
                            JOIN sensors
                            ON users.id=sensors.u_id
                            WHERE users.username=?
                            ORDER BY datetime DESC
                            LIMIT 1''', (username,))
        sensor = c.fetchall()
        c.close()
        conn.close()
        return sensor[0]

    def get_sensor_all(self, username=None):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        if username is None:
            c.execute('''SELECT users.username, sensors.datetime, sensors.temperature, sensors.humidity, sensors.avg_soil_humidity, sensors.rain, sensors.wind_speed, sensors.camera_analysis, sensors.water_status, sensors.gas, sensors.color, sensors.status
                            FROM users
                            JOIN sensors
                            ON users.id=sensors.u_id
                            ORDER BY datetime DESC''')
        else:
            c.execute('''SELECT sensors.datetime, sensors.temperature, sensors.humidity, sensors.avg_soil_humidity, sensors.rain, sensors.wind_speed, sensors.camera_analysis, sensors.water_status, sensors.gas, sensors.color, sensors.status
                            FROM users
                            JOIN sensors
                            ON users.id=sensors.u_id
                            WHERE users.username=?
                            ORDER BY datetime DESC''', (username,))
        sensor = c.fetchall()
        c.close()
        conn.close()
        return sensor

    def get_dummy_data(self):
        return [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, "0"]

    def get_listing(self, product_id):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute('''SELECT listings.u_id, listings.datetime, listings.name, listings.price, listings.units, listings.info, listings.image_name, listings.location, listings.verified, listings.negotiable
                                FROM listings
                                WHERE listings.id=?''', (product_id, ))
        listing = c.fetchall()
        c.close()
        conn.close()
        return listing[0]

    def get_listings_all(self):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute('''SELECT listings.id, listings.u_id, listings.datetime, listings.name, listings.price, listings.units, listings.info, listings.image_name, listings.location, listings.verified, listings.negotiable
                                FROM listings
                                ORDER BY datetime DESC''')
        listings = c.fetchall()
        c.close()
        conn.close()
        return listings

    def update_picture(self, picture, username):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute('''UPDATE users SET image_file=? WHERE username=?''', (picture, username))
        conn.commit()
        c.close()
        conn.close()

    def get_id(self, username):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute('''SELECT id FROM users
                        WHERE username=?''', (username,))
        user_id = c.fetchone()[0]
        c.close()
        conn.close()
        return user_id

    def get_email(self, username):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute('''SELECT email FROM users
                                WHERE username=?''', (username,))
        email = c.fetchone()[0]
        c.close()
        conn.close()
        return email

    def get_image(self, username):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute('''SELECT image_file FROM users
                                WHERE username=?''', (username,))
        image = c.fetchone()[0]
        c.close()
        conn.close()
        return image

    def reset_pw(self, user_id, password):
        encoded_pw = password.encode('utf-8')
        hashed_pw = bcrypt.hashpw(encoded_pw, bcrypt.gensalt())
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute('''UPDATE users
                        SET password=?
                        WHERE username=?''', (hashed_pw, user_id))
        conn.commit()
        c.close()
        conn.close()

    def check_product_id(self, product_id):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute('''SELECT listings.id 
                        FROM listings 
                        WHERE listings.id = ?;''', (product_id,))
        result = c.fetchone()
        conn.commit()
        c.close()
        conn.close()

        return result


class User(UserMixin):

    def __init__(self, username):
        db = DB('site.db')
        self.username = username
        self.id = username
        self.email = db.get_email(self.username)
        self.user_id = db.get_id(self.username)
        self.image = db.get_image(self.username)

    def get_sensors_all(self):
        db = DB('site.db')
        return db.get_sensor_all(self.username)

    def reset_pass(self):
        s = Serializer('saksham2001', 1800)
        return s.dumps({'user_id': self.user_id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer('saksham2001')
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return user_id


class SensorData(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('u_id', type=str, required=True, help='this field cannot be left blank')
    parser.add_argument('time', type=str, required=True, help='this field cannot be left blank')
    parser.add_argument('date', type=str, required=True, help='this field cannot be left blank')
    parser.add_argument('temperature', type=str, required=True, help='this field cannot be left blank')
    parser.add_argument('humidity', type=str, required=True, help='this field cannot be left blank')
    parser.add_argument('av_soil_humidity', type=str, required=True, help='this field cannot be left blank')
    parser.add_argument('rain', type=str, required=True, help='this field cannot be left blank')
    parser.add_argument('wind_speed', type=str, required=True, help='this field cannot be left blank')
    parser.add_argument('camera_analysis', type=str, required=True, help='this field cannot be left blank')
    parser.add_argument('water_status', type=str, required=True, help='this field cannot be left blank')
    parser.add_argument('gas', type=str, required=True, help='this field cannot be left blank')
    parser.add_argument('color', type=str, required=True, help='this field cannot be left blank')
    parser.add_argument('status', type=str, required=True, help='this field cannot be left blank')

    def post(self, username):

        data = SensorData.parser.parse_args()

        try:
            DB.add_sensor_api(data['u_id'], data['time'], data['date'], data['temperature'], data['humidity'],
                              data['av_soil_humidity'], data['rain'], data['wind_speed'], data['camera_analysis'],
                              data['water_status'], data['gas'], data['color'], data['status'])
        except:
            return {'An error occurred while inserting the item'}, 500

        data_inst = {'u_id': data['u_id'], 'time': data['time'], 'date': data['date'], 'temperature': data['temperature'],
                     'humidity': data['humidity'], 'av_soil_humidity': data['av_soil_humidity'], 'rain': data['rain'],
                     'wind_speed': data['wind_speed'], 'camera_analysis': data['camera_analysis'],
                     'water_status': data['water_status'], 'gas': data['gas'], 'color': data['color'],
                     'status': data['status'], 'username': username}

        return data_inst, 201
from dbms import DB

db = DB('site.db')

db.create_user_table()
db.create_sensor_table()
db.create_listings_table()

db.add_user('adminone', 'adminone@gmail.com', 'eknumber')
db.add_listing(1, '00:00:01', "01/01/15", 'wheat', 10.01, 'per Ton', 'Best Quality', 'wheat.jpeg', 'Mirzapur, Uttar Pradesh', 'TRUE', 'TRUE')
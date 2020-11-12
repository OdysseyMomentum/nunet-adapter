pg_createcluster 10 main  #!! needed on new postgresql volume maps(maybe, maybe)

/etc/init.d/postgresql start
sudo -u postgres bash ../setup_db.sh
python3.6 ../create_network.py
python3.6  populate_db.py --data initial_fixtures.json 
python3.6  session_manager_server.py 

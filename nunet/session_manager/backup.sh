#the server address to store the database should be filled before running. 
now=$(date +%"s")
db_name="**$now.bak"
docker exec ** bash -c "PGPASSWORD="**" pg_dump -h localhost -p 5432 -U ** ** > "$db_name""
sudo docker cp production_nunet:/nunet-demo/session_manager/"$db_name" "$db_name"
sudo scp "$db_name" nunet-backup@*.*.*.*:/home/nunet-backup

psql <<  EOF
      CREATE DATABASE nunet_db;
      CREATE USER nunet WITH PASSWORD 'nunet';
      \c nunet_db
      GRANT ALL PRIVILEGES ON DATABASE nunet_db TO nunet;
EOF
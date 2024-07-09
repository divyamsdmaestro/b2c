docker run -e "ACCEPT_EULA=Y" -e "MSSQL_SA_PASSWORD=YourStrong@Passw0rd" \
   -p 1433:1433 --name sql_b2c_backend --hostname sql_b2c_backend \
   -d mcr.microsoft.com/mssql/server:2022-latest

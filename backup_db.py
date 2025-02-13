import subprocess
# pip install mysqldump

def backup_mysql_database(host, user, password, database, output_file):
    try:
        command = f"mysqldump -h {host} -u {user} -p{password} {database} > {output_file}"
        subprocess.run(command, shell=True, check=True)
        print(f"Backup berhasil disimpan di {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"Terjadi kesalahan saat backup: {e}")

backup_mysql_database(
    host="viaduct.proxy.rlwy.net",
    user="root",
    password="BidvozghXocWEgDjBxvHoOFgjAPoRnqM",
    database="railway",
    output_file="backup.sql"
)

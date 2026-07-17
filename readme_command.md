# バックアップスクリプト

```
#!/bin/bash
# Redmineバックアップ＆Windows共有フォルダへコピー

# バックアップ保存先（Ubuntu側）
BACKUP_DIR=~/backup/redmine/$(date +%Y%m%d)
mkdir -p $BACKUP_DIR

# 1. DBバックアップ
docker exec redmine-docker-db-1 mysqldump -u root -pexample redmine > $BACKUP_DIR/redmine_db.sql

# 2. filesディレクトリバックアップ
docker cp redmine-docker-app-1:/usr/src/redmine/files $BACKUP_DIR/files

# 3. configディレクトリバックアップ
docker cp redmine-docker-app-1:/usr/src/redmine/config $BACKUP_DIR/config

# 4. tarでまとめる
cd $BACKUP_DIR/..
ARCHIVE=redmine_backup_$(date +%Y%m%d).tar.gz
tar czf $ARCHIVE $(date +%Y%m%d)

# 5. Windows共有フォルダへコピー
cp $ARCHIVE /mnt/windows_backup/

echo "バックアップ完了: $ARCHIVE を /mnt/windows_backup にコピーしました"
```

# コピーに必要なマウント設定
```
sudo mount -t cifs //192.168.0.181/RedmineBackup /mnt/windows_backup -o username=D-FPGASERVER,password=9999,uid=$(id -u),gid=$(id -g),file_mode=0777,dir_mode=0777
```


# cronのログ閲覧
```
grep CRON /var/log/syslog
```

# 自動でマウントする方法
```
//192.168.0.181/RedmineBackup /mnt/windows_backup cifs username=D-FPGASERVER,password=9999,uid=1000,gid=1000,file_mode=0777,dir_mode=0777 0 0
```

# マウント設定反映（再起動せず）
```
sudo mount -a
```

# 再マウント確認
```
mount | grep cifs
```

# コピー・削除 cp rm
```
rm -rf フォルダ名
cp -r フォルダ名
```

# redmine-serverのHDDの容量を確認したい
```
df -h
```

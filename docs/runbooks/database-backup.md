# Runbook: Database Backup

## Objective
Create a safe backup of the production database.

## Prerequisites
- Admin access to server (SSH: root@97v.ru)
- kubectl installed
- 30 minutes available

## Steps

### 1. Check Database Status
```bash
ssh root@97v.ru
systemctl status postgresql
```

**Expected output:** Active (running)

### 2. Create Backup
```bash
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump super_brain > backup_$DATE.sql
```

**Expected output:** Backup file created

### 3. Verify Backup
```bash
ls -lh backup_*.sql
head -n 10 backup_*.sql
```

**Expected output:** File exists with reasonable size

### 4. Upload to S3
```bash
aws s3 cp backup_$DATE.sql s3://backups/
```

**Expected output:** Upload successful

## Verification
- [ ] Backup file exists
- [ ] File size > 1MB
- [ ] File uploaded to S3
- [ ] Can view file in S3 console

## Rollback
N/A (read-only operation)

## Duration
Approximately 15 minutes

## Troubleshooting

**Issue:** PostgreSQL not running
```bash
systemctl start postgresql
systemctl status postgresql
```

**Issue:** Disk space full
```bash
df -h
rm -rf /tmp/old_backups
```

**Issue:** S3 upload fails
- Check AWS credentials
- Verify network connectivity
- Check S3 bucket permissions

## Contact
admin@97v.ru

import sys
import os
import time
import shutil
import hashlib
import zipfile
import logging
import smtplib
import schedule
from email.message import EmailMessage


LOG_DIR = "Logs"
LOG_FILE = os.path.join(LOG_DIR, "Backup.log")
HISTORY_FILE = "history.txt"
BACKUP_DIR = "MarvellousBackup"
EXCLUDE_EXT = (".tmp", ".log", ".exe")

SENDER_EMAIL = "aditishinde270523@gmail.com"
APP_PASSWORD = "fecxsegmafxoirhb"
RECEIVER_EMAIL = "satugade87@gmail.com"

def CreateLog():
    if not os.path.exists(LOG_DIR):
        os.mkdir(LOG_DIR)

    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.INFO,
        format="%(asctime)s : %(levelname)s : %(message)s"
    )


def CalculateHash(path):
    hobj = hashlib.md5()
    with open(path, "rb") as f:
        while True:
            data = f.read(1024)
            if not data:
                break
            hobj.update(data)
    return hobj.hexdigest()


def BackupFiles(Source):
    copied = []
    os.makedirs(BACKUP_DIR, exist_ok=True)

    for root, dirs, files in os.walk(Source):
        for file in files:
            if file.endswith(EXCLUDE_EXT):
                continue

            src_path = os.path.join(root, file)
            relative = os.path.relpath(src_path, Source)
            dest_path = os.path.join(BACKUP_DIR, relative)

            os.makedirs(os.path.dirname(dest_path), exist_ok=True)

            if (not os.path.exists(dest_path)) or \
               (CalculateHash(src_path) != CalculateHash(dest_path)):
                shutil.copy2(src_path, dest_path)
                copied.append(relative)

    return copied


def CreateZip():
    timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
    zip_name = f"Backup_{timestamp}.zip"

    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as z:
        for root, dirs, files in os.walk(BACKUP_DIR):
            for file in files:
                full = os.path.join(root, file)
                relative = os.path.relpath(full, BACKUP_DIR)
                z.write(full, relative)

    return zip_name, os.path.getsize(zip_name)


def AddHistory(files, size):
    with open(HISTORY_FILE, "a") as f:
        f.write(f"{time.ctime()} | Files Copied: {files} | Zip Size: {size}\n")


def SendMail(zipfile_name):
    try:
        current_time = time.ctime()

        msg = EmailMessage()
        msg["From"] = SENDER_EMAIL
        msg["To"] = RECEIVER_EMAIL
        msg["Subject"] = "Marvellous Data Shield – Backup Report"

        body = f"""
Jay Ganesh 

Backup Process Completed Successfully.

Backup Time : {current_time}
Backup File : {zipfile_name}

Please find the backup ZIP file attached with this mail.

Regards,
Marvellous Infosystems
"""
        msg.set_content(body)

    
        with open(zipfile_name, "rb") as f:
            msg.add_attachment(
                f.read(),
                maintype="application",
                subtype="octet-stream",
                filename=zipfile_name
            )

        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(SENDER_EMAIL, APP_PASSWORD)
        server.send_message(msg)
        server.quit()

        print("Mail sent successfully")
        logging.info("Mail sent successfully")

    except Exception as e:
        print("Mail sending failed:", e)
        logging.error(f"Mail Error: {e}")


def StartBackup(Source):
    print("\nBackup started at:", time.ctime())
    logging.info("Backup started")

    files = BackupFiles(Source)
    zip_name, size = CreateZip()

    logging.info(f"Files copied: {len(files)}")
    logging.info(f"Zip created: {zip_name}")

    AddHistory(len(files), size)
    SendMail(zip_name)

    print("Backup completed successfully")


def main():
    CreateLog()

    Border = "-" * 50
    print(Border)
    print("--------- Marvellous Data Shield System ----------")
    print(Border)

    if len(sys.argv) == 3:
        interval = int(sys.argv[1])
        source = sys.argv[2]

        schedule.every(interval).minutes.do(StartBackup, source)

        print("Backup scheduler started")
        print("Time Interval (minutes):", interval)
        print("Source Directory:", source)
        print("Press Ctrl + C to stop")
        print(Border)

        while True:
            schedule.run_pending()
            time.sleep(1)

    else:
        print("Usage:")
        print("python Backup.py <TimeInterval> <SourceDirectory>")
        print("Example: python Backup.py 5 Data")

if __name__ == "__main__":
    main()

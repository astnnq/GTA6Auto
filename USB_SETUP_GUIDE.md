# USB Storage Setup For Raspberry Pi

Use this when the Pi SD card is too small for the pipeline.

The best setup is:

```text
SD card: operating system only
USB drive: project, Python environment, clips, audio, renders, thumbnails, review folder
```

## 1. Plug In The USB Drive

SSH into the Pi:

```bash
ssh pi@YOUR_PI_IP
```

Find the USB device:

```bash
lsblk -f
```

Look for something like:

```text
sda
└─sda1  exfat   USBNAME
```

The partition is usually `/dev/sda1`.

## 2. Option A: Use The USB Without Formatting

If the drive already has a filesystem and you do not want to erase it:

```bash
sudo mkdir -p /mnt/gta6-usb
sudo mount /dev/sda1 /mnt/gta6-usb
sudo chown -R $USER:$USER /mnt/gta6-usb
mkdir -p /mnt/gta6-usb/gta6-pipeline
```

Make it mount automatically after reboot:

```bash
sudo blkid /dev/sda1
```

Copy the `UUID` and filesystem `TYPE`, then edit:

```bash
sudo nano /etc/fstab
```

Add a line like this, replacing the UUID and type:

```text
UUID=YOUR_UUID /mnt/gta6-usb exfat defaults,nofail,uid=1000,gid=1000 0 2
```

For ext4 drives, use:

```text
UUID=YOUR_UUID /mnt/gta6-usb ext4 defaults,nofail 0 2
```

Test it:

```bash
sudo umount /mnt/gta6-usb
sudo mount -a
df -h
```

## 3. Option B: Format The USB For Linux

This erases the USB drive.

```bash
sudo umount /dev/sda1 2>/dev/null || true
sudo mkfs.ext4 -F /dev/sda1
sudo mkdir -p /mnt/gta6-usb
sudo mount /dev/sda1 /mnt/gta6-usb
sudo chown -R $USER:$USER /mnt/gta6-usb
mkdir -p /mnt/gta6-usb/gta6-pipeline
```

Make it auto-mount:

```bash
UUID=$(sudo blkid -s UUID -o value /dev/sda1)
echo "UUID=$UUID /mnt/gta6-usb ext4 defaults,nofail 0 2" | sudo tee -a /etc/fstab
sudo umount /mnt/gta6-usb
sudo mount -a
df -h
```

## 4. Copy The Project To USB

From your Windows PC:

```powershell
cd "C:\Users\austi\OneDrive\Documents\gta6-pipeline\gta6-pipeline"
.\deploy_to_pi.ps1 -PiHost YOUR_PI_IP -PiUser pi -RemoteDir /mnt/gta6-usb/gta6-pipeline
```

## 5. Install Onto The USB

On the Pi:

```bash
cd /mnt/gta6-usb/gta6-pipeline
PROJECT_DIR=/mnt/gta6-usb/gta6-pipeline bash setup.sh
```

This puts the virtual environment and generated files on the USB instead of the SD card.

## 6. Run It

```bash
cd /mnt/gta6-usb/gta6-pipeline
.venv/bin/python run_pipeline.py dry
```

Finished drafts will go to:

```text
/mnt/gta6-usb/gta6-pipeline/review/
```

## 7. Check Space

```bash
df -h
du -sh /mnt/gta6-usb/gta6-pipeline/*
```

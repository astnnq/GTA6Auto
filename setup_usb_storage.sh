#!/bin/bash
# Prepare a USB drive for the GTA6 pipeline on Raspberry Pi.
# WARNING: Formatting mode erases the selected USB partition.

set -e

DEVICE="${1:-}"
MOUNT_POINT="${2:-/mnt/gta6-usb}"
FORMAT="${FORMAT_USB:-false}"

if [ -z "$DEVICE" ]; then
  echo "Usage: bash setup_usb_storage.sh /dev/sda1"
  echo ""
  echo "Find the USB partition with:"
  echo "  lsblk -f"
  echo ""
  echo "Optional erase/format mode:"
  echo "  FORMAT_USB=true bash setup_usb_storage.sh /dev/sda1"
  exit 1
fi

echo "Selected device: ${DEVICE}"
echo "Mount point: ${MOUNT_POINT}"

if [ "$FORMAT" = "true" ]; then
  echo ""
  echo "WARNING: This will erase ${DEVICE}."
  read -r -p "Type ERASE to continue: " CONFIRM
  if [ "$CONFIRM" != "ERASE" ]; then
    echo "Cancelled."
    exit 1
  fi
  sudo umount "$DEVICE" 2>/dev/null || true
  sudo mkfs.ext4 -F "$DEVICE"
fi

sudo mkdir -p "$MOUNT_POINT"
sudo mount "$DEVICE" "$MOUNT_POINT"
sudo chown -R "$USER:$USER" "$MOUNT_POINT"

UUID="$(sudo blkid -s UUID -o value "$DEVICE")"
FSTYPE="$(sudo blkid -s TYPE -o value "$DEVICE")"

if [ -z "$UUID" ] || [ -z "$FSTYPE" ]; then
  echo "Could not read UUID or filesystem type for ${DEVICE}."
  exit 1
fi

FSTAB_LINE="UUID=${UUID} ${MOUNT_POINT} ${FSTYPE} defaults,nofail 0 2"

if ! grep -q "$UUID" /etc/fstab; then
  echo "Adding USB mount to /etc/fstab..."
  echo "$FSTAB_LINE" | sudo tee -a /etc/fstab >/dev/null
else
  echo "USB already appears in /etc/fstab."
fi

mkdir -p "${MOUNT_POINT}/gta6-pipeline"

echo ""
echo "USB storage is ready."
echo "Project folder:"
echo "  ${MOUNT_POINT}/gta6-pipeline"
echo ""
echo "To install the pipeline there:"
echo "  cd ${MOUNT_POINT}/gta6-pipeline"
echo "  PROJECT_DIR=${MOUNT_POINT}/gta6-pipeline bash setup.sh"

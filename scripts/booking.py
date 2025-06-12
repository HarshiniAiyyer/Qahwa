import re
import csv
import uuid  # ✅ Add this import
from datetime import datetime
from utils.emails import send_confirmation_email

bookings = 'D:\\qar\\data\\bookingslist.csv'  # You may update this path

def extractinfo(entry: str):
    emails = re.search(r'[\w\.-]+@[\w\.-]+(?=[^\w\.-]|$)', entry)
    dates = re.search(r'\b\d{1,2}/\d{1,2}/\d{2,4}\b', entry)
    times = re.search(r'\b\d{1,2}[:.]\d{2}\s?(AM|PM|am|pm)?\b', entry)
    names = re.search(r"My name is ([A-Za-z ]+)", entry)

    email = emails.group(0) if emails else ""
    email = email.rstrip('.,;:!?')

    return {
        "name": names.group(1).strip() if names else "Anonymous",
        "email": email,
        "date": dates.group(0) if dates else "",
        "time": times.group(0).upper().replace(".", ":") if times else "",
        "timestamp": datetime.now().isoformat()
    }

def slot_is_full(date: str, time: str) -> bool:
    try:
        with open(bookings, mode="r", newline="") as csvfile:
            reader = csv.DictReader(csvfile)
            count = sum(1 for row in reader if row["date"] == date and row["time"] == time)
            return count >= 10
    except FileNotFoundError:
        return False

def savebooking(infos: dict) -> bool:
    if slot_is_full(infos["date"], infos["time"]):
        return False

    isfile = False
    try:
        with open(bookings, "r"):
            isfile = True
    except FileNotFoundError:
        pass

    with open(bookings, mode="a", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=["name", "email", "date", "time", "timestamp", "booking_id"])
        if not isfile:
            writer.writeheader()
        writer.writerow(infos)
    return True

def bookingscheck(entry: str):
    info = extractinfo(entry)

    if slot_is_full(info["date"], info["time"]):
        return f"❌ Sorry! The slot on {info['date']} at {info['time']} is fully booked. Please choose another time."

    # Generate booking ID
    info["booking_id"] = str(uuid.uuid4())[:8]

    saved = savebooking(info)
    if saved:
        send_confirmation_email(info["name"], info["email"], info["date"], info["time"], info["booking_id"])
        return (
            f"✅ Booking confirmed for {info['name']} on {info['date']} at {info['time']}.\n"
            f"📧 Confirmation sent to {info['email']}.\n"
            f"🆔 Your booking ID is: {info['booking_id']}"
        )
    else:
        return f"❌ Booking failed. Please try a different slot."

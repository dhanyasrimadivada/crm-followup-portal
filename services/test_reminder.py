from services.reminder_service import send_payment_reminder

invoice_id = 1

try:
    send_payment_reminder(invoice_id)
    print("REMINDER TEST SUCCESSFUL")

except Exception as e:
    print("REMINDER TEST FAILED")
    print(e)
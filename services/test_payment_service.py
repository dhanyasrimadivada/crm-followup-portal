from services.payment_service import get_overdue_invoices


print()
print("=" * 60)
print("PAYMENT SERVICE TEST")
print("=" * 60)

overdue = get_overdue_invoices()

print()
print(f"Overdue invoices found: {len(overdue)}")

for invoice in overdue:
    print(
        f"Invoice: {invoice.invoice_number} | "
        f"Amount: ₹{invoice.total_amount} | "
        f"Due: {invoice.due_date} | "
        f"Status: {invoice.status}"
    )

print()
print("=" * 60)
print("PAYMENT TEST COMPLETED")
print("=" * 60)
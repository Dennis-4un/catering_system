import os
from app import create_app
from app.extensions import db
from app.models import (
    Role, User, Customer, Venue, Event, Menu, MenuItem, Package, PackageItem,
    EventMenuItem, Quotation, QuotationItem, Contract, Payment, Invoice,
    InventoryItem, StockTransaction, Supplier, Purchase, PurchaseItem,
    Recipe, RecipeIngredient, ProductionPlan, StaffAssignment, EventChecklist,
    Delivery, WastageRecord, Complaint, Review, Notification, AuditLog,
)

app = create_app(os.environ.get("FLASK_CONFIG", "development"))


@app.shell_context_processor
def make_shell_context():
    """Lets `flask shell` start with the db + every model already imported."""
    return {
        "db": db, "Role": Role, "User": User, "Customer": Customer, "Venue": Venue,
        "Event": Event, "Menu": Menu, "MenuItem": MenuItem, "Package": Package,
        "PackageItem": PackageItem, "EventMenuItem": EventMenuItem,
        "Quotation": Quotation, "QuotationItem": QuotationItem, "Contract": Contract,
        "Payment": Payment, "Invoice": Invoice, "InventoryItem": InventoryItem,
        "StockTransaction": StockTransaction, "Supplier": Supplier, "Purchase": Purchase,
        "PurchaseItem": PurchaseItem, "Recipe": Recipe, "RecipeIngredient": RecipeIngredient,
        "ProductionPlan": ProductionPlan, "StaffAssignment": StaffAssignment,
        "EventChecklist": EventChecklist, "Delivery": Delivery, "WastageRecord": WastageRecord,
        "Complaint": Complaint, "Review": Review, "Notification": Notification,
        "AuditLog": AuditLog,
    }


if __name__ == "__main__":
    app.run(debug=True)

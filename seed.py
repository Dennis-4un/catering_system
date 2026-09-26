"""
Owner: Sameer. Run once after `flask db upgrade` to create the seven system
roles (Section 4) and a first Administrator account.

Usage:
    python seed.py
"""
import os
from app import create_app
from app.extensions import db
from app.models import Role, User
from app.models.rbac import ALL_ROLES, ROLE_ADMIN

ROLE_PERMISSIONS = {
    "customer": "create_event,view_own_events,approve_quotation,make_payment,submit_feedback",
    "coordinator": "manage_inquiries,prepare_quotations,coordinate_customers",
    "kitchen_manager": "manage_menus,manage_recipes,manage_production_plans",
    "operations_manager": "assign_staff,manage_equipment,manage_event_day_tasks",
    "inventory_manager": "manage_stock,manage_suppliers,manage_purchases,record_wastage",
    "finance_officer": "verify_payments,manage_invoices,manage_expenses,manage_refunds",
    "admin": "manage_users,manage_roles,manage_all_records,view_audit_logs",
}

DEFAULT_ADMIN_EMAIL = os.environ.get("SEED_ADMIN_EMAIL", "admin@catering-system.com")
DEFAULT_ADMIN_PASSWORD = os.environ.get("SEED_ADMIN_PASSWORD", "ChangeMe123!")


def seed():
    created_roles = 0
    for role_name in ALL_ROLES:
        if not Role.query.filter_by(name=role_name).first():
            db.session.add(Role(name=role_name, permissions=ROLE_PERMISSIONS.get(role_name, "")))
            created_roles += 1
    db.session.commit()
    print(f"Roles ensured ({created_roles} created).")

    admin_role = Role.query.filter_by(name=ROLE_ADMIN).first()
    if not User.query.filter_by(email=DEFAULT_ADMIN_EMAIL).first():
        admin = User(name="System Administrator", email=DEFAULT_ADMIN_EMAIL, role=admin_role)
        admin.set_password(DEFAULT_ADMIN_PASSWORD)
        db.session.add(admin)
        db.session.commit()
        print(f"Admin account created: {DEFAULT_ADMIN_EMAIL} / {DEFAULT_ADMIN_PASSWORD}")
        print("Change this password immediately after first login.")
    else:
        print("Admin account already exists — skipped.")


def seed_demo_data():
    """Optional demo data (venues, a menu, a coordinator + kitchen manager
    account) so the Phase 1/2 flow can be exercised immediately without
    manually creating everything through the UI first."""
    from app.models import Venue, Menu, MenuItem

    if not Venue.query.first():
        db.session.add_all([
            Venue(name="Grand Ballroom", address="45 Garden Rd, City Center", capacity=400,
                  contact_info="021-111-2222", style="ballroom"),
            Venue(name="Riverside Marquee", address="12 River Lane", capacity=150,
                  contact_info="021-333-4444", style="garden"),
            Venue(name="Skyline Rooftop", address="Tower 9, Business District", capacity=120,
                  contact_info="021-555-6666", style="rooftop"),
            Venue(name="Heritage Banquet Hall", address="Old City Road", capacity=600,
                  contact_info="021-777-8888", style="hall"),
        ])
        print("Demo venues created.")

    if not Menu.query.first():
        menu = Menu(name="Classic Wedding Menu", category="mains",
                    description="Traditional favourites for large gatherings.")
        db.session.add(menu)
        db.session.flush()
        db.session.add_all([
            # Starters
            MenuItem(menu_id=menu.id, name="Chicken Seekh Kebab", dietary_tags="halal",
                     dish_category="starter", unit_cost=180,
                     description="Grilled minced chicken skewers with house spices."),
            MenuItem(menu_id=menu.id, name="Vegetable Spring Rolls", dietary_tags="vegetarian",
                     dish_category="starter", unit_cost=120,
                     description="Crispy rolls with a mixed vegetable filling."),
            MenuItem(menu_id=menu.id, name="Chicken Tikka", dietary_tags="halal",
                     dish_category="starter", unit_cost=200,
                     description="Char-grilled marinated chicken pieces."),
            # Mains
            MenuItem(menu_id=menu.id, name="Chicken Biryani", dietary_tags="halal",
                     dish_category="main", unit_cost=350,
                     description="Fragrant basmati rice layered with spiced chicken."),
            MenuItem(menu_id=menu.id, name="Vegetable Korma", dietary_tags="vegetarian,halal",
                     dish_category="main", unit_cost=280,
                     description="Mixed vegetables in a mild creamy curry."),
            MenuItem(menu_id=menu.id, name="Beef Karahi", dietary_tags="halal",
                     dish_category="main", unit_cost=400,
                     description="Slow-cooked beef in a tomato-based karahi sauce."),
            MenuItem(menu_id=menu.id, name="Chicken Handi", dietary_tags="halal",
                     dish_category="main", unit_cost=380,
                     description="Rich, creamy chicken curry cooked in a handi."),
            MenuItem(menu_id=menu.id, name="Dal Makhani", dietary_tags="vegetarian,halal",
                     dish_category="main", unit_cost=220,
                     description="Slow-simmered black lentils finished with cream."),
            # Bread / Rice
            MenuItem(menu_id=menu.id, name="Butter Naan", dietary_tags="vegetarian",
                     dish_category="bread", unit_cost=40,
                     description="Soft leavened bread brushed with butter."),
            MenuItem(menu_id=menu.id, name="Steamed Basmati Rice", dietary_tags="vegetarian,vegan,halal",
                     dish_category="bread", unit_cost=60,
                     description="Fluffy long-grain basmati rice."),
            # Desserts
            MenuItem(menu_id=menu.id, name="Kheer", description="Rice pudding dessert",
                     dietary_tags="vegetarian,nut-free", dish_category="dessert", unit_cost=120),
            MenuItem(menu_id=menu.id, name="Gulab Jamun", dietary_tags="vegetarian",
                     dish_category="dessert", unit_cost=100,
                     description="Soft milk-solid dumplings in rose-scented syrup."),
            MenuItem(menu_id=menu.id, name="Fruit Trifle", dietary_tags="vegetarian",
                     dish_category="dessert", unit_cost=140,
                     description="Layered sponge, custard and seasonal fruit."),
            # Beverages
            MenuItem(menu_id=menu.id, name="Kashmiri Chai", dietary_tags="vegetarian,halal",
                     dish_category="beverage", unit_cost=60,
                     description="Pink tea served with a dedicated tea station."),
            MenuItem(menu_id=menu.id, name="Fresh Lime Soda", dietary_tags="vegetarian,vegan,halal",
                     dish_category="beverage", unit_cost=50,
                     description="Chilled soda with fresh lime and mint."),
            MenuItem(menu_id=menu.id, name="Mango Lassi", dietary_tags="vegetarian,halal",
                     dish_category="beverage", unit_cost=80,
                     description="Creamy yoghurt-based mango drink."),
        ])
        db.session.flush()
        print("Demo menu + dishes created.")

    from app.models.menu import Package, PackageItem
    if not Package.query.first():
        biryani = MenuItem.query.filter_by(name="Chicken Biryani").first()
        naan = MenuItem.query.filter_by(name="Butter Naan").first()
        gulab = MenuItem.query.filter_by(name="Gulab Jamun").first()
        chai = MenuItem.query.filter_by(name="Kashmiri Chai").first()
        karahi = MenuItem.query.filter_by(name="Beef Karahi").first()
        kebab = MenuItem.query.filter_by(name="Chicken Seekh Kebab").first()

        silver = Package(name="Silver Package", price_per_guest=650,
                          description="Essential wedding package — mains, bread and a dessert.",
                          waiters_included=False, waiter_addon_cost_per_guest=80)
        gold = Package(name="Gold Package", price_per_guest=1100,
                       description="Full-service package with starters, mains and tea station.",
                       waiters_included=True, waiter_addon_cost_per_guest=0)
        db.session.add_all([silver, gold])
        db.session.flush()

        if biryani and naan and gulab:
            db.session.add_all([
                PackageItem(package_id=silver.id, menu_item_id=biryani.id),
                PackageItem(package_id=silver.id, menu_item_id=naan.id),
                PackageItem(package_id=silver.id, menu_item_id=gulab.id),
            ])
        if biryani and karahi and kebab and naan and chai:
            db.session.add_all([
                PackageItem(package_id=gold.id, menu_item_id=kebab.id),
                PackageItem(package_id=gold.id, menu_item_id=biryani.id),
                PackageItem(package_id=gold.id, menu_item_id=karahi.id),
                PackageItem(package_id=gold.id, menu_item_id=naan.id),
                PackageItem(package_id=gold.id, menu_item_id=chai.id),
            ])
        db.session.flush()
        print("Demo packages created (Silver — waiters as add-on, Gold — waiters included).")

        from app.models import InventoryItem, Recipe, RecipeIngredient
        if not InventoryItem.query.first():
            rice = InventoryItem(name="Basmati Rice", unit="kg", current_stock=500, reorder_level=50)
            chicken = InventoryItem(name="Chicken", unit="kg", current_stock=300, reorder_level=30)
            veg = InventoryItem(name="Mixed Vegetables", unit="kg", current_stock=200, reorder_level=20)
            milk = InventoryItem(name="Milk", unit="litre", current_stock=150, reorder_level=15)
            db.session.add_all([rice, chicken, veg, milk])
            db.session.flush()
            print("Demo inventory items created.")

            biryani = MenuItem.query.filter_by(name="Chicken Biryani").first()
            korma = MenuItem.query.filter_by(name="Vegetable Korma").first()
            kheer = MenuItem.query.filter_by(name="Kheer").first()

            r1 = Recipe(menu_item_id=biryani.id, yield_qty=10)
            r2 = Recipe(menu_item_id=korma.id, yield_qty=10)
            r3 = Recipe(menu_item_id=kheer.id, yield_qty=10)
            db.session.add_all([r1, r2, r3])
            db.session.flush()
            db.session.add_all([
                RecipeIngredient(recipe_id=r1.id, inventory_item_id=rice.id, quantity_required=2),
                RecipeIngredient(recipe_id=r1.id, inventory_item_id=chicken.id, quantity_required=3),
                RecipeIngredient(recipe_id=r2.id, inventory_item_id=veg.id, quantity_required=2.5),
                RecipeIngredient(recipe_id=r3.id, inventory_item_id=milk.id, quantity_required=2),
            ])
            print("Demo recipes + ingredients created.")

    coordinator_email = "coordinator@catering-system.com"
    if not User.query.filter_by(email=coordinator_email).first():
        coord_role = Role.query.filter_by(name="coordinator").first()
        coordinator = User(name="Demo Coordinator", email=coordinator_email, role=coord_role)
        coordinator.set_password("Coordinator123!")
        db.session.add(coordinator)
        print(f"Demo coordinator created: {coordinator_email} / Coordinator123!")

    km_email = "kitchen@catering-system.com"
    if not User.query.filter_by(email=km_email).first():
        km_role = Role.query.filter_by(name="kitchen_manager").first()
        km = User(name="Demo Kitchen Manager", email=km_email, role=km_role)
        km.set_password("Kitchen123!")
        db.session.add(km)
        print(f"Demo kitchen manager created: {km_email} / Kitchen123!")

    finance_email = "finance@catering-system.com"
    if not User.query.filter_by(email=finance_email).first():
        finance_role = Role.query.filter_by(name="finance_officer").first()
        finance = User(name="Demo Finance Officer", email=finance_email, role=finance_role)
        finance.set_password("Finance123!")
        db.session.add(finance)
        print(f"Demo finance officer created: {finance_email} / Finance123!")

    inventory_email = "inventory@catering-system.com"
    if not User.query.filter_by(email=inventory_email).first():
        inventory_role = Role.query.filter_by(name="inventory_manager").first()
        inv_mgr = User(name="Demo Inventory Manager", email=inventory_email, role=inventory_role)
        inv_mgr.set_password("Inventory123!")
        db.session.add(inv_mgr)
        print(f"Demo inventory manager created: {inventory_email} / Inventory123!")

    ops_email = "operations@catering-system.com"
    if not User.query.filter_by(email=ops_email).first():
        ops_role = Role.query.filter_by(name="operations_manager").first()
        ops_mgr = User(name="Demo Operations Manager", email=ops_email, role=ops_role)
        ops_mgr.set_password("Operations123!")
        db.session.add(ops_mgr)
        print(f"Demo operations manager created: {ops_email} / Operations123!")

    db.session.commit()


if __name__ == "__main__":
    app = create_app(os.environ.get("FLASK_CONFIG", "development"))
    with app.app_context():
        seed()
        seed_demo_data()

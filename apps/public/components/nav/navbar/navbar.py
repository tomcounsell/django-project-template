from django_components import component

from apps.item.models import Brand, Category


@component.register("navbar")
class Navbar(component.Component):
    template_name = "nav/navbar/navbar.html"

    def get_context_data(self, active_brand_id=None, active_category_id=None):
        brand = (
            Brand.objects.filter(id=active_brand_id).first()
            if active_brand_id
            else None
        )
        category = (
            Category.objects.filter(id=active_category_id).first()
            if active_category_id
            else None
        )
        return {"brand": brand, "category": category}

    class Media:
        # css = "nav/navbar/navbar.css"
        js = "nav/navbar/navbar.js"

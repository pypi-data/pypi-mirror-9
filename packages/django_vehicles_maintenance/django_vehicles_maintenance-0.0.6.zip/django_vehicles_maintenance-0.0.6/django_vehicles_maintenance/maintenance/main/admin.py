from django.contrib import admin
from maintenance.main.models import chassis, storage_tank, carburetion_tank, radio, vehicle, garage, chassis_maintenance, storage_tank_maintenance, carburetion_tank_maintenance, service, services_group, services_group_items, chassis_maintenance_S, chassis_maintenance_SG, storage_tank_maintenance_S, storage_tank_maintenance_SG, carburetion_tank_S, carburetion_tank_SG

# class chassis_maintenanceInline(admin.TabularInline):
#     model = chassis_maintenance
#     extra = 1

# class Chassisdmin(admin.ModelAdmin):
#     inlines = [chassis_maintenanceInline]

# admin.site.register(chassis, Chassisdmin)
# admin.site.register(storage_tank)
# admin.site.register(carburetion_tank)
# admin.site.register(radio)
# admin.site.register(vehicle)
# admin.site.register(garage)
# admin.site.register(chassis_maintenance)
# admin.site.register(storage_tank_maintenance)
# admin.site.register(carburetion_tank_maintenance)
# admin.site.register(service)
# admin.site.register(services_group)
# admin.site.register(services_group_items)
# admin.site.register(chassis_maintenance_S)
# admin.site.register(chassis_maintenance_SG)
# admin.site.register(storage_tank_maintenance_S)
# admin.site.register(storage_tank_maintenance_SG)
# admin.site.register(carburetion_tank_S)
# admin.site.register(carburetion_tank_SG)
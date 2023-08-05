from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from maintenance.main.models import *
from maintenance.main.forms import *

from django.core.context_processors import csrf
from django.template import RequestContext # For CSRF
from django.forms.formsets import formset_factory, BaseFormSet
from django.forms.models import inlineformset_factory

# user autentication
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, permission_required

# Create your views here.
@login_required(login_url='/login/')
def index(request):
  	vehicles = vehicle.objects.all().order_by('name')
  	return render_to_response('index.html',{'vehicles':vehicles},context_instance=RequestContext(request))

@login_required(login_url='/login/')
def new_vehicleView(request):
	if request.method == 'POST':
		vehicleForm = new_vehicleForm(request.POST, request.FILES)
		if vehicleForm.is_valid():
			vehicleForm.save()
			vehicles = vehicle.objects.all().order_by('name')
			return render_to_response('index.html',context_instance = RequestContext(request))
	else:
	 	vehicleForm = new_vehicleForm()

	return render_to_response('new_vehicle.html', {'vehicleForm': vehicleForm,}
			,context_instance = RequestContext(request))

@permission_required('chassis_maintenance_S.can_delete_chassis_maintenance_S', login_url="/login/")
def delete_chassis_maintenanceS(request, id = None):
	chassis_maintenanceS = get_object_or_404(chassis_maintenance_S, pk=id)
	chassis_maintenanceS.delete()
	
	f  = chassis_maintenance_Form(instance=chassis_maintenanceS.chassis_maintenance)
	fs = chassisServiceFormSet(prefix='chassisServiceFormS', instance=chassis_maintenanceS.chassis_maintenance)
	fsg = chassisServiceGroupFormSet(prefix='chassisServiceFormSG', instance=chassis_maintenanceS.chassis_maintenance)
	return render_to_response('chassis_maintenance_manageFormSet.html', {'fs': fs, 'fsg':fsg, 'f':f,'chassisMaintenance':chassisMaintenance,}, context_instance = RequestContext(request))

@login_required(login_url='/login/')
def service_group_inlineView(request , id = None, template_name='service_group_inline.html'):
	
	if id:
		ServicesGroup = get_object_or_404(services_group, pk=id)
	else:
		ServicesGroup = services_group()

	ServiceGroupInlineFS = inlineformset_factory(services_group, services_group_items, extra=1)

	if request.method == "POST":
		SGFormset = ServiceGroupInlineFS(request.POST, request.FILES, instance=ServicesGroup)
		
		if SGFormset.is_valid():
			SGFormset.save()
    	 	return render_to_response(template_name, {"SGFormset": SGFormset,},context_instance = RequestContext(request))
	else:
		SGFormset = ServiceGroupInlineFS(instance=ServicesGroup)
	
	return render_to_response(template_name, {"SGFormset": SGFormset,},context_instance = RequestContext(request))

##########################################
## 										##
##           FORMSET BIEN 100%          ##
##										##
##########################################
@login_required(login_url='/login/')
def servicesView(request, template="services.html"):
	services = service.objects.all().order_by('-service_type')
	servicesGroups = services_group.objects.all()
	c = {'services':services,'servicesGroups':servicesGroups,}
	return render_to_response(template, c, context_instance=RequestContext(request))

@login_required(login_url='/login/')	
def services_groupInline_formset(request, id = None, template= "services_groupInline.html"):
	Services_groupItemsformSet = get_services_group_items_formset(services_group_itemsForm, extra=1, can_delete=True)
	if id:
		servicesgroup = get_object_or_404(services_group, pk=id)
	else:
		servicesgroup = services_group()
	
	if request.method == 'POST':
		form = services_groupForm(request.POST, instance=servicesgroup)
		formset = Services_groupItemsformSet(request.POST, instance=servicesgroup)
		if form.is_valid() and formset.is_valid():
			form.save()
			formset.save()
			services = service.objects.all().order_by('-service_type')
			servicesGroups = services_group.objects.all()
			c = {'services':services,'servicesGroups':servicesGroups,}
			return render_to_response('services.html', c, context_instance = RequestContext(request))
	else:
		form = services_groupForm(instance= servicesgroup)
		formset = Services_groupItemsformSet(instance = servicesgroup)
	return render_to_response(template, {'form': form, 'formset': formset},
        context_instance=RequestContext(request))

@permission_required('services_group.can_delete_services_group', login_url="/login/")
def delete_services_group(request, id = None):
	ServicesGroup = get_object_or_404(services_group, pk=id)
	ServicesGroup.delete()
	services = service.objects.all().order_by('-service_type')
	servicesGroups = services_group.objects.all()
	c = {'services':services,'servicesGroups':servicesGroups,}
	return render_to_response('services.html', c, context_instance = RequestContext(request))

@login_required(login_url='/login/')
def service_manageView(request, id = None, template_name='service.html'):
	if id:
		Service = get_object_or_404(service, pk=id)
	else:
		Service = service()

	if request.method == 'POST':
		Form = serviceForm(request.POST, instance=Service)
		if Form.is_valid():
			Form.save()
			services = service.objects.all().order_by('-service_type')
			servicesGroups = services_group.objects.all()
			c = {'services':services,'servicesGroups':servicesGroups,}
			return render_to_response('services.html', c, context_instance = RequestContext(request))
	else:
	 	Form = serviceForm(instance=Service)

	return render_to_response(template_name, {'Form': Form,}
			,context_instance = RequestContext(request))

@permission_required('service.can_delete_radio_maintenance', login_url="/login/")
def delete_service(request, id = None):
	Service = get_object_or_404(service, pk=id)
	Service.delete()
	services = service.objects.all().order_by('-service_type')
	servicesGroups = services_group.objects.all()
	c = {'services':services,'servicesGroups':servicesGroups,}
	return render_to_response('services.html', c, context_instance = RequestContext(request))

##########################################
## 										##
##               CHASSIS 			    ##
##										##
##########################################
@login_required(login_url='/login/')
def chassisesView(request, template="vehicle/chassis/chassises.html"):
	Chassises = chassis.objects.all()
	c = {'Chassises':Chassises}
	return render_to_response(template, c, context_instance=RequestContext(request))

@login_required(login_url='/login/')
def chassis_manageView(request, id= None, template_name = 'vehicle/chassis/chassis_manage.html'):
	if id:
	  	chassisI = get_object_or_404(chassis, pk=id)
	else:
		chassisI = chassis()

	if request.method == 'POST':
		chassisForm = chassis_manageForm(request.POST, instance= chassisI)
		if chassisForm.is_valid():
			chassisForm.save()
			Chassises = chassis.objects.all()
			c = {'Chassises':Chassises}
			return render_to_response('vehicle/chassis/chassises.html', c, context_instance=RequestContext(request))
	else:
	 	chassisForm = chassis_manageForm(instance= chassisI)

	return render_to_response(template_name, {'chassisForm': chassisForm,}
			,context_instance = RequestContext(request))

@login_required(login_url='/login/')
def chassis_maintenanceView(request, query):
 	chassisD = get_object_or_404(chassis, pk=query)
 	chassis_maintenances = chassis_maintenance.objects.filter(chassis = chassisD).order_by('-date')
	chassis_services = chassis_maintenance_Service.objects.filter(chassis_maintenance__chassis = chassisD)
	chassis_services_groups = chassis_maintenance_SG.objects.filter(chassis_maintenance__chassis = chassisD)
	ServicesGroups = services_group.objects.all()
	ServicesGroupItems = services_group_items.objects.all()
	context = {'chassis': chassisD, 'chassis_services': chassis_services, 'chassis_services_groups':chassis_services_groups, 'chassis_maintenances': chassis_maintenances,'ServicesGroups':ServicesGroups,'ServicesGroupItems':ServicesGroupItems}
	return render_to_response('vehicle/chassis/chassis_maintenance.html', context,context_instance=RequestContext(request))

@login_required(login_url='/login/')
def chassis_maintenace_Inline_formset(request, id = None, chassis_id = None, template= "vehicle/chassis/chassis_maintenance_Inline.html"):
	Chassis = get_object_or_404( chassis, pk =  chassis_id)
	ChassisMaintenace_SItems_formset = get_chassis_maintenace_Serviceitems_formset(chassis_maintenance_serviceForm, extra=1, can_delete=True)
	ChassisMaintenace_SGItems_formset = get_chassis_maintenace_SGitems_formset(chassis_maintenance_sgForm, extra=1, can_delete=True)
	message = ""
	if id:
		chassismaintenance = get_object_or_404(chassis_maintenance, pk=id)
	else:
		chassismaintenance = chassis_maintenance()
	
	if request.method == 'POST':
		form = chassis_maintenanceForm(request.POST, instance=chassismaintenance)
		formset = ChassisMaintenace_SItems_formset(request.POST, instance=chassismaintenance)
		formsetSG = ChassisMaintenace_SGItems_formset(request.POST, instance=chassismaintenance)
		if form.is_valid() and formset.is_valid() and formsetSG.is_valid():
			
			ch = form.save(commit = False)
			ch.chassis = Chassis
			ch.save()

			formset.save()
			formsetSG.save()
			message = "Datos Guardados"
			return render_to_response(template, {'Chassis':Chassis,'form': form, 'formset': formset,'formsetSG': formsetSG,'message':message}, context_instance=RequestContext(request))
	else:
		form = chassis_maintenanceForm(instance= chassismaintenance)
		formset = ChassisMaintenace_SItems_formset(instance = chassismaintenance)
		formsetSG = ChassisMaintenace_SGItems_formset(instance = chassismaintenance)
	return render_to_response(template, {'Chassis':Chassis,'form': form, 'formset': formset,'formsetSG': formsetSG, 'message':message}, context_instance=RequestContext(request))

@permission_required('chassis.can_delete_chassis_maintenance', login_url="/login/")
def delete_chassis_maintenance(request, id = None, chassis_id = None):
	chassisD = get_object_or_404(chassis, pk= chassis_id)
	chassis_maintenanceInstance = get_object_or_404(chassis_maintenance, pk=id)
	chassis_maintenanceInstance.delete()
	
	chassis_maintenances = chassis_maintenance.objects.filter(chassis = chassisD)
	chassis_services = chassis_maintenance_Service.objects.filter(chassis_maintenance__chassis = chassisD)
	chassis_services_groups = chassis_maintenance_SG.objects.filter(chassis_maintenance__chassis = chassisD)
	ServicesGroups = services_group.objects.all()
	ServicesGroupItems = services_group_items.objects.all()
	context = {'chassis': chassisD, 'chassis_services': chassis_services, 'chassis_services_groups':chassis_services_groups, 'chassis_maintenances': chassis_maintenances,'ServicesGroups':ServicesGroups,'ServicesGroupItems':ServicesGroupItems}
	return render_to_response('vehicle/chassis/chassis_maintenance.html', context,context_instance=RequestContext(request))

@permission_required('chassis.can_delete_chassis', login_url="/login/")
def delete_chassis(request, id = None, template="vehicle/chassis/chassises.html"):
	chassisI = get_object_or_404(chassis, pk= id)
	chassisI.delete()
	Chassises = chassis.objects.all()
	c = {'Chassises':Chassises}
	return render_to_response(template, c, context_instance=RequestContext(request))
	

def chassis_maintenanceReportView(request, query):
 	chassisD = get_object_or_404(chassis, pk=query)
 	chassis_maintenances = chassis_maintenance.objects.filter(chassis = chassisD).order_by('date')
	chassis_services = chassis_maintenance_Service.objects.filter(chassis_maintenance__chassis = chassisD)
	chassis_services_groups = chassis_maintenance_SG.objects.filter(chassis_maintenance__chassis = chassisD)
	ServicesGroups = services_group.objects.all()
	ServicesGroupItems = services_group_items.objects.all()
	context = {'chassis': chassisD, 'chassis_services': chassis_services, 'chassis_services_groups':chassis_services_groups, 'chassis_maintenances': chassis_maintenances,'ServicesGroups':ServicesGroups,'ServicesGroupItems':ServicesGroupItems}
	return render_to_response('vehicle/chassis/chassis_maintenanceReport.html', context,context_instance=RequestContext(request))

##########################################
## 										##
##      CARBURATION TANK MAINTENACE     ##
##										##
##########################################
@login_required(login_url='/login/')
def carburetion_tanksView(request, template="vehicle/carburetion_tank/carburetion_tanks.html"):
	CarburetionTanks = carburetion_tank.objects.all()
	c = {'carburetion_tanks':CarburetionTanks}
	return render_to_response(template, c, context_instance=RequestContext(request))

@login_required(login_url='/login/')
def carburetion_tank_maintenanceView(request, query):
 	carburetion_tankD = get_object_or_404(carburetion_tank, pk=query)
 	carburetion_tank_maintenances = carburetion_tank_maintenance.objects.filter(carburetion_tank = carburetion_tankD).order_by('-date')
	carburetion_tank_services = carburetion_tank_S.objects.filter(carburetion_tank_maintenance__carburetion_tank = carburetion_tankD)
	carburetion_tank_services_groups = carburetion_tank_SG.objects.filter(carburetion_tank_maintenance__carburetion_tank = carburetion_tankD)
	context = {'carburetion_tank': carburetion_tankD, 'carburetion_tank_services': carburetion_tank_services, 'carburetion_tank_services_groups':carburetion_tank_services_groups, 'carburetion_tank_maintenances': carburetion_tank_maintenances}
	return render_to_response('vehicle/carburetion_tank/carburetion_tank_maintenance.html', context,context_instance=RequestContext(request))

@login_required(login_url='/login/')
def carburetion_tank_manageView(request, id = None, template_name='vehicle/carburetion_tank/carburetion_tank_manage.html'):
	if id:
		carburetion_tankI = get_object_or_404(carburetion_tank, pk=id)
	else:
		carburetion_tankI = carburetion_tank()

	if request.method == 'POST':
		carburetion_tankForm = carburetion_tank_manageForm(request.POST, instance= carburetion_tankI)
		if carburetion_tankForm.is_valid():
			carburetion_tankForm.save()
			CarburetionTanks = carburetion_tank.objects.all()
			c = {'carburetion_tanks':CarburetionTanks}
			return render_to_response('vehicle/carburetion_tank/carburetion_tanks.html', c, context_instance=RequestContext(request))
	else:
	 	carburetion_tankForm = carburetion_tank_manageForm(instance= carburetion_tankI)

	return render_to_response(template_name, {'carburetion_tankForm': carburetion_tankForm,}
			,context_instance = RequestContext(request))

@login_required(login_url='/login/')
def carburetion_tank_maintenance_Inline_formset(request, id = None, carburetion_tank_id= None , template= "vehicle/carburetion_tank/carburetion_tank_maintenance_Inline.html"):
	CarburetionTank = get_object_or_404(carburetion_tank, pk = carburetion_tank_id)
	CarburetionTank_SItems_formset = get_carburetion_tank_maintenace_Sitems_formset(carburetion_tank_maintenance_sForm, extra=1, can_delete=True)
	#CarburetionTank_SGItems_formset = get_carburetion_tank_maintenace_SGitems_formset(carburetion_tank_maintenance_sgForm, extra=1, can_delete=True)
	message = ""
	if id:
		carburetiontankmaintenance = get_object_or_404(carburetion_tank_maintenance, pk=id)
	else:
		carburetiontankmaintenance = carburetion_tank_maintenance()
	
	if request.method == 'POST':
		form = carburetion_tank_maintenanceForm(request.POST, instance=carburetiontankmaintenance)
		formset = CarburetionTank_SItems_formset(request.POST, instance=carburetiontankmaintenance)
		#formsetSG = CarburetionTank_SGItems_formset(request.POST, instance=carburetiontankmaintenance)
		#if form.is_valid() and formset.is_valid() and formsetSG.is_valid():
		if form.is_valid() and formset.is_valid():
			
			ct = form.save(commit = False)
			ct.carburetion_tank = CarburetionTank
			ct.save()

			formset.save()
			#formsetSG.save()
			message = "Datos Guardados"
			return render_to_response(template, {'CarburetionTank':CarburetionTank,'form': form, 'formset': formset,'message':message}, context_instance=RequestContext(request))
	else:
		form = carburetion_tank_maintenanceForm(instance=carburetiontankmaintenance)
		formset = CarburetionTank_SItems_formset(instance=carburetiontankmaintenance)
		#formsetSG = CarburetionTank_SGItems_formset(instance=carburetiontankmaintenance)
	return render_to_response(template, {'CarburetionTank':CarburetionTank,'form': form, 'formset': formset, 'message':message}, context_instance=RequestContext(request))

@permission_required('carburetion_tank.can_delete_carburetion_tank_maintenance', login_url="/login/")
def delete_carburetion_tank_maintenance(request, id = None, carburetion_tank_id = None):
	carburetion_tank_maintenanceInstance = get_object_or_404(carburetion_tank_maintenance, pk=id)
	carburetion_tank_maintenanceInstance.delete()

	carburetion_tankD = get_object_or_404(carburetion_tank, pk=carburetion_tank_id)
 	carburetion_tank_maintenances = carburetion_tank_maintenance.objects.filter(carburetion_tank = carburetion_tankD)
	carburetion_tank_services = carburetion_tank_S.objects.filter(carburetion_tank_maintenance__carburetion_tank = carburetion_tankD)
	carburetion_tank_services_groups = carburetion_tank_SG.objects.filter(carburetion_tank_maintenance__carburetion_tank = carburetion_tankD)
	context = {'carburetion_tank': carburetion_tankD, 'carburetion_tank_services': carburetion_tank_services, 'carburetion_tank_services_groups':carburetion_tank_services_groups, 'carburetion_tank_maintenances': carburetion_tank_maintenances}
	return render_to_response('vehicle/carburetion_tank/carburetion_tank_maintenance.html', context,context_instance=RequestContext(request))

@permission_required('carburetion_tank.can_delete_carburetion_tank', login_url="/login/")
def delete_carburetion_tank(request, id = None, template="vehicle/carburetion_tank/carburetion_tanks.html"):
	carburetion_tankI = get_object_or_404(carburetion_tank, pk=id)
	carburetion_tankI.delete()
	CarburetionTanks = carburetion_tank.objects.all()
	c = {'carburetion_tanks':CarburetionTanks}
	return render_to_response(template, c, context_instance=RequestContext(request))

@login_required(login_url='/login/')
def carburetion_tank_maintenanceReportView(request, query):
 	carburetion_tankD = get_object_or_404(carburetion_tank, pk=query)
 	carburetion_tank_maintenances = carburetion_tank_maintenance.objects.filter(carburetion_tank = carburetion_tankD).order_by('date')
	carburetion_tank_services = carburetion_tank_S.objects.filter(carburetion_tank_maintenance__carburetion_tank = carburetion_tankD)
	carburetion_tank_services_groups = carburetion_tank_SG.objects.filter(carburetion_tank_maintenance__carburetion_tank = carburetion_tankD)
	context = {'carburetion_tank': carburetion_tankD, 'carburetion_tank_services': carburetion_tank_services, 'carburetion_tank_services_groups':carburetion_tank_services_groups, 'carburetion_tank_maintenances': carburetion_tank_maintenances}
	return render_to_response('vehicle/carburetion_tank/carburetion_tank_maintenanceReport.html', context,context_instance=RequestContext(request))
##########################################
## 										##
##      STORAGE TANK MAINTENACE         ##
##										##
##########################################
@login_required(login_url='/login/')
def storage_tanksView(request, template="vehicle/storage_tank/storage_tanks.html"):
	StorageTanks = storage_tank.objects.all()
	c = {'StorageTanks':StorageTanks}
	return render_to_response(template, c, context_instance=RequestContext(request))

@login_required(login_url='/login/')
def storage_tank_maintenance_Inline_formset(request, id = None, storage_tank_id = None, template= "vehicle/storage_tank/storage_tank_maintenance_Inline.html"):
	StorageTank = get_object_or_404(storage_tank, pk = storage_tank_id)
	StorageTank_SItems_formset = get_storage_tank_maintenace_Sitems_formset(storage_tank_maintenance_sForm, extra=1, can_delete=True)
	#StorageTank_SGItems_formset = get_storage_tank_maintenace_SGitems_formset(storage_tank_maintenance_sgForm, extra=1, can_delete=True)
	message = ""
	if id:
		storagetankmaintenance = get_object_or_404(storage_tank_maintenance, pk=id)
	else:
		storagetankmaintenance = storage_tank_maintenance()
	
	if request.method == 'POST':
		form = storage_tank_maintenanceForm(request.POST, instance=storagetankmaintenance)
		formset = StorageTank_SItems_formset(request.POST, instance=storagetankmaintenance)
		#formsetSG = StorageTank_SGItems_formset(request.POST, instance=storagetankmaintenance)
		#if form.is_valid() and formset.is_valid() and formsetSG.is_valid():
		if form.is_valid() and formset.is_valid():
			st = form.save(commit = False)
			st.storage_tank = StorageTank
			st.save()
			formset.save()
			#formsetSG.save()
			message = "Datos Guardados"
			return render_to_response(template, {'StorageTank':StorageTank,'form': form, 'formset': formset,'message':message}, context_instance=RequestContext(request))
	else:
		form = storage_tank_maintenanceForm(instance=storagetankmaintenance)
		formset = StorageTank_SItems_formset(instance=storagetankmaintenance)
		#formsetSG = StorageTank_SGItems_formset(instance=storagetankmaintenance)
	return render_to_response(template, {'StorageTank':StorageTank,'form': form, 'formset': formset, 'message':message}, context_instance=RequestContext(request))

@login_required(login_url='/login/')
def storage_tank_maintenanceView(request, query):
 	storage_tankD = get_object_or_404(storage_tank, pk=query)
 	storage_tank_maintenances = storage_tank_maintenance.objects.filter(storage_tank = storage_tankD).order_by('-date')
	storage_tank_services = storage_tank_maintenance_S.objects.filter(storage_tank_maintenance__storage_tank = storage_tankD)
	storage_tank_services_groups = storage_tank_maintenance_SG.objects.filter(storage_tank_maintenance__storage_tank = storage_tankD)
	context = {'storage_tank': storage_tankD, 'storage_tank_services': storage_tank_services, 'storage_tank_services_groups':storage_tank_services_groups, 'storage_tank_maintenances': storage_tank_maintenances}
	return render_to_response('vehicle/storage_tank/storage_tank_maintenance.html', context,context_instance=RequestContext(request))

@login_required(login_url='/login/')
def storage_tank_manageView(request, id = None, template_name='vehicle/storage_tank/storage_tank_manage.html'):
	if id:
	  	storage_tankI = get_object_or_404(storage_tank, pk=id)
	else:
		storage_tankI = storage_tank()

	if request.method == 'POST':
		storage_tankForm = storage_tank_manageForm(request.POST, instance= storage_tankI)
		if storage_tankForm.is_valid():
			storage_tankForm.save()
			StorageTanks = storage_tank.objects.all()
			c = {'StorageTanks':StorageTanks}
			return render_to_response('vehicle/storage_tank/storage_tanks.html', c, context_instance=RequestContext(request))
	else:
	 	storage_tankForm = storage_tank_manageForm(instance= storage_tankI)

	return render_to_response(template_name, {'storage_tankForm': storage_tankForm,}
			,context_instance = RequestContext(request))

@permission_required('storage_maintenanc.can_delete_storage_maintenance', login_url="/login/")
def delete_storage_maintenance(request, id = None, storage_tank_id = None ):
	storage_maintenanceInstance = get_object_or_404(storage_tank_maintenance, pk=id)
	storage_maintenanceInstance.delete()
	storage_tankD = get_object_or_404(storage_tank, pk=storage_tank_id)
 	storage_tank_maintenances = storage_tank_maintenance.objects.filter(storage_tank = storage_tankD)
	storage_tank_services = storage_tank_maintenance_S.objects.filter(storage_tank_maintenance__storage_tank = storage_tankD)
	storage_tank_services_groups = storage_tank_maintenance_SG.objects.filter(storage_tank_maintenance__storage_tank = storage_tankD)
	context = {'storage_tank': storage_tankD, 'storage_tank_services': storage_tank_services, 'storage_tank_services_groups':storage_tank_services_groups, 'storage_tank_maintenances': storage_tank_maintenances}
	return render_to_response('vehicle/storage_tank/storage_tank_maintenance.html', context,context_instance=RequestContext(request))


@permission_required('storagetank.can_delete_storage_tank', login_url="/login/")
def delete_storage_tank(request, id = None, template="vehicle/storage_tank/storage_tanks.html"):
	storagetankInstance = get_object_or_404(storage_tank, pk=id)
	storagetankInstance.delete()

	StorageTanks = storage_tank.objects.all()
	c = {'StorageTanks':StorageTanks}
	return render_to_response(template, c, context_instance=RequestContext(request))

@login_required(login_url='/login/')
def storage_tank_maintenanceReportView(request, query):
 	storage_tankD = get_object_or_404(storage_tank, pk=query)
 	storage_tank_maintenances = storage_tank_maintenance.objects.filter(storage_tank = storage_tankD).order_by('date')
	storage_tank_services = storage_tank_maintenance_S.objects.filter(storage_tank_maintenance__storage_tank = storage_tankD)
	storage_tank_services_groups = storage_tank_maintenance_SG.objects.filter(storage_tank_maintenance__storage_tank = storage_tankD)
	context = {'storage_tank': storage_tankD, 'storage_tank_services': storage_tank_services, 'storage_tank_services_groups':storage_tank_services_groups, 'storage_tank_maintenances': storage_tank_maintenances}
	return render_to_response('vehicle/storage_tank/storage_tank_maintenanceReport.html', context,context_instance=RequestContext(request))


##########################################
## 										##
##               LOGIN     			    ##
##										##
##########################################
def ingresar(request):
    if not request.user.is_anonymous():
        return HttpResponseRedirect('/')
    if request.method == 'POST':
        formulario = AuthenticationForm(request.POST)
        if formulario.is_valid:
            usuario = request.POST['username']
            clave = request.POST['password']
            acceso = authenticate(username=usuario, password=clave)
            if acceso is not None:
                if acceso.is_active:
                    login(request, acceso)
                    return HttpResponseRedirect('/')
                else:
                    return render_to_response('noactivo.html', context_instance=RequestContext(request))
            else:
                return render_to_response('login.html',{'form':formulario, 'message':'Nombre de usaurio o password no validos',}, context_instance=RequestContext(request))
    else:
        formulario = AuthenticationForm()
    return render_to_response('login.html',{'form':formulario, 'message':'',}, context_instance=RequestContext(request))

def logoutUser(request):
    logout(request)
    return HttpResponseRedirect('/')

##########################################
## 										##
##               GARAGE    			    ##
##										##
##########################################

@login_required(login_url='/login/')
def garagesView(request, template="vehicle/garage/garages.html"):
	Garages = garage.objects.all()
	c = {'Garages':Garages}
	return render_to_response(template, c, context_instance=RequestContext(request))

@login_required(login_url='/login/')
def garage_manageView(request, id = None, template_name='vehicle/garage/garage_manage.html'):
	if id:
		Garage = get_object_or_404(garage, pk=id)
	else:
		Garage = garage()

	if request.method == 'POST':
		Form = garage_manageForm(request.POST, instance = Garage)
		if Form.is_valid():
			Form.save()
			Garages = garage.objects.all()
			c = {'Garages':Garages}
			return render_to_response('vehicle/garage/garages.html', c, context_instance=RequestContext(request))
	else:
	 	Form = serviceForm(instance=Garage)

	return render_to_response(template_name, {'Form': Form,}
			,context_instance = RequestContext(request))

@permission_required('garage.can_delete_garage', login_url="/login/")
def delete_garageView(request, id = None, template="vehicle/garage/garages.html"):
	garageInstance = get_object_or_404(garage, pk=id)
	garageInstance.delete()

	Garages = garage.objects.all()
	c = {'Garages':Garages}
	return render_to_response(template, c, context_instance=RequestContext(request))
##########################################
## 										##
##               VEHICLE 			    ##
##										##
##########################################

@login_required(login_url='/login/')
def vehicle_manageView(request, id= None, template_name = 'vehicle/vehicle_manage.html'):
	if id:
	  	vehicleI = get_object_or_404(vehicle, pk=id)
	else:
		vehicleI = vehicle()

	if request.method == 'POST':
		vehicleForm = new_vehicleForm(request.POST, request.FILES, instance= vehicleI)
		if vehicleForm.is_valid():
			vehicleForm.save()
			vehicles = vehicle.objects.all().order_by('name')
			return render_to_response("index.html", {'vehicles':vehicles}, context_instance = RequestContext(request))
	else:
	 	vehicleForm = new_vehicleForm(instance= vehicleI)

	return render_to_response(template_name, {'vehicleForm': vehicleForm,}
			,context_instance = RequestContext(request))

@login_required(login_url='/login/')
def vehicle_details(request, query):
 	vehicleD = get_object_or_404(vehicle, pk=query)
	context = {'vehicle': vehicleD}
	return render_to_response('vehicle/vehicle_details.html', context,context_instance=RequestContext(request))

@permission_required('vehicles.can_delete_vehicle', login_url="/login/")
def delete_vehicle(request, id = None):
	vehicleInstance = get_object_or_404(vehicle, pk=id)
	vehicleInstance.delete()

	vehicles = vehicle.objects.all().order_by('name')
  	return render_to_response('index.html',{'vehicles':vehicles},context_instance=RequestContext(request))

##########################################
## 										##
##                RADIO                 ##
##										##
##########################################

@login_required(login_url='/login/')
def radiosView(request, template="vehicle/radio/radios.html"):
	Radios = radio.objects.all()
	c = {'Radios':Radios}
	return render_to_response(template, c, context_instance=RequestContext(request))

@login_required(login_url='/login/')
def radio_maintenanceView(request, query):
 	radioD = get_object_or_404(radio, pk=query)
 	radio_maintenances = radio_maintenance.objects.filter(radio = radioD).order_by('-date')
	radio_services = radio_maintenance_S.objects.filter(radio_maintenance__radio = radioD)
	radio_services_groups = radio_maintenance_SG.objects.filter(radio_maintenance__radio = radioD)
	context = {'radio': radioD, 'radio_services': radio_services, 'radio_services_groups':radio_services_groups, 'radio_maintenances': radio_maintenances}
	return render_to_response('vehicle/radio/radio_maintenance.html', context,context_instance=RequestContext(request))

@login_required(login_url='/login/')
def radio_manageView(request, id = None, template_name='vehicle/radio/radio_manage.html'):
	if id:
		radioI = get_object_or_404(radio, pk=id)
	else:
		radioI = radio()

	if request.method == 'POST':
		radioForm = radio_manageForm(request.POST, instance=radioI)
		if radioForm.is_valid():
			radioForm.save()
			Radios = radio.objects.all()
			c = {'Radios':Radios}
			return render_to_response('vehicle/radio/radios.html', c, context_instance=RequestContext(request))
	else:
	 	radioForm = radio_manageForm(instance=radioI)

	return render_to_response(template_name, {'radioForm': radioForm,}
			,context_instance = RequestContext(request))

@login_required(login_url='/login/')
def radio_maintenance_Inline_formset(request, id = None, radio_id = None, template= "vehicle/radio/radio_maintenance_Inline.html"):
	Radio = get_object_or_404(radio, pk = radio_id)

	Radio_SItems_formset = get_radio_maintenace_Sitems_formset(radio_maintenance_sForm, extra=1, can_delete=True)
	#StorageTank_SGItems_formset = get_storage_tank_maintenace_SGitems_formset(storage_tank_maintenance_sgForm, extra=1, can_delete=True)
	message = ""

	if id:
	  	radiomaintenance = get_object_or_404(radio_maintenance, pk=id)
	else:
		radiomaintenance = radio_maintenance()
	
	if request.method == 'POST':
		form = radio_maintenanceForm(request.POST, instance=radiomaintenance)
		formset = Radio_SItems_formset(request.POST, instance=radiomaintenance)
		#formsetSG = StorageTank_SGItems_formset(request.POST, instance=storagetankmaintenance)
		#if form.is_valid() and formset.is_valid() and formsetSG.is_valid():
		if form.is_valid() and formset.is_valid():

			r = form.save(commit = False)
			r.radio = Radio
			r.save()

			form.save()
			formset.save()
			#formsetSG.save()
			message = "Datos Guardados"
			return render_to_response(template, {'Radio':Radio,'form': form, 'formset': formset,'message':message}, context_instance=RequestContext(request))
	else:
		form = radio_maintenanceForm(instance=radiomaintenance)
		formset = Radio_SItems_formset(instance=radiomaintenance)

		#formsetSG = StorageTank_SGItems_formset(instance=storagetankmaintenance)
	return render_to_response(template, {'Radio':Radio,'form': form, 'formset': formset, 'message':message}, context_instance=RequestContext(request))

@permission_required('radio.can_delete_radio_maintenance', login_url="/login/")
def delete_radio_maintenance(request, id = None, radio_id = None):
	radio_maintenanceInstance = get_object_or_404(radio_maintenance, pk=id)
	radio_maintenanceInstance.delete()

	radioD = get_object_or_404(radio, pk = radio_id)
 	radio_maintenances = radio_maintenance.objects.filter(radio = radioD)
	radio_services = radio_maintenance_S.objects.filter(radio_maintenance__radio = radioD)
	radio_services_groups = radio_maintenance_SG.objects.filter(radio_maintenance__radio = radioD)
	context = {'radio': radioD, 'radio_services': radio_services, 'radio_services_groups':radio_services_groups, 'radio_maintenances': radio_maintenances}
	return render_to_response('vehicle/radio/radio_maintenance.html', context,context_instance=RequestContext(request))


@permission_required('radio.can_delete_radio', login_url="/login/")
def delete_radio(request, id = None, template="vehicle/radio/radios.html"):
	radioInstance = get_object_or_404(radio, pk=id)
	radioInstance.delete()

	Radios = radio.objects.all()
	c = {'Radios':Radios}
	return render_to_response(template, c, context_instance=RequestContext(request))

@login_required(login_url='/login/')
def radio_maintenanceReportView(request, query):
 	radioD = get_object_or_404(radio, pk=query)
 	radio_maintenances = radio_maintenance.objects.filter(radio = radioD).order_by('date')
	radio_services = radio_maintenance_S.objects.filter(radio_maintenance__radio = radioD)
	radio_services_groups = radio_maintenance_SG.objects.filter(radio_maintenance__radio = radioD)
	context = {'radio': radioD, 'radio_services': radio_services, 'radio_services_groups':radio_services_groups, 'radio_maintenances': radio_maintenances}
	return render_to_response('vehicle/radio/radio_maintenanceReport.html', context,context_instance=RequestContext(request))

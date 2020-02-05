from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .models import *
import requests
import json
from django.contrib.auth.models import User
import datetime, random
from rest_framework import status
from rest_framework.decorators import api_view
from django.core.mail import EmailMessage, BadHeaderError, send_mail

##from rest_framework import viewsets
from .models import *
from .serializers import *
# Create your views here.
"""
class FaseLunarViewSet(viewsets.ModelViewSet):
    queryset = Fase_lunar.objects.all()
    serializer_class = FaseLunarSerializer
    
class ProvinciaViewSet(viewsets.ModelViewSet):
    queryset = Provincias.objects.all()
    serializer_class = FaseLunarSerializer

class CantonViewSet(viewsets.ModelViewSet):
    queryset = Cantones.objects.all()
    serializer_class = FaseLunarSerializer

class ParroquiaViewSet(viewsets.ModelViewSet):
    queryset = Parroquias.objects.all()
    serializer_class = FaseLunarSerializer

class ObservacionViewSet(viewsets.ModelViewSet):
    queryset = Observaciones.objects.all()
    serializer_class = ObservacionSerializer

class MedicionesViewSet(viewsets.ModelViewSet):
    queryset = Mediciones.objects.all()
    serializer_class = MedicionesSerializer"""

def llenar_base(request):
    """
    rol = Roles(nombre="admin")
    rol.save()
    rol = Roles(nombre="validador")
    rol.save()
    rol = Roles(nombre="observador")
    rol.save()
    rol = Roles(nombre="visitante")
    rol.save()

    geo = json.loads(requests.get("https://cip-rrd.herokuapp.com/geografia").content)
    for key in geo:
        if key != "1":
            prov = Provincias(nombre=geo[key]['nombre'])
            prov.save()
            for cant in geo[key]['cantones']:
                for k in cant:
                    canton = Cantones(nombre=k, id_provincia=prov)
                    canton.save()
                    for i in cant[k]:
                        parroquia = Parroquias(nombre=i, id_canton=canton)
                        parroquia.save()

    est1 = Estados(nombre="Activado")
    est1.save()
    est2 = Estados(nombre="Removido")
    est2.save()
    est3 = Estados(nombre="Pendiente")
    est3.save()
    est4 = Estados(nombre="Chequiando")
    est4.save()
    est5 = Estados(nombre="Aprovado")
    est5.save()
    estac = json.loads(requests.get("https://cip-rrd.herokuapp.com/estaciones").content)
    for key in estac:
        p_name = estac[key]['parish']
        if estac[key]['parish'] == "Manglar Alto" or estac[key]['parish'] == "Olon":
            p_name = "Manglaralto"
        elif estac[key]['parish'] == "Salinas":
            p_name = "Vicente Rocafuerte"
        parro = Parroquias.objects.filter(nombre=p_name)[0]
        estacion = Estaciones(id_parroquia=parro, nombre=estac[key]['name'], latitud=estac[key]['coord']['lat'], 
                longitud=estac[key]['coord']['lng'], puntosReferencia="N/A", foto=estac[key]['img'], id_estado=est1)
        estacion.save()

    usua = json.loads(requests.get("http://cip-rrd.herokuapp.com/usuarios").content)  
    for k in usua:
        auth = User(username=usua[k]['usuario'], password=usua[k]['usuario'], first_name=usua[k]['nombre'], 
                        last_name=usua[k]['apellido'], email=usua[k]['email'])
        auth.save()
        rol = Roles.objects.filter(nombre=usua[k]['rol'])[0]
        provt = usua[k]['provincia']
        if usua[k]['provincia'] == "Galápagos" or usua[k]['provincia'] == "Gauyas": 
            provt = "Guayas"
        prov = Provincias.objects.filter(nombre=provt)[0]
        est = Estados.objects.filter(id_estado=1)[0]
        u = Usuarios(auth_user=auth, institucion=usua[k]['institucion'], telefono=usua[k]['cedula'], cedula=usua[k]['cedula'], 
                    id_provincia=prov, id_rol=rol, id_estado=est)
        u.save()
       
    obs = json.loads(requests.get(
        "https://cip-rrd.herokuapp.com/observaciones").content)
    ep = ["invierno", "verano"]
    est = Estados.objects.filter(id_estado=3)[0]
    for k in obs:
        ob = obs[k]
        p_name = ob['estacion']['Parroquia']
    
        if ob['estacion']['Parroquia'] == "Manglar Alto" or ob['estacion']['Parroquia'] == "Santa Elena":
            p_name = "Manglaralto"
        elif ob['estacion']['Parroquia'] == "Playas":
            p_name = "General Villamil"
        elif ob['estacion']['Parroquia'] == "Salinas":
            p_name = "Vicente Rocafuerte"
        p = Parroquias.objects.filter(nombre=p_name)[0]
        esta = Estaciones.objects.filter(nombre=ob['estacion']['nombre'], id_parroquia=p)[0]
        fase = Fase_lunar.objects.filter(nombre=ob['fase_lunar'])[0]
        fecha = datetime.datetime.strptime(ob["fecha"], "%d/%m/%Y").date()
        n, a = ob["observador"].split(" ")
        a_u = User.objects.filter(first_name=n)[0]
        usu = Usuarios.objects.filter(auth_user=a_u)[0]
        obser = Observaciones(epoca=ep[random.randint(0, 1)], fecha=fecha, registeredto=datetime.datetime.now(), id_usuario=usu,
            id_fase_lunar=fase, id_estacion=esta, id_estado=est)
        obser.save()
        for md in ob["mediciones"]:
            t_ola = Tipo_oleaje.objects.filter(id_tipo=md["olas"]["tipo"])[0]
            cr = md["corriente_de_resaca"]
            if cr == "SI":
                cr = True
            else: cr = False
            if md["hora"] == "11:20":
                md["hora"] = "11:30"
            per = Periodos.objects.filter(horario=datetime.datetime.strptime(md["hora"], "%H:%M").time())[0]
            medi = Mediciones(id_observacion=obser, fechaHora=datetime.datetime.now(), ola_tipo_oleaje=t_ola, corriente_resaca=cr,
                       latitud=obser.id_estacion.latitud, longitud=obser.id_estacion.longitud, temperatura=26.0, id_periodo=per, perfil_playa=md["orientacion_de_playa"],
                       ancho_zon_surf=md["ancho_de_zona_de_surf"], lp_flotador=md["distancia_lp_al_flotador"], lp_rompiente=md["distancia_lp_al_rompiente"],
                       crl_espacio=md["corriente_del_litoral"]["espacio"], crl_tiempo=md["corriente_del_litoral"]["tiempo"], crl_velocidad=md["corriente_del_litoral"]["velocidad"], 
                       crl_direccion=md["corriente_del_litoral"]["direccion"], vien_direccion=md["viento"]["direccion"], vien_velocidad=md["viento"]["direccion"], ola_ortogonal=md["olas"]["ortogonal"], 
                       ola_periodo_onda=md["olas"]["periodo"], ola_altura_rompiente_promedio=md["olas"]["altura_promedio"], ola_direccion=0, estado=est)
            medi.save()
            i = 1
            for alt in md["olas"]["alturas"]:
                al_r = Altura_rompiente(num_medicion=i, valor=alt, id_medicion=medi)
                al_r.save()
                i = i + 1
        """
    return HttpResponse("hello!!!")


@api_view(['POST'])
def sendEmail(request):
    if request.method == 'POST':
        dic =  request.POST.dict()

        nombres = dic['nombres']
        asunto = dic['asunto']
        mail = dic['correo']
        mensaje = dic['mensaje']
        textomensaje = '<br>'
        lista = mensaje.split('\n')
        c = 0
        for i in lista:
            textomensaje += i+'</br>'
            c+=1
            if len(lista)  > c :
                textomensaje += '<br>'
        msj = '<p><strong>Nombres: </strong>'+nombres+'</p><p><strong>Correo: </strong>'+mail+'</p><strong>Mensaje: </strong>'+textomensaje+'</p>'
        msj2 = msj+'<br/><br/><br/><p>Usted se contacto con Centro Internacional del Pacífico.</p><p><strong>NO RESPONDER A ESTE MENSAJE</strong>, nosotros nos pondremos en conacto con usted de ser necesario.</p><br/>'
        try:
            send_mail('Contactanos: '+asunto, msj,'investigacioncentro63@gmail.com', ['investigacioncentro63@gmail.com'], fail_silently=False, html_message = '<html><body>'+msj+'</body></html>')
            send_mail('Correo enviado: '+asunto, msj2, 'investigacioncentro63@gmail.com', [mail], fail_silently=False, html_message= '<html><body>'+msj2+'</body></html>')
        except BadHeaderError:
            return HttpResponse('Invalid header found.')
        return HttpResponse(status=201)
    return HttpResponse(status=404)

@api_view(['POST'])
def postObservaciones(request):
    if request.method=='POST':       
        response=json.loads(request.body)
        
        fechaHora= response["fechaHora"]
        provincia=response["provincia"]
        parroquia=response["parroquia"]
        canton=response["canton"]
        estacion=response["estacion"]
        fase_lunar=response["fase"]
        epocac=response["epoca"]
        temperatura = response["temperatura"]
        perfil_playa = response["perfil_playa"]
        corriente_de_resaca= response["corriente_resaca"]
        latitud= response["latitud"]
        longitud= response["longitud"]
        ancho_zon_surf= response["ancho_zon_surf"]

        lp_flotador=response["lp_flotador"]
        lp_rompiente=response["lp_rompiente"]
        crl_espacio= response["crl_espacio"]
        crl_tiempo= response["crl_tiempo"]
        crl_velocidad= response["crl_velocidad"]
        vien_direccion= response["vien_direccion"]
        vien_velocidad= response["vien_velocidad"]
        ola_ortogonal= response["ola_ortogonal"]
        ola_periodo_onda= response["ola_periodo_onda"]
        ola_altura_rompiente_promedio= response["ola_altura_rompiente_promedio"]
        ola_direccion= response["ola_direccion"]
        id_observacion= response["id_observacion"]
        ola_tipo_oleaje= response["ola_tipo_oleaje"]
        id_periodo= response["id_periodo"]
        estado=response["estado"]

     
        est = Estados.objects.filter(id_estado=estado)[0]
        provinc = Provincias.objects.filter(nombre=provincia)[0]
        parr = Parroquias.objects.filter(nombre=parroquia)[0]
        estac = Estaciones.objects.filter(nombre=estacion)[0]
        period = Periodos.objects.filter(id_periodos=id_periodo)[0]
        fas = Fase_lunar.objects.filter(nombre=fase_lunar)[0]
        rol = Roles.objects.filter(nombre="admin")[0]
        perios= Periodos.objects.get(id_periodos=1)
        ol = Tipo_oleaje.objects.get(id_tipo=ola_tipo_oleaje)
        auth2 = User.objects.get(username="chjoguer")
        u2= Usuarios.objects.get(auth_user=auth2)
     
        observacion = Observaciones(epoca=epocac,id_usuario=u2
        ,registeredto=datetime.datetime.now(),id_fase_lunar=fas,id_estacion=estac,id_estado=est)
       
        medicion = Mediciones(id_observacion=observacion
        ,corriente_resaca=corriente_de_resaca,fechaHora=datetime.datetime.now(),latitud=latitud,longitud=longitud
        ,temperatura=temperatura,perfil_playa=perfil_playa,ancho_zon_surf=ancho_zon_surf
        ,lp_flotador=lp_flotador,lp_rompiente=lp_rompiente,crl_espacio=crl_espacio,crl_tiempo=crl_tiempo,crl_velocidad=crl_velocidad,crl_direccion=response["crl_direccion"]
        ,vien_direccion=vien_direccion,id_periodo=perios,vien_velocidad=vien_velocidad,ola_ortogonal=ola_ortogonal,ola_periodo_onda=ola_periodo_onda,ola_altura_rompiente_promedio=ola_altura_rompiente_promedio
        ,ola_direccion=0,ola_tipo_oleaje=ol,estado=est)



        olaAltura = Altura_rompiente(num_medicion=1,valor=response["md1"],id_medicion=medicion)
        olaAltura2 = Altura_rompiente(num_medicion=1,valor=response["md2"],id_medicion=medicion)
        olaAltura3 = Altura_rompiente(num_medicion=1,valor=response["md3"],id_medicion=medicion)
        olaAltura4 = Altura_rompiente(num_medicion=1,valor=response["md4"],id_medicion=medicion)
        olaAltura5 = Altura_rompiente(num_medicion=1,valor=response["md5"],id_medicion=medicion)
        olaAltura6 = Altura_rompiente(num_medicion=1,valor=response["md6"],id_medicion=medicion)
        olaAltura7 = Altura_rompiente(num_medicion=1,valor=response["md7"],id_medicion=medicion)
        olaAltura8 = Altura_rompiente(num_medicion=1,valor=response["md8"],id_medicion=medicion)
        olaAltura9 = Altura_rompiente(num_medicion=1,valor=response["md9"],id_medicion=medicion)
        olaAltura10 = Altura_rompiente(num_medicion=1,valor=response["md10"],id_medicion=medicion)

        observacion.save()
        medicion.save()
        olaAltura.save()
        olaAltura2.save()
        olaAltura3.save()
        olaAltura4.save()
        olaAltura5.save()
        olaAltura6.save()
        olaAltura7.save()
        olaAltura8.save()
        olaAltura9.save()
        olaAltura10.save()

        
     

    return JsonResponse(response)



@api_view(['GET'])
def getObservaciones(request):
    if request.method == 'GET':
        response = dict()
        obs = Observaciones.objects.all()
        for o in obs:
            datos = dict()
            response[o.id_observacion] = datos
            datos["estacion"] = dict()
            est = o.id_estacion
            usuario = o.id_usuario.auth_user
            datos["estacion"]["id"] = est.id_estacion
            datos["estacion"]["nombre"] = est.nombre
            datos["estacion"]["Parroquia"] = est.id_parroquia.nombre
            datos["estacion"]["img"] = est.foto
            datos["fecha"] = o.fecha
            datos["fase_lunar"] = o.id_fase_lunar.nombre
            datos["observador"] = usuario.first_name + " " + usuario.last_name
            datos["mediciones"] = list()
            meds = Mediciones.objects.filter(id_observacion=o)
            for med in meds:
                info = dict()
                info["hora"] = med.id_periodo.horario
                cl = dict()
                info["corriente_del_litoral"] = cl
                cl["espacio"] = med.crl_espacio
                cl["tiempo"] = med.crl_tiempo
                cl["direccion"] = med.crl_direccion
                cl["velocidad"] = med.crl_velocidad
                info["corriente_de_resaca"] = med.corriente_resaca
                info["ancho_de_zona_de_surf"] = med.ancho_zon_surf
                info["distancia_lp_al_flotador"] = med.lp_flotador
                info["distancia_lp_al_rompiente"] = med.lp_rompiente
                v = dict()
                info["viento"] = v
                v["velocidad"] = med.vien_velocidad
                v["direccion"] = med.vien_direccion
                info["orientacion_de_playa"] = med.perfil_playa
                ol = dict()
                info["olas"] = ol
                ol["ortogonal"] = med.ola_ortogonal
                ol["tipo"] = med.ola_tipo_oleaje.nombre
                ol["periodo"] = med.ola_periodo_onda
                ol["alturas"] = list()
                alts = Altura_rompiente.objects.filter(id_medicion=med)
                for alt in alts:
                    ol["alturas"].append(alt.valor)
                ol["altura_promedio"] = med.ola_altura_rompiente_promedio
                datos["mediciones"].append(info)
        return JsonResponse(response)